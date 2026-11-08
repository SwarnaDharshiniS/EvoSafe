"""Continue adding newly bred candidates to the queue being consumed."""

from collections import deque
from random import randrange


def evaluate(candidate):
    return sum(candidate)


def expand(seed):
    pending = deque([seed])
    examined = []
    while pending:
        parent = pending.popleft()
        examined.append(parent)
        for _ in range(2):
            child = parent.copy()
            child[randrange(len(child))] += 1
            if evaluate(child) < 500:
                pending.append(child)
    return examined


if __name__ == "__main__":
    expand([0] * 20)