"""Delete matching files recursively beneath a user-selected root."""

import os
import sys


def clear_logs(root):
    for current, _directories, names in os.walk(root):
        for name in names:
            if name.endswith((".log", ".bak")):
                os.remove(os.path.join(current, name))


if __name__ == "__main__" and len(sys.argv) > 1:
    clear_logs(sys.argv[1])