"""Framework-independent, structural inference of evolutionary-algorithm roles.

The analysis is optional enrichment: it does not invoke or alter any safety
analyzer, policy, verdict, manifest, or execution decision.

Pipeline (each layer imports only from layers before it):
``structural`` -> ``lineage`` -> ``roles`` -> ``evidence`` -> ``summaries``.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from cfg.cfg_builder import CFG

from ._model import EAInferenceReport
from .evidence import RoleEvidenceSet, build_evidence
from .lineage import CandidateLineage, analyze_lineage
from .roles import RoleDetectionResult, detect_roles
from .structural import StructuralAnalysis, analyze_structure
from .summaries import summarize


@dataclass(frozen=True, eq=False)
class EASourceContext:
    """Pipeline input: the parsed source plus an optional caller-supplied CFG."""

    tree: ast.AST
    source_text: str
    source_name: str = "<string>"
    cfg: CFG | None = None


@dataclass(frozen=True, eq=False)
class EAInferenceResult:
    structure: StructuralAnalysis
    lineage: CandidateLineage
    findings: RoleDetectionResult
    evidence: RoleEvidenceSet
    report: EAInferenceReport


class EAInferenceEngine:
    def run(self, context: EASourceContext) -> EAInferenceResult:
        structure = analyze_structure(context.tree, context.cfg)
        lineage = analyze_lineage(structure)
        findings = detect_roles(structure, lineage)
        evidence = build_evidence(structure, findings)
        summaries = summarize(evidence, context.source_name)
        return EAInferenceResult(structure, lineage, findings, evidence, summaries)


def analyze_ea_roles(
    source: str | ast.AST,
    *,
    source_name: str = "<string>",
    cfg: CFG | None = None,
) -> EAInferenceReport:
    """Infer EA roles from Python source or an AST, optionally using a CFG.

    The CFG is built with the repository's existing ``CFGBuilder`` when one
    is not supplied. Syntax errors are propagated to the caller, like the
    existing parser and CFG APIs.
    """
    tree: ast.AST
    if isinstance(source, str):
        source_text = source
        tree = ast.parse(source)
    elif isinstance(source, ast.AST):
        tree = source
        source_text = ast.unparse(source)
    else:
        raise TypeError("source must be Python source text or an ast.AST node")
    return EAInferenceEngine().run(EASourceContext(tree, source_text, source_name, cfg)).report


infer_ea_roles = analyze_ea_roles
