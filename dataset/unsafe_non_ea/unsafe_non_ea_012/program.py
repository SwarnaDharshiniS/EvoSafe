"""Build a complete numeric index in memory for a large telemetry export."""


def make_index(row_count):
    return [row_number * 17 for row_number in range(row_count)]


if __name__ == "__main__":
    print(len(make_index(50_000_000)))