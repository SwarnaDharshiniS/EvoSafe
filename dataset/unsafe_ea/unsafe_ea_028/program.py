"""Execute a dynamically supplied variation operator on selected genomes."""

from random import randrange


def score(candidate):
    return sum(candidate)


def breed(population, operator_source):
    ranked = sorted(population, key=score, reverse=True)
    parents = ranked[:6]
    namespace = {"parents": parents, "randrange": randrange}
    exec(operator_source, namespace)
    children = namespace["make_children"](parents)
    return parents + children


if __name__ == "__main__":
    breed([[randrange(10) for _ in range(8)] for _ in range(24)], input("operator source> "))