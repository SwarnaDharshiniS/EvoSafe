"""Layer 5 — summary: orders evidence deterministically and produces the public ``EAInferenceReport``."""

from __future__ import annotations

from ._model import EAInferenceReport, EARole, EARoleFinding
from .evidence import RoleEvidenceSet


def summarize(evidence: RoleEvidenceSet, source_name: str) -> EAInferenceReport:
    """Layer entry point."""
    roles: dict[EARole, EARoleFinding] = {}
    for role in EARole:
        item = evidence.for_role(role)
        ordered = sorted(item.evidence, key=lambda entry: (entry.line or 0, entry.col or 0, entry.kind, entry.snippet or ""))
        roles[role] = EARoleFinding(
            role=role,
            confidence=item.confidence,
            evidence=ordered,
            reason=ordered[0].description if ordered else None,
            termination_kind=item.termination_kind,
        )
    return EAInferenceReport(source_name=source_name, roles=roles)
