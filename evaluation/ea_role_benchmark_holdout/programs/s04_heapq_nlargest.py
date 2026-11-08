"""Top-k selection with heapq.nlargest."""
import heapq

population = [[3, 1], [2, 2], [0, 5]]
for cand in population:
    merit = cand[0] * cand[1]
best_two = heapq.nlargest(2, population, key=lambda c: c[0] * c[1])
