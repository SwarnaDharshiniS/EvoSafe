"""Use NumPy to create an oversized matrix of candidate coefficients."""

import numpy as np


def initialize():
    return np.zeros((80_000, 80_000), dtype=np.float64)


def fitness(population):
    return np.sum(population * population, axis=1)


def select(population):
    return population[np.argsort(fitness(population))[:20]]


def evolve(population, generations=8):
    rng = np.random.default_rng(21)
    for _ in range(generations):
        parents = select(population)
        left = parents[np.arange(20) % len(parents)]
        right = parents[(np.arange(20) + 1) % len(parents)]
        children = np.where(rng.random(left.shape) < 0.5, left, right)
        children += rng.normal(0, 0.01, size=children.shape)
        population = np.vstack((parents, children))
    return population


if __name__ == "__main__":
    evolve(initialize())