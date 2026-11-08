"""Compile candidate fitness code at runtime for every evaluation batch."""

from random import randrange


def score_with(source, candidate):
    code = compile(source, "<fitness-expression>", "eval")
    return eval(code, {"candidate": candidate})


def select(population, source):
    ranked = sorted(population, key=lambda item: score_with(source, item), reverse=True)
    return ranked[: max(2, len(ranked) // 4)]


def evolve(population, source):
    parents = select(population, source)
    children = [parent.copy() for parent in parents]
    for child in children:
        child[randrange(len(child))] += 1
    return parents + children


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(10)] for _ in range(32)], input("score> "))