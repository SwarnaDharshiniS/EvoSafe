"""Combine every member of two parent groups and store all resulting children."""

from itertools import product
from random import randrange


def objective(genome):
    return sum(value * value for value in genome)


def mate(population):
    ordered = sorted(population, key=objective)
    left_group, right_group = ordered[:300], ordered[300:]
    offspring = []
    for left, right in product(left_group, right_group):
        child = [a if index % 2 else b for index, (a, b) in enumerate(zip(left, right))]
        child[randrange(len(child))] += 1
        offspring.append(child)
    return ordered[:20] + offspring


if __name__ == "__main__":
    mate([[randrange(50) for _ in range(32)] for _ in range(600)])