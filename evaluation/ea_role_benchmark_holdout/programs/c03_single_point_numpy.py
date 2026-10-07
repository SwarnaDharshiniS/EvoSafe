"""Single-point crossover on NumPy rows."""
import numpy as np

pop = np.random.rand(6, 5)
fitness = pop.sum(axis=1)
p1, p2 = pop[0], pop[1]
cut = 2
child = np.concatenate([p1[:cut], p2[cut:]])
