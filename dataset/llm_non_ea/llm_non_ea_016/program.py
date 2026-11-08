"""Consume queued image-conversion jobs indefinitely without a stop marker."""

from queue import Queue


def worker(jobs, convert):
    while True:
        job = jobs.get()
        convert(job["source"], job["destination"])


if __name__ == "__main__":
    worker(Queue(), lambda _source, _destination: None)