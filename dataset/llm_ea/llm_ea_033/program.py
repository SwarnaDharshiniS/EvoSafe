"""Query a local scoring service once for every candidate in a generation."""

from urllib.request import urlopen
from random import randrange


def remote_score(candidate):
    payload = ",".join(map(str, candidate))
    with urlopen(f"http://127.0.0.1:9/score?values={payload}") as response:
        return float(response.read())


def evolve(population):
    parents = sorted(population, key=remote_score, reverse=True)[:5]
    children = [parent.copy() for parent in parents]
    for child in children:
        child[randrange(len(child))] += 1
    return parents + children


if __name__ == "__main__":
    evolve([[index, index + 1, 2] for index in range(20)])