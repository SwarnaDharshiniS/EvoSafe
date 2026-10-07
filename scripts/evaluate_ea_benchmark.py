#!/usr/bin/env python3
"""Score EvoSafe EA-role inference against an explicitly labeled small benchmark.

Benchmark metrics are emitted in separate artifacts and never merged into the
unlabeled corpus evaluation. Programs are analyzed statically and are not run.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.safety_ir import build_safety_ir_from_source

DETECTOR_SOURCES = (
    "analysis/ea_inference/inference.py",
    "analysis/ea_inference/_data_flow.py",
    "analysis/ea_inference/_model.py",
    "analysis/ea_inference/_ast_utils.py",
    "analysis/ea_inference/structural.py",
    "analysis/ea_inference/lineage.py",
    "analysis/ea_inference/_context.py",
    "analysis/ea_inference/roles.py",
    "analysis/ea_inference/evidence.py",
    "analysis/ea_inference/summaries.py",
    "analysis/ea_inference/detectors/__init__.py",
    "analysis/ea_inference/detectors/cross_role.py",
    "analysis/ea_inference/detectors/population.py",
    "analysis/ea_inference/detectors/fitness.py",
    "analysis/ea_inference/detectors/selection.py",
    "analysis/ea_inference/detectors/mutation.py",
    "analysis/ea_inference/detectors/crossover.py",
    "analysis/ea_inference/detectors/replacement.py",
    "analysis/ea_inference/detectors/termination.py",
)

ROLE_NAMES = (
    "population",
    "fitness_evaluation",
    "selection",
    "mutation",
    "crossover",
    "replacement",
    "termination",
)


def detector_fingerprint() -> dict[str, str]:
    return {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in DETECTOR_SOURCES
    }


def _negative_rationale(program: dict[str, Any], role: str) -> str:
    negative = program["negative_rationale"]
    return negative[role] if isinstance(negative, dict) else negative


def _validate_manifest(manifest: dict[str, Any]) -> None:
    if not isinstance(manifest.get("programs"), list) or not manifest["programs"]:
        raise ValueError("benchmark manifest must contain a non-empty programs array")
    seen: set[str] = set()
    for program in manifest["programs"]:
        name = program.get("name")
        if not isinstance(name, str) or name in seen:
            raise ValueError(f"benchmark program names must be unique strings: {name!r}")
        seen.add(name)
        labels = program.get("ground_truth")
        if not isinstance(labels, dict) or set(labels) != set(ROLE_NAMES):
            raise ValueError(f"{name}: ground_truth must explicitly label all seven roles")
        if not all(isinstance(labels[role], bool) for role in ROLE_NAMES):
            raise ValueError(f"{name}: every role ground_truth value must be boolean")
        negative = program.get("negative_rationale")
        if isinstance(negative, dict):
            missing = [role for role in ROLE_NAMES if not labels[role] and not str(negative.get(role, "")).strip()]
            if missing:
                raise ValueError(f"{name}: negative roles {missing} require a negative rationale")
        elif not isinstance(negative, str) or not negative.strip():
            raise ValueError(f"{name}: negative_rationale is required")
        positives = program.get("positive_rationale", {})
        for role in ROLE_NAMES:
            if labels[role] and not str(positives.get(role, "")).strip():
                raise ValueError(f"{name}: positive role {role} requires a positive rationale")


def _metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    role_metrics: dict[str, Any] = {}
    for role in ROLE_NAMES:
        tp = fp = fn = tn = 0
        for record in records:
            actual = record["ground_truth"][role]
            predicted = record["predictions"][role]["detected"]
            if actual and predicted:
                tp += 1
            elif not actual and predicted:
                fp += 1
            elif actual and not predicted:
                fn += 1
            else:
                tn += 1
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision is not None and recall is not None and precision + recall
            else 0.0 if precision is not None and recall is not None else None
        )
        role_metrics[role] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    available = [role_metrics[role] for role in ROLE_NAMES if role_metrics[role]["precision"] is not None]
    macro = {
        metric: sum(item[metric] for item in available) / len(available) if available else None
        for metric in ("precision", "recall", "f1")
    }
    macro["roles_included"] = len(available)
    return {"per_role": role_metrics, "macro_average": macro}


def _analyze_program(program: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    source_path = (manifest_path.parent / program["path"]).resolve()
    source = source_path.read_text(encoding="utf-8")
    enabled = build_safety_ir_from_source(
        source,
        source_name=program["name"],
        include_ea=True,
    ).to_dict()
    disabled = build_safety_ir_from_source(
        source,
        source_name=program["name"],
        include_ea=False,
    ).to_dict()
    roles = enabled["ea_roles"]["roles"]
    ground_truth = dict(program["ground_truth"])
    positive_rationale = program.get("positive_rationale", {})
    rationale = {
        role: positive_rationale[role] if ground_truth[role] else _negative_rationale(program, role)
        for role in ROLE_NAMES
    }
    return {
        "program_name": program["name"],
        "path": program["path"],
        "category": program.get("category", "unclassified"),
        "safety_expectation": program.get("safety_expectation"),
        "safety_verdict": enabled["verdict_hint"],
        "safety_verdict_without_ea": disabled["verdict_hint"],
        "safety_verdict_unchanged": enabled["verdict_hint"] == disabled["verdict_hint"],
        "ground_truth": ground_truth,
        "rationale": rationale,
        "predictions": {
            role: {
                "detected": bool(roles[role]["detected"]),
                "confidence": roles[role]["confidence"],
                "evidence": roles[role]["evidence"],
                "reason": roles[role]["reason"],
            }
            for role in ROLE_NAMES
        },
    }


def _unknown_safety_check() -> dict[str, Any]:
    """Treat parse failure as harness UNKNOWN; neither analyzer returns a verdict."""
    invalid_source = "def broken(:\n    pass\n"
    outcomes: list[str] = []
    for include_ea in (False, True):
        try:
            result = build_safety_ir_from_source(invalid_source, source_name="<invalid>", include_ea=include_ea)
            outcomes.append(result.verdict_hint)
        except (SyntaxError, ValueError, TypeError):
            outcomes.append("UNKNOWN")
    return {
        "status_without_ea": outcomes[0],
        "status_with_ea": outcomes[1],
        "unchanged": outcomes[0] == outcomes[1],
        "note": "UNKNOWN here is the benchmark harness status for invalid syntax; the safety API raises before producing a verdict.",
    }


def _safety_separation(records: list[dict[str, Any]]) -> dict[str, Any]:
    examples = [
        record for record in records
        if record.get("safety_expectation") in {"SAFE", "UNSAFE"}
    ]
    result = {
        record["program_name"]: {
            "expected": record["safety_expectation"],
            "with_ea": record["safety_verdict"],
            "without_ea": record["safety_verdict_without_ea"],
            "unchanged": record["safety_verdict_unchanged"],
            "expectation_matches": record["safety_verdict"] == record["safety_expectation"],
        }
        for record in examples
    }
    result["unknown_parse_status"] = _unknown_safety_check()
    changed = [record["program_name"] for record in records if not record["safety_verdict_unchanged"]]
    result["all_programs_verdict_unchanged"] = {"checked": len(records), "changed": changed, "unchanged": not changed}
    return result


def evaluate_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _validate_manifest(manifest)
    records = [_analyze_program(program, manifest_path) for program in manifest["programs"]]
    safety = _safety_separation(records)
    checks = [value for key, value in safety.items() if key not in {"unknown_parse_status", "all_programs_verdict_unchanged"}]
    safety["all_checks_pass"] = all(
        item["unchanged"] and item["expectation_matches"] for item in checks
    ) and safety["unknown_parse_status"]["unchanged"] and safety["all_programs_verdict_unchanged"]["unchanged"]
    return {
        "schema_version": "1.0",
        "benchmark_name": manifest["name"],
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "detector_fingerprint": detector_fingerprint(),
        "program_count": len(records),
        "programs": records,
        "metrics": _metrics(records),
        "safety_separation": safety,
        "note": "These metrics apply only to this labeled benchmark. They are not corpus metrics and do not estimate generalization.",
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['benchmark_name']}",
        "",
        f"- Labeled programs: **{report['program_count']}**",
        "- Metrics are benchmark-only and are not merged with unlabeled corpus results.",
        "- Ground truth is explicit per program for all seven roles; each role includes a rationale whether positive or negative.",
        "",
        "## Per-role metrics",
        "",
        "| Role | TP | FP | FN | TN | Precision | Recall | F1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for role, metrics in report["metrics"]["per_role"].items():
        values = [metrics[name] for name in ("precision", "recall", "f1")]
        fmt = lambda value: "—" if value is None else f"{value:.3f}"
        lines.append(
            f"| {role} | {metrics['tp']} | {metrics['fp']} | {metrics['fn']} | {metrics['tn']} | "
            f"{fmt(values[0])} | {fmt(values[1])} | {fmt(values[2])} |"
        )
    macro = report["metrics"]["macro_average"]
    lines.extend([
        "",
        f"**Macro average** over {macro['roles_included']} roles: precision **{macro['precision']:.3f}**, recall **{macro['recall']:.3f}**, F1 **{macro['f1']:.3f}**.",
        "",
        "## Program-level findings",
        "",
    ])
    for record in report["programs"]:
        lines.append(f"### `{record['program_name']}` — {record['category']}")
        lines.append("")
        lines.append(
            f"Safety: **{record['safety_verdict']}** (without EA: {record['safety_verdict_without_ea']}; unchanged={record['safety_verdict_unchanged']})."
        )
        lines.append("")
        lines.append("| Role | Truth | Prediction | Confidence | Evidence / rationale |")
        lines.append("|---|---:|---:|---|---|")
        for role in ROLE_NAMES:
            prediction = record["predictions"][role]
            evidence = "<br>".join(
                f"line {item.get('line')}: {item.get('description')} (`{item.get('snippet') or ''}`)"
                for item in prediction["evidence"]
            ) or "No detector evidence."
            lines.append(
                f"| {role} | {record['ground_truth'][role]} | {prediction['detected']} | {prediction['confidence']} | "
                f"Truth: {record['rationale'][role]}<br>Evidence: {evidence} |"
            )
        lines.append("")
    lines.extend(["## Safety separation", ""])
    for name, check in report["safety_separation"].items():
        if name == "all_checks_pass":
            continue
        if name == "all_programs_verdict_unchanged":
            lines.append(
                f"- All {check['checked']} programs: verdict identical with and without EA inference = {check['unchanged']} (changed: {', '.join(check['changed']) or 'none'})."
            )
            continue
        if name == "unknown_parse_status":
            lines.append(
                f"- Invalid-syntax UNKNOWN harness status: {check['status_without_ea']} without EA, {check['status_with_ea']} with EA; unchanged={check['unchanged']}. {check['note']}"
            )
        else:
            lines.append(
                f"- `{name}`: expected {check['expected']}; observed {check['with_ea']} with EA / {check['without_ea']} without EA; unchanged={check['unchanged']}."
            )
    lines.extend([
        "",
        f"Overall benchmark safety-independence checks: **{'PASS' if report['safety_separation']['all_checks_pass'] else 'FAIL'}**.",
        "",
    ])
    return "\n".join(lines)


def _write_csv(path: Path, report: dict[str, Any]) -> None:
    columns = ["program_name", "path", "category", "safety_verdict", "safety_verdict_without_ea", "safety_verdict_unchanged"]
    for role in ROLE_NAMES:
        columns.extend((f"{role}_truth", f"{role}_detected", f"{role}_confidence", f"{role}_rationale", f"{role}_evidence"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record in report["programs"]:
            row: dict[str, Any] = {
                "program_name": record["program_name"],
                "path": record["path"],
                "category": record["category"],
                "safety_verdict": record["safety_verdict"],
                "safety_verdict_without_ea": record["safety_verdict_without_ea"],
                "safety_verdict_unchanged": record["safety_verdict_unchanged"],
            }
            for role in ROLE_NAMES:
                prediction = record["predictions"][role]
                row[f"{role}_truth"] = record["ground_truth"][role]
                row[f"{role}_detected"] = prediction["detected"]
                row[f"{role}_confidence"] = prediction["confidence"]
                row[f"{role}_rationale"] = record["rationale"][role]
                row[f"{role}_evidence"] = json.dumps(prediction["evidence"], sort_keys=True, ensure_ascii=False)
            writer.writerow(row)


def write_outputs(report: dict[str, Any], json_path: Path, csv_path: Path, markdown_path: Path) -> None:
    for path in (json_path, csv_path, markdown_path):
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        elif path.suffix == ".csv":
            _write_csv(path, report)
        else:
            path.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", default="evaluation/ea_role_benchmark/benchmark.json")
    parser.add_argument("--json-output", default="evaluation/ea_role_benchmark/results.json")
    parser.add_argument("--csv-output", default="evaluation/ea_role_benchmark/results.csv")
    parser.add_argument("--summary-output", default="evaluation/ea_role_benchmark/results.md")
    args = parser.parse_args(argv)
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    report = evaluate_manifest(manifest_path)
    write_outputs(report, Path(args.json_output), Path(args.csv_output), Path(args.summary_output))
    metrics = report["metrics"]
    print(f"Benchmark programs: {report['program_count']}")
    print(f"Macro: {metrics['macro_average']}")
    print(f"Safety separation: {'PASS' if report['safety_separation']['all_checks_pass'] else 'FAIL'}")
    return 0 if report["safety_separation"]["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
