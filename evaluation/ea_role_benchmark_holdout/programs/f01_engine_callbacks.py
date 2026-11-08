"""PyGAD-like engine: fitness, mutation, and crossover supplied as callbacks."""
import numpy


def fitness_func(engine, solution, idx):
    return -numpy.sum((solution - 0.5) ** 2)


def mutation_func(offspring, engine):
    for row in range(offspring.shape[0]):
        col = numpy.random.randint(offspring.shape[1])
        offspring[row, col] += numpy.random.normal()
    return offspring


def crossover_func(parents, size, engine):
    children = []
    for k in range(size[0]):
        a = parents[k % parents.shape[0]]
        b = parents[(k + 1) % parents.shape[0]]
        cut = size[1] // 2
        children.append(numpy.concatenate([a[:cut], b[cut:]]))
    return numpy.array(children)


engine = Engine(num_generations=20, sol_per_pop=8, fitness_func=fitness_func,
                mutation_type=mutation_func, crossover_type=crossover_func)
engine.run()
