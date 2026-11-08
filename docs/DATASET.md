# Dataset

## Contents

| Category | Reviewed programs | Source type | What it is |
|---|---:|---|---|
| `benign` | 600 | existing corpus | Ordinary Python: 294 educational algorithm and data-structure programs and 306 Python Cookbook examples. No EA roles. |
| `deap` | 51 | existing corpus | DEAP framework examples (GA, GP, ES, coevolution, and others). |
| `non_deap` | 85 | existing corpus | Non-DEAP EA / metaheuristic code: PyGAD (58), mealpy (26), pymoo (1). |
| `generic_unsafe` | 40 | controlled generation | Controlled-generation unsafe programs without EA structure. |
| `unsafe_ea` | 40 | controlled generation | Controlled-generation unsafe programs with EA structure. |
| `unsafe_non_ea` | 40 | controlled generation | Controlled-generation unsafe programs, no EA structure. |
| `llm_ea` | 40 | LLM generated | Generated EA programs, reviewed and labelled. |
| `llm_non_ea` | 40 | LLM generated | Generated non-EA programs, reviewed and labelled. |
| **Total reviewed** | **936** | | |

The directory holds 1,114 Python programs in total. The other **178 are unreviewed and excluded** from every Review 2 number (173 in `non_deap`, 3 in `deap`, 2 in `benign`).

## Labels

Every reviewed program `foo.py` has `foo.py.metadata.json` with:

- `expected_safety`: `SAFE`, `UNSAFE`, `CONDITIONALLY_SAFE` or `UNKNOWN`
- `ea_roles`: booleans for population, fitness, selection, mutation, crossover, replacement, termination
- `safety_violations`, `description`, `ground_truth_reason`, `review_status`, `source_type`, `source_path`

| Safety label | Programs | Meaning |
|---|---:|---|
| `SAFE` | 35 | Reviewed as safe under the configured policy (all in `llm_*` categories) |
| `UNSAFE` | 67 | Reviewed as unsafe (spread over the five generated / controlled categories) |
| `CONDITIONALLY_SAFE` | 7 | Safe only if policy checks are satisfied |
| `UNKNOWN` | 827 | Not individually adjudicated against the safety policy. A category label such as "benign" is **not** a safety verdict. |

EA-role label counts (true / false over 936): population 207 / 729, fitness 209 / 727, selection 209 / 727, mutation 194 / 742, crossover 115 / 821, replacement 203 / 733, termination 172 / 764.

## Validation and known issues

Validation status is `READY_WITH_RECORDED_DUPLICATES` (full report: `dataset/dataset_validation_report.md`).

- All 936 reviewed sources parse; no unreadable sources, missing references, schema failures or duplicate program IDs.
- Duplicates are recorded, not removed: 3 exact-duplicate source groups (9 extra files, mostly identical `setup.py` files in the cookbook examples) and 116 near-duplicate pairs at token similarity of at least 0.90.
- Two files outside the evaluation set do not parse under Python 3: `benign/algorithms/dynamic_programming/catalan_numbers.py` and `egg_dropping.py` (Python 2 `except A, B` syntax).
- Safety ground truth is thin where it matters most: only 109 determinate labels, and no determinate labels at all in `benign`, `deap` and `non_deap`.

## Provenance

| Source type | Programs |
|---|---:|
| existing corpus (third-party open-source code) | 736 |
| controlled generation (written for this project) | 120 |
| LLM generated | 80 |
