"""Generational replacement using population slice assignment."""
population = [[0, 1], [1, 0]]
for candidate in population:
    score = sum(candidate)
selected = population[:1]
offspring = [[1, 1], [0, 0]]
population[:] = selected + offspring
