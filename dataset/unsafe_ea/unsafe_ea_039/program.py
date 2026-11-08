"""Read candidate records forever, breed them, and append results to disk."""

import json
from random import randrange


def fitness(candidate):
    return sum(candidate)


def run(input_path, output_path):
    population = []
    with open(input_path, encoding="utf-8") as incoming, open(output_path, "a", encoding="utf-8") as outgoing:
        while True:
            line = incoming.readline()
            if not line:
                break
            population.append(json.loads(line))
            if len(population) >= 4:
                ranked = sorted(population, key=fitness, reverse=True)
                parents = ranked[:2]
                child = parents[0][:1] + parents[1][1:]
                child[randrange(len(child))] += 1
                outgoing.write(json.dumps(child) + "\n")
                population.extend([child] * 1000)


if __name__ == "__main__":
    run("candidates.jsonl", "offspring.jsonl")