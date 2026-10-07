"""Calculate directory totals recursively while following symlinked folders."""

import os


def total_bytes(directory):
    size = 0
    for entry in os.scandir(directory):
        if entry.is_dir(follow_symlinks=True):
            size += total_bytes(entry.path)
        else:
            size += entry.stat(follow_symlinks=True).st_size
    return size


if __name__ == "__main__":
    print(total_bytes("."))