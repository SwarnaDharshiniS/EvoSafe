"""Walk a dependency graph recursively without tracking visited nodes."""


def collect_dependencies(graph, module):
    output = [module]
    for child in graph.get(module, ()):
        output.extend(collect_dependencies(graph, child))
    return output


if __name__ == "__main__":
    graph = {"parser": ["schema"], "schema": ["parser"]}
    print(collect_dependencies(graph, "parser"))