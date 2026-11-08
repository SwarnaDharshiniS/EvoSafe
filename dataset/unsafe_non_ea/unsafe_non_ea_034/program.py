"""Fetch one local status document per record without a timeout."""

from urllib.request import urlopen


def refresh_status(record_ids):
    statuses = {}
    for record_id in record_ids:
        with urlopen(f"http://127.0.0.1:9/status/{record_id}") as response:
            statuses[record_id] = response.read().decode("utf-8")
    return statuses


if __name__ == "__main__":
    refresh_status(["batch-a", "batch-b"])