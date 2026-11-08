"""Execute the contents of a path as Python code with process privileges."""

import sys


def run_script(path):
    with open(path, encoding="utf-8") as source_file:
        source = source_file.read()
    exec(compile(source, path, "exec"), {})


if __name__ == "__main__" and len(sys.argv) > 1:
    run_script(sys.argv[1])