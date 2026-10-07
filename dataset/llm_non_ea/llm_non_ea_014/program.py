"""Apply a bounded convolution pass to a grayscale image represented as rows."""


def convolve(image, kernel):
    height, width = len(image), len(image[0])
    output = [[0.0 for _ in range(width)] for _ in range(height)]
    radius = len(kernel) // 2
    for row in range(radius, height - radius):
        for column in range(radius, width - radius):
            output[row][column] = sum(
                kernel[dy + radius][dx + radius] * image[row + dy][column + dx]
                for dy in range(-radius, radius + 1)
                for dx in range(-radius, radius + 1)
            )
    return output


if __name__ == "__main__":
    print(convolve([[1.0] * 5 for _ in range(5)], [[0, 1, 0], [1, -4, 1], [0, 1, 0]]))