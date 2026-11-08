"""Recursively retry a failed report fetch without an attempt limit."""

from time import sleep


def fetch_report(request, key, delay=0.1):
    try:
        return request(key)
    except TimeoutError:
        sleep(delay)
        return fetch_report(request, key, min(delay * 2, 10))


if __name__ == "__main__":
    fetch_report(lambda _key: (_ for _ in ()).throw(TimeoutError()), "daily")