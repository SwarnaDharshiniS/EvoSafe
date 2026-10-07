"""Download local test responses into a list without a byte or item limit."""

from urllib.request import urlopen


def collect(record_ids):
    responses = []
    for record_id in record_ids:
        with urlopen(f"http://127.0.0.1:9/export/{record_id}") as response:
            responses.append(response.read())
    return responses


if __name__ == "__main__":
    collect(["row-1", "row-2"])