"""A generational optimizer whose stagnation counter resets on rare ties."""

from random import randrange


def quality(bits):
    return sum(bits)


def evolve():
    population = [[randrange(2) for _ in range(48)] for _ in range(60)]
    best = -1
    stagnant = 0
    while stagnant < 5:
        scores = [(quality(candidate), candidate) for candidate in population]
        score, champion = max(scores, key=lambda row: row[0])
        if score >= best:
            best = score
            stagnant = 0
        else:
            stagnant += 1
        parents = [row[1] for row in sorted(scores, reverse=True)[:12]]
        population = parents + [
            [gene if randrange(30) else 1 - gene for gene in parents[index % 12]]
            for index in range(48)
        ]
    return champion


if __name__ == "__main__":
    evolve()