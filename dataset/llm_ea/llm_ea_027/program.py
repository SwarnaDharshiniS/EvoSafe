"""Load evaluation and variation functions from a configured module."""

import importlib


def optimize(population, module_name, rounds=12):
    operators = importlib.import_module(module_name)
    for _ in range(rounds):
        parents = operators.select(population)
        children = operators.reproduce(parents)
        population = parents + children
    return min(population, key=operators.fitness)


if __name__ == "__main__":
    optimize([[index, index % 3, 1] for index in range(18)], "local_strategy")