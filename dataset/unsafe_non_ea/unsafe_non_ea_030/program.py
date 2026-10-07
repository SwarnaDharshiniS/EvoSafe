"""Compile a submitted transform and run it on imported measurement data."""

import sys


def apply_transform(source_text, measurements):
    program = compile(source_text, "<submitted-transform>", "exec")
    environment = {"measurements": measurements}
    exec(program, environment)
    return environment.get("result")


if __name__ == "__main__":
    apply_transform(sys.stdin.read(), [1.0, 2.0, 3.0])