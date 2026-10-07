"""Expand each node into many children for a fixed number of levels."""


def expand(levels, width):
    if levels == 0:
        return {"leaf": True}
    return [expand(levels - 1, width) for _ in range(width)]


if __name__ == "__main__":
    expand(12, 8)