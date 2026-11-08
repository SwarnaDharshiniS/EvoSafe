"""Load a serialized report and recursively summarize nested records."""

import pickle
import sys


def summarize(value):
    if isinstance(value, dict):
        return sum(summarize(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return sum(summarize(item) for item in value)
    return 1


if __name__ == "__main__":
    print(summarize(pickle.loads(sys.stdin.buffer.read())))