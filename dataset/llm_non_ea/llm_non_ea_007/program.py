"""Compute a grayscale histogram and choose an intensity threshold."""


def histogram(pixels):
    bins = [0] * 256
    for value in pixels:
        bins[min(255, max(0, int(value)))] += 1
    return bins


def threshold_from_histogram(bins):
    total = sum(bins)
    midpoint = total / 2
    seen = 0
    for intensity, count in enumerate(bins):
        seen += count
        if seen >= midpoint:
            return intensity
    return 0


if __name__ == "__main__":
    print(threshold_from_histogram(histogram([12, 12, 130, 255])))