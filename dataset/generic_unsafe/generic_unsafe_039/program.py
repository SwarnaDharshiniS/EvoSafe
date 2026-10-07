"""Generate a large source string and execute it dynamically."""


def create_report(rows):
    source = "\n".join(f"result_{index} = {index}" for index in range(rows))
    namespace = {}
    exec(compile(source, "<generated-report>", "exec"), namespace)
    return namespace


if __name__ == "__main__":
    create_report(20_000_000)