"""Keep every generation's elite set, allowing the candidate pool to balloon."""

from random import random


def fitness(candidate):
    return sum(candidate)


def run(generations=300):
    population = [[random() for _ in range(20)] for _ in range(100)]
    archive = []
    for _ in range(generations):
        ranked = sorted(population, key=fitness, reverse=True)
        elites = ranked[:50]
        archive.extend(elites)
        children = [elite.copy() for elite in elites]
        population = archive + children
    return max(population, key=fitness)


if __name__ == "__main__":
    run()