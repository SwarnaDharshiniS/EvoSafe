"""Apply configured expressions to operational report rows."""

import json
import sys


def include_record(record, expression):
    return {**record, "visible": bool(eval(expression, {"record": record}))}


def build_report(config_path, records_path):
    with open(config_path, encoding="utf-8") as config_file:
        expression = json.load(config_file)["row_filter"]
    with open(records_path, encoding="utf-8") as records_file:
        records = json.load(records_file)
    return [include_record(record, expression) for record in records]


if __name__ == "__main__" and len(sys.argv) > 2:
    print(build_report(sys.argv[1], sys.argv[2]))