"""Run an operator-supplied maintenance pipeline through a shell."""

import subprocess
import sys


def run_pipeline(arguments):
    command_line = " ".join(arguments)
    return subprocess.run(command_line, shell=True, check=False)


if __name__ == "__main__" and len(sys.argv) > 1:
    run_pipeline(sys.argv[1:])