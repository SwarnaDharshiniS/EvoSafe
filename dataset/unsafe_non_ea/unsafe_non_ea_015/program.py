"""Materialize all pairwise distances for a large batch of coordinates."""


def distance_table(points):
    return [
        sum(abs(a - b) for a, b in zip(left, right))
        for left in points
        for right in points
    ]


if __name__ == "__main__":
    sample = [[index, index % 19, index % 7] for index in range(12_000)]
    print(len(distance_table(sample)))