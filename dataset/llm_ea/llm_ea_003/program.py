"""Optimize a fixed-size shipment plan using tuples and helper functions."""

from random import randrange

CAPACITY = 40


def cost(plan):
    overflow = max(0, sum(plan) - CAPACITY)
    return overflow * 20 + sum(abs(value - 5) for value in plan)


def make_child(first, second):
    split = len(first) // 2
    child = list(first[:split] + second[split:])
    child[randrange(len(child))] += randrange(-2, 3)
    return tuple(child)


def optimize():
    population = [tuple(randrange(10) for _ in range(8)) for _ in range(36)]
    for _ in range(18):
        selected = sorted(population, key=cost)[:9]
        descendants = [make_child(selected[i], selected[-i - 1]) for i in range(9)]
        population = selected + descendants
    return min(population, key=cost)


if __name__ == "__main__":
    print(optimize())