"""Direct GA: while-loop until convergence, list-of-lists genomes."""
import random

population = [[random.randint(0, 1) for _ in range(6)] for _ in range(8)]
best = 0
while best < 6:
    scored = [(sum(ind), ind) for ind in population]
    scored.sort(reverse=True)
    best = scored[0][0]
    parents = [ind for _, ind in scored[:4]]
    children = []
    for i in range(0, len(parents) - 1, 2):
        cut = random.randrange(1, 6)
        children.append(parents[i][:cut] + parents[i + 1][cut:])
    for child in children:
        pos = random.randrange(6)
        child[pos] = 1 - child[pos]
    population = parents + children
