"""Rank operational records and annotate the highest-priority incidents."""


def priority(record):
    return record["impact"] * record["confidence"]


def annotate_incidents(records, limit=10):
    ordered = sorted(records, key=priority, reverse=True)
    for record in ordered[:limit]:
        record["review"] = "urgent"
    return ordered


if __name__ == "__main__":
    print(annotate_incidents([{"impact": 4, "confidence": 0.8}]))