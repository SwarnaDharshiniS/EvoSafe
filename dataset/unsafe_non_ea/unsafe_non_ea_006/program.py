"""Resolve a dependency worklist without cycle detection or a work limit."""


def expand_dependencies(start, dependency_map):
    pending = [start]
    visited = []
    while pending:
        package = pending.pop()
        visited.append(package)
        pending.extend(dependency_map.get(package, ()))
    return visited


if __name__ == "__main__":
    expand_dependencies("app", {"app": ["core"], "core": ["app"]})