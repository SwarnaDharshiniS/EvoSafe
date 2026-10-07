"""Candidate modified in place through two alias levels."""
population = [[0.0, 1.0], [2.0, 3.0]]
for member in population:
    score = member[0] + member[1]
    view = member
    same = view
    same[1] = same[1] * 0.9
