"""Dispatch population and variation operations indirectly from a registry."""

from random import randrange


def make_pool():
    return [[randrange(10) for _ in range(8)] for _ in range(24)]


def objective(genome):
    return sum(genome)


def choose(pool):
    return sorted(pool, key=objective, reverse=True)[:6]


def perturb(genome):
    child = genome.copy()
    child[randrange(len(child))] += 1
    return child


OPERATORS = {"create": make_pool, "select": choose, "mutate": perturb}


def run(rounds=15):
    current = OPERATORS["create"]()
    for _ in range(rounds):
        parents = OPERATORS["select"](current)
        current = parents + [OPERATORS["mutate"](parents[i % 6]) for i in range(12)]
    return current


if __name__ == "__main__":
    run()