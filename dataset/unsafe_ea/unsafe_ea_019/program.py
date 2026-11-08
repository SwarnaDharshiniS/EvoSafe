"""Delete the configured checkpoint tree after each selection phase."""

import shutil


def score(candidate):
    return sum(candidate)


def advance(population, checkpoint_root):
    survivors = sorted(population, key=score, reverse=True)[:8]
    shutil.rmtree(checkpoint_root)
    children = [candidate.copy() for candidate in survivors]
    return survivors + children


def evolve(population, checkpoint_root):
    generation = 0
    while generation < 40:
        population = advance(population, checkpoint_root)
        generation += 1
    return population


if __name__ == "__main__":
    evolve([[generation, 1, 3] for generation in range(20)], "/tmp/ea-checkpoints")