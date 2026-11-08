# R2 EA-Role Error Analysis

Frozen dataset SHA-256: `c40f92f8c0b49732a045469c1091bccf32d5d14360234456edc8fb7218680082`.

All seven roles were compared for every frozen row. **1328 error instances**: 361 FP and 967 FN. One program may contribute multiple errors. Every mismatch has one primary diagnostic group.

## Structural Error Groups

| Category | Errors | FP | FN | Roles affected | Representative program IDs |
|---|---:|---:|---:|---|---|
| comprehensions / ordinary collection transforms | 203 | 203 | 0 | population, fitness, selection | `legacy_benign_2c709f0a098b`, `legacy_benign_d983fbb0d24f`, `legacy_benign_73194c083745`, `legacy_benign_d63030d5c056`, `legacy_benign_62b953d9965c`, `legacy_benign_b347d125327b` |
| replacement / offspring flow | 184 | 0 | 184 | replacement | `legacy_deap_a8bb87e619d2`, `legacy_deap_daf756986348`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab` |
| selection/ranking | 176 | 0 | 176 | selection | `legacy_deap_a8bb87e619d2`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b` |
| non-EA lookalikes | 148 | 148 | 0 | termination, crossover, replacement, population, fitness, mutation, selection | `legacy_benign_2c709f0a098b`, `legacy_benign_d983fbb0d24f`, `legacy_benign_53b239eb3134`, `legacy_benign_5b779e4dcaf9`, `legacy_benign_d63030d5c056`, `legacy_benign_68fae353ad04` |
| mutation | 140 | 1 | 139 | mutation | `legacy_deap_a8bb87e619d2`, `legacy_deap_849b802d9183`, `legacy_deap_08d4fc5b1089`, `legacy_deap_2648616e5db8`, `legacy_deap_8196027d738d`, `legacy_deap_a90785fea716` |
| candidate lineage / fitness dependency | 130 | 0 | 130 | fitness | `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b`, `legacy_deap_ea85dba53854` |
| termination | 128 | 3 | 125 | termination | `legacy_deap_a8bb87e619d2`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b` |
| population/collection recognition | 113 | 2 | 111 | population | `legacy_deap_a8bb87e619d2`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b` |
| candidate lineage / two-parent crossover | 105 | 4 | 101 | crossover | `legacy_deap_37bd9d00fbfa`, `legacy_deap_849b802d9183`, `legacy_deap_2648616e5db8`, `legacy_deap_856c2e5e6a3e`, `legacy_deap_d3be80dd647e`, `legacy_deap_24b7ac78885a` |
| helper functions | 1 | 0 | 1 | mutation | `llm_ea_024` |

## Role Error Counts

| Role | FP | FN | Total |
|---|---:|---:|---:|
| Population | 142 | 111 | 253 |
| Fitness | 130 | 130 | 260 |
| Selection | 23 | 176 | 199 |
| Mutation | 13 | 140 | 153 |
| Crossover | 11 | 101 | 112 |
| Replacement | 9 | 184 | 193 |
| Termination | 33 | 125 | 158 |

### comprehensions / ordinary collection transforms

The stored evidence treats list/set/generator comprehensions that map, filter, or score ordinary records as EA population/fitness/selection signals. This produces false positives where there is no candidate reproduction lifecycle.
Roles affected: population, fitness, selection. Representative IDs: `legacy_benign_2c709f0a098b`, `legacy_benign_d983fbb0d24f`, `legacy_benign_73194c083745`, `legacy_benign_d63030d5c056`, `legacy_benign_62b953d9965c`, `legacy_benign_b347d125327b`.

### replacement / offspring flow

Survivors/offspring update the active collection, but replacement lineage is not recovered through rebinding, slices, or helper-returned collections.
Roles affected: replacement. Representative IDs: `legacy_deap_a8bb87e619d2`, `legacy_deap_daf756986348`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`.

### selection/ranking

Survivor or parent choice is present but its ranking/filtering relationship to EA candidates is not recognized.
Roles affected: selection. Representative IDs: `legacy_deap_a8bb87e619d2`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b`.

### non-EA lookalikes

False positives on ordinary non-EA code with collections, loops, data scoring, ranking, or in-place updates that superficially resemble EA operations.
Roles affected: termination, crossover, replacement, population, fitness, mutation, selection. Representative IDs: `legacy_benign_2c709f0a098b`, `legacy_benign_d983fbb0d24f`, `legacy_benign_53b239eb3134`, `legacy_benign_5b779e4dcaf9`, `legacy_benign_d63030d5c056`, `legacy_benign_68fae353ad04`.

### mutation

A candidate-derived copy is changed, but mutation is not connected to the candidate flow or helper result.
Roles affected: mutation. Representative IDs: `legacy_deap_a8bb87e619d2`, `legacy_deap_849b802d9183`, `legacy_deap_08d4fc5b1089`, `legacy_deap_2648616e5db8`, `legacy_deap_8196027d738d`, `legacy_deap_a90785fea716`.

### candidate lineage / fitness dependency

Per-candidate score dependence is missed when data flow is indirect or abstracted, despite explicit fitness ground truth.
Roles affected: fitness. Representative IDs: `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b`, `legacy_deap_ea85dba53854`.

### termination

A termination condition governs evolution but is separated from the recognized candidate loop/context or represented through an unsupported condition.
Roles affected: termination. Representative IDs: `legacy_deap_a8bb87e619d2`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b`.

### population/collection recognition

The source contains candidate-like collections but the analyzer misses their population role, or collection context is incomplete.
Roles affected: population. Representative IDs: `legacy_deap_a8bb87e619d2`, `legacy_deap_6e40a77bf219`, `legacy_deap_8eedb37d3d28`, `legacy_deap_88f310d614c9`, `legacy_deap_bb53dcd9d2ab`, `legacy_deap_8937bafe919b`.

### candidate lineage / two-parent crossover

Crossover positives require a structurally supported relationship to two distinct candidate-derived inputs; helper or expression flow is often not resolved.
Roles affected: crossover. Representative IDs: `legacy_deap_37bd9d00fbfa`, `legacy_deap_849b802d9183`, `legacy_deap_2648616e5db8`, `legacy_deap_856c2e5e6a3e`, `legacy_deap_d3be80dd647e`, `legacy_deap_24b7ac78885a`.

### helper functions

The role-relevant state crosses a local helper boundary; the evidence does not consistently propagate the full candidate relationship.
Roles affected: mutation. Representative IDs: `llm_ea_024`.

These are descriptive groups based on the frozen predictions, stored evidence, and source structure. They are not fixes or relabeling; no detector was changed.

## Observed Limitations

- **Current safety analysis:** 827 reviewed programs have `UNKNOWN` ground truth, and every one received a non-UNKNOWN prediction (447 `SAFE`, 194 `UNSAFE`, 186 `CONDITIONALLY_SAFE`). On the 109 determinate cases, there was one false SAFE and one SAFE case predicted `CONDITIONALLY_SAFE`; no false UNSAFE occurred. Safety accuracy outside the determinate subset is therefore not established by this dataset.
- **EA inference:** 1,328 role-error instances comprise 361 false positives and 967 false negatives. Replacement (184 FN), selection (176 FN), mutation (139 FN), and fitness (130 FN) account for substantial observed misses. The largest FP groups are comprehension-based ordinary transforms (203) and other non-EA lookalikes (148).
- **Python dynamic-language cues:** Across role-error rows, source/evidence text contains helper cues in 11 errors, alias cues in 18, callback/dispatch cues in 65, dynamic-call cues in 77, and array-related lexical cues in 481. These counts overlap and are descriptive search cues, not proven causes; array terms in particular are broad. The frozen evidence yielded only one separately classified helper-function error and no standalone alias/callback/dynamic error group, so stronger causal claims are not supported.
- **Dataset:** 827 of 936 evaluated labels are safety `UNKNOWN`; the legacy corpus contributes many of these. The lock also excludes 178 unreviewed programs. Exact and near-duplicate findings are retained in the frozen validation report and may affect the independence of examples.

These limitations are restricted to observed R2 labels, outputs, and stored evidence. No code or ground truth was changed.
