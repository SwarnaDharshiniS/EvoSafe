"""Gaussian mutation applied in place to every candidate."""
import random

population = [[random.gauss(0, 1) for _ in range(3)] for _ in range(5)]
for vec in population:
    energy = sum(x * x for x in vec)
for vec in population:
    for i in range(len(vec)):
        vec[i] += random.gauss(0, 0.1)
