"""Remove a requested import artifact without checking its location."""

import os
import sys


def remove_artifact(path):
    os.remove(path)


if __name__ == "__main__" and len(sys.argv) > 1:
    remove_artifact(sys.argv[1])