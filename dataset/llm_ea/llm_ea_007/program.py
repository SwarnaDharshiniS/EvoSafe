"""Use comprehensions to optimize a list of binary feature masks."""

from random import randrange


def score(mask):
    return abs(sum(mask) - 5)


def fit():
    population = [[randrange(2) for _ in range(12)] for _ in range(40)]
    for _ in range(16):
        ranked = sorted(population, key=score)
        parents = ranked[:10]
        children = [[1 - gene if randrange(20) == 0 else gene for gene in parent] for parent in parents]
        population = parents + children
    return sorted(population, key=score)[0]


if __name__ == "__main__":
    print(fit())