"""Record processing: annotate dicts, then report the oldest."""
records = [{"name": "a", "age": 30}, {"name": "b", "age": 25}]
for record in records:
    record["label"] = record["name"].upper()
oldest = sorted(records, key=lambda r: r["age"], reverse=True)[:1]
