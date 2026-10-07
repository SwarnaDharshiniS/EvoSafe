"""Extract candidate-produced archives into a shared output directory."""

import tarfile
import sys
from random import randrange


def fitness(candidate):
    return sum(candidate)


def evaluate_artifact(candidate, archive_path):
    with tarfile.open(archive_path) as bundle:
        bundle.extractall("/srv/evolution/artifacts")
    return fitness(candidate)


def evolve(population, archives):
    ranked = sorted(population, key=fitness, reverse=True)
    selected = ranked[: len(ranked) // 2]
    for index, candidate in enumerate(selected):
        evaluate_artifact(candidate, archives[index])
    offspring = [candidate.copy() for candidate in selected]
    for child in offspring:
        child[0] += 1
    return selected + offspring


if __name__ == "__main__":
    archives = sys.argv[1:]
    population = [[randrange(20) for _ in range(10)] for _ in range(2 * len(archives))]
    evolve(population, archives)