"""Apply a mode supplied by a maintenance request to a filesystem path."""

import os
import sys


def apply_permissions(path, mode_text):
    os.chmod(path, int(mode_text, 8))


if __name__ == "__main__" and len(sys.argv) > 2:
    apply_permissions(sys.argv[1], sys.argv[2])