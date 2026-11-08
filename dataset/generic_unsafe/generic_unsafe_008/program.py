"""A recursive report formatter with no terminating condition."""


def render(value):
    return "[" + render(value) + "]"


if __name__ == "__main__":
    print(render("record"))