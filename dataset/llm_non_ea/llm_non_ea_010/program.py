"""Simulate inventory changes from a finite sequence of warehouse events."""


def replay(initial, events):
    stock = initial.copy()
    for event in events:
        sku = event["sku"]
        stock[sku] = stock.get(sku, 0) + event["delta"]
        if stock[sku] < 0:
            raise ValueError(f"negative inventory for {sku}")
    return stock


if __name__ == "__main__":
    print(replay({"box": 12}, [{"sku": "box", "delta": -2}]))