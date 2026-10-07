"""Cache a full generation's expensive feature vectors without eviction."""

from random import random


def features(candidate):
    return [value ** power for value in candidate for power in range(1, 80)]


def fitness(candidate):
    return sum(features(candidate))


def evolve(generations=80):
    population = [[random() for _ in range(500)] for _ in range(2_000)]
    feature_cache = {}
    for _ in range(generations):
        for candidate in population:
            feature_cache[tuple(candidate)] = features(candidate)
        ranked = sorted(population, key=lambda item: sum(feature_cache[tuple(item)]))
        parents = ranked[:50]
        offspring = [parent.copy() for parent in parents]
        for child in offspring:
            child[0] += random()
        population = parents + offspring
    return population


if __name__ == "__main__":
    evolve()