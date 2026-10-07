"""Threshold filtering of candidates by fitness."""
population = [[0.2, 0.5], [0.9, 0.1], [0.4, 0.4]]
for p in population:
    total = sum(p)
viable = [p for p in population if sum(p) > 0.6]
