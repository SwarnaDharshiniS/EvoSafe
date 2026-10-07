"""Build an in-memory mapping for every integer in an enormous range."""


def cache_labels():
    return {number: f"label-{number}" for number in range(100_000_000)}


if __name__ == "__main__":
    cache_labels()