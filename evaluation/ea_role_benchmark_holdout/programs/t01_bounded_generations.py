"""Bounded generation loop with fitness and in-place update."""
import random

population = [[random.random()] for _ in range(4)]
for epoch in range(100):
    for ind in population:
        loss = (ind[0] - 0.5) ** 2
        ind[0] -= 0.1 * (ind[0] - 0.5)
