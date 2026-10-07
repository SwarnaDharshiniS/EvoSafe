"""Mutation helper that returns a perturbed new list."""
import random


def perturb(solution, step):
    return [x + random.uniform(-step, step) for x in solution]


population = [[0.0, 0.0], [1.0, 1.0]]
for s in population:
    cost = abs(s[0]) + abs(s[1])
    neighbour = perturb(s, 0.1)
