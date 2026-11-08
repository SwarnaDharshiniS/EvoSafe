"""Start subprocesses without waiting for or limiting their lifetime."""

import subprocess


def start_workers(commands):
    children = []
    for command in commands:
        children.append(subprocess.Popen(command, shell=True))
    return children


if __name__ == "__main__":
    start_workers([["echo", "worker"]] * 100_000)