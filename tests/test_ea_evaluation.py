"""Tests for the static EA corpus evaluation utility."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.evaluate_ea_corpus import (
    ROLE_NAMES,
    _analyze,
    _classify,
    _comparison,
    _independence_check,
    _role_metrics,
    _reviewed_examples,
    _summary,
)


class TestCorpusEvaluation(unittest.TestCase):

    def test_framework_corpus_categories_are_location_based(self):
        self.assertEqual(
            _classify(ROOT / "dataset/deap/ga/onemax.py")["category"],
            "framework_specific_ea",
        )
        self.assertEqual(
            _classify(ROOT / "dataset/benign/algorithms/example.py")["category"],
            "benign_python_corpus",
        )
        self.assertEqual(
            _classify(ROOT / "Python/genetic_algorithm/basic_string.py")["category"],
            "generic_ea",
        )
        self.assertEqual(
            _classify(ROOT / "dataset/non_deap/pygad/example_custom_operators.py")["framework"],
            "PyGAD",
        )
        self.assertEqual(
            _classify(ROOT / "examples/api_quickstart.py")["category"],
            "unknown_uncertain",
        )

    def test_analysis_record_contains_requested_fields_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ea_case.py"
            path.write_text(
                "candidates = initialize()\n"
                "for candidate in candidates:\n"
                "    score = objective(candidate)\n",
                encoding="utf-8",
            )
            result = _analyze(path)
        self.assertEqual(result["safety_verdict"], "SAFE")
        for role in ROLE_NAMES:
            field = "fitness" if role == "fitness_evaluation" else role
            self.assertIn(f"{field}_detected", result)
            self.assertIn(f"{field}_confidence", result)
            self.assertIn("evidence", result[role])
        self.assertTrue(result["population_detected"])
        self.assertTrue(result["fitness_detected"])
        self.assertTrue(result["evidence"])

    def test_role_metrics_only_calculated_from_explicit_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.py"
            path.write_text("x = 1\n", encoding="utf-8")
            record = _analyze(path)
        self.assertIsNone(_role_metrics([record], None))
        labels = {
            record["program_name"]: {
                "population": False,
                "fitness_evaluation": False,
            }
        }
        metrics = _role_metrics([record], labels)
        self.assertEqual(metrics["population"]["true_negatives"], 1)
        self.assertEqual(metrics["population"]["precision"], 0.0)
        self.assertFalse(metrics["selection"]["metrics_available"])

    def test_safety_verdicts_unchanged_by_ea_inference(self):
        results = _independence_check()
        self.assertEqual(len(results), 5)
        for name, result in results.items():
            with self.subTest(case=name):
                self.assertTrue(result["verdict_unchanged"])
                self.assertTrue(result["expected_verdict_matches"])
        incomplete = results["ea_incomplete_recognition"]
        self.assertTrue(incomplete["detected_roles"])
        self.assertTrue(incomplete["not_detected_roles"])

    def test_manual_source_spot_check_reports_supported_misses(self):
        records = [
            _analyze(ROOT / "dataset/deap/ga/onemax.py"),
            _analyze(ROOT / "Python/genetic_algorithm/basic_string.py"),
        ]
        spot_check = _summary(records, None)["manual_spot_check"]
        self.assertIsNotNone(spot_check)
        self.assertEqual(spot_check["case_count"], 2)
        self.assertTrue(all(role["manually_labeled_positive_cases"] == 2 for role in spot_check["role_summary"].values()))
        for role, metrics in spot_check["role_summary"].items():
            detected = sum(record[role]["detected"] for record in records)
            self.assertEqual(metrics["true_positives"], detected)
            self.assertEqual(metrics["false_negatives"], 2 - detected)
            self.assertEqual(metrics["recall_on_manual_positive_cases"], detected / 2)

    def test_old_new_comparison_reports_detection_and_confidence_delta(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.py"
            path.write_text("x = 1\n", encoding="utf-8")
            current = _analyze(path)
        old = json.loads(json.dumps(current))
        old["population"].update({"detected": True, "confidence": "MEDIUM"})
        old["safety_verdict"] = "SAFE"
        current["population"].update({"detected": False, "confidence": "LOW"})
        current["safety_verdict"] = "SAFE"
        comparison = _comparison({"programs": [old], "summary": {"verdict_counts": {"SAFE": 1}}}, [current])
        population = comparison["role_comparison"]["population"]
        self.assertEqual(population["old_detections"], 1)
        self.assertEqual(population["new_detections"], 0)
        self.assertEqual(population["delta"], -1)
        self.assertEqual(population["old_confidence_distribution"], {"MEDIUM": 1})
        self.assertEqual(population["new_confidence_distribution"], {})
        self.assertEqual(comparison["safety_verdict_changes"], [])

    def test_manual_audit_lists_framework_and_ordinary_python_examples(self):
        paths = (
            ROOT / "dataset/deap/ga/onemax.py",
            ROOT / "Python/genetic_algorithm/basic_string.py",
            ROOT / "dataset/non_deap/pygad/example_custom_operators.py",
            ROOT / "dataset/non_deap/pymoo/algorithms/moo/nsga2/nsga2_custom.py",
            ROOT / "dataset/non_deap/mealpy/applications/keras/mha-hybrid-mlp-classification.py",
        )
        reviewed = _reviewed_examples([_analyze(path) for path in paths])
        self.assertGreaterEqual(len(reviewed), 5)
        pygad = next(item for item in reviewed if item["program_name"].endswith("example_custom_operators.py"))
        self.assertIn("mutation", pygad["role_evidence"])
        mealpy = next(item for item in reviewed if "mha-hybrid-mlp" in item["program_name"])
        self.assertEqual(mealpy["category_uncertainty"].split(";")[0], "population-based metaheuristic")

    def test_manual_review_flags_known_non_ea_pattern_sources(self):
        paths = (
            ROOT / "Python/machine_learning/astar.py",
            ROOT / "dataset/benign/algorithms/data_structures/arrays/sudoku_solver.py",
            ROOT / "dataset/benign/algorithms/data_structures/heap/binomial_heap.py",
        )
        reviewed = _reviewed_examples([_analyze(path) for path in paths])
        self.assertEqual(len(reviewed), 3)
        for item in reviewed:
            with self.subTest(program=item["program_name"]):
                self.assertTrue(item["false_positive_candidates"])
                self.assertFalse(item["manually_inspected_source_roles"])


if __name__ == "__main__":
    unittest.main()
