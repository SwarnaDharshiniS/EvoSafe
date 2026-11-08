"""Use aliases and an indirect crossover helper in a small bounded optimizer."""

from random import randrange as pick_int


def energy(chromosome):
    return sum(value * value for value in chromosome)


def splice(first, second):
    boundary = len(first) // 2
    return first[:boundary] + second[boundary:]


def jitter(chromosome):
    altered = chromosome.copy()
    altered[pick_int(len(altered))] += pick_int(3) - 1
    return altered


def run():
    pool = [[pick_int(12) for _ in range(10)] for _ in range(30)]
    for _ in range(14):
        selected = sorted(pool, key=energy)[:6]
        pool = selected + [jitter(splice(selected[i], selected[-i - 1])) for i in range(6)]
    return min(pool, key=energy)


if __name__ == "__main__":
    run()