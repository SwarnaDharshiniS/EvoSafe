"""Combine tuple genomes and mutate a bounded set of numeric candidates."""

from random import randrange


def error(values):
    return sum((value - 4) ** 2 for value in values)


def next_pool(population):
    parents = sorted(population, key=error)[:7]
    children = []
    for index in range(14):
        left, right = parents[index % 7], parents[(index + 2) % 7]
        point = randrange(1, len(left))
        child = list(left[:point] + right[point:])
        child[-1] += randrange(-1, 2)
        children.append(tuple(child))
    return parents + children


def main():
    population = [tuple(randrange(9) for _ in range(6)) for _ in range(28)]
    generation = 0
    while generation < 20:
        population = next_pool(population)
        generation += 1
    return min(population, key=error)


if __name__ == "__main__":
    print(main())