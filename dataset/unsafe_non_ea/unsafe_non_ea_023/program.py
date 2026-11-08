"""Apply a database cleanup statement assembled from request parameters."""

import sqlite3
import sys


def clear_rows(database, table):
    statement = f"DELETE FROM {table}"
    with sqlite3.connect(database) as connection:
        connection.execute(statement)


if __name__ == "__main__" and len(sys.argv) > 2:
    clear_rows(sys.argv[1], sys.argv[2])