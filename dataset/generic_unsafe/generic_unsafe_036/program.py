"""Accept connections indefinitely and recurse for each client session."""

import socket


def serve_connection(client):
    request = client.recv(4096)
    if request:
        client.sendall(b"received\n")
        serve_connection(client)
    client.close()


def serve(port=9000):
    listener = socket.socket()
    listener.bind(("127.0.0.1", port))
    listener.listen()
    while True:
        client, _address = listener.accept()
        serve_connection(client)


if __name__ == "__main__":
    serve()