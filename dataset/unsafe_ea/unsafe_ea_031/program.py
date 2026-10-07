"""Allocate an enormous candidate pool before beginning a small EA run."""

from random import random


def fitness(candidate):
    return sum(candidate)


def evolve():
    population = [[random() for _ in range(64)] for _ in range(20_000_000)]
    for _ in range(5):
        population = sorted(population, key=fitness, reverse=True)[:100]
        offspring = [candidate.copy() for candidate in population]
        for child in offspring:
            child[0] += random()
        population.extend(offspring)
    return population


if __name__ == "__main__":
    evolve()