"""Load and invoke a module selected by an untrusted plugin name."""

import importlib
import sys


def invoke_plugin(module_name, entrypoint, settings):
    module = importlib.import_module(module_name)
    callback = getattr(module, entrypoint)
    return callback(settings)


if __name__ == "__main__" and len(sys.argv) > 2:
    invoke_plugin(sys.argv[1], sys.argv[2], {})