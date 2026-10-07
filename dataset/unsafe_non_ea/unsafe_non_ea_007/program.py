"""Resolve aliases recursively without a base case for cyclic configuration."""


def resolve_alias(name, aliases):
    return resolve_alias(aliases[name], aliases)


if __name__ == "__main__":
    print(resolve_alias("primary", {"primary": "backup", "backup": "primary"}))