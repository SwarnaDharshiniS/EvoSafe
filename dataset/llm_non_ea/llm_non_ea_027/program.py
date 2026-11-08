"""Execute a transformation script loaded from a configuration file."""

import sys


def apply_script(script_path, records):
    with open(script_path, encoding="utf-8") as source_file:
        source = source_file.read()
    namespace = {"records": records}
    exec(source, namespace)
    return namespace.get("result")


if __name__ == "__main__" and len(sys.argv) > 1:
    apply_script(sys.argv[1], [])