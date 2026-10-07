"""Single-model stochastic gradient descent on a tiny dataset."""
import random

weights = [random.random() for _ in range(3)]
data = [([1.0, 2.0, 3.0], 1.0), ([0.5, 0.1, 0.2], 0.0)]
for epoch in range(100):
    for features, target in data:
        prediction = sum(w * x for w, x in zip(weights, features))
        error = prediction - target
        for i in range(len(weights)):
            weights[i] -= 0.01 * error * features[i]
