"""Run a helper-driven genetic optimizer for a small ordering problem."""

from random import randrange


def distance(order):
    return sum(abs(order[i] - order[i - 1]) for i in range(1, len(order)))


def select_routes(routes):
    return sorted(routes, key=distance)[:8]


def recombine(first, second):
    midpoint = len(first) // 2
    child = first[:midpoint] + [item for item in second if item not in first[:midpoint]]
    return child[:len(first)]


def run_generations(pool, rounds):
    for _ in range(rounds):
        parents = select_routes(pool)
        children = []
        for index, parent in enumerate(parents):
            child = recombine(parent, parents[(index + 1) % len(parents)])
            child[randrange(len(child))] = randrange(len(child))
            children.append(child)
        pool = parents + children
    return min(pool, key=distance)


if __name__ == "__main__":
    run_generations([list(range(10)) for _ in range(24)], 18)