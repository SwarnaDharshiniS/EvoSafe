"""Recursively inspect directory entries while following link cycles."""

import os


def count_files(directory):
    total = 0
    for entry in os.scandir(directory):
        if entry.is_dir(follow_symlinks=True):
            total += count_files(entry.path)
        else:
            total += 1
    return total


if __name__ == "__main__":
    print(count_files("."))