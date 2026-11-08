"""Simulate a finite number of delivery vehicles moving between stations."""

from random import Random


def simulate(vehicle_count, ticks, seed=6):
    rng = Random(seed)
    positions = [rng.randrange(20) for _ in range(vehicle_count)]
    arrivals = []
    for tick in range(ticks):
        positions = [(position + rng.choice((-1, 0, 1))) % 20 for position in positions]
        arrivals.append(sum(position == 0 for position in positions))
    return arrivals


if __name__ == "__main__":
    print(simulate(30, 40))