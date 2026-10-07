"""No-improvement (stagnation) termination with random perturbation."""
import random

population = [[random.random()] for _ in range(4)]
best, stale = float("inf"), 0
while stale < 10:
    current = min((ind[0] - 0.3) ** 2 for ind in population)
    if current < best:
        best, stale = current, 0
    else:
        stale += 1
    for ind in population:
        ind[0] += random.gauss(0, 0.05)
