"""Load a processing plugin named by command-line configuration."""

import importlib
import sys


def load_processor(module_name, entrypoint, batch):
    module = importlib.import_module(module_name)
    return getattr(module, entrypoint)(batch)


if __name__ == "__main__" and len(sys.argv) > 2:
    load_processor(sys.argv[1], sys.argv[2], [])