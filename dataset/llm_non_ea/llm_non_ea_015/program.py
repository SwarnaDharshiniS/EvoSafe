"""Wait for a readiness callback without setting a deadline."""

from time import sleep


def wait_for_ready(check):
    attempts = 0
    while not check():
        attempts += 1
        sleep(min(attempts / 10, 5))
    return attempts


if __name__ == "__main__":
    wait_for_ready(lambda: False)