"""Arithmetic (blend) crossover in a helper, applied to adjacent members."""


def blend(x, y, alpha=0.5):
    return [alpha * a + (1 - alpha) * b for a, b in zip(x, y)]


population = [[0.1, 0.2], [0.4, 0.8], [0.9, 0.3]]
for vec in population:
    loss = sum(v * v for v in vec)
offspring = [blend(population[i], population[i + 1]) for i in range(len(population) - 1)]
