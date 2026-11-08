"""Layer 4 — evidence: materializes role observations into located, CFG-annotated ``EAEvidence``."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from ._context import EvidenceSite
from ._model import EAConfidence, EAEvidence, EARole, EARoleFinding, TerminationKind
from .roles import RoleDetectionResult
from .structural import CFGBlockIndex, StructuralAnalysis


def _text(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return type(node).__name__


class EvidenceBuilder:
    """Builds source-located evidence annotated with stable CFG block references."""

    def __init__(self, cfg_blocks: CFGBlockIndex) -> None:
        self.cfg_blocks = cfg_blocks

    def build(self, site: EvidenceSite) -> EAEvidence:
        node = site.node
        return EAEvidence(
            kind=site.kind,
            description=site.description,
            line=getattr(node, "lineno", None),
            col=getattr(node, "col_offset", None),
            end_line=getattr(node, "end_lineno", None),
            end_col=getattr(node, "end_col_offset", None),
            ast_node=type(node).__name__,
            snippet=_text(node),
            cfg_blocks=self.cfg_blocks(node),
        )


@dataclass(frozen=True)
class RoleEvidence:
    """Deduplicated evidence for one role, in first-observation order (unsorted)."""

    role: EARole
    confidence: EAConfidence = EAConfidence.LOW
    evidence: tuple[EAEvidence, ...] = ()
    termination_kind: TerminationKind | None = None


@dataclass(frozen=True, eq=False)
class RoleEvidenceSet:
    roles: Mapping[EARole, RoleEvidence]

    def for_role(self, role: EARole) -> RoleEvidence:
        return self.roles[role]


def _raise_confidence(finding: EARoleFinding, confidence: EAConfidence) -> None:
    if confidence.value == EAConfidence.HIGH.value:
        finding.confidence = EAConfidence.HIGH
    elif finding.confidence == EAConfidence.LOW:
        finding.confidence = confidence


def build_evidence(structure: StructuralAnalysis, detection: RoleDetectionResult) -> RoleEvidenceSet:
    """Layer entry point."""
    builder = EvidenceBuilder(structure.cfg_blocks)
    accumulators = {role: EARoleFinding(role=role) for role in EARole}
    for observation in detection.observations:
        finding = accumulators[observation.role]
        evidence = builder.build(observation.site)
        if evidence not in finding.evidence:
            finding.evidence.append(evidence)
        _raise_confidence(finding, observation.confidence)
        if observation.termination_kind is not None:
            finding.termination_kind = observation.termination_kind
    return RoleEvidenceSet(MappingProxyType({
        role: RoleEvidence(role, finding.confidence, tuple(finding.evidence), finding.termination_kind)
        for role, finding in accumulators.items()
    }))
