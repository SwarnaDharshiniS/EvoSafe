"""Random survey sampling with no evolutionary process."""
import random

respondents = list(range(1000))
sample = random.sample(respondents, 50)
for person in sample:
    print(person)
