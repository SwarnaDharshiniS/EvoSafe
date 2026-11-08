"""Evaluate a user-supplied filter expression against report rows."""


def filter_rows(rows, expression):
    return [row for row in rows if eval(expression, {"row": row})]


if __name__ == "__main__":
    print(filter_rows([{"active": True}], input("filter expression> ")))