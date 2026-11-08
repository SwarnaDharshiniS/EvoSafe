"""Conservative intra-procedural value-flow facts for EA analysis.

This module deliberately models only simple, statically visible Python flows.
It is not a general Python interpreter: unknown calls, branch-dependent values,
and unsupported assignment targets remain unknown rather than being guessed.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, NamedTuple, TypeAlias

from ._model import EAConfidence, EARole

_SAFE_BUILTINS = {
    "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float",
    "int", "len", "list", "map", "max", "min", "next", "range", "reversed",
    "round", "set", "sorted", "str", "sum", "tuple", "zip",
}


@dataclass(frozen=True, order=True)
class FlowLocation:
    line: int | None = None
    col: int | None = None
    end_line: int | None = None
    end_col: int | None = None


class ScopedName(NamedTuple):
    """A variable name qualified by its function scope (``<module>`` at top level)."""

    scope: str
    name: str


class ProgramPoint(NamedTuple):
    scope: str
    line: int


class RegistryKey(NamedTuple):
    registry_id: str | None
    key: str


class DataFlowKind(str, Enum):
    ASSIGNMENT = "assignment"
    ALIAS = "alias"
    REASSIGNMENT = "reassignment"
    CALL_RESULT = "call_result"
    CALL_SITE = "call_site"
    CALL_ARGUMENT = "call_argument"
    RETURN_VALUE = "return_value"
    LOOP_TARGET = "loop_target"
    CONTAINER_MUTATION = "container_mutation"
    SLICE_REPLACEMENT = "slice_replacement"
    COMPREHENSION = "comprehension"


class DispatchKind(str, Enum):
    KEYED_INVOKE = "keyed_invoke"
    ATTRIBUTE_DISPATCH = "attribute_dispatch"
    HIGHER_ORDER_MAP = "higher_order_map"


@dataclass(frozen=True)
class DataFlowFact:
    kind: DataFlowKind
    scope: str
    source: str | None
    target: str | None
    location: FlowLocation
    related_location: FlowLocation | None = None
    callee: str | None = None
    resolved: bool | None = None
    evidence: str | None = None

    @property
    def target_names(self) -> tuple[str, ...]:
        """``target`` split into its comma-joined names."""
        return tuple(self.target.split(",")) if self.target else ()


@dataclass(frozen=True)
class _Value:
    roots: frozenset[str] = frozenset()
    dependencies: frozenset[str] = frozenset()
    known: bool = False


Environment: TypeAlias = dict[str, _Value]


@dataclass(frozen=True)
class FunctionSummary:
    name: str
    scope: str
    parameters: tuple[str, ...]
    return_alias_parameters: frozenset[int] = frozenset()
    return_dependent_parameters: frozenset[int] = frozenset()
    return_paths_unambiguous: bool = False
    return_resolved: bool = False
    dynamic_behavior: bool = False
    unresolved_calls: bool = False
    role_evidence: tuple["FunctionRoleEvidence", ...] = ()


@dataclass(frozen=True)
class FunctionRoleEvidence:
    role: EARole
    parameter_indices: frozenset[int]
    node: ast.AST
    description: str
    certainty: EAConfidence = EAConfidence.MEDIUM


@dataclass(frozen=True)
class RegistrationFact:
    scope: str
    registry_id: str | None
    key: str
    callable_name: str
    callable_scope: str | None
    location: FlowLocation
    node: ast.Call
    callable_node: ast.AST
    ambiguous: bool = False


@dataclass(frozen=True)
class DispatchFact:
    registration: RegistrationFact
    scope: str
    kind: DispatchKind
    call: ast.Call
    callable_reference: ast.AST
    arguments: tuple[ast.AST, ...]
    ambiguous: bool = False


def _location(node: ast.AST) -> FlowLocation:
    return FlowLocation(
        line=getattr(node, "lineno", None),
        col=getattr(node, "col_offset", None),
        end_line=getattr(node, "end_lineno", None),
        end_col=getattr(node, "end_col_offset", None),
    )


def _target_names(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        return set().union(*(_target_names(item) for item in node.elts)) if node.elts else set()
    return set()


def _callable_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _walk_function_body(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterable[ast.AST]:
    def visit(node: ast.AST) -> Iterable[ast.AST]:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        yield node
        for child in ast.iter_child_nodes(node):
            yield from visit(child)

    for statement in fn.body:
        yield from visit(statement)


def _is_nested_under_control(node: ast.AST, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(fn):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    current = parents.get(node)
    controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.Match, ast.With, ast.AsyncWith)
    while current is not None and current is not fn:
        if isinstance(current, controls):
            return True
        current = parents.get(current)
    return False


def _ast_names(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def _is_copy_method_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"copy", "clone", "deepcopy"}
        and not node.args
    )


def _target_root(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


class IntraProceduralDataFlow:
    """Build simple binding/argument/return facts using the existing AST tree."""

    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree
        self.facts: list[DataFlowFact] = []
        self.functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        self.summaries: dict[str, FunctionSummary] = {}
        self.registrations: list[RegistrationFact] = []
        self.dispatches: list[DispatchFact] = []
        self._scope_nodes: dict[str, ast.AST] = {"<module>": tree}
        self._scope_for: dict[ast.AST, str] = {}
        self._snapshots: dict[ProgramPoint, Environment] = {}
        self._binding_locations: dict[ScopedName, FlowLocation] = {}
        self._collect_scopes(tree, "<module>")
        self._build_summaries()
        self._analyze_scopes()
        self._collect_registrations_and_dispatches()

    def _collect_scopes(self, node: ast.AST, scope: str) -> None:
        self._scope_for[node] = scope
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                child_scope = f"{scope}.{child.name}" if scope != "<module>" else child.name
                self.functions[child_scope] = child
                self._scope_nodes[child_scope] = child
                self._scope_for[child] = scope
                for item in child.body:
                    self._collect_scopes(item, child_scope)
            else:
                self._collect_scopes(child, scope)

    def scope_for(self, node: ast.AST) -> str:
        current: ast.AST | None = node
        while current is not None:
            if current in self._scope_for:
                return self._scope_for[current]
            current = None
        return "<module>"

    def _binding_location(self, scope: str, name: str) -> FlowLocation | None:
        return self._binding_locations.get(ScopedName(scope, name))

    def _first_binding_location(self, scope: str, names: Iterable[str]) -> FlowLocation | None:
        return next((
            self._binding_locations[ScopedName(scope, name)] for name in names
            if ScopedName(scope, name) in self._binding_locations
        ), None)

    def _formal_names(self, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, ...]:
        args = fn.args
        return tuple(
            arg.arg
            for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs)
        )

    def _build_summaries(self) -> None:
        self.summaries = {
            scope: FunctionSummary(fn.name, scope, self._formal_names(fn))
            for scope, fn in self.functions.items()
        }
        # Small bounded fixed point permits wrappers such as f(x): return g(x)
        # when g has a simple local summary. It is not recursive analysis.
        for _ in range(min(5, max(1, len(self.functions)))):
            updated = {
                scope: self._summarize_function(scope, fn)
                for scope, fn in self.functions.items()
            }
            if updated == self.summaries:
                break
            self.summaries = updated

    def _summarize_function(
        self,
        scope: str,
        fn: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> FunctionSummary:
        parameters = self._formal_names(fn)
        parameter_roots = {
            name: _Value(frozenset({f"param:{scope}:{index}"}), frozenset({f"param:{scope}:{index}"}), True)
            for index, name in enumerate(parameters)
        }
        return_values: list[_Value] = []
        self._summarize_block(fn.body, dict(parameter_roots), return_values, scope)

        aliases: set[int] = set()
        dependencies: set[int] = set()
        for value in return_values:
            for index in range(len(parameters)):
                token = f"param:{scope}:{index}"
                if token in value.roots:
                    aliases.add(index)
                if token in value.dependencies:
                    dependencies.add(index)

        body_nodes = sorted(
            _walk_function_body(fn),
            key=lambda node: (getattr(node, "lineno", 0), getattr(node, "col_offset", 0)),
        )
        return_nodes = [node for node in body_nodes if isinstance(node, ast.Return)]
        dynamic_names = {"eval", "exec", "globals", "locals", "vars", "getattr", "setattr", "delattr", "__import__"}
        dynamic_behavior = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in dynamic_names
            for node in body_nodes
        ) or any(isinstance(node, (ast.Await, ast.Yield, ast.YieldFrom)) for node in body_nodes)
        return_paths_unambiguous = len(return_nodes) == 1 and not _is_nested_under_control(return_nodes[0], fn)

        alias_parameters = {name: index for index, name in enumerate(parameters)}
        copied_parameters: dict[str, int] = {}
        pending_copy_writes: list[tuple[str, ast.AST]] = []
        assigned_exprs: dict[str, ast.AST] = {}
        role_evidence: list[FunctionRoleEvidence] = []

        def parameter_refs(expr: ast.AST | None, seen: frozenset[str] = frozenset()) -> set[int]:
            if expr is None:
                return set()
            refs: set[int] = set()
            for item in ast.walk(expr):
                if not isinstance(item, ast.Name):
                    continue
                if item.id in alias_parameters:
                    refs.add(alias_parameters[item.id])
                elif item.id in assigned_exprs and item.id not in seen:
                    refs.update(parameter_refs(assigned_exprs[item.id], seen | {item.id}))
            return refs

        def add_evidence(role: EARole, indices: set[int], node: ast.AST, description: str) -> None:
            if not indices:
                return
            certainty = EAConfidence.LOW if dynamic_behavior else EAConfidence.MEDIUM
            item = FunctionRoleEvidence(role, frozenset(indices), node, description, certainty)
            if item not in role_evidence:
                role_evidence.append(item)

        # Follow simple local aliases and retain their source expressions. This
        # is intentionally name-only within one function scope, not a heap model.
        for statement in body_nodes:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                value = statement.value
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                if value is not None:
                    for target in targets:
                        for name in _target_names(target):
                            assigned_exprs[name] = value
                            if isinstance(value, ast.Name) and value.id in alias_parameters:
                                alias_parameters[name] = alias_parameters[value.id]
                            elif name in alias_parameters:
                                alias_parameters.pop(name, None)
                            if _is_copy_method_call(value) and _target_root(value.func.value) in alias_parameters:
                                copied_parameters[name] = alias_parameters[_target_root(value.func.value)]
                            elif isinstance(value, ast.Name) and value.id in copied_parameters:
                                copied_parameters[name] = copied_parameters[value.id]
                            else:
                                copied_parameters.pop(name, None)
            elif isinstance(statement, ast.AugAssign):
                for name in _target_names(statement.target):
                    alias_parameters.pop(name, None)

            target = getattr(statement, "target", None)
            if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = statement.targets if isinstance(statement, ast.Assign) else [getattr(statement, "target", None)]
                for target in targets:
                    if not isinstance(target, (ast.Subscript, ast.Attribute)):
                        continue
                    if any(
                        isinstance(part, ast.Attribute) and part.attr.lower() == "fitness"
                        for part in ast.walk(target)
                    ):
                        continue
                    root = _target_root(target)
                    if root in copied_parameters:
                        # A modified copy is only mutation if it is returned (checked below).
                        pending_copy_writes.append((root, statement))
                        continue
                    base_names = _ast_names(target.value)
                    indices = {alias_parameters[name] for name in base_names if name in alias_parameters}
                    is_collection_replacement = (
                        isinstance(target, ast.Subscript)
                        and isinstance(target.slice, ast.Slice)
                    )
                    add_evidence(
                        EARole.REPLACEMENT if is_collection_replacement else EARole.MUTATION,
                        indices,
                        statement,
                        "The helper replaces a slice of its collection argument." if is_collection_replacement
                        else "The helper writes an element or attribute of its candidate argument.",
                    )

            if isinstance(statement, ast.Call) and isinstance(statement.func, ast.Attribute):
                receiver = statement.func.value
                receiver_names = _ast_names(receiver)
                indices = {alias_parameters[name] for name in receiver_names if name in alias_parameters}
                if statement.func.attr in {"append", "extend", "insert", "clear", "pop", "remove", "update"}:
                    add_evidence(
                        EARole.REPLACEMENT, indices, statement,
                        "The helper updates a collection argument in place.",
                    )

        def expanded_return(expr: ast.AST | None) -> list[ast.AST]:
            if expr is None:
                return []
            names = _target_names(expr)
            expansions = [assigned_exprs[name] for name in names if name in assigned_exprs]
            return [expr, *expansions]

        for return_node in return_nodes:
            if isinstance(return_node.value, ast.Name):
                for root, write in pending_copy_writes:
                    if root == return_node.value.id:
                        add_evidence(
                            EARole.MUTATION, {copied_parameters[root]}, write,
                            "The helper modifies a copy of its candidate argument and returns that copy.",
                        )
            expressions = expanded_return(return_node.value)
            for expr in expressions:
                refs = parameter_refs(expr)
                if isinstance(expr, (ast.BinOp, ast.List, ast.Tuple)) and len(refs) >= 2:
                    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
                        add_evidence(
                            EARole.CROSSOVER, refs, expr,
                            "The helper constructs a returned value by combining multiple argument-derived representations.",
                        )
                        add_evidence(
                            EARole.REPLACEMENT, refs, expr,
                            "The helper returns a newly composed collection from multiple argument-derived values.",
                        )
                calls = [item for item in ast.walk(expr) if isinstance(item, ast.Call)]
                for call in calls:
                    call_refs = parameter_refs(call)
                    callee = _callable_name(call)
                    callee_summary = self._resolve_summary(callee, scope) if callee else None
                    if call_refs and callee_summary is None and not _is_copy_method_call(call):
                        add_evidence(
                            EARole.FITNESS_EVALUATION, call_refs, call,
                            "The helper returns a call result whose arguments include candidate-derived values.",
                        )
                    if callee_summary:
                        for evidence in callee_summary.role_evidence:
                            mapped: set[int] = set()
                            for index in evidence.parameter_indices:
                                if index < len(call.args):
                                    mapped.update(parameter_refs(call.args[index]))
                            add_evidence(
                                evidence.role, mapped, evidence.node,
                                f"The helper delegates this operation to local helper {callee!r}: {evidence.description}",
                            )

                if isinstance(expr, ast.Subscript) and isinstance(expr.slice, ast.Slice):
                    add_evidence(
                        EARole.SELECTION, refs, expr,
                        "The helper returns a slice of an argument-derived collection.",
                    )
                if isinstance(expr, ast.Call) and _callable_name(expr) in {"sorted", "filter", "min", "max"}:
                    add_evidence(
                        EARole.SELECTION, parameter_refs(expr), expr,
                        "The helper returns a ranking or filtering operation over an argument-derived collection.",
                    )
                if isinstance(expr, ast.Call) and _callable_name(expr) in {"sorted", "filter", "min", "max"}:
                    for keyword in expr.keywords:
                        if keyword.arg == "key":
                            key_refs = parameter_refs(keyword.value)
                            if key_refs:
                                add_evidence(
                                    EARole.SELECTION, parameter_refs(expr), expr,
                                    "The helper ranks candidates using a key derived from its arguments.",
                                )
                if isinstance(expr, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
                    for generator in expr.generators:
                        if generator.ifs:
                            add_evidence(
                                EARole.SELECTION, parameter_refs(generator.iter), expr,
                                "The helper returns a comprehension that filters an argument-derived collection.",
                            )

            if isinstance(return_node.value, (ast.Compare, ast.BoolOp)):
                add_evidence(
                    EARole.TERMINATION, parameter_refs(return_node.value), return_node,
                    "The helper returns a condition structurally derived from its arguments.",
                )

        # A function with multiple or nested return paths cannot provide a
        # reliable return summary. Keep explicit mutation evidence but suppress
        # return-dependent role summaries in the caller.
        if not return_paths_unambiguous or dynamic_behavior:
            role_evidence = [
                FunctionRoleEvidence(
                    item.role, item.parameter_indices, item.node, item.description, EAConfidence.LOW
                )
                for item in role_evidence
            ]

        unresolved_calls = any(
            isinstance(node, ast.Call)
            and not _is_copy_method_call(node)
            and (
                _callable_name(node) is None
                or (
                    _callable_name(node) not in _SAFE_BUILTINS
                    and self._resolve_summary(_callable_name(node), scope) is None
                )
            )
            for node in body_nodes
        )
        if unresolved_calls:
            role_evidence = [
                FunctionRoleEvidence(
                    item.role, item.parameter_indices, item.node, item.description, EAConfidence.LOW
                )
                for item in role_evidence
            ]

        return FunctionSummary(
            name=fn.name,
            scope=scope,
            parameters=parameters,
            return_alias_parameters=frozenset(aliases) if return_paths_unambiguous and not unresolved_calls else frozenset(),
            return_dependent_parameters=frozenset(dependencies) if return_paths_unambiguous else frozenset(),
            return_paths_unambiguous=return_paths_unambiguous,
            return_resolved=return_paths_unambiguous and not dynamic_behavior and not unresolved_calls,
            dynamic_behavior=dynamic_behavior,
            unresolved_calls=unresolved_calls,
            role_evidence=tuple(role_evidence),
        )

    def _summarize_block(
        self,
        statements: Iterable[ast.stmt],
        env: Environment,
        returns: list[_Value],
        scope: str,
    ) -> Environment:
        current = dict(env)
        for stmt in statements:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(stmt, ast.Assign):
                value = self._summary_expr(stmt.value, current, scope)
                for target in stmt.targets:
                    for name in _target_names(target):
                        current[name] = value
            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                value = self._summary_expr(stmt.value, current, scope)
                for name in _target_names(stmt.target):
                    current[name] = value
            elif isinstance(stmt, ast.Return) and stmt.value is not None:
                returns.append(self._summary_expr(stmt.value, current, scope))
            elif isinstance(stmt, ast.If):
                left = self._summarize_block(stmt.body, dict(current), returns, scope)
                right = self._summarize_block(stmt.orelse, dict(current), returns, scope) if stmt.orelse else current
                current = {
                    name: left[name] if name in left and left[name] == right.get(name) else _Value()
                    for name in set(current) | set(left) | set(right)
                }
            elif isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
                self._summarize_block(stmt.body, dict(current), returns, scope)
                current = {name: _Value() for name in current}
        return current

    def _summary_expr(self, node: ast.AST, env: Environment, scope: str) -> _Value:
        if isinstance(node, ast.Name):
            return env.get(node.id, _Value())
        if isinstance(node, ast.Call):
            callee = _callable_name(node)
            summary = self._resolve_summary(callee, scope) if callee else None
            if summary and summary.return_resolved:
                actuals = [self._summary_expr(arg, env, scope) for arg in node.args]
                roots: set[str] = set()
                dependencies: set[str] = set()
                for index in summary.return_alias_parameters | summary.return_dependent_parameters:
                    if index < len(actuals):
                        actual = actuals[index]
                        if index in summary.return_alias_parameters:
                            roots.update(actual.roots)
                        dependencies.update(actual.dependencies)
                return _Value(frozenset(roots), frozenset(dependencies | roots), bool(roots or dependencies))
            return _Value()
        deps = frozenset().union(*(env[name].dependencies for name in _names(node, env)))
        return _Value(dependencies=deps, known=bool(deps))

    def _analyze_scopes(self) -> None:
        module = self._scope_nodes["<module>"]
        module_body = module.body if isinstance(module, ast.Module) else []
        self._analyze_block(module_body, {}, "<module>")
        for scope, fn in self.functions.items():
            params = self._formal_names(fn)
            env = {
                name: _Value(frozenset({f"param:{scope}:{index}"}), frozenset({f"param:{scope}:{index}"}), True)
                for index, name in enumerate(params)
            }
            for name, value in env.items():
                self._binding_locations[ScopedName(scope, name)] = _location(fn.args)
            self._analyze_block(fn.body, env, scope)

    def _snapshot(self, scope: str, node: ast.AST, env: Environment) -> None:
        line = getattr(node, "lineno", None)
        if line is not None:
            self._snapshots[ProgramPoint(scope, line)] = dict(env)

    def _analyze_block(self, statements: Iterable[ast.stmt], env: Environment, scope: str) -> Environment:
        current = dict(env)
        for stmt in statements:
            self._snapshot(scope, stmt, current)
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(stmt, ast.Assign):
                value = self._eval(stmt.value, current, scope)
                source_names = sorted(_names(stmt.value, current))
                for target in stmt.targets:
                    for name in sorted(_target_names(target)):
                        self._bind(name, value, stmt, source_names, current, scope)
                    if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Slice):
                        collection_names = sorted(_ast_names(target.value))
                        self.facts.append(DataFlowFact(
                            kind=DataFlowKind.SLICE_REPLACEMENT, scope=scope,
                            source=",".join(source_names) if source_names else None,
                            target=",".join(collection_names) if collection_names else None,
                            location=_location(stmt),
                            related_location=self._first_binding_location(scope, collection_names),
                            resolved=bool(collection_names) and all(self.value_known(name, scope=scope, line=getattr(stmt, "lineno", None)) for name in collection_names),
                            evidence="A full or partial slice assignment replaces the contents of an existing collection.",
                        ))
            elif isinstance(stmt, ast.AnnAssign):
                value = self._eval(stmt.value, current, scope) if stmt.value is not None else _Value()
                source_names = sorted(_names(stmt.value, current)) if stmt.value is not None else []
                for name in sorted(_target_names(stmt.target)):
                    self._bind(name, value, stmt, source_names, current, scope)
            elif isinstance(stmt, ast.AugAssign):
                names = sorted(_target_names(stmt.target))
                for name in names:
                    old = current.get(name, _Value())
                    rhs = self._eval(stmt.value, current, scope)
                    current[name] = _Value(known=False)
                    self.facts.append(DataFlowFact(
                        kind=DataFlowKind.REASSIGNMENT, scope=scope, source=name, target=name,
                        location=_location(stmt), related_location=self._binding_location(scope, name),
                        evidence="Augmented assignment replaces the prior static value with an unknown computed value.",
                    ))
            elif isinstance(stmt, ast.Expr):
                self._eval(stmt.value, current, scope)
            elif isinstance(stmt, ast.Return):
                value = self._eval(stmt.value, current, scope) if stmt.value is not None else _Value()
                source_names = sorted(_names(stmt.value, current)) if stmt.value is not None else []
                self.facts.append(DataFlowFact(
                    kind=DataFlowKind.RETURN_VALUE, scope=scope,
                    source=",".join(source_names) if source_names else None,
                    target=None, location=_location(stmt),
                    related_location=self._first_binding_location(scope, source_names),
                    evidence="Return expression has statically visible dependencies." if value.known else "Return value is not statically resolved.",
                ))
            elif isinstance(stmt, ast.If):
                self._eval(stmt.test, current, scope)
                before = dict(current)
                left = self._analyze_block(stmt.body, dict(before), scope)
                right = self._analyze_block(stmt.orelse, dict(before), scope) if stmt.orelse else before
                current = {
                    name: left[name] if name in left and left[name] == right.get(name) else before.get(name, _Value())
                    for name in set(before) | set(left) | set(right)
                }
            elif isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
                iterator = stmt.iter if isinstance(stmt, (ast.For, ast.AsyncFor)) else stmt.test
                iterator_value = self._eval(iterator, current, scope)
                before = dict(current)
                loop_env = dict(before)
                if isinstance(stmt, (ast.For, ast.AsyncFor)):
                    target_names = sorted(_target_names(stmt.target))
                    for name in target_names:
                        element = _Value(
                            roots=frozenset({f"element:{scope}:{name}@{getattr(stmt, 'lineno', None)}"}),
                            dependencies=iterator_value.dependencies,
                            known=True,
                        )
                        loop_env[name] = element
                        self._binding_locations[ScopedName(scope, name)] = _location(stmt.target)
                        self.facts.append(DataFlowFact(
                            kind=DataFlowKind.LOOP_TARGET, scope=scope,
                            source=",".join(sorted(_names(iterator, current))) or None,
                            target=name, location=_location(stmt),
                            related_location=self._first_binding_location(scope, _names(iterator, current)),
                            evidence="Loop target represents an element drawn from the iterated expression, not the collection object itself.",
                        ))
                body_env = self._analyze_block(stmt.body, loop_env, scope)
                current = {
                    name: value if body_env.get(name, value) == value else _Value()
                    for name, value in before.items()
                }
                for name in set(body_env) - set(before):
                    current[name] = _Value()
                if stmt.orelse:
                    self._analyze_block(stmt.orelse, dict(current), scope)
            elif isinstance(stmt, (ast.With, ast.AsyncWith)):
                for item in stmt.items:
                    self._eval(item.context_expr, current, scope)
                current = self._analyze_block(stmt.body, current, scope)
            elif isinstance(stmt, (ast.Try,)):
                before = dict(current)
                body_env = self._analyze_block(stmt.body, dict(before), scope)
                branch_envs = [body_env]
                branch_envs.extend(self._analyze_block(handler.body, dict(before), scope) for handler in stmt.handlers)
                branch_envs.append(self._analyze_block(stmt.orelse, dict(before), scope) if stmt.orelse else before)
                current = {
                    name: branch_envs[0][name] if all(branch.get(name) == branch_envs[0].get(name) for branch in branch_envs[1:]) else before.get(name, _Value())
                    for name in set().union(*(set(branch) for branch in branch_envs))
                }
                current = self._analyze_block(stmt.finalbody, current, scope)
            else:
                for child in ast.iter_child_nodes(stmt):
                    if isinstance(child, ast.expr):
                        self._eval(child, current, scope)
            line = getattr(stmt, "lineno", None)
            if line is not None:
                self._snapshots[ProgramPoint(scope, line)] = dict(current)
        return current

    def _bind(
        self,
        name: str,
        value: _Value,
        stmt: ast.AST,
        source_names: list[str],
        env: Environment,
        scope: str,
    ) -> None:
        previous = self._binding_location(scope, name)
        binding = _location(stmt)
        env[name] = value if value.known else _Value(frozenset({f"{scope}:{name}@{binding.line}"}), known=True)
        self._binding_locations[ScopedName(scope, name)] = binding
        for source_name in source_names:
            self.facts.append(DataFlowFact(
                kind=DataFlowKind.ASSIGNMENT, scope=scope, source=source_name, target=name,
                location=binding, related_location=self._binding_location(scope, source_name),
                evidence="Assignment carries a statically known value or dependency." if value.known else "Assignment source is present but its value is unresolved.",
            ))
        call = getattr(stmt, "value", None)
        if isinstance(call, ast.Call):
            callee = _callable_name(call)
            summary = self._resolve_summary(callee, scope) if callee else None
            self.facts.append(DataFlowFact(
                kind=DataFlowKind.CALL_RESULT, scope=scope, source=callee, target=name,
                location=binding, related_location=_location(call), callee=callee,
                resolved=summary is not None,
                evidence="Assignment receives a locally summarized call result." if summary else "Call result is assigned, but its value relationship remains unknown.",
            ))
        if len(source_names) == 1 and isinstance(getattr(stmt, "value", None), ast.Name) and value.known:
            self.facts.append(DataFlowFact(
                kind=DataFlowKind.ALIAS, scope=scope, source=source_names[0], target=name,
                location=binding, related_location=self._binding_location(scope, source_names[0]),
                evidence="Simple name assignment aliases the current value.",
            ))
        if previous is not None:
            self.facts.append(DataFlowFact(
                kind=DataFlowKind.REASSIGNMENT, scope=scope, source=name, target=name,
                location=binding, related_location=previous,
                evidence="A later assignment replaces the variable's prior binding.",
            ))

    def _eval(self, node: ast.AST | None, env: Environment, scope: str) -> _Value:
        if node is None:
            return _Value()
        if isinstance(node, ast.Name):
            return self._value_for_name(node.id, env, scope, getattr(node, "lineno", None))
        if isinstance(node, ast.Call):
            callee = _callable_name(node)
            summary = self._resolve_summary(callee, scope) if callee else None
            argument_values = [self._eval(arg, env, scope) for arg in node.args]
            keyword_values = {kw.arg: self._eval(kw.value, env, scope) for kw in node.keywords if kw.arg is not None}
            call_location = _location(node)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "append", "extend", "insert", "clear", "pop", "remove", "update", "add", "discard",
            }:
                receiver_value = self._eval(node.func.value, env, scope)
                receiver_names = sorted(_names(node.func.value, env))
                self.facts.append(DataFlowFact(
                    kind=DataFlowKind.CONTAINER_MUTATION, scope=scope,
                    source=",".join(receiver_names) if receiver_names else None,
                    target=",".join(sorted(receiver_value.roots)) if receiver_value.roots else None,
                    location=call_location,
                    related_location=self._first_binding_location(scope, receiver_names),
                    resolved=receiver_value.known,
                    evidence=f"Method {node.func.attr} mutates an object through its current receiver binding.",
                ))
            self.facts.append(DataFlowFact(
                kind=DataFlowKind.CALL_SITE, scope=scope, source=callee,
                target=None, location=call_location, callee=callee,
                resolved=summary is not None,
                evidence="Local function call resolved to a simple return summary." if summary else "Call target or return relationship is unresolved.",
            ))
            if summary is not None:
                for index, parameter in enumerate(summary.parameters):
                    actual = argument_values[index] if index < len(argument_values) else keyword_values.get(parameter, _Value())
                    actual_expr = node.args[index] if index < len(node.args) else next(
                        (keyword.value for keyword in node.keywords if keyword.arg == parameter),
                        None,
                    )
                    actual_names = sorted(_names(actual_expr, env)) if actual_expr is not None else []
                    self.facts.append(DataFlowFact(
                        kind=DataFlowKind.CALL_ARGUMENT, scope=scope,
                        source=",".join(actual_names) if actual_names else None,
                        target=f"{summary.scope}:{parameter}",
                        location=call_location,
                        related_location=self._first_binding_location(scope, actual_names),
                        callee=callee, resolved=True,
                        evidence="Call argument is mapped to a local function parameter.",
                    ))
                roots: set[str] = set()
                dependencies: set[str] = set()
                for index in summary.return_alias_parameters | summary.return_dependent_parameters:
                    actual = argument_values[index] if index < len(argument_values) else _Value()
                    roots.update(actual.roots if index in summary.return_alias_parameters else ())
                    dependencies.update(actual.dependencies)
                if summary.return_alias_parameters or summary.return_dependent_parameters:
                    return _Value(frozenset(roots), frozenset(dependencies | roots), True)
            if summary is None:
                for index, arg in enumerate(node.args):
                    names = sorted(_names(arg, env))
                    self.facts.append(DataFlowFact(
                        kind=DataFlowKind.CALL_ARGUMENT, scope=scope,
                        source=",".join(names) if names else None,
                        target=f"{callee or '<dynamic>'}:arg#{index}",
                        location=call_location,
                        related_location=self._first_binding_location(scope, names),
                        callee=callee, resolved=False,
                        evidence="Argument is linked to a call site, but its parameter and return semantics are unresolved.",
                    ))
            return _Value()
        if isinstance(node, ast.Lambda):
            return _Value()
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for generator in node.generators:
                self._eval(generator.iter, env, scope)
                for condition in generator.ifs:
                    self._eval(condition, env, scope)
            value_node = node.key if isinstance(node, ast.DictComp) else node.elt
            self._eval(value_node, env, scope)
            self.facts.append(DataFlowFact(
                kind=DataFlowKind.COMPREHENSION, scope=scope, source=",".join(sorted(_names(node, env))),
                target=None, location=_location(node),
                evidence="Comprehension explicitly relates its output expression to generator iteration values.",
            ))
            return _Value(known=False)
        if isinstance(node, ast.Attribute):
            return self._eval(node.value, env, scope)
        if isinstance(node, ast.Subscript):
            return self._eval(node.value, env, scope)
        if isinstance(node, ast.NamedExpr):
            value = self._eval(node.value, env, scope)
            for name in sorted(_target_names(node.target)):
                self._bind(name, value, node, sorted(_names(node.value, env)), env, scope)
            return value
        if isinstance(node, ast.AST):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.expr):
                    self._eval(child, env, scope)
        return _Value()

    def _resolve_summary(self, callee: str, caller_scope: str) -> FunctionSummary | None:
        local_name = f"{caller_scope}.{callee}" if caller_scope != "<module>" else callee
        return self.summaries.get(local_name) or self.summaries.get(callee)

    def _value_for_name(
        self,
        name: str,
        env: Environment,
        scope: str,
        line: int | None,
    ) -> _Value:
        if name in env:
            return env[name]
        scoped_value = self._environment_at(scope, line).get(name)
        if scoped_value is not None:
            return scoped_value
        if scope != "<module>":
            return self._environment_at("<module>", line).get(name, _Value())
        return _Value()

    def _registry_id(self, receiver: ast.AST | None, scope: str, line: int | None) -> str | None:
        if receiver is None:
            return None
        if not isinstance(receiver, ast.Name):
            return None
        value = self._value_for_name(receiver.id, {}, scope, line)
        if not value.known or not value.roots:
            return None
        return "|".join(sorted(value.roots))

    def _callable_scope(self, callable_name: str, scope: str) -> str | None:
        local_name = f"{scope}.{callable_name}" if scope != "<module>" else callable_name
        if local_name in self.functions:
            return local_name
        if callable_name in self.functions:
            return callable_name
        return None

    def _matching_registrations(self, registry_id: str | None, key: str) -> list[RegistrationFact]:
        return [
            registration for registration in self.registrations
            if registration.registry_id == registry_id and registration.key == key
        ]

    def _make_dispatch(
        self,
        *,
        registry_id: str | None,
        key: str,
        scope: str,
        kind: DispatchKind,
        call: ast.Call,
        reference: ast.AST,
        arguments: tuple[ast.AST, ...],
    ) -> DispatchFact | None:
        registrations = self._matching_registrations(registry_id, key)
        if not registrations:
            return None
        targets = {item.callable_name for item in registrations}
        ambiguous = len(targets) != 1 or any(item.ambiguous for item in registrations)
        registration = registrations[-1]
        return DispatchFact(
            registration=registration,
            scope=scope,
            kind=kind,
            call=call,
            callable_reference=reference,
            arguments=arguments,
            ambiguous=ambiguous,
        )

    def _collect_registrations_and_dispatches(self) -> None:
        calls = sorted(
            (node for node in ast.walk(self.tree) if isinstance(node, ast.Call)),
            key=lambda node: (getattr(node, "lineno", 0), getattr(node, "col_offset", 0)),
        )
        registrations: list[RegistrationFact] = []
        for call in calls:
            func = call.func
            method = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else None
            if method != "register" or len(call.args) < 2:
                continue
            key_node, callable_node = call.args[:2]
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                continue
            if isinstance(callable_node, ast.Name):
                callable_name = callable_node.id
            elif isinstance(callable_node, ast.Attribute):
                callable_name = ast.unparse(callable_node)
            else:
                continue
            scope = self.scope_for(call)
            receiver = func.value if isinstance(func, ast.Attribute) else None
            registry_id = self._registry_id(receiver, scope, getattr(call, "lineno", None))
            registrations.append(RegistrationFact(
                scope=scope,
                registry_id=registry_id,
                key=key_node.value,
                callable_name=callable_name,
                callable_scope=self._callable_scope(callable_name, scope),
                location=_location(call),
                node=call,
                callable_node=callable_node,
            ))

        groups: dict[RegistryKey, list[RegistrationFact]] = {}
        for registration in registrations:
            groups.setdefault(RegistryKey(registration.registry_id, registration.key), []).append(registration)
        self.registrations = []
        for group in groups.values():
            target_set = {registration.callable_name for registration in group}
            self.registrations.extend(
                replace(registration, ambiguous=len(target_set) != 1)
                for registration in group
            )

        dispatches: list[DispatchFact] = []
        for call in calls:
            scope = self.scope_for(call)
            func = call.func
            if isinstance(func, ast.Attribute) and func.attr == "invoke_registered" and call.args:
                key = call.args[0]
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    dispatch = self._make_dispatch(
                        registry_id=self._registry_id(func.value, scope, getattr(call, "lineno", None)),
                        key=key.value, scope=scope, kind=DispatchKind.KEYED_INVOKE, call=call,
                        reference=func, arguments=tuple(call.args[1:]),
                    )
                    if dispatch:
                        dispatches.append(dispatch)
                continue
            if isinstance(func, ast.Name) and func.id == "invoke_registered" and call.args:
                key = call.args[0]
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    dispatch = self._make_dispatch(
                        registry_id=None, key=key.value, scope=scope,
                        kind=DispatchKind.KEYED_INVOKE, call=call, reference=func,
                        arguments=tuple(call.args[1:]),
                    )
                    if dispatch:
                        dispatches.append(dispatch)
                continue
            if isinstance(func, ast.Attribute) and func.attr != "register":
                dispatch = self._make_dispatch(
                    registry_id=self._registry_id(func.value, scope, getattr(call, "lineno", None)),
                    key=func.attr, scope=scope, kind=DispatchKind.ATTRIBUTE_DISPATCH, call=call,
                    reference=func, arguments=tuple(call.args),
                )
                if dispatch:
                    dispatches.append(dispatch)

            if not (isinstance(func, ast.Name) and func.id == "map" and call.args):
                continue
            callback = call.args[0]
            if not isinstance(callback, ast.Attribute):
                continue
            dispatch = self._make_dispatch(
                registry_id=self._registry_id(callback.value, scope, getattr(callback, "lineno", None)),
                key=callback.attr, scope=scope, kind=DispatchKind.HIGHER_ORDER_MAP, call=call,
                reference=callback, arguments=tuple(call.args[1:]),
            )
            if dispatch:
                dispatches.append(dispatch)
        self.dispatches = dispatches

    def dispatch_for_call(self, call: ast.Call) -> list[DispatchFact]:
        """Return proven registration/dispatch pairs associated with a call AST."""
        return [dispatch for dispatch in self.dispatches if dispatch.call is call]

    def summary_for_call(self, call: ast.Call, caller_scope: str | None = None) -> FunctionSummary | None:
        """Return a same-source summary only for a direct, simple function call."""
        callee = _callable_name(call)
        if callee is None:
            return None
        return self._resolve_summary(callee, caller_scope or self.scope_for(call))

    def alias_group(self, name: str, *, scope: str = "<module>", line: int | None = None) -> set[str]:
        """Names sharing a statically known current binding at a source point."""
        env = self._environment_at(scope, line)
        value = env.get(name)
        if value is None or not value.known or not value.roots:
            return {name}
        return {
            other for other, other_value in env.items()
            if other_value.known and other_value.roots == value.roots
        } | {name}

    def roots_for_name(self, name: str, *, scope: str = "<module>", line: int | None = None) -> frozenset[str]:
        value = self._environment_at(scope, line).get(name)
        if value is None and scope != "<module>":
            value = self._environment_at("<module>", line).get(name)
        return value.roots if value and value.known else frozenset()

    def value_known(self, name: str, *, scope: str = "<module>", line: int | None = None) -> bool:
        value = self._environment_at(scope, line).get(name)
        return bool(value and value.known)

    def _environment_at(self, scope: str, line: int | None) -> Environment:
        candidates = [
            (point, env) for (candidate_scope, point), env in self._snapshots.items()
            if candidate_scope == scope and (line is None or point <= line)
        ]
        return dict(max(candidates, key=lambda item: item[0])[1]) if candidates else {}


def _names(node: ast.AST | None, env: Environment) -> set[str]:
    if node is None:
        return set()
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name) and item.id in env}
