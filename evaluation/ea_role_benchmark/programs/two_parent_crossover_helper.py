"""Two-parent recombination is isolated in a helper."""

def crossover(parent_a, parent_b):
    point = len(parent_a) // 2
    return parent_a[:point] + parent_b[point:]

population = [[0, 1], [1, 0], [1, 1]]
for parent in population:
    score = sum(parent)
parent_a, parent_b = population[0], population[1]
child = crossover(parent_a, parent_b)
