"""Recursively produce multiple descendants without a depth or count limit."""

from random import randrange


def quality(candidate):
    return sum(candidate)


def descendants(parent, depth):
    children = []
    for _ in range(3):
        child = parent.copy()
        child[randrange(len(child))] += 1
        children.append(child)
        if quality(child) < 1000:
            children.extend(descendants(child, depth + 1))
    return children


def evolve(population):
    parents = sorted(population, key=quality, reverse=True)[:5]
    return parents + [child for parent in parents for child in descendants(parent, 0)]


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(12)] for _ in range(20)])