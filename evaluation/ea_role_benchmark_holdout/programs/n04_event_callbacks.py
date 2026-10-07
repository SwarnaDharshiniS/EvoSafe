"""Ordinary publish/subscribe event callbacks."""
handlers = {}


def on(event, fn):
    handlers.setdefault(event, []).append(fn)


def emit(event, payload):
    for fn in handlers.get(event, []):
        fn(payload)


on("save", print)
emit("save", {"id": 1})
