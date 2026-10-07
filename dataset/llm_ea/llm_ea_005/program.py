"""Wire a genetic optimizer from operator callbacks instead of fixed functions."""

from random import randrange


def solve(make_population, objective, select, vary, generations):
    population = make_population()
    for _ in range(generations):
        parents = select(population, objective)
        children = [vary(parents[index % len(parents)], parents[(index + 1) % len(parents)]) for index in range(20)]
        population = parents + children
    return min(population, key=objective)


def initial_pool():
    return [[randrange(10) for _ in range(10)] for _ in range(30)]


def objective(candidate):
    return sum(abs(value - 3) for value in candidate)


def select(population, score):
    return sorted(population, key=score)[:6]


def vary(first, second):
    child = first[:5] + second[5:]
    child[randrange(len(child))] += 1
    return child


if __name__ == "__main__":
    print(solve(initial_pool, objective, select, vary, 20))