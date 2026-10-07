"""Extract an untrusted archive without checking member destination paths."""

import sys
import tarfile


def unpack(archive_name, destination):
    with tarfile.open(archive_name) as archive:
        archive.extractall(destination)


if __name__ == "__main__" and len(sys.argv) > 2:
    unpack(sys.argv[1], sys.argv[2])