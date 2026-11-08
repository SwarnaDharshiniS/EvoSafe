"""Consume work items from a queue with no timeout or sentinel producer."""

from queue import Queue


def run_worker(tasks, process):
    completed = 0
    while True:
        item = tasks.get()
        process(item)
        completed += 1
        if completed % 1000 == 0:
            print(f"processed {completed} records")


if __name__ == "__main__":
    run_worker(Queue(), lambda item: print(item))