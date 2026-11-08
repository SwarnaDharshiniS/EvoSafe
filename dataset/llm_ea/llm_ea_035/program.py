"""Use recursive helper calls to expand each selected candidate indefinitely."""

from random import randrange


def fitness(candidate):
    return sum(candidate)


def descend(parent):
    child = parent.copy()
    child[randrange(len(child))] += 1
    return descend(child)


def optimize(population):
    parents = sorted(population, key=fitness, reverse=True)[:5]
    return parents + [descend(parent) for parent in parents]


if __name__ == "__main__":
    optimize([[randrange(10) for _ in range(10)] for _ in range(20)])