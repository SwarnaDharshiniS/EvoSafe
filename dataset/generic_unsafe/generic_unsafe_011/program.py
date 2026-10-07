"""A recursive retry strategy has no maximum-attempt or deadline check."""

from time import sleep


def fetch_with_retry(fetch, key, pause=0.05):
    try:
        return fetch(key)
    except TimeoutError:
        sleep(pause)
        return fetch_with_retry(fetch, key, min(pause * 2, 5))


if __name__ == "__main__":
    fetch_with_retry(lambda _key: (_ for _ in ()).throw(TimeoutError()), "invoice")