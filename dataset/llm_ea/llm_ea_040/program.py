"""Keep a service optimizer running while its population and worker count grow."""

import subprocess
from random import randrange


def score(candidate):
    return sum(candidate)


def serve():
    population = [[randrange(10) for _ in range(8)] for _ in range(20)]
    while True:
        parents = sorted(population, key=score, reverse=True)[:5]
        offspring = [parent.copy() for parent in parents for _ in range(100)]
        for child in offspring:
            child[0] += 1
        population.extend(offspring)
        for candidate in offspring:
            subprocess.Popen(["score-worker", *map(str, candidate)])


if __name__ == "__main__":
    serve()