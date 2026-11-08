"""Serve a local diagnostics endpoint indefinitely without a shutdown path."""

import socket


def serve(port=9011):
    listener = socket.socket()
    listener.bind(("127.0.0.1", port))
    listener.listen()
    while True:
        client, _address = listener.accept()
        client.sendall(b"diagnostics ready\n")
        client.close()


if __name__ == "__main__":
    serve()