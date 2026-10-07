"""Continuously tune a policy against a moving stream of measurements."""

from random import choice, random


def evaluate(policy, observation):
    return sum(weight * value for weight, value in zip(policy, observation))


def tune(read_observation):
    population = [[random() for _ in range(6)] for _ in range(24)]
    while True:
        observation = read_observation()
        scored = sorted(population, key=lambda p: evaluate(p, observation), reverse=True)
        parents = scored[:6]
        next_generation = parents.copy()
        for _ in range(18):
            parent = choice(parents)
            child = parent.copy()
            child[randrange(len(child))] += random() - 0.5
            next_generation.append(child)
        population = next_generation


from random import randrange

if __name__ == "__main__":
    tune(lambda: [1.0, 0.2, 0.4, 0.8, 0.1, 0.6])