"""Walk module dependencies recursively without a visited set."""


def visit(graph, name):
    modules = [name]
    for dependency in graph.get(name, ()):
        modules.extend(visit(graph, dependency))
    return modules


if __name__ == "__main__":
    visit({"ui": ["core"], "core": ["ui"]}, "ui")