"""Optional composition of existing safety facts with EA-role enrichment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .capability import analyze_source as analyze_capabilities
from .decision import SafetyDecisionEngine, SafetyPolicy
from .ea_inference import EAInferenceReport, analyze_ea_roles
from .resource import ResourceReport, analyze_source as analyze_resources
from .taint import analyze_to_dict as analyze_taint


@dataclass
class AnalysisResult:
    """Combined report; EA findings are optional and never enter verdicting."""

    safety_facts: dict[str, Any]
    resource_facts: ResourceReport
    ea_roles: EAInferenceReport | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    source_name: str = "<string>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source_name,
            "safety_facts": self.safety_facts,
            "resource_facts": self.resource_facts.to_dict(),
            "ea_roles": self.ea_roles.to_dict() if self.ea_roles is not None else None,
            "evidence": self.evidence,
        }


def analyze_program(
    source: str,
    *,
    source_name: str = "<string>",
    include_ea: bool = False,
    policies: list[SafetyPolicy] | None = None,
) -> AnalysisResult:
    """Run the established safety passes and optionally attach EA inference.

    The final safety decision is computed exclusively from the pre-existing
    taint, capability, and resource reports. ``include_ea`` affects only the
    optional enrichment fields and evidence list.
    """
    taint_facts = analyze_taint(source)
    capability_facts = analyze_capabilities(source, name=source_name).to_dict()
    resource_report = analyze_resources(source, name=source_name)
    resource_facts = resource_report.to_dict()
    decision = SafetyDecisionEngine(policies=policies).evaluate(
        taint_results=taint_facts,
        capability_results=capability_facts,
        resource_results=resource_facts,
    )

    ea_roles = analyze_ea_roles(source, source_name=source_name) if include_ea else None
    evidence: list[dict[str, Any]] = []
    evidence.extend({"analysis": "taint", **item} for item in taint_facts.get("findings", []))
    for capability_items in capability_facts.get("by_capability", {}).values():
        evidence.extend({"analysis": "capability", **item} for item in capability_items)
    evidence.extend({"analysis": "resource", **item} for item in resource_facts.get("flags", []))
    if ea_roles is not None:
        for role, finding in ea_roles.roles.items():
            evidence.extend(
                {"analysis": "ea_inference", "role": role.value, **item.to_dict()}
                for item in finding.evidence
            )
    evidence.sort(key=lambda item: (
        item.get("analysis", ""), item.get("line") or 0, item.get("col") or 0,
        item.get("role", ""), item.get("kind", ""),
    ))

    return AnalysisResult(
        source_name=source_name,
        safety_facts={
            "taint": taint_facts,
            "capability": capability_facts,
            "decision": decision.to_dict(),
        },
        resource_facts=resource_report,
        ea_roles=ea_roles,
        evidence=evidence,
    )