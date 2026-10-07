"""Safe, bounded evolutionary-style search."""
import random
population = [[0, 0], [0, 1], [1, 0]]
for candidate in population:
    score = sum(candidate)
selected = sorted(population, key=sum, reverse=True)[:2]
offspring = []
for candidate in selected:
    child = candidate.copy()
    child[random.randrange(len(child))] = 1
    offspring.append(child)
population = selected + offspring
for generation in range(4):
    for candidate in population:
        score = sum(candidate)
