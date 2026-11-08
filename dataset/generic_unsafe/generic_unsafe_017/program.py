"""Replicate a nested row template into an excessive in-memory table."""


def make_table(columns=256):
    template = [None] * columns
    return [template.copy() for _ in range(20_000_000)]


if __name__ == "__main__":
    make_table()