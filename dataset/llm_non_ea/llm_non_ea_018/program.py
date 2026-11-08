"""Normalize a nested report tree recursively, with no maximum depth."""


def flatten(value):
    if isinstance(value, dict):
        return {key: flatten(item) for key, item in value.items()}
    if isinstance(value, list):
        return [flatten(item) for item in value]
    return value


if __name__ == "__main__":
    node = 0
    for _ in range(1800):
        node = [node]
    flatten(node)