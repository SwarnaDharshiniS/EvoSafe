"""Merge a never-pruned historical archive into the active population."""

from random import random


def evaluate(chromosome):
    return abs(sum(chromosome) - 5)


def evolve(epochs=180):
    population = [[random() for _ in range(14)] for _ in range(45)]
    history = []
    for _ in range(epochs):
        history.extend(population)
        ranked = sorted(population, key=evaluate)
        parents = ranked[:9]
        children = [parent[:] for parent in parents]
        population = history + children
    return min(population, key=evaluate)


if __name__ == "__main__":
    evolve()