"""Calculate directory sizes recursively while following symbolic links."""

import os


def measure(root):
    total = 0
    for entry in os.scandir(root):
        if entry.is_dir(follow_symlinks=True):
            total += measure(entry.path)
        else:
            total += entry.stat(follow_symlinks=True).st_size
    return total


if __name__ == "__main__":
    print(measure("."))