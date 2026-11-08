"""PyGAD-like engine configured only with parameters; no operator code in source."""
engine = Engine(num_generations=50, sol_per_pop=20, num_genes=4, mutation_percent_genes=10)
engine.run()
print(engine.best_solution())
