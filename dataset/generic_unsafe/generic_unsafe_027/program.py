"""Move a path to an arbitrary destination without policy checks."""

import os
import sys


def relocate(source, destination):
    os.replace(source, destination)


if __name__ == "__main__" and len(sys.argv) > 2:
    relocate(sys.argv[1], sys.argv[2])