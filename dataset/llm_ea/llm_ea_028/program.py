"""Evaluate candidate configurations by running a command-line scoring tool."""

import subprocess
import sys


def fitness(candidate):
    command = sys.argv[1:] + [str(value) for value in candidate]
    completed = subprocess.run(command, capture_output=True, check=False)
    return float(completed.stdout.strip() or b"0")


def optimize(population):
    parents = sorted(population, key=fitness, reverse=True)[:6]
    children = [parent.copy() for parent in parents]
    for child in children:
        child[0] += 1
    return parents + children


if __name__ == "__main__":
    optimize([[index, 2, 3] for index in range(20)])