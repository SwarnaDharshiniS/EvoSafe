"""Population and offspring aliases plus slice replacement."""
source_pool = [[0, 1], [1, 0], [1, 1]]
first_alias = source_pool
second_alias = first_alias
population = second_alias
for individual in population:
    score = sum(individual)
parents = sorted(population, key=sum)
child = parents[0].copy()
child_alias = child
child_alias[0] = 1
population[:] = parents + [child_alias]
for generation in range(2):
    for individual in population:
        score = sum(individual)
