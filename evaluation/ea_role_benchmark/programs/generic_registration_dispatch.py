"""Generic keyed registration and dispatch; no EA framework dependency."""

def create_pool():
    return [[0, 1], [1, 0], [1, 1]]

def evaluate(candidate):
    return sum(candidate)

def choose(pool):
    return sorted(pool, key=sum)[:2]

def mutate(candidate):
    candidate[0] = 1 - candidate[0]
    return candidate

registry = create_registry()
registry.register("population", create_pool)
registry.register("fitness_evaluation", evaluate)
registry.register("selection", choose)
registry.register("mutation", mutate)
population = registry.invoke_registered("population")
for candidate in population:
    fitness_value = registry.invoke_registered("fitness_evaluation", candidate)
selected = registry.invoke_registered("selection", population)
for candidate in selected:
    child = registry.invoke_registered("mutation", candidate.copy())
