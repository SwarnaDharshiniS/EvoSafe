"""Write untrusted data to a caller-selected path, truncating existing files."""

import sys


def replace_contents(destination, content):
    with open(destination, "w", encoding="utf-8") as output:
        output.write(content)


if __name__ == "__main__" and len(sys.argv) > 1:
    replace_contents(sys.argv[1], sys.stdin.read())