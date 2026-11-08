"""Wait for a sensor state indefinitely while backing off between polls."""

from time import sleep


def await_ready(read_sensor):
    delay = 0.2
    polls = 0
    while not read_sensor():
        sleep(delay)
        polls += 1
        delay = min(delay * 1.5, 20)
    return polls


if __name__ == "__main__":
    await_ready(lambda: False)