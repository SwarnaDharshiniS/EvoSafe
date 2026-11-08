"""Callbacks registered under EA-sounding keys that do ordinary text work."""


def mutate(message):
    return message.upper()


def select(lines):
    return [line for line in lines if line]


bus = make_registry()
bus.register("mutate", mutate)
bus.register("select", select)
text = bus.invoke_registered("mutate", "hello")
lines = bus.invoke_registered("select", ["a", "", "b"])
