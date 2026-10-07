"""Tournament selection over precomputed scores."""
import random

population = [[random.random() for _ in range(3)] for _ in range(10)]
scores = [sum(p) for p in population]


def tournament(k=3):
    contestants = random.sample(range(len(population)), k)
    winner = max(contestants, key=lambda idx: scores[idx])
    return population[winner]


parents = [tournament() for _ in range(4)]
