"""Stateless EA detectors sharing the ``detect(context) -> list[RoleObservation]`` API."""

from .cross_role import HelperSummaryDetector, RegisteredDispatchDetector
from .crossover import CrossoverDetector
from .fitness import FitnessDetector
from .mutation import MutationDetector
from .population import PopulationDetector
from .replacement import ReplacementDetector
from .selection import SelectionDetector, SurvivorSliceSelectionDetector
from .termination import TerminationDetector

__all__ = [
    "CrossoverDetector",
    "FitnessDetector",
    "HelperSummaryDetector",
    "MutationDetector",
    "PopulationDetector",
    "RegisteredDispatchDetector",
    "ReplacementDetector",
    "SelectionDetector",
    "SurvivorSliceSelectionDetector",
    "TerminationDetector",
]
