"""Traverse graph neighbors recursively without tracking visited nodes."""


def total_weight(graph, node):
    weight = graph[node]["weight"]
    for neighbor in graph[node]["links"]:
        weight += total_weight(graph, neighbor)
    return weight


if __name__ == "__main__":
    network = {
        "north": {"weight": 2, "links": ["south"]},
        "south": {"weight": 3, "links": ["north"]},
    }
    print(total_weight(network, "north"))