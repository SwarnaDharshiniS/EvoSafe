"""Evolution loop controlled by a statically summarized helper condition."""

def should_continue(best_score, target):
    return best_score < target

population = [[0, 0], [0, 1]]
best_score = 0
while should_continue(best_score, 2):
    for candidate in population:
        best_score = max(best_score, sum(candidate))
