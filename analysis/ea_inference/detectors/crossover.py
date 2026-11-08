"""Crossover detection: offspring composed from two or more candidate sources."""

from __future__ import annotations

import ast

from .._ast_utils import _local_name, _names, _target_names
from .._context import EAAnalysisContext, EADetector, ObservationCollector, RoleObservation
from .._model import EAConfidence, EARole
from .._structure import CandidateRelation


_NON_RECOMBINING_BUILTINS = {
    "abs", "all", "any", "enumerate", "filter", "isinstance", "len", "map",
    "max", "min", "print", "range", "round", "sorted", "sum", "zip",
}


class CrossoverDetector(EADetector):
    @staticmethod
    def _candidate_refs(context: EAAnalysisContext, node: ast.AST) -> set[str]:
        state = context.state
        refs = _names(node) & state.candidate_names
        for item in ast.walk(node):
            if isinstance(item, ast.Subscript) and isinstance(item.value, ast.Name):
                if item.value.id in state.population_names | state.selection_names:
                    refs.add(f"{item.value.id}[candidate]")
        return refs

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        parent_aliases: set[str] = set(state.candidate_names)
        for node in context.nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                target = node.targets[0] if isinstance(node, ast.Assign) else node.target
                if isinstance(value, ast.Subscript) and isinstance(value.value, ast.Name) and value.value.id in state.population_names | state.selection_names:
                    parent_aliases.update(_target_names(target))

        for node in context.nodes:
            if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
                continue
            left_refs = self._candidate_refs(context, node.left) | (_names(node.left) & parent_aliases)
            right_refs = self._candidate_refs(context, node.right) | (_names(node.right) & parent_aliases)
            combined = left_refs | right_refs
            has_slices = any(isinstance(item, ast.Slice) for item in ast.walk(node))
            if len(combined) < 2 or not (has_slices or (left_refs and right_refs)):
                continue
            found.add(EARole.CROSSOVER, context.evidence("multi_parent_recombination", "A combined representation is constructed from at least two candidate sources.", node), EAConfidence.HIGH if has_slices else EAConfidence.MEDIUM)
            state.offspring_names.update(context.direct_assignment_target_names(node))

        for fact in context.lineage.lineage:
            if fact.relation != CandidateRelation.DERIVED_FROM_TWO_CANDIDATES:
                continue
            if _local_name(fact.source_collection) not in state.population_names | state.selection_names:
                continue
            if len(set(fact.source_candidates)) < 2:
                continue
            found.add(
                EARole.CROSSOVER,
                context.evidence("candidate_lineage_two_parent_dependency", fact.evidence, fact.node),
                fact.confidence,
            )
            state.offspring_names.add(fact.destination.rsplit(":", 1)[-1])

        for node in context.nodes:
            if not isinstance(node, ast.Call) or len(node.args) < 2:
                continue
            if isinstance(node.func, ast.Name) and node.func.id in _NON_RECOMBINING_BUILTINS:
                continue
            arg_refs = [self._candidate_refs(context, arg) | (_names(arg) & parent_aliases) for arg in node.args]
            if len(set().union(*arg_refs)) < 2 or not all(arg_refs[:2]):
                continue
            loop = context.in_loop(node)
            if not (loop and set(loop.iterable_names) & (state.population_names | state.selection_names)):
                continue
            found.add(EARole.CROSSOVER, context.evidence("multi_parent_call", "A transformation call consumes two candidate sources in an evolutionary collection loop.", node), EAConfidence.MEDIUM)
            state.offspring_names.update(context.enclosing_assignment_target_names(node))
        return found.observations()
