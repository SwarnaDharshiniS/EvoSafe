# EvoSafe held-out seven-role EA evaluation benchmark

- Labeled programs: **51**
- Metrics are benchmark-only and are not merged with unlabeled corpus results.
- Ground truth is explicit per program for all seven roles; each role includes a rationale whether positive or negative.

## Per-role metrics

| Role | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| population | 28 | 5 | 7 | 11 | 0.848 | 0.800 | 0.824 |
| fitness_evaluation | 22 | 5 | 14 | 10 | 0.815 | 0.611 | 0.698 |
| selection | 6 | 2 | 10 | 33 | 0.750 | 0.375 | 0.500 |
| mutation | 9 | 3 | 10 | 29 | 0.750 | 0.474 | 0.581 |
| crossover | 0 | 0 | 8 | 43 | — | 0.000 | — |
| replacement | 4 | 1 | 7 | 39 | 0.800 | 0.364 | 0.500 |
| termination | 7 | 1 | 4 | 39 | 0.875 | 0.636 | 0.737 |

**Macro average** over 6 roles: precision **0.806**, recall **0.543**, F1 **0.640**.

## Program-level findings

### `d01_direct_while_convergence` — direct_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of bit-list genomes iterated each generation.<br>Evidence: line 7: A comprehension invokes a computation on each element of a collection; generator and call source locations are retained. (`[(sum(ind), ind) for ind in population]`)<br>line 15: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for child in children:
    pos = random.randrange(6)
    child[pos] = 1 - child[pos]`) |
| fitness_evaluation | True | True | MEDIUM | Truth: sum(ind) scores each genome.<br>Evidence: line 7: A call consumes the comprehension's candidate variable while iterating a collection. (`sum(ind)`) |
| selection | True | False | LOW | Truth: Scored genomes are sorted and the top four kept as parents.<br>Evidence: No detector evidence. |
| mutation | True | True | HIGH | Truth: A random bit of each child is flipped.<br>Evidence: line 17: A candidate or its alias is modified through an element or attribute update. (`child[pos] = 1 - child[pos]`) |
| crossover | True | False | LOW | Truth: Children join a prefix of one parent and suffix of the next.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: population is reassigned to parents + children.<br>Evidence: line 18: A candidate collection is replaced by a newly composed collection. (`population = parents + children`) |
| termination | True | True | MEDIUM | Truth: while best < 6 stops on reaching the optimum.<br>Evidence: line 6: The evolutionary loop is controlled by a runtime condition. (`while best < 6:
    scored = [(sum(ind), ind) for ind in population]
    scored.sort(reverse=True)
    best = scored[0][0]
    parents = [ind for _, ind in scored[:4]]
    children = []
    for i in range(0, len(parents) - 1, 2):
        cut = random.randrange(1, 6)
        children.append(parents[i][:cut] + parents[i + 1][cut:])
    for child in children:
        pos = random.randrange(6)
        child[pos] = 1 - child[pos]
    population = parents + children`) |

### `d02_direct_class_based` — direct_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: self.pool holds the candidate genomes.<br>Evidence: line 15: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for genome in elite:
    clone = list(genome)
    clone[0] = 1
    offspring.append(clone)`) |
| fitness_evaluation | True | True | HIGH | Truth: Search.score sums a genome and is used as the ranking key.<br>Evidence: line 16: A computed value depends on a candidate passed to a call. (`clone = list(genome)`) |
| selection | True | False | LOW | Truth: sorted(..., key=self.score)[:2] keeps the elite.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: A copied genome has a gene overwritten to form offspring.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Offspring derive from a single elite genome; no two parents are combined.<br>Evidence: No detector evidence. |
| replacement | True | False | LOW | Truth: self.pool is reassigned to elite + offspring.<br>Evidence: No detector evidence. |
| termination | True | False | LOW | Truth: Generations are bounded by range(20).<br>Evidence: No detector evidence. |

### `d03_direct_numpy_es` — direct_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | False | LOW | Truth: pop is a 10x3 array of candidate vectors.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: np.sum(pop ** 2, axis=1) scores every row.<br>Evidence: No detector evidence. |
| selection | True | False | LOW | Truth: argsort order selects the five best rows as parents.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: Gaussian noise is added to parents to create kids.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Each kid comes from one parent plus noise; no recombination.<br>Evidence: No detector evidence. |
| replacement | True | False | LOW | Truth: pop is rebuilt from parents and kids via vstack.<br>Evidence: No detector evidence. |
| termination | True | False | LOW | Truth: Generations are bounded by range(50).<br>Evidence: No detector evidence. |

### `d04_direct_dict_individuals` — direct_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: pop is a list of dict individuals holding genes.<br>Evidence: line 6: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for ind in pop:
    ind['fitness'] = -sum(((g - 0.5) ** 2 for g in ind['genes']))`) |
| fitness_evaluation | True | False | LOW | Truth: ind['fitness'] is computed from the genes.<br>Evidence: No detector evidence. |
| selection | True | True | HIGH | Truth: pop is sorted by fitness and the top five survive.<br>Evidence: line 8: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`pop.sort(key=lambda ind: ind['fitness'], reverse=True)`)<br>line 9: A slice of the population is retained as survivors. (`survivors = pop[:5]`)<br>line 15: The retained slice is used to rebuild the population. (`pop = survivors + newborn`) |
| mutation | False | True | HIGH | Truth: Genes are only inherited; no gene is perturbed or overwritten after crossover.<br>Evidence: line 7: A candidate or its alias is modified through an element or attribute update. (`ind['fitness'] = -sum(((g - 0.5) ** 2 for g in ind['genes']))`) |
| crossover | True | False | LOW | Truth: Uniform crossover picks each gene from ind or mate.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: pop is reassigned to survivors + newborn.<br>Evidence: line 15: A candidate collection is replaced by a newly composed collection. (`pop = survivors + newborn`) |
| termination | True | True | HIGH | Truth: Generations are bounded by range(30).<br>Evidence: line 5: The evolutionary loop iterates a finite built-in range or literal collection. (`for gen in range(30):
    for ind in pop:
        ind['fitness'] = -sum(((g - 0.5) ** 2 for g in ind['genes']))
    pop.sort(key=lambda ind: ind['fitness'], reverse=True)
    survivors = pop[:5]
    newborn = []
    for ind in survivors:
        mate = random.choice(survivors)
        genes = [a if random.random() < 0.5 else b for a, b in zip(ind['genes'], mate['genes'])]
        newborn.append({'genes': genes})
    pop = survivors + newborn`) |

### `h01_helper_chain_mutation` — helper_chain

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of genomes iterated in a loop.<br>Evidence: line 16: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for genome in population:
    fitness = sum(genome)
    offspring = mutate(genome)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(genome) scores each genome.<br>Evidence: line 12: The helper returns a call result whose arguments include candidate-derived values. (`random.randrange(len(child))`)<br>line 12: The helper returns a call result whose arguments include candidate-derived values. (`len(child)`)<br>line 17: A computed value depends on a candidate passed to a call. (`fitness = sum(genome)`)<br>line 18: Local helper 'mutate' receives values structurally linked to the EA role inputs. (`mutate(genome)`) |
| selection | False | False | LOW | Truth: No candidate is chosen over another.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: mutate copies the genome and flip() inverts a random bit through a second helper.<br>Evidence: line 6: The helper delegates this operation to local helper 'flip': The helper writes an element or attribute of its candidate argument. (`bits[i] = 1 - bits[i]`)<br>line 18: Local helper 'mutate' receives values structurally linked to the EA role inputs. (`mutate(genome)`) |
| crossover | False | False | LOW | Truth: No two genomes are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is never rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop or stop condition.<br>Evidence: No detector evidence. |

### `h02_helper_chain_fitness` — helper_chain

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | MEDIUM | Truth: population is a list of genomes iterated in a comprehension.<br>Evidence: line 17: A comprehension invokes a computation on each element of a collection; generator and call source locations are retained. (`[evaluate(g) for g in population]`) |
| fitness_evaluation | True | True | MEDIUM | Truth: evaluate -> objective(decode(genome)) scores each genome through three helpers.<br>Evidence: line 9: The helper delegates this operation to local helper 'objective': The helper returns a call result whose arguments include candidate-derived values. (`sum((v * v for v in values))`)<br>line 17: A call consumes the comprehension's candidate variable while iterating a collection. (`evaluate(g)`)<br>line 17: Local helper 'evaluate' receives values structurally linked to the EA role inputs. (`evaluate(g)`) |
| selection | False | False | LOW | Truth: Scores are computed but never used to choose candidates.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: decode builds a derived value list for scoring; the genome is not varied.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No two genomes are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is never rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `h03_helper_chain_crossover_replace` — helper_chain

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | False | LOW | Truth: pool is the list of genomes evolved by next_generation.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: pool.sort(key=sum) scores genomes by sum.<br>Evidence: No detector evidence. |
| selection | True | False | LOW | Truth: The two best genomes after sorting become parents.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No gene is perturbed; the child is a pure recombination.<br>Evidence: No detector evidence. |
| crossover | True | False | LOW | Truth: recombine -> splice joins two parents at a random cut.<br>Evidence: No detector evidence. |
| replacement | True | False | LOW | Truth: pool is reassigned to the helper-returned parents + child.<br>Evidence: No detector evidence. |
| termination | True | False | LOW | Truth: Generations are bounded by range(10).<br>Evidence: No detector evidence. |

### `a01_multilevel_population_alias` — alias

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: initial -> pool -> current -> alias_of_alias all name the candidate list.<br>Evidence: line 7: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in current:
    cost = sum((x * x for x in individual))`) |
| fitness_evaluation | True | True | HIGH | Truth: cost is a per-individual sum of squares.<br>Evidence: line 8: A computed value depends on a candidate passed to a call. (`cost = sum((x * x for x in individual))`) |
| selection | True | False | LOW | Truth: The aliased list is sorted by cost and sliced to the two best.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No candidate is modified.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: elite is a new name; the population is not replaced.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `a02_candidate_alias_mutation` — alias

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidate vectors iterated as member.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for member in population:
    score = member[0] + member[1]
    view = member
    same = view
    same[1] = same[1] * 0.9`) |
| fitness_evaluation | True | False | LOW | Truth: score is computed from each member.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: No candidate is chosen.<br>Evidence: No detector evidence. |
| mutation | True | True | HIGH | Truth: same, an alias of view and member, has a gene scaled in place.<br>Evidence: line 7: A candidate or its alias is modified through an element or attribute update. (`same[1] = same[1] * 0.9`) |
| crossover | False | False | LOW | Truth: No two candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `a03_offspring_alias_replacement` — alias

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: pop is a list of candidates iterated as p.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for p in pop:
    val = sum(p)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(p) scores each candidate.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`val = sum(p)`) |
| selection | False | False | LOW | Truth: No candidate is chosen by quality.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No candidate is altered.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Offspring are literals, not combinations of parents.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: pop[:] is overwritten with next_pop, an alias of offspring.<br>Evidence: line 7: A statically resolved alias of an inferred population is replaced by slice assignment. (`pop[:] = next_pop`)<br>line 7: An element of an inferred candidate collection is replaced. (`pop[:] = next_pop`) |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `c01_uniform_crossover` — crossover

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of bit genomes.<br>Evidence: line 5: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for genome in population:
    fit = sum(genome)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(genome) scores each genome.<br>Evidence: line 6: A computed value depends on a candidate passed to a call. (`fit = sum(genome)`) |
| selection | False | False | LOW | Truth: Parents are fixed indices, not chosen by quality.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No gene is perturbed.<br>Evidence: No detector evidence. |
| crossover | True | False | LOW | Truth: child picks each gene from mother or father uniformly at random.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `c02_blend_crossover_helper` — crossover

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of real vectors.<br>Evidence: line 9: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for vec in population:
    loss = sum((v * v for v in vec))`) |
| fitness_evaluation | True | True | HIGH | Truth: loss is a per-vector sum of squares.<br>Evidence: line 10: A computed value depends on a candidate passed to a call. (`loss = sum((v * v for v in vec))`) |
| selection | False | False | LOW | Truth: Parents are adjacent indices, not chosen by quality.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No random perturbation is applied.<br>Evidence: No detector evidence. |
| crossover | True | False | LOW | Truth: blend(x, y) arithmetically combines two adjacent population members.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: offspring never replaces population.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `c03_single_point_numpy` — crossover

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | False | LOW | Truth: pop is a 6x5 array of candidate rows.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: pop.sum(axis=1) scores every row.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Rows 0 and 1 are fixed, not chosen by fitness.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No gene is perturbed.<br>Evidence: No detector evidence. |
| crossover | True | False | LOW | Truth: np.concatenate joins p1[:cut] and p2[cut:].<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: pop is never rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `c04_crossover_method` — crossover

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of Genome objects.<br>Evidence: line 14: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for g in population:
    g.score = sum(g.genes)`) |
| fitness_evaluation | True | True | HIGH | Truth: g.score = sum(g.genes) scores each genome.<br>Evidence: line 15: A computed value depends on a candidate passed to a call. (`g.score = sum(g.genes)`) |
| selection | False | False | LOW | Truth: Parents are fixed indices.<br>Evidence: No detector evidence. |
| mutation | False | True | HIGH | Truth: No gene is perturbed.<br>Evidence: line 15: A candidate or its alias is modified through an element or attribute update. (`g.score = sum(g.genes)`) |
| crossover | True | False | LOW | Truth: Genome.cross(other) builds a child from halves of two genomes.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `m01_gaussian_inplace` — mutation

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of real vectors.<br>Evidence: line 5: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for vec in population:
    energy = sum((x * x for x in vec))`)<br>line 7: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for vec in population:
    for i in range(len(vec)):
        vec[i] += random.gauss(0, 0.1)`) |
| fitness_evaluation | True | True | HIGH | Truth: energy is a per-vector sum of squares.<br>Evidence: line 6: A computed value depends on a candidate passed to a call. (`energy = sum((x * x for x in vec))`) |
| selection | False | False | LOW | Truth: No candidate is chosen.<br>Evidence: No detector evidence. |
| mutation | True | True | HIGH | Truth: Every gene receives Gaussian noise in place via vec[i] +=.<br>Evidence: line 9: A candidate or its alias is modified through an element or attribute update. (`vec[i] += random.gauss(0, 0.1)`) |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop; range loops only index genes.<br>Evidence: No detector evidence. |

### `m02_attribute_mutation` — mutation

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: agents is a list of Agent candidates.<br>Evidence: line 12: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for agent in agents:
    agent.score = agent.speed - agent.size`)<br>line 14: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for agent in agents:
    agent.speed *= random.uniform(0.9, 1.1)`) |
| fitness_evaluation | True | False | LOW | Truth: agent.score is computed from agent attributes.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: No agent is chosen.<br>Evidence: No detector evidence. |
| mutation | True | True | HIGH | Truth: agent.speed is randomly rescaled in place.<br>Evidence: line 13: A candidate or its alias is modified through an element or attribute update. (`agent.score = agent.speed - agent.size`)<br>line 15: A candidate or its alias is modified through an element or attribute update. (`agent.speed *= random.uniform(0.9, 1.1)`) |
| crossover | False | False | LOW | Truth: No agents are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The agent list is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `m03_swap_mutation_copy` — mutation

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: tours is a list of permutation candidates.<br>Evidence: line 5: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for tour in tours:
    length = sum((abs(tour[i] - tour[i + 1]) for i in range(len(tour) - 1)))`) |
| fitness_evaluation | True | True | HIGH | Truth: length scores each tour.<br>Evidence: line 6: A computed value depends on a candidate passed to a call. (`length = sum((abs(tour[i] - tour[i + 1]) for i in range(len(tour) - 1)))`) |
| selection | False | False | LOW | Truth: random.sample picks gene positions, not candidates; tours[0] is fixed.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: Two positions of a copied tour are swapped.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Only one tour is involved.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: tours is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `m04_perturb_helper` — mutation

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | False | LOW | Truth: population is a list of candidate solutions.<br>Evidence: line 10: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for s in population:
    cost = abs(s[0]) + abs(s[1])
    neighbour = perturb(s, 0.1)`) |
| fitness_evaluation | True | False | LOW | Truth: cost is computed per solution.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: No solution is chosen.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: perturb returns a uniformly perturbed copy of a solution.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No solutions are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `s01_tournament` — selection

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | MEDIUM | Truth: population is a list of candidate vectors.<br>Evidence: line 5: A comprehension invokes a computation on each element of a collection; generator and call source locations are retained. (`[sum(p) for p in population]`) |
| fitness_evaluation | True | True | MEDIUM | Truth: scores holds sum(p) per candidate.<br>Evidence: line 5: A call consumes the comprehension's candidate variable while iterating a collection. (`sum(p)`) |
| selection | True | True | MEDIUM | Truth: tournament samples k contestants and returns the best by score.<br>Evidence: line 9: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`random.sample(range(len(population)), k)`) |
| mutation | False | False | LOW | Truth: No candidate is altered.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: range(4) repeats parent draws; it is not a generation loop.<br>Evidence: No detector evidence. |

### `s02_roulette` — selection

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | MEDIUM | Truth: population is a list of bit genomes.<br>Evidence: line 5: A comprehension invokes a computation on each element of a collection; generator and call source locations are retained. (`[sum(p) + 1 for p in population]`) |
| fitness_evaluation | True | True | MEDIUM | Truth: weights are sum(p) + 1 per genome.<br>Evidence: line 5: A call consumes the comprehension's candidate variable while iterating a collection. (`sum(p)`) |
| selection | True | True | MEDIUM | Truth: random.choices draws parents proportionally to weights.<br>Evidence: line 6: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`random.choices(population, weights=weights, k=2)`) |
| mutation | False | False | LOW | Truth: No genome is altered.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No genomes are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `s03_filter_threshold` — selection

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidate vectors.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for p in population:
    total = sum(p)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(p) scores each candidate.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`total = sum(p)`) |
| selection | True | True | MEDIUM | Truth: Candidates with sum above 0.6 are kept as viable.<br>Evidence: line 5: A comprehension filters an inferred candidate collection by a condition. (`[p for p in population if sum(p) > 0.6]`) |
| mutation | False | False | LOW | Truth: No candidate is altered.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: viable is a new name; the population is not replaced.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `s04_heapq_nlargest` — selection

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | False | LOW | Truth: population is a list of candidates.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: merit is c[0] * c[1] per candidate.<br>Evidence: No detector evidence. |
| selection | True | False | LOW | Truth: heapq.nlargest keeps the two best by merit.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No candidate is altered.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not replaced.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `r01_reassignment_elitism` — replacement

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidates.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for ind in population:
    value = sum(ind)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(ind) scores each candidate.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`value = sum(ind)`) |
| selection | True | True | HIGH | Truth: sorted(..., key=sum)[-1:] keeps the best as elite.<br>Evidence: line 5: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`sorted(population, key=sum)`) |
| mutation | False | False | LOW | Truth: No candidate is altered.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: children are literals, not combinations.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: population is reassigned to elite + children.<br>Evidence: line 7: A candidate collection is replaced by a newly composed collection. (`population = elite + children`) |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `r02_steady_state_remove_append` — replacement

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidates.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for ind in population:
    value = sum(ind)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(ind) scores each candidate.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`value = sum(ind)`) |
| selection | True | True | MEDIUM | Truth: min(population, key=sum) chooses the worst for removal.<br>Evidence: line 5: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`min(population, key=sum)`) |
| mutation | False | False | LOW | Truth: No candidate is altered.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: newcomer is a literal.<br>Evidence: No detector evidence. |
| replacement | True | False | LOW | Truth: The worst is removed and a newcomer appended.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `r03_index_replacement` — replacement

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | False | LOW | Truth: population is a list of candidates.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: scores holds p[0] per candidate.<br>Evidence: No detector evidence. |
| selection | True | False | LOW | Truth: scores.index(min(scores)) chooses the worst slot.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: The worst slot is replaced, not varied.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | True | False | LOW | Truth: population[worst] is overwritten with a new random candidate.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `t01_bounded_generations` — termination

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidates.<br>Evidence: line 6: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for ind in population:
    loss = (ind[0] - 0.5) ** 2
    ind[0] -= 0.1 * (ind[0] - 0.5)`) |
| fitness_evaluation | True | False | LOW | Truth: loss is computed per candidate.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: No candidate is chosen.<br>Evidence: No detector evidence. |
| mutation | True | True | HIGH | Truth: Each candidate's gene is updated in place every epoch.<br>Evidence: line 8: A candidate or its alias is modified through an element or attribute update. (`ind[0] -= 0.1 * (ind[0] - 0.5)`) |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | True | True | HIGH | Truth: The generation loop is bounded by range(100).<br>Evidence: line 5: The evolutionary loop iterates a finite built-in range or literal collection. (`for epoch in range(100):
    for ind in population:
        loss = (ind[0] - 0.5) ** 2
        ind[0] -= 0.1 * (ind[0] - 0.5)`) |

### `t02_stagnation` — termination

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidates.<br>Evidence: line 12: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for ind in population:
    ind[0] += random.gauss(0, 0.05)`) |
| fitness_evaluation | True | False | LOW | Truth: (ind[0] - 0.3) ** 2 scores each candidate.<br>Evidence: No detector evidence. |
| selection | False | True | MEDIUM | Truth: min only tracks the best value; no candidate is chosen.<br>Evidence: line 7: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`min(((ind[0] - 0.3) ** 2 for ind in population))`) |
| mutation | True | True | HIGH | Truth: Gaussian noise is added to each candidate in place.<br>Evidence: line 13: A candidate or its alias is modified through an element or attribute update. (`ind[0] += random.gauss(0, 0.05)`) |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | True | True | MEDIUM | Truth: while stale < 10 stops after ten non-improving generations.<br>Evidence: line 6: The evolutionary loop is controlled by a runtime condition. (`while stale < 10:
    current = min(((ind[0] - 0.3) ** 2 for ind in population))
    if current < best:
        best, stale = (current, 0)
    else:
        stale += 1
    for ind in population:
        ind[0] += random.gauss(0, 0.05)`) |

### `t03_helper_convergence` — termination

Safety: **CONDITIONALLY_SAFE** (without EA: CONDITIONALLY_SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidates.<br>Evidence: line 11: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for ind in population:
    ind[0] *= 0.9`) |
| fitness_evaluation | False | False | LOW | Truth: Only a population-wide aggregate is recorded; no candidate is individually scored.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: No candidate is chosen.<br>Evidence: No detector evidence. |
| mutation | True | True | HIGH | Truth: ind[0] is scaled in place each iteration.<br>Evidence: line 12: A candidate or its alias is modified through an element or attribute update. (`ind[0] *= 0.9`) |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | True | True | MEDIUM | Truth: while not converged(history) stops when the helper reports convergence.<br>Evidence: line 10: The evolutionary loop is controlled by a runtime condition. (`while not converged(history):
    for ind in population:
        ind[0] *= 0.9
    history.append(sum((ind[0] for ind in population)))`) |

### `g01_registry_neutral_names` — registration

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidates passed to registered operators.<br>Evidence: line 17: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for c in population:
    m = ops.invoke_registered('measure', c)
    t = ops.invoke_registered('transform', c)`)<br>line 17: A registered EA operation consumes a loop element drawn from a collection. (`for c in population:
    m = ops.invoke_registered('measure', c)
    t = ops.invoke_registered('transform', c)`) |
| fitness_evaluation | True | True | MEDIUM | Truth: helper_b, registered as 'measure', scores a candidate.<br>Evidence: line 10: The helper returns a call result whose arguments include candidate-derived values. (`abs(candidate[0])`)<br>line 15: The registered callback body provides structural evidence for fitness_evaluation. (`ops.register('measure', helper_b)`)<br>line 18: This reference resolves to the callable registered under 'measure'. (`ops.invoke_registered`)<br>line 18: The registered callable is dispatched with arguments linked to the fitness_evaluation role. (`ops.invoke_registered('measure', c)`) |
| selection | False | False | LOW | Truth: No candidate is chosen.<br>Evidence: No detector evidence. |
| mutation | True | True | MEDIUM | Truth: helper_a, registered as 'transform', negates a gene in place.<br>Evidence: line 5: The helper writes an element or attribute of its candidate argument. (`candidate[0] = -candidate[0]`)<br>line 14: The registered callback body provides structural evidence for mutation. (`ops.register('transform', helper_a)`)<br>line 19: This reference resolves to the callable registered under 'transform'. (`ops.invoke_registered`)<br>line 19: The registered callable is dispatched with arguments linked to the mutation role. (`ops.invoke_registered('transform', c)`) |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `g02_misleading_ea_keys_non_ea` — registration_non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Strings and lines are processed; there is no candidate collection.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Nothing is scored.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Filtering empty lines is ordinary text cleanup.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: upper() formats a message; no candidate is varied.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Nothing is combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Nothing is replaced.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no loop.<br>Evidence: No detector evidence. |

### `g03_dict_dispatch_mutation` — registration

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of vectors.<br>Evidence: line 13: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for vec in population:
    score = sum(vec)
    child = ops['mut'](vec)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(vec) scores each vector.<br>Evidence: line 14: A computed value depends on a candidate passed to a call. (`score = sum(vec)`)<br>line 15: A computed value depends on a candidate passed to a call. (`child = ops['mut'](vec)`) |
| selection | False | False | LOW | Truth: No vector is chosen.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: ops['mut'] dispatches to jitter, which perturbs a copied vector.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No vectors are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `f01_engine_callbacks` — framework

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: The population lives inside the external engine.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: fitness_func scores a solution and is supplied to Engine.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Parent selection is framework-internal.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: mutation_func adds noise to offspring genes and is supplied to Engine.<br>Evidence: No detector evidence. |
| crossover | True | False | LOW | Truth: crossover_func joins halves of two parents and is supplied to Engine.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Population replacement is framework-internal.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: num_generations is configuration; the loop is framework-internal.<br>Evidence: No detector evidence. |

### `f02_engine_parent_selection` — framework

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: The population lives inside the external engine.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: fitness_func scores a solution and is supplied to Engine.<br>Evidence: No detector evidence. |
| selection | True | False | LOW | Truth: parent_selection_func returns the top-ranked solutions and is supplied to Engine.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Mutation is framework-internal.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Crossover is framework-internal.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Replacement is framework-internal.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: num_generations is configuration only.<br>Evidence: No detector evidence. |

### `f03_engine_config_only` — framework

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: No population is defined in source.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: No fitness function is defined in source.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: No selection logic in source.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: mutation_percent_genes is configuration only.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No crossover logic in source.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: No replacement logic in source.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: num_generations is configuration only.<br>Evidence: No detector evidence. |

### `n01_matrix_multiply` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Plain matrix multiplication: index loops accumulate products; nothing evolves.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Plain matrix multiplication: index loops accumulate products; nothing evolves.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Plain matrix multiplication: index loops accumulate products; nothing evolves.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Plain matrix multiplication: index loops accumulate products; nothing evolves.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Plain matrix multiplication: index loops accumulate products; nothing evolves.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Plain matrix multiplication: index loops accumulate products; nothing evolves.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Plain matrix multiplication: index loops accumulate products; nothing evolves.<br>Evidence: No detector evidence. |

### `n02_image_blur` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Image box blur: pixel writes are convolution, not candidate variation.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Image box blur: pixel writes are convolution, not candidate variation.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Image box blur: pixel writes are convolution, not candidate variation.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Image box blur: pixel writes are convolution, not candidate variation.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Image box blur: pixel writes are convolution, not candidate variation.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Image box blur: pixel writes are convolution, not candidate variation.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Image box blur: pixel writes are convolution, not candidate variation.<br>Evidence: No detector evidence. |

### `n03_sgd_training` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | True | HIGH | Truth: Single-model gradient descent: data rows are not candidates and weight updates are not mutation.<br>Evidence: line 7: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for features, target in data:
    prediction = sum((w * x for w, x in zip(weights, features)))
    error = prediction - target
    for i in range(len(weights)):
        weights[i] -= 0.01 * error * features[i]`) |
| fitness_evaluation | False | True | HIGH | Truth: Single-model gradient descent: data rows are not candidates and weight updates are not mutation.<br>Evidence: line 8: A computed value depends on a candidate passed to a call. (`prediction = sum((w * x for w, x in zip(weights, features)))`) |
| selection | False | False | LOW | Truth: Single-model gradient descent: data rows are not candidates and weight updates are not mutation.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Single-model gradient descent: data rows are not candidates and weight updates are not mutation.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Single-model gradient descent: data rows are not candidates and weight updates are not mutation.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Single-model gradient descent: data rows are not candidates and weight updates are not mutation.<br>Evidence: No detector evidence. |
| termination | False | True | HIGH | Truth: Single-model gradient descent: data rows are not candidates and weight updates are not mutation.<br>Evidence: line 6: The evolutionary loop iterates a finite built-in range or literal collection. (`for epoch in range(100):
    for features, target in data:
        prediction = sum((w * x for w, x in zip(weights, features)))
        error = prediction - target
        for i in range(len(weights)):
            weights[i] -= 0.01 * error * features[i]`) |

### `n04_event_callbacks` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Ordinary publish/subscribe callbacks with no optimisation process.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Ordinary publish/subscribe callbacks with no optimisation process.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Ordinary publish/subscribe callbacks with no optimisation process.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Ordinary publish/subscribe callbacks with no optimisation process.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Ordinary publish/subscribe callbacks with no optimisation process.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Ordinary publish/subscribe callbacks with no optimisation process.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Ordinary publish/subscribe callbacks with no optimisation process.<br>Evidence: No detector evidence. |

### `n05_record_processing` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | True | HIGH | Truth: Records are annotated and reported; sorting by age is reporting, not evolutionary selection.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for record in records:
    record['label'] = record['name'].upper()`) |
| fitness_evaluation | False | True | HIGH | Truth: Records are annotated and reported; sorting by age is reporting, not evolutionary selection.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`record['label'] = record['name'].upper()`) |
| selection | False | True | HIGH | Truth: Records are annotated and reported; sorting by age is reporting, not evolutionary selection.<br>Evidence: line 5: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`sorted(records, key=lambda r: r['age'], reverse=True)`) |
| mutation | False | True | HIGH | Truth: Records are annotated and reported; sorting by age is reporting, not evolutionary selection.<br>Evidence: line 4: A candidate or its alias is modified through an element or attribute update. (`record['label'] = record['name'].upper()`) |
| crossover | False | False | LOW | Truth: Records are annotated and reported; sorting by age is reporting, not evolutionary selection.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Records are annotated and reported; sorting by age is reporting, not evolutionary selection.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Records are annotated and reported; sorting by age is reporting, not evolutionary selection.<br>Evidence: No detector evidence. |

### `n06_survey_sampling` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Random survey sampling with no scoring or evolution.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Random survey sampling with no scoring or evolution.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Random survey sampling with no scoring or evolution.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Random survey sampling with no scoring or evolution.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Random survey sampling with no scoring or evolution.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Random survey sampling with no scoring or evolution.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Random survey sampling with no scoring or evolution.<br>Evidence: No detector evidence. |

### `n07_list_splice` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Two ordinary lists are spliced; they are data, not parent candidates.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Two ordinary lists are spliced; they are data, not parent candidates.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Two ordinary lists are spliced; they are data, not parent candidates.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Two ordinary lists are spliced; they are data, not parent candidates.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Two ordinary lists are spliced; they are data, not parent candidates.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Two ordinary lists are spliced; they are data, not parent candidates.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Two ordinary lists are spliced; they are data, not parent candidates.<br>Evidence: No detector evidence. |

### `n08_tensor_batch` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Batched linear-layer training: batch rows are data and the weight update is a gradient step.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Batched linear-layer training: batch rows are data and the weight update is a gradient step.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Batched linear-layer training: batch rows are data and the weight update is a gradient step.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Batched linear-layer training: batch rows are data and the weight update is a gradient step.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Batched linear-layer training: batch rows are data and the weight update is a gradient step.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Batched linear-layer training: batch rows are data and the weight update is a gradient step.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Batched linear-layer training: batch rows are data and the weight update is a gradient step.<br>Evidence: No detector evidence. |

### `n09_cache_eviction` — non_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | True | HIGH | Truth: FIFO cache eviction: slice assignment updates a cache, not a population.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for key in cache:
    size = len(key)`) |
| fitness_evaluation | False | True | HIGH | Truth: FIFO cache eviction: slice assignment updates a cache, not a population.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`size = len(key)`) |
| selection | False | False | LOW | Truth: FIFO cache eviction: slice assignment updates a cache, not a population.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: FIFO cache eviction: slice assignment updates a cache, not a population.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: FIFO cache eviction: slice assignment updates a cache, not a population.<br>Evidence: No detector evidence. |
| replacement | False | True | HIGH | Truth: FIFO cache eviction: slice assignment updates a cache, not a population.<br>Evidence: line 5: A statically resolved alias of an inferred population is replaced by slice assignment. (`cache[:] = cache[1:] + ['d']`)<br>line 5: An element of an inferred candidate collection is replaced. (`cache[:] = cache[1:] + ['d']`) |
| termination | False | False | LOW | Truth: FIFO cache eviction: slice assignment updates a cache, not a population.<br>Evidence: No detector evidence. |

### `x01_unresolved_transform` — ambiguous

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | True | HIGH | Truth: load_population and transform are unresolved; no role is implemented in this source.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in items:
    result = transform(candidate)`) |
| fitness_evaluation | False | True | HIGH | Truth: load_population and transform are unresolved; no role is implemented in this source.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`result = transform(candidate)`) |
| selection | False | False | LOW | Truth: load_population and transform are unresolved; no role is implemented in this source.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: load_population and transform are unresolved; no role is implemented in this source.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: load_population and transform are unresolved; no role is implemented in this source.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: load_population and transform are unresolved; no role is implemented in this source.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: load_population and transform are unresolved; no role is implemented in this source.<br>Evidence: No detector evidence. |

### `x02_getattr_dispatch` — ambiguous

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of genomes.<br>Evidence: line 14: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for genome in population:
    score = sum(genome)
    operator(genome)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(genome) scores each genome.<br>Evidence: line 15: A computed value depends on a candidate passed to a call. (`score = sum(genome)`) |
| selection | False | False | LOW | Truth: random.choice picks an operator name, not a candidate.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: The getattr-resolved operator is Operators.bitflip, which flips a gene in place.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No genomes are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `x03_eval_built_operator` — ambiguous

Safety: **UNSAFE** (without EA: UNSAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of genomes.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for genome in population:
    rank = genome[0]
    reverse_op = eval('lambda g: g[::-1]')
    mutant = reverse_op(genome)`) |
| fitness_evaluation | True | True | HIGH | Truth: rank is computed from each genome.<br>Evidence: line 6: A computed value depends on a candidate passed to a call. (`mutant = reverse_op(genome)`) |
| selection | False | False | LOW | Truth: No genome is chosen.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: An eval-built reversal operator produces a mutant from each genome.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No genomes are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no generation loop.<br>Evidence: No detector evidence. |

### `sf01_safe_ea` — safety

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | False | LOW | Truth: population is a list of bit genomes.<br>Evidence: No detector evidence. |
| fitness_evaluation | True | False | LOW | Truth: sort(key=sum) scores genomes.<br>Evidence: No detector evidence. |
| selection | True | False | LOW | Truth: After sorting, the best genome is chosen as the variation source.<br>Evidence: No detector evidence. |
| mutation | True | False | LOW | Truth: A copy of best has one gene set.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Only one parent is used.<br>Evidence: No detector evidence. |
| replacement | True | False | LOW | Truth: population[-1] (the worst) is overwritten by the variant.<br>Evidence: No detector evidence. |
| termination | True | False | LOW | Truth: Generations are bounded by range(10).<br>Evidence: No detector evidence. |

### `sf02_unsafe_ea_eval` — safety

Safety: **UNSAFE** (without EA: UNSAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | MEDIUM | Truth: population is a list of candidates.<br>Evidence: line 7: A comprehension invokes a computation on each element of a collection; generator and call source locations are retained. (`[(eval(expr, {'x': ind}), ind) for ind in population]`) |
| fitness_evaluation | True | True | MEDIUM | Truth: A user expression is evaluated per candidate as fitness.<br>Evidence: line 7: A call consumes the comprehension's candidate variable while iterating a collection. (`eval(expr, {'x': ind})`) |
| selection | True | False | LOW | Truth: Scored candidates are sorted and the best three kept.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Survivors are duplicated unchanged.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | True | False | LOW | Truth: population is reassigned to the duplicated survivors.<br>Evidence: No detector evidence. |
| termination | True | True | HIGH | Truth: Generations are bounded by range(5).<br>Evidence: line 6: The evolutionary loop iterates a finite built-in range or literal collection. (`for gen in range(5):
    scored = [(eval(expr, {'x': ind}), ind) for ind in population]
    scored.sort(key=lambda pair: pair[0])
    population = [ind for _, ind in scored[:3]] * 2`) |

### `sf03_unsafe_ea_subprocess` — safety

Safety: **UNSAFE** (without EA: UNSAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: population is a list of candidates.<br>Evidence: line 8: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for ind in population:
    cost = abs(ind[0] - 0.5)
    ind[0] += random.uniform(-0.1, 0.1)`) |
| fitness_evaluation | True | True | HIGH | Truth: cost is computed per candidate.<br>Evidence: line 9: A computed value depends on a candidate passed to a call. (`cost = abs(ind[0] - 0.5)`) |
| selection | False | False | LOW | Truth: No candidate is chosen.<br>Evidence: No detector evidence. |
| mutation | True | True | HIGH | Truth: Uniform noise is added to each candidate in place.<br>Evidence: line 10: A candidate or its alias is modified through an element or attribute update. (`ind[0] += random.uniform(-0.1, 0.1)`) |
| crossover | False | False | LOW | Truth: No candidates are combined.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The population is not rebuilt.<br>Evidence: No detector evidence. |
| termination | True | True | HIGH | Truth: Generations are bounded by range(5).<br>Evidence: line 7: The evolutionary loop iterates a finite built-in range or literal collection. (`for gen in range(5):
    for ind in population:
        cost = abs(ind[0] - 0.5)
        ind[0] += random.uniform(-0.1, 0.1)
    os.system(command)`) |

### `sf04_safe_non_ea` — safety

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | True | MEDIUM | Truth: Plain string formatting with no optimisation process.<br>Evidence: line 3: A comprehension invokes a computation on each element of a collection; generator and call source locations are retained. (`[f'Hello, {n.title()}!' for n in names]`) |
| fitness_evaluation | False | True | MEDIUM | Truth: Plain string formatting with no optimisation process.<br>Evidence: line 3: A call consumes the comprehension's candidate variable while iterating a collection. (`n.title()`) |
| selection | False | False | LOW | Truth: Plain string formatting with no optimisation process.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Plain string formatting with no optimisation process.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Plain string formatting with no optimisation process.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Plain string formatting with no optimisation process.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Plain string formatting with no optimisation process.<br>Evidence: No detector evidence. |

### `sf05_unsafe_non_ea` — safety

Safety: **UNSAFE** (without EA: UNSAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: Executes user-supplied code; no EA structure.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: Executes user-supplied code; no EA structure.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: Executes user-supplied code; no EA structure.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Executes user-supplied code; no EA structure.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Executes user-supplied code; no EA structure.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Executes user-supplied code; no EA structure.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Executes user-supplied code; no EA structure.<br>Evidence: No detector evidence. |

## Safety separation

- `n01_matrix_multiply`: expected SAFE; observed SAFE with EA / SAFE without EA; unchanged=True.
- `x03_eval_built_operator`: expected UNSAFE; observed UNSAFE with EA / UNSAFE without EA; unchanged=True.
- `sf01_safe_ea`: expected SAFE; observed SAFE with EA / SAFE without EA; unchanged=True.
- `sf02_unsafe_ea_eval`: expected UNSAFE; observed UNSAFE with EA / UNSAFE without EA; unchanged=True.
- `sf03_unsafe_ea_subprocess`: expected UNSAFE; observed UNSAFE with EA / UNSAFE without EA; unchanged=True.
- `sf04_safe_non_ea`: expected SAFE; observed SAFE with EA / SAFE without EA; unchanged=True.
- `sf05_unsafe_non_ea`: expected UNSAFE; observed UNSAFE with EA / UNSAFE without EA; unchanged=True.
- Invalid-syntax UNKNOWN harness status: UNKNOWN without EA, UNKNOWN with EA; unchanged=True. UNKNOWN here is the benchmark harness status for invalid syntax; the safety API raises before producing a verdict.
- All 51 programs: verdict identical with and without EA inference = True (changed: none).

Overall benchmark safety-independence checks: **PASS**.
