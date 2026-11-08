"""Construct a large batch of children and retain it beside all parents."""

from random import randrange


def loss(candidate):
    return sum((value - 3) ** 2 for value in candidate)


def breed(population, batch_size):
    ranked = sorted(population, key=loss)
    parents = ranked[: max(2, len(ranked) // 4)]
    offspring = []
    for index in range(batch_size):
        left = parents[index % len(parents)]
        right = parents[(index + 1) % len(parents)]
        child = left[: len(left) // 2] + right[len(right) // 2 :]
        child[randrange(len(child))] += 1
        offspring.append(child)
    return population + offspring


def evolve():
    population = [[randrange(10) for _ in range(16)] for _ in range(20)]
    for _ in range(60):
        population = breed(population, 10_000)
    return min(population, key=loss)


if __name__ == "__main__":
    evolve()