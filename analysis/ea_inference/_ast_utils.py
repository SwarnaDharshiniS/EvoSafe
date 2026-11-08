"""Pure AST and name helpers shared by every inference layer."""

from __future__ import annotations

import ast


_COPY_METHODS = {"copy", "clone", "deepcopy"}


def _names(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def _target_names(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        return set().union(*(_target_names(item) for item in node.elts)) if node.elts else set()
    return set()


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id.lower()
    if isinstance(func, ast.Attribute):
        return func.attr.lower()
    return ""


def _has_name(node: ast.AST, names: set[str]) -> bool:
    return bool(_names(node) & names)


def _copy_source(node: ast.AST | None) -> ast.AST | None:
    """Return the copied object for x.copy()/copy.copy(x)/deepcopy(x), else None."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr in _COPY_METHODS and not node.args:
        return func.value
    name = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else None
    if name in {"copy", "deepcopy"} and len(node.args) == 1:
        return node.args[0]
    return None


def _root_name(node: ast.AST | None) -> str | None:
    """Base variable of a subscript/attribute chain: rows[i][j] -> rows."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _is_index_iteration(iterable: ast.AST) -> bool:
    # range() yields integer indices, not candidate objects.
    return isinstance(iterable, ast.Call) and isinstance(iterable.func, ast.Name) and iterable.func.id == "range"


def _is_fitness_metadata_target(node: ast.AST) -> bool:
    return any(
        isinstance(item, ast.Attribute) and item.attr.lower() == "fitness"
        for item in ast.walk(node)
    )


def _local_name(qualified: str | None) -> str | None:
    """Strip the scope prefix from a structure-fact name: 'f:pop' -> 'pop'."""
    return qualified.rsplit(":", 1)[-1] if qualified else None
