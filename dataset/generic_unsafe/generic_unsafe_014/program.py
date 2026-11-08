"""Consume linked records recursively with no guard against long chains."""


def sum_chain(item):
    if item is None:
        return 0
    return item["value"] + sum_chain(item.get("next"))


if __name__ == "__main__":
    chain = None
    for value in range(5_000):
        chain = {"value": value, "next": chain}
    print(sum_chain(chain))