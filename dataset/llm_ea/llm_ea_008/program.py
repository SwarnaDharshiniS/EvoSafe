"""Use NumPy arrays for vectorized fitness and genetic variation."""

import numpy as np


def optimize(seed=4):
    rng = np.random.default_rng(seed)
    population = rng.uniform(-3, 3, size=(48, 6))
    target = np.array([1.0, -2.0, 0.5, 3.0, -1.0, 2.0])
    for _ in range(30):
        scores = np.sum((population - target) ** 2, axis=1)
        parents = population[np.argsort(scores)[:12]]
        left = parents[np.arange(24) % len(parents)]
        right = parents[(np.arange(24) + 1) % len(parents)]
        mask = rng.random((24, 6)) < 0.5
        children = np.where(mask, left, right)
        children += rng.normal(0, 0.08, size=children.shape)
        population = np.vstack((parents, children))
    return population[np.argmin(np.sum((population - target) ** 2, axis=1))]


if __name__ == "__main__":
    print(optimize())