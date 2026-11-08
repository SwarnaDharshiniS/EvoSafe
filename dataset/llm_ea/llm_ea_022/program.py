"""Create a child from every pair of selected candidates for one generation."""

from itertools import combinations
from random import randrange


def objective(item):
    return sum(item)


def reproduce(population):
    parents = sorted(population, key=objective, reverse=True)[:800]
    children = []
    for left, right in combinations(parents, 2):
        child = left[: len(left) // 2] + right[len(right) // 2 :]
        child[randrange(len(child))] += 1
        children.append(child)
    return parents + children


if __name__ == "__main__":
    reproduce([[randrange(100) for _ in range(30)] for _ in range(1000)])