"""Group usage rows with an in-memory SQLite query for a local report."""

import sqlite3


def summarize(rows):
    with sqlite3.connect(":memory:") as database:
        database.execute("CREATE TABLE usage (team TEXT, units INTEGER)")
        database.executemany("INSERT INTO usage VALUES (?, ?)", rows)
        return database.execute("SELECT team, SUM(units) FROM usage GROUP BY team").fetchall()


if __name__ == "__main__":
    print(summarize([("ops", 3), ("ops", 4)]))