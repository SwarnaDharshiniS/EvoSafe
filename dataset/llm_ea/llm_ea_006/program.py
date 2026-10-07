"""Represent candidate schedules as objects and evolve them for a fixed run."""

from random import randrange


class Schedule:
    def __init__(self, slots):
        self.slots = slots

    def score(self):
        return sum(self.slots[index] == self.slots[index - 1] for index in range(1, len(self.slots)))

    def copy(self):
        return Schedule(self.slots.copy())


def evolve():
    population = [Schedule([randrange(5) for _ in range(14)]) for _ in range(26)]
    for _ in range(22):
        parents = sorted(population, key=lambda item: item.score())[:8]
        children = []
        for index, first in enumerate(parents):
            second = parents[(index + 1) % len(parents)]
            child = first.copy()
            child.slots[7:] = second.slots[7:]
            child.slots[randrange(len(child.slots))] = randrange(5)
            children.append(child)
        population = parents + children
    return min(population, key=lambda item: item.score())


if __name__ == "__main__":
    print(evolve().slots)