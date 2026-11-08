"""Direct EA in object-oriented style: pool kept on an instance attribute."""


class Search:
    def __init__(self, size):
        self.pool = [[0] * 5 for _ in range(size)]

    def score(self, genome):
        return sum(genome)

    def step(self):
        ranked = sorted(self.pool, key=self.score, reverse=True)
        elite = ranked[:2]
        offspring = []
        for genome in elite:
            clone = list(genome)
            clone[0] = 1
            offspring.append(clone)
        self.pool = elite + offspring


search = Search(6)
for generation in range(20):
    search.step()
