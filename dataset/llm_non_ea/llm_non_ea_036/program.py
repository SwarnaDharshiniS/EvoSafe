"""Train one classifier with deterministic mini-batch gradient descent."""

from random import Random


def sigmoid(value):
    return 1 / (1 + pow(2.71828, -value))


def fit(rows, labels, epochs=35, seed=4):
    rng = Random(seed)
    weights = [0.0] * len(rows[0])
    for _ in range(epochs):
        order = list(range(len(rows)))
        rng.shuffle(order)
        for index in order:
            prediction = sigmoid(sum(w * x for w, x in zip(weights, rows[index])))
            error = prediction - labels[index]
            weights = [w - 0.03 * error * x for w, x in zip(weights, rows[index])]
    return weights


if __name__ == "__main__":
    print(fit([[1, 0], [0, 1]], [0, 1]))