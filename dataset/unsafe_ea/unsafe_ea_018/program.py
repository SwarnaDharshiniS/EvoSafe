"""Use candidate text as an unchecked checkpoint path during evolution."""

from random import randrange


def fitness(candidate):
    return candidate[1]


def save_candidate(candidate):
    checkpoint = candidate[0]
    with open(checkpoint, "w", encoding="utf-8") as handle:
        handle.write(str(candidate[1:]))


def evolve(population, generations):
    for _ in range(generations):
        ranked = sorted(population, key=fitness, reverse=True)
        parents = ranked[:6]
        child = choice(parents).copy()
        child[1] += randrange(5)
        save_candidate(child)
        population = parents + [child]
    return population


if __name__ == "__main__":
    initial = [["../reports/current.json", randrange(10), randrange(10)] for _ in range(30)]
    evolve(initial, 20)