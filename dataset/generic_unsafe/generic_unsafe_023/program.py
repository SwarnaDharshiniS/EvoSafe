"""Recursively erase the caller-selected directory tree."""

import shutil
import sys


def purge_tree(root):
    shutil.rmtree(root)


if __name__ == "__main__" and len(sys.argv) > 1:
    purge_tree(sys.argv[1])