"""Population detection: candidate collections iterated by evaluation or reproduction logic."""

from __future__ import annotations

import ast

from .._ast_utils import (
    _call_name,
    _copy_source,
    _has_name,
    _is_fitness_metadata_target,
    _is_index_iteration,
    _local_name,
    _names,
    _root_name,
    _target_names,
)
from .._context import (
    CandidateAssignment,
    CandidateComprehensionScan,
    CandidateLoopScan,
    EAAnalysisContext,
    EADetector,
    ObservationCollector,
    PopulationScan,
    RoleObservation,
)
from .._model import EAConfidence, EARole
from .._structure import CandidateRelation


_FITNESS_WORDS = {"evaluate", "evaluation", "fitness", "objective", "score", "loss"}
_SUMMARIZED_OPERATION_ROLES = frozenset({
    EARole.FITNESS_EVALUATION,
    EARole.MUTATION,
    EARole.CROSSOVER,
    EARole.SELECTION,
    EARole.REPLACEMENT,
})


class PopulationDetector(EADetector):
    """Emits population evidence and records candidate-consuming calls for ``FitnessDetector``."""

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        found = ObservationCollector()
        loops = self._scan_candidate_loops(context, found)
        comprehensions = self._scan_candidate_comprehensions(context, found)
        context.state.population_scan = PopulationScan(loops, comprehensions)
        return found.observations()

    def _scan_candidate_loops(
        self, context: EAAnalysisContext, found: ObservationCollector,
    ) -> tuple[CandidateLoopScan, ...]:
        state = context.state
        scans: list[CandidateLoopScan] = []
        for info in context.loops:
            loop = info.node
            if not isinstance(loop, (ast.For, ast.AsyncFor)) or not info.target_names:
                continue
            if _is_index_iteration(loop.iter):
                continue
            body = context.loop_body_nodes(loop)
            scope = context.data_flow.scope_for(loop)
            candidate_bindings = set(info.target_names)
            for statement in sorted(body, key=lambda item: (getattr(item, "lineno", 0), getattr(item, "col_offset", 0))):
                line = getattr(statement, "lineno", None)
                for candidate_name in tuple(candidate_bindings):
                    candidate_bindings.update(context.data_flow.alias_group(candidate_name, scope=scope, line=line))
                if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                    value = statement.value
                    copied = _copy_source(value)
                    # Only identity aliases and copies stay candidates; derived values (scores, sums) do not.
                    if (
                        isinstance(value, ast.Name) and value.id in candidate_bindings
                    ) or (copied is not None and _root_name(copied) in candidate_bindings):
                        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                        candidate_bindings.update(set().union(*(_target_names(target) for target in targets)))
            target_used = any(_has_name(node, set(info.target_names)) for node in body)
            if not target_used:
                continue

            candidate_calls = [
                call for node in body if isinstance(node, ast.Call)
                for call in [node]
                if _has_name(call, candidate_bindings)
            ]
            score_calls = [
                call for call in candidate_calls
                if any(word in _call_name(call) for word in _FITNESS_WORDS)
                and context.summaries.for_call(call) is None
            ]
            assigned_candidate_calls: list[CandidateAssignment] = []
            for statement in body:
                if not isinstance(statement, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                    continue
                value = statement.value
                if isinstance(value, ast.Call) and _has_name(value, candidate_bindings):
                    assigned_candidate_calls.append((statement, value))

            mutations = []
            for node in body:
                if not isinstance(node, (ast.AugAssign, ast.Assign, ast.AnnAssign)):
                    continue
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(
                    isinstance(target, (ast.Subscript, ast.Attribute))
                    and not _is_fitness_metadata_target(target)
                    and _root_name(target) in candidate_bindings
                    for target in targets
                ):
                    mutations.append(node)
            parent_combinations = [
                node for node in body if isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Add)
                and len(_names(node) & candidate_bindings) >= 2
            ]
            summarized_calls = []
            uncertain_summary_calls = []
            unresolved_direct_calls = []
            for _, call in assigned_candidate_calls:
                summary = context.summaries.for_call(call)
                if summary is None:
                    unresolved_direct_calls.append(call)
                elif any(
                    item.role in _SUMMARIZED_OPERATION_ROLES
                    for item in summary.role_evidence
                ) and not any(
                    item.certainty != EAConfidence.LOW and item.role in _SUMMARIZED_OPERATION_ROLES
                    for item in summary.role_evidence
                ):
                    uncertain_summary_calls.append(call)
                elif any(
                    item.certainty != EAConfidence.LOW and item.role in _SUMMARIZED_OPERATION_ROLES
                    for item in summary.role_evidence
                ):
                    summarized_calls.append(call)
            structural_operation = bool(
                unresolved_direct_calls or summarized_calls or mutations or parent_combinations
            )
            named_evaluation = bool(score_calls)
            # A framework-neutral candidate iteration plus candidate-consuming
            # evaluation/reproduction is needed; collection and variable names
            # alone are deliberately insufficient.
            if not (structural_operation or named_evaluation or uncertain_summary_calls):
                continue

            collection_name = next(iter(sorted(info.iterable_names)), None)
            evidence = context.evidence(
                "candidate_iteration",
                "A loop iterates a collection and uses each element in candidate evaluation or reproduction logic.",
                loop,
            )
            population_confidence = (
                EAConfidence.LOW if uncertain_summary_calls and not (structural_operation or named_evaluation)
                else EAConfidence.HIGH if collection_name and (structural_operation or named_evaluation)
                else EAConfidence.MEDIUM
            )
            found.add(EARole.POPULATION, evidence, population_confidence)
            if collection_name:
                scope = context.data_flow.scope_for(loop)
                state.population_names.update(
                    context.data_flow.alias_group(
                        collection_name,
                        scope=scope,
                        line=getattr(loop, "lineno", None),
                    )
                )
            state.candidate_names.update(candidate_bindings)
            for candidate in context.lineage.candidates:
                if candidate.relation != CandidateRelation.ELEMENT_OF_COLLECTION:
                    continue
                if candidate.location.line != getattr(loop, "lineno", None):
                    continue
                if _local_name(candidate.source_collection) in info.iterable_names:
                    state.candidate_names.add(candidate.candidate.rsplit(":", 1)[-1].split("@", 1)[0])

            scans.append(CandidateLoopScan(tuple(assigned_candidate_calls), tuple(score_calls)))
        return tuple(scans)

    def _scan_candidate_comprehensions(
        self, context: EAAnalysisContext, found: ObservationCollector,
    ) -> tuple[CandidateComprehensionScan, ...]:
        state = context.state
        scans: list[CandidateComprehensionScan] = []
        for node in context.nodes:
            if not isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
                continue
            for generator in node.generators:
                iter_names = _names(generator.iter)
                candidate_names = _target_names(generator.target)
                if not iter_names or not candidate_names or _is_index_iteration(generator.iter):
                    continue
                calls = [
                    item for item in ast.walk(node.elt)
                    if isinstance(item, ast.Call) and _has_name(item, candidate_names)
                ]
                if not calls:
                    continue
                scope = context.data_flow.scope_for(node)
                aliases = set().union(*(
                    context.data_flow.alias_group(name, scope=scope, line=getattr(node, "lineno", None))
                    for name in iter_names
                ))
                evidence = context.evidence(
                    "candidate_comprehension",
                    "A comprehension invokes a computation on each element of a collection; generator and call source locations are retained.",
                    node,
                )
                found.add(EARole.POPULATION, evidence, EAConfidence.MEDIUM)
                state.population_names.update(aliases)
                state.candidate_names.update(candidate_names)
                scans.append(CandidateComprehensionScan(node, tuple(calls)))
        return tuple(scans)
