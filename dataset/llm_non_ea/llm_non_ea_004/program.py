"""Train a linear regression model with mini-batch gradient updates."""

from random import Random


def predict(weights, row):
    return sum(weight * value for weight, value in zip(weights, row))


def fit(features, targets, epochs=40, batch_size=8):
    rng = Random(17)
    weights = [0.0] * len(features[0])
    for _ in range(epochs):
        order = list(range(len(features)))
        rng.shuffle(order)
        for start in range(0, len(order), batch_size):
            batch = order[start : start + batch_size]
            gradient = [0.0] * len(weights)
            for item in batch:
                error = predict(weights, features[item]) - targets[item]
                for column, value in enumerate(features[item]):
                    gradient[column] += error * value
            weights = [w - 0.01 * g / len(batch) for w, g in zip(weights, gradient)]
    return weights


if __name__ == "__main__":
    print(fit([[1.0, 0.0], [0.0, 1.0]], [2.0, 3.0]))