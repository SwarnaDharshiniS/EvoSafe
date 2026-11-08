"""Layer 3 support — role-detection context, typed observations, and inter-detector bindings."""

from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TypeAlias

from ._ast_utils import _names
from ._data_flow import IntraProceduralDataFlow
from ._model import EAConfidence, EARole, TerminationKind
from .lineage import CandidateLineage
from .structural import HelperSummaries, StructuralAnalysis, _LoopInfo


@dataclass(frozen=True, eq=False)
class EvidenceSite:
    """Where and why a role was observed; the evidence layer materializes it into ``EAEvidence``."""

    kind: str
    description: str
    node: ast.AST

    @property
    def line(self) -> int | None:
        return getattr(self.node, "lineno", None)


@dataclass(frozen=True, eq=False)
class RoleObservation:
    role: EARole
    site: EvidenceSite
    confidence: EAConfidence
    termination_kind: TerminationKind | None = None


class ObservationCollector:
    """Per-detector, append-only record of observations in emission order."""

    def __init__(self) -> None:
        self._observations: list[RoleObservation] = []

    def add(
        self,
        role: EARole,
        site: EvidenceSite,
        confidence: EAConfidence,
        termination_kind: TerminationKind | None = None,
    ) -> None:
        self._observations.append(RoleObservation(role, site, confidence, termination_kind))

    def observed_lines(self, *roles: EARole) -> set[int | None]:
        return {item.site.line for item in self._observations if item.role in roles}

    def observations(self) -> list[RoleObservation]:
        return list(self._observations)


CandidateAssignment: TypeAlias = tuple[ast.Assign | ast.AnnAssign | ast.NamedExpr, ast.Call]


@dataclass(frozen=True)
class CandidateLoopScan:
    """Candidate-consuming calls observed in a loop accepted as population iteration."""

    assigned_candidate_calls: tuple[CandidateAssignment, ...]
    score_calls: tuple[ast.Call, ...]


@dataclass(frozen=True)
class CandidateComprehensionScan:
    node: ast.ListComp | ast.SetComp | ast.GeneratorExp
    calls: tuple[ast.Call, ...]


@dataclass(frozen=True)
class PopulationScan:
    loops: tuple[CandidateLoopScan, ...] = ()
    comprehensions: tuple[CandidateComprehensionScan, ...] = ()


@dataclass
class RoleBindings:
    """Mutable inference progress that later detectors build on."""

    population_names: set[str] = field(default_factory=set)
    candidate_names: set[str] = field(default_factory=set)
    selection_names: set[str] = field(default_factory=set)
    offspring_names: set[str] = field(default_factory=set)
    fitness_names: set[str] = field(default_factory=set)
    population_scan: PopulationScan = field(default_factory=PopulationScan)
    observations: list[RoleObservation] = field(default_factory=list)

    def observed_lines(self, *roles: EARole) -> set[int | None]:
        return {item.site.line for item in self.observations if item.role in roles}


@dataclass(frozen=True, eq=False)
class EAAnalysisContext:
    """Role-detection view: read-only access to layers 1-2 plus the shared ``RoleBindings``."""

    structure: StructuralAnalysis
    lineage: CandidateLineage
    state: RoleBindings

    @property
    def nodes(self) -> tuple[ast.AST, ...]:
        return self.structure.nodes

    @property
    def parent(self) -> Mapping[ast.AST, ast.AST]:
        return self.structure.parent

    @property
    def loops(self) -> tuple[_LoopInfo, ...]:
        return self.structure.loops

    @property
    def data_flow(self) -> IntraProceduralDataFlow:
        return self.structure.data_flow

    @property
    def summaries(self) -> HelperSummaries:
        return self.structure.summaries

    def evidence(self, kind: str, description: str, node: ast.AST) -> EvidenceSite:
        return EvidenceSite(kind, description, node)

    def loop_body_nodes(self, loop: ast.For | ast.AsyncFor | ast.While) -> list[ast.AST]:
        return self.structure.loop_body_nodes(loop)

    def in_loop(self, node: ast.AST) -> _LoopInfo | None:
        return self.structure.in_loop(node)

    def assigned_names(self, node: ast.AST) -> set[str]:
        return self.structure.assigned_names(node)

    def direct_assignment_target_names(self, node: ast.AST) -> set[str]:
        return self.structure.direct_assignment_target_names(node)

    def enclosing_assignment_target_names(self, node: ast.AST) -> set[str]:
        return self.structure.enclosing_assignment_target_names(node)


class EADetector(ABC):
    """Stateless detector API: read the shared context, return role observations."""

    @abstractmethod
    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        ...


def expand_population_aliases(context: EAAnalysisContext) -> None:
    state = context.state
    changed = True
    while changed:
        before = set(state.population_names)
        for node in context.nodes:
            if not isinstance(node, ast.Name) or node.id not in state.population_names:
                continue
            scope = context.data_flow.scope_for(node)
            state.population_names.update(
                context.data_flow.alias_group(
                    node.id,
                    scope=scope,
                    line=getattr(node, "lineno", None),
                )
            )
        changed = state.population_names != before


def mark_iterated_candidates(context: EAAnalysisContext) -> None:
    state = context.state
    for info in context.loops:
        if set(_names(info.node.iter if isinstance(info.node, (ast.For, ast.AsyncFor)) else None)) & state.population_names:
            state.candidate_names.update(info.target_names)


def bind_population_element_aliases(context: EAAnalysisContext) -> None:
    """Names bound to single elements of an inferred population are candidates."""
    state = context.state
    collections = state.population_names | state.selection_names
    for node in context.nodes:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, value = node.targets[0], node.value
        if isinstance(target, ast.Tuple) and isinstance(value, ast.Tuple) and len(target.elts) == len(value.elts):
            pairs = list(zip(target.elts, value.elts))
        else:
            pairs = [(target, value)]
        for name_node, element in pairs:
            if (
                isinstance(name_node, ast.Name)
                and isinstance(element, ast.Subscript)
                and not isinstance(element.slice, ast.Slice)
                and isinstance(element.value, ast.Name)
                and element.value.id in collections
            ):
                state.candidate_names.add(name_node.id)
