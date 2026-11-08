"""Load a custom crossover operator by executing submitted Python source."""

from random import randrange


def breed(population, operator_source):
    parents = sorted(population, key=sum, reverse=True)[:6]
    namespace = {"parents": parents, "randrange": randrange}
    exec(operator_source, namespace)
    children = namespace["make_children"](parents)
    return parents + children


if __name__ == "__main__":
    breed([[randrange(10) for _ in range(8)] for _ in range(20)], input("operator> "))