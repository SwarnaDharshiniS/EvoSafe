"""Ordinary matrix writes and list construction."""
rows = [[0] * 4 for _ in range(4)]
for row in range(4):
    for col in range(4):
        rows[row][col] = row + col
