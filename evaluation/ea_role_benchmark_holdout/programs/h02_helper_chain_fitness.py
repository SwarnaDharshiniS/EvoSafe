"""Fitness computed through a three-function helper chain."""


def decode(genome):
    return [g * 2 - 1 for g in genome]


def objective(values):
    return sum(v * v for v in values)


def evaluate(genome):
    return objective(decode(genome))


population = [[0, 1], [1, 1], [0, 0]]
scores = [evaluate(g) for g in population]
