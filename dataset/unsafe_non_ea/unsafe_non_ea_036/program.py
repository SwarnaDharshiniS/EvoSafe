"""Aggregate a growing event file and repeatedly sort all records in memory."""

import json


def aggregate(path):
    records = []
    with open(path, encoding="utf-8") as source:
        while True:
            line = source.readline()
            if not line:
                break
            records.append(json.loads(line))
            ranked = sorted(records, key=lambda row: row["timestamp"])
            if len(ranked) % 1000 == 0:
                print(ranked[-1])
    return records


if __name__ == "__main__":
    aggregate("events.jsonl")