"""Recursively fork candidate lineages without a depth or offspring limit."""

from random import randrange


def fitness(candidate):
    return sum(candidate)


def expand_lineage(parent):
    child = parent.copy()
    child[randrange(len(child))] += 1
    descendants = [child]
    for branch in (child, child.copy()):
        descendants.extend(expand_lineage(branch))
    return descendants


def evolve(population):
    parents = sorted(population, key=fitness, reverse=True)[:4]
    descendants = [child for parent in parents for child in expand_lineage(parent)]
    return parents + descendants


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(8)] for _ in range(20)])