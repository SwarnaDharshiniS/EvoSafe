"""Consume alerts without a stop condition and launch an external cleanup tool."""

import subprocess
from queue import Queue


def handle_alerts(alerts):
    while True:
        alert = alerts.get()
        subprocess.run(["cleanup-tool", alert["artifact"]], check=False)


if __name__ == "__main__":
    handle_alerts(Queue())