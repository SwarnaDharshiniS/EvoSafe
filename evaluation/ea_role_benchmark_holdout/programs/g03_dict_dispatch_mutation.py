"""Mutation dispatched through a dict of operators."""
import random


def jitter(vec):
    out = list(vec)
    out[0] += random.random()
    return out


ops = {"mut": jitter}
population = [[0.0, 1.0], [1.0, 0.0]]
for vec in population:
    score = sum(vec)
    child = ops["mut"](vec)
