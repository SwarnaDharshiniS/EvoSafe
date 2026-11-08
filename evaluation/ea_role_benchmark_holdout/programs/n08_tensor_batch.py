"""Batched tensor update for a single linear layer."""
import numpy as np

batch = np.random.rand(16, 8)
weights = np.random.rand(8, 4)
for step in range(10):
    logits = batch @ weights
    weights += 0.01 * batch.T @ (logits - logits.mean())
