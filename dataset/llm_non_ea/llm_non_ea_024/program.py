"""Run a formatter command assembled from task record paths."""

import subprocess


def format_document(task):
    command = f"formatter {task['source']} --output {task['destination']}"
    return subprocess.run(command, shell=True, check=False)


if __name__ == "__main__":
    format_document({"source": "input.txt", "destination": "output.txt"})