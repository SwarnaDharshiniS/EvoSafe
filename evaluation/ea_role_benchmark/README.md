# Controlled seven-role EA benchmark

This small source benchmark is separate from the unlabeled repository corpus evaluation. It contains 18 readable Python programs with explicit boolean ground truth for Population, Fitness Evaluation, Selection, Mutation, Crossover, Replacement, and Termination. `benchmark.json` provides every per-program role label plus rationale for positive and negative labels; the report expands those rationales beside the exact detector evidence.

The examples cover direct and helper-function EAs, aliases, generic keyed registration/dispatch, DEAP-style registration shape without a DEAP dependency, comprehension scoring, two-parent crossover, helper mutation, slice replacement, helper-returned termination conditions, ordinary loops, indexed writes, random indexing, ordinary callback registration, SAFE/UNSAFE EA, incomplete EA, and UNSAFE non-EA.

## Run

Use the integrated corpus runner with `--benchmark-manifest evaluation/ea_role_benchmark/benchmark.json`, or run `scripts/evaluate_ea_benchmark.py` directly. Benchmark results are written separately to `evaluation/ea_role_benchmark/results.json`, `results.csv`, and `results.md`. They are not merged with corpus precision/recall summaries.

Programs are statically analyzed and never executed. The unsafe examples contain an `eval(input())` sink but are not run. The benchmark's UNKNOWN safety check uses a separate invalid-syntax input: the safety API raises before returning a verdict, so the harness maps that parse failure to an UNKNOWN analysis status only for the equality check.

Metrics are descriptive of this controlled set; the benchmark is small and deliberately pattern-focused, not a representative estimate of real-world accuracy.
