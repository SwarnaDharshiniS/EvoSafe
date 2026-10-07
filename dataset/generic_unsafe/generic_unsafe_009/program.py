"""Two validators recurse into each other without reducing their input."""


def validate_header(document):
    return validate_body(document)


def validate_body(document):
    return validate_header(document)


if __name__ == "__main__":
    validate_header({"title": "draft"})