#!/usr/bin/env python3
"""Re-run the frozen Review 2 evaluation and compare it with the archived results.

Steps
1. Recompute the dataset hash from ``dataset/dataset_lock.json`` and the files on disk.
2. Analyse every locked program through the Safety IR entry point (source only, nothing is
   executed) with EA inference on, exactly as the Review 2 run did.
3. Compare predictions with ``evaluation/r2_results.json``.
4. Recompute the headline safety and EA-role metrics.

Usage (from the repository root)::

    python3 scripts/reproduce_r2.py
    python3 scripts/reproduce_r2.py --json-output /tmp/r2_reproduced.json

Exit status is 0 only when the dataset hash matches and every prediction is identical
to the archived run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.safety_ir import build_safety_ir_from_source, safety_ir_to_json  # noqa: E402

ROLES = ("population", "fitness", "selection", "mutation", "crossover", "replacement", "termination")
# The analyzer calls the fitness role "fitness_evaluation"; the dataset labels call it "fitness".
ROLE_KEY = {"fitness": "fitness_evaluation"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dataset_hash(programs: list[dict]) -> str:
    rows = sorted(programs, key=lambda p: p["program_path"])
    text = "".join(
        f'{p["program_path"]}\t{sha256(ROOT / p["program_path"])}\t'
        f'{p["metadata_path"]}\t{sha256(ROOT / p["metadata_path"])}\n'
        for p in rows
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-output", help="write the reproduced per-program predictions here")
    args = ap.parse_args()

    lock = json.loads((ROOT / "dataset/dataset_lock.json").read_text())
    programs = lock["programs"]
    frozen = {r["program_id"]: r for r in json.loads((ROOT / "evaluation/r2_results.json").read_text())["results"]}

    computed = dataset_hash(programs)
    hash_ok = computed == lock["overall_dataset_hash"]
    print(f"dataset hash  : {computed}")
    print(f"matches lock  : {hash_ok}")

    rows, diffs, failures, times = [], [], 0, []
    for entry in programs:
        meta = json.loads((ROOT / entry["metadata_path"]).read_text())
        source = (ROOT / entry["program_path"]).read_text(encoding="utf-8")
        t0 = time.perf_counter()
        try:
            # Review 2 used the Safety IR entry point (which applies the default external-access
            # policy), not analysis.pipeline.analyze_program (which applies no policy).
            ir = build_safety_ir_from_source(source, source_name=entry["program_path"], include_ea=True)
            out = json.loads(safety_ir_to_json(ir))
            verdict = out["decision"]["verdict"]
            roles = {r: bool(out["ea_roles"]["roles"][ROLE_KEY.get(r, r)]["detected"]) for r in ROLES}
        except Exception as exc:  # recorded, not hidden
            failures += 1
            verdict, roles = None, {r: None for r in ROLES}
            print(f"analysis failure: {entry['program_path']}: {exc}")
        times.append(time.perf_counter() - t0)
        row = {
            "program_id": entry["program_id"],
            "category": entry["category"],
            "gt_safety": meta["expected_safety"],
            "pred_safety": verdict,
            "gt_roles": {r: bool(meta["ea_roles"][r]) for r in ROLES},
            "pred_roles": roles,
        }
        rows.append(row)
        old = frozen.get(entry["program_id"])
        if old is None or old["predicted_safety"] != verdict or old["predicted_ea_roles"] != roles:
            diffs.append(entry["program_id"])

    # Safety metrics on determinate ground truth (UNKNOWN excluded, as in the archived report).
    det = [r for r in rows if r["gt_safety"] != "UNKNOWN" and r["pred_safety"] is not None]
    exact = sum(r["gt_safety"] == r["pred_safety"] for r in det)
    print(f"\nprograms analysed       : {len(rows)}  (failures: {failures})")
    print(f"determinate exact acc   : {exact}/{len(det)} = {exact / len(det):.3f}")
    for cls in ("SAFE", "UNSAFE"):
        tp = sum(r["gt_safety"] == cls and r["pred_safety"] == cls for r in det)
        fp = sum(r["gt_safety"] != cls and r["pred_safety"] == cls for r in det)
        fn = sum(r["gt_safety"] == cls and r["pred_safety"] != cls for r in det)
        p, rc, f = prf(tp, fp, fn)
        print(f"  {cls:<7} TP={tp:<3} FP={fp:<3} FN={fn:<3} P={p:.3f} R={rc:.3f} F1={f:.3f}")

    print("\nEA roles (all programs)")
    fs = []
    for role in ROLES:
        tp = sum(r["gt_roles"][role] and r["pred_roles"][role] for r in rows)
        fp = sum((not r["gt_roles"][role]) and r["pred_roles"][role] for r in rows)
        fn = sum(r["gt_roles"][role] and not r["pred_roles"][role] for r in rows)
        p, rc, f = prf(tp, fp, fn)
        fs.append((p, rc, f))
        print(f"  {role:<12} TP={tp:<4} FP={fp:<4} FN={fn:<4} P={p:.3f} R={rc:.3f} F1={f:.3f}")
    n = len(fs)
    print(f"  macro        P={sum(x[0] for x in fs) / n:.3f} R={sum(x[1] for x in fs) / n:.3f} F1={sum(x[2] for x in fs) / n:.3f}")

    ordered = sorted(times)
    print(f"\ntiming: mean {sum(times) / len(times):.4f}s  median {ordered[len(ordered) // 2]:.4f}s  max {ordered[-1]:.4f}s")
    print(f"predictions differing from archived run: {len(diffs)}")
    for pid in diffs[:10]:
        print("  ", pid)

    if args.json_output:
        Path(args.json_output).write_text(json.dumps({"dataset_hash": computed, "results": rows}, indent=1))

    return 0 if hash_ok and not diffs and not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
