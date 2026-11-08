# R2 Preliminary Evaluation Metrics

- Dataset: `review-2.0`
- Dataset SHA-256: `c40f92f8c0b49732a045469c1091bccf32d5d14360234456edc8fb7218680082`
- Programs: 936
- Analysis failures: 0

## Safety Metrics

SAFE/UNSAFE one-vs-rest metrics use only determinate ground truth (`SAFE`, `UNSAFE`, `CONDITIONALLY_SAFE`). Ground-truth `UNKNOWN` cases are excluded from those binary metrics but remain in the full confusion matrix, overall raw accuracy, and the explicit unknown-case list. `CONDITIONALLY_SAFE` remains a distinct label.

- Overall exact accuracy (all labels, including UNKNOWN): 107/936 = 0.114
- Exact accuracy on determinate ground truth: 107/109 = 0.982
- Ground-truth UNKNOWN: 827; predicted UNKNOWN: 0
- Analysis failures: 0
- False SAFE (ground truth UNSAFE, predicted SAFE): 1
- False UNSAFE (ground truth SAFE, predicted UNSAFE): 0
- Conditional ground truth predicted SAFE: 0; predicted UNSAFE: 0
- Safety mismatches: 829

| Class | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| SAFE | 34 | 1 | 1 | 73 | 0.971 | 0.971 | 0.971 |
| UNSAFE | 66 | 0 | 1 | 42 | 1.000 | 0.985 | 0.992 |

### Safety Confusion Matrix

| Ground truth \ Prediction | SAFE | UNSAFE | UNKNOWN | CONDITIONALLY_SAFE | ANALYSIS_FAILURE |
|---|---:|---:|---:|---:|---:|
| SAFE | 34 | 0 | 0 | 1 | 0 |
| UNSAFE | 1 | 66 | 0 | 0 | 0 |
| UNKNOWN | 447 | 194 | 0 | 186 | 0 |
| CONDITIONALLY_SAFE | 0 | 0 | 0 | 7 | 0 |

## Seven-Role Metrics

Macro precision: 0.572 (7 defined roles); macro recall: 0.252 (7); macro F1: 0.316 (7).

| Role | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Population | 96 | 142 | 111 | 587 | 0.403 | 0.464 | 0.431 |
| Fitness | 79 | 130 | 130 | 597 | 0.378 | 0.378 | 0.378 |
| Selection | 33 | 23 | 176 | 704 | 0.589 | 0.158 | 0.249 |
| Mutation | 54 | 13 | 140 | 729 | 0.806 | 0.278 | 0.414 |
| Crossover | 14 | 11 | 101 | 810 | 0.560 | 0.122 | 0.200 |
| Replacement | 19 | 9 | 184 | 724 | 0.679 | 0.094 | 0.165 |
| Termination | 47 | 33 | 125 | 731 | 0.588 | 0.273 | 0.373 |

Per-role confusion matrices use truth rows and prediction columns:

| Role | GT True / Pred True | GT True / Pred False | GT False / Pred True | GT False / Pred False |
|---|---:|---:|---:|---:|
| Population | 96 | 111 | 142 | 587 |
| Fitness | 79 | 130 | 130 | 597 |
| Selection | 33 | 176 | 23 | 704 |
| Mutation | 54 | 140 | 13 | 729 |
| Crossover | 14 | 101 | 11 | 810 |
| Replacement | 19 | 184 | 9 | 724 |
| Termination | 47 | 125 | 33 | 731 |

## Category Results

| Category | Programs | Safety Accuracy (determinate GT) | Raw Accuracy (all) | UNKNOWN GT | EA Macro F1 |
|---|---:|---:|---:|---:|---:|
| benign | 600 | Undefined | 0.000 | 600 | 0.000 |
| deap | 51 | Undefined | 0.000 | 51 | 0.628 |
| generic_unsafe | 40 | 1.000 | 0.425 | 23 | 0.000 |
| llm_ea | 40 | 0.935 | 0.725 | 9 | 0.471 |
| llm_non_ea | 40 | 1.000 | 0.725 | 11 | 0.000 |
| non_deap | 85 | Undefined | 0.000 | 85 | 0.021 |
| unsafe_ea | 40 | 1.000 | 0.300 | 28 | 0.479 |
| unsafe_non_ea | 40 | 1.000 | 0.500 | 20 | 0.000 |

## V1/V2 Snapshot Comparison

| Snapshot | Programs | Macro Precision | Macro Recall | Macro F1 | Dataset / split | Roles included |
|---|---:|---:|---:|---:|---|---:|
| v1 development | 18 | 1.000 | 1.000 | 1.000 | evaluation/ea_role_benchmark/benchmark.json | 7 |
| v1 historical evaluation | 51 | 0.806 | 0.543 | 0.640 | evaluation/ea_role_benchmark_holdout/benchmark.json | 6 |
| v2 development candidate | 18 | 1.000 | 1.000 | 1.000 | evaluation/ea_role_benchmark/benchmark.json | 7 |
| v2 current R2 | 936 | 0.572 | 0.252 | 0.316 | dataset/dataset_lock.json | 7 |

These snapshots are not a paired v1-to-v2 comparison: v1 historical uses 51 held-out programs; development snapshots use the same 18-program benchmark; R2 uses 936 programs with a different label mix. The archived v2 candidate fingerprint does not match the current R2 run fingerprint. The 2,562-program corpus comparison is excluded because it has no role-level ground truth.

## Interpretation

- **Safety:** On determinate labels, exact accuracy is 0.982 across 109 cases; SAFE precision/recall are 0.971/0.971, and UNSAFE precision/recall are 1.000/0.985. This covers only 109 determinate cases; 827 unresolved ground truths remain visible, not treated as SAFE.
- **EA roles:** Macro F1 is 0.316, with macro recall 0.252; replacement, crossover, and selection have the weakest F1 scores (0.165, 0.200, 0.249).
- **PoC assessment:** The results support a working preliminary proof of concept: all 936 analyses completed and the system returns differentiated safety and role outputs. They do not support claims of broad safety assurance or production readiness; role recall and UNKNOWN coverage are substantial limitations.

## Outputs

- `evaluation/r2_metrics.json`
- `evaluation/r2_metrics.csv`
- `evaluation/r2_metrics.md`
- `evaluation/r2_tables.md`
- `evaluation/plots/`

