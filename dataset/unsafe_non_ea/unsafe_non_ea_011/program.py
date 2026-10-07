"""Normalize nested document data recursively with no depth budget."""


def normalize(value):
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return str(value)


if __name__ == "__main__":
    document = "leaf"
    for _ in range(2500):
        document = {"next": document}
    normalize(document)