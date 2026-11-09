"""Tests for the demo web service and API."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from webapp import service  # noqa: E402

try:
    from fastapi.testclient import TestClient  # noqa: E402

    from api.index import app  # noqa: E402

    HAVE_API = True
except Exception:  # fastapi / httpx not installed
    HAVE_API = False

UNSAFE = "import os\nos.system(input())\n"
EA = (ROOT / "webapp/examples.json").exists() and service.EXAMPLES[0]["source"]


class ServiceTests(unittest.TestCase):
    def test_every_analysis_runs_on_every_example(self):
        for ex in service.EXAMPLES:
            with self.subTest(example=ex["id"]):
                out = service.analyze(ex["source"], list(service.ANALYSES))
                self.assertEqual(set(out["analyses"]), set(service.ANALYSES))
                self.assertIn(out["verdict"]["verdict"], {"SAFE", "CONDITIONALLY_SAFE", "UNSAFE"})

    def test_unsafe_example_is_unsafe_with_taint_finding(self):
        out = service.analyze(UNSAFE, ["taint"])
        self.assertEqual(out["verdict"]["verdict"], "UNSAFE")
        self.assertEqual(out["analyses"]["taint"]["total"], 1)

    def test_ea_example_finds_roles_without_changing_verdict(self):
        with_ea = service.analyze(EA, ["ea_roles"])
        without = service.analyze(EA, ["taint"])
        self.assertEqual(with_ea["verdict"]["verdict"], without["verdict"]["verdict"])
        found = [k for k, v in with_ea["analyses"]["ea_roles"]["roles"].items() if v["detected"]]
        self.assertGreaterEqual(len(found), 4)

    def test_verdict_matches_review2_entry_point(self):
        """The demo must use the same Safety IR entry point as the Review 2 results."""
        from analysis.safety_ir import build_safety_ir_from_source

        src = "import os\nprint(os.listdir('.'))\n"
        direct = build_safety_ir_from_source(src, source_name="x.py", include_ea=False).decision["verdict"]
        self.assertEqual(service.analyze(src, ["taint"])["verdict"]["verdict"], direct)

    def test_syntax_error_reports_line(self):
        with self.assertRaises(service.InputError) as ctx:
            service.analyze("x = 1\ndef f(:\n  pass\n")
        self.assertEqual(ctx.exception.line, 2)

    def test_rejects_empty_unknown_and_oversized_input(self):
        for bad, analyses in (("   ", None), ("x = 1", ["nope"]), ("x" * (service.MAX_SOURCE_CHARS + 1), None), ("\n" * service.MAX_SOURCE_LINES, None)):
            with self.subTest(bad=bad[:10], analyses=analyses):
                with self.assertRaises(service.InputError):
                    service.analyze(bad, analyses)

    def test_deeply_nested_source_does_not_crash(self):
        nested = "x = " + "(" * 400 + "1" + ")" * 400
        try:
            service.analyze(nested, ["taint"])
        except service.InputError:
            pass  # a clear user-facing refusal is acceptable; an unhandled crash is not


@unittest.skipUnless(HAVE_API, "fastapi/httpx not installed")
class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_and_examples(self):
        self.assertEqual(self.client.get("/api/health").json()["status"], "ok")
        self.assertGreaterEqual(len(self.client.get("/api/examples").json()), 5)

    def test_analyze_ok(self):
        r = self.client.post("/api/analyze", json={"source": UNSAFE, "analyses": ["taint", "capability"]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["verdict"]["verdict"], "UNSAFE")

    def test_analyze_syntax_error_is_422_with_line(self):
        r = self.client.post("/api/analyze", json={"source": "def f(:\n pass", "analyses": ["taint"]})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()["line"], 1)

    def test_analyze_unknown_analysis_is_422(self):
        r = self.client.post("/api/analyze", json={"source": "x = 1", "analyses": ["nope"]})
        self.assertEqual(r.status_code, 422)

    def test_missing_source_is_rejected(self):
        self.assertEqual(self.client.post("/api/analyze", json={}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
