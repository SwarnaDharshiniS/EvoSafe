"""Aggregate daily sales rows into totals by store and date."""

from collections import defaultdict


def summarize(rows):
    totals = defaultdict(float)
    for row in rows:
        totals[(row["store"], row["day"])] += float(row["amount"])
    return dict(totals)


if __name__ == "__main__":
    print(summarize([{"store": "north", "day": "mon", "amount": 12.5}]))