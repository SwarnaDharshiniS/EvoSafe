"""Find a zero of a scalar function with Newton's method."""


def solve(function, derivative, initial, tolerance=1e-8, iterations=80):
    value = initial
    for _ in range(iterations):
        slope = derivative(value)
        if abs(slope) < 1e-12:
            return None
        updated = value - function(value) / slope
        if abs(updated - value) < tolerance:
            return updated
        value = updated
    return value


if __name__ == "__main__":
    print(solve(lambda x: x * x - 3, lambda x: 2 * x, 2.0))