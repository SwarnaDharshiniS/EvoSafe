"""Use a class to evolve model coefficients with a bounded termination rule."""

from random import gauss, random


class CoefficientSearch:
    def __init__(self, dimensions=5):
        self.population = [[random() for _ in range(dimensions)] for _ in range(24)]

    def loss(self, values):
        return sum((value - 0.75) ** 2 for value in values)

    def run(self, generations=20):
        for _ in range(generations):
            parents = sorted(self.population, key=self.loss)[:6]
            children = []
            for parent in parents:
                child = parent.copy()
                child[0] += gauss(0, 0.1)
                children.append(child)
            self.population = parents + children
        return min(self.population, key=self.loss)


if __name__ == "__main__":
    print(CoefficientSearch().run())