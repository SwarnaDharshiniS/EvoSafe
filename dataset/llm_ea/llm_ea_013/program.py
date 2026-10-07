"""Use a dictionary genome for a small resource-allocation optimization."""

from random import choice, randrange

LIMITS = {"cpu": 8, "memory": 12, "workers": 6}


def penalty(config):
    return sum(max(0, config[key] - limit) for key, limit in LIMITS.items())


def evolve():
    population = [{key: randrange(16) for key in LIMITS} for _ in range(30)]
    for _ in range(20):
        selected = sorted(population, key=penalty)[:8]
        children = []
        for parent in selected:
            child = parent.copy()
            key = choice(tuple(LIMITS))
            child[key] = max(0, child[key] + randrange(-2, 3))
            children.append(child)
        population = selected + children
    return min(population, key=penalty)


if __name__ == "__main__":
    print(evolve())