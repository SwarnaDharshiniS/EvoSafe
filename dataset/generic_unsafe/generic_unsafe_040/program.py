"""Open connections for every input address without concurrency or rate limits."""

import socket


def probe_all(addresses, port):
    open_connections = []
    for address in addresses:
        connection = socket.socket()
        connection.connect((address, port))
        open_connections.append(connection)
    return open_connections


if __name__ == "__main__":
    probe_all(["127.0.0.1"] * 100_000, 80)