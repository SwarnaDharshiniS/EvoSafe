# Dataset Validation Report

- Dataset version: `review-2.0`
- Validation timestamp (UTC): `2026-10-08T06:01:26Z`
- Status: **READY_WITH_RECORDED_DUPLICATES**
- Ready for frozen evaluation: **true**

## Inventory

| Category | Python programs | Metadata files | Reviewed | Unreviewed/excluded |
|---|---:|---:|---:|---:|
| `benign` | 602 | 600 | 600 | 2 |
| `deap` | 54 | 51 | 51 | 3 |
| `generic_unsafe` | 40 | 40 | 40 | 0 |
| `llm_ea` | 40 | 40 | 40 | 0 |
| `llm_non_ea` | 40 | 40 | 40 | 0 |
| `non_deap` | 258 | 85 | 85 | 173 |
| `unsafe_ea` | 40 | 40 | 40 | 0 |
| `unsafe_non_ea` | 40 | 40 | 40 | 0 |
| **Total** | **1114** | **936** | **936** | **178** |

## Ground Truth

| Safety label | Count |
|---|---:|
| `SAFE` | 35 |
| `UNSAFE` | 67 |
| `UNKNOWN` | 827 |
| `CONDITIONALLY_SAFE` | 7 |

| EA role | True | False |
|---|---:|---:|
| `population` | 207 | 729 |
| `fitness` | 209 | 727 |
| `selection` | 209 | 727 |
| `mutation` | 194 | 742 |
| `crossover` | 115 | 821 |
| `replacement` | 203 | 733 |
| `termination` | 172 | 764 |

## Validation

- Reviewed sources parsed: 936/936.
- Syntax failures in reviewed programs: 0.
- Unreadable reviewed sources: 0.
- Missing source references: 0.
- Metadata schema/reference failures: 0.
- Duplicate program IDs: 0.
- Unreviewed programs excluded: 178.

### Syntax Failures Outside Evaluation Scope

- `dataset/benign/algorithms/dynamic_programming/catalan_numbers.py` line 74: SyntaxError: multiple exception types must be parenthesized (catalan_numbers.py, line 74)
- `dataset/benign/algorithms/dynamic_programming/egg_dropping.py` line 69: SyntaxError: multiple exception types must be parenthesized (egg_dropping.py, line 69)

## Duplicates

- Exact source groups: 3 (9 extra files).
- Exact token groups: 3 (9 extra files).
- Exact metadata groups: 0.
- Near-duplicate pairs at token similarity >= 0.90: 116.
- Duplicate examples are retained; no files were deleted or labels adjusted.
- Exact source group: `dataset/benign/cookbook/11/creating_a_tcp_server/echoserv.py`, `dataset/benign/cookbook/11/creating_a_tcp_server/echoserv1.py`
- Exact source group: `dataset/benign/cookbook/15/consuming_an_iterable_from_c/setup.py`, `dataset/benign/cookbook/15/diagnosing_segmentation_faults/setup.py`, `dataset/benign/cookbook/15/passing_null_terminated_strings_to_c_libraries/setup.py`, `dataset/benign/cookbook/15/passing_unicode_strings_to_c_libraries/setup.py`, `dataset/benign/cookbook/15/reading_file_like_objects_from_c/setup.py`, `dataset/benign/cookbook/15/working_with_c_strings_of_dubious_encoding/setup.py`
- Exact source group: `dataset/benign/cookbook/15/defining_and_exporting_c_apis_from_extension_modules/setup.py`, `dataset/benign/cookbook/15/managing_opaque_pointers_in_c_extension_modules/setup.py`, `dataset/benign/cookbook/15/writing_a_simple_c_extension_module/setup.py`, `dataset/benign/cookbook/15/writing_an_extension_function_that_operates_on_arrays/setup.py`

## Provenance

- `controlled_generation`: 120
- `existing_corpus`: 736
- `llm_generated`: 80

## Freeze

Frozen dataset SHA-256: `c40f92f8c0b49732a045469c1091bccf32d5d14360234456edc8fb7218680082`.
The lock includes source and metadata SHA-256 hashes for every reviewed evaluation program. Unreviewed programs are excluded. Known duplicates are listed above and in the manifest.
