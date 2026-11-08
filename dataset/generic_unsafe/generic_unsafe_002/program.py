"""Drain a queue until a sentinel arrives, with no timeout or shutdown path."""

from queue import Queue


def consume(inbox):
    handled = 0
    while True:
        job = inbox.get()
        if job is None:
            return handled
        job()
        handled += 1


if __name__ == "__main__":
    consume(Queue())