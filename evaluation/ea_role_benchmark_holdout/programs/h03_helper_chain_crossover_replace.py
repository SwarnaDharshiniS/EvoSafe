"""Generation step split across helpers: ranking, recombination, rebuild."""
import random


def splice(a, b, cut):
    return a[:cut] + b[cut:]


def recombine(mother, father):
    cut = random.randrange(1, len(mother))
    return splice(mother, father, cut)


def next_generation(pool):
    pool.sort(key=sum, reverse=True)
    parents = pool[:2]
    child = recombine(parents[0], parents[1])
    return parents + [child]


pool = [[0, 1, 1], [1, 0, 0], [1, 1, 1]]
for gen in range(10):
    pool = next_generation(pool)
