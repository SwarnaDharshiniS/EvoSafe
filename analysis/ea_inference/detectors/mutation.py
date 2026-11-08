"""Mutation detection: in-place or copy-then-write modification of candidates."""

from __future__ import annotations

import ast

from .._ast_utils import (
    _copy_source,
    _has_name,
    _is_fitness_metadata_target,
    _local_name,
    _names,
    _root_name,
    _target_names,
)
from .._context import EAAnalysisContext, EADetector, ObservationCollector, RoleObservation
from .._model import EAConfidence, EARole
from .._structure import CandidateRelation


class MutationDetector(EADetector):
    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        found = ObservationCollector()
        self._detect_candidate_modification(context, found)
        self._detect_copied_candidate_modification(context, found)
        return found.observations()

    def _detect_candidate_modification(self, context: EAAnalysisContext, found: ObservationCollector) -> None:
        state = context.state
        for info in context.loops:
            loop = info.node
            if not isinstance(loop, (ast.For, ast.AsyncFor)) or not (set(info.iterable_names) & state.population_names):
                continue
            aliases = set(info.target_names)
            body = context.loop_body_nodes(loop)
            for node in body:
                if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                    continue
                value = node.value
                target_nodes = node.targets if isinstance(node, ast.Assign) else [node.target]
                source_names = _names(value)
                for target_node in target_nodes:
                    target_names = _target_names(target_node)
                    if not (target_names & aliases):
                        continue
                    is_copy = (
                        isinstance(value, ast.Call)
                        and isinstance(value.func, ast.Attribute)
                        and value.func.attr in {"copy", "clone", "copyto"}
                        and _has_name(value.func.value, aliases)
                    )
                    if not (source_names & aliases) and not is_copy:
                        aliases.difference_update(target_names)
                if isinstance(value, ast.Name) and value.id in aliases:
                    for target_node in target_nodes:
                        aliases.update(_target_names(target_node))
                for alias_name in tuple(aliases):
                    aliases.update(context.data_flow.alias_group(
                        alias_name,
                        scope=context.data_flow.scope_for(loop),
                        line=getattr(node, "lineno", None),
                    ))
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr in {"copy", "clone", "copyto"} and _has_name(value.func.value, aliases):
                    target = node.targets[0] if isinstance(node, ast.Assign) else node.target
                    aliases.update(_target_names(target))
                elif isinstance(value, (ast.BinOp, ast.List, ast.Tuple, ast.Subscript)) and _has_name(value, aliases):
                    target = node.targets[0] if isinstance(node, ast.Assign) else node.target
                    aliases.update(_target_names(target))

            for node in body:
                if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                    continue
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if not isinstance(target, (ast.Subscript, ast.Attribute)) or _root_name(target) not in aliases:
                        continue
                    if _is_fitness_metadata_target(target):
                        continue
                    found.add(EARole.MUTATION, context.evidence("candidate_modification", "A candidate or its alias is modified through an element or attribute update.", node), EAConfidence.HIGH)
                    state.offspring_names.update(_names(target) & aliases)
            for node in body:
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr in {"append", "insert", "pop", "remove", "clear", "sort", "reverse"} and _has_name(node.func.value, aliases):
                    found.add(EARole.MUTATION, context.evidence("candidate_in_place_operation", "A candidate collection or representation is modified in place.", node), EAConfidence.MEDIUM)

        for fact in context.lineage.lineage:
            if fact.relation != CandidateRelation.MUTATED_CANDIDATE:
                continue
            collection_name = _local_name(fact.source_collection)
            candidate_name = fact.destination.rsplit(":", 1)[-1]
            if collection_name not in state.population_names and candidate_name not in state.candidate_names:
                continue
            found.add(
                EARole.MUTATION,
                context.evidence("candidate_lineage_mutation", fact.evidence, fact.node),
                EAConfidence.MEDIUM,
            )

    def _detect_copied_candidate_modification(self, context: EAAnalysisContext, found: ObservationCollector) -> None:
        """Copy of a population/selected element whose contents are then written."""
        state = context.state
        collections = state.population_names | state.selection_names | state.candidate_names
        copies: dict[str, ast.AST] = {}
        for node in context.nodes:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue
            if _root_name(_copy_source(node.value)) in collections:
                copies[node.targets[0].id] = node
        if not copies:
            return
        explained_lines = state.observed_lines(EARole.MUTATION) | found.observed_lines(EARole.MUTATION)
        for node in context.nodes:
            if not isinstance(node, (ast.Assign, ast.AugAssign)):
                continue
            if getattr(node, "lineno", None) in explained_lines:
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if not isinstance(target, (ast.Subscript, ast.Attribute)) or _is_fitness_metadata_target(target):
                    continue
                root = _root_name(target)
                if root is None:
                    continue
                group = context.data_flow.alias_group(
                    root, scope=context.data_flow.scope_for(node), line=getattr(node, "lineno", None),
                )
                origin = next((copies[name] for name in sorted(group) if name in copies), None)
                if origin is None or getattr(origin, "lineno", 0) > getattr(node, "lineno", 0):
                    continue
                found.add(EARole.MUTATION, context.evidence("candidate_copy", "A population or selected candidate is copied.", origin), EAConfidence.MEDIUM)
                found.add(EARole.MUTATION, context.evidence("candidate_copy_modification", "The candidate copy (or an alias of it) is modified through an element or attribute write.", node), EAConfidence.MEDIUM)
                state.offspring_names.update(group)
