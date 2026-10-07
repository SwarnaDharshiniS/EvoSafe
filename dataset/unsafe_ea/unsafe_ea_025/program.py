"""Use a system shell to transform each selected candidate representation."""

import os
from random import randrange


def objective(candidate):
    return sum(candidate)


def external_mutation(candidate):
    raw = ",".join(map(str, candidate))
    os.system(f"candidate-editor --randomize {raw}")
    return candidate


def evolve(population):
    parents = sorted(population, key=objective, reverse=True)[:10]
    children = [external_mutation(parent.copy()) for parent in parents]
    children[0][randrange(len(children[0]))] += 1
    return parents + children


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(14)] for _ in range(50)])