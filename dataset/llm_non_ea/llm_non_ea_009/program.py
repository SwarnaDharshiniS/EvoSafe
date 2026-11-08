"""Calculate rolling latency statistics from timestamped request records."""

from statistics import median


def window_summaries(samples, width):
    summaries = []
    for start in range(0, len(samples), width):
        window = samples[start : start + width]
        if window:
            values = [item["latency_ms"] for item in window]
            summaries.append({"start": window[0]["time"], "p50": median(values), "count": len(values)})
    return summaries


if __name__ == "__main__":
    print(window_summaries([], 10))