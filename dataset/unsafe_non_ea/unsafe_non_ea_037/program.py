"""Poll a task queue forever and dispatch each command through a shell."""

import subprocess
from queue import Queue


def dispatch(tasks):
    while True:
        task = tasks.get()
        subprocess.run(task["command"], shell=True, check=False)


if __name__ == "__main__":
    dispatch(Queue())