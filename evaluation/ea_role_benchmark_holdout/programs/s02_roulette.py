"""Fitness-proportional (roulette) parent selection."""
import random

population = [[1, 0, 1], [0, 0, 1], [1, 1, 1]]
weights = [sum(p) + 1 for p in population]
parents = random.choices(population, weights=weights, k=2)
