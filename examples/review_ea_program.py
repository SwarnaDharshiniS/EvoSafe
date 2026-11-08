"""Evolve short integer vectors toward a fixed target over eight generations."""

import random


TARGET = (2, 4, 1, 3, 5, 0)


def distance(candidate: list[int]) -> int:
    return sum(abs(gene - target) for gene, target in zip(candidate, TARGET))


def evolve(seed: int = 7) -> tuple[list[int], int]:
    rng = random.Random(seed)
    population = [[rng.randrange(6) for _ in TARGET] for _ in range(12)]

    for _generation in range(8):
        parents = sorted(population, key=distance)[:4]
        children = []
        for index, first in enumerate(parents):
            second = parents[(index + 1) % len(parents)]
            child = first[:3] + second[3:]
            position = rng.randrange(len(child))
            child[position] = rng.randrange(6)
            children.append(child)
        population = parents + children

    best = min(population, key=distance)
    return best, distance(best)


if __name__ == "__main__":
    print(evolve())