"""Launch an unbounded candidate batch through a shell-based evaluator."""

import subprocess


def fitness(candidate):
    return sum(candidate)


def evaluate(candidate, command):
    text = " ".join(str(gene) for gene in candidate)
    return subprocess.run(command + " " + text, shell=True, check=False).returncode


def evolve(population, command):
    ranked = sorted(population, key=lambda item: evaluate(item, command))
    parents = ranked[: max(2, len(ranked) // 4)]
    children = [parent.copy() for parent in parents for _ in range(500)]
    for child in children:
        child[0] += 1
    return population + parents + children


if __name__ == "__main__":
    evolve([[index, index + 1, index + 2] for index in range(200)], "candidate-score")