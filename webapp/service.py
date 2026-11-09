"""Run EvoSafe analyses on submitted source and return JSON-ready results.

This module only *analyses* source text. It never imports, executes or evaluates the
submitted program, and it does not expose the sandbox / execution orchestrator.
"""

from __future__ import annotations

import ast
import json
import time
from pathlib import Path
from typing import Any, Callable

from analysis.capability import analyze_to_dict as capability_dict
from analysis.ea_inference import analyze_ea_roles
from analysis.manifest import generate_manifest_from_source
from analysis.resource import analyze_to_dict as resource_dict
from analysis.safety_ir import build_safety_ir_from_source, safety_ir_to_json
from analysis.taint import analyze_to_dict as taint_dict
from cfg.cfg_builder import build_cfg
from parser.ast_parser import parse_source

EXAMPLES: list[dict[str, str]] = json.loads((Path(__file__).parent / "examples.json").read_text(encoding="utf-8"))

MAX_SOURCE_CHARS = 60_000
MAX_SOURCE_LINES = 2_000

ANALYSES: dict[str, str] = {
    "taint": "Taint flows",
    "capability": "Capabilities",
    "resource": "Resource risk",
    "ea_roles": "EA roles",
    "cfg": "Control-flow graph",
    "ast": "Syntax tree",
    "manifest": "Safety manifest",
    "safety_ir": "Safety IR",
}
DEFAULT_ANALYSES = ("taint", "capability", "resource", "ea_roles")


class InputError(ValueError):
    """The request cannot be analysed; the message is safe to show to the user."""

    def __init__(self, message: str, *, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.line = line
        self.column = column


def _cfg(source: str) -> dict[str, Any]:
    functions = build_cfg(source=source, function="*")
    return {
        "module": build_cfg(source=source).to_dict(),
        "functions": {name: cfg.to_dict() for name, cfg in functions.items()},
    }


def _safety_ir(source: str, name: str, include_ea: bool) -> dict[str, Any]:
    return json.loads(safety_ir_to_json(build_safety_ir_from_source(source, source_name=name, include_ea=include_ea)))


def validate(source: str, analyses: list[str]) -> list[str]:
    if not isinstance(source, str) or not source.strip():
        raise InputError("Paste some Python source to analyse.")
    if len(source) > MAX_SOURCE_CHARS:
        raise InputError(f"Source is too long ({len(source):,} characters). The demo accepts up to {MAX_SOURCE_CHARS:,}.")
    if source.count("\n") + 1 > MAX_SOURCE_LINES:
        raise InputError(f"Source has too many lines. The demo accepts up to {MAX_SOURCE_LINES:,}.")
    unknown = [a for a in analyses if a not in ANALYSES]
    if unknown:
        raise InputError("Unknown analysis: " + ", ".join(unknown) + ". Choose from: " + ", ".join(ANALYSES) + ".")
    chosen = list(dict.fromkeys(analyses)) or list(DEFAULT_ANALYSES)
    try:
        ast.parse(source)
    except SyntaxError as exc:
        raise InputError(f"Syntax error: {exc.msg}", line=exc.lineno, column=exc.offset) from exc
    except (RecursionError, MemoryError, ValueError) as exc:
        raise InputError("This source can't be parsed: it is too deeply nested or contains invalid characters.") from exc
    return chosen


def analyze(source: str, analyses: list[str] | None = None, name: str = "input.py") -> dict[str, Any]:
    """Run the selected analyses.

    Returns ``{"verdict": {...}, "analyses": {name: payload}, "timings_ms": {...}}``.
    The verdict always comes from the Safety IR decision (default external-access policy),
    the same entry point the Review 2 evaluation used.
    """
    chosen = validate(source, list(analyses or DEFAULT_ANALYSES))

    runners: dict[str, Callable[[], Any]] = {
        "taint": lambda: taint_dict(source),
        "capability": lambda: capability_dict(source, name=name),
        "resource": lambda: resource_dict(source, name=name),
        "ea_roles": lambda: analyze_ea_roles(source, source_name=name).to_dict(),
        "cfg": lambda: _cfg(source),
        "ast": lambda: parse_source(source),
        "manifest": lambda: generate_manifest_from_source(source, source_name=name),
        "safety_ir": lambda: _safety_ir(source, name, include_ea="ea_roles" in chosen),
    }

    timings: dict[str, float] = {}
    results: dict[str, Any] = {}

    def timed(key: str, fn: Callable[[], Any]) -> Any:
        t0 = time.perf_counter()
        try:
            return fn()
        except RecursionError as exc:
            raise InputError("This source is too deeply nested to analyse.") from exc
        finally:
            timings[key] = round((time.perf_counter() - t0) * 1000, 1)

    ir = timed("verdict", lambda: _safety_ir(source, name, include_ea=False))
    decision = ir["decision"]
    verdict = {
        "verdict": decision["verdict"],
        "reasons": decision.get("reasons", []),
        "rule_hits": decision.get("rule_hits", []),
        "policy_results": decision.get("policy_results", []),
        "resource_risk": ir.get("metadata", {}).get("resource_risk"),
        "taint_total": ir.get("metadata", {}).get("taint_total", 0),
        "capability_total": ir.get("metadata", {}).get("capability_total", 0),
    }
    for key in chosen:
        results[key] = timed(key, runners[key])

    return {"verdict": verdict, "analyses": results, "timings_ms": timings, "source_lines": source.count("\n") + 1}
