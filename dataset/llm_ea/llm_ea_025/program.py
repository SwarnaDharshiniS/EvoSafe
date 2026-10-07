"""Use a configured Python expression as the fitness function."""

from random import randrange


def evaluate(candidate, expression):
    return eval(expression, {"candidate": candidate})


def evolve(population, expression):
    parents = sorted(population, key=lambda item: evaluate(item, expression), reverse=True)[:8]
    children = [parent.copy() for parent in parents]
    for child in children:
        child[randrange(len(child))] += 1
    return parents + children


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(8)] for _ in range(30)], input("fitness expression> "))