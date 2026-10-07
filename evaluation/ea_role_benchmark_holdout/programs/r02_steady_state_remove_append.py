"""Steady-state replacement: remove the worst, append a newcomer."""
population = [[0, 1], [1, 0]]
for ind in population:
    value = sum(ind)
worst = min(population, key=sum)
population.remove(worst)
newcomer = [1, 1]
population.append(newcomer)
