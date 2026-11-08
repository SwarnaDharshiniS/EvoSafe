"""A compact EA with visible roles."""
import random

population = [[0, 1], [1, 0], [1, 1], [0, 0]]
for individual in population:
    fitness_value = sum(individual)
selected = sorted(population, key=sum, reverse=True)[:2]
offspring = []
for individual in selected:
    child = individual.copy()
    child[0] += random.randint(0, 1)
    offspring.append(child)
for parent_a, parent_b in zip(selected, selected[1:]):
    child = parent_a[:1] + parent_b[1:]
    offspring.append(child)
population = selected + offspring
for generation in range(3):
    for individual in population:
        fitness_value = sum(individual)
