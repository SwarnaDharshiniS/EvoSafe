# EvoSafe controlled seven-role EA benchmark

- Labeled programs: **18**
- Metrics are benchmark-only and are not merged with unlabeled corpus results.
- Ground truth is explicit per program for all seven roles; each role includes a rationale whether positive or negative.

## Per-role metrics

| Role | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| population | 13 | 0 | 0 | 5 | 1.000 | 1.000 | 1.000 |
| fitness_evaluation | 13 | 0 | 0 | 5 | 1.000 | 1.000 | 1.000 |
| selection | 8 | 0 | 0 | 10 | 1.000 | 1.000 | 1.000 |
| mutation | 8 | 0 | 0 | 10 | 1.000 | 1.000 | 1.000 |
| crossover | 2 | 0 | 0 | 16 | 1.000 | 1.000 | 1.000 |
| replacement | 5 | 0 | 0 | 13 | 1.000 | 1.000 | 1.000 |
| termination | 4 | 0 | 0 | 14 | 1.000 | 1.000 | 1.000 |

**Macro average** over 7 roles: precision **1.000**, recall **1.000**, F1 **1.000**.

## Program-level findings

### `direct_ea` — direct_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A collection of candidate vectors is iterated and updated across generations.<br>Evidence: line 5: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in population:
    fitness_value = sum(individual)`)<br>line 9: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in selected:
    child = individual.copy()
    child[0] += random.randint(0, 1)
    offspring.append(child)`)<br>line 13: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for parent_a, parent_b in zip(selected, selected[1:]):
    child = parent_a[:1] + parent_b[1:]
    offspring.append(child)`)<br>line 18: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in population:
    fitness_value = sum(individual)`) |
| fitness_evaluation | True | True | HIGH | Truth: Each candidate is scored by sum(candidate).<br>Evidence: line 6: A computed value depends on a candidate passed to a call. (`fitness_value = sum(individual)`)<br>line 19: A computed value depends on a candidate passed to a call. (`fitness_value = sum(individual)`) |
| selection | True | True | HIGH | Truth: Candidates are ranked by score and truncated to the best subset.<br>Evidence: line 7: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`sorted(population, key=sum, reverse=True)`) |
| mutation | True | True | HIGH | Truth: A copied candidate gene is changed using a random value.<br>Evidence: line 11: A candidate or its alias is modified through an element or attribute update. (`child[0] += random.randint(0, 1)`) |
| crossover | True | True | HIGH | Truth: A child combines slices from two distinct parents.<br>Evidence: line 14: A combined representation is constructed from at least two candidate sources. (`parent_a[:1] + parent_b[1:]`) |
| replacement | True | True | HIGH | Truth: The old population is replaced by selected parents plus offspring.<br>Evidence: line 16: A candidate collection is replaced by a newly composed collection. (`population = selected + offspring`) |
| termination | True | True | HIGH | Truth: The generation process is bounded by range(3).<br>Evidence: line 17: The evolutionary loop iterates a finite built-in range or literal collection. (`for generation in range(3):
    for individual in population:
        fitness_value = sum(individual)`) |

### `helper_function_ea` — helper_function_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A candidate collection is traversed by candidate and passed into helpers.<br>Evidence: line 14: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    fitness_value = score(candidate)`)<br>line 17: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in selected:
    child = mutate(candidate.copy())`) |
| fitness_evaluation | True | True | MEDIUM | Truth: score(candidate) computes a candidate-dependent length score.<br>Evidence: line 4: The helper returns a call result whose arguments include candidate-derived values. (`len(candidate)`)<br>line 15: Local helper 'score' receives values structurally linked to the EA role inputs. (`score(candidate)`) |
| selection | True | True | MEDIUM | Truth: select(pool) ranks candidates and returns a subset.<br>Evidence: line 7: The helper returns a slice of an argument-derived collection. (`sorted(pool, key=len)[:2]`)<br>line 16: Local helper 'select' receives values structurally linked to the EA role inputs. (`select(population)`) |
| mutation | True | True | MEDIUM | Truth: mutate(candidate) changes a copied candidate gene and returns the changed candidate.<br>Evidence: line 10: The helper writes an element or attribute of its candidate argument. (`candidate[0] = 1 - candidate[0]`)<br>line 18: Local helper 'mutate' receives values structurally linked to the EA role inputs. (`mutate(candidate.copy())`) |
| crossover | False | False | LOW | Truth: There is no two-parent recombination, population replacement, or generation/process termination construct in this helper example.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: There is no two-parent recombination, population replacement, or generation/process termination construct in this helper example.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: There is no two-parent recombination, population replacement, or generation/process termination construct in this helper example.<br>Evidence: No detector evidence. |

### `alias_based_ea` — alias_based_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: source_pool, first_alias, second_alias, and population are chained aliases of the candidate collection.<br>Evidence: line 6: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in population:
    score = sum(individual)`)<br>line 14: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in population:
    score = sum(individual)`) |
| fitness_evaluation | True | True | HIGH | Truth: Each candidate is scored by sum(candidate).<br>Evidence: line 7: A computed value depends on a candidate passed to a call. (`score = sum(individual)`)<br>line 15: A computed value depends on a candidate passed to a call. (`score = sum(individual)`) |
| selection | True | True | HIGH | Truth: The population is ordered by candidate score and sliced to select parents.<br>Evidence: line 8: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`sorted(population, key=sum)`) |
| mutation | True | True | MEDIUM | Truth: child_alias is an alias of a copied candidate whose first element is changed.<br>Evidence: line 9: A population or selected candidate is copied. (`child = parents[0].copy()`)<br>line 11: The candidate copy (or an alias of it) is modified through an element or attribute write. (`child_alias[0] = 1`) |
| crossover | False | False | LOW | Truth: No operation combines information from two distinct parent candidates to create a child.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: A slice assignment replaces the aliased population contents with selected candidates and the child.<br>Evidence: line 12: A statically resolved alias of an inferred population is replaced by slice assignment. (`population[:] = parents + [child_alias]`)<br>line 12: An element of an inferred candidate collection is replaced. (`population[:] = parents + [child_alias]`) |
| termination | True | True | HIGH | Truth: The generation loop is bounded by range(2).<br>Evidence: line 13: The evolutionary loop iterates a finite built-in range or literal collection. (`for generation in range(2):
    for individual in population:
        score = sum(individual)`) |

### `generic_registration_dispatch` — generic_registration_dispatch

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A registered population factory is invoked through the same registry and its returned collection is iterated.<br>Evidence: line 17: A statically paired registration and invocation declares a population-producing role. (`registry.register('population', create_pool)`)<br>line 21: The registered callable is invoked and its result is assigned to a collection variable. (`registry.invoke_registered('population')`)<br>line 22: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    fitness_value = registry.invoke_registered('fitness_evaluation', candidate)`)<br>line 22: A registered EA operation consumes a loop element drawn from a collection. (`for candidate in population:
    fitness_value = registry.invoke_registered('fitness_evaluation', candidate)`)<br>line 25: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in selected:
    child = registry.invoke_registered('mutation', candidate.copy())`)<br>line 25: A registered EA operation consumes a loop element drawn from a collection. (`for candidate in selected:
    child = registry.invoke_registered('mutation', candidate.copy())`) |
| fitness_evaluation | True | True | MEDIUM | Truth: The registered evaluate function computes sum(candidate) and is dispatched for each candidate.<br>Evidence: line 7: The helper returns a call result whose arguments include candidate-derived values. (`sum(candidate)`)<br>line 18: Registration key 'fitness_evaluation' explicitly labels the callback as fitness_evaluation. (`registry.register('fitness_evaluation', evaluate)`)<br>line 23: This reference resolves to the callable registered under 'fitness_evaluation'. (`registry.invoke_registered`)<br>line 23: The registered callable is dispatched with arguments linked to the fitness_evaluation role. (`registry.invoke_registered('fitness_evaluation', candidate)`) |
| selection | True | True | MEDIUM | Truth: The registered choose function ranks the population and returns the top subset.<br>Evidence: line 10: The helper returns a slice of an argument-derived collection. (`sorted(pool, key=sum)[:2]`)<br>line 19: Registration key 'selection' explicitly labels the callback as selection. (`registry.register('selection', choose)`)<br>line 24: This reference resolves to the callable registered under 'selection'. (`registry.invoke_registered`)<br>line 24: The registered callable is dispatched with arguments linked to the selection role. (`registry.invoke_registered('selection', population)`) |
| mutation | True | True | MEDIUM | Truth: The registered mutate function changes a candidate gene and is dispatched on copied selected candidates.<br>Evidence: line 13: The helper writes an element or attribute of its candidate argument. (`candidate[0] = 1 - candidate[0]`)<br>line 20: Registration key 'mutation' explicitly labels the callback as mutation. (`registry.register('mutation', mutate)`)<br>line 26: This reference resolves to the callable registered under 'mutation'. (`registry.invoke_registered`)<br>line 26: The registered callable is dispatched with arguments linked to the mutation role. (`registry.invoke_registered('mutation', candidate.copy())`) |
| crossover | False | False | LOW | Truth: The registered operations do not combine two parents, replace the population, or control a generation termination condition.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The registered operations do not combine two parents, replace the population, or control a generation termination condition.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: The registered operations do not combine two parents, replace the population, or control a generation termination condition.<br>Evidence: No detector evidence. |

### `deap_style_registration` — deap_style_registration

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A population factory is registered and invoked to create the iterated candidates.<br>Evidence: line 16: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in population:
    fitness = toolbox.evaluate(individual)`)<br>line 16: A registered EA operation consumes a loop element drawn from a collection. (`for individual in population:
    fitness = toolbox.evaluate(individual)`)<br>line 19: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in selected:
    child = toolbox.mutate(individual.copy())`)<br>line 19: A registered EA operation consumes a loop element drawn from a collection. (`for individual in selected:
    child = toolbox.mutate(individual.copy())`) |
| fitness_evaluation | True | True | HIGH | Truth: The registered evaluate callable scores each candidate.<br>Evidence: line 4: The helper returns a call result whose arguments include candidate-derived values. (`sum(candidate)`)<br>line 12: Registration key 'evaluate' explicitly labels the callback as fitness_evaluation. (`toolbox.register('evaluate', evaluate)`)<br>line 17: A candidate is consumed by an evaluation-like computation inside collection iteration. (`toolbox.evaluate(individual)`)<br>line 17: This reference resolves to the callable registered under 'evaluate'. (`toolbox.evaluate`)<br>line 17: The registered callable is dispatched with arguments linked to the fitness_evaluation role. (`toolbox.evaluate(individual)`) |
| selection | True | True | MEDIUM | Truth: The registered select callable sorts the population by the evaluation key.<br>Evidence: line 13: Registered callable 'sorted' is a builtin ranking/filtering function applied to the population. (`toolbox.register('select', sorted)`)<br>line 18: This reference resolves to the callable registered under 'select'. (`toolbox.select`)<br>line 18: The registered callable is dispatched with arguments linked to the selection role. (`toolbox.select(population, key=evaluate)`) |
| mutation | True | True | MEDIUM | Truth: The registered mutate callable changes candidate content and returns it.<br>Evidence: line 7: The helper writes an element or attribute of its candidate argument. (`candidate[0] = 1 - candidate[0]`)<br>line 14: Registration key 'mutate' explicitly labels the callback as mutation. (`toolbox.register('mutate', mutate)`)<br>line 20: This reference resolves to the callable registered under 'mutate'. (`toolbox.mutate`)<br>line 20: The registered callable is dispatched with arguments linked to the mutation role. (`toolbox.mutate(individual.copy())`) |
| crossover | False | False | LOW | Truth: This registration-shape example has no mating/crossover operation, no population replacement, and no generation/process termination construct.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: This registration-shape example has no mating/crossover operation, no population replacement, and no generation/process termination construct.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: This registration-shape example has no mating/crossover operation, no population replacement, and no generation/process termination construct.<br>Evidence: No detector evidence. |

### `comprehension_fitness` — comprehension_fitness

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | MEDIUM | Truth: The comprehension iterates a collection of candidate vectors.<br>Evidence: line 3: A comprehension invokes a computation on each element of a collection; generator and call source locations are retained. (`[sum(candidate) for candidate in population]`) |
| fitness_evaluation | True | True | MEDIUM | Truth: sum(candidate) produces a score for each candidate.<br>Evidence: line 3: A call consumes the comprehension's candidate variable while iterating a collection. (`sum(candidate)`) |
| selection | False | False | LOW | Truth: The comprehension only scores candidates; it does not rank/filter survivors, modify candidates, combine parents, replace the collection, or define a generation stop condition.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: The comprehension only scores candidates; it does not rank/filter survivors, modify candidates, combine parents, replace the collection, or define a generation stop condition.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: The comprehension only scores candidates; it does not rank/filter survivors, modify candidates, combine parents, replace the collection, or define a generation stop condition.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The comprehension only scores candidates; it does not rank/filter survivors, modify candidates, combine parents, replace the collection, or define a generation stop condition.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: The comprehension only scores candidates; it does not rank/filter survivors, modify candidates, combine parents, replace the collection, or define a generation stop condition.<br>Evidence: No detector evidence. |

### `two_parent_crossover_helper` — two_parent_crossover_helper

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A candidate collection is iterated and supplies both parents.<br>Evidence: line 8: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for parent in population:
    score = sum(parent)`) |
| fitness_evaluation | True | True | HIGH | Truth: The parents are scored using sum(parent).<br>Evidence: line 9: A computed value depends on a candidate passed to a call. (`score = sum(parent)`) |
| selection | False | False | LOW | Truth: The example does not rank/filter candidates, mutate a candidate, replace the population, or implement a generation stop condition.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: The example does not rank/filter candidates, mutate a candidate, replace the population, or implement a generation stop condition.<br>Evidence: No detector evidence. |
| crossover | True | True | HIGH | Truth: crossover(parent_a, parent_b) constructs a child by joining a slice from each parent.<br>Evidence: line 5: The helper constructs a returned value by combining multiple argument-derived representations. (`parent_a[:point] + parent_b[point:]`)<br>line 5: A combined representation is constructed from at least two candidate sources. (`parent_a[:point] + parent_b[point:]`)<br>line 11: Local helper 'crossover' receives values structurally linked to the EA role inputs. (`crossover(parent_a, parent_b)`) |
| replacement | False | False | LOW | Truth: The example does not rank/filter candidates, mutate a candidate, replace the population, or implement a generation stop condition.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: The example does not rank/filter candidates, mutate a candidate, replace the population, or implement a generation stop condition.<br>Evidence: No detector evidence. |

### `mutation_helper` — mutation_helper

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A collection of candidate vectors is iterated.<br>Evidence: line 9: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for individual in population:
    score = sum(individual)
    child = mutate(individual)`) |
| fitness_evaluation | True | True | HIGH | Truth: Each candidate receives a sum-based score.<br>Evidence: line 10: A computed value depends on a candidate passed to a call. (`score = sum(individual)`) |
| selection | False | False | LOW | Truth: No ranking/filtering, two-parent recombination, population replacement, or generation termination is present.<br>Evidence: No detector evidence. |
| mutation | True | True | MEDIUM | Truth: mutate copies a candidate, changes a gene, and returns the modified copy.<br>Evidence: line 5: The helper modifies a copy of its candidate argument and returns that copy. (`changed[0] = 1 - changed[0]`)<br>line 11: Local helper 'mutate' receives values structurally linked to the EA role inputs. (`mutate(individual)`) |
| crossover | False | False | LOW | Truth: No ranking/filtering, two-parent recombination, population replacement, or generation termination is present.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: No ranking/filtering, two-parent recombination, population replacement, or generation termination is present.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: No ranking/filtering, two-parent recombination, population replacement, or generation termination is present.<br>Evidence: No detector evidence. |

### `slice_replacement` — slice_replacement

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A collection of candidates is iterated and retained as a population.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    score = sum(candidate)`) |
| fitness_evaluation | True | True | HIGH | Truth: Each candidate is scored by sum(candidate).<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`score = sum(candidate)`) |
| selection | True | True | MEDIUM | Truth: A slice retains a selected subset of candidates.<br>Evidence: line 5: A slice of the population is retained as survivors. (`selected = population[:1]`)<br>line 7: The retained slice is used to rebuild the population. (`population[:] = selected + offspring`) |
| mutation | False | False | LOW | Truth: The offspring are supplied as values; this source does not modify an existing candidate or construct one from two parents, and has no process termination condition.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: The offspring are supplied as values; this source does not modify an existing candidate or construct one from two parents, and has no process termination condition.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: population[:] is replaced with the selected subset and offspring collection.<br>Evidence: line 7: A statically resolved alias of an inferred population is replaced by slice assignment. (`population[:] = selected + offspring`)<br>line 7: An element of an inferred candidate collection is replaced. (`population[:] = selected + offspring`) |
| termination | False | False | LOW | Truth: The offspring are supplied as values; this source does not modify an existing candidate or construct one from two parents, and has no process termination condition.<br>Evidence: No detector evidence. |

### `termination_helper` — termination_helper

Safety: **CONDITIONALLY_SAFE** (without EA: CONDITIONALLY_SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A collection of candidate vectors is traversed by the process loop.<br>Evidence: line 9: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    best_score = max(best_score, sum(candidate))`) |
| fitness_evaluation | True | True | HIGH | Truth: Each candidate is scored using sum(candidate) to update best_score.<br>Evidence: line 10: A computed value depends on a candidate passed to a call. (`best_score = max(best_score, sum(candidate))`) |
| selection | False | False | LOW | Truth: No ranking/filtering, candidate modification, multi-parent combination, or population replacement is present.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: No ranking/filtering, candidate modification, multi-parent combination, or population replacement is present.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: No ranking/filtering, candidate modification, multi-parent combination, or population replacement is present.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: No ranking/filtering, candidate modification, multi-parent combination, or population replacement is present.<br>Evidence: No detector evidence. |
| termination | True | True | MEDIUM | Truth: The outer EA process loop continues according to the helper-returned condition should_continue(best_score, 2).<br>Evidence: line 4: The helper returns a condition structurally derived from its arguments. (`return best_score < target`)<br>line 8: The evolutionary loop is controlled by a runtime condition. (`while should_continue(best_score, 2):
    for candidate in population:
        best_score = max(best_score, sum(candidate))`)<br>line 8: The EA process loop uses a locally summarized condition helper. (`should_continue(best_score, 2)`) |

### `non_ea_loop` — non_ea_control_flow

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: The loops only accumulate an integer total; range iteration and a while condition alone are not EA termination or population evidence, and there are no candidates or evolutionary operators.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: The loops only accumulate an integer total; range iteration and a while condition alone are not EA termination or population evidence, and there are no candidates or evolutionary operators.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: The loops only accumulate an integer total; range iteration and a while condition alone are not EA termination or population evidence, and there are no candidates or evolutionary operators.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: The loops only accumulate an integer total; range iteration and a while condition alone are not EA termination or population evidence, and there are no candidates or evolutionary operators.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: The loops only accumulate an integer total; range iteration and a while condition alone are not EA termination or population evidence, and there are no candidates or evolutionary operators.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The loops only accumulate an integer total; range iteration and a while condition alone are not EA termination or population evidence, and there are no candidates or evolutionary operators.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: The loops only accumulate an integer total; range iteration and a while condition alone are not EA termination or population evidence, and there are no candidates or evolutionary operators.<br>Evidence: No detector evidence. |

### `non_ea_indexed_writes` — non_ea_indexed_writes

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: The indexed writes fill a fixed matrix with row-plus-column values; they are not candidate mutation, recombination, or population replacement.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: The indexed writes fill a fixed matrix with row-plus-column values; they are not candidate mutation, recombination, or population replacement.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: The indexed writes fill a fixed matrix with row-plus-column values; they are not candidate mutation, recombination, or population replacement.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: The indexed writes fill a fixed matrix with row-plus-column values; they are not candidate mutation, recombination, or population replacement.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: The indexed writes fill a fixed matrix with row-plus-column values; they are not candidate mutation, recombination, or population replacement.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The indexed writes fill a fixed matrix with row-plus-column values; they are not candidate mutation, recombination, or population replacement.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: The indexed writes fill a fixed matrix with row-plus-column values; they are not candidate mutation, recombination, or population replacement.<br>Evidence: No detector evidence. |

### `non_ea_random_indexing` — non_ea_random_indexing

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: A single random choice selects an ordinary color string; there is no candidate population, fitness relationship, iterative selection, or reproduction.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: A single random choice selects an ordinary color string; there is no candidate population, fitness relationship, iterative selection, or reproduction.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: A single random choice selects an ordinary color string; there is no candidate population, fitness relationship, iterative selection, or reproduction.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: A single random choice selects an ordinary color string; there is no candidate population, fitness relationship, iterative selection, or reproduction.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: A single random choice selects an ordinary color string; there is no candidate population, fitness relationship, iterative selection, or reproduction.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: A single random choice selects an ordinary color string; there is no candidate population, fitness relationship, iterative selection, or reproduction.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: A single random choice selects an ordinary color string; there is no candidate population, fitness relationship, iterative selection, or reproduction.<br>Evidence: No detector evidence. |

### `ordinary_callback_registration` — ordinary_callback_registration

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: A generic on_message callback trims text. Registration and dispatch without EA-role structure are not evidence of evolutionary operators.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: A generic on_message callback trims text. Registration and dispatch without EA-role structure are not evidence of evolutionary operators.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: A generic on_message callback trims text. Registration and dispatch without EA-role structure are not evidence of evolutionary operators.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: A generic on_message callback trims text. Registration and dispatch without EA-role structure are not evidence of evolutionary operators.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: A generic on_message callback trims text. Registration and dispatch without EA-role structure are not evidence of evolutionary operators.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: A generic on_message callback trims text. Registration and dispatch without EA-role structure are not evidence of evolutionary operators.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: A generic on_message callback trims text. Registration and dispatch without EA-role structure are not evidence of evolutionary operators.<br>Evidence: No detector evidence. |

### `safe_ea` — safe_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: Candidate vectors are traversed and updated as a population.<br>Evidence: line 4: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    score = sum(candidate)`)<br>line 8: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in selected:
    child = candidate.copy()
    child[random.randrange(len(child))] = 1
    offspring.append(child)`)<br>line 14: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    score = sum(candidate)`) |
| fitness_evaluation | True | True | HIGH | Truth: Each candidate is scored by sum(candidate).<br>Evidence: line 5: A computed value depends on a candidate passed to a call. (`score = sum(candidate)`)<br>line 15: A computed value depends on a candidate passed to a call. (`score = sum(candidate)`) |
| selection | True | True | HIGH | Truth: Candidates are ranked and the best subset is selected.<br>Evidence: line 6: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`sorted(population, key=sum, reverse=True)`) |
| mutation | True | True | HIGH | Truth: A selected candidate copy has one gene changed.<br>Evidence: line 10: A candidate or its alias is modified through an element or attribute update. (`child[random.randrange(len(child))] = 1`) |
| crossover | False | False | LOW | Truth: Although candidates are copied and mutated, no child is formed by combining two parents; mutation is not crossover.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: The population is rebuilt from selected candidates and offspring.<br>Evidence: line 12: A candidate collection is replaced by a newly composed collection. (`population = selected + offspring`) |
| termination | True | True | HIGH | Truth: The generation process is bounded by range(4).<br>Evidence: line 13: The evolutionary loop iterates a finite built-in range or literal collection. (`for generation in range(4):
    for candidate in population:
        score = sum(candidate)`) |

### `unsafe_ea` — unsafe_ea

Safety: **UNSAFE** (without EA: UNSAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: Candidate vectors are iterated and maintained as a population.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    score = sum(candidate)`) |
| fitness_evaluation | True | True | HIGH | Truth: sum(candidate) computes a candidate score.<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`score = sum(candidate)`) |
| selection | True | True | HIGH | Truth: Candidates are sorted by score.<br>Evidence: line 5: A ranking, filtering, or sampling operation consumes an inferred candidate collection. (`sorted(population, key=sum)`) |
| mutation | True | True | MEDIUM | Truth: A copied candidate has a gene flipped.<br>Evidence: line 6: A population or selected candidate is copied. (`child = selected[0].copy()`)<br>line 7: The candidate copy (or an alias of it) is modified through an element or attribute write. (`child[0] = 1 - child[0]`) |
| crossover | False | False | LOW | Truth: The program contains no two-parent recombination and no generation/process termination loop; the unsafe eval(input()) sink does not imply any EA role.<br>Evidence: No detector evidence. |
| replacement | True | True | HIGH | Truth: A slice assignment replaces the current population with selected candidates and a child.<br>Evidence: line 8: A statically resolved alias of an inferred population is replaced by slice assignment. (`population[:] = selected + [child]`)<br>line 8: An element of an inferred candidate collection is replaced. (`population[:] = selected + [child]`) |
| termination | False | False | LOW | Truth: The program contains no two-parent recombination and no generation/process termination loop; the unsafe eval(input()) sink does not imply any EA role.<br>Evidence: No detector evidence. |

### `incomplete_ambiguous_ea` — incomplete_ambiguous_ea

Safety: **SAFE** (without EA: SAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | True | True | HIGH | Truth: A candidate collection is explicitly traversed and its elements are passed to an operation.<br>Evidence: line 3: A loop iterates a collection and uses each element in candidate evaluation or reproduction logic. (`for candidate in population:
    value = objective(candidate)`) |
| fitness_evaluation | True | True | HIGH | Truth: objective(candidate) computes a per-candidate objective value; the program docstring states it is candidate scoring, matching the specification example score = objective(individual).<br>Evidence: line 4: A computed value depends on a candidate passed to a call. (`value = objective(candidate)`)<br>line 4: A candidate is consumed by an evaluation-like computation inside collection iteration. (`objective(candidate)`) |
| selection | False | False | LOW | Truth: Only candidate scoring is visible; the EA is incomplete. No selection, mutation, crossover, replacement, or process termination role is present. (Label corrected in Build 7: an earlier edit set fitness to false without changing the program, contradicting its documented intent.)<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: Only candidate scoring is visible; the EA is incomplete. No selection, mutation, crossover, replacement, or process termination role is present. (Label corrected in Build 7: an earlier edit set fitness to false without changing the program, contradicting its documented intent.)<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: Only candidate scoring is visible; the EA is incomplete. No selection, mutation, crossover, replacement, or process termination role is present. (Label corrected in Build 7: an earlier edit set fitness to false without changing the program, contradicting its documented intent.)<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: Only candidate scoring is visible; the EA is incomplete. No selection, mutation, crossover, replacement, or process termination role is present. (Label corrected in Build 7: an earlier edit set fitness to false without changing the program, contradicting its documented intent.)<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: Only candidate scoring is visible; the EA is incomplete. No selection, mutation, crossover, replacement, or process termination role is present. (Label corrected in Build 7: an earlier edit set fitness to false without changing the program, contradicting its documented intent.)<br>Evidence: No detector evidence. |

### `unsafe_non_ea` — unsafe_non_ea

Safety: **UNSAFE** (without EA: UNSAFE; unchanged=True).

| Role | Truth | Prediction | Confidence | Evidence / rationale |
|---|---:|---:|---|---|
| population | False | False | LOW | Truth: The source only reads and dynamically evaluates a command; an unsafe sink is unrelated to every EA role.<br>Evidence: No detector evidence. |
| fitness_evaluation | False | False | LOW | Truth: The source only reads and dynamically evaluates a command; an unsafe sink is unrelated to every EA role.<br>Evidence: No detector evidence. |
| selection | False | False | LOW | Truth: The source only reads and dynamically evaluates a command; an unsafe sink is unrelated to every EA role.<br>Evidence: No detector evidence. |
| mutation | False | False | LOW | Truth: The source only reads and dynamically evaluates a command; an unsafe sink is unrelated to every EA role.<br>Evidence: No detector evidence. |
| crossover | False | False | LOW | Truth: The source only reads and dynamically evaluates a command; an unsafe sink is unrelated to every EA role.<br>Evidence: No detector evidence. |
| replacement | False | False | LOW | Truth: The source only reads and dynamically evaluates a command; an unsafe sink is unrelated to every EA role.<br>Evidence: No detector evidence. |
| termination | False | False | LOW | Truth: The source only reads and dynamically evaluates a command; an unsafe sink is unrelated to every EA role.<br>Evidence: No detector evidence. |

## Safety separation

- `non_ea_loop`: expected SAFE; observed SAFE with EA / SAFE without EA; unchanged=True.
- `ordinary_callback_registration`: expected SAFE; observed SAFE with EA / SAFE without EA; unchanged=True.
- `safe_ea`: expected SAFE; observed SAFE with EA / SAFE without EA; unchanged=True.
- `unsafe_ea`: expected UNSAFE; observed UNSAFE with EA / UNSAFE without EA; unchanged=True.
- `unsafe_non_ea`: expected UNSAFE; observed UNSAFE with EA / UNSAFE without EA; unchanged=True.
- Invalid-syntax UNKNOWN harness status: UNKNOWN without EA, UNKNOWN with EA; unchanged=True. UNKNOWN here is the benchmark harness status for invalid syntax; the safety API raises before producing a verdict.
- All 18 programs: verdict identical with and without EA inference = True (changed: none).

Overall benchmark safety-independence checks: **PASS**.
