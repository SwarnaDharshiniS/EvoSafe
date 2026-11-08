"""Generate offspring indefinitely while a numeric validator rejects them."""

from random import randrange


def valid(genome):
    return sum(genome) < 0


def make_child(parent):
    while True:
        child = parent.copy()
        child[randrange(len(child))] = randrange(10)
        if valid(child):
            return child


def breed(population):
    parents = sorted(population, key=sum)[:6]
    return parents + [make_child(parents[index % 6]) for index in range(12)]


if __name__ == "__main__":
    breed([[randrange(10) for _ in range(8)] for _ in range(30)])