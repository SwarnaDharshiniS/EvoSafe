# EvoSafe EA Inference: Baseline Comparison

- Baseline programs: **2562**
- Current programs: **2562**
- Paired program names: **2562**
- Paired successful analyses: **2545**
- Baseline safety verdicts: `{"CONDITIONALLY_SAFE": 448, "SAFE": 1667, "UNKNOWN": 17, "UNSAFE": 430}`
- Current safety verdicts: `{"CONDITIONALLY_SAFE": 447, "SAFE": 1667, "UNKNOWN": 17, "UNSAFE": 431}`
- Safety verdict changes among paired programs: **1**
- Corpus-wide role precision/recall/F1: **not computed**; role-level ground truth is not available.

## Overall role comparison

| Role | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---|---|
| population | 413 | 886 | +473 | `{"HIGH": 411, "MEDIUM": 2}` | `{"HIGH": 652, "MEDIUM": 234}` |
| fitness_evaluation | 335 | 625 | +290 | `{"HIGH": 331, "MEDIUM": 4}` | `{"HIGH": 325, "MEDIUM": 300}` |
| selection | 63 | 153 | +90 | `{"HIGH": 9, "MEDIUM": 54}` | `{"HIGH": 18, "MEDIUM": 135}` |
| mutation | 106 | 457 | +351 | `{"HIGH": 98, "MEDIUM": 8}` | `{"HIGH": 448, "MEDIUM": 9}` |
| crossover | 81 | 289 | +208 | `{"HIGH": 3, "MEDIUM": 78}` | `{"HIGH": 14, "MEDIUM": 275}` |
| replacement | 31 | 92 | +61 | `{"HIGH": 31}` | `{"HIGH": 91, "MEDIUM": 1}` |
| termination | 106 | 203 | +97 | `{"HIGH": 46, "MEDIUM": 60}` | `{"HIGH": 57, "MEDIUM": 146}` |

## Comparison by corpus stratum

### population

| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---:|---|---|
| DEAP | 55 | 24 | 49 | +25 | `{"HIGH": 24}` | `{"HIGH": 32, "MEDIUM": 17}` |
| PyGAD | 72 | 6 | 3 | -3 | `{"HIGH": 6}` | `{"HIGH": 3}` |
| pymoo | 146 | 11 | 13 | +2 | `{"HIGH": 11}` | `{"HIGH": 13}` |
| mealpy | 67 | 3 | 12 | +9 | `{"HIGH": 3}` | `{"HIGH": 12}` |
| generic_ea | 2 | 1 | 2 | +1 | `{"HIGH": 1}` | `{"HIGH": 1, "MEDIUM": 1}` |
| generic_educational_python | 1565 | 278 | 596 | +318 | `{"HIGH": 276, "MEDIUM": 2}` | `{"HIGH": 438, "MEDIUM": 158}` |
| safety_oriented_corpus | 620 | 89 | 203 | +114 | `{"HIGH": 89}` | `{"HIGH": 151, "MEDIUM": 52}` |

### fitness_evaluation

| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---:|---|---|
| DEAP | 55 | 21 | 34 | +13 | `{"HIGH": 21}` | `{"HIGH": 20, "MEDIUM": 14}` |
| PyGAD | 72 | 6 | 3 | -3 | `{"HIGH": 5, "MEDIUM": 1}` | `{"HIGH": 3}` |
| pymoo | 146 | 10 | 12 | +2 | `{"HIGH": 10}` | `{"HIGH": 12}` |
| mealpy | 67 | 3 | 7 | +4 | `{"HIGH": 3}` | `{"HIGH": 7}` |
| generic_ea | 2 | 1 | 2 | +1 | `{"HIGH": 1}` | `{"HIGH": 1, "MEDIUM": 1}` |
| generic_educational_python | 1565 | 221 | 416 | +195 | `{"HIGH": 219, "MEDIUM": 2}` | `{"HIGH": 212, "MEDIUM": 204}` |
| safety_oriented_corpus | 620 | 72 | 143 | +71 | `{"HIGH": 71, "MEDIUM": 1}` | `{"HIGH": 68, "MEDIUM": 75}` |

### selection

| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---:|---|---|
| DEAP | 55 | 7 | 22 | +15 | `{"HIGH": 1, "MEDIUM": 6}` | `{"HIGH": 1, "MEDIUM": 21}` |
| PyGAD | 72 | 1 | 1 | +0 | `{"MEDIUM": 1}` | `{"MEDIUM": 1}` |
| pymoo | 146 | 0 | 1 | +1 | `{}` | `{"MEDIUM": 1}` |
| mealpy | 67 | 0 | 0 | +0 | `{}` | `{}` |
| generic_ea | 2 | 0 | 0 | +0 | `{}` | `{}` |
| generic_educational_python | 1565 | 40 | 97 | +57 | `{"HIGH": 6, "MEDIUM": 34}` | `{"HIGH": 14, "MEDIUM": 83}` |
| safety_oriented_corpus | 620 | 15 | 32 | +17 | `{"HIGH": 2, "MEDIUM": 13}` | `{"HIGH": 3, "MEDIUM": 29}` |

### mutation

| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---:|---|---|
| DEAP | 55 | 5 | 31 | +26 | `{"HIGH": 3, "MEDIUM": 2}` | `{"HIGH": 28, "MEDIUM": 3}` |
| PyGAD | 72 | 1 | 1 | +0 | `{"HIGH": 1}` | `{"HIGH": 1}` |
| pymoo | 146 | 1 | 6 | +5 | `{"HIGH": 1}` | `{"HIGH": 6}` |
| mealpy | 67 | 0 | 8 | +8 | `{}` | `{"HIGH": 8}` |
| generic_ea | 2 | 0 | 1 | +1 | `{}` | `{"HIGH": 1}` |
| generic_educational_python | 1565 | 77 | 303 | +226 | `{"HIGH": 72, "MEDIUM": 5}` | `{"HIGH": 299, "MEDIUM": 4}` |
| safety_oriented_corpus | 620 | 22 | 107 | +85 | `{"HIGH": 21, "MEDIUM": 1}` | `{"HIGH": 105, "MEDIUM": 2}` |

### crossover

| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---:|---|---|
| DEAP | 55 | 8 | 19 | +11 | `{"HIGH": 3, "MEDIUM": 5}` | `{"HIGH": 3, "MEDIUM": 16}` |
| PyGAD | 72 | 0 | 0 | +0 | `{}` | `{}` |
| pymoo | 146 | 0 | 4 | +4 | `{}` | `{"MEDIUM": 4}` |
| mealpy | 67 | 0 | 4 | +4 | `{}` | `{"MEDIUM": 4}` |
| generic_ea | 2 | 0 | 1 | +1 | `{}` | `{"MEDIUM": 1}` |
| generic_educational_python | 1565 | 54 | 204 | +150 | `{"MEDIUM": 54}` | `{"HIGH": 10, "MEDIUM": 194}` |
| safety_oriented_corpus | 620 | 19 | 55 | +36 | `{"MEDIUM": 19}` | `{"HIGH": 1, "MEDIUM": 54}` |

### replacement

| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---:|---|---|
| DEAP | 55 | 4 | 18 | +14 | `{"HIGH": 4}` | `{"HIGH": 18}` |
| PyGAD | 72 | 0 | 0 | +0 | `{}` | `{}` |
| pymoo | 146 | 3 | 5 | +2 | `{"HIGH": 3}` | `{"HIGH": 5}` |
| mealpy | 67 | 0 | 0 | +0 | `{}` | `{}` |
| generic_ea | 2 | 0 | 0 | +0 | `{}` | `{}` |
| generic_educational_python | 1565 | 16 | 49 | +33 | `{"HIGH": 16}` | `{"HIGH": 48, "MEDIUM": 1}` |
| safety_oriented_corpus | 620 | 8 | 20 | +12 | `{"HIGH": 8}` | `{"HIGH": 20}` |

### termination

| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |
|---|---:|---:|---:|---:|---|---|
| DEAP | 55 | 19 | 25 | +6 | `{"HIGH": 11, "MEDIUM": 8}` | `{"HIGH": 14, "MEDIUM": 11}` |
| PyGAD | 72 | 0 | 0 | +0 | `{}` | `{}` |
| pymoo | 146 | 1 | 1 | +0 | `{"HIGH": 1}` | `{"HIGH": 1}` |
| mealpy | 67 | 0 | 0 | +0 | `{}` | `{}` |
| generic_ea | 2 | 1 | 2 | +1 | `{"HIGH": 1}` | `{"HIGH": 1, "MEDIUM": 1}` |
| generic_educational_python | 1565 | 63 | 129 | +66 | `{"HIGH": 24, "MEDIUM": 39}` | `{"HIGH": 32, "MEDIUM": 97}` |
| safety_oriented_corpus | 620 | 21 | 44 | +23 | `{"HIGH": 8, "MEDIUM": 13}` | `{"HIGH": 8, "MEDIUM": 36}` |

## Audited programs and evidence review

### `dataset/deap/ga/onemax.py`

Safety verdict: **CONDITIONALLY_SAFE**

Explicit population/evaluate/select/mate/mutate registrations, map callback use, two-parent offspring call, pop[:] replacement, and generation/convergence loop are visible in source.

Detected: population, fitness_evaluation, selection, mutation, crossover, replacement, termination; potential missed in-source roles: none; false-positive candidates for manual follow-up: none. 

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | MEDIUM | 45: registered_role — toolbox.register('population', tools.initRepeat, list, toolbox.individual)<br>77: registered_dispatch — toolbox.population(n=300)<br>112: registered_candidate_iteration — for child1, child2 in zip(offspring[::2], offspring[1::2]):
    if random.random() < CXPB:
        toolbox.mate(child1, child2)
        del child1.fitness.values
        del child2.fitness.values<br>123: registered_candidate_iteration — for mutant in offspring:
    if random.random() < MUTPB:
        toolbox.mutate(mutant)
        del mutant.fitness.values |
| fitness_evaluation | True | MEDIUM | 49: registered_callback_summary — sum(individual)<br>55: registered_role — toolbox.register('evaluate', evalOneMax)<br>88: registered_dispatch — map(toolbox.evaluate, pop)<br>88: registered_callable_reference — toolbox.evaluate |
| selection | True | MEDIUM | 68: registered_role — toolbox.register('select', tools.selTournament, tournsize=3)<br>107: registered_callable_reference — toolbox.select<br>107: registered_dispatch — toolbox.select(pop, len(pop))<br>131: candidate_filter — [ind for ind in offspring if not ind.fitness.valid] |
| mutation | True | MEDIUM | 62: registered_role — toolbox.register('mutate', tools.mutFlipBit, indpb=0.05)<br>127: registered_callable_reference — toolbox.mutate<br>127: registered_dispatch — toolbox.mutate(mutant) |
| crossover | True | MEDIUM | 58: registered_role — toolbox.register('mate', tools.cxTwoPoint)<br>116: multi_parent_call — toolbox.mate(child1, child2)<br>116: registered_callable_reference — toolbox.mate<br>116: registered_dispatch — toolbox.mate(child1, child2) |
| replacement | True | HIGH | 139: population_slice_replacement — pop[:] = offspring<br>139: survivor_replacement — pop[:] = offspring |
| termination | True | MEDIUM | 101: loop_termination — while max(fits) < 100 and g < 1000:
    g = g + 1
    print('-- Generation %i --' % g)
    offspring = toolbox.select(pop, len(pop))
    offspring = list(map(toolbox.clone, offspring))
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
    for mutant in offspring:
        if random.random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    print('  Evaluated %i individuals' % len(invalid_ind))
    pop[:] = offspring
    fits = [ind.fitness.values[0] for ind in pop]
    length = len(pop)
    mean = sum(fits) / length
    sum2 = sum((x * x for x in fits))
    std = abs(sum2 / length - mean ** 2) ** 0.5
    print('  Min %s' % min(fits))
    print('  Max %s' % max(fits))
    print('  Avg %s' % mean)
    print('  Std %s' % std) |

### `Python/genetic_algorithm/basic_string.py`

Safety verdict: **UNSAFE**

Source code has candidate initialization, evaluate() scoring, sorted/ranked scores and random parent indexing, mutate()/crossover() helper calls, population clear/extend rebuild, and a convergence exit inside while True.

Detected: population, fitness_evaluation, termination; potential missed in-source roles: selection, mutation, crossover, replacement; false-positive candidates for manual follow-up: none. 

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | MEDIUM | 159: candidate_comprehension — [evaluate(item, target) for item in population] |
| fitness_evaluation | True | MEDIUM | 32: helper_fitness_evaluation — float(score)<br>159: comprehension_candidate_call — evaluate(item, target)<br>159: helper_call_site — evaluate(item, target) |
| selection | False | LOW | — |
| mutation | False | LOW | — |
| crossover | False | LOW | — |
| replacement | False | LOW | — |
| termination | True | MEDIUM | 141: loop_termination — while True:
    generation += 1
    total_population += len(population)
    population_score = [evaluate(item, target) for item in population]
    population_score = sorted(population_score, key=lambda x: x[1], reverse=True)
    if population_score[0][0] == target:
        return (generation, total_population, population_score[0][0])
    if debug and generation % 10 == 0:
        print(f'\nGeneration: {generation}\nTotal Population:{total_population}\nBest score: {population_score[0][1]}\nBest string: {population_score[0][0]}')
    population_best = population[:int(N_POPULATION / 3)]
    population.clear()
    population.extend(population_best)
    population_score = [(item, score / len(target)) for item, score in population_score]
    for i in range(N_SELECTED):
        population.extend(select(population_score[int(i)], population_score, genes))
        if len(population) > N_POPULATION:
            break |

### `dataset/non_deap/pygad/example_custom_operators.py`

Safety verdict: **CONDITIONALLY_SAFE**

Defines fitness_func, parent_selection_func, crossover_func, and mutation_func; callback wiring is passed to pygad.GA and execution is delegated to ga_instance.run(). Population initialization and generation termination are framework-managed.

Detected: population, fitness_evaluation, selection, mutation; potential missed in-source roles: selection, crossover; false-positive candidates for manual follow-up: population, fitness_evaluation, selection. 
Evidence caveat for `mutation`: One mutation finding is valid at the offspring indexed update; another is just copying selected parent rows.

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | HIGH | 31: candidate_iteration — for parent_num in range(num_parents):
    parents[parent_num, :] = ga_instance.population[fitness_sorted[parent_num], :].copy()<br>56: candidate_iteration — for chromosome_idx in range(offspring.shape[0]):
    random_gene_idx = numpy.random.choice(range(offspring.shape[1]))
    offspring[chromosome_idx, random_gene_idx] += numpy.random.random() |
| fitness_evaluation | True | HIGH | 32: candidate_dependent_call — parents[parent_num, :] = ga_instance.population[fitness_sorted[parent_num], :].copy() |
| selection | True | MEDIUM | 58: rank_or_filter — numpy.random.choice(range(offspring.shape[1])) |
| mutation | True | HIGH | 32: candidate_modification — parents[parent_num, :] = ga_instance.population[fitness_sorted[parent_num], :].copy()<br>60: candidate_modification — offspring[chromosome_idx, random_gene_idx] += numpy.random.random() |
| crossover | False | LOW | — |
| replacement | False | LOW | — |
| termination | False | LOW | — |

### `dataset/non_deap/pymoo/algorithms/moo/nsga2/nsga2_custom.py`

Safety verdict: **SAFE**

Defines a custom sampler, problem _evaluate callback, two-parent crossover, and mutation; NSGA2 selection/replacement and minimize termination are framework-managed.

Detected: population, fitness_evaluation, selection, mutation, replacement, termination; potential missed in-source roles: crossover; false-positive candidates for manual follow-up: fitness_evaluation, selection, replacement, termination. 
Evidence caveat for `mutation`: Valid mutation evidence at the MyMutation assignment is mixed with sampler/crossover array writes.

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | HIGH | 37: candidate_iteration — for i in range(n_samples):
    X[i, 0] = ''.join([np.random.choice(problem.ALPHABET) for _ in range(problem.n_characters)])<br>68: candidate_iteration — for i in range(problem.n_characters):
    if np.random.random() < 0.5:
        off_a[i] = a[i]
        off_b[i] = b[i]
    else:
        off_a[i] = b[i]
        off_b[i] = a[i]<br>87: candidate_iteration — for i in range(len(X)):
    if np.random.random() < 0.5:
        X[i, 0] = ''.join(np.array([e for e in X[i, 0]])[np.random.permutation(problem.n_characters)]) |
| fitness_evaluation | True | HIGH | 89: candidate_dependent_call — X[i, 0] = ''.join(np.array([e for e in X[i, 0]])[np.random.permutation(problem.n_characters)]) |
| selection | True | MEDIUM | 38: rank_or_filter — np.random.choice(problem.ALPHABET) |
| mutation | True | HIGH | 38: candidate_modification — X[i, 0] = ''.join([np.random.choice(problem.ALPHABET) for _ in range(problem.n_characters)])<br>70: candidate_modification — off_a[i] = a[i]<br>71: candidate_modification — off_b[i] = b[i]<br>73: candidate_modification — off_a[i] = b[i]<br>74: candidate_modification — off_b[i] = a[i]<br>89: candidate_modification — X[i, 0] = ''.join(np.array([e for e in X[i, 0]])[np.random.permutation(problem.n_characters)]) |
| crossover | False | LOW | — |
| replacement | True | HIGH | 38: survivor_replacement — X[i, 0] = ''.join([np.random.choice(problem.ALPHABET) for _ in range(problem.n_characters)])<br>89: survivor_replacement — X[i, 0] = ''.join(np.array([e for e in X[i, 0]])[np.random.permutation(problem.n_characters)]) |
| termination | True | HIGH | 59: loop_termination — for k in range(n_matings):
    a, b = (X[0, k, 0], X[1, k, 0])
    off_a = ['_'] * problem.n_characters
    off_b = ['_'] * problem.n_characters
    for i in range(problem.n_characters):
        if np.random.random() < 0.5:
            off_a[i] = a[i]
            off_b[i] = b[i]
        else:
            off_a[i] = b[i]
            off_b[i] = a[i]
    Y[0, k, 0], Y[1, k, 0] = (''.join(off_a), ''.join(off_b)) |

### `dataset/non_deap/mealpy/applications/keras/mha-hybrid-mlp-classification.py`

Safety verdict: **SAFE**

The source supplies fitness_function to a Mealpy GWO optimizer and calls solve(); GWO is a population-based metaheuristic, but the evolutionary-role interpretation of its framework-managed internals is intentionally uncertain. The weight_sizes/reshape loop is model decoding, not population iteration.

Detected: population, fitness_evaluation; potential missed in-source roles: fitness_evaluation; false-positive candidates for manual follow-up: population, fitness_evaluation. 
Category note: population-based metaheuristic; EA taxonomy applicability requires review.

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | HIGH | 37: candidate_comprehension — [np.size(w) for w in self.model.get_weights()]<br>53: candidate_comprehension — [(w.shape, np.size(w)) for w in self.model.get_weights()]<br>57: candidate_iteration — for ws in weight_sizes:
    temp = np.reshape(solution[cut_point:cut_point + ws[1]], ws[0])
    weights.append(temp)
    cut_point += ws[1] |
| fitness_evaluation | True | HIGH | 37: comprehension_candidate_call — np.size(w)<br>53: comprehension_candidate_call — np.size(w)<br>58: candidate_dependent_call — temp = np.reshape(solution[cut_point:cut_point + ws[1]], ws[0]) |
| selection | False | LOW | — |
| mutation | False | LOW | — |
| crossover | False | LOW | — |
| replacement | False | LOW | — |
| termination | False | LOW | — |

### `Python/machine_learning/astar.py`

Safety verdict: **CONDITIONALLY_SAFE**

A* graph search manages open/closed frontiers, chooses the minimum f-score node, updates path-cost/heuristic fields, and appends neighbors. These are graph-search operations, not evolutionary roles.

Detected: population, selection, mutation, crossover, replacement, termination; potential missed in-source roles: none; false-positive candidates for manual follow-up: population, selection, mutation, crossover, replacement, termination. 

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | HIGH | 114: candidate_iteration — for n in world.get_neighbours(current):
    for c in _closed:
        if c == n:
            continue
    n.g = current.g + 1
    x1, y1 = n.position
    x2, y2 = goal.position
    n.h = (y2 - y1) ** 2 + (x2 - x1) ** 2
    n.f = n.h + n.g
    for c in _open:
        if c == n and c.f < n.f:
            continue
    _open.append(n)<br>146: candidate_iteration — for i in s:
    world.w[i] = 1 |
| fitness_evaluation | False | LOW | — |
| selection | True | MEDIUM | 109: rank_or_filter — np.argmin([n.f for n in _open]) |
| mutation | True | HIGH | 118: candidate_modification — n.g = current.g + 1<br>121: candidate_modification — n.h = (y2 - y1) ** 2 + (x2 - x1) ** 2<br>122: candidate_modification — n.f = n.h + n.g<br>147: candidate_modification — world.w[i] = 1 |
| crossover | True | MEDIUM | 121: multi_parent_recombination — (y2 - y1) ** 2 + (x2 - x1) ** 2 |
| replacement | True | HIGH | 127: offspring_insertion — _open.append(n) |
| termination | True | MEDIUM | 108: loop_termination — while _open:
    min_f = np.argmin([n.f for n in _open])
    current = _open[min_f]
    _closed.append(_open.pop(min_f))
    if current == goal:
        break
    for n in world.get_neighbours(current):
        for c in _closed:
            if c == n:
                continue
        n.g = current.g + 1
        x1, y1 = n.position
        x2, y2 = goal.position
        n.h = (y2 - y1) ** 2 + (x2 - x1) ** 2
        n.f = n.h + n.g
        for c in _open:
            if c == n and c.f < n.f:
                continue
        _open.append(n) |

### `dataset/benign/algorithms/data_structures/arrays/sudoku_solver.py`

Safety verdict: **UNSAFE**

The file implements constraint propagation, unit construction, candidate filtering, and recursive search for Sudoku; list comprehensions, filtering, concatenation, and iteration are not EA roles.

Detected: population, fitness_evaluation, selection, crossover, replacement, termination; potential missed in-source roles: none; false-positive candidates for manual follow-up: population, fitness_evaluation, selection, crossover, replacement, termination. 

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | MEDIUM | 36: candidate_comprehension — [cross(rows, c) for c in cols]<br>37: candidate_comprehension — [cross(r, cols) for r in rows]<br>48: candidate_comprehension — (len(units[s]) == 3 for s in squares)<br>49: candidate_comprehension — (len(peers[s]) == 20 for s in squares)<br>92: candidate_comprehension — (eliminate(values, s, d2) for d2 in other_values)<br>111: candidate_comprehension — (eliminate(values, s2, d2) for s2 in peers[s])<br>128: candidate_comprehension — (len(values[s]) for s in squares)<br>132: candidate_comprehension — (values[r + c].center(width) + ('&#124;' if c in '36' else '') for c in cols)<br>162: candidate_comprehension — (len(values[s]) == 1 for s in squares)<br>165: candidate_comprehension — ((len(values[s]), s) for s in squares if len(values[s]) > 1)<br>166: candidate_comprehension — (search(assign(values.copy(), s, d)) for d in values[s])<br>188: candidate_comprehension — [time_solve(grid) for grid in grids]<br>204: candidate_comprehension — (unitsolved(unit) for unit in unitlist)<br>225: candidate_comprehension — (values[s] if len(values[s]) == 1 else '.' for s in squares) |
| fitness_evaluation | True | MEDIUM | 36: comprehension_candidate_call — cross(rows, c)<br>37: comprehension_candidate_call — cross(r, cols)<br>48: comprehension_candidate_call — len(units[s])<br>49: comprehension_candidate_call — len(peers[s])<br>71: helper_call_site — grid_values(grid)<br>83: helper_fitness_evaluation — dict(zip(squares, chars))<br>83: helper_fitness_evaluation — zip(squares, chars)<br>92: comprehension_candidate_call — eliminate(values, s, d2)<br>111: comprehension_candidate_call — eliminate(values, s2, d2)<br>128: comprehension_candidate_call — len(values[s])<br>133: comprehension_candidate_call — values[r + c].center(width)<br>145: helper_call_site — search(parse_grid(grid))<br>162: comprehension_candidate_call — len(values[s])<br>165: comprehension_candidate_call — len(values[s])<br>166: comprehension_candidate_call — search(assign(values.copy(), s, d))<br>166: helper_call_site — search(assign(values.copy(), s, d))<br>166: comprehension_candidate_call — assign(values.copy(), s, d)<br>166: helper_fitness_evaluation — values.copy()<br>166: helper_fitness_evaluation — values.copy()<br>166: helper_fitness_evaluation — values.copy()<br>166: helper_fitness_evaluation — values.copy()<br>166: helper_fitness_evaluation — values.copy()<br>178: helper_call_site — solve(grid)<br>182: helper_call_site — grid_values(grid)<br>188: comprehension_candidate_call — time_solve(grid)<br>204: comprehension_candidate_call — unitsolved(unit)<br>225: comprehension_candidate_call — len(values[s]) |
| selection | True | MEDIUM | 40: candidate_filter — [u for u in unitlist if s in u]<br>128: rank_or_filter — max((len(values[s]) for s in squares))<br>165: rank_or_filter — min(((len(values[s]), s) for s in squares if len(values[s]) > 1))<br>165: candidate_filter — ((len(values[s]), s) for s in squares if len(values[s]) > 1)<br>221: rank_or_filter — random.choice(values[s])<br>223: candidate_filter — [values[s] for s in squares if len(values[s]) == 1] |
| mutation | False | LOW | — |
| crossover | True | MEDIUM | 36: multi_parent_recombination — [cross(rows, c) for c in cols] + [cross(r, cols) for r in rows]<br>133: multi_parent_recombination — values[r + c].center(width) + ('&#124;' if c in '36' else '')<br>133: multi_parent_recombination — r + c |
| replacement | True | HIGH | 35: population_reconstruction — unitlist = [cross(rows, c) for c in cols] + [cross(r, cols) for r in rows] + [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]<br>105: survivor_replacement — values[s] = values[s].replace(d, '') |
| termination | True | MEDIUM | 71: loop_termination — for s, d in grid_values(grid).items():
    if d in digits and (not assign(values, s, d)):
        return False |

### `dataset/benign/algorithms/data_structures/heap/binomial_heap.py`

Safety verdict: **UNSAFE**

The file implements binomial-heap tree merging, linking, insertion, and deletion. Indexed link updates, list merging, and loops are data-structure operations, not mutation/crossover/replacement roles in an EA.

Detected: population, fitness_evaluation, mutation, crossover, replacement, termination; potential missed in-source roles: none; false-positive candidates for manual follow-up: population, fitness_evaluation, mutation, crossover, replacement, termination. 

| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |
|---|---|---|---|
| population | True | HIGH | 164: candidate_iteration — for i in range(len(combined_roots_list) - 1):
    if combined_roots_list[i][1] != combined_roots_list[i + 1][1]:
        combined_roots_list[i][0].parent = combined_roots_list[i + 1][0]
        combined_roots_list[i + 1][0].left = combined_roots_list[i][0]<br>396: candidate_comprehension — ('-' * level + str(value) for value, level in preorder_heap) |
| fitness_evaluation | True | MEDIUM | 396: comprehension_candidate_call — str(value) |
| selection | False | LOW | — |
| mutation | True | HIGH | 166: candidate_modification — combined_roots_list[i][0].parent = combined_roots_list[i + 1][0]<br>167: candidate_modification — combined_roots_list[i + 1][0].left = combined_roots_list[i][0] |
| crossover | True | MEDIUM | 396: multi_parent_recombination — '-' * level + str(value) |
| replacement | True | HIGH | 158: offspring_insertion — combined_roots_list.append((i, True)) |
| termination | True | MEDIUM | 156: loop_termination — while i or j:
    if i and (not j or i.left_tree_size < j.left_tree_size):
        combined_roots_list.append((i, True))
        i = i.parent
    else:
        combined_roots_list.append((j, False))
        j = j.parent |

## Safety verdict changes

- `tests/test_ea_inference.py`: CONDITIONALLY_SAFE → UNSAFE. The test source changed after the prior run and now imports ast for new tests; the existing capability analyzer classifies the ast module as DYN. This is corpus-source drift, not an EA detector changing the verdict.
## Interpretation

Detection deltas are not automatically accuracy gains. Review evidence for source-role correspondence, especially medium-confidence facts tied to callback configuration, generic loop operations, indexed assignments, and collection updates. The framework directories are provenance labels, not role-level ground truth.
