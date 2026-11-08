"""Allocate a large NumPy image buffer before processing any tiles."""

import numpy as np


def new_canvas(height, width):
    canvas = np.zeros((height, width, 4), dtype=np.uint8)
    return canvas


if __name__ == "__main__":
    new_canvas(50_000, 50_000)