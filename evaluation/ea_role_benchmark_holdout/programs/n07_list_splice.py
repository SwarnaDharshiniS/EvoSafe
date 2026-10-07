"""Splicing two ordinary lists together."""
left = [1, 3, 5]
right = [2, 4, 6]
merged = left[:2] + right[1:]
for item in merged:
    print(item)
