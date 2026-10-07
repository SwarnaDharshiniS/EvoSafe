"""Population reached through several alias levels, then ranked and truncated."""
import random

initial = [[random.random() for _ in range(3)] for _ in range(6)]
pool = initial
current = pool
for individual in current:
    cost = sum(x * x for x in individual)
alias_of_alias = current
alias_of_alias.sort(key=lambda v: sum(x * x for x in v))
elite = alias_of_alias[:2]
