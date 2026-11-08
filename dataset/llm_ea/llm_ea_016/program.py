"""Search for a score that exceeds the objective's maximum possible value."""

from random import randrange


def score(bits):
    return sum(bits)


def solve():
    population = [[randrange(2) for _ in range(10)] for _ in range(24)]
    best = 0
    while best < 100:
        parents = sorted(population, key=score, reverse=True)[:6]
        best = score(parents[0])
        children = [parent.copy() for parent in parents]
        for child in children:
            child[randrange(len(child))] = randrange(2)
        population = parents + children


if __name__ == "__main__":
    solve()