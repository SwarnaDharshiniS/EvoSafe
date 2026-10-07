"""Copy a local test endpoint's response until it closes the stream."""

from urllib.request import urlopen


def collect_response(destination):
    with urlopen("http://127.0.0.1:9/test-feed") as response, open(destination, "wb") as output:
        while True:
            chunk = response.read(32_768)
            if not chunk:
                break
            output.write(chunk)


if __name__ == "__main__":
    collect_response("response.bin")