"""Run an unbounded population loop with a dynamically supplied operator."""

from random import randrange


def objective(candidate):
    return sum(candidate)


def evolve(population, operator_source):
    while True:
        parents = sorted(population, key=objective, reverse=True)[:6]
        namespace = {"parents": parents, "randrange": randrange}
        exec(operator_source, namespace)
        children = namespace["children"]
        for child in children:
            child[randrange(len(child))] += 1
        population = parents + children


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(8)] for _ in range(24)], "children = [p.copy() for p in parents]")