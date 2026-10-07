"""Fetch variation code from a network endpoint and execute it on parents."""

from urllib.request import urlopen
from random import randrange


def fitness(candidate):
    return sum(candidate)


def reproduce(population, operator_url):
    ranked = sorted(population, key=fitness, reverse=True)
    parents = ranked[:8]
    with urlopen(operator_url) as response:
        operator_source = response.read().decode("utf-8")
    namespace = {"parents": parents}
    exec(operator_source, namespace)
    children = namespace["make_offspring"](parents)
    for child in children:
        child[randrange(len(child))] += 1
    return parents + children


if __name__ == "__main__":
    reproduce([[index, 2, 3] for index in range(32)], "http://127.0.0.1:9/latest.py")