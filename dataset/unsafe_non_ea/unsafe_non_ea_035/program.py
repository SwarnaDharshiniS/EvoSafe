"""Open and retain one loopback socket for every configured service address."""

import socket


def connect_all(addresses):
    connections = []
    for address in addresses:
        connection = socket.create_connection((address, 9020))
        connections.append(connection)
    return connections


if __name__ == "__main__":
    connect_all(["127.0.0.1"] * 1000)