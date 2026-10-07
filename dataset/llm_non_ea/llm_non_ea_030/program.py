"""Collect local UDP diagnostics messages forever and acknowledge each sender."""

import socket


def serve(port=9040):
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.bind(("127.0.0.1", port))
    while True:
        _message, address = listener.recvfrom(8192)
        listener.sendto(b"received", address)


if __name__ == "__main__":
    serve()