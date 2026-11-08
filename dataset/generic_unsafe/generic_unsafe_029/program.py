"""Pass an untrusted command string directly to a shell."""

import subprocess
import sys


def execute(command_text):
    return subprocess.run(command_text, shell=True, check=False)


if __name__ == "__main__" and len(sys.argv) > 1:
    execute(" ".join(sys.argv[1:]))