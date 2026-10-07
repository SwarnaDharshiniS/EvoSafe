"""Result models for optional evolutionary-algorithm role inference."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TypedDict


class EARole(str, Enum):
    POPULATION = "population"
    FITNESS_EVALUATION = "fitness_evaluation"
    SELECTION = "selection"
    MUTATION = "mutation"
    CROSSOVER = "crossover"
    REPLACEMENT = "replacement"
    TERMINATION = "termination"


class EAConfidence(str, Enum):
    """Ordinal evidence strength, not a statistically calibrated probability."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TerminationKind(str, Enum):
    STATICALLY_BOUNDED = "statically_bounded"
    CONDITION_BASED = "condition_based"
    UNKNOWN_OR_UNBOUNDED = "unknown_or_unbounded"


class EAEvidenceDict(TypedDict):
    kind: str
    description: str
    line: int | None
    col: int | None
    end_line: int | None
    end_col: int | None
    ast_node: str | None
    snippet: str | None
    cfg_blocks: list[str]


class EARoleFindingDict(TypedDict):
    role: str
    detected: bool
    confidence: str
    evidence: list[EAEvidenceDict]
    reason: str | None
    termination_kind: str | None


class EAInferenceReportDict(TypedDict):
    source: str
    roles: dict[str, EARoleFindingDict]


@dataclass(frozen=True)
class EAEvidence:
    kind: str
    description: str
    line: int | None = None
    col: int | None = None
    end_line: int | None = None
    end_col: int | None = None
    ast_node: str | None = None
    snippet: str | None = None
    cfg_blocks: tuple[str, ...] = ()

    def to_dict(self) -> EAEvidenceDict:
        return {
            "kind": self.kind,
            "description": self.description,
            "line": self.line,
            "col": self.col,
            "end_line": self.end_line,
            "end_col": self.end_col,
            "ast_node": self.ast_node,
            "snippet": self.snippet,
            "cfg_blocks": list(self.cfg_blocks),
        }


@dataclass
class EARoleFinding:
    role: EARole
    confidence: EAConfidence = EAConfidence.LOW
    evidence: list[EAEvidence] = field(default_factory=list)
    reason: str | None = None
    termination_kind: TerminationKind | None = None

    @property
    def detected(self) -> bool:
        return bool(self.evidence) and self.confidence != EAConfidence.LOW

    def to_dict(self) -> EARoleFindingDict:
        return {
            "role": self.role.value,
            "detected": self.detected,
            "confidence": self.confidence.value,
            "evidence": [item.to_dict() for item in self.evidence],
            "reason": self.reason,
            "termination_kind": self.termination_kind.value if self.termination_kind else None,
        }


@dataclass
class EAInferenceReport:
    source_name: str = "<string>"
    roles: dict[EARole, EARoleFinding] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for role in EARole:
            self.roles.setdefault(role, EARoleFinding(role=role))

    def for_role(self, role: EARole | str) -> EARoleFinding:
        return self.roles[EARole(role)]

    def to_dict(self) -> EAInferenceReportDict:
        return {
            "source": self.source_name,
            "roles": {role.value: self.roles[role].to_dict() for role in EARole},
        }