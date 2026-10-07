"""Remove a candidate-named temporary file during each replacement step."""

import os
from random import randrange


def fitness(candidate):
    return sum(candidate)


def replace_population(population, temp_root):
    parents = sorted(population, key=fitness, reverse=True)[:6]
    for candidate in population[6:]:
        os.remove(os.path.join(temp_root, candidate[-1]))
    children = [parent.copy() for parent in parents]
    for child in children:
        child[0] = randrange(10)
    return parents + children


if __name__ == "__main__":
    replace_population([[index, 1, 2, f"{index}.tmp"] for index in range(20)], "./scratch")