"""Recursively convert arbitrarily deep nested input without a depth limit."""


def normalize(node):
    if isinstance(node, dict):
        return {key: normalize(value) for key, value in node.items()}
    if isinstance(node, list):
        return [normalize(value) for value in node]
    return str(node)


if __name__ == "__main__":
    document = "leaf"
    for _ in range(2_000):
        document = [document]
    normalize(document)