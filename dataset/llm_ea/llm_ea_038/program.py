"""Combine callback-based evaluation and list-comprehension offspring creation."""

from random import randrange


def score(item):
    return sum(item)


def evolve(population, evaluate, rounds):
    for _ in range(rounds):
        parents = sorted(population, key=evaluate, reverse=True)[:8]
        children = [parent.copy() for parent in parents]
        for child in children:
            child[randrange(len(child))] += 1
        population = parents + children
    return population


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(8)] for _ in range(32)], score, 18)