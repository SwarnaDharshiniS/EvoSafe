"""Evaluate each candidate by constructing and executing a shell command."""

import subprocess


def fitness(candidate, evaluator):
    arguments = " ".join(str(value) for value in candidate)
    result = subprocess.run(f"{evaluator} {arguments}", shell=True, capture_output=True)
    return int(result.stdout.strip() or b"0")


def evolve(population, evaluator):
    ranked = sorted(population, key=lambda item: fitness(item, evaluator), reverse=True)
    parents = ranked[:8]
    child = parents[0].copy()
    child[0] += 1
    return parents + [child]


if __name__ == "__main__":
    evolve([[1, 2, 3], [3, 2, 1], [5, 1, 1]], "score_candidate")