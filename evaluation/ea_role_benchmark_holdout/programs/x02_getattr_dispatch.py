"""Mutation operator chosen dynamically via getattr."""
import random


class Operators:
    def bitflip(self, genome):
        genome[0] = 1 - genome[0]
        return genome


name = random.choice(["bitflip"])
operator = getattr(Operators(), name)
population = [[0, 1], [1, 0]]
for genome in population:
    score = sum(genome)
    operator(genome)
