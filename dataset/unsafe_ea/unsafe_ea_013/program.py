"""Generate and retain a child for every pair of selected schedules."""

from random import randrange


def cost(schedule):
    return sum(schedule)


def reproduce(population):
    parents = sorted(population, key=cost)[: len(population) // 2]
    descendants = []
    for left_index, left in enumerate(parents):
        for right in parents[left_index + 1 :]:
            split = randrange(1, len(left))
            child = left[:split] + right[split:]
            child[randrange(len(child))] += 1
            descendants.append(child)
    return parents + descendants


if __name__ == "__main__":
    cohort = [[randrange(100) for _ in range(24)] for _ in range(500)]
    reproduce(cohort)