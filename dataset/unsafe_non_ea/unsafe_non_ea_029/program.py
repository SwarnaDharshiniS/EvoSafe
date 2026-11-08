"""Load a local automation script and execute it in the current process."""

import sys


def run_script(path):
    with open(path, encoding="utf-8") as source_file:
        script_text = source_file.read()
    exec(script_text, {})


if __name__ == "__main__" and len(sys.argv) > 1:
    run_script(sys.argv[1])