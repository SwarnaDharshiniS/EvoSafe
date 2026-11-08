# R2 Publication Tables

Dataset: `review-2.0`, SHA-256 `c40f92f8c0b49732a045469c1091bccf32d5d14360234456edc8fb7218680082`. All EA-role metric rows cover the 936 locked programs. Safety class metrics exclude ground-truth UNKNOWN; UNKNOWN remains a separate confusion-matrix row and count.

## Safety by Category

| Category | Programs | Safety Accuracy (determinate GT) | Raw Accuracy (all) | SAFE GT | UNSAFE GT | UNKNOWN GT | CONDITIONAL GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| benign | 600 | Undefined | 0.000 | 0 | 0 | 600 | 0 |
| deap | 51 | Undefined | 0.000 | 0 | 0 | 51 | 0 |
| generic_unsafe | 40 | 1.000 | 0.425 | 0 | 15 | 23 | 2 |
| llm_ea | 40 | 0.935 | 0.725 | 17 | 13 | 9 | 1 |
| llm_non_ea | 40 | 1.000 | 0.725 | 18 | 10 | 11 | 1 |
| non_deap | 85 | Undefined | 0.000 | 0 | 0 | 85 | 0 |
| unsafe_ea | 40 | 1.000 | 0.300 | 0 | 11 | 28 | 1 |
| unsafe_non_ea | 40 | 1.000 | 0.500 | 0 | 18 | 20 | 2 |

## Seven-Role Results

| Role | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Population | 96 | 142 | 111 | 587 | 0.403 | 0.464 | 0.431 |
| Fitness | 79 | 130 | 130 | 597 | 0.378 | 0.378 | 0.378 |
| Selection | 33 | 23 | 176 | 704 | 0.589 | 0.158 | 0.249 |
| Mutation | 54 | 13 | 140 | 729 | 0.806 | 0.278 | 0.414 |
| Crossover | 14 | 11 | 101 | 810 | 0.560 | 0.122 | 0.200 |
| Replacement | 19 | 9 | 184 | 724 | 0.679 | 0.094 | 0.165 |
| Termination | 47 | 33 | 125 | 731 | 0.588 | 0.273 | 0.373 |

**Macro:** Precision 0.572; Recall 0.252; F1 0.316 (7 roles).

## Safety Confusion Matrix

| Ground truth \ Prediction | SAFE | UNSAFE | UNKNOWN | CONDITIONALLY_SAFE | ANALYSIS_FAILURE |
|---|---:|---:|---:|---:|---:|
| SAFE | 34 | 0 | 0 | 1 | 0 |
| UNSAFE | 1 | 66 | 0 | 0 | 0 |
| UNKNOWN | 447 | 194 | 0 | 186 | 0 |
| CONDITIONALLY_SAFE | 0 | 0 | 0 | 7 | 0 |

## Version / Split Snapshots

| Snapshot | N | Macro P | Macro R | Macro F1 | Dataset and caveat |
|---|---:|---:|---:|---:|---|
| v1 development | 18 | 1.000 | 1.000 | 1.000 | evaluation/ea_role_benchmark/benchmark.json; Tuned/development set; optimistic. Same 18-program set also used by v2 development. |
| v1 historical evaluation | 51 | 0.806 | 0.543 | 0.640 | evaluation/ea_role_benchmark_holdout/benchmark.json; Held-out benchmark with v1; distinct from the 18-program development set and current R2 corpus. |
| v2 development candidate | 18 | 1.000 | 1.000 | 1.000 | evaluation/ea_role_benchmark/benchmark.json; Saved v2 candidate snapshot on the same 18-program development set; candidate fingerprint does not match R2 run fingerprint. |
| v2 current R2 | 936 | 0.572 | 0.252 | 0.316 | dataset/dataset_lock.json; Current frozen R2 corpus; different 936-program dataset and broad label composition, so do not treat score deltas as paired gains. |
