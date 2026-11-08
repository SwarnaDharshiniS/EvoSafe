"""Enumerate a massive discrete genome space and materialize every candidate."""

from itertools import product


def fitness(genome):
    return sum(genome)


def search():
    population = list(product(range(100), repeat=8))
    ranked = sorted(population, key=fitness, reverse=True)
    selected = ranked[:20]
    offspring = [tuple(value + 1 for value in candidate) for candidate in selected]
    return selected + offspring


if __name__ == "__main__":
    search()