"""Keep the latest status record for each external job identifier."""


def latest_by_id(records):
    latest = {}
    for record in records:
        key = record["job_id"]
        if key not in latest or record["updated_at"] > latest[key]["updated_at"]:
            latest[key] = record.copy()
    return list(latest.values())


if __name__ == "__main__":
    print(latest_by_id([]))