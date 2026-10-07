"""Process a worklist whose handler can keep adding more work."""


def expand(record, pending):
    for child in record.get("children", ()):
        pending.append(child)


def process(seed):
    pending = [seed]
    visited_count = 0
    while pending:
        current = pending.pop()
        expand(current, pending)
        visited_count += 1
    return visited_count


if __name__ == "__main__":
    root = {"children": [{"children": []}]}
    print(process(root))