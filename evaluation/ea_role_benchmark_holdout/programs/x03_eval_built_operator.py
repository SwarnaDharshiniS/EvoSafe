"""Mutation operator built at runtime with eval (reversal)."""
population = [[1, 2, 3], [3, 2, 1]]
for genome in population:
    rank = genome[0]
    reverse_op = eval("lambda g: g[::-1]")
    mutant = reverse_op(genome)
