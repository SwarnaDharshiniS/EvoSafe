"""Retry delivery forever when the remote service remains unavailable."""

from time import sleep


def submit(send, record):
    wait = 0.1
    while True:
        try:
            return send(record)
        except OSError:
            sleep(wait)
            wait = min(wait * 2, 45)


if __name__ == "__main__":
    submit(lambda _record: (_ for _ in ()).throw(OSError("offline")), {"id": 7})