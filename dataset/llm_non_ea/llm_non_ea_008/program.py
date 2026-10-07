"""Select bright image tiles for a quality-control contact sheet."""


def brightness(tile):
    return sum(sum(pixel) for row in tile for pixel in row) / max(1, sum(len(row) for row in tile))


def inspect_tiles(tiles, count=12):
    scored = [(brightness(tile), tile_id, tile) for tile_id, tile in tiles]
    return sorted(scored, key=lambda entry: entry[0], reverse=True)[:count]


if __name__ == "__main__":
    print(inspect_tiles([("tile-1", [[(20, 30, 40)]])]))