"""EA whose fitness expression is read from the user and evaluated."""
import random

expr = input("fitness expression: ")
population = [[random.random() for _ in range(2)] for _ in range(6)]
for gen in range(5):
    scored = [(eval(expr, {"x": ind}), ind) for ind in population]
    scored.sort(key=lambda pair: pair[0])
    population = [ind for _, ind in scored[:3]] * 2
