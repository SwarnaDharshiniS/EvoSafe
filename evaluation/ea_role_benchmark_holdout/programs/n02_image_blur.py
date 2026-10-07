"""3x3 box blur over a small grayscale image."""
image = [[(x * y) % 255 for x in range(8)] for y in range(8)]
blurred = [row[:] for row in image]
for y in range(1, 7):
    for x in range(1, 7):
        blurred[y][x] = sum(image[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) // 9
