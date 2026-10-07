"""Replace the worst-scoring member by index."""
import random

population = [[random.random()] for _ in range(5)]
scores = [p[0] for p in population]
worst = scores.index(min(scores))
population[worst] = [random.random()]
