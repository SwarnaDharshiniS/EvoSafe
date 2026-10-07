"""Optional structural inference of evolutionary-algorithm roles."""

from ._model import (
    EAConfidence,
    EAEvidence,
    EAInferenceReport,
    EARole,
    EARoleFinding,
    TerminationKind,
)
from .inference import analyze_ea_roles, infer_ea_roles

__all__ = [
    "EAConfidence",
    "EAEvidence",
    "EAInferenceReport",
    "EARole",
    "EARoleFinding",
    "TerminationKind",
    "analyze_ea_roles",
    "infer_ea_roles",
]