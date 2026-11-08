"""Keep evolving routing policies until an external quality threshold is met."""

from random import randrange


def route_cost(route):
    return sum(abs(a - b) for a, b in zip(route, route[1:]))


def search():
    population = [[randrange(40) for _ in range(16)] for _ in range(50)]
    best_cost = float("inf")
    while True:
        parents = sorted(population, key=route_cost)[:10]
        best_cost = route_cost(parents[0])
        children = []
        for index, first in enumerate(parents):
            second = parents[(index + 1) % len(parents)]
            child = first[:8] + second[8:]
            child[randrange(len(child))] = randrange(40)
            children.append(child)
        population = parents + children
        if best_cost == 0:
            break


if __name__ == "__main__":
    search()