# EvoSafe Review 2 Frozen Evaluation

- Dataset version: `review-2.0`
- Dataset SHA-256: `c40f92f8c0b49732a045469c1091bccf32d5d14360234456edc8fb7218680082`
- EvoSafe git revision: `0891f932119b21a0258f12a41441022e515e9aca`
- EvoSafe source fingerprint: `72e0dd15c716bd8162203c34e66e61b86c90f4fed119c86ce26e42bf15fa21df` (47 source files)
- Python: `3.12.3`
- Run interval (UTC): `2026-10-08T06:04:11Z` to `2026-10-08T06:04:24Z`
- Programs evaluated: 936
- Successful analyses: 936
- Failed analyses: 0
- Safety mismatches: 829

## Predicted Safety Counts

- `CONDITIONALLY_SAFE`: 194
- `SAFE`: 482
- `UNKNOWN`: 0
- `UNSAFE`: 260

## EA-Role Predictions

- `population` detected: 238
- `fitness` detected: 209
- `selection` detected: 56
- `mutation` detected: 67
- `crossover` detected: 25
- `replacement` detected: 28
- `termination` detected: 80

## Outputs

- `evaluation/r2_results.json`
- `evaluation/r2_results.csv`

The evaluation used the existing Safety IR implementation with EA enrichment enabled. Unsafe programs were analyzed as source only and never executed. `CONDITIONALLY_SAFE` predictions are preserved verbatim; failed analyses have null predictions and are not counted as `UNKNOWN`. No aggregate EA-role metrics were calculated; independent metric calculation is deferred. Safety mismatches are recorded as requested. No labels or implementation were altered.
