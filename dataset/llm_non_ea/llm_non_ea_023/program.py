"""Save a generated report to a caller-selected output path."""

import sys


def write_report(path, text):
    with open(path, "w", encoding="utf-8") as output:
        output.write(text)


if __name__ == "__main__" and len(sys.argv) > 1:
    write_report(sys.argv[1], sys.stdin.read())