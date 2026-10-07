"""Two-parent crossover implemented as a method on a genome class."""


class Genome:
    def __init__(self, genes):
        self.genes = genes

    def cross(self, other):
        half = len(self.genes) // 2
        return Genome(self.genes[:half] + other.genes[half:])


population = [Genome([0, 1, 0, 1]), Genome([1, 1, 1, 0])]
for g in population:
    g.score = sum(g.genes)
child = population[0].cross(population[1])
