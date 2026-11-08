"""Build a large in-memory lookup table from a telemetry sequence."""


def make_lookup(count):
    return {index: f"event-{index % 97}" for index in range(count)}


if __name__ == "__main__":
    print(len(make_lookup(30_000_000)))