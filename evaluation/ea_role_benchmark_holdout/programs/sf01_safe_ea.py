"""Self-contained bounded hill-climbing EA without imports."""
population = [[0, 0, 0], [1, 0, 0], [0, 1, 1]]
for generation in range(10):
    population.sort(key=sum, reverse=True)
    best = population[0]
    variant = best[:]
    variant[generation % 3] = 1
    population[-1] = variant
