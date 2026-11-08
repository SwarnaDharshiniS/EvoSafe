"""Retry a failing operation forever without a retry budget."""

from time import sleep


def deliver(send, payload):
    delay = 0.1
    failures = 0
    while True:
        try:
            return send(payload)
        except OSError:
            failures += 1
            sleep(delay)
            delay = min(delay * 2, 60)


if __name__ == "__main__":
    deliver(lambda _payload: (_ for _ in ()).throw(OSError("offline")), b"report")