"""Selection detection: ranking, filtering, sampling, and survivor slicing of populations."""

from __future__ import annotations

import ast

from .._ast_utils import _call_name, _local_name, _names, _root_name
from .._context import EAAnalysisContext, EADetector, ObservationCollector, RoleObservation
from .._model import EAConfidence, EARole
from .._structure import CandidateRelation


_SELECTION_CALLS = {
    "sorted", "sort", "min", "max", "filter", "sample", "choice",
    "choices", "nsmallest", "nlargest", "argmin", "argmax",
}


class SelectionDetector(EADetector):
    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        for node in context.nodes:
            if isinstance(node, ast.Call) and _call_name(node) in _SELECTION_CALLS:
                refs = _names(node) & state.population_names
                has_key = any(keyword.arg == "key" for keyword in node.keywords)
                if not refs or not (has_key or _call_name(node) in {"sort", "filter", "sample", "choice", "choices", "min", "max", "nsmallest", "nlargest", "argmin", "argmax"}):
                    continue
                confidence = EAConfidence.HIGH if has_key and _call_name(node) in {"sorted", "sort"} else EAConfidence.MEDIUM
                found.add(EARole.SELECTION, context.evidence("rank_or_filter", "A ranking, filtering, or sampling operation consumes an inferred candidate collection.", node), confidence)
                state.selection_names.update(context.enclosing_assignment_target_names(node))

            if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
                for generator in node.generators:
                    if not (_names(generator.iter) & state.population_names):
                        continue
                    if not generator.ifs:
                        continue
                    found.add(EARole.SELECTION, context.evidence("candidate_filter", "A comprehension filters an inferred candidate collection by a condition.", node), EAConfidence.MEDIUM)
                    state.selection_names.update(context.direct_assignment_target_names(node))

        for fact in context.lineage.lineage:
            if fact.relation != CandidateRelation.SELECTED_FROM_COLLECTION:
                continue
            if isinstance(fact.node, (ast.Assign, ast.AnnAssign)):
                value = fact.node.value
                if isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Slice):
                    continue
            if _local_name(fact.source_collection) not in state.population_names:
                continue
            found.add(
                EARole.SELECTION,
                context.evidence("candidate_lineage_selection", fact.evidence, fact.node),
                fact.confidence,
            )
            state.selection_names.add(fact.destination.rsplit(":", 1)[-1])
        return found.observations()


class SurvivorSliceSelectionDetector(EADetector):
    """Selection evidence for a population slice carried into a rebuild; runs after replacement."""

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        slices: dict[str, ast.Assign] = {}
        for node in context.nodes:
            if (
                isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Subscript) and isinstance(node.value.slice, ast.Slice)
                and isinstance(node.value.value, ast.Name) and node.value.value.id in state.population_names
            ):
                slices[node.targets[0].id] = node
        for node in context.nodes:
            if not isinstance(node, ast.Assign) or not slices:
                continue
            if not any(_root_name(target) in state.population_names for target in node.targets):
                continue
            for name in sorted(_names(node.value) & set(slices)):
                found.add(EARole.SELECTION, context.evidence("survivor_slice", "A slice of the population is retained as survivors.", slices[name]), EAConfidence.MEDIUM)
                found.add(EARole.SELECTION, context.evidence("survivor_slice_use", "The retained slice is used to rebuild the population.", node), EAConfidence.MEDIUM)
                state.selection_names.add(name)
        return found.observations()
