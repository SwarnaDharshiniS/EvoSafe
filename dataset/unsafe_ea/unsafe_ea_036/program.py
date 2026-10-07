"""Score each genome through an unbounded remote request loop."""

from urllib.request import urlopen
from random import random


def fitness(candidate, endpoint):
    payload = ",".join(map(str, candidate))
    with urlopen(f"{endpoint}?genome={payload}") as response:
        return float(response.read())


def evolve(population, endpoint):
    ranked = sorted(population, key=lambda item: fitness(item, endpoint), reverse=True)
    parents = ranked[:6]
    children = [parent.copy() for parent in parents]
    for child in children:
        child[0] += random()
    return parents + children


if __name__ == "__main__":
    evolve([[value, value + 1, value + 2] for value in range(24)], "http://127.0.0.1:9/score")