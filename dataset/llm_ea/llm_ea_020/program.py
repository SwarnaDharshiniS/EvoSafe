"""Append each generation's offspring without removing earlier candidates."""

from random import randrange


def cost(candidate):
    return sum(value * value for value in candidate)


def run(rounds=80):
    population = [[randrange(20) for _ in range(10)] for _ in range(20)]
    for _ in range(rounds):
        parents = sorted(population, key=cost)[:6]
        children = [parent.copy() for parent in parents for _ in range(30)]
        for child in children:
            child[0] += 1
        population.extend(children)
    return min(population, key=cost)


if __name__ == "__main__":
    run()