"""Retry child construction indefinitely when a candidate fails validation."""

from random import randrange


def valid(candidate):
    return sum(candidate) < 0


def objective(candidate):
    return sum(abs(value) for value in candidate)


def make_child(parent):
    while True:
        child = parent.copy()
        child[randrange(len(child))] = randrange(10)
        if valid(child):
            return child


def evolve(population):
    parents = sorted(population, key=objective)[:8]
    return parents + [make_child(parents[index % 8]) for index in range(20)]


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(12)] for _ in range(40)])