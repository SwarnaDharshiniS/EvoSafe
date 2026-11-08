"""Serve a local objective endpoint while updating a population forever."""

import socket
from random import randrange


def score(candidate):
    return sum(candidate)


def serve(population, port=9032):
    listener = socket.socket()
    listener.bind(("127.0.0.1", port))
    listener.listen()
    while True:
        client, _address = listener.accept()
        parents = sorted(population, key=score, reverse=True)[:5]
        child = parents[0].copy()
        child[randrange(len(child))] += 1
        population = parents + [child]
        client.sendall(str(score(child)).encode("ascii"))
        client.close()


if __name__ == "__main__":
    serve([[randrange(10) for _ in range(8)] for _ in range(24)])