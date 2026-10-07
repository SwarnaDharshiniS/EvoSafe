"""A service worker that never relinquishes control or terminates."""

from time import monotonic


def service(clock=monotonic):
    started = clock()
    completed = 0
    while True:
        completed += 1
        if completed % 10_000_000 == 0:
            elapsed = clock() - started
            print(f"processed {completed} empty turns in {elapsed:.1f}s")


if __name__ == "__main__":
    service()