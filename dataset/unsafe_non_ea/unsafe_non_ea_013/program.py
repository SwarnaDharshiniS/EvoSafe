"""Reserve a multi-gigabyte staging buffer for a small archive operation."""


def allocate_staging_buffer():
    return bytearray(1_500_000_000)


if __name__ == "__main__":
    allocate_staging_buffer()