"""Parameter search that can keep evolving when its target is unreachable."""

from random import random


def error(candidate):
    return abs(sum(candidate) - 10_000)


def mutate(candidate):
    child = candidate.copy()
    child[0] += random() * 0.001
    return child


def search():
    population = [[random() for _ in range(8)] for _ in range(40)]
    best = float("inf")
    while best > 1e-9:
        ranked = sorted(population, key=error)
        best = error(ranked[0])
        parents = ranked[:8]
        population = parents + [mutate(parents[index % len(parents)]) for index in range(32)]
    return ranked[0]


if __name__ == "__main__":
    search()