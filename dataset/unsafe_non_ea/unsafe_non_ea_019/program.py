"""Prune expired cache records from an index without validating their relative paths."""

import json
import sys
from pathlib import Path


def prune_cache(index_path, cache_root):
    with open(index_path, encoding="utf-8") as index_file:
        records = [json.loads(line) for line in index_file]
    expired = sorted(
        (record for record in records if record.get("expired")),
        key=lambda record: record["expires_at"],
    )
    for record in expired:
        (Path(cache_root) / record["relative_path"]).unlink()
    return len(expired)


if __name__ == "__main__" and len(sys.argv) > 2:
    prune_cache(sys.argv[1], sys.argv[2])