"""Search for a score threshold that the scoring function cannot reach."""

from random import randrange


def score(candidate):
    return sum(candidate) % 100


def hunt():
    population = [[randrange(100) for _ in range(10)] for _ in range(50)]
    champion_score = -1
    while champion_score < 100:
        ranked = sorted(population, key=score, reverse=True)
        champion_score = score(ranked[0])
        chosen = ranked[:10]
        offspring = []
        for index, parent in enumerate(chosen):
            child = parent.copy()
            child[index % len(child)] = randrange(100)
            offspring.append(child)
        population = chosen + offspring


if __name__ == "__main__":
    hunt()