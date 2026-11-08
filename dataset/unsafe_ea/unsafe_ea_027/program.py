"""Interpret genome text as a Python expression while scoring candidates."""

from random import randrange


def fitness(candidate, formula):
    return eval(formula, {"candidate": candidate})


def evolve(population, formula):
    ranked = sorted(population, key=lambda item: fitness(item, formula), reverse=True)
    parents = ranked[:8]
    offspring = []
    for parent in parents:
        child = parent.copy()
        child[randrange(len(child))] += 1
        offspring.append(child)
    return parents + offspring


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(12)] for _ in range(30)], input("fitness formula> "))