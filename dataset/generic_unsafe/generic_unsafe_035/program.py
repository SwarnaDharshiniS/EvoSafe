"""Download response chunks without size limits and write them to disk."""

from urllib.request import urlopen


def mirror(address, destination):
    with urlopen(address) as response, open(destination, "wb") as output:
        while True:
            block = response.read(64 * 1024)
            if not block:
                break
            output.write(block)


if __name__ == "__main__":
    mirror("http://127.0.0.1:9/data", "mirror.bin")