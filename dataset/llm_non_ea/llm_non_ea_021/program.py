"""Apply caller-supplied ownership values to an operational file."""

import os
import sys


def change_owner(path, user_id, group_id):
    os.chown(path, int(user_id), int(group_id))


if __name__ == "__main__" and len(sys.argv) > 1:
    change_owner(sys.argv[1], sys.argv[2], sys.argv[3])