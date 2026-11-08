# EvoSafe — Implementation Guide 

**Language:** Python 3.12 · **External dependency:** `networkx` (only for the CFG)

---

## 0. Summary

EvoSafe is a **static-analysis toolkit for Python programs**, aimed especially at **evolutionary-algorithm (EA) code**. *Static* means it **reads the source code without running it**. It turns the code into compiler-style representations (AST → CFG → Safety IR). On those it runs three independent safety analyses: **taint** (does untrusted input reach a dangerous function?), **capability** (does the code touch files, network, processes, or `eval`?) and **resource** (could it loop forever, recurse forever, or allocate huge memory?). A **rule-based decision engine** combines them into **SAFE / CONDITIONALLY_SAFE / UNSAFE**. The result can be sealed into a **hash-signed manifest**. An **optional EA-role inference module** then labels which parts of the code act as population, fitness, selection, mutation, crossover, replacement, and termination. Code that passes can be run through a **validation-gated sandbox** (subprocess or Docker).

---

## 1. Background primer 

### 1.1 Evolutionary algorithms (EA) 
An EA solves optimization problems the way natural selection works:

```
population = random candidates                     ← POPULATION
while not done:                                    ← TERMINATION
    scores  = [fitness(c) for c in population]     ← FITNESS EVALUATION
    parents = pick best/random-weighted ones       ← SELECTION
    kids    = combine(parent1, parent2)            ← CROSSOVER (recombination)
    kids    = randomly tweak(kids)                 ← MUTATION
    population = survivors + kids                  ← REPLACEMENT
```

| Role | Meaning | Typical code shape |
|---|---|---|
| Population | Collection of candidate solutions | `pop = [random_individual() for _ in range(N)]` |
| Fitness | Scores how good a candidate is | `score = f(ind)`, `sorted(pop, key=fitness)` |
| Selection | Picks parents/survivors | `sorted(...)[:k]`, `random.choice`, tournaments |
| Crossover | Builds a child from **two** parents | `child = p1[:cut] + p2[cut:]` |
| Mutation | Small random change to one candidate | `ind[i] = random.random()` |
| Replacement | New generation replaces the old one | `pop = survivors + children` |
| Termination | When to stop | `for gen in range(100)`, `while best < target` |

**Why EA code needs safety checking:** EA systems (especially genetic programming, or LLM-driven code evolution) often **generate and run code automatically**. Generated code can contain `eval`, `os.system`, infinite loops, or huge allocations. EvoSafe is a **gate** that checks code *before* it is executed.

### 1.2 Compiler concepts used
| Concept | Plain meaning | Where in EvoSafe |
|---|---|---|
| **Parsing / AST** (Abstract Syntax Tree) | Source text → tree of statements and expressions | `parser/ast_parser.py` (Python's built-in `ast` module) |
| **Basic block** | A run of statements with no jumps in or out except at its ends | `cfg/cfg_builder.py: BasicBlock` |
| **CFG** (Control-Flow Graph) | Graph whose nodes are basic blocks and whose edges are possible jumps (if/loop/try) | `cfg/cfg_builder.py` |
| **Data-flow analysis** | Tracks how values move through variables along the CFG | taint engine, `ea_inference/_data_flow.py` |
| **Taint analysis** | A data-flow analysis: mark untrusted input as "tainted", follow it, and alert if it reaches a dangerous "sink" | `analysis/taint/` |
| **Lattice / join / fixed point** | At merge points take the **union** of facts; repeat loops until nothing changes | `_merge_envs`, `_loop_fixed_point` |
| **Call graph** | Which function calls which; cycles in it mean recursion | `resource_estimator._build_call_graph` |
| **IR** (Intermediate Representation) | A structured, tool-friendly form of the program | `analysis/safety_ir/` |
| **Soundness vs precision** | Sound = never misses a real bug; precise = few false alarms. Practical tools trade one against the other | Discussed in §10 |

---

## 2. Overall architecture

```
                    Python source (file or --src string)
                                 │
              ┌──────────────────┴──────────────────┐
              │ CLI: main.py      Python API         │
              └──────────────────┬──────────────────┘
                                 ▼
                   ┌──────────────────────────┐
                   │ FRONT END                │
                   │ parser/ast_parser.py (AST)│
                   │ cfg/cfg_builder.py  (CFG)│
                   └─────────────┬────────────┘
        ┌────────────────────────┼─────────────────────────┐
        ▼                        ▼                         ▼
 ┌──────────────┐      ┌──────────────────┐      ┌──────────────────┐
 │ TAINT        │      │ CAPABILITY       │      │ RESOURCE         │
 │ source→sink  │      │ FS/NET/PROC/DYN  │      │ loops/recursion/ │
 │ data flow    │      │ import+call scan │      │ allocation       │
 └──────┬───────┘      └────────┬─────────┘      └────────┬─────────┘
        └──────────────┬────────┴─────────────────────────┘
                       ▼
          ┌──────────────────────────────┐
          │ DECISION ENGINE (rule-based)  │  + optional policies
          │ SAFE < CONDITIONALLY_SAFE <   │
          │ UNSAFE  (max of all rules)    │
          └──────────────┬───────────────┘
           ┌─────────────┼───────────────────┐
           ▼             ▼                   ▼
   Safety Manifest   Safety IR (JSON)   pipeline.AnalysisResult
   (SHA-256 digest)                           │
                                              │  (include_ea=True)
                                              ▼
                          EA-ROLE INFERENCE (enrichment ONLY,
                          never changes the verdict)

   Execution request ─► static validation gate ─► subprocess / Docker backend
                                 └── rejected ─► "validation failed" result
```

**Key design rule:** the safety verdict is computed **only** from taint + capability + resource. EA inference is computed *after* the verdict and can never change it (`analysis/pipeline.py`, `include_ea=False` by default).

---

## 3. Directory map — what each folder/file does

| Path | Responsibility |
|---|---|
| `main.py` | CLI. Parses arguments and dispatches to `ast`, `cfg`, `taint`, `caps`, `resource`, `manifest`, `safety-ir`. Contains no analysis logic itself (a "thin dispatcher"). |
| `parser/ast_parser.py` | Parses source and serializes the AST to JSON. |
| `parser/notebook_execution_parser.py` | Handles Jupyter notebook sources. |
| `cfg/cfg_builder.py` | Builds the CFG (`BasicBlock`, `CFG`, `CFGBuilder`, `build_cfg`). |
| `analysis/taint/_model.py` | Data model plus the **registries**: `SOURCES`, `SOURCE_ATTRS`, `SINKS`, `SANITIZERS`, `TAINT_PASSING_STR_METHODS`; `TaintTag`, `TaintFinding`, `ChainStep`. |
| `analysis/taint/taint_engine.py` | The taint analyzer (`TaintAnalyzer`). |
| `analysis/capability/_model.py` | `CapClass` (FS/NET/PROC/DYN), `Severity`, `CALL_SIGNALS`, `IMPORT_SIGNALS`, report classes. |
| `analysis/capability/capability_analyzer.py` | Two-pass AST visitor that resolves aliases and matches signals. |
| `analysis/resource/_model.py` | `ResourceFlag`, `ResourceReport`, `RiskLevel`. |
| `analysis/resource/resource_estimator.py` | Loop depth, call graph, recursion, unbounded-loop and allocation heuristics, risk score. |
| `analysis/decision/engine.py` | `SafetyDecisionEngine`, `SafetyPolicy` protocol, `ExternalAccessPolicy`. |
| `analysis/decision/execution_policy.py` | `ExecutionPolicy` plus the adapter `ExecutionPolicySafetyPolicy`. |
| `analysis/manifest/safety_manifest_generator.py` | Deterministic manifest with a SHA-256 digest. |
| `analysis/manifest/manifest_verifier.py` | Recomputes the digest and checks the manifest structure (tamper detection). |
| `analysis/safety_ir/_model.py`, `safety_ir_builder.py` | Combines everything into a single JSON IR. |
| `analysis/pipeline.py` | `analyze_program()`: the one-call combined report, with optional EA enrichment. |
| `analysis/ea_inference/` | EA-role inference (see §8). |
| `sandbox/execution_orchestrator.py` | Runs validated units via subprocess/Docker with time and resource limits; captures output, return code, and timing. |
| `sandbox/distributed_scheduler.py` | Scheduling of multiple units; skips units whose dependencies failed. |
| `tests/` | Unit and integration tests (`python3 -m unittest discover -s tests -v`). |
| `scripts/` | Corpus and benchmark evaluation runners. |
| `evaluation/ea_role_benchmark/` | 18 hand-labeled EA programs with seven-role ground truth. |
| `dataset/` | Corpora: benign algorithms (sorting, graphs, DP…), Python Cookbook examples, non-DEAP EA libraries (e.g. PyGAD). Each file has a `.metadata.json`. |
| `examples/` | `api_quickstart.py`, `quickstart.ipynb`. |

**Package convention:** each analysis package has `__init__.py` (public API), `_model.py` (data classes, private) and `*_engine/analyzer.py` (algorithm). This separates the **data model** from the **logic** and keeps the public API small.

---

## 4. End-to-end flow (one call)

`analysis/pipeline.py → analyze_program(source, include_ea=False, policies=None)`:

1. `analyze_taint(source)` → dict of findings
2. `analyze_capabilities(source)` → capability report
3. `analyze_resources(source)` → resource report
4. `SafetyDecisionEngine(policies).evaluate(taint, caps, resource)` → verdict
5. If `include_ea`: `analyze_ea_roles(source)` → role report
6. All evidence is merged into one list and **sorted** by (analysis, line, col, role, kind), so the output is **deterministic**.
7. Returns `AnalysisResult` → `.to_dict()`

CLI flow example: `python3 main.py taint file.py` → `cmd_taint` → read file → `taint_dict(source)` → print a summary or JSON.

---

## 5. Front end

### 5.1 AST (`parser/ast_parser.py`)
- Uses Python's standard `ast.parse`. **Why:** it's the official grammar, it's always correct for the running Python version, and there's nothing to maintain.
- Alternatives: `libcst` (keeps formatting and comments), `tree-sitter` (multi-language, error-tolerant), `astroid` (adds type inference, used by pylint).
- Syntax errors are **raised, not hidden**. The CLI prints `error: syntax error`.

### 5.2 CFG (`cfg/cfg_builder.py`)
**Data model:**
- `BasicBlock(id, stmts, kind, label)`, where kind ∈ `entry, exit, sequence, branch, loop_header, loop_exit`
- `CFG` wraps a `networkx.DiGraph`. Edge labels: `unconditional, true, false, loop-body, loop-back, loop-exit, break, return, raise, exception, fallthrough`
- Queries: `loops()`, `branches()`, `loop_back_edges()`, `entry_block()`, `exit_block()`, `to_dict()`

**Algorithm** (`_process_stmts`): recursive descent over statements, keeping a set of **"live" predecessor blocks**, meaning blocks that still need an outgoing edge.
- Plain statement → appended to the current block
- `if` → a `branch` block, with the true body and the else body processed recursively; returns the union of both live sets
- `for`/`while` → a `loop_header`, the body, a `loop-back` edge to the header, and a `loop_exit` block; `break` is redirected to the loop exit
- `try` → an `exception` edge from the try block to each handler; `finally` takes all live paths
- `return`/`raise` → edge to the function's `exit`, and the live set becomes empty
- Nested `def`/`class` → treated as an **opaque** statement (you can build its CFG separately with `--function`)

**Why networkx:** ready-made graph algorithms (topological sort, cycle detection) and easy serialization.
**Alternatives:** `staticfg`, `py2cfg`, or CPython bytecode via the `dis` module (exact, but harder to map back to source lines).

---

## 6. The three safety analyses

### 6.1 Taint analysis (`analysis/taint/taint_engine.py`)
**Question it answers:** "Can user-controlled data reach a dangerous function?"
Example: `os.system(input())`, where `input()` is the **source** and `os.system` is the **sink**.

**Core data structure:** `TaintEnv = dict[variable → frozenset[TaintTag]]`.
A `TaintTag` records *where* the taint came from (kind, line, col, expression) plus the **chain of steps** it travelled. This gives the readable "Path:" output.

**Algorithm** (an *abstract interpreter*, which "executes" the code over taint sets instead of real values):
| Construct | Rule |
|---|---|
| Constant | clean (∅) |
| Variable | look up env |
| `a + b`, f-string, list/dict/tuple | **union** of the children's taint |
| Comparison `a < b` | ∅ (produces a bool, which isn't injectable) |
| Source call (`input()`, `sys.argv`, `os.environ`, …) | a fresh TaintTag |
| Sanitizer call | ∅ (taint removed) |
| String methods (`strip`, `join`, …) | pass taint through |
| Sink call with a tainted argument | **emit a TaintFinding** (severity from the `SINKS` table) |
| Unknown call | conservatively, the return value carries the arguments' taint |
| `if` / `try` | copy the env per branch, then **merge (union)** = lattice join |
| Loops | repeat the body until env stops changing (**fixed point**), max `MAX_LOOP_ITERS = 3` |
| User-defined function call | **inline** the callee with the parameters' taint, up to `MAX_CALL_DEPTH = 2` (limited inter-procedural analysis) |
| Imports | alias tracking: `from sys import argv`, `import os as o` → `o.environ` |

**Properties:** flow-sensitive (statement order matters), intra-procedural with bounded inlining, path-insensitive (branches are merged, so conditions aren't tracked).

**Why this design:** it's simple, fast, explainable (it produces a path for every finding), and needs no external solver.
**What could be used instead:**
- **Worklist algorithm on the CFG** (the classic Kildall/monotone framework), which guarantees a true fixed point.
- **IFDS/IDE** (Reps–Horwitz–Sagiv): precise inter-procedural taint, as used in FlowDroid.
- **Existing tools:** Pysa (Meta), CodeQL, Bandit (pattern-based only), Semgrep taint mode.
- **Symbolic execution** (e.g. CrossHair) for path-sensitive results.

### 6.2 Capability analysis (`analysis/capability/capability_analyzer.py`)
**Question it answers:** "What *powers* does this code use?", even when no taint is present.
Classes: **FS** (files), **NET** (sockets/HTTP), **PROC** (subprocess/os.system), **DYN** (`eval`, `exec`, `compile`, `__import__`).

**Algorithm:** two passes over the AST using `ast.NodeVisitor`:
1. **Pass 1 (`_ImportCollector`)** builds alias tables:
   `import subprocess as sp` → `{"sp": "subprocess"}`; `from os import system as run_it` → `{"run_it": "os.system"}`.
2. **Pass 2** visits every `Call`, resolves its name through the alias tables to a canonical dotted name, and looks it up in `CALL_SIGNALS`. Imports are matched against `IMPORT_SIGNALS` using the **longest-prefix match** (`subprocess.Popen` → `subprocess`). Import findings are de-duplicated.

**Why two passes:** an alias may be used before (textually) or inside code that comes earlier in the walk. Collecting aliases first makes resolution independent of order.
**Limitation:** calls made purely by `getattr(os, "sys"+"tem")`, `importlib`, or other dynamic tricks can't be resolved statically. That's exactly why **DYN is treated as UNSAFE**.

### 6.3 Resource estimation (`analysis/resource/resource_estimator.py`)
**Question it answers:** "Could this code hang or exhaust memory?" Exact termination is **undecidable** (the Halting Problem), so the estimator uses **conservative heuristics**.

| Check | Method |
|---|---|
| Loop nesting depth | recursive AST walk counting `for`/`while` |
| CFG loop count | `CFGBuilder.build_module(...).loops()` |
| Call graph | function → called functions (simple names) |
| Recursion | DFS for a cycle back to the start node |
| Max call depth | memoized DFS; a cycle counts as depth 50 |
| `while True` | flag `while_true` |
| Unbounded while | `while` whose test isn't a comparison against a constant → `potentially_unbounded_loop` |
| Large range | `range(≥ 1,000,000)` → `large_range` |
| Large allocation | `list/bytearray/numpy.zeros(≥ 10,000,000)`, `[0] * 10**7` → `suspicious_allocation` |
| Recursion with no base case | no `if <arg> <cmp> <const>: return` → `recursive_no_base` |
| Complexity label | depth 1 → O(n), 2 → O(n²), recursion + loops → "≥ O(n²)", … |

**Risk score:** weighted points (hard-unbounded and large-range flags = 3, allocation = 2, depth ≥ 3 = 2, call depth ≥ 20 = 2, …). Score ≥ 8 → HIGH, ≥ 3 → MEDIUM, otherwise LOW.

**Alternatives:** ranking functions and termination provers (e.g. AProVE), abstract interpretation with interval domains, cost analysis (e.g. COSTA), or simply **runtime limits** (the sandbox does this as a second line of defense).

---

## 7. Decision, manifest, IR

### 7.1 Decision engine (`analysis/decision/engine.py`)
Verdicts form an ordered scale `SAFE(0) < CONDITIONALLY_SAFE(1) < UNSAFE(2)`, and the final verdict is the **maximum** of all rule outcomes (`_max_verdict`), so the most severe rule wins.

| Rule | Trigger | Verdict |
|---|---|---|
| `tainted_sink_flow` | taint total > 0 | UNSAFE |
| `dynamic_execution` | any DYN capability | UNSAFE |
| `unbounded_resource` | `while_true` / `recursive_no_base`, or risk HIGH | UNSAFE |
| `unbounded_resource` | other unbounded flags | CONDITIONALLY_SAFE |
| Policies (plug-ins) | e.g. `ExternalAccessPolicy`: FS/NET present and not allowed → CONDITIONALLY_SAFE; denied → UNSAFE | as returned |

**Design pattern:** `SafetyPolicy` is a **Protocol** (Strategy pattern). New policies can be added without editing the engine (Open/Closed principle). Reasons and rule hits are **sorted**, so the output is reproducible.
**Why rule-based rather than ML:** explainable, deterministic, auditable, and needs no training data. That matters for a *certifying* gate.

### 7.2 Safety manifest (`analysis/manifest/`)
- Normalizes (sorts) every sub-report, runs the decision with `ExternalAccessPolicy` (plus an optional `ExecutionPolicy`), and builds a dict.
- **Canonical JSON** (`sort_keys`, compact separators) → **SHA-256** = `manifest_digest`. It also stores per-input hashes.
- The default timestamp is the fixed epoch `1970-01-01T00:00:00Z`, so the **same code always gives the same digest**. That's what makes manifests reproducible and tamper-evident.
- `manifest_verifier.py` recomputes the digest to detect modification.
- Could be extended with: digital signatures (Ed25519/Sigstore) so the digest proves *who* produced it, not just integrity.

### 7.3 Safety IR (`analysis/safety_ir/`)
A "compiler-inspired" JSON document that unifies functions, loops, CFG info, taint flows, capabilities, evidence, and the decision. It's meant for downstream tools such as dashboards, schedulers, or the EA framework itself. Comparable ideas include SARIF (the standard static-analysis results format), which would be a good export target.

---

## 8. EA-role inference (`analysis/ea_inference/`)

### 8.1 Purpose
Given *any* EA code (hand-written, PyGAD-style, DEAP-style, no framework), the module finds **which lines play which EA role**, with evidence and a confidence level (HIGH/MEDIUM/LOW, which is **ordinal, not a probability**). It's **framework-independent**: it looks at *structure*, not library names. Function names like `crossover` are **not** accepted as evidence on their own.

### 8.2 Layered pipeline (`inference.py`)
```
source → ast.parse (+ optional CFG)
   │
   ▼ Layer 1  structural.py / _structure.py / _data_flow.py
   │   IntraProceduralDataFlow: bindings, aliases, collection mutations,
   │   helper-function summaries, registration/dispatch (DEAP-style toolbox)
   │   Facts: CollectionFact, CandidateFact
   ▼ Layer 2  lineage.py
   │   CandidateLineageFact: "this value was SELECTED_FROM / derived from
   │   one or TWO candidate sources"
   ▼ Layer 3  roles.py → detectors/*  (ordered!)
   │   Population → Fitness → RegisteredDispatch → bind element aliases
   │   → HelperSummary → Selection → Mutation → Crossover → Replacement
   │   → SurvivorSliceSelection → Termination
   ▼ Layer 4  evidence.py   (source-located evidence per role)
   ▼ Layer 5  summaries.py  → EAInferenceReport
```
Each layer imports only from earlier layers (a strict one-directional dependency), which keeps it testable.

### 8.3 Why the detector order matters
Detectors share a `RoleBindings` state. Selection needs to know `population_names`, which the Population detector produces. Replacement needs the selection and offspring names. Survivor-slice selection runs *after* replacement because it needs to see the population being rebuilt.

### 8.4 Example detector: Selection (`detectors/selection.py`)
Evidence types:
- `rank_or_filter`: `sorted/min/max/sample/choice/nlargest/...` applied to a population name. HIGH confidence if it's `sorted`/`sort` with `key=`, otherwise MEDIUM.
- `candidate_filter`: a comprehension over the population with an `if` condition.
- `candidate_lineage_selection`: a lineage fact of type `SELECTED_FROM_COLLECTION`.
- `survivor_slice`: `elite = pop[:k]`, then later `pop = elite + ...`

Crossover requires **two distinct candidate-derived sources** combined into one value. Mutation requires a candidate being modified or copied and changed. Termination is classified from loop structure.

### 8.5 Evaluation
`evaluation/ea_role_benchmark/` has 18 labeled programs (helpers, aliases, DEAP-style registration, comprehensions, two-parent crossover, …). Run them with `scripts/evaluate_ea_benchmark.py`. Per-role precision and recall describe *this set only*; it's small and pattern-focused.

---

## 9. Sandbox (`sandbox/`)
1. A unit must first pass static validation (verdict and/or manifest).
2. The scheduler skips units whose dependencies failed.
3. Accepted units run on a **subprocess** backend (shares the host OS, so it's weaker) or a **Docker** backend (container isolation).
4. Timeout and resource limits are enforced; stdout, stderr, return code, timing, and status are captured.

**Defense in depth:** the static analysis can miss things, so runtime limits are a second barrier. Stronger options: gVisor, Firecracker microVMs, seccomp, nsjail, WebAssembly (Pyodide).

---

## 10. Design rationale

| Decision | Reason |
|---|---|
| Separate packages per analysis | Each one is independently testable and replaceable (single responsibility) |
| Analyses produce **facts**; only the decision engine produces **verdicts** | Separates measurement from judgment, and policies can change without touching the analyzers |
| EA inference kept outside verdicting | EA heuristics are uncertain; they must never make unsafe code look safe (or the reverse) |
| `_model.py` per package | Data classes separate from the algorithm; easy JSON serialization |
| Deterministic sorting and an epoch timestamp | Reproducible output and stable hashes (needed for certification) |
| Static, not dynamic | Running untrusted code to check whether it's safe is itself unsafe |
| Conservative (over-approximate) | For a safety gate, a false alarm is cheaper than a missed attack |
| Thin CLI | All logic is reusable from Python, and the CLI is just a wrapper |

---

## 11. Future work
- CFG-based worklist data flow with SSA form (precise def-use chains)
- Inter-procedural summaries for taint (IFDS)
- SARIF output for IDE/GitHub code-scanning integration
- Signed manifests (Sigstore)
- Interval abstract domain for loop bounds
- Larger labeled EA benchmark (DEAP, PyGAD, EvoTorch, LLM-generated code)
- Integration as a pre-execution hook in GP/LLM code-evolution loops

---