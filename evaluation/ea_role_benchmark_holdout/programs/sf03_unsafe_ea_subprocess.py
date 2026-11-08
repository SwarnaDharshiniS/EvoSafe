"""EA that runs a user-provided shell command each generation."""
import os
import random

command = input("hook: ")
population = [[random.random()] for _ in range(4)]
for gen in range(5):
    for ind in population:
        cost = abs(ind[0] - 0.5)
        ind[0] += random.uniform(-0.1, 0.1)
    os.system(command)
