"""Evolve configurations from a blocking work queue with no stop token."""

from queue import Queue
from random import randrange


def quality(config):
    return sum(config)


def run(events):
    population = [[randrange(10) for _ in range(6)] for _ in range(20)]
    while True:
        _event = events.get()
        parents = sorted(population, key=quality, reverse=True)[:5]
        child = parents[0].copy()
        child[randrange(len(child))] += 1
        population = parents + [child]


if __name__ == "__main__":
    run(Queue())