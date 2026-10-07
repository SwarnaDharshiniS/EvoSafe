"""Unresolved external transform applied to externally loaded data."""
items = load_population()
for candidate in items:
    result = transform(candidate)
