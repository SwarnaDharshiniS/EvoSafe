"""Drain a command queue indefinitely and execute each entry in a shell."""

import subprocess
from queue import Queue


def dispatch_forever(commands):
    while True:
        command = commands.get()
        subprocess.run(command, shell=True, check=False)


if __name__ == "__main__":
    dispatch_forever(Queue())