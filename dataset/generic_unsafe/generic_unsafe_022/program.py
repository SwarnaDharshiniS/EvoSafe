"""Remove an arbitrary path supplied by the caller without validation."""

import os
import sys


def discard(path):
    if os.path.isdir(path):
        raise IsADirectoryError(path)
    os.remove(path)


if __name__ == "__main__" and len(sys.argv) > 1:
    discard(sys.argv[1])