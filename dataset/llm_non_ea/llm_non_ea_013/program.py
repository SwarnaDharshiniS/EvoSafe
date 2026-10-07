"""Cluster geographic observations with a fixed number of centroid updates."""

from math import dist


def assign(points, centers):
    return [min(range(len(centers)), key=lambda index: dist(point, centers[index])) for point in points]


def cluster(points, centers, rounds=12):
    centers = [point.copy() for point in centers]
    for _ in range(rounds):
        groups = [[] for _ in centers]
        for point, label in zip(points, assign(points, centers)):
            groups[label].append(point)
        for index, group in enumerate(groups):
            if group:
                centers[index] = [sum(row[col] for row in group) / len(group) for col in range(len(group[0]))]
    return centers


if __name__ == "__main__":
    print(cluster([[0.0, 1.0], [2.0, 3.0]], [[0.0, 0.0], [3.0, 3.0]]))