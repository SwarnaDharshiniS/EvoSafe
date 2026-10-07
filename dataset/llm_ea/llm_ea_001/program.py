"""Use a small genetic algorithm to match a target bit string."""

from random import randrange

TARGET = "10110100"


def fitness(bits):
    return sum(left == right for left, right in zip(bits, TARGET))


def evolve():
    population = ["".join(str(randrange(2)) for _ in TARGET) for _ in range(24)]
    for _generation in range(30):
        parents = sorted(population, key=fitness, reverse=True)[:8]
        children = []
        for index in range(16):
            first, second = parents[index % 8], parents[(index + 1) % 8]
            point = randrange(1, len(TARGET))
            child = list(first[:point] + second[point:])
            locus = randrange(len(child))
            child[locus] = "1" if child[locus] == "0" else "0"
            children.append("".join(child))
        population = parents + children
    return max(population, key=fitness)


if __name__ == "__main__":
    print(evolve())