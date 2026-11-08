"""Route optimizer with no generation limit or convergence stop."""

from random import randrange


def distance(route):
    return sum(abs(route[index] - route[index - 1]) for index in range(len(route)))


def breed(population):
    ranked = sorted(population, key=distance)
    parents = ranked[: max(2, len(ranked) // 3)]
    left, right = parents[0], parents[-1]
    point = len(left) // 2
    child = left[:point] + right[point:]
    child[randrange(len(child))] = randrange(100)
    return ranked, child


def optimize():
    population = [[randrange(100) for _ in range(20)] for _ in range(80)]
    while True:
        survivors, child = breed(population)
        population[:] = survivors + [child]


if __name__ == "__main__":
    optimize()