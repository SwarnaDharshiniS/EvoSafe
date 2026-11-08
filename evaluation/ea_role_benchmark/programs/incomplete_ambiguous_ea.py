"""Partial EA evidence: candidate scoring but no visible reproduction roles."""
population = [[1, 0], [0, 1]]
for candidate in population:
    value = objective(candidate)
