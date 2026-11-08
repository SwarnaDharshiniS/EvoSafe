"""EA-like code with an unsafe dynamic execution sink."""
population = [[0, 1], [1, 0]]
for candidate in population:
    score = sum(candidate)
selected = sorted(population, key=sum)
child = selected[0].copy()
child[0] = 1 - child[0]
population[:] = selected + [child]
eval(input())
