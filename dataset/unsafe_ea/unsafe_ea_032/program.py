"""Recompute and retain a dense pairwise distance matrix every generation."""

from random import random


def objective(candidate):
    return sum(candidate)


def diversity(population):
    return [[sum(abs(a - b) for a, b in zip(left, right)) for right in population] for left in population]


def evolve(population, rounds=40):
    for _ in range(rounds):
        matrix = diversity(population)
        ranked = sorted(zip(population, matrix), key=lambda row: objective(row[0]), reverse=True)
        survivors = [row[0] for row in ranked[: len(ranked) // 2]]
        offspring = [candidate.copy() for candidate in survivors]
        for child in offspring:
            child[0] += 0.001
        population = survivors + offspring
    return population


if __name__ == "__main__":
    evolve([[random() for _ in range(80)] for _ in range(8_000)])