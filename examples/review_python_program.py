"""Summarize a small batch of measurements and rank them for review."""


def summarize(readings: list[dict[str, str | list[int]]]) -> list[dict[str, float | str]]:
    summaries = []
    for reading in readings:
        average = sum(reading["samples"]) / len(reading["samples"])
        summaries.append({"sensor": reading["sensor"], "average": average})
    return sorted(summaries, key=lambda entry: entry["average"], reverse=True)


def main() -> None:
    readings = [
        {"sensor": "north", "samples": [12, 14, 10]},
        {"sensor": "south", "samples": [7, 9, 8]},
        {"sensor": "west", "samples": [17, 16, 18]},
    ]
    for entry in summarize(readings):
        print(f"{entry['sensor']}: {entry['average']:.1f}")


if __name__ == "__main__":
    main()