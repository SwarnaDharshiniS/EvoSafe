"""Remove a candidate-named file while recording each fitness evaluation."""

import os
from random import randrange


def evaluate(candidate, log_root):
    score = sum(candidate)
    log_file = os.path.join(log_root, "".join(map(str, candidate)) + ".txt")
    with open(log_file, "w", encoding="utf-8") as handle:
        handle.write(f"fitness={score}\n")
    return score


def select_and_clean(population, log_root):
    ranked = sorted(population, key=lambda item: evaluate(item, log_root), reverse=True)
    survivors = ranked[:10]
    for discarded in ranked[10:]:
        os.remove(os.path.join(log_root, "".join(map(str, discarded)) + ".txt"))
    children = [candidate.copy() for candidate in survivors]
    for child in children:
        child[0] += 1
    return survivors + children


if __name__ == "__main__":
    select_and_clean([[randrange(10) for _ in range(8)] for _ in range(50)], "/var/log/ea")