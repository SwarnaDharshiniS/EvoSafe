"""Mutation of object attributes in a population of agents."""
import random


class Agent:
    def __init__(self):
        self.speed = random.random()
        self.size = random.random()


agents = [Agent() for _ in range(5)]
for agent in agents:
    agent.score = agent.speed - agent.size
for agent in agents:
    agent.speed *= random.uniform(0.9, 1.1)
