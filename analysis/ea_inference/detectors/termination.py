"""Termination detection: classification of the evolutionary process loop's stopping behavior."""

from __future__ import annotations

import ast

from .._ast_utils import _call_name, _local_name, _names
from .._context import EAAnalysisContext, EADetector, ObservationCollector, RoleObservation
from .._model import EAConfidence, EARole, TerminationKind


class TerminationDetector(EADetector):
    """Must run last: EA-loop recognition reads the other roles' merged evidence."""

    @staticmethod
    def _loop_has_ea_evidence(context: EAAnalysisContext, loop: ast.For | ast.AsyncFor | ast.While) -> bool:
        state = context.state
        if isinstance(loop, (ast.For, ast.AsyncFor)) and set(_names(loop.iter)) & state.population_names:
            return True
        start = getattr(loop, "lineno", -1)
        end = getattr(loop, "end_lineno", start)
        if any(
            fact.location.line is not None and start <= fact.location.line <= end
            and _local_name(fact.source_collection) in state.population_names
            for fact in context.lineage.candidates
        ):
            return True
        roles = (EARole.FITNESS_EVALUATION, EARole.SELECTION, EARole.MUTATION, EARole.CROSSOVER, EARole.REPLACEMENT)
        if any(line is not None and start <= line <= end for line in state.observed_lines(*roles)):
            return True
        return any(isinstance(node, (ast.For, ast.AsyncFor)) and set(_names(node.iter)) & state.population_names for node in context.loop_body_nodes(loop))

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        for info in context.loops:
            loop = info.node
            if not self._loop_has_ea_evidence(context, loop):
                continue
            if isinstance(loop, (ast.For, ast.AsyncFor)) and set(_names(loop.iter)) & (state.population_names | state.selection_names):
                continue
            ancestor = context.parent.get(loop)
            nested_in_ea_loop = False
            while ancestor is not None:
                if isinstance(ancestor, (ast.For, ast.AsyncFor, ast.While)) and self._loop_has_ea_evidence(context, ancestor):
                    nested_in_ea_loop = True
                    break
                ancestor = context.parent.get(ancestor)
            if nested_in_ea_loop:
                continue
            if isinstance(loop, (ast.For, ast.AsyncFor)):
                bounded = isinstance(loop.iter, (ast.List, ast.Tuple, ast.Set, ast.Dict))
                if isinstance(loop.iter, ast.Call):
                    bounded = _call_name(loop.iter) in {"range", "enumerate", "zip"}
                kind = TerminationKind.STATICALLY_BOUNDED if bounded else TerminationKind.UNKNOWN_OR_UNBOUNDED
                reason = "The evolutionary loop iterates a finite built-in range or literal collection." if bounded else "The iterable's termination bound cannot be established structurally."
            elif isinstance(loop.test, ast.Constant) and loop.test.value in (True, 1):
                kind = TerminationKind.UNKNOWN_OR_UNBOUNDED
                reason = "The evolutionary loop has a constant-true condition and no statically established exit."
            else:
                kind = TerminationKind.CONDITION_BASED
                reason = "The evolutionary loop is controlled by a runtime condition."
            found.add(
                EARole.TERMINATION, context.evidence("loop_termination", reason, loop),
                EAConfidence.HIGH if kind == TerminationKind.STATICALLY_BOUNDED else EAConfidence.MEDIUM,
                termination_kind=kind,
            )
        self._detect_helper_termination(context, found)
        return found.observations()

    def _detect_helper_termination(self, context: EAAnalysisContext, found: ObservationCollector) -> None:
        state = context.state
        for info in context.loops:
            loop = info.node
            if not isinstance(loop, ast.While) or not self._loop_has_ea_evidence(context, loop):
                continue
            for call in (node for node in ast.walk(loop.test) if isinstance(node, ast.Call)):
                summary = context.summaries.for_call(call)
                if summary is None or not summary.return_resolved:
                    continue
                for evidence in summary.role_evidence:
                    if evidence.role != EARole.TERMINATION or evidence.certainty == EAConfidence.LOW:
                        continue
                    actual_names = set().union(*(_names(arg) for arg in call.args)) if call.args else set()
                    if not (actual_names & (state.population_names | state.candidate_names | state.fitness_names)):
                        continue
                    found.add(
                        EARole.TERMINATION,
                        context.evidence("helper_termination_condition", evidence.description, evidence.node),
                        EAConfidence.MEDIUM,
                    )
                    found.add(
                        EARole.TERMINATION,
                        context.evidence("helper_termination_call", "The EA process loop uses a locally summarized condition helper.", call),
                        EAConfidence.MEDIUM,
                        termination_kind=TerminationKind.CONDITION_BASED,
                    )
                    break
