"""Build a very large generation from an integer-coded solution space."""

from random import random


def fitness(candidate):
    return sum(candidate)


def initialize():
    return [[random() for _ in range(12)] for _ in range(20_000_000)]


def step(population, generations=5):
    for _ in range(generations):
        parents = sorted(population, key=fitness, reverse=True)[:20]
        children = [parent.copy() for parent in parents]
        for child in children:
            child[0] += random()
        population = parents + children
    return population


if __name__ == "__main__":
    step(initialize())