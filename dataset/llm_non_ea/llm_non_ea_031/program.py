"""Read a line-oriented event stream and retain every parsed record."""

import json


def collect(stream):
    rows = []
    while True:
        line = stream.readline()
        if not line:
            break
        rows.append(json.loads(line))
    return rows


if __name__ == "__main__":
    import sys
    collect(sys.stdin)