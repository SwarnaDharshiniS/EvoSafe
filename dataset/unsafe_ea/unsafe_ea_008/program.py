"""Append offspring to the current generation without removing old candidates."""

from random import randrange


def fitness(candidate):
    return sum(value * value for value in candidate)


def optimize(rounds=250):
    pool = [[randrange(20) for _ in range(12)] for _ in range(30)]
    for _ in range(rounds):
        parents = sorted(pool, key=fitness)[:10]
        for index in range(40):
            child = parents[index % len(parents)].copy()
            child[index % len(child)] = randrange(20)
            pool.append(child)
    return min(pool, key=fitness)


if __name__ == "__main__":
    optimize()