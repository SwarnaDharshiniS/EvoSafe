"""Load a report-processing plugin named in the command-line configuration."""

import importlib
import sys


def process(module_name, function_name, rows):
    module = importlib.import_module(module_name)
    return getattr(module, function_name)(rows)


if __name__ == "__main__" and len(sys.argv) > 2:
    process(sys.argv[1], sys.argv[2], [])