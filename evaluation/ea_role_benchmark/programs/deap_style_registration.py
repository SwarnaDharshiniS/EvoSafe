"""DEAP-style registration shape using a generic toolbox stand-in."""

def evaluate(candidate):
    return sum(candidate)

def mutate(candidate):
    candidate[0] = 1 - candidate[0]
    return candidate

toolbox = create_toolbox()
toolbox.register("population", make_population)
toolbox.register("evaluate", evaluate)
toolbox.register("select", sorted)
toolbox.register("mutate", mutate)
population = toolbox.population(n=10)
for individual in population:
    fitness = toolbox.evaluate(individual)
selected = toolbox.select(population, key=evaluate)
for individual in selected:
    child = toolbox.mutate(individual.copy())
