"""Fitness-evaluation detection: computations that consume individual candidates."""

from __future__ import annotations

import ast

from .._ast_utils import _copy_source, _local_name, _target_names
from .._context import EAAnalysisContext, EADetector, ObservationCollector, RoleObservation
from .._model import EAConfidence, EARole
from .._structure import CandidateRelation


class FitnessDetector(EADetector):
    """Consumes ``state.population_scan``; must run after ``PopulationDetector``."""

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        scan = state.population_scan
        for loop_scan in scan.loops:
            for statement, call in loop_scan.assigned_candidate_calls:
                summary = context.summaries.for_call(call)
                if summary is not None:
                    continue
                # Copies and registered dispatches are handled by their own role evidence.
                if _copy_source(call) is not None or context.data_flow.dispatch_for_call(call):
                    continue
                found.add(
                    EARole.FITNESS_EVALUATION,
                    context.evidence("candidate_dependent_call", "A computed value depends on a candidate passed to a call.", statement),
                    EAConfidence.HIGH,
                )
                state.fitness_names.update(_target_names(statement.targets[0] if isinstance(statement, ast.Assign) else statement.target))
            for call in loop_scan.score_calls:
                found.add(
                    EARole.FITNESS_EVALUATION,
                    context.evidence("candidate_evaluation_call", "A candidate is consumed by an evaluation-like computation inside collection iteration.", call),
                    EAConfidence.MEDIUM if not loop_scan.assigned_candidate_calls else EAConfidence.HIGH,
                )
                state.fitness_names.update(context.assigned_names(call))

        for comprehension in scan.comprehensions:
            for call in comprehension.calls:
                found.add(
                    EARole.FITNESS_EVALUATION,
                    context.evidence(
                        "comprehension_candidate_call",
                        "A call consumes the comprehension's candidate variable while iterating a collection.",
                        call,
                    ),
                    EAConfidence.MEDIUM,
                )
            state.fitness_names.update(context.direct_assignment_target_names(comprehension.node))

        for fact in context.lineage.lineage:
            if fact.relation != CandidateRelation.COMPUTED_FROM_CANDIDATE:
                continue
            if _local_name(fact.source_collection) not in state.population_names:
                continue
            found.add(
                EARole.FITNESS_EVALUATION,
                context.evidence("candidate_lineage_computation", fact.evidence, fact.node),
                fact.confidence,
            )
            state.fitness_names.add(fact.destination.rsplit(":", 1)[-1])
        return found.observations()
