"""Materialize a report for a range far larger than a practical request."""


def build_index():
    return [position * 3 for position in range(100_000_000)]


if __name__ == "__main__":
    print(len(build_index()))