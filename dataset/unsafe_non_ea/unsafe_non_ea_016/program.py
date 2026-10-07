"""Read an entire input stream and then allocate parsed copies of every row."""

import sys


def load_table(stream):
    raw_text = stream.read()
    return [line.split(",") for line in raw_text.splitlines()]


if __name__ == "__main__":
    print(len(load_table(sys.stdin)))