"""Fully materialize a combinatorial set of candidate configurations."""

from itertools import product


def all_settings(options):
    dimensions = [options] * 12
    return list(product(*dimensions))


if __name__ == "__main__":
    all_settings(range(40))