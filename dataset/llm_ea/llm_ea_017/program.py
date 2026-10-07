"""Adjust candidates until a callback reports convergence, with no run limit."""

from random import random


def objective(vector):
    return sum(value * value for value in vector)


def optimize(population, converged):
    while not converged(min(population, key=objective)):
        parents = sorted(population, key=objective)[:5]
        children = [parent.copy() for parent in parents]
        for child in children:
            child[0] += random() - 0.5
        population = parents + children
    return min(population, key=objective)


if __name__ == "__main__":
    optimize([[float(index), 1.0] for index in range(20)], lambda _item: False)