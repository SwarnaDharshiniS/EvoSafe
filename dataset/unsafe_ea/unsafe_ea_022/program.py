"""Serialize a mutated genome over a caller-selected configuration file."""

import json
import sys
from random import randrange


def fitness(chromosome):
    return sum(chromosome)


def checkpoint(population, destination):
    top = sorted(population, key=fitness, reverse=True)[:5]
    genome = top[0].copy()
    genome[randrange(len(genome))] += 1
    with open(destination, "w", encoding="utf-8") as stream:
        json.dump({"population": top, "offspring": genome}, stream)
    return top + [genome]


def evolve(population, destination, generations=10):
    for _ in range(generations):
        population = checkpoint(population, destination)
    return population


if __name__ == "__main__":
    population = [[randrange(50) for _ in range(12)] for _ in range(40)]
    evolve(population, sys.argv[1])