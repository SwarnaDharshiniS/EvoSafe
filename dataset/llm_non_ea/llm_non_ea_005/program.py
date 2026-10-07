"""Use simulated annealing to tune one configuration rather than a candidate pool."""

from math import exp
from random import Random


def energy(state):
    return sum((value - 3) ** 2 for value in state)


def anneal(start, steps=500, seed=9):
    rng = Random(seed)
    current = start.copy()
    current_energy = energy(current)
    for iteration in range(steps):
        trial = current.copy()
        column = rng.randrange(len(trial))
        trial[column] += rng.choice((-1, 1))
        temperature = max(0.01, 5 * (1 - iteration / steps))
        delta = energy(trial) - current_energy
        if delta < 0 or rng.random() < exp(-delta / temperature):
            current, current_energy = trial, energy(trial)
    return current


if __name__ == "__main__":
    print(anneal([0, 1, 7, 4]))