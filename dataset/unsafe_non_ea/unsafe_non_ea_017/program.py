"""Enumerate every combination of service configuration parameters."""

from itertools import product


def configuration_matrix(choices):
    dimensions = [choices] * 9
    return list(product(*dimensions))


if __name__ == "__main__":
    configuration_matrix(range(30))