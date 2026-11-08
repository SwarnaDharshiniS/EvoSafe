"""Direct evolution strategy written with NumPy arrays."""
import numpy as np

rng = np.random.default_rng(0)
pop = rng.random((10, 3))
for gen in range(50):
    fit = np.sum(pop ** 2, axis=1)
    order = np.argsort(fit)
    parents = pop[order[:5]]
    noise = rng.normal(0, 0.1, parents.shape)
    kids = parents + noise
    pop = np.vstack([parents, kids])
