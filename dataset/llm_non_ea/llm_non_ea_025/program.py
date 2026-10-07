"""Launch a separate formatter process for each document in a batch."""

from subprocess import Popen


def schedule(documents, formatter):
    return [Popen([formatter, document]) for document in documents]


if __name__ == "__main__":
    schedule([f"doc-{index}" for index in range(2500)], "format-worker")