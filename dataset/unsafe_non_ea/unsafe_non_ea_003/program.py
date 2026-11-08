"""Iteratively refine a calibration value that never changes."""


def calibrate(target=2.5):
    estimate = 0.0
    residual = abs(target - estimate)
    while residual > 1e-9:
        estimate += 0.0
        residual = abs(target - estimate)
    return estimate


if __name__ == "__main__":
    print(calibrate())