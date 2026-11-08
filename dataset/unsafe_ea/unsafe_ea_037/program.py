"""Accept unbounded candidate submissions and feed them into a live EA."""

import pickle
import socket
from random import random


def fitness(candidate):
    return sum(candidate)


def evolve_from_stream(port=9010):
    population = [[0, 0, 0] for _ in range(20)]
    listener = socket.socket()
    listener.bind(("127.0.0.1", port))
    listener.listen()
    while True:
        client, _address = listener.accept()
        incoming = pickle.loads(client.recv(1_000_000))
        ranked = sorted(population + [incoming], key=fitness, reverse=True)
        parents = ranked[:10]
        offspring = [parent.copy() for parent in parents]
        for child in offspring:
            child[0] += random()
        population = parents + offspring
        client.close()


if __name__ == "__main__":
    evolve_from_stream()