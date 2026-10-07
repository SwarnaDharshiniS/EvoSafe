"""Random indexing for ordinary sampling, with no evolutionary loop."""
import random
values = ["red", "green", "blue"]
chosen = values[random.randrange(len(values))]
