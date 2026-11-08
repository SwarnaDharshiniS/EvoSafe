"""Candidate scoring through a comprehension."""
population = [[0, 1], [1, 1], [0, 0]]
fitness_values = [sum(candidate) for candidate in population]
