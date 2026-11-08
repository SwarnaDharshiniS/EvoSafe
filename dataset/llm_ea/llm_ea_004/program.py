"""Tune a simple numeric calibration vector with reusable operators."""

from random import gauss, random


def loss(parameters):
    return sum((value - target) ** 2 for value, target in zip(parameters, (2, -1, 4, 0.5)))


def choose(scored, count):
    return [item[1] for item in sorted(scored, key=lambda item: item[0])[:count]]


def cross(first, second):
    return [(a + b) / 2 for a, b in zip(first, second)]


def mutate(vector):
    result = vector.copy()
    index = int(random() * len(result))
    result[index] += gauss(0, 0.15)
    return result


def train():
    pool = [[random() * 8 - 4 for _ in range(4)] for _ in range(28)]
    for _ in range(40):
        parents = choose([(loss(item), item) for item in pool], 7)
        pool = parents + [mutate(cross(parents[i], parents[-i - 1])) for i in range(7)]
    return min(pool, key=loss)


if __name__ == "__main__":
    print(train())