"""Invoke a user-selected maintenance command through the system shell."""

import os
import sys


def run_maintenance(command):
    return os.system(command)


if __name__ == "__main__" and len(sys.argv) > 1:
    run_maintenance(" ".join(sys.argv[1:]))