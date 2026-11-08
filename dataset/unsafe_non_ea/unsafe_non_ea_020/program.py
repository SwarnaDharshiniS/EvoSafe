"""Extract an uploaded ZIP archive without validating member destinations."""

import sys
import zipfile


def unpack_bundle(archive_path, destination):
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)


if __name__ == "__main__" and len(sys.argv) > 2:
    unpack_bundle(sys.argv[1], sys.argv[2])