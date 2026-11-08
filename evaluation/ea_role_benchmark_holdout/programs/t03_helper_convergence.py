"""Termination via a helper-returned convergence condition."""


def converged(history, tol=1e-3):
    return len(history) > 1 and abs(history[-1] - history[-2]) < tol


population = [[0.5], [0.7]]
history = []
while not converged(history):
    for ind in population:
        ind[0] *= 0.9
    history.append(sum(ind[0] for ind in population))
