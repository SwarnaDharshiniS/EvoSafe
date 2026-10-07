"""Run a fixed number of gradient steps for a small numerical objective."""


def objective(values):
    return sum((value - target) ** 2 for value, target in zip(values, (1.0, -2.0)))


def optimize(initial, rate=0.05, steps=120):
    current = initial.copy()
    for _ in range(steps):
        gradient = [2 * (value - target) for value, target in zip(current, (1.0, -2.0))]
        current = [value - rate * delta for value, delta in zip(current, gradient)]
    return current


if __name__ == "__main__":
    print(optimize([8.0, 5.0]))