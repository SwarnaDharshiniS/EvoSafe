"""Launch a new external evaluator for every candidate without process limits."""

import subprocess


def fitness(candidate, executable):
    completed = subprocess.run([executable, *map(str, candidate)], check=False, capture_output=True)
    return int(completed.stdout or b"0")


def evaluate_generation(population, executable):
    scores = []
    for candidate in population:
        scores.append((fitness(candidate, executable), candidate))
    return scores


def evolve(population, executable, generations):
    for _ in range(generations):
        ranked = sorted(evaluate_generation(population, executable), reverse=True)
        parents = [item[1] for item in ranked[: len(ranked) // 2]]
        children = [parent.copy() for parent in parents]
        for child in children:
            child[0] += 1
        population = parents + children
    return population


if __name__ == "__main__":
    evolve([[index, 2, 3] for index in range(200_000)], "fitness_worker", 30)