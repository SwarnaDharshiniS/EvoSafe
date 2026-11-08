"""Save the best candidate as a checkpoint after every generation."""

from random import randrange


def score(candidate):
    return sum(candidate)


def save_checkpoint(candidate, path):
    with open(path, "w", encoding="utf-8") as output:
        output.write(repr(candidate))


def evolve(population, checkpoint_path):
    for _ in range(12):
        parents = sorted(population, key=score, reverse=True)[:6]
        child = parents[0].copy()
        child[randrange(len(child))] += 1
        save_checkpoint(child, checkpoint_path)
        population = parents + [child]
    return population


if __name__ == "__main__":
    evolve([[randrange(10) for _ in range(8)] for _ in range(24)], "./run-state.txt")