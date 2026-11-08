"""Treat interactive text as a Python expression in the current process."""


def calculate(expression):
    return eval(expression)


if __name__ == "__main__":
    print(calculate(input("expression> ")))