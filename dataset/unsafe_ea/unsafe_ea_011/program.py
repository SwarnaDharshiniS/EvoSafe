"""Duplicate selected parents repeatedly without a population-size ceiling."""

from random import random


def score(candidate):
    return sum(candidate)


def evolve(cycles=120):
    population = [[random() for _ in range(9)] for _ in range(18)]
    for _ in range(cycles):
        leaders = sorted(population, key=score, reverse=True)[:6]
        cloned = [leader.copy() for leader in leaders for _ in range(12)]
        mutated = []
        for child in cloned:
            child[0] += random() / 100
            mutated.append(child)
        population.extend(mutated)
    return max(population, key=score)


if __name__ == "__main__":
    evolve()