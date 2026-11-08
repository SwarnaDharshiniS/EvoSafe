"""Add a fresh immigrant cohort each epoch while keeping the prior population."""

from random import randrange


def objective(candidate):
    return sum(abs(value - 12) for value in candidate)


def introduce(population, cohort):
    ranked = sorted(population, key=objective)
    survivors = ranked[:8]
    newcomers = [[randrange(100) for _ in range(10)] for _ in range(cohort)]
    return population + survivors + newcomers


def run():
    pool = [[randrange(100) for _ in range(10)] for _ in range(20)]
    generation = 0
    while generation < 75:
        pool = introduce(pool, generation * 150)
        generation += 1
    return min(pool, key=objective)


if __name__ == "__main__":
    run()