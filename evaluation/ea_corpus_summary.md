# EvoSafe EA Inference Corpus Evaluation

- Programs analyzed: **2562**
- Successfully analyzed: **2545**
- Analysis errors: **17**
- Corpus categories: `{"benign_python_corpus": 622, "framework_specific_ea": 340, "generic_ea": 2, "generic_python": 1580, "unknown_uncertain": 18}`
- Safety verdicts: `{"CONDITIONALLY_SAFE": 447, "SAFE": 1667, "UNKNOWN": 17, "UNSAFE": 431}`
- Corpus-wide role labels: **not present**; corpus-wide precision, recall, F1, and false-positive/false-negative totals are unavailable.

## EA roles

| Role | Detected | Not detected | Confidence among detections |
|---|---:|---:|---|
| population | 886 | 1659 | `{"HIGH": 652, "MEDIUM": 234}` |
| fitness_evaluation | 625 | 1920 | `{"HIGH": 325, "MEDIUM": 300}` |
| selection | 153 | 2392 | `{"HIGH": 18, "MEDIUM": 135}` |
| mutation | 457 | 2088 | `{"HIGH": 448, "MEDIUM": 9}` |
| crossover | 289 | 2256 | `{"HIGH": 14, "MEDIUM": 275}` |
| replacement | 92 | 2453 | `{"HIGH": 91, "MEDIUM": 1}` |
| termination | 203 | 2342 | `{"HIGH": 57, "MEDIUM": 146}` |

### Detections within key EA corpus categories

| Category | Role | Detected | Not detected |
|---|---|---:|---:|
| framework_specific_ea | population | 77 | 263 |
| framework_specific_ea | fitness_evaluation | 56 | 284 |
| framework_specific_ea | selection | 24 | 316 |
| framework_specific_ea | mutation | 46 | 294 |
| framework_specific_ea | crossover | 27 | 313 |
| framework_specific_ea | replacement | 23 | 317 |
| framework_specific_ea | termination | 26 | 314 |
| generic_ea | population | 2 | 0 |
| generic_ea | fitness_evaluation | 2 | 0 |
| generic_ea | selection | 0 | 2 |
| generic_ea | mutation | 1 | 1 |
| generic_ea | crossover | 1 | 1 |
| generic_ea | replacement | 0 | 2 |
| generic_ea | termination | 2 | 0 |

### Framework-associated corpus breakdown

| Framework | Role | Detected | Not detected |
|---|---|---:|---:|
| DEAP | population | 49 | 6 |
| DEAP | fitness_evaluation | 34 | 21 |
| DEAP | selection | 22 | 33 |
| DEAP | mutation | 31 | 24 |
| DEAP | crossover | 19 | 36 |
| DEAP | replacement | 18 | 37 |
| DEAP | termination | 25 | 30 |
| PyGAD | population | 3 | 69 |
| PyGAD | fitness_evaluation | 3 | 69 |
| PyGAD | selection | 1 | 71 |
| PyGAD | mutation | 1 | 71 |
| PyGAD | crossover | 0 | 72 |
| PyGAD | replacement | 0 | 72 |
| PyGAD | termination | 0 | 72 |
| mealpy | population | 12 | 55 |
| mealpy | fitness_evaluation | 7 | 60 |
| mealpy | selection | 0 | 67 |
| mealpy | mutation | 8 | 59 |
| mealpy | crossover | 4 | 63 |
| mealpy | replacement | 0 | 67 |
| mealpy | termination | 0 | 67 |
| pymoo | population | 13 | 133 |
| pymoo | fitness_evaluation | 12 | 134 |
| pymoo | selection | 1 | 145 |
| pymoo | mutation | 6 | 140 |
| pymoo | crossover | 4 | 142 |
| pymoo | replacement | 5 | 141 |
| pymoo | termination | 1 | 145 |

## Corpus inventory

- `dataset/benign`: 622 Python files
- `dataset/deap`: 55 Python files
- `dataset/generic_unsafe`: 0 Python files
- `dataset/llm_ea`: 0 Python files
- `dataset/llm_non_ea`: 0 Python files
- `dataset/non_deap`: 285 Python files
- `dataset/unsafe_ea`: 0 Python files
- `dataset/unsafe_non_ea`: 0 Python files

Framework-associated Python files:
- `DEAP`: 55 files under `dataset/deap`
- `mealpy`: 67 files under `dataset/non_deap/mealpy`
- `PyGAD`: 72 files under `dataset/non_deap/pygad`
- `pymoo`: 146 files under `dataset/non_deap/pymoo`

Notebooks not analyzed by this runner:
- `dataset/deap/hyperparameter_tuning.ipynb`
- `dataset/non_deap/mealpy/applications/discrete-problems/knapsack_problem.ipynb`
- `dataset/non_deap/mealpy/applications/discrete-problems/product_planning.ipynb`
- `dataset/non_deap/mealpy/run_multitask.ipynb`
- `dataset/non_deap/mealpy/run_tuner.ipynb`
- `dataset/non_deap/mealpy/utils/run_problem.ipynb`
- `dataset/non_deap/pygad/example_travelling_salesman.ipynb`
- `examples/quickstart.ipynb`

Directory provenance is not treated as role-level ground truth. `dataset/unsafe_ea`, `dataset/unsafe_non_ea`, `dataset/generic_unsafe`, `dataset/llm_ea`, and `dataset/llm_non_ea` contain no Python files in this checkout.

## Manual review summary

- Reviewed source examples: **8**
- Confirmed non-EA programs reviewed: **3**
- Detected role/program pairs in those non-EA sources (confirmed false-positive candidates): **18**
- Additional misleading/non-corresponding framework evidence candidates: **29**
- Potential missed source roles in reviewed EA/framework examples: **8**
These are small manually inspected samples, not corpus-wide precision/recall metrics.

## Candidate manual-review cases

The JSON contains **332** review candidates for labeled EA corpus paths where one or more roles were not detected. These are not confirmed misses; the category does not say which roles a file implements.
A manual source audit confirmed all seven roles in 2 representative files. Spot-check metrics:
- `population`: TP=2, FN=0, recall=1.0; precision/F1 unavailable because there are no manually labeled negative programs.
- `fitness_evaluation`: TP=2, FN=0, recall=1.0; precision/F1 unavailable because there are no manually labeled negative programs.
- `selection`: TP=1, FN=1, recall=0.5; precision/F1 unavailable because there are no manually labeled negative programs.
- `mutation`: TP=1, FN=1, recall=0.5; precision/F1 unavailable because there are no manually labeled negative programs.
- `crossover`: TP=1, FN=1, recall=0.5; precision/F1 unavailable because there are no manually labeled negative programs.
- `replacement`: TP=1, FN=1, recall=0.5; precision/F1 unavailable because there are no manually labeled negative programs.
- `termination`: TP=2, FN=0, recall=1.0; precision/F1 unavailable because there are no manually labeled negative programs.

Likely cause for each confirmed miss:
- `Python/genetic_algorithm/basic_string.py` / `selection`: selection and ranking logic is distributed across select() and basic().
- `Python/genetic_algorithm/basic_string.py` / `mutation`: mutation is encapsulated in mutate() and reached through offspring helper calls.
- `Python/genetic_algorithm/basic_string.py` / `crossover`: two-parent crossover is encapsulated in crossover() and called indirectly from select().
- `Python/genetic_algorithm/basic_string.py` / `replacement`: population clear/extend and survivor retention are spread across basic() and select().
- `Python/genetic_algorithm/travelling_salesman_problem.py` — not detected: selection, replacement; hypothesis: helper_function_or_indirect_data_flow_possible.
- `dataset/deap/bbob.py` — not detected: selection, crossover, replacement; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/coev/coop_base.py` — not detected: replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/coev/hillis.py` — not detected: crossover; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/coev/symbreg.py` — not detected: replacement; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/de/sphere.py` — not detected: termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/eda/emna.py` — not detected: population, fitness_evaluation, selection, mutation, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/eda/pbil.py` — not detected: fitness_evaluation, selection, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/es/cma_1+l_minfct.py` — not detected: population, fitness_evaluation, selection, mutation, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/es/cma_bipop.py` — not detected: population, fitness_evaluation, selection, mutation, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/es/cma_minfct.py` — not detected: population, fitness_evaluation, selection, mutation, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/es/cma_mo.py` — not detected: mutation, crossover, replacement; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/es/cma_plotting.py` — not detected: fitness_evaluation, selection, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/es/fctmin.py` — not detected: fitness_evaluation, selection, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/es/onefifth.py` — not detected: selection, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/ga/evoknn.py` — not detected: selection, mutation, crossover, replacement; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/ga/evoknn_jmlr.py` — not detected: fitness_evaluation, mutation, crossover, replacement; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/ga/evosn.py` — not detected: replacement; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/ga/knapsack.py` — not detected: fitness_evaluation, selection, crossover, replacement, termination; hypothesis: framework_operator_api_or_helper_boundary_possible.
- `dataset/deap/ga/knn.py` — not detected: selection, crossover, replacement; hypothesis: framework_operator_api_or_helper_boundary_possible.
- … 312 additional cases are listed in the JSON report.

### Reviewed examples

- `dataset/deap/ga/onemax.py` — detected: population, fitness_evaluation, selection, mutation, crossover, replacement, termination; not detected: none. Explicit population/evaluate/select/mate/mutate registrations, map callback use, two-parent offspring call, pop[:] replacement, and generation/convergence loop are visible in source.
- `Python/genetic_algorithm/basic_string.py` — detected: population, fitness_evaluation, termination; not detected: selection, mutation, crossover, replacement. Source code has candidate initialization, evaluate() scoring, sorted/ranked scores and random parent indexing, mutate()/crossover() helper calls, population clear/extend rebuild, and a convergence exit inside while True.
- `dataset/non_deap/pygad/example_custom_operators.py` — detected: population, fitness_evaluation, selection, mutation; not detected: crossover, replacement, termination. Defines fitness_func, parent_selection_func, crossover_func, and mutation_func; callback wiring is passed to pygad.GA and execution is delegated to ga_instance.run(). Population initialization and generation termination are framework-managed.
- `dataset/non_deap/pymoo/algorithms/moo/nsga2/nsga2_custom.py` — detected: population, fitness_evaluation, selection, mutation, replacement, termination; not detected: crossover. Defines a custom sampler, problem _evaluate callback, two-parent crossover, and mutation; NSGA2 selection/replacement and minimize termination are framework-managed.
- `dataset/non_deap/mealpy/applications/keras/mha-hybrid-mlp-classification.py` — detected: population, fitness_evaluation; not detected: selection, mutation, crossover, replacement, termination. The source supplies fitness_function to a Mealpy GWO optimizer and calls solve(); GWO is a population-based metaheuristic, but the evolutionary-role interpretation of its framework-managed internals is intentionally uncertain. The weight_sizes/reshape loop is model decoding, not population iteration.
- `Python/machine_learning/astar.py` — detected: population, selection, mutation, crossover, replacement, termination; not detected: fitness_evaluation. A* graph search manages open/closed frontiers, chooses the minimum f-score node, updates path-cost/heuristic fields, and appends neighbors. These are graph-search operations, not evolutionary roles.
- `dataset/benign/algorithms/data_structures/arrays/sudoku_solver.py` — detected: population, fitness_evaluation, selection, crossover, replacement, termination; not detected: mutation. The file implements constraint propagation, unit construction, candidate filtering, and recursive search for Sudoku; list comprehensions, filtering, concatenation, and iteration are not EA roles.
- `dataset/benign/algorithms/data_structures/heap/binomial_heap.py` — detected: population, fitness_evaluation, mutation, crossover, replacement, termination; not detected: selection. The file implements binomial-heap tree merging, linking, insertion, and deletion. Indexed link updates, list merging, and loops are data-structure operations, not mutation/crossover/replacement roles in an EA.

## Analysis failures

All recorded failures are source parse/analysis errors, not detector misses. Several legacy Python 2-style `except` clauses are invalid under the active Python 3 parser.
- `Python/digital_image_processing/filters/local_binary_pattern.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 22)
- `Python/divide_and_conquer/convex_hull.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 127)
- `Python/dynamic_programming/catalan_numbers.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 74)
- `Python/dynamic_programming/egg_dropping.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 69)
- `Python/maths/greatest_common_divisor.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 76)
- `Python/maths/special_numbers/kaprekar_constant.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 198)
- `Python/project_euler/problem_002/sol4.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 59)
- `Python/project_euler/problem_003/sol1.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 83)
- `Python/project_euler/problem_003/sol2.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 47)
- `Python/project_euler/problem_003/sol3.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 47)
- `Python/project_euler/problem_005/sol1.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 50)
- `Python/project_euler/problem_007/sol2.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 90)
- `Python/web_programming/crypto_price_tracker.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 27)
- `Python/web_programming/fetch_well_rx_price.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 70)
- `Python/web_programming/instagram_crawler.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 56)
- `dataset/benign/algorithms/dynamic_programming/catalan_numbers.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 74)
- `dataset/benign/algorithms/dynamic_programming/egg_dropping.py` — SyntaxError: multiple exception types must be parenthesized (<unknown>, line 69)

## Safety-independence check

- `safe_ea`: SAFE without EA, SAFE with EA; unchanged=True; expected=True.
- `unsafe_ea`: UNSAFE without EA, UNSAFE with EA; unchanged=True; expected=True.
- `safe_non_ea`: SAFE without EA, SAFE with EA; unchanged=True; expected=True.
- `unsafe_non_ea`: UNSAFE without EA, UNSAFE with EA; unchanged=True; expected=True.
- `ea_incomplete_recognition`: SAFE without EA, SAFE with EA; unchanged=True; expected=True.

## Interpretation and limitations

- The DEAP/PyGAD/pymoo/mealpy directories provide framework-associated examples, but not role-level annotations; corpus directory placement alone is not sufficient to calculate role metrics.
- Framework callbacks, registered operators, delegated algorithm loops, helper functions, aliases, and indirect data flow are plausible sources of unrecognized structure. These remain hypotheses until reviewed against each source.
- `dataset/benign` is a safety-oriented label, not proof that every file is non-EA. Its role detections require manual review rather than being counted as false positives.
- Notebooks are inventoried but not analyzed by this Python-file runner.
- The report does not execute corpus files and does not implement resource enrichment.
