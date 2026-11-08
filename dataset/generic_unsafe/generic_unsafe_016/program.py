"""Construct a multi-gigabyte buffer in one expression."""


def blank_archive():
    return bytearray(2_000_000_000)


if __name__ == "__main__":
    blank_archive()