# Evaluation artefacts

| Group | Files | Use |
|---|---|---|
| **Review 2 (current, frozen)** | `r2_*.json`, `r2_*.csv`, `r2_*.md`, `plots/` | The results reported in the README, thesis and paper. Regenerate predictions and metrics with `python3 scripts/reproduce_r2.py`. |
| **EA role benchmarks** | `ea_role_benchmark/` (18 development programs), `ea_role_benchmark_holdout/` (51 held-out programs) | Role-level ground truth used while building and testing the detectors. Run with `scripts/evaluate_ea_benchmark.py`. |
| **Corpus survey (earlier)** | `ea_corpus_summary.md`, `ea_corpus_comparison.md` | Detections over a 2,562-program corpus with no role labels, so no precision/recall. Produced by `scripts/evaluate_ea_corpus.py`, which needs the optional `Python/` tree. |

Start with `r2_metrics.md` for numbers and `r2_error_analysis.md` for why roles are missed. See [../docs/RESULTS.md](../docs/RESULTS.md) for the consolidated write-up.
