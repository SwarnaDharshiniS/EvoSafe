"""Direct GA with dict individuals and uniform crossover, no mutation."""
import random

pop = [{"genes": [random.random() for _ in range(4)]} for _ in range(10)]
for gen in range(30):
    for ind in pop:
        ind["fitness"] = -sum((g - 0.5) ** 2 for g in ind["genes"])
    pop.sort(key=lambda ind: ind["fitness"], reverse=True)
    survivors = pop[:5]
    newborn = []
    for ind in survivors:
        mate = random.choice(survivors)
        genes = [a if random.random() < 0.5 else b for a, b in zip(ind["genes"], mate["genes"])]
        newborn.append({"genes": genes})
    pop = survivors + newborn
