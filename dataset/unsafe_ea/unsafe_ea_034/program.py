"""Deep-copy large nested candidates during each selection and reproduction pass."""

from copy import deepcopy
from random import randrange


def fitness(candidate):
    return sum(sum(row) for row in candidate)


def evolve(population, generations=30):
    for _ in range(generations):
        ranked = sorted(population, key=fitness, reverse=True)
        survivors = [deepcopy(item) for item in ranked[:20]]
        offspring = [deepcopy(item) for item in survivors for _ in range(5)]
        for child in offspring:
            child[randrange(len(child))][0] += 1
        population = survivors + offspring
    return population


if __name__ == "__main__":
    evolve([[[randrange(10) for _ in range(400)] for _ in range(300)] for _ in range(100)])