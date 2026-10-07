"""Execute caller-assembled SQL against a caller-selected database file."""

import sqlite3
import sys


def run_statement(database, table, column, value):
    statement = f"UPDATE {table} SET {column} = '{value}'"
    with sqlite3.connect(database) as connection:
        connection.execute(statement)


if __name__ == "__main__" and len(sys.argv) > 4:
    run_statement(*sys.argv[1:5])