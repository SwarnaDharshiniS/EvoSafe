"""Tests for the explicitly labeled EA-role benchmark and corpus-runner integration."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.evaluate_ea_benchmark import ROLE_NAMES, evaluate_manifest
from scripts.evaluate_ea_corpus import main as evaluate_corpus_main


MANIFEST = ROOT / "evaluation/ea_role_benchmark/benchmark.json"
HOLDOUT = ROOT / "evaluation/ea_role_benchmark_holdout"


class TestHeldOutBenchmarkLock(unittest.TestCase):
    def test_manifest_is_valid_and_fully_labeled(self):
        from scripts.evaluate_ea_benchmark import _validate_manifest

        manifest = json.loads((HOLDOUT / "benchmark.json").read_text())
        _validate_manifest(manifest)
        self.assertGreaterEqual(len(manifest["programs"]), 40)
        for program in manifest["programs"]:
            negative = program["negative_rationale"]
            if any(not v for v in program["ground_truth"].values()):
                self.assertTrue(isinstance(negative, str) or all(
                    negative.get(role) for role in ROLE_NAMES if not program["ground_truth"][role]
                ), program["name"])

    def test_labels_and_programs_match_lock(self):
        import hashlib

        lock = json.loads((HOLDOUT / "labels.lock.json").read_text())
        self.assertEqual(hashlib.sha256((HOLDOUT / "benchmark.json").read_bytes()).hexdigest(), lock["manifest_sha256"])
        on_disk = {f"programs/{p.name}" for p in (HOLDOUT / "programs").glob("*.py")}
        self.assertEqual(on_disk, set(lock["programs"]))
        for path, digest in lock["programs"].items():
            self.assertEqual(hashlib.sha256((HOLDOUT / path).read_bytes()).hexdigest(), digest, path)


class TestLabeledEABenchmark(unittest.TestCase):

    def test_benchmark_has_explicit_labels_and_rationale_for_every_role(self):
        report = evaluate_manifest(MANIFEST)
        self.assertEqual(report["program_count"], 18)
        for program in report["programs"]:
            self.assertEqual(set(program["ground_truth"]), set(ROLE_NAMES))
            self.assertEqual(set(program["rationale"]), set(ROLE_NAMES))
            self.assertTrue(all(isinstance(program["ground_truth"][role], bool) for role in ROLE_NAMES))
            self.assertTrue(all(program["rationale"][role].strip() for role in ROLE_NAMES))

    def test_previously_misclassified_benchmark_roles_now_match_ground_truth(self):
        fixed = {
            ("non_ea_indexed_writes", "population"),
            ("non_ea_indexed_writes", "mutation"),
            ("non_ea_indexed_writes", "crossover"),
            ("termination_helper", "crossover"),
            ("two_parent_crossover_helper", "crossover"),
            ("mutation_helper", "mutation"),
            ("alias_based_ea", "mutation"),
            ("unsafe_ea", "mutation"),
            ("deap_style_registration", "selection"),
            ("slice_replacement", "selection"),
        }
        programs = {program["program_name"]: program for program in evaluate_manifest(MANIFEST)["programs"]}
        for name, role in sorted(fixed):
            with self.subTest(program=name, role=role):
                program = programs[name]
                self.assertEqual(program["predictions"][role]["detected"], program["ground_truth"][role])
                if program["ground_truth"][role]:
                    self.assertTrue(all(item.get("line") for item in program["predictions"][role]["evidence"]))

    def test_metrics_are_computed_per_role_and_macro_averaged(self):
        report = evaluate_manifest(MANIFEST)
        for role in ROLE_NAMES:
            metric = report["metrics"]["per_role"][role]
            self.assertEqual(metric["tp"] + metric["fn"], sum(p["ground_truth"][role] for p in report["programs"]))
            self.assertEqual(metric["fp"] + metric["tn"], sum(not p["ground_truth"][role] for p in report["programs"]))
            self.assertIsNotNone(metric["precision"])
            self.assertIsNotNone(metric["recall"])
            self.assertIsNotNone(metric["f1"])
        self.assertEqual(report["metrics"]["macro_average"]["roles_included"], 7)

    def test_safety_statuses_are_unchanged_with_and_without_ea(self):
        report = evaluate_manifest(MANIFEST)
        self.assertTrue(report["safety_separation"]["all_checks_pass"])
        self.assertEqual(report["safety_separation"]["safe_ea"]["with_ea"], "SAFE")
        self.assertEqual(report["safety_separation"]["unsafe_ea"]["with_ea"], "UNSAFE")
        unknown = report["safety_separation"]["unknown_parse_status"]
        self.assertEqual(unknown["status_without_ea"], "UNKNOWN")
        self.assertEqual(unknown["status_with_ea"], "UNKNOWN")
        self.assertTrue(unknown["unchanged"])

    def test_corpus_runner_writes_benchmark_outputs_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            args = [
                "evaluation/ea_role_benchmark/programs/direct_ea.py",
                "--json-output", str(output / "corpus.json"),
                "--csv-output", str(output / "corpus.csv"),
                "--summary-output", str(output / "corpus.md"),
                "--comparison-json", str(output / "comparison.json"),
                "--comparison-summary", str(output / "comparison.md"),
                "--benchmark-manifest", "evaluation/ea_role_benchmark/benchmark.json",
                "--benchmark-json", str(output / "benchmark.json"),
                "--benchmark-csv", str(output / "benchmark.csv"),
                "--benchmark-summary", str(output / "benchmark.md"),
                "--skip-independence-check",
            ]
            self.assertEqual(evaluate_corpus_main(args), 0)
            corpus = json.loads((output / "corpus.json").read_text(encoding="utf-8"))
            benchmark = json.loads((output / "benchmark.json").read_text(encoding="utf-8"))
            self.assertNotIn("benchmark_metrics", corpus["summary"])
            self.assertEqual(benchmark["program_count"], 18)
            self.assertIn("macro_average", benchmark["metrics"])
            self.assertTrue((output / "benchmark.csv").exists())
            self.assertTrue((output / "benchmark.md").exists())


if __name__ == "__main__":
    unittest.main()
