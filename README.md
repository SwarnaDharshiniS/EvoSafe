# EvoSafe

EvoSafe is a Python static-analysis toolkit for inspecting source structure, control flow, data flow, security-relevant behavior, and heuristic resource risks. It can produce individual analysis reports, deterministic safety manifests, and a structured Safety IR document for downstream tools.

The analyzers operate on source code; they do not need to import or execute the analyzed program. Static analysis is necessarily approximate. A `SAFE` verdict is the result of the configured rules and evidence, not a proof that arbitrary Python code is harmless.

## Capabilities

- **AST parsing:** parse Python source and serialize its syntax tree.
- **Control-flow graphs:** build module or function CFGs, including basic blocks and edges.
- **Taint analysis:** trace selected source values through code toward sensitive sinks.
- **Capability analysis:** identify filesystem, network, process, and dynamic-execution signals.
- **Resource estimation:** report heuristic risks related to loops, recursion, and call depth.
- **Safety decisions:** combine taint, capability, and resource reports, with optional policy hooks.
- **Safety manifests:** generate deterministic source-analysis summaries with a digest and rejection reasons.
- **Safety IR:** represent functions, loops, capabilities, CFG information, taint flows, evidence, and the safety decision in JSON.
- **Optional EA-role inference:** infer structural evolutionary-algorithm roles and candidate lineage. This enrichment is opt-in and does not participate in safety verdicting.
- **Sandboxed execution orchestration:** gate execution on static validation and run units through subprocess or Docker backends with configured limits. This is an execution facility, not a replacement for a hardened operating-system or container security boundary.

## Requirements

- Python 3.12 is the recommended development runtime.
- The CFG implementation uses `networkx`.

From the repository root, install the runtime dependency if it is not already available:

```bash
python3 -m pip install networkx
```

EvoSafe currently uses repository-local modules rather than a published/installable package configuration. Run the CLI and examples from the repository root.

## Command-Line Usage

The CLI entry point is `main.py`. Each command accepts either a source file or an inline source string with `--src`.

```bash
python3 main.py ast --src "answer = 40 + 2"
python3 main.py ast path/to/program.py

python3 main.py cfg --src $'for item in items:\n    process(item)'
python3 main.py cfg path/to/program.py --function calculate
python3 main.py cfg path/to/program.py --function "*"

python3 main.py taint --src "import os; os.system(input())"
python3 main.py caps path/to/program.py --json
python3 main.py resource path/to/program.py --json
python3 main.py manifest path/to/program.py --json
python3 main.py safety-ir path/to/program.py
```

### Commands

| Command | Purpose | Output |
|---|---|---|
| `ast` | Parse source and serialize the AST. | JSON |
| `cfg` | Build a module CFG or select one function with `--function NAME`; use `*` for all functions. | JSON |
| `taint` | Report supported source-to-sink data flows. | Human-readable summary or JSON with `--json` |
| `caps` | Report capability signals and their severity. | Human-readable summary or JSON with `--json` |
| `resource` | Report resource metrics and heuristic flags. | Human-readable summary or JSON with `--json` |
| `manifest` | Generate a deterministic safety manifest. | Summary or JSON with `--json` |
| `safety-ir` | Generate the structured Safety IR document. | JSON |

The `manifest` command accepts `--analysis-version` (default `1.0.0`) and `--timestamp`. If no timestamp is supplied, the manifest uses a deterministic epoch value. `safety-ir` accepts the same version option and defaults its timestamp to `1970-01-01T00:00:00Z`.

## Python API

Individual analyzers can be called directly. For a combined report, `analysis.pipeline.analyze_program` runs the existing safety analyzers and optionally attaches EA-role inference:

```python
from analysis.pipeline import analyze_program

source = """
def run(command):
	import os
	os.system(command)

run(input("command: "))
"""

report = analyze_program(source, source_name="sample.py", include_ea=True)
result = report.to_dict()
print(result["safety_facts"]["decision"]["verdict"])
print(result["ea_roles"]["roles"]["population"]["detected"])
```

`include_ea` defaults to `False`. EA findings are descriptive enrichment and are not input to the safety decision. The direct APIs are available from their modules, including `analysis.taint`, `analysis.capability`, `analysis.resource`, `analysis.manifest`, `analysis.safety_ir`, `analysis.ea_inference`, and `cfg`.

Run the complete API walkthrough with:

```bash
python3 examples/api_quickstart.py
```

The [quickstart notebook](examples/quickstart.ipynb) and [API example](examples/api_quickstart.py) provide additional examples.

## Verdict Semantics

The decision engine orders verdict severity as `SAFE`, `CONDITIONALLY_SAFE`, then `UNSAFE`. Taint findings and dynamic-execution signals can cause `UNSAFE`; high-risk unbounded resource patterns can cause `UNSAFE`, while other unbounded-resource findings can require review. Optional policies can make a result conditional or unsafe. Inspect the report’s evidence, rule hits, and reasons rather than interpreting the verdict as a formal proof.

EA inference is optional. It identifies structural roles such as population, fitness evaluation, selection, mutation, crossover, replacement, and termination. Confidence describes structural evidence strength, not a probability. Dynamic or unresolved flows may remain unknown or undetected.

## Tests

Run the repository test suite from the root:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover parsing, CFG construction, analyzers, decision policies, manifests, Safety IR, optional EA inference, and sandbox orchestration.

## Repository Layout

- `main.py` – CLI entry point.
- `parser/` – Python source and notebook parsing.
- `cfg/` – CFG construction.
- `analysis/` – taint, capability, resource, decision, manifest, Safety IR, pipeline, and optional EA inference.
- `sandbox/` – validation-gated execution orchestration and scheduling.
- `examples/` – API and notebook examples.
- `tests/` – unit and integration tests.
- `scripts/` – corpus and labeled-benchmark evaluation utilities.
- `evaluation/` – benchmark manifests and generated evaluation artifacts.
- `dataset/` – example corpora used for analysis and evaluation.
- `Python/` – a bundled Python-algorithm source tree used as corpus material; it is distinct from EvoSafe's analyzer implementation.

See [architecture.md](architecture.md) for the analysis pipeline, module boundaries, data flow, and trust boundaries.
