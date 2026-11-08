"""Uniform crossover between two population members."""
import random

population = [[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 0, 0]]
for genome in population:
    fit = sum(genome)
mother, father = population[0], population[1]
child = [m if random.random() < 0.5 else f for m, f in zip(mother, father)]
