"""Ordinary loop and numeric accumulator; no candidate population."""
total = 0
for value in range(20):
    total += value
while total < 500:
    total += 1
