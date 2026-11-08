"""Fetch a status page from a loopback test endpoint without a timeout."""

from urllib.request import urlopen


def read_status(record_id):
    with urlopen(f"http://127.0.0.1:9/status/{record_id}") as response:
        return response.read().decode("utf-8")


if __name__ == "__main__":
    print(read_status("sample-record"))