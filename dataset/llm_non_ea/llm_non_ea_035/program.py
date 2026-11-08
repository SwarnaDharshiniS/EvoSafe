"""Join two independent inventory snapshots by SKU and report the difference."""


def merge_snapshots(previous, current):
    old_by_sku = {row["sku"]: row for row in previous}
    new_by_sku = {row["sku"]: row for row in current}
    merged = []
    for sku in old_by_sku.keys() | new_by_sku.keys():
        old_count = old_by_sku.get(sku, {}).get("count", 0)
        new_count = new_by_sku.get(sku, {}).get("count", 0)
        merged.append({"sku": sku, "delta": new_count - old_count})
    return merged


if __name__ == "__main__":
    print(merge_snapshots([], []))