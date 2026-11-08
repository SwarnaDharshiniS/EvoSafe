"""PyGAD-like engine with a custom parent-selection callback."""
import numpy


def fitness_func(engine, solution, idx):
    return float(numpy.sum(solution))


def parent_selection_func(fitness, num_parents, engine):
    order = numpy.argsort(fitness)[::-1][:num_parents]
    return engine.population[order].copy(), order


engine = Engine(num_generations=5, fitness_func=fitness_func,
                parent_selection_type=parent_selection_func)
engine.run()
