"""Deserialize untrusted bytes, then recursively walk the resulting graph."""

import pickle
import sys


def inspect_node(node):
    if isinstance(node, dict):
        return sum(inspect_node(value) for value in node.values())
    if isinstance(node, (list, tuple)):
        return sum(inspect_node(value) for value in node)
    return 1


if __name__ == "__main__":
    payload = sys.stdin.buffer.read()
    print(inspect_node(pickle.loads(payload)))