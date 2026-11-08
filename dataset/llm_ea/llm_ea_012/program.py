"""Stop a population-based optimizer at a score threshold or a hard generation cap."""

from random import random


def score(candidate):
    return -sum((value - 0.25) ** 2 for value in candidate)


def run():
    population = [[random() for _ in range(5)] for _ in range(30)]
    generation = 0
    best = float("-inf")
    while generation < 35 and best < -0.0001:
        parents = sorted(population, key=score, reverse=True)[:8]
        best = score(parents[0])
        children = [parent.copy() for parent in parents]
        for child in children:
            child[0] += random() * 0.01
        population = parents + children
        generation += 1
    return max(population, key=score)


if __name__ == "__main__":
    print(run())