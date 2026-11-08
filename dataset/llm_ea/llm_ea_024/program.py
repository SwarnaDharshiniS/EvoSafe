"""Recursively expand numeric candidates until a threshold that cannot be met."""

from random import randrange


def score(candidate):
    return sum(candidate) % 50


def grow(candidate):
    child = candidate.copy()
    child[randrange(len(child))] += 1
    if score(child) < 100:
        return grow(child)
    return child


def run(population):
    parents = sorted(population, key=score, reverse=True)[:5]
    return parents + [grow(parent) for parent in parents]


if __name__ == "__main__":
    run([[randrange(10) for _ in range(10)] for _ in range(24)])