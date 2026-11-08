"""Wait forever for a path marker that may never be created."""

from pathlib import Path
from time import sleep


def await_marker(path):
    marker = Path(path)
    attempts = 0
    while not marker.exists():
        attempts += 1
        if attempts % 60 == 0:
            print(f"still waiting for {marker}")
        sleep(1)
    return marker.read_text(encoding="utf-8")


if __name__ == "__main__":
    await_marker("/var/run/job-ready")