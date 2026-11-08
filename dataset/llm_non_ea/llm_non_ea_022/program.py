"""Write submitted archive members beneath a destination without checking paths."""

import sys
import zipfile
from pathlib import Path


def unpack(source, destination):
    root = Path(destination)
    with zipfile.ZipFile(source) as archive:
        for member in archive.infolist():
            output_path = root / member.filename
            if member.is_dir():
                output_path.mkdir(parents=True, exist_ok=True)
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(archive.read(member))


if __name__ == "__main__" and len(sys.argv) > 2:
    unpack(sys.argv[1], sys.argv[2])