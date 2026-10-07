"""Layer 2 — candidate lineage: collection, candidate, and lineage facts over the structural layer."""

from __future__ import annotations

from typing import TypeAlias

from ._structure import CandidateCollectionAnalyzer, CandidateCollectionFacts
from .structural import StructuralAnalysis


CandidateLineage: TypeAlias = CandidateCollectionFacts


def analyze_lineage(structure: StructuralAnalysis) -> CandidateLineage:
    """Layer entry point."""
    return CandidateCollectionAnalyzer(structure.tree, structure.data_flow, structure.cfg_blocks).facts
