#!/usr/bin/env python3
"""Extract the numbers the demo's Evaluation page shows from the frozen Review 2 metrics.

Reads evaluation/r2_metrics.json and writes public/data/review2.json. Run it again if the
metrics are ever regenerated.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = ("population", "fitness", "selection", "mutation", "crossover", "replacement", "termination")


def main() -> None:
    m = json.loads((ROOT / "evaluation/r2_metrics.json").read_text())
    s = m["safety"]
    out = {
        "dataset_version": m["dataset_version"],
        "dataset_hash": m["dataset_hash"],
        "programs": s["program_count"],
        "safety": {
            "determinate": s["determinate_ground_truth_program_count"],
            "correct": s["accuracy_determinate_ground_truth_correct"],
            "accuracy": s["accuracy_determinate_ground_truth"],
            "ground_truth_counts": s["ground_truth_counts"],
            "prediction_counts": s["prediction_counts"],
            "classes": {
                c: {k: v[k] for k in ("precision", "recall", "f1")}
                for c, v in s["binary_class_metrics_on_determinate_ground_truth"].items()
            },
        },
        "roles": {r: {k: m["ea_roles"]["overall"][r][k] for k in ("precision", "recall", "f1")} for r in ROLES},
        "roles_macro": {k: m["ea_roles"]["macro_average"][k] for k in ("precision", "recall", "f1")},
        "categories": {
            c: {
                "programs": v["programs"],
                "determinate": v["determinate_ground_truth_programs"],
                "unknown": v["unknown_ground_truth_programs"],
                "safety_accuracy": v["safety_accuracy_determinate_ground_truth"],
                "ea_macro_f1": v["ea_macro_f1"],
            }
            for c, v in m["category_results"].items()
        },
        "snapshots": m["v1_v2_comparison"]["rows"],
    }
    dest = ROOT / "public" / "data" / "review2.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(f"wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
