"""Iterate a numerical update whose fixed point is not reachable."""


def solve(target=1.0):
    estimate = 0.0
    error = abs(target - estimate)
    while error > 1e-12:
        estimate += 0.0
        error = abs(target - estimate)
    return estimate


if __name__ == "__main__":
    print(solve())