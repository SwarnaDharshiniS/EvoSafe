"""Tests for framework-independent EA role inference."""

import ast
import json
import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.ea_inference import (
    EAConfidence,
    EARole,
    TerminationKind,
    analyze_ea_roles,
)
from analysis.pipeline import analyze_program
from analysis.ea_inference._data_flow import IntraProceduralDataFlow
from analysis.ea_inference._structure import (
    CandidateCollectionAnalyzer,
    CandidateRelation,
    CollectionOperation,
)
from cfg.cfg_builder import build_cfg


def infer(code: str):
    return analyze_ea_roles(textwrap.dedent(code), source_name="<test>")


class TestPopulationAndFitness(unittest.TestCase):

    def test_candidate_collection_iteration_and_evaluation(self):
        result = infer("""
            candidates = initialize_candidates()
            for candidate in candidates:
                evaluate(candidate)
        """)
        population = result.for_role(EARole.POPULATION)
        fitness = result.for_role(EARole.FITNESS_EVALUATION)
        self.assertTrue(population.detected)
        self.assertTrue(fitness.detected)
        self.assertEqual(population.confidence, EAConfidence.HIGH)
        self.assertEqual(population.evidence[0].line, 3)
        self.assertTrue(population.evidence[0].cfg_blocks)

    def test_candidate_dependent_score_call_is_fitness(self):
        result = infer("""
            candidates = create()
            for item in candidates:
                value = objective(item)
        """)
        finding = result.for_role(EARole.FITNESS_EVALUATION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.HIGH)
        self.assertIn("item", finding.evidence[0].snippet)

    def test_unrelated_collection_and_score_names_are_not_enough(self):
        result = infer("""
            population = [1, 2, 3]
            score = 10 * 2
            for item in population:
                print(item)
        """)
        self.assertFalse(result.for_role(EARole.POPULATION).detected)
        self.assertFalse(result.for_role(EARole.FITNESS_EVALUATION).detected)

    def test_candidate_independent_score_is_not_fitness(self):
        result = infer("""
            candidates = create()
            for item in candidates:
                value = objective(10)
        """)
        self.assertFalse(result.for_role(EARole.FITNESS_EVALUATION).detected)

    def test_candidate_scoring_comprehension_is_detected(self):
        result = infer("""
            population = create_population()
            scores = [evaluate(candidate) for candidate in population]
        """)
        self.assertTrue(result.for_role(EARole.POPULATION).detected)
        self.assertTrue(result.for_role(EARole.FITNESS_EVALUATION).detected)
        self.assertEqual(result.for_role(EARole.POPULATION).evidence[0].kind, "candidate_comprehension")

    def test_previously_missed_basic_string_example_recovers_structural_roles(self):
        source_path = Path(__file__).parent.parent / "Python/genetic_algorithm/basic_string.py"
        result = analyze_ea_roles(source_path.read_text(encoding="utf-8"), source_name=str(source_path))
        self.assertTrue(result.for_role(EARole.POPULATION).detected)
        self.assertTrue(result.for_role(EARole.FITNESS_EVALUATION).detected)
        self.assertTrue(result.for_role(EARole.TERMINATION).detected)
        self.assertTrue(all(finding.evidence for finding in (
            result.for_role(EARole.POPULATION),
            result.for_role(EARole.FITNESS_EVALUATION),
            result.for_role(EARole.TERMINATION),
        )))

    def test_alias_of_population_collection_supports_selection(self):
        result = infer("""
            source = create_population()
            population = source
            for candidate in population:
                score = objective(candidate)
            ranked = sorted(source, key=objective)
        """)
        self.assertTrue(result.for_role(EARole.POPULATION).detected)
        self.assertTrue(result.for_role(EARole.SELECTION).detected)


class TestSelection(unittest.TestCase):

    def test_ranking_candidates_with_key(self):
        result = infer("""
            candidates = create()
            for item in candidates:
                value = objective(item)
            survivors = sorted(candidates, key=objective)[-5:]
        """)
        finding = result.for_role(EARole.SELECTION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.HIGH)
        self.assertEqual(finding.evidence[0].line, 5)

    def test_ordinary_list_filtering_is_not_selection(self):
        result = infer("""
            values = [1, 2, 3]
            positives = [value for value in values if value > 0]
        """)
        self.assertFalse(result.for_role(EARole.SELECTION).detected)


class TestMutationAndCrossover(unittest.TestCase):

    def test_copy_then_candidate_element_modification_is_mutation(self):
        result = infer("""
            candidates = create()
            for individual in candidates:
                child = individual.copy()
                child[0] += random_change()
        """)
        finding = result.for_role(EARole.MUTATION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.HIGH)
        self.assertEqual(finding.evidence[0].line, 5)

    def test_candidate_alias_element_write_is_mutation(self):
        result = infer("""
            candidates = create()
            for individual in candidates:
                alias = individual
                alias[0] = changed_value
        """)
        self.assertTrue(result.for_role(EARole.MUTATION).detected)
        self.assertTrue(any("alias" in item.snippet for item in result.for_role(EARole.MUTATION).evidence))

    def test_ordinary_variable_update_is_not_mutation(self):
        result = infer("""
            total = 0
            total += 1
        """)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)

    def test_two_parent_slice_recombination_is_crossover(self):
        result = infer("""
            candidates = create()
            for parent1, parent2 in pairs(candidates):
                child = parent1[:3] + parent2[3:]
        """)
        finding = result.for_role(EARole.CROSSOVER)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.HIGH)
        self.assertEqual(finding.evidence[0].line, 4)

    def test_unrelated_concatenation_is_not_crossover(self):
        result = infer("""
            text = left + right
        """)
        self.assertFalse(result.for_role(EARole.CROSSOVER).detected)


class TestReplacement(unittest.TestCase):

    def test_offspring_added_to_candidate_collection(self):
        result = infer("""
            candidates = create()
            for individual in candidates:
                child = individual.copy()
                child[0] += random_change()
                candidates.append(child)
        """)
        finding = result.for_role(EARole.REPLACEMENT)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.HIGH)

    def test_candidate_index_replacement(self):
        result = infer("""
            candidates = create()
            for item in candidates:
                objective(item)
            candidates[worst_index] = child
        """)
        self.assertTrue(result.for_role(EARole.REPLACEMENT).detected)

    def test_rebuilt_population_from_selected_and_offspring(self):
        result = infer("""
            candidates = create()
            for item in candidates:
                value = objective(item)
            selected = sorted(candidates, key=objective)
            offspring = create_offspring(selected)
            candidates = selected + offspring
        """)
        self.assertTrue(result.for_role(EARole.SELECTION).detected)
        self.assertTrue(result.for_role(EARole.REPLACEMENT).detected)

    def test_ordinary_collection_append_is_not_replacement(self):
        result = infer("""
            values = []
            values.append(1)
        """)
        self.assertFalse(result.for_role(EARole.REPLACEMENT).detected)


class TestTermination(unittest.TestCase):

    def test_bounded_generation_loop(self):
        result = infer("""
            candidates = create()
            for generation in range(100):
                for individual in candidates:
                    value = objective(individual)
        """)
        finding = result.for_role(EARole.TERMINATION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.termination_kind, TerminationKind.STATICALLY_BOUNDED)

    def test_condition_based_termination(self):
        result = infer("""
            candidates = create()
            while best_score < threshold:
                for individual in candidates:
                    value = objective(individual)
        """)
        self.assertEqual(
            result.for_role(EARole.TERMINATION).termination_kind,
            TerminationKind.CONDITION_BASED,
        )

    def test_unbounded_ea_loop_is_unknown_or_unbounded(self):
        result = infer("""
            candidates = create()
            while True:
                for individual in candidates:
                    value = objective(individual)
        """)
        self.assertEqual(
            result.for_role(EARole.TERMINATION).termination_kind,
            TerminationKind.UNKNOWN_OR_UNBOUNDED,
        )

    def test_unrelated_bounded_loop_is_not_ea_termination(self):
        result = infer("""
            total = 0
            for index in range(10):
                total += index
        """)
        self.assertFalse(result.for_role(EARole.TERMINATION).detected)

    def test_population_traversal_alone_is_not_process_termination(self):
        result = infer("""
            candidates = create()
            for candidate in candidates:
                value = objective(candidate)
        """)
        self.assertFalse(result.for_role(EARole.TERMINATION).detected)


class TestReportAndFrameworkIndependence(unittest.TestCase):

    def test_generic_code_needs_no_framework_import(self):
        result = infer("""
            pool = create_candidates()
            for candidate in pool:
                measured = objective(candidate)
        """)
        self.assertTrue(result.for_role("population").detected)
        self.assertTrue(result.for_role("fitness_evaluation").detected)

    def test_misleading_role_names_alone_do_not_detect(self):
        result = infer("""
            population = [1]
            fitness = 1
            selection = population[0]
            mutation = 0
            crossover = [1] + [2]
            replacement = []
            termination = True
        """)
        self.assertFalse(any(finding.detected for finding in result.roles.values()))

    def test_supplied_cfg_and_serialization_are_supported(self):
        source = textwrap.dedent("""
            pool = create()
            for candidate in pool:
                value = objective(candidate)
        """)
        cfg = build_cfg(source)
        first = analyze_ea_roles(source, source_name="example.py", cfg=cfg)
        second = analyze_ea_roles(source, source_name="example.py")
        self.assertTrue(first.for_role(EARole.POPULATION).evidence[0].cfg_blocks)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(json.dumps(first.to_dict(), sort_keys=True), json.dumps(second.to_dict(), sort_keys=True))

    def test_composite_pipeline_keeps_ea_optional_and_verdict_independent(self):
        source = "eval(input())"
        base = analyze_program(source)
        enriched = analyze_program(source, include_ea=True)
        self.assertIsNone(base.ea_roles)
        self.assertIsNotNone(enriched.ea_roles)
        self.assertEqual(
            base.safety_facts["decision"]["verdict"],
            enriched.safety_facts["decision"]["verdict"],
        )
        self.assertEqual(enriched.safety_facts["decision"]["verdict"], "UNSAFE")
        self.assertIn("safety_facts", enriched.to_dict())
        self.assertIn("resource_facts", enriched.to_dict())
        self.assertIn("ea_roles", enriched.to_dict())
        self.assertIn("evidence", enriched.to_dict())


class TestIntraProceduralDataFlow(unittest.TestCase):

    def _flow(self, source: str) -> IntraProceduralDataFlow:
        return IntraProceduralDataFlow(ast.parse(textwrap.dedent(source)))

    def test_simple_assignment_flow_records_source_and_target(self):
        flow = self._flow("""
            first = create_population()
            second = first
        """)
        fact = next(item for item in flow.facts if item.kind == "assignment" and item.source == "first" and item.target == "second")
        self.assertEqual(fact.location.line, 3)
        self.assertTrue(flow.value_known("second", line=3))

    def test_alias_flow_tracks_shared_binding(self):
        flow = self._flow("""
            population = create_population()
            pop = population
        """)
        self.assertEqual(flow.alias_group("pop", line=3), {"population", "pop"})
        alias = next(item for item in flow.facts if item.kind == "alias")
        self.assertEqual(alias.source, "population")
        self.assertEqual(alias.target, "pop")
        self.assertEqual(alias.related_location.line, 2)

    def test_chained_alias_flow_preserves_object_identity(self):
        flow = self._flow("""
            population = create_population()
            first = population
            second = first
            third = second
        """)
        self.assertEqual(flow.alias_group("third", line=5), {"population", "first", "second", "third"})

    def test_slice_replacement_retains_collection_alias_and_location(self):
        flow = self._flow("""
            population = create_population()
            alias = population
            offspring = create_offspring()
            alias[:] = offspring
        """)
        fact = next(item for item in flow.facts if item.kind == "slice_replacement")
        self.assertEqual(fact.target, "alias")
        self.assertEqual(fact.source, "offspring")
        self.assertEqual(fact.location.line, 5)
        self.assertEqual(flow.alias_group("alias", line=5), {"population", "alias"})

    def test_container_mutation_uses_aliased_object_root(self):
        flow = self._flow("""
            population = create_population()
            alias = population
            alias.append(child)
        """)
        fact = next(item for item in flow.facts if item.kind == "container_mutation")
        self.assertEqual(fact.source, "alias")
        self.assertEqual(fact.target, next(iter(flow.roots_for_name("population", line=4))))
        self.assertTrue(fact.resolved)

    def test_function_argument_flow_maps_call_argument_to_parameter(self):
        flow = self._flow("""
            def identity(item):
                return item
            population = create_population()
            candidate = identity(population)
        """)
        fact = next(item for item in flow.facts if item.kind == "call_argument" and item.callee == "identity")
        self.assertEqual(fact.source, "population")
        self.assertEqual(fact.target, "identity:item")
        self.assertTrue(fact.resolved)
        self.assertEqual(fact.location.line, 5)

    def test_statically_resolvable_function_return_preserves_alias(self):
        flow = self._flow("""
            def identity(item):
                alias = item
                return alias
            population = create_population()
            candidate = identity(population)
        """)
        self.assertEqual(flow.alias_group("candidate", line=6), {"population", "candidate"})
        returned = next(item for item in flow.facts if item.kind == "return_value" and item.scope == "identity")
        self.assertEqual(returned.source, "alias")
        self.assertEqual(returned.location.line, 4)

    def test_unresolved_call_does_not_inherit_argument_alias(self):
        flow = self._flow("""
            population = create_population()
            result = unknown_transform(population)
        """)
        call = next(item for item in flow.facts if item.kind == "call_site" and item.callee == "unknown_transform")
        argument = next(item for item in flow.facts if item.kind == "call_argument" and item.callee == "unknown_transform")
        call_result = next(item for item in flow.facts if item.kind == "call_result" and item.target == "result")
        self.assertFalse(call.resolved)
        self.assertFalse(argument.resolved)
        self.assertFalse(call_result.resolved)
        self.assertEqual(call_result.related_location.line, 3)
        self.assertEqual(argument.source, "population")
        self.assertEqual(flow.alias_group("result", line=3), {"result"})

    def test_population_alias_and_unresolved_transform_call_chain(self):
        flow = self._flow("""
            population = create_population()
            pop = population
            offspring = mutate(pop)
        """)
        self.assertEqual(flow.alias_group("pop", line=3), {"population", "pop"})
        argument = next(item for item in flow.facts if item.kind == "call_argument" and item.callee == "mutate")
        result = next(item for item in flow.facts if item.kind == "call_result" and item.target == "offspring")
        self.assertEqual(argument.source, "pop")
        self.assertEqual(argument.location.line, 4)
        self.assertFalse(result.resolved)
        self.assertEqual(result.location.line, 4)

    def test_reassignment_invalidates_prior_alias(self):
        flow = self._flow("""
            population = create_population()
            alias = population
            alias = create_other()
        """)
        self.assertEqual(flow.alias_group("alias", line=4), {"alias"})
        reassignment = next(item for item in flow.facts if item.kind == "reassignment" and item.target == "alias")
        self.assertEqual(reassignment.location.line, 4)
        self.assertEqual(reassignment.related_location.line, 3)

    def test_flow_facts_preserve_assignment_locations(self):
        flow = self._flow("""
            base = create()
            alias = base
            alias = transform(alias)
        """)
        facts = [item for item in flow.facts if item.target == "alias"]
        self.assertEqual([item.location.line for item in facts if item.kind == "assignment"], [3, 4])
        self.assertTrue(all(item.location.col is not None for item in facts))


class TestCandidateCollectionStructure(unittest.TestCase):

    def _facts(self, source: str):
        tree = ast.parse(textwrap.dedent(source))
        return CandidateCollectionAnalyzer(tree, IntraProceduralDataFlow(tree)).facts

    def test_indexed_candidate_preserves_collection_origin(self):
        """A constant indexed read is an element of its source collection."""
        facts = self._facts("""
            values = build()
            item = values[0]
        """)
        indexed = next(f for f in facts.candidates if f.relation == CandidateRelation.ELEMENT_OF_COLLECTION)
        self.assertEqual(indexed.source_collection, "<module>:values")
        self.assertIn("values[0]", indexed.candidate)

    def test_iteration_target_is_an_element_of_collection(self):
        """A for-target receives an element from the iterated collection."""
        facts = self._facts("""
            values = build()
            for item in values:
                consume(item)
        """)
        self.assertTrue(any(f.relation == CandidateRelation.ELEMENT_OF_COLLECTION for f in facts.candidates))
        self.assertTrue(any(f.operation == CollectionOperation.ITERATE for f in facts.collections))

    def test_local_helper_returning_collection_is_recorded(self):
        """A collection returned by a same-source helper has explicit provenance."""
        facts = self._facts("""
            def build():
                return [1, 2, 3]
            values = build()
        """)
        self.assertTrue(any(f.operation == CollectionOperation.HELPER_RETURN and f.collection.endswith(":values") for f in facts.collections))

    def test_collection_rebinding_is_distinct_from_element_mutation(self):
        """Rebinding one collection name to another preserves both identities."""
        facts = self._facts("""
            first = [1, 2]
            second = [3, 4]
            current = first
            current = second
        """)
        self.assertTrue(any(f.operation == CollectionOperation.REASSIGN and f.collection.endswith(":current") for f in facts.collections))

    def test_slice_is_a_collection_subset_not_an_unrelated_value(self):
        """A slice fact retains its source collection and selected result."""
        facts = self._facts("""
            values = [1, 2, 3]
            subset = values[:2]
        """)
        self.assertTrue(any(f.operation == CollectionOperation.SLICE for f in facts.collections))
        self.assertTrue(any(f.relation == CandidateRelation.SELECTED_FROM_COLLECTION for f in facts.candidates))

    def test_index_comprehension_retains_the_indexed_source_collection(self):
        """A comprehension over indices can still select elements from another collection."""
        facts = self._facts("""
            values = [[1], [2], [3]]
            indices = [2, 0]
            chosen = [values[index] for index in indices]
        """)
        self.assertTrue(any(f.relation == CandidateRelation.SELECTED_FROM_COLLECTION and f.source_collection == "<module>:values" for f in facts.candidates))

    def test_candidate_alias_preserves_lineage(self):
        """A direct name alias refers to the same candidate-derived value."""
        facts = self._facts("""
            values = [[1], [2]]
            item = values[0]
            alias = item
        """)
        self.assertTrue(any(f.relation == CandidateRelation.ALIAS_OF_CANDIDATE and f.candidate.endswith(":alias") for f in facts.candidates))

    def test_explicit_candidate_copy_preserves_origin_without_aliasing(self):
        """list(candidate) creates a copy lineage rather than an identity alias."""
        facts = self._facts("""
            values = [[1], [2]]
            item = values[0]
            cloned = list(item)
        """)
        self.assertTrue(any(f.relation == CandidateRelation.COPY_OF_CANDIDATE and f.candidate.endswith(":cloned") for f in facts.candidates))

    def test_write_to_candidate_derived_copy_is_candidate_mutation(self):
        """An indexed write through a candidate copy retains candidate origin."""
        facts = self._facts("""
            values = [[1], [2]]
            item = values[0]
            cloned = list(item)
            cloned[0] += 1
        """)
        self.assertTrue(any(f.relation == CandidateRelation.MUTATED_CANDIDATE and f.location.line == 5 for f in facts.lineage))

    def test_candidate_list_method_is_candidate_mutation(self):
        """A container method invoked on a candidate-derived list changes that candidate."""
        facts = self._facts("""
            values = [[1], [2]]
            item = values[0]
            item.append(3)
        """)
        self.assertTrue(any(f.relation == CandidateRelation.MUTATED_CANDIDATE and f.location.line is not None for f in facts.lineage))

    def test_two_distinct_indexed_candidates_feed_one_helper_output(self):
        """A resolved helper returning a composition links two distinct elements."""
        facts = self._facts("""
            def combine(left, right):
                return left[:1] + right[1:]
            values = [[1, 2], [3, 4]]
            first = values[0]
            second = values[1]
            result = combine(first, second)
        """)
        dependency = next(f for f in facts.lineage if f.relation == CandidateRelation.DERIVED_FROM_TWO_CANDIDATES)
        self.assertEqual(len(set(dependency.source_candidates)), 2)
        self.assertEqual(dependency.destination, "<module>:result")

    def test_candidate_argument_is_linked_to_collection_insertion(self):
        """Appending a tracked candidate produces an insertion lineage fact."""
        facts = self._facts("""
            values = [[1], [2]]
            output = []
            item = values[0]
            output.append(item)
        """)
        self.assertTrue(any(f.relation == CandidateRelation.INSERTED_INTO_COLLECTION for f in facts.lineage))

    def test_candidate_assignment_replaces_an_existing_collection_element(self):
        """Replacing a collection slot with a candidate-derived value is explicit."""
        facts = self._facts("""
            values = [[1], [2]]
            item = values[0]
            values[-1] = item
        """)
        self.assertTrue(any(f.relation == CandidateRelation.REPLACED_IN_COLLECTION for f in facts.lineage))

    def test_clear_extend_is_collection_replacement(self):
        """Repopulation after clear is represented as replacement, not mere insertion."""
        facts = self._facts("""
            values = [[1], [2]]
            output = []
            item = values[0]
            output.clear()
            output.extend([item])
        """)
        self.assertTrue(any(f.relation == CandidateRelation.REPLACED_IN_COLLECTION for f in facts.lineage))

    def test_matrix_write_has_no_candidate_mutation_lineage(self):
        """An indexed matrix write is not candidate mutation without lineage."""
        facts = self._facts("""
            matrix = [[0, 0], [0, 0]]
            matrix[0][1] = 4
        """)
        self.assertFalse(any(f.relation == CandidateRelation.MUTATED_CANDIDATE for f in facts.lineage))

    def test_copy_of_ordinary_list_has_no_candidate_copy_lineage(self):
        """Copying an ordinary list does not invent candidate identity."""
        facts = self._facts("""
            values = [1, 2]
            cloned = values.copy()
        """)
        self.assertFalse(any(f.relation == CandidateRelation.COPY_OF_CANDIDATE for f in facts.candidates))

    def test_unresolved_two_argument_call_does_not_create_dependency(self):
        """An unknown callee cannot establish how two inputs contribute to output."""
        facts = self._facts("""
            values = [[1], [2]]
            first = values[0]
            second = values[1]
            result = unknown(first, second)
        """)
        self.assertFalse(any(f.relation == CandidateRelation.DERIVED_FROM_TWO_CANDIDATES for f in facts.lineage))

    def test_unrelated_two_argument_call_has_no_candidate_dependency(self):
        """Two ordinary scalar arguments are not candidates or crossover parents."""
        facts = self._facts("""
            def combine(left, right):
                return left + right
            result = combine(2, 3)
        """)
        self.assertFalse(any(f.relation == CandidateRelation.DERIVED_FROM_TWO_CANDIDATES for f in facts.lineage))

    def test_scalar_result_is_not_candidate_lineage(self):
        """A scalar calculation without a collection-derived input stays unrelated."""
        facts = self._facts("""
            result = 2 * 3 + 4
        """)
        self.assertFalse(facts.candidates)
        self.assertFalse(facts.lineage)

    def test_resolved_candidate_dependent_helper_has_computation_fact(self):
        """A local score helper's returned value remains linked to its argument."""
        facts = self._facts("""
            def measure(item):
                return sum(item)
            values = [[1], [2]]
            item = values[0]
            value = measure(item)
        """)
        self.assertTrue(any(f.relation == CandidateRelation.COMPUTED_FROM_CANDIDATE and f.destination.endswith(":value") for f in facts.lineage))

    def test_branch_ambiguous_alias_is_not_promoted(self):
        """A name assigned from different candidates on separate branches is ambiguous."""
        facts = self._facts("""
            def combine(left, right):
                return left[:1] + right[1:]
            values = [[1], [2]]
            first = values[0]
            second = values[1]
            if flag:
                maybe = first
            else:
                maybe = second
            result = combine(maybe, first)
        """)
        self.assertFalse(any(f.relation == CandidateRelation.DERIVED_FROM_TWO_CANDIDATES for f in facts.lineage))


class TestHelperFunctionSummaries(unittest.TestCase):

    def test_mutation_helper_tracks_candidate_argument_and_return(self):
        result = infer("""
            def mutate(individual):
                individual[0] += 1
                return individual
            population = create()
            for individual in population:
                child = mutate(individual)
        """)
        finding = result.for_role(EARole.MUTATION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.MEDIUM)
        self.assertEqual({item.kind for item in finding.evidence}, {"helper_mutation", "helper_call_site"})
        self.assertTrue(any(item.line == 3 for item in finding.evidence))
        self.assertTrue(any(item.line == 7 for item in finding.evidence))

    def test_fitness_helper_chain_maps_candidate_to_returned_score(self):
        result = infer("""
            def objective(candidate):
                return sum(candidate)
            def evaluate(candidate):
                return objective(candidate)
            population = create()
            for individual in population:
                fitness = evaluate(individual)
        """)
        finding = result.for_role(EARole.FITNESS_EVALUATION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.MEDIUM)
        self.assertTrue(any(item.kind == "helper_fitness_evaluation" and item.line == 3 for item in finding.evidence))
        self.assertTrue(any(item.kind == "helper_call_site" and item.line == 8 for item in finding.evidence))

    def test_selection_helper_returns_ranked_population_subset(self):
        result = infer("""
            def select(population):
                return sorted(population, key=objective)[:2]
            population = create()
            for individual in population:
                score = objective(individual)
            selected = select(population)
        """)
        finding = result.for_role(EARole.SELECTION)
        self.assertTrue(finding.detected)
        self.assertTrue(any(item.kind == "helper_selection" for item in finding.evidence))

    def test_crossover_helper_combines_two_candidate_arguments(self):
        result = infer("""
            def crossover(parent1, parent2):
                return parent1[:1] + parent2[1:]
            population = create()
            for parent1, parent2 in pairs(population):
                child = crossover(parent1, parent2)
        """)
        finding = result.for_role(EARole.CROSSOVER)
        self.assertTrue(finding.detected)
        self.assertTrue(any(item.kind == "helper_crossover" for item in finding.evidence))

    def test_replacement_helper_updates_and_returns_population(self):
        result = infer("""
            def replace(population, offspring):
                population[:] = offspring
                return population
            population = create()
            for individual in population:
                score = objective(individual)
            population = replace(population, offspring)
        """)
        finding = result.for_role(EARole.REPLACEMENT)
        self.assertTrue(finding.detected)
        self.assertTrue(any(item.kind == "helper_replacement" for item in finding.evidence))

    def test_replacement_helper_returns_rebuilt_collection(self):
        result = infer("""
            def replace(population, offspring):
                return population + offspring
            population = create()
            for individual in population:
                score = objective(individual)
            new_population = replace(population, offspring)
        """)
        finding = result.for_role(EARole.REPLACEMENT)
        self.assertTrue(finding.detected)
        self.assertTrue(any(item.kind == "helper_replacement" for item in finding.evidence))

    def test_termination_helper_used_by_ea_process_loop(self):
        result = infer("""
            def should_stop(population):
                return len(population) == 0
            population = create()
            while not should_stop(population):
                for individual in population:
                    score = objective(individual)
        """)
        finding = result.for_role(EARole.TERMINATION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.termination_kind, TerminationKind.CONDITION_BASED)
        self.assertTrue(any(item.kind == "helper_termination_condition" for item in finding.evidence))

    def test_helper_chain_propagates_mutation_summary(self):
        result = infer("""
            def mutate_one(candidate):
                candidate[0] += 1
                return candidate
            def mutate_wrapper(candidate):
                return mutate_one(candidate)
            population = create()
            for individual in population:
                child = mutate_wrapper(individual)
        """)
        finding = result.for_role(EARole.MUTATION)
        self.assertTrue(finding.detected)
        self.assertTrue(any("mutate_one" in item.description for item in finding.evidence))

    def test_ambiguous_return_paths_do_not_propagate_helper_role(self):
        result = infer("""
            def maybe_candidate(candidate):
                if flag:
                    return candidate
                return unrelated
            population = create()
            for individual in population:
                value = maybe_candidate(individual)
        """)
        self.assertFalse(result.for_role(EARole.FITNESS_EVALUATION).detected)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)

    def test_unresolved_helper_remains_low_confidence(self):
        result = infer("""
            def score_one(candidate):
                return unknown_operation(candidate)
            population = create()
            for individual in population:
                score = score_one(individual)
        """)
        finding = result.for_role(EARole.FITNESS_EVALUATION)
        self.assertFalse(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.LOW)
        self.assertTrue(any(item.kind == "helper_fitness_evaluation" for item in finding.evidence))

    def test_ordinary_helper_computation_is_not_ea_role(self):
        result = infer("""
            def increment(value):
                return value + 1
            values = [1, 2, 3]
            for value in values:
                answer = increment(value)
        """)
        self.assertFalse(any(finding.detected for finding in result.roles.values()))


class TestRegistrationDispatch(unittest.TestCase):

    def test_registered_function_invoked_by_generic_keyed_dispatch(self):
        result = infer("""
            def tweak(candidate):
                candidate[0] += 1
                return candidate
            registry = create_registry()
            registry_alias = registry
            registry_alias.register("operation", tweak)
            population = create_population()
            for candidate in population:
                child = registry.invoke_registered("operation", candidate)
        """)
        finding = result.for_role(EARole.MUTATION)
        self.assertTrue(finding.detected)
        kinds = {item.kind for item in finding.evidence}
        self.assertIn("registered_role", kinds)
        self.assertIn("registered_dispatch", kinds)
        self.assertTrue(any(item.line == 7 for item in finding.evidence))
        self.assertTrue(any(item.line == 10 for item in finding.evidence))

    def test_registered_callable_attribute_dispatch_is_generic(self):
        result = infer("""
            def tweak(candidate):
                candidate[0] += 1
                return candidate
            registry = create_registry()
            registry.register("mutation", tweak)
            population = create_population()
            for candidate in population:
                child = registry.mutation(candidate)
        """)
        self.assertTrue(result.for_role(EARole.MUTATION).detected)
        self.assertTrue(any(item.kind == "registered_dispatch" for item in result.for_role(EARole.MUTATION).evidence))

    def test_unresolved_registered_callable_is_not_classified(self):
        result = infer("""
            registry = create_registry()
            registry.register("mutation", missing_callback)
            population = create_population()
            for candidate in population:
                registry.mutation(candidate)
        """)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)

    def test_ambiguous_registration_is_not_classified(self):
        result = infer("""
            def first(candidate):
                candidate[0] += 1
                return candidate
            def second(candidate):
                candidate[1] += 1
                return candidate
            registry = create_registry()
            registry.register("mutation", first)
            registry.register("mutation", second)
            population = create_population()
            for candidate in population:
                registry.mutation(candidate)
        """)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)

    def test_non_ea_registration_does_not_create_role(self):
        result = infer("""
            def handle(value):
                return value + 1
            registry = create_registry()
            registry.register("handler", handle)
            registry.invoke_registered("handler", 3)
        """)
        self.assertFalse(any(finding.detected for finding in result.roles.values()))

    def test_deap_onemax_roles_are_detected_from_generic_dispatch(self):
        source_path = Path(__file__).parent.parent / "dataset/deap/ga/onemax.py"
        result = analyze_ea_roles(source_path.read_text(encoding="utf-8"), source_name=str(source_path))
        for role, finding in result.roles.items():
            with self.subTest(role=role):
                self.assertTrue(finding.detected)
                self.assertTrue(any(item.kind.startswith("registered_") for item in finding.evidence) or role in {EARole.REPLACEMENT, EARole.TERMINATION})
        mutation = result.for_role(EARole.MUTATION)
        self.assertEqual(mutation.confidence, EAConfidence.MEDIUM)
        self.assertFalse(any(item.kind == "candidate_modification" for item in mutation.evidence))

    def test_basic_string_roles_remain_visible_without_registration_semantics(self):
        source_path = Path(__file__).parent.parent / "Python/genetic_algorithm/basic_string.py"
        result = analyze_ea_roles(source_path.read_text(encoding="utf-8"), source_name=str(source_path))
        self.assertTrue(result.for_role(EARole.POPULATION).detected)
        self.assertTrue(result.for_role(EARole.FITNESS_EVALUATION).detected)
        self.assertTrue(result.for_role(EARole.TERMINATION).detected)
        for role in (EARole.SELECTION, EARole.MUTATION, EARole.CROSSOVER, EARole.REPLACEMENT):
            self.assertFalse(result.for_role(role).detected)


class TestBenchmarkDrivenFalsePositives(unittest.TestCase):

    def test_indexed_matrix_writes_are_not_population_mutation_or_crossover(self):
        result = infer("""
            rows = [[0] * 4 for _ in range(4)]
            for row in range(4):
                for col in range(4):
                    rows[row][col] = row + col
        """)
        self.assertFalse(any(finding.detected for finding in result.roles.values()))

    def test_index_inside_subscript_is_not_a_candidate_write(self):
        result = infer("""
            candidates = create()
            table = {}
            for candidate in candidates:
                table[candidate] = objective(candidate)
        """)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)

    def test_derived_score_is_not_a_crossover_parent(self):
        result = infer("""
            population = create()
            best_score = 0
            for candidate in population:
                best_score = max(best_score, sum(candidate))
        """)
        self.assertFalse(result.for_role(EARole.CROSSOVER).detected)

    def test_builtin_two_argument_call_is_not_crossover(self):
        result = infer("""
            population = create()
            for first, second in pairs(population):
                child = max(first, second)
        """)
        self.assertFalse(result.for_role(EARole.CROSSOVER).detected)

    def test_unrelated_two_argument_helper_is_not_crossover(self):
        result = infer("""
            def combine(a, b):
                return a + b
            total = combine(3, 4)
        """)
        self.assertFalse(result.for_role(EARole.CROSSOVER).detected)


class TestBenchmarkDrivenFalseNegatives(unittest.TestCase):

    def test_helper_crossover_with_tuple_element_parents(self):
        result = infer("""
            def recombine(left, right):
                point = len(left) // 2
                return left[:point] + right[point:]
            population = create()
            for candidate in population:
                score = sum(candidate)
            first, second = population[0], population[1]
            child = recombine(first, second)
        """)
        finding = result.for_role(EARole.CROSSOVER)
        self.assertTrue(finding.detected)
        self.assertTrue(any(item.kind == "helper_crossover" and item.line == 4 for item in finding.evidence))
        self.assertTrue(any(item.kind == "helper_call_site" and item.line == 9 for item in finding.evidence))

    def test_helper_mutating_and_returning_a_copy(self):
        result = infer("""
            def mutate(candidate):
                changed = candidate.copy()
                changed[0] = 1 - changed[0]
                return changed
            population = create()
            for individual in population:
                score = sum(individual)
                child = mutate(individual)
        """)
        finding = result.for_role(EARole.MUTATION)
        self.assertTrue(finding.detected)
        self.assertTrue(any(item.kind == "helper_mutation" and item.line == 4 for item in finding.evidence))

    def test_helper_copy_modified_but_not_returned_is_not_mutation(self):
        result = infer("""
            def inspect(candidate):
                scratch = candidate.copy()
                scratch[0] = 0
                return len(candidate)
            population = create()
            for individual in population:
                size = inspect(individual)
        """)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)

    def test_copied_selected_candidate_written_through_alias(self):
        result = infer("""
            population = create()
            for individual in population:
                score = sum(individual)
            parents = sorted(population, key=sum)
            child = parents[0].copy()
            child_alias = child
            child_alias[0] = 1
        """)
        finding = result.for_role(EARole.MUTATION)
        self.assertTrue(finding.detected)
        self.assertEqual(finding.confidence, EAConfidence.MEDIUM)
        self.assertTrue(any(item.kind == "candidate_copy_modification" and item.line == 8 for item in finding.evidence))

    def test_copy_of_unrelated_list_is_not_mutation(self):
        result = infer("""
            settings = load()
            local = settings.copy()
            local[0] = 1
        """)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)

    def test_registered_builtin_ranking_is_selection(self):
        result = infer("""
            def evaluate(candidate):
                return sum(candidate)
            toolbox = create_toolbox()
            toolbox.register("evaluate", evaluate)
            toolbox.register("select", sorted)
            population = make()
            for individual in population:
                fitness = toolbox.evaluate(individual)
            selected = toolbox.select(population, key=evaluate)
        """)
        finding = result.for_role(EARole.SELECTION)
        self.assertTrue(finding.detected)
        self.assertTrue(any(item.kind == "registered_dispatch" and item.line == 10 for item in finding.evidence))

    def test_registered_builtin_with_conflicting_key_is_not_classified(self):
        result = infer("""
            toolbox = create_toolbox()
            toolbox.register("mutate", sorted)
            population = make()
            for individual in population:
                score = sum(individual)
            out = toolbox.mutate(population)
        """)
        self.assertFalse(result.for_role(EARole.MUTATION).detected)
        self.assertFalse(result.for_role(EARole.SELECTION).detected)

    def test_population_slice_reused_in_rebuild_is_selection(self):
        result = infer("""
            population = create()
            for candidate in population:
                score = sum(candidate)
            survivors = population[:1]
            population[:] = survivors + offspring
        """)
        finding = result.for_role(EARole.SELECTION)
        self.assertTrue(finding.detected)
        self.assertEqual({item.kind for item in finding.evidence}, {"survivor_slice", "survivor_slice_use"})

    def test_population_slice_not_reused_is_not_selection(self):
        result = infer("""
            population = create()
            for candidate in population:
                score = sum(candidate)
            preview = population[:3]
            print(preview)
        """)
        self.assertFalse(result.for_role(EARole.SELECTION).detected)


if __name__ == "__main__":
    unittest.main()