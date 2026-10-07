"""EA roles implemented in small local helper functions."""

def score(candidate):
    return len(candidate)

def select(pool):
    return sorted(pool, key=len)[:2]

def mutate(candidate):
    candidate[0] = 1 - candidate[0]
    return candidate

population = [[0, 1], [1, 0], [1, 1]]
for candidate in population:
    fitness_value = score(candidate)
selected = select(population)
for candidate in selected:
    child = mutate(candidate.copy())
