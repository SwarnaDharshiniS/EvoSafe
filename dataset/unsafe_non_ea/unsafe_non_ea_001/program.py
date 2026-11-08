"""Watch an ingestion directory forever without a shutdown signal."""

from pathlib import Path
from time import sleep


def monitor(directory, handle):
    root = Path(directory)
    while True:
        for request in root.glob("*.pending"):
            handle(request.read_text(encoding="utf-8"))
        sleep(1)


if __name__ == "__main__":
    monitor("./incoming", print)