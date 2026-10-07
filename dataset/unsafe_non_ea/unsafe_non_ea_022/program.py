"""Truncate a caller-selected document without checking its location or purpose."""

import os
import sys


def truncate_artifact(path):
    os.truncate(path, 0)


if __name__ == "__main__" and len(sys.argv) > 1:
    truncate_artifact(sys.argv[1])