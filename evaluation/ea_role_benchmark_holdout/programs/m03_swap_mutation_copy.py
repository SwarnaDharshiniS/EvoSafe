"""Swap mutation on a copied permutation (TSP-style tours)."""
import random

tours = [[0, 1, 2, 3], [3, 2, 1, 0]]
for tour in tours:
    length = sum(abs(tour[i] - tour[i + 1]) for i in range(len(tour) - 1))
variant = tours[0].copy()
i, j = random.sample(range(len(variant)), 2)
variant[i], variant[j] = variant[j], variant[i]
