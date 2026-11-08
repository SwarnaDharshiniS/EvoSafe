"""Mutation reached through a two-level helper chain."""
import random


def flip(bits, i):
    bits[i] = 1 - bits[i]
    return bits


def mutate(genome):
    child = list(genome)
    return flip(child, random.randrange(len(child)))


population = [[0, 1, 0], [1, 1, 0]]
for genome in population:
    fitness = sum(genome)
    offspring = mutate(genome)
