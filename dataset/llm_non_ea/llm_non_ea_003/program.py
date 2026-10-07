"""Fit one numeric parameter vector with ordinary gradient descent."""


def loss(weights, observations):
    return sum((sum(w * x for w, x in zip(weights, row[:-1])) - row[-1]) ** 2 for row in observations)


def train(observations, dimensions, step_size=0.001, epochs=150):
    weights = [0.0] * dimensions
    for _ in range(epochs):
        gradients = [0.0] * dimensions
        for row in observations:
            error = sum(w * x for w, x in zip(weights, row[:-1])) - row[-1]
            for index, value in enumerate(row[:-1]):
                gradients[index] += 2 * error * value
        weights = [w - step_size * g / len(observations) for w, g in zip(weights, gradients)]
    return weights


if __name__ == "__main__":
    print(train([[1.0, 2.0], [2.0, 4.0]], 1))