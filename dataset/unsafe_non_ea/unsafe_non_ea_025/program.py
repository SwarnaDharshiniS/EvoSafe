"""Start one external worker for every queued document and never reap it."""

from subprocess import Popen


def start_workers(documents, executable):
    children = []
    for document in documents:
        children.append(Popen([executable, document]))
    return children


if __name__ == "__main__":
    start_workers([f"record-{index}" for index in range(5000)], "document-worker")