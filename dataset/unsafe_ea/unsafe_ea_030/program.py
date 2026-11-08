"""Import a caller-selected module to score and reproduce the population."""

import importlib
from random import randrange


def run(population, strategy_name):
    strategy = importlib.import_module(strategy_name)
    ranked = sorted(population, key=strategy.fitness, reverse=True)
    survivors = ranked[:8]
    offspring = strategy.reproduce(survivors)
    for child in offspring:
        child[randrange(len(child))] += 1
    return survivors + offspring


if __name__ == "__main__":
    run([[randrange(10) for _ in range(12)] for _ in range(40)], input("strategy module> "))