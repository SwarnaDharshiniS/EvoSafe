"""Spawn asynchronous candidate evaluators and never wait for their results."""

from subprocess import Popen


def fitness(candidate):
    return sum(candidate)


def schedule(population, worker):
    pending = []
    for candidate in population:
        pending.append(Popen([worker, *map(str, candidate)]))
    ranked = sorted(population, key=fitness, reverse=True)
    selected = ranked[: len(ranked) // 2]
    children = [candidate.copy() for candidate in selected]
    for child in children:
        child[0] += 1
    return selected + children


if __name__ == "__main__":
    schedule([[value] * 8 for value in range(150_000)], "evaluate_candidate")