"""Replacement detection: populations rebuilt from or updated with selected/offspring candidates."""

from __future__ import annotations

import ast

from .._ast_utils import _local_name, _names, _target_names
from .._context import EAAnalysisContext, EADetector, ObservationCollector, RoleObservation
from .._data_flow import DataFlowKind
from .._model import EAConfidence, EARole
from .._structure import CandidateRelation


class ReplacementDetector(EADetector):
    def _detect_slice_replacement(self, context: EAAnalysisContext, found: ObservationCollector) -> None:
        for fact in context.data_flow.facts:
            if fact.kind != DataFlowKind.SLICE_REPLACEMENT or not fact.target:
                continue
            target_names = set(fact.target_names)
            if not target_names & context.state.population_names:
                continue
            node = next((
                item for item in context.nodes
                if isinstance(item, ast.Assign)
                and getattr(item, "lineno", None) == fact.location.line
                and any(
                    isinstance(target, ast.Subscript)
                    and _names(target.value) & target_names
                    and isinstance(target.slice, ast.Slice)
                    for target in item.targets
                )
            ), None)
            if node is not None:
                found.add(
                    EARole.REPLACEMENT,
                    context.evidence("population_slice_replacement", "A statically resolved alias of an inferred population is replaced by slice assignment.", node),
                    EAConfidence.HIGH,
                )

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        population_names = set(state.population_names)
        for node in context.nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                target = node.targets[0] if isinstance(node, ast.Assign) else node.target
                value = node.value
                assigned_names = _target_names(target)
                if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add) and assigned_names & population_names:
                    source_names = _names(value)
                    if source_names & (state.selection_names | state.offspring_names) or len(source_names) >= 2:
                        found.add(EARole.REPLACEMENT, context.evidence("population_reconstruction", "A candidate collection is replaced by a newly composed collection.", node), EAConfidence.HIGH)
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id in population_names:
                    found.add(EARole.REPLACEMENT, context.evidence("survivor_replacement", "An element of an inferred candidate collection is replaced.", node), EAConfidence.HIGH)

            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                collection = node.func.value.id
                if collection not in population_names or node.func.attr not in {"append", "extend", "insert", "update"}:
                    continue
                added_names = set().union(*(_names(arg) for arg in node.args)) if node.args else set()
                if added_names & state.offspring_names or (node.func.attr == "extend" and added_names & state.selection_names):
                    found.add(EARole.REPLACEMENT, context.evidence("offspring_insertion", "Offspring or selected candidates are inserted into an inferred population.", node), EAConfidence.HIGH)

            # Invoked per node (deduplicated by add) to keep the original evidence ordering.
            self._detect_slice_replacement(context, found)

        for fact in context.lineage.lineage:
            if fact.relation not in {
                CandidateRelation.INSERTED_INTO_COLLECTION,
                CandidateRelation.REPLACED_IN_COLLECTION,
            }:
                continue
            if _local_name(fact.source_collection) not in population_names:
                continue
            if fact.relation == CandidateRelation.INSERTED_INTO_COLLECTION:
                inserted_names = set(_names(fact.node))
                if not inserted_names & (state.selection_names | state.offspring_names):
                    continue
            elif not set(_names(fact.node)) & (state.selection_names | state.offspring_names):
                continue
            found.add(
                EARole.REPLACEMENT,
                context.evidence("candidate_lineage_replacement", fact.evidence, fact.node),
                fact.confidence,
            )
        return found.observations()
