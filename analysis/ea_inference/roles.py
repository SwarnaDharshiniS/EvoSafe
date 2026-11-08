"""Layer 3 — role detection: runs detectors over structure and lineage, yielding typed role observations."""

from __future__ import annotations

from dataclasses import dataclass

from ._context import (
    EAAnalysisContext,
    EADetector,
    RoleBindings,
    RoleObservation,
    bind_population_element_aliases,
)
from .detectors import (
    CrossoverDetector,
    FitnessDetector,
    HelperSummaryDetector,
    MutationDetector,
    PopulationDetector,
    RegisteredDispatchDetector,
    ReplacementDetector,
    SelectionDetector,
    SurvivorSliceSelectionDetector,
    TerminationDetector,
)
from .lineage import CandidateLineage
from .structural import StructuralAnalysis


@dataclass(frozen=True)
class RoleDetectionResult:
    observations: tuple[RoleObservation, ...]


def _apply(detector: EADetector, context: EAAnalysisContext) -> None:
    context.state.observations.extend(detector.detect(context))


def detect_roles(structure: StructuralAnalysis, lineage: CandidateLineage) -> RoleDetectionResult:
    """Layer entry point."""
    context = EAAnalysisContext(structure=structure, lineage=lineage, state=RoleBindings())
    # Order matters: each step reads role bindings and observations produced by earlier ones.
    _apply(PopulationDetector(), context)
    _apply(FitnessDetector(), context)
    _apply(RegisteredDispatchDetector(), context)
    bind_population_element_aliases(context)
    _apply(HelperSummaryDetector(), context)
    _apply(SelectionDetector(), context)
    _apply(MutationDetector(), context)
    _apply(CrossoverDetector(), context)
    _apply(ReplacementDetector(), context)
    _apply(SurvivorSliceSelectionDetector(), context)
    _apply(TerminationDetector(), context)
    return RoleDetectionResult(tuple(context.state.observations))
