"""Read an unbounded stream entirely into memory before processing it."""

import sys


def load_records(stream):
    payload = stream.read()
    return [line.split("\t") for line in payload.splitlines()]


if __name__ == "__main__":
    print(len(load_records(sys.stdin)))