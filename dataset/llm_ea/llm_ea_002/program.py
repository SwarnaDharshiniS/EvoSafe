"""Search for low-conflict room assignments with a bounded genetic algorithm."""

from random import randrange

ROOMS = 6


def conflicts(schedule):
    return sum(schedule[index] == schedule[index - 1] for index in range(1, len(schedule)))


def crossover(left, right):
    seam = len(left) // 2
    return left[:seam] + right[seam:]


def run():
    population = [[randrange(ROOMS) for _ in range(12)] for _ in range(32)]
    for _ in range(25):
        parents = sorted(population, key=conflicts)[:8]
        offspring = []
        for index, parent in enumerate(parents):
            child = crossover(parent, parents[(index + 1) % len(parents)])
            child[randrange(len(child))] = randrange(ROOMS)
            offspring.append(child)
        population = parents + offspring
    return min(population, key=conflicts)


if __name__ == "__main__":
    print(run())