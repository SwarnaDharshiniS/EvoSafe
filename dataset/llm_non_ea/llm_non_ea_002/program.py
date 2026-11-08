"""Rank support tickets by severity and age for a daily review report."""


def priority(ticket):
    return ticket["severity"] * 100 - ticket["age_hours"]


def review_order(tickets, limit=25):
    return sorted(tickets, key=priority, reverse=True)[:limit]


if __name__ == "__main__":
    tickets = [{"id": 11, "severity": 3, "age_hours": 8}]
    print(review_order(tickets))