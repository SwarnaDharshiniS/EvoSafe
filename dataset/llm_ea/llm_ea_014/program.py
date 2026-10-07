"""Optimize a numeric model with a compact population and elitist replacement."""

from random import gauss, random


def objective(weights):
    return (weights[0] - 1) ** 2 + (weights[1] + 2) ** 2 + abs(weights[2])


def improve():
    population = [[random() * 4 - 2 for _ in range(3)] for _ in range(20)]
    for _ in range(24):
        ranked = sorted(population, key=objective)
        parents = ranked[:5]
        children = []
        for first, second in zip(parents, parents[1:] + parents[:1]):
            child = [(a + b) / 2 + gauss(0, 0.05) for a, b in zip(first, second)]
            children.append(child)
        population = parents + children
    return min(population, key=objective)


if __name__ == "__main__":
    print(improve())