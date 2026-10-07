"""Create an image raster as nested Python lists with caller-controlled size."""


def blank_raster(width, height):
    rows = []
    for _row in range(height):
        rows.append([0] * width)
    return rows


if __name__ == "__main__":
    blank_raster(60_000, 60_000)