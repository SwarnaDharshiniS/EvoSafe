"""Elitist replacement by reassigning the population variable."""
population = [[0, 1], [1, 1], [1, 0]]
for ind in population:
    value = sum(ind)
elite = sorted(population, key=sum)[-1:]
children = [[1, 0], [0, 0]]
population = elite + children
