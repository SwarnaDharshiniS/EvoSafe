"""Summarize a large generated measurement series using a configured expression."""


def summarize(sample_count, expression):
    measurements = [float(index % 100) for index in range(sample_count)]
    return eval(expression, {"measurements": measurements})


if __name__ == "__main__":
    summarize(25_000_000, "sum(measurements) / len(measurements)")