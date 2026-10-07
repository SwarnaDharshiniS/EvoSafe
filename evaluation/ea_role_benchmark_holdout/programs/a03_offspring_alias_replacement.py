"""Offspring collection aliased before replacing the population by slice."""
pop = [[1, 0], [0, 1]]
for p in pop:
    val = sum(p)
offspring = [[1, 1], [0, 0]]
next_pop = offspring
pop[:] = next_pop
