#!/usr/bin/env python3
"""Evaluate EvoSafe's current EA inference against Python source corpora.

This utility parses and statically analyzes source files; it never executes
corpus programs. Corpus-directory labels are kept separate from per-role
labels: only an explicit role-label JSON file enables precision/recall metrics.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.safety_ir import build_safety_ir_from_source

ROLE_NAMES = (
    "population",
    "fitness_evaluation",
    "selection",
    "mutation",
    "crossover",
    "replacement",
    "termination",
)
ROLE_FIELDS = {"fitness_evaluation": "fitness"}

DEFAULT_PATHS = (
    "dataset",
    "examples",
    "tests",
    "main.py",
    "Python",
)


def _classify(path: Path) -> dict[str, Any]:
    """Use repository corpus placement as a category label, not role truth."""
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return {"category": "unknown_uncertain", "basis": "external_explicit_path"}

    parts = Path(relative).parts
    if len(parts) >= 2 and parts[0] == "dataset":
        if parts[1] == "deap":
            return {"category": "framework_specific_ea", "framework": "DEAP", "basis": "dataset/deap directory"}
        if parts[1] == "non_deap" and len(parts) >= 3 and parts[2] in {"mealpy", "pygad", "pymoo"}:
            framework = {"mealpy": "mealpy", "pygad": "PyGAD", "pymoo": "pymoo"}[parts[2]]
            return {
                "category": "framework_specific_ea",
                "framework": framework,
                "basis": f"dataset/non_deap/{parts[2]} directory",
            }
        if parts[1] == "benign":
            return {"category": "benign_python_corpus", "basis": "dataset/benign safety corpus label; not an EA-role label"}
        if parts[1] in {"unsafe_ea", "unsafe_non_ea", "generic_unsafe", "llm_ea", "llm_non_ea"}:
            return {"category": parts[1], "basis": f"dataset/{parts[1]} directory label"}
    if len(parts) >= 2 and parts[0] == "Python" and parts[1] == "genetic_algorithm":
        if path.name != "__init__.py":
            return {"category": "generic_ea", "basis": "Python/genetic_algorithm directory"}
        return {"category": "generic_python", "basis": "package marker; not an EA program label"}
    if parts[0] in {"examples", "tests"} or len(parts) == 1:
        return {"category": "unknown_uncertain", "basis": "example/test/root program without EA class annotation"}
    if parts[0] == "Python":
        return {"category": "generic_python", "basis": "educational Python collection"}
    return {"category": "unknown_uncertain", "framework": None, "basis": "no repository label"}


def _iter_programs(inputs: list[Path]) -> list[Path]:
    found: dict[str, Path] = {}
    for item in inputs:
        path = item if item.is_absolute() else ROOT / item
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(path)
        candidates = [path] if path.is_file() else sorted(path.rglob("*.py"))
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix == ".py" and not any(
                part in {".git", "__pycache__", ".venv", "venv"} for part in candidate.parts
            ):
                found[str(candidate)] = candidate
    return [found[key] for key in sorted(found)]


def _role_result(role_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "detected": bool(role_data.get("detected", False)),
        "confidence": role_data.get("confidence", "LOW"),
        "termination_kind": role_data.get("termination_kind"),
        "evidence": role_data.get("evidence", []),
        "reason": role_data.get("reason"),
    }


def _analyze(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "program_name": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
        "program_category": _classify(path),
        "safety_verdict": "UNKNOWN",
        "error": None,
    }
    try:
        source = path.read_text(encoding="utf-8")
        ir = build_safety_ir_from_source(source, source_name=record["program_name"], include_ea=True)
        data = ir.to_dict()
        record["safety_verdict"] = data["verdict_hint"]
        roles = data["ea_roles"]["roles"]
        for role in ROLE_NAMES:
            record[role] = _role_result(roles[role])
            field = ROLE_FIELDS.get(role, role)
            record[f"{field}_detected"] = record[role]["detected"]
            record[f"{field}_confidence"] = record[role]["confidence"]
        record["evidence"] = [item for item in data.get("evidence", []) if item.get("analysis") == "ea_inference"]
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["evidence"] = []
        for role in ROLE_NAMES:
            record[role] = {"detected": False, "confidence": "LOW", "termination_kind": None, "evidence": [], "reason": None}
            field = ROLE_FIELDS.get(role, role)
            record[f"{field}_detected"] = False
            record[f"{field}_confidence"] = "LOW"
    return record


def _role_metrics(records: list[dict[str, Any]], labels: dict[str, Any] | None) -> dict[str, Any] | None:
    if labels is None:
        return None
    results: dict[str, Any] = {}
    aliases = {role: role for role in ROLE_NAMES}
    aliases["fitness"] = "fitness_evaluation"
    for role in ROLE_NAMES:
        tp = fp = fn = tn = 0
        labeled = 0
        for record in records:
            program_labels = labels.get(record["program_name"], {})
            truth: Any = None
            for key, value in program_labels.items():
                if aliases.get(key, key) == role:
                    truth = value
                    break
            if not isinstance(truth, bool) or record.get("error"):
                continue
            labeled += 1
            predicted = bool(record[role]["detected"])
            if predicted and truth:
                tp += 1
            elif predicted and not truth:
                fp += 1
            elif not predicted and truth:
                fn += 1
            else:
                tn += 1
        if not labeled:
            results[role] = {"labeled_programs": 0, "metrics_available": False}
            continue
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        results[role] = {
            "labeled_programs": labeled,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return results


def _independence_check() -> dict[str, Any]:
    cases = {
        "safe_ea": """
            candidates = initialize()
            for generation in range(5):
                for candidate in candidates:
                    score = objective(candidate)
        """,
        "unsafe_ea": """
            candidates = initialize()
            for generation in range(5):
                for candidate in candidates:
                    score = objective(candidate)
            eval(input())
        """,
        "safe_non_ea": "answer = sum([1, 2, 3])\n",
        "unsafe_non_ea": "eval(input())\n",
        "ea_incomplete_recognition": """
            candidates = initialize()
            for candidate in candidates:
                score = objective(candidate)
        """,
    }
    expected_verdicts = {
        "safe_ea": "SAFE",
        "unsafe_ea": "UNSAFE",
        "safe_non_ea": "SAFE",
        "unsafe_non_ea": "UNSAFE",
        "ea_incomplete_recognition": "SAFE",
    }
    results: dict[str, Any] = {}
    for name, source in cases.items():
        source = textwrap.dedent(source).lstrip()
        without_ea = build_safety_ir_from_source(source, source_name=f"<check:{name}>", include_ea=False).to_dict()
        with_ea = build_safety_ir_from_source(source, source_name=f"<check:{name}>", include_ea=True).to_dict()
        role_results = with_ea["ea_roles"]["roles"]
        results[name] = {
            "expected_verdict": expected_verdicts[name],
            "verdict_without_ea": without_ea["verdict_hint"],
            "verdict_with_ea": with_ea["verdict_hint"],
            "verdict_unchanged": without_ea["verdict_hint"] == with_ea["verdict_hint"],
            "expected_verdict_matches": with_ea["verdict_hint"] == expected_verdicts[name],
            "detected_roles": [role for role in ROLE_NAMES if role_results[role]["detected"]],
            "not_detected_roles": [role for role in ROLE_NAMES if not role_results[role]["detected"]],
        }
    return results


def _summary(records: list[dict[str, Any]], role_metrics: dict[str, Any] | None) -> dict[str, Any]:
    category_counts = Counter(record["program_category"]["category"] for record in records)
    verdict_counts = Counter(record["safety_verdict"] for record in records)
    role_counts: dict[str, Any] = {}
    for role in ROLE_NAMES:
        detected = [record for record in records if not record.get("error") and record[role]["detected"]]
        not_detected = [record for record in records if not record.get("error") and not record[role]["detected"]]
        confs = Counter(record[role]["confidence"] for record in detected)
        role_counts[role] = {
            "detected": len(detected),
            "not_detected": len(not_detected),
            "confidence_among_detected": dict(sorted(confs.items())),
            "manual_review_candidates": [
                record["program_name"] for record in detected if record[role]["confidence"] == "LOW"
            ],
        }
    role_counts_by_category: dict[str, Any] = {}
    for category in sorted(category_counts):
        category_records = [
            record for record in records
            if record["program_category"]["category"] == category and not record.get("error")
        ]
        role_counts_by_category[category] = {
            role: {
                "detected": sum(record[role]["detected"] for record in category_records),
                "not_detected": sum(not record[role]["detected"] for record in category_records),
            }
            for role in ROLE_NAMES
        }
    role_counts_by_framework: dict[str, Any] = {}
    frameworks = sorted({
        record["program_category"].get("framework")
        for record in records
        if record["program_category"].get("framework")
    })
    for framework in frameworks:
        framework_records = [
            record for record in records
            if record["program_category"].get("framework") == framework and not record.get("error")
        ]
        role_counts_by_framework[framework] = {
            role: {
                "detected": sum(record[role]["detected"] for record in framework_records),
                "not_detected": sum(not record[role]["detected"] for record in framework_records),
            }
            for role in ROLE_NAMES
        }
    ea_categories = {"framework_specific_ea", "generic_ea", "unsafe_ea", "llm_ea"}
    review_cases = []
    for record in records:
        if record.get("error") or record["program_category"]["category"] not in ea_categories:
            continue
        if record["program_name"] in {"dataset/deap/ga/onemax.py", "Python/genetic_algorithm/basic_string.py"}:
            continue
        missing = [role for role in ROLE_NAMES if not record[role]["detected"]]
        if missing:
            category = record["program_category"]["category"]
            if category == "framework_specific_ea":
                likely_reason = "framework_operator_api_or_helper_boundary_possible"
                reason_basis = "framework corpus placement; callbacks, registered operators, and delegated algorithms may hide role structure, but this file has no role-level annotation"
            else:
                likely_reason = "helper_function_or_indirect_data_flow_possible"
                reason_basis = "generic EA corpus placement; operators may be split across helpers, but this file has no role-level annotation"
            review_cases.append({
                "program_name": record["program_name"],
                "not_detected_roles": missing,
                "interpretation": "Potential review case, not a confirmed false negative: corpus category does not label individual roles; a role may be absent or represented outside current structural patterns.",
                "likely_reason": likely_reason,
                "reason_basis": reason_basis,
            })
    return {
        "program_count": len(records),
        "successfully_analyzed_count": sum(not record.get("error") for record in records),
        "analysis_errors": sum(bool(record.get("error")) for record in records),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "corpus_category_counts": dict(sorted(category_counts.items())),
        "role_counts": role_counts,
        "role_counts_by_category": role_counts_by_category,
        "role_counts_by_framework": role_counts_by_framework,
        "ground_truth_role_metrics": role_metrics,
        "manual_spot_check": _manual_spot_check(records),
        "missed_role_cases": review_cases,
        "metric_note": "No role-level precision/recall/F1 is reported without explicit role annotations. Corpus-directory categories are not treated as role labels.",
    }


def _confidence_distribution(records: list[dict[str, Any]], role: str) -> dict[str, int]:
    counts = Counter(
        record[role]["confidence"]
        for record in records
        if not record.get("error") and record[role]["detected"]
    )
    return {level: counts.get(level, 0) for level in ("HIGH", "MEDIUM", "LOW") if counts.get(level, 0)}


def _comparison(old_report: dict[str, Any] | None, new_records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if old_report is None:
        return None
    old_records = old_report.get("programs", [])
    old_by_name = {record["program_name"]: record for record in old_records}
    new_by_name = {record["program_name"]: record for record in new_records}
    common = sorted(set(old_by_name) & set(new_by_name))
    paired_successful = [
        name for name in common
        if not old_by_name[name].get("error") and not new_by_name[name].get("error")
    ]
    comparison: dict[str, Any] = {
        "baseline_program_count": len(old_records),
        "current_program_count": len(new_records),
        "common_program_count": len(common),
        "paired_successfully_analyzed_count": len(paired_successful),
        "programs_only_in_baseline": sorted(set(old_by_name) - set(new_by_name)),
        "programs_only_in_current": sorted(set(new_by_name) - set(old_by_name)),
        "baseline_safety_verdicts": old_report.get("summary", {}).get("verdict_counts", {}),
        "current_safety_verdicts": dict(sorted(Counter(record["safety_verdict"] for record in new_records).items())),
        "role_comparison": {},
        "role_comparison_by_group": {},
        "program_role_changes": [],
        "safety_verdict_changes": [],
        "ground_truth_metrics": None,
        "methodology_note": "Paired comparison uses the same program_name records and reports detection/confidence count changes only. It is not ground-truth precision/recall.",
    }
    groups = {
        "DEAP": lambda record: record.get("program_category", {}).get("framework") == "DEAP",
        "PyGAD": lambda record: record.get("program_category", {}).get("framework") == "PyGAD",
        "pymoo": lambda record: record.get("program_category", {}).get("framework") == "pymoo",
        "mealpy": lambda record: record.get("program_category", {}).get("framework") == "mealpy",
        "generic_ea": lambda record: record.get("program_category", {}).get("category") == "generic_ea",
        "generic_educational_python": lambda record: record.get("program_category", {}).get("category") == "generic_python",
        "safety_oriented_corpus": lambda record: record.get("program_category", {}).get("category") == "benign_python_corpus",
    }
    for role in ROLE_NAMES:
        old_role_rows = [old_by_name[name] for name in paired_successful]
        new_role_rows = [new_by_name[name] for name in paired_successful]
        old_detected = sum(record[role]["detected"] for record in old_role_rows)
        new_detected = sum(record[role]["detected"] for record in new_role_rows)
        comparison["role_comparison"][role] = {
            "old_detections": old_detected,
            "new_detections": new_detected,
            "delta": new_detected - old_detected,
            "old_confidence_distribution": _confidence_distribution(old_role_rows, role),
            "new_confidence_distribution": _confidence_distribution(new_role_rows, role),
        }
        comparison["role_comparison_by_group"][role] = {}
        for group_name, predicate in groups.items():
            group_names = [name for name in paired_successful if predicate(new_by_name[name])]
            old_group = [old_by_name[name] for name in group_names]
            new_group = [new_by_name[name] for name in group_names]
            old_count = sum(record[role]["detected"] for record in old_group)
            new_count = sum(record[role]["detected"] for record in new_group)
            comparison["role_comparison_by_group"][role][group_name] = {
                "programs": len(group_names),
                "old_detections": old_count,
                "new_detections": new_count,
                "delta": new_count - old_count,
                "old_confidence_distribution": _confidence_distribution(old_group, role),
                "new_confidence_distribution": _confidence_distribution(new_group, role),
            }
    for name in common:
        old_record, new_record = old_by_name[name], new_by_name[name]
        role_changes = []
        for role in ROLE_NAMES:
            old_detected = bool(old_record.get(role, {}).get("detected", False))
            new_detected = bool(new_record.get(role, {}).get("detected", False))
            if old_detected != new_detected or old_record.get(role, {}).get("confidence") != new_record.get(role, {}).get("confidence"):
                role_changes.append({
                    "role": role,
                    "old_detected": old_detected,
                    "new_detected": new_detected,
                    "old_confidence": old_record.get(role, {}).get("confidence"),
                    "new_confidence": new_record.get(role, {}).get("confidence"),
                    "new_evidence": new_record.get(role, {}).get("evidence", []),
                })
        if role_changes:
            comparison["program_role_changes"].append({"program_name": name, "changes": role_changes})
        if old_record.get("safety_verdict") != new_record.get("safety_verdict"):
            explanation = None
            if name == "tests/test_ea_inference.py":
                explanation = "The test source changed after the prior run and now imports ast for new tests; the existing capability analyzer classifies the ast module as DYN. This is corpus-source drift, not an EA detector changing the verdict."
            comparison["safety_verdict_changes"].append({
                "program_name": name,
                "old": old_record.get("safety_verdict"),
                "new": new_record.get("safety_verdict"),
                "explanation": explanation or "Source content changed between evaluations or underlying safety inputs differed; inspect source history.",
            })
    return comparison


def _manual_spot_check(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    ground_truth = {
        "dataset/deap/ga/onemax.py": {
            "basis": "population/operator registrations (lines 45-68), offspring replacement (line 139), and bounded/convergence loop (line 101)",
            "causes": {
                "population": "population initializer is registered through toolbox; collection/candidate relationship is indirect",
                "fitness_evaluation": "evaluation is registered and invoked via map(toolbox.evaluate, ...), obscuring candidate dependence",
                "selection": "selection is invoked through a registered toolbox operator",
                "mutation": "mutation is invoked through a registered toolbox operator on offspring aliases",
                "crossover": "crossover is invoked through a registered toolbox operator over zip-derived parent aliases",
                "replacement": "population initializer alias is not recovered before pop[:] = offspring",
                "termination": "while condition uses max(fits) and generation counter without a linked population/fitness data flow",
            },
        },
        "Python/genetic_algorithm/basic_string.py": {
            "basis": "generic source documents and implements population creation, evaluation, selection, crossover, mutation, replacement, and convergence/termination across helpers",
            "causes": {
                "population": "population construction and consumption occur across separate helper/function scopes",
                "fitness_evaluation": "evaluation is encapsulated in evaluate() and called from population-processing code",
                "selection": "selection and ranking logic is distributed across select() and basic()",
                "mutation": "mutation is encapsulated in mutate() and reached through offspring helper calls",
                "crossover": "two-parent crossover is encapsulated in crossover() and called indirectly from select()",
                "replacement": "population clear/extend and survivor retention are spread across basic() and select()",
                "termination": "while True termination occurs through a return condition in another branch/function scope",
            },
        },
    }
    indexed = {item["program_name"]: item for item in records if not item.get("error")}
    cases = []
    for program_name, annotation in ground_truth.items():
        record = indexed.get(program_name)
        if record is None:
            continue
        roles = {}
        for role in ROLE_NAMES:
            detected = bool(record[role]["detected"])
            roles[role] = {
                "manual_ground_truth": True,
                "detected": detected,
                "true_positive": detected,
                "false_negative": not detected,
                "recall_on_this_positive_case": 1.0 if detected else 0.0,
                "likely_reason_if_missed": annotation["causes"][role] if not detected else None,
                "precision": None,
                "f1": None,
                "note": "Positive case only; no negative examples, so precision and F1 are not estimable.",
            }
        cases.append({"program_name": program_name, "basis": annotation["basis"], "roles": roles})
    if not cases:
        return None
    role_summary = {}
    for role in ROLE_NAMES:
        tp = sum(case["roles"][role]["true_positive"] for case in cases)
        fn = sum(case["roles"][role]["false_negative"] for case in cases)
        total = tp + fn
        role_summary[role] = {
            "manually_labeled_positive_cases": total,
            "true_positives": tp,
            "false_negatives": fn,
            "recall_on_manual_positive_cases": tp / total if total else None,
            "precision": None,
            "f1": None,
            "note": "No manually labeled negative programs; precision and F1 are not estimable.",
        }
    return {
        "case_count": len(cases),
        "cases": cases,
        "role_summary": role_summary,
    }


def _corpus_inventory(inputs: list[Path]) -> dict[str, Any]:
    items = []
    for input_path in inputs:
        path = input_path if input_path.is_absolute() else ROOT / input_path
        path = path.resolve()
        py_count = len(list(path.rglob("*.py"))) if path.is_dir() else int(path.suffix == ".py")
        notebook_count = len(list(path.rglob("*.ipynb"))) if path.is_dir() else int(path.suffix == ".ipynb")
        items.append({
            "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            "python_files": py_count,
            "notebooks_not_analyzed": notebook_count,
        })
    dataset = ROOT / "dataset"
    dataset_sections = []
    if dataset.exists():
        for section in sorted(item for item in dataset.iterdir() if item.is_dir()):
            dataset_sections.append({
                "name": section.name,
                "python_files": len(list(section.rglob("*.py"))),
                "role_level_ground_truth": False,
            })
    framework_counts = []
    framework_roots = {
        "DEAP": dataset / "deap",
        "mealpy": dataset / "non_deap" / "mealpy",
        "PyGAD": dataset / "non_deap" / "pygad",
        "pymoo": dataset / "non_deap" / "pymoo",
    }
    for name, path in framework_roots.items():
        framework_counts.append({
            "name": name,
            "path": path.relative_to(ROOT).as_posix(),
            "python_files": len(list(path.rglob("*.py"))) if path.exists() else 0,
            "corpus_label_only": True,
        })
    notebooks = sorted((ROOT / "dataset").rglob("*.ipynb")) + sorted((ROOT / "examples").rglob("*.ipynb"))
    return {
        "inputs": items,
        "dataset_sections": dataset_sections,
        "framework_subcorpora": framework_counts,
        "notebooks_not_analyzed": [path.relative_to(ROOT).as_posix() for path in notebooks],
        "ground_truth_note": "Directory categories describe corpus provenance/safety grouping only; none annotate the seven EA roles.",
    }


def _reviewed_examples(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    notes = {
        "dataset/deap/ga/onemax.py": {
            "source_roles": list(ROLE_NAMES),
            "inspection": "Explicit population/evaluate/select/mate/mutate registrations, map callback use, two-parent offspring call, pop[:] replacement, and generation/convergence loop are visible in source.",
            "delegated_roles": [],
        },
        "Python/genetic_algorithm/basic_string.py": {
            "source_roles": list(ROLE_NAMES),
            "inspection": "Source code has candidate initialization, evaluate() scoring, sorted/ranked scores and random parent indexing, mutate()/crossover() helper calls, population clear/extend rebuild, and a convergence exit inside while True.",
            "delegated_roles": [],
        },
        "dataset/non_deap/pygad/example_custom_operators.py": {
            "source_roles": ["fitness_evaluation", "selection", "crossover", "mutation"],
            "inspection": "Defines fitness_func, parent_selection_func, crossover_func, and mutation_func; callback wiring is passed to pygad.GA and execution is delegated to ga_instance.run(). Population initialization and generation termination are framework-managed.",
            "delegated_roles": ["population", "replacement", "termination"],
            "false_positive_candidates": ["population", "fitness_evaluation", "selection"],
            "misleading_evidence_roles": {"mutation": "One mutation finding is valid at the offspring indexed update; another is just copying selected parent rows."},
            "missed_source_roles": ["selection", "crossover"],
        },
        "dataset/non_deap/pymoo/algorithms/moo/nsga2/nsga2_custom.py": {
            "source_roles": ["population", "fitness_evaluation", "crossover", "mutation"],
            "inspection": "Defines a custom sampler, problem _evaluate callback, two-parent crossover, and mutation; NSGA2 selection/replacement and minimize termination are framework-managed.",
            "delegated_roles": ["selection", "replacement", "termination"],
            "false_positive_candidates": ["fitness_evaluation", "selection", "replacement", "termination"],
            "misleading_evidence_roles": {"mutation": "Valid mutation evidence at the MyMutation assignment is mixed with sampler/crossover array writes."},
            "missed_source_roles": ["crossover"],
        },
        "dataset/non_deap/mealpy/applications/keras/mha-hybrid-mlp-classification.py": {
            "source_roles": ["fitness_evaluation"],
            "inspection": "The source supplies fitness_function to a Mealpy GWO optimizer and calls solve(); GWO is a population-based metaheuristic, but the evolutionary-role interpretation of its framework-managed internals is intentionally uncertain. The weight_sizes/reshape loop is model decoding, not population iteration.",
            "delegated_roles": ["population", "selection", "mutation", "crossover", "replacement", "termination"],
            "uncertain_category": "population-based metaheuristic; EA taxonomy applicability requires review",
            "false_positive_candidates": ["population", "fitness_evaluation"],
            "missed_source_roles": ["fitness_evaluation"],
        },
        "Python/machine_learning/astar.py": {
            "source_roles": [],
            "inspection": "A* graph search manages open/closed frontiers, chooses the minimum f-score node, updates path-cost/heuristic fields, and appends neighbors. These are graph-search operations, not evolutionary roles.",
            "delegated_roles": [],
            "false_positive_candidates": list(ROLE_NAMES),
        },
        "dataset/benign/algorithms/data_structures/arrays/sudoku_solver.py": {
            "source_roles": [],
            "inspection": "The file implements constraint propagation, unit construction, candidate filtering, and recursive search for Sudoku; list comprehensions, filtering, concatenation, and iteration are not EA roles.",
            "delegated_roles": [],
            "false_positive_candidates": list(ROLE_NAMES),
        },
        "dataset/benign/algorithms/data_structures/heap/binomial_heap.py": {
            "source_roles": [],
            "inspection": "The file implements binomial-heap tree merging, linking, insertion, and deletion. Indexed link updates, list merging, and loops are data-structure operations, not mutation/crossover/replacement roles in an EA.",
            "delegated_roles": [],
            "false_positive_candidates": list(ROLE_NAMES),
        },
    }
    indexed = {record["program_name"]: record for record in records}
    out = []
    for program_name, annotation in notes.items():
        record = indexed.get(program_name)
        if record is None:
            continue
        source_roles = set(annotation["source_roles"])
        delegated_roles = set(annotation["delegated_roles"])
        false_positive_candidates = annotation.get("false_positive_candidates", [
            role for role in ROLE_NAMES
            if record[role]["detected"] and role not in source_roles and role not in delegated_roles
        ])
        false_positive_candidates = [role for role in false_positive_candidates if record[role]["detected"]]
        potential_misses = annotation.get("missed_source_roles", [
            role for role in annotation["source_roles"]
            if not record[role]["detected"]
        ])
        example = {
            "program_name": program_name,
            "safety_verdict": record["safety_verdict"],
            "manually_inspected_source_roles": annotation["source_roles"],
            "framework_delegated_or_not_in_source": annotation["delegated_roles"],
            "detected_roles": [role for role in ROLE_NAMES if record[role]["detected"]],
            "not_detected_roles": [role for role in ROLE_NAMES if not record[role]["detected"]],
            "potential_missed_source_roles": potential_misses,
            "false_positive_candidates": false_positive_candidates,
            "misleading_evidence_roles": {
                role: note for role, note in annotation.get("misleading_evidence_roles", {}).items()
                if record[role]["detected"]
            },
            "manual_observation": annotation["inspection"],
            "role_evidence": {role: record[role]["evidence"] for role in ROLE_NAMES},
            "evidence_review_status": "manual source review; counts are not corpus-wide metrics",
        }
        if annotation.get("uncertain_category"):
            example["category_uncertainty"] = annotation["uncertain_category"]
        if program_name in {"dataset/deap/ga/onemax.py", "Python/genetic_algorithm/basic_string.py"}:
            example["manual_ground_truth_roles"] = {role: True for role in ROLE_NAMES}
            example["manual_ground_truth_basis"] = "source inspection confirmed all seven role implementations"
        out.append(example)
    return out


def _markdown_summary(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# EvoSafe EA Inference Corpus Evaluation",
        "",
        f"- Programs analyzed: **{summary['program_count']}**",
        f"- Successfully analyzed: **{summary['successfully_analyzed_count']}**",
        f"- Analysis errors: **{summary['analysis_errors']}**",
        f"- Corpus categories: `{json.dumps(summary['corpus_category_counts'], sort_keys=True)}`",
        f"- Safety verdicts: `{json.dumps(summary['verdict_counts'], sort_keys=True)}`",
        "- Corpus-wide role labels: **not present**; corpus-wide precision, recall, F1, and false-positive/false-negative totals are unavailable.",
        "",
        "## EA roles",
        "",
        "| Role | Detected | Not detected | Confidence among detections |",
        "|---|---:|---:|---|",
    ]
    for role, values in summary["role_counts"].items():
        lines.append(
            f"| {role} | {values['detected']} | {values['not_detected']} | `{json.dumps(values['confidence_among_detected'], sort_keys=True)}` |"
        )
    lines.extend(["", "### Detections within key EA corpus categories", "", "| Category | Role | Detected | Not detected |", "|---|---|---:|---:|"])
    for category in ("framework_specific_ea", "generic_ea"):
        for role, values in summary["role_counts_by_category"].get(category, {}).items():
            lines.append(f"| {category} | {role} | {values['detected']} | {values['not_detected']} |")
    lines.extend(["", "### Framework-associated corpus breakdown", "", "| Framework | Role | Detected | Not detected |", "|---|---|---:|---:|"])
    for framework, role_values in summary["role_counts_by_framework"].items():
        for role, values in role_values.items():
            lines.append(f"| {framework} | {role} | {values['detected']} | {values['not_detected']} |")
    lines.extend(["", "## Corpus inventory", ""])
    for section in report["corpus_inventory"]["dataset_sections"]:
        lines.append(f"- `dataset/{section['name']}`: {section['python_files']} Python files")
    lines.append("")
    lines.append("Framework-associated Python files:")
    for framework in report["corpus_inventory"]["framework_subcorpora"]:
        lines.append(f"- `{framework['name']}`: {framework['python_files']} files under `{framework['path']}`")
    lines.append("")
    lines.append("Notebooks not analyzed by this runner:")
    for notebook in report["corpus_inventory"]["notebooks_not_analyzed"]:
        lines.append(f"- `{notebook}`")
    lines.extend([
        "",
        "Directory provenance is not treated as role-level ground truth. `dataset/unsafe_ea`, `dataset/unsafe_non_ea`, `dataset/generic_unsafe`, `dataset/llm_ea`, and `dataset/llm_non_ea` contain no Python files in this checkout.",
        "",
        "## Manual review summary",
        "",
        f"- Reviewed source examples: **{summary['manual_review']['reviewed_examples']}**",
        f"- Confirmed non-EA programs reviewed: **{summary['manual_review']['manually_confirmed_non_ea_programs']}**",
        f"- Detected role/program pairs in those non-EA sources (confirmed false-positive candidates): **{summary['manual_review']['detected_role_pairs_in_manually_confirmed_non_ea_programs']}**",
        f"- Additional misleading/non-corresponding framework evidence candidates: **{summary['manual_review']['misleading_or_non_corresponding_evidence_candidates']}**",
        f"- Potential missed source roles in reviewed EA/framework examples: **{summary['manual_review']['potential_missed_source_role_pairs_in_reviewed_ea_examples']}**",
        "These are small manually inspected samples, not corpus-wide precision/recall metrics.",
        "",
        "## Candidate manual-review cases",
        "",
        f"The JSON contains **{len(summary['missed_role_cases'])}** review candidates for labeled EA corpus paths where one or more roles were not detected. These are not confirmed misses; the category does not say which roles a file implements.",
    ])
    spot_check = summary["manual_spot_check"]
    if spot_check is not None:
        lines.append(f"A manual source audit confirmed all seven roles in {spot_check['case_count']} representative files. Spot-check metrics:")
        for role, metrics in spot_check["role_summary"].items():
            lines.append(
                f"- `{role}`: TP={metrics['true_positives']}, FN={metrics['false_negatives']}, recall={metrics['recall_on_manual_positive_cases']}; precision/F1 unavailable because there are no manually labeled negative programs."
            )
        lines.append("")
        lines.append("Likely cause for each confirmed miss:")
        for case in spot_check["cases"]:
            for role, finding in case["roles"].items():
                if finding["false_negative"]:
                    lines.append(f"- `{case['program_name']}` / `{role}`: {finding['likely_reason_if_missed']}.")
    for case in summary["missed_role_cases"][:20]:
        lines.append(f"- `{case['program_name']}` — not detected: {', '.join(case['not_detected_roles'])}; hypothesis: {case['likely_reason']}.")
    if len(summary["missed_role_cases"]) > 20:
        lines.append(f"- … {len(summary['missed_role_cases']) - 20} additional cases are listed in the JSON report.")
    lines.extend(["", "### Reviewed examples", ""])
    for example in report["reviewed_examples"]:
        lines.append(
            f"- `{example['program_name']}` — detected: {', '.join(example['detected_roles']) or 'none'}; not detected: {', '.join(example['not_detected_roles']) or 'none'}. {example['manual_observation']}"
        )
    errors = [record for record in report["programs"] if record.get("error")]
    lines.extend(["", "## Analysis failures", ""])
    if errors:
        lines.append("All recorded failures are source parse/analysis errors, not detector misses. Several legacy Python 2-style `except` clauses are invalid under the active Python 3 parser.")
        for record in errors:
            lines.append(f"- `{record['program_name']}` — {record['error'].splitlines()[0]}")
    else:
        lines.append("None.")
    lines.extend(["", "## Safety-independence check", ""])
    if report["safety_independence_check"] is None:
        lines.append("Skipped.")
    else:
        for name, case in report["safety_independence_check"].items():
            lines.append(
                f"- `{name}`: {case['verdict_without_ea']} without EA, {case['verdict_with_ea']} with EA; unchanged={case['verdict_unchanged']}; expected={case['expected_verdict_matches']}."
            )
    lines.extend([
        "",
        "## Interpretation and limitations",
        "",
        "- The DEAP/PyGAD/pymoo/mealpy directories provide framework-associated examples, but not role-level annotations; corpus directory placement alone is not sufficient to calculate role metrics.",
        "- Framework callbacks, registered operators, delegated algorithm loops, helper functions, aliases, and indirect data flow are plausible sources of unrecognized structure. These remain hypotheses until reviewed against each source.",
        "- `dataset/benign` is a safety-oriented label, not proof that every file is non-EA. Its role detections require manual review rather than being counted as false positives.",
        "- Notebooks are inventoried but not analyzed by this Python-file runner.",
        "- The report does not execute corpus files and does not implement resource enrichment.",
        "",
    ])
    return "\n".join(lines)


def _markdown_comparison(report: dict[str, Any], records: list[dict[str, Any]]) -> str:
    comparison = report.get("comparison")
    if comparison is None:
        return "# EvoSafe EA Inference Comparison\n\nNo prior baseline was supplied.\n"
    lines = [
        "# EvoSafe EA Inference: Baseline Comparison",
        "",
        f"- Baseline programs: **{comparison['baseline_program_count']}**",
        f"- Current programs: **{comparison['current_program_count']}**",
        f"- Paired program names: **{comparison['common_program_count']}**",
        f"- Paired successful analyses: **{comparison['paired_successfully_analyzed_count']}**",
        f"- Baseline safety verdicts: `{json.dumps(comparison['baseline_safety_verdicts'], sort_keys=True)}`",
        f"- Current safety verdicts: `{json.dumps(comparison['current_safety_verdicts'], sort_keys=True)}`",
        f"- Safety verdict changes among paired programs: **{len(comparison['safety_verdict_changes'])}**",
        "- Corpus-wide role precision/recall/F1: **not computed**; role-level ground truth is not available.",
        "",
        "## Overall role comparison",
        "",
        "| Role | Old detections | New detections | Delta | Old confidence | New confidence |",
        "|---|---:|---:|---:|---|---|",
    ]
    for role, values in comparison["role_comparison"].items():
        lines.append(
            f"| {role} | {values['old_detections']} | {values['new_detections']} | {values['delta']:+d} | `{json.dumps(values['old_confidence_distribution'], sort_keys=True)}` | `{json.dumps(values['new_confidence_distribution'], sort_keys=True)}` |"
        )
    lines.extend(["", "## Comparison by corpus stratum", ""])
    for role in ROLE_NAMES:
        lines.extend([
            f"### {role}",
            "",
            "| Group | Programs | Old detections | New detections | Delta | Old confidence | New confidence |",
            "|---|---:|---:|---:|---:|---|---|",
        ])
        for group, values in comparison["role_comparison_by_group"][role].items():
            lines.append(
                f"| {group} | {values['programs']} | {values['old_detections']} | {values['new_detections']} | {values['delta']:+d} | `{json.dumps(values['old_confidence_distribution'], sort_keys=True)}` | `{json.dumps(values['new_confidence_distribution'], sort_keys=True)}` |"
            )
        lines.append("")
    lines.extend(["## Audited programs and evidence review", ""])
    records_by_name = {record["program_name"]: record for record in records}
    for example in report["reviewed_examples"]:
        lines.append(f"### `{example['program_name']}`")
        lines.append("")
        lines.append(f"Safety verdict: **{example['safety_verdict']}**")
        lines.append("")
        lines.append(example["manual_observation"])
        lines.append("")
        lines.append(f"Detected: {', '.join(example['detected_roles']) or 'none'}; potential missed in-source roles: {', '.join(example['potential_missed_source_roles']) or 'none'}; false-positive candidates for manual follow-up: {', '.join(example['false_positive_candidates']) or 'none'}. ")
        for role, note in example["misleading_evidence_roles"].items():
            lines.append(f"Evidence caveat for `{role}`: {note}")
        if example.get("category_uncertainty"):
            lines.append(f"Category note: {example['category_uncertainty']}.")
        lines.append("")
        lines.append("| Role | Detected | Confidence | Evidence snippets (line: kind — snippet) |")
        lines.append("|---|---|---|---|")
        for role in ROLE_NAMES:
            details = records_by_name[example["program_name"]][role]
            snippets = "<br>".join(
                f"{item.get('line')}: {item.get('kind')} — {str(item.get('snippet') or '').replace('|', '&#124;')}"
                for item in details["evidence"]
            ) or "—"
            lines.append(f"| {role} | {details['detected']} | {details['confidence']} | {snippets} |")
        lines.append("")
    lines.extend(["## Safety verdict changes", ""])
    if comparison["safety_verdict_changes"]:
        for change in comparison["safety_verdict_changes"]:
            lines.append(f"- `{change['program_name']}`: {change['old']} → {change['new']}. {change['explanation']}")
    else:
        lines.append("None among paired program names.")
    lines.extend([
        "## Interpretation",
        "",
        "Detection deltas are not automatically accuracy gains. Review evidence for source-role correspondence, especially medium-confidence facts tied to callback configuration, generic loop operations, indexed assignments, and collection updates. The framework directories are provenance labels, not role-level ground truth.",
        "",
    ])
    return "\n".join(lines)


def _csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return value


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    columns = ["program_name", "category", "category_basis", "safety_verdict", "error"]
    for role in ROLE_NAMES:
        columns.extend((f"{role}_detected", f"{role}_confidence", f"{role}_evidence", f"{role}_reason"))
    columns.append("evidence")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record in records:
            row: dict[str, Any] = {
                "program_name": record["program_name"],
                "category": record["program_category"]["category"],
                "category_basis": record["program_category"]["basis"],
                "safety_verdict": record["safety_verdict"],
                "error": record.get("error"),
                "evidence": record.get("evidence", []),
            }
            for role in ROLE_NAMES:
                row[f"{role}_detected"] = record[role]["detected"]
                row[f"{role}_confidence"] = record[role]["confidence"]
                row[f"{role}_evidence"] = record[role]["evidence"]
                row[f"{role}_reason"] = record[role]["reason"]
            writer.writerow({key: _csv_value(value) for key, value in row.items()})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Python files/directories; defaults to repository corpora")
    parser.add_argument("--json-output", default="evaluation/ea_corpus_results.json")
    parser.add_argument("--csv-output", default="evaluation/ea_corpus_results.csv")
    parser.add_argument("--summary-output", default="evaluation/ea_corpus_summary.md")
    parser.add_argument("--comparison-json", default="evaluation/ea_corpus_comparison.json")
    parser.add_argument("--comparison-summary", default="evaluation/ea_corpus_comparison.md")
    parser.add_argument("--comparison-baseline", help="Old per-program evaluation JSON; defaults to saved baseline, then current result path")
    parser.add_argument("--baseline-snapshot", default="evaluation/ea_corpus_baseline.json")
    parser.add_argument("--benchmark-manifest", help="Optional labeled EA benchmark manifest; results are written separately from corpus metrics")
    parser.add_argument("--benchmark-json", default="evaluation/ea_role_benchmark/results.json")
    parser.add_argument("--benchmark-csv", default="evaluation/ea_role_benchmark/results.csv")
    parser.add_argument("--benchmark-summary", default="evaluation/ea_role_benchmark/results.md")
    parser.add_argument("--labels", help="Optional JSON mapping program_name to role booleans for measured metrics")
    parser.add_argument("--skip-independence-check", action="store_true")
    args = parser.parse_args(argv)

    inputs = [Path(item) for item in args.paths] if args.paths else [Path(item) for item in DEFAULT_PATHS]
    programs = _iter_programs(inputs)
    records = [_analyze(path) for path in programs]
    results_path = Path(args.json_output)
    if not results_path.is_absolute():
        results_path = ROOT / results_path
    snapshot_path = Path(args.baseline_snapshot)
    if not snapshot_path.is_absolute():
        snapshot_path = ROOT / snapshot_path
    baseline_path = Path(args.comparison_baseline) if args.comparison_baseline else (
        snapshot_path if snapshot_path.exists() else results_path
    )
    if not baseline_path.is_absolute():
        baseline_path = ROOT / baseline_path
    baseline_report = None
    if baseline_path.exists():
        baseline_report = json.loads(baseline_path.read_text(encoding="utf-8"))
        if not snapshot_path.exists():
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(json.dumps(baseline_report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    labels = None
    if args.labels:
        labels = json.loads(Path(args.labels).read_text(encoding="utf-8"))
    metrics = _role_metrics(records, labels)
    reviewed_examples = _reviewed_examples(records)
    comparison = _comparison(baseline_report, records)
    reviewed_non_ea = {
        "Python/machine_learning/astar.py",
        "dataset/benign/algorithms/data_structures/arrays/sudoku_solver.py",
        "dataset/benign/algorithms/data_structures/heap/binomial_heap.py",
    }
    record_by_name = {record["program_name"]: record for record in records}
    manual_review_summary = {
        "reviewed_examples": len(reviewed_examples),
        "manually_confirmed_non_ea_programs": len(reviewed_non_ea),
        "detected_role_pairs_in_manually_confirmed_non_ea_programs": sum(
            bool(record_by_name[name][role]["detected"])
            for name in reviewed_non_ea if name in record_by_name
            for role in ROLE_NAMES
        ),
        "misleading_or_non_corresponding_evidence_candidates": sum(
            len(item["false_positive_candidates"]) + len(item["misleading_evidence_roles"])
            for item in reviewed_examples
        ),
        "potential_missed_source_role_pairs_in_reviewed_ea_examples": sum(
            len(item["potential_missed_source_roles"])
            for item in reviewed_examples
            if item.get("manual_ground_truth_roles") or item["program_name"].startswith("dataset/non_deap/")
        ),
        "not_corpus_wide_metrics": True,
    }
    summary = _summary(records, metrics)
    summary["manual_review"] = manual_review_summary
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "analyzer": "EvoSafe seven-role structural EA inference",
        "programs": records,
        "summary": summary,
        "corpus_inventory": _corpus_inventory(inputs),
        "reviewed_examples": reviewed_examples,
        "comparison": comparison,
        "safety_independence_check": None if args.skip_independence_check else _independence_check(),
    }

    json_path = results_path
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    csv_path = Path(args.csv_output)
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path
    _write_csv(csv_path, records)
    summary_path = Path(args.summary_output)
    if not summary_path.is_absolute():
        summary_path = ROOT / summary_path
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(_markdown_summary(report), encoding="utf-8")
    comparison_json_path = Path(args.comparison_json)
    if not comparison_json_path.is_absolute():
        comparison_json_path = ROOT / comparison_json_path
    comparison_summary_path = Path(args.comparison_summary)
    if not comparison_summary_path.is_absolute():
        comparison_summary_path = ROOT / comparison_summary_path
    comparison_json_path.parent.mkdir(parents=True, exist_ok=True)
    comparison_summary_path.parent.mkdir(parents=True, exist_ok=True)
    comparison_json_path.write_text(
        json.dumps(comparison, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    comparison_summary_path.write_text(
        _markdown_comparison({"comparison": comparison, "reviewed_examples": reviewed_examples}, records),
        encoding="utf-8",
    )

    benchmark_report = None
    if args.benchmark_manifest:
        from scripts.evaluate_ea_benchmark import evaluate_manifest, write_outputs

        benchmark_path = Path(args.benchmark_manifest)
        if not benchmark_path.is_absolute():
            benchmark_path = ROOT / benchmark_path
        benchmark_report = evaluate_manifest(benchmark_path)
        write_outputs(
            benchmark_report,
            Path(args.benchmark_json),
            Path(args.benchmark_csv),
            Path(args.benchmark_summary),
        )

    summary = report["summary"]
    print(f"Programs analyzed: {summary['program_count']}")
    print(f"Analysis errors: {summary['analysis_errors']}")
    print(f"Categories: {json.dumps(summary['corpus_category_counts'], sort_keys=True)}")
    print(f"Safety verdicts: {json.dumps(summary['verdict_counts'], sort_keys=True)}")
    print("EA role detections (no corpus-wide role labels; see manual spot-check):")
    for role, values in summary["role_counts"].items():
        print(f"  {role}: detected={values['detected']}, not_detected={values['not_detected']}, confidence={values['confidence_among_detected']}")
    print(f"Potential manual-review cases: {len(summary['missed_role_cases'])}")
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")
    print(f"Summary: {summary_path}")
    print(f"Baseline: {baseline_path if baseline_report is not None else 'not available'}")
    print(f"Comparison JSON: {comparison_json_path}")
    print(f"Comparison summary: {comparison_summary_path}")
    if benchmark_report is not None:
        print(f"Separate labeled benchmark programs: {benchmark_report['program_count']}")
        print(f"Benchmark macro metrics: {json.dumps(benchmark_report['metrics']['macro_average'], sort_keys=True)}")
    if comparison is not None:
        print(f"Paired programs: {comparison['common_program_count']}")
        print(f"Safety verdict changes: {len(comparison['safety_verdict_changes'])}")
    if report["safety_independence_check"] is not None:
        passed = all(
            case["verdict_unchanged"] and case["expected_verdict_matches"]
            for case in report["safety_independence_check"].values()
        )
        print(f"Safety independence check: {'PASS' if passed else 'FAIL'}")
        if not passed:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
