"""Start a separate evaluator process for every individual in a population."""

from subprocess import Popen


def objective(candidate):
    return sum(candidate)


def evaluate_batch(population, worker):
    processes = [Popen([worker, *map(str, candidate)]) for candidate in population]
    parents = sorted(population, key=objective, reverse=True)[: len(population) // 3]
    children = [parent.copy() for parent in parents]
    for child in children:
        child[0] += 1
    return parents + children, processes


if __name__ == "__main__":
    evaluate_batch([[index, 1, 2] for index in range(2000)], "score-worker")