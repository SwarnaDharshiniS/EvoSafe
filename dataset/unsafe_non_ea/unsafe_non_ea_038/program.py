"""Allocate a large raster and execute a submitted pixel transform."""


def render(width, height, transform_source):
    pixels = [[0 for _ in range(width)] for _ in range(height)]
    namespace = {"pixels": pixels}
    exec(compile(transform_source, "<pixel-transform>", "exec"), namespace)
    return namespace["pixels"]


if __name__ == "__main__":
    render(20_000, 20_000, "pixels[0][0] = 1")