"""Layer 1 — structural analysis: AST indexes, CFGs, CFG block references, data flow, helper summaries."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import NamedTuple

from cfg.cfg_builder import CFG, CFGBuilder

from ._ast_utils import _names, _target_names
from ._data_flow import FunctionSummary, IntraProceduralDataFlow


@dataclass(frozen=True)
class _LoopInfo:
    node: ast.For | ast.AsyncFor | ast.While
    target_names: frozenset[str]
    iterable_names: frozenset[str]


def _loop_info(node: ast.For | ast.AsyncFor | ast.While) -> _LoopInfo:
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return _LoopInfo(node, frozenset(_target_names(node.target)), frozenset(_names(node.iter)))
    return _LoopInfo(node, frozenset(), frozenset())


class NodeLocationKey(NamedTuple):
    """Fallback CFG lookup key for AST nodes not reached by identity (e.g. re-parsed copies)."""

    line: int
    node_type: str


class CFGBlockIndex:
    """Maps AST nodes to stable ``<cfg>:<block-kind>@<first-line>`` references."""

    def __init__(self, cfgs: tuple[CFG, ...]) -> None:
        refs: dict[ast.AST, list[str]] = {}
        for current in cfgs:
            for block in current.blocks.values():
                if not block.stmts:
                    continue
                linenos = [
                    line for stmt in block.stmts for item in ast.walk(stmt)
                    if (line := getattr(item, "lineno", None)) is not None
                ]
                if not linenos:
                    continue
                first_line = min(linenos)
                stable_ref = f"{current.name}:{block.kind}@{first_line}"
                for stmt in block.stmts:
                    for item in ast.walk(stmt):
                        refs.setdefault(item, []).append(stable_ref)
        by_location: dict[NodeLocationKey, list[str]] = {}
        for node, values in refs.items():
            line = getattr(node, "lineno", None)
            if line is not None:
                by_location.setdefault(NodeLocationKey(line, type(node).__name__), []).extend(values)
        self._by_location: Mapping[NodeLocationKey, tuple[str, ...]] = MappingProxyType({
            key: tuple(dict.fromkeys(values)) for key, values in by_location.items()
        })
        self._by_node: Mapping[ast.AST, tuple[str, ...]] = MappingProxyType({
            node: tuple(dict.fromkeys(values)) for node, values in refs.items()
        })

    def __call__(self, node: ast.AST) -> tuple[str, ...]:
        return self._by_node.get(
            node,
            self._by_location.get(
                NodeLocationKey(getattr(node, "lineno", -1), type(node).__name__), ()
            ),
        )


@dataclass(frozen=True, eq=False)
class HelperSummaries:
    """Read-only index of local function summaries, resolved once per call site."""

    by_scope: Mapping[str, FunctionSummary]
    by_call: Mapping[ast.Call, FunctionSummary | None]

    @classmethod
    def from_data_flow(cls, data_flow: IntraProceduralDataFlow, nodes: tuple[ast.AST, ...]) -> HelperSummaries:
        return cls(
            by_scope=MappingProxyType(dict(data_flow.summaries)),
            by_call=MappingProxyType({
                node: data_flow.summary_for_call(node, data_flow.scope_for(node))
                for node in nodes if isinstance(node, ast.Call)
            }),
        )

    def for_call(self, call: ast.Call) -> FunctionSummary | None:
        return self.by_call[call]

    def for_scope(self, scope: str) -> FunctionSummary | None:
        return self.by_scope.get(scope)


@dataclass(frozen=True, eq=False)
class StructuralAnalysis:
    """Output of the structural layer; framework-neutral facts about the analyzed source."""

    tree: ast.AST
    nodes: tuple[ast.AST, ...]
    parent: Mapping[ast.AST, ast.AST]
    loops: tuple[_LoopInfo, ...]
    # One CFG per function plus the module unless the caller supplied a single CFG.
    cfgs: tuple[CFG, ...]
    cfg_blocks: CFGBlockIndex
    data_flow: IntraProceduralDataFlow
    summaries: HelperSummaries

    def loop_body_nodes(self, loop: ast.For | ast.AsyncFor | ast.While) -> list[ast.AST]:
        body = loop.body
        return [item for stmt in body for item in ast.walk(stmt)]

    def in_loop(self, node: ast.AST) -> _LoopInfo | None:
        current = self.parent.get(node)
        while current is not None:
            for info in self.loops:
                if info.node is current:
                    return info
            current = self.parent.get(current)
        return None

    def assigned_names(self, node: ast.AST) -> set[str]:
        parent = self.parent.get(node)
        while parent is not None and not isinstance(parent, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            parent = self.parent.get(parent)
        if isinstance(parent, ast.Assign):
            return set().union(*(_target_names(target) for target in parent.targets))
        if isinstance(parent, ast.AnnAssign):
            return _target_names(parent.target)
        if isinstance(parent, ast.NamedExpr):
            return _target_names(parent.target)
        return set()

    def direct_assignment_target_names(self, node: ast.AST) -> set[str]:
        """First-target names when ``node`` is the immediate value of an assignment."""
        return self._first_target_names(self.parent.get(node))

    def enclosing_assignment_target_names(self, node: ast.AST) -> set[str]:
        """First-target names of the nearest enclosing ``Assign``/``AnnAssign``."""
        parent = self.parent.get(node)
        while parent is not None and not isinstance(parent, (ast.Assign, ast.AnnAssign)):
            parent = self.parent.get(parent)
        return self._first_target_names(parent)

    @staticmethod
    def _first_target_names(node: ast.AST | None) -> set[str]:
        if isinstance(node, ast.Assign):
            return _target_names(node.targets[0])
        if isinstance(node, ast.AnnAssign):
            return _target_names(node.target)
        return set()


def _build_cfgs(tree: ast.AST, nodes: tuple[ast.AST, ...], cfg: CFG | None) -> tuple[CFG, ...]:
    if cfg is not None:
        return (cfg,)
    builder = CFGBuilder()
    cfgs: list[CFG] = []
    if isinstance(tree, ast.Module):
        cfgs.append(builder.build_module(tree))
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cfgs.append(builder.build(node))
    return tuple(cfgs)


def analyze_structure(tree: ast.AST, cfg: CFG | None = None) -> StructuralAnalysis:
    """Layer entry point."""
    parent = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }
    nodes = tuple(ast.walk(tree))
    data_flow = IntraProceduralDataFlow(tree)
    loops = tuple(
        _loop_info(node) for node in nodes if isinstance(node, (ast.For, ast.AsyncFor, ast.While))
    )
    cfgs = _build_cfgs(tree, nodes, cfg)
    return StructuralAnalysis(
        tree=tree,
        nodes=nodes,
        parent=MappingProxyType(parent),
        loops=loops,
        cfgs=cfgs,
        cfg_blocks=CFGBlockIndex(cfgs),
        data_flow=data_flow,
        summaries=HelperSummaries.from_data_flow(data_flow, nodes),
    )
