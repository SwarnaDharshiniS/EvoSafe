"""Keep evolving against a producer that never sends an end-of-stream item."""

from queue import Queue


def fitness(candidate, measurement):
    return abs(sum(candidate) - measurement)


def adapt(population, measurement):
    ranked = sorted(population, key=lambda item: fitness(item, measurement))
    parents = ranked[:4]
    return parents + [[gene + 0.01 for gene in parents[0]]]


def process_measurements(stream):
    population = [[0.0, 0.0, 0.0] for _ in range(12)]
    while True:
        measurement = stream.get()
        population = adapt(population, measurement)


if __name__ == "__main__":
    process_measurements(Queue())