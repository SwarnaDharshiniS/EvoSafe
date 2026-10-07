"""FIFO cache eviction using slice assignment."""
cache = ["a", "b", "c"]
for key in cache:
    size = len(key)
cache[:] = cache[1:] + ["d"]
