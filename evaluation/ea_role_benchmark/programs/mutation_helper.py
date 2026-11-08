"""Candidate mutation through a helper."""

def mutate(candidate):
    changed = candidate.copy()
    changed[0] = 1 - changed[0]
    return changed

population = [[0, 1], [1, 0]]
for individual in population:
    score = sum(individual)
    child = mutate(individual)
