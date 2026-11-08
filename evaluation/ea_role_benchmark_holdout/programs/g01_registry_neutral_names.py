"""Registered EA operators whose keys and names do not reveal their roles."""


def helper_a(candidate):
    candidate[0] = -candidate[0]
    return candidate


def helper_b(candidate):
    return abs(candidate[0])


ops = make_registry()
ops.register("transform", helper_a)
ops.register("measure", helper_b)
population = [[1.0], [-2.0]]
for c in population:
    m = ops.invoke_registered("measure", c)
    t = ops.invoke_registered("transform", c)
