"""Poll an automation queue forever and launch an external cleanup command."""

import subprocess
from queue import Queue


def handle_jobs(jobs):
    while True:
        job = jobs.get()
        subprocess.Popen(["cleanup-worker", job["path"]])


if __name__ == "__main__":
    handle_jobs(Queue())