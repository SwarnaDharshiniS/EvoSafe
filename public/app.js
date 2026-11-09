"use strict";

const API = (window.EVOSAFE_API || "").replace(/\/$/, "");

const ANALYSES = [
  { id: "taint", label: "Taint flows", on: true },
  { id: "capability", label: "Capabilities", on: true },
  { id: "resource", label: "Resource risk", on: true },
  { id: "ea_roles", label: "EA roles", on: true },
  { id: "cfg", label: "Control-flow graph", on: false },
  { id: "ast", label: "Syntax tree", on: false },
  { id: "manifest", label: "Safety manifest", on: false },
  { id: "safety_ir", label: "Safety IR", on: false },
];

const ROLE_ORDER = [
  ["population", "Population"],
  ["fitness_evaluation", "Fitness"],
  ["selection", "Selection"],
  ["crossover", "Crossover"],
  ["mutation", "Mutation"],
  ["replacement", "Replacement"],
  ["termination", "Termination"],
];

const ROLE_HELP = {
  population: "A collection of candidate solutions that the program evolves.",
  fitness_evaluation: "Each candidate gets a score that depends on that candidate.",
  selection: "Better candidates are chosen to become parents or survivors.",
  crossover: "A new candidate is built from two parents.",
  mutation: "A copy of a candidate is changed at random.",
  replacement: "Offspring or survivors take over the active population.",
  termination: "A condition ends the evolution loop.",
};

const CATEGORY_NAME = { benign: "Ordinary programs", deap: "DEAP examples", non_deap: "Other EA libraries", generic_unsafe: "Unsafe, no EA", unsafe_ea: "Unsafe EA", unsafe_non_ea: "Unsafe, no EA (set 2)", llm_ea: "Generated EA programs", llm_non_ea: "Generated non-EA programs" };
const STEP_LABEL = { source: "starts at", assign: "stored in", call_arg: "passed to", return: "returned from", attribute: "read from", binop: "combined in", format: "formatted into" };

const state = { examples: [], result: null, source: "", activeTab: null, markers: new Map(), picked: null, stale: false, cfgFn: "<module>" };

/* ---------- tiny DOM helper (always textContent, never innerHTML, so analysed code can't inject markup) ---------- */
function el(tag, attrs, ...kids) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === false || v == null) continue;
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) {
    if (kid == null || kid === false) continue;
    node.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return node;
}
const $ = (id) => document.getElementById(id);
const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + "s"}`;
const pct = (x) => (x == null ? "n/a" : x.toFixed(3));

/* ---------- routing ---------- */
const VIEWS = ["analyze", "evaluation", "about"];
function route() {
  const name = (location.hash.replace(/^#\/?/, "") || "analyze").split("/")[0];
  const view = VIEWS.includes(name) ? name : "analyze";
  for (const v of VIEWS) $("view-" + v).hidden = v !== view;
  document.querySelectorAll("[data-nav]").forEach((a) => {
    if (a.dataset.nav === view) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  if (view === "evaluation") renderEvaluation();
  if (view === "about") renderAbout();
  document.title = view === "analyze" ? "EvoSafe" : `${view[0].toUpperCase() + view.slice(1)} · EvoSafe`;
}

/* ---------- editor ---------- */
const src = () => $("src");
function lineCount() { return src().value.split("\n").length; }

function paintEditor() {
  const n = lineCount();
  const gutter = $("gutter");
  const inner = $("hlinner");
  const frag = document.createDocumentFragment();
  const hfrag = document.createDocumentFragment();
  for (let i = 1; i <= n; i++) {
    const m = state.markers.get(i);
    const cls = m ? " m-" + m.cls : "";
    const row = el("div", { class: "gl" + cls, title: m ? m.texts.join("\n") : false }, String(i), el("i"));
    frag.append(row);
    const picked = state.picked === i ? " pick" : "";
    const err = state.errorLine === i ? " err" : "";
    hfrag.append(el("div", { class: "hr" + cls + picked + err }));
  }
  gutter.replaceChildren(frag);
  inner.replaceChildren(hfrag);
  syncScroll();
  $("lines").textContent = plural(n, "line");
}
function syncScroll() {
  const t = src();
  $("gutter").scrollTop = t.scrollTop;
  $("hlinner").style.transform = `translate(${-t.scrollLeft}px, ${-t.scrollTop}px)`;
}
function goToLine(line) {
  state.picked = line;
  paintEditor();
  const t = src();
  const target = (line - 1) * 20 - t.clientHeight / 2 + 40;
  t.scrollTop = Math.max(0, target);
  syncScroll();
}

function addMarker(line, cls, text) {
  if (!line) return;
  const rank = { high: 4, med: 3, ea: 2, low: 1 };
  const cur = state.markers.get(line) || { cls: "low", texts: [] };
  if (rank[cls] > rank[cur.cls] || !state.markers.has(line)) cur.cls = cls;
  cur.texts.push(text);
  state.markers.set(line, cur);
}
const sevCls = (s) => (s === "CRITICAL" || s === "HIGH" ? "high" : s === "MEDIUM" ? "med" : "low");

function computeMarkers(res) {
  state.markers = new Map();
  const a = res.analyses;
  if (a.taint) for (const f of a.taint.findings) {
    addMarker(f.location.line, sevCls(f.severity), f.message.replace(/^\[[A-Z]+\]\s*/, ""));
    for (const s of f.sources) addMarker(s.line, "med", `Untrusted input: ${s.expr}`);
  }
  if (a.capability) for (const uses of Object.values(a.capability.by_capability)) for (const u of uses) {
    if (u.line) addMarker(u.line, sevCls(u.severity), `${u.cap_class}: ${u.symbol}`);
  }
  if (a.resource) for (const f of a.resource.flags) addMarker(f.line, "med", f.message);
  if (a.ea_roles) for (const [name, r] of Object.entries(a.ea_roles.roles)) {
    for (const ev of r.evidence || []) addMarker(ev.line, "ea", `EA ${name.replace("_", " ")}`);
  }
}

/* ---------- reasons in plain language ---------- */
function reasonText(code) {
  const [key, arg] = code.split(":");
  const n = Number(arg);
  switch (key) {
    case "taint_findings_present": return `${plural(n, "flow")} of untrusted data reach${n === 1 ? "es" : ""} a sensitive operation`;
    case "dynamic_execution_primitive_detected": return "Runs code that is built while the program runs (eval, exec or similar)";
    case "unbounded_resource_behavior_high_risk": return "A loop or recursion has no clear end";
    case "unbounded_resource_behavior": return "A loop or recursion may not end, so a person should review it";
    case "policy_check_required": {
      const what = { FS: "the file system", NET: "the network", PROC: "other processes", DYN: "dynamic code execution" }[arg] || arg;
      return `Uses ${what}, so a policy check is required before running`;
    }
    default: return code;
  }
}
const VERDICT_TEXT = {
  SAFE: ["Safe", "None of EvoSafe's rules found a problem. That is not a proof the code is harmless."],
  CONDITIONALLY_SAFE: ["Conditionally safe", "Safe only if the policy checks below pass before it runs."],
  UNSAFE: ["Unsafe", "At least one rule marks this program as unsafe."],
};

/* ---------- running an analysis ---------- */
function selected() { return [...document.querySelectorAll("#picks input:checked")].map((i) => i.value); }

async function run() {
  const source = src().value;
  const analyses = selected();
  if (!analyses.length) return showError("Choose at least one analysis to run.");
  const btn = $("run");
  btn.disabled = true;
  btn.textContent = "Analyzing…";
  $("syntax").hidden = true;
  state.errorLine = null;
  try {
    const resp = await fetch(API + "/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, analyses }),
    });
    const body = await resp.json().catch(() => ({}));
    if (resp.status === 422) {
      state.errorLine = body.line || null;
      const where = body.line ? ` (line ${body.line})` : "";
      $("syntax").textContent = (body.error || "This source can't be analysed.") + where;
      $("syntax").hidden = false;
      state.markers = new Map();
      paintEditor();
      if (body.line) goToLine(body.line);
      return;
    }
    if (resp.status === 404) throw new Error("The analysis service isn't available at /api/analyze.");
    if (!resp.ok) throw new Error(body.detail || `The server answered ${resp.status}.`);
    state.result = body;
    state.source = source;
    state.stale = false;
    state.picked = null;
    state.activeTab = defaultTab(body, analyses);
    computeMarkers(body);
    paintEditor();
    renderResults(true);
  } catch (err) {
    showError(`Couldn't get an analysis. ${err.message || ""} Try again in a moment.`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyze";
  }
}
function showError(text) {
  $("results").replaceChildren(el("div", { class: "empty", role: "alert" }, el("p", { class: "empty-title" }, "Something went wrong"), el("p", {}, text)));
}

/* Open on the most informative tab: findings first, then EA roles, then the first analysis chosen. */
function defaultTab(res, analyses) {
  const a = res.analyses;
  if (a.taint && a.taint.total) return "taint";
  if (a.capability && a.capability.summary.total_uses && res.verdict.verdict !== "SAFE") return "capability";
  if (a.resource && a.resource.flags.length) return "resource";
  if (a.ea_roles && Object.values(a.ea_roles.roles).some((r) => r.detected)) return "ea_roles";
  return analyses[0];
}

/* ---------- results ---------- */
function renderResults(animate) {
  const res = state.result;
  const v = res.verdict;
  const [word, sentence] = VERDICT_TEXT[v.verdict] || [v.verdict, ""];
  const band = el("section", { class: `verdict v-${v.verdict}${animate ? " reveal" : ""}`, "aria-label": "Verdict" },
    el("p", { class: "vword" }, word),
    el("p", { class: "vsub" }, sentence),
    v.reasons.length ? el("ul", { class: "vreasons" }, v.reasons.map((r) => el("li", { title: r }, reasonText(r)))) : null,
    el("p", { class: "vmeta" },
      el("span", {}, `${plural(res.source_lines, "line")} analysed in ${Object.values(res.timings_ms).reduce((a, b) => a + b, 0).toFixed(0)} ms`),
      el("span", {}, `Resource risk: ${(v.resource_risk || "n/a").toLowerCase()}`)),
    state.stale ? el("span", { class: "stale" }, "The code changed since this analysis. Run it again.") : null);

  const keys = Object.keys(res.analyses);
  const tablist = el("div", { class: "tabs", role: "tablist", "aria-label": "Analyses" },
    keys.map((k) => {
      const meta = ANALYSES.find((a) => a.id === k);
      const count = tabCount(k, res.analyses[k]);
      return el("button", {
        class: "tab", role: "tab", id: "tab-" + k, "aria-selected": String(k === state.activeTab), "aria-controls": "panel", tabindex: k === state.activeTab ? "0" : "-1",
        onclick: () => { state.activeTab = k; renderResults(false); },
        onkeydown: (e) => tabKeys(e, keys),
      }, meta.label, count ? el("span", { class: "n" + (count.hot ? " hot" : "") }, String(count.n)) : null);
    }));
  const panel = el("div", { class: "panel", id: "panel", role: "tabpanel", "aria-labelledby": "tab-" + state.activeTab, tabindex: "0" }, renderPanel(state.activeTab, res.analyses[state.activeTab]));
  $("results").replaceChildren(band, tablist, panel);
}
function tabKeys(e, keys) {
  const i = keys.indexOf(state.activeTab);
  let j = null;
  if (e.key === "ArrowRight") j = (i + 1) % keys.length;
  if (e.key === "ArrowLeft") j = (i - 1 + keys.length) % keys.length;
  if (j == null) return;
  e.preventDefault();
  state.activeTab = keys[j];
  renderResults(false);
  $("tab-" + keys[j]).focus();
}
function tabCount(k, d) {
  if (k === "taint") return { n: d.total, hot: d.total > 0 };
  if (k === "capability") return { n: d.summary.total_uses, hot: false };
  if (k === "resource") return { n: d.flags.length, hot: false };
  if (k === "ea_roles") return { n: Object.values(d.roles).filter((r) => r.detected).length, hot: false };
  return null;
}
function renderPanel(k, d) {
  return { taint: panelTaint, capability: panelCapability, resource: panelResource, ea_roles: panelEA, cfg: panelCFG, ast: panelAST, manifest: panelManifest, safety_ir: panelIR }[k](d);
}

const lineBtn = (line) => (line ? el("button", { class: "lnk", type: "button", onclick: () => goToLine(line), "aria-label": `Go to line ${line}` }, `line ${line}`) : null);

function rawJson(data, name) {
  const text = JSON.stringify(data, null, 2);
  const shown = text.length > 250000 ? text.slice(0, 250000) + "\n… (truncated; download for the full file)" : text;
  const copy = el("button", { class: "btn2", type: "button", onclick: async (e) => { try { await navigator.clipboard.writeText(text); e.target.textContent = "Copied"; setTimeout(() => (e.target.textContent = "Copy JSON"), 1500); } catch { e.target.textContent = "Copy failed"; } } }, "Copy JSON");
  const dl = el("button", { class: "btn2", type: "button", onclick: () => {
    const url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
    const a = el("a", { href: url, download: `evosafe-${name}.json` }); document.body.append(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  } }, "Download JSON");
  return el("details", { class: "rawwrap" }, el("summary", {}, "Raw JSON"), el("div", { class: "rawbar" }, copy, dl), el("pre", { class: "raw", tabindex: "0" }, shown));
}

function panelTaint(d) {
  const wrap = el("div", {}, el("h3", {}, "Taint flows"), el("p", { class: "lead" }, "Follows values that come from outside the program, such as input(), to operations that could do damage with them."));
  if (!d.findings.length) wrap.append(el("p", { class: "none" }, "No untrusted data reaches a sensitive operation."));
  for (const f of d.findings) {
    const steps = f.taint_paths[0] || [];
    wrap.append(el("article", { class: "item" },
      el("div", { class: "item-head" }, el("span", { class: "sev " + sevCls(f.severity) }, f.severity.toLowerCase()), el("span", { class: "item-msg" }, f.message.replace(/^\[[A-Z]+\]\s*/, "")), lineBtn(f.location.line)),
      steps.length ? el("ol", { class: "path" },
        steps.map((s) => el("li", {}, el("span", { class: "k" }, STEP_LABEL[s.kind] || s.kind.replaceAll("_", " ")), el("code", {}, s.expr || s.variable || ""), lineBtn(s.line))),
        el("li", {}, el("span", { class: "k" }, "reaches"), el("code", {}, f.sink), lineBtn(f.location.line))) : null));
  }
  wrap.append(rawJson(d, "taint"));
  return wrap;
}

function panelCapability(d) {
  const wrap = el("div", {}, el("h3", {}, "Capabilities"), el("p", { class: "lead" }, "What the program can reach beyond its own memory: files, network, other processes and dynamic code."));
  const names = { FS: "File system", NET: "Network", PROC: "Processes", DYN: "Dynamic code" };
  const groups = Object.entries(d.by_capability);
  if (!groups.length) wrap.append(el("p", { class: "none" }, "No file, network, process or dynamic-code use found."));
  for (const [cap, uses] of groups) {
    wrap.append(el("section", { class: "cap-group" }, el("h4", {}, `${names[cap] || cap} (${uses.length})`),
      uses.map((u) => el("div", { class: "cap-row" }, el("span", { class: "sev " + sevCls(u.severity) }, u.severity.toLowerCase()), el("code", {}, u.symbol), el("span", {}, u.reason), lineBtn(u.line)))));
  }
  wrap.append(rawJson(d, "capability"));
  return wrap;
}

function panelResource(d) {
  const m = d.metrics;
  const wrap = el("div", {}, el("h3", {}, "Resource risk"), el("p", { class: "lead" }, "Heuristics for code that may run for too long or use too much memory."),
    el("dl", { class: "kv" },
      el("dt", {}, "Overall risk"), el("dd", {}, d.risk_score.toLowerCase()),
      el("dt", {}, "Loop nesting depth"), el("dd", {}, String(m.loop_nesting_depth)),
      el("dt", {}, "Recursion"), el("dd", {}, m.recursion_present ? "present" : "none"),
      el("dt", {}, "Loops that may not end"), el("dd", {}, m.potentially_unbounded_loops ? "yes" : "no"),
      el("dt", {}, "Deepest call chain"), el("dd", {}, String(m.max_function_call_depth)),
      el("dt", {}, "Complexity guess"), el("dd", {}, m.complexity_heuristic)));
  if (!d.flags.length) wrap.append(el("p", { class: "none" }, "No risky resource pattern found."));
  for (const f of d.flags) wrap.append(el("article", { class: "item" }, el("div", { class: "item-head" }, el("span", { class: "sev med" }, f.kind.replaceAll("_", " ")), el("span", { class: "item-msg" }, f.message), lineBtn(f.line)), f.evidence ? el("code", {}, f.evidence) : null));
  wrap.append(rawJson(d, "resource"));
  return wrap;
}

function panelEA(d) {
  const roles = d.roles;
  const wrap = el("div", {}, el("h3", {}, "Evolutionary-algorithm roles"), el("p", { class: "lead" }, "If the code looks like an evolutionary algorithm, these are the parts EvoSafe recognises. A lit step means structural evidence was found."),
    el("ol", { class: "loop", "aria-label": "Roles found" }, ROLE_ORDER.map(([k, label]) => {
      const r = roles[k];
      return el("li", { class: r && r.detected ? "on" : "" }, label, el("b", {}, r && r.detected ? r.confidence.toLowerCase() : "not found"));
    })));
  for (const [k, label] of ROLE_ORDER) {
    const r = roles[k];
    if (!r) continue;
    const body = el("div", { class: "body" }, el("p", {}, ROLE_HELP[k]));
    if (r.detected) {
      for (const ev of r.evidence || []) body.append(el("p", {}, ev.description || ev.kind, " ", lineBtn(ev.line)), ev.snippet ? el("code", { class: "snip" }, ev.snippet) : null);
      if (r.termination_kind) body.append(el("p", {}, "Ends by: " + String(r.termination_kind).toLowerCase().replaceAll("_", " ")));
    } else body.append(el("p", {}, r.reason || "No structural evidence found."));
    wrap.append(el("details", { class: "role" }, el("summary", {}, `${label}: ${r.detected ? "found (" + r.confidence.toLowerCase() + " confidence)" : "not found"}`), body));
  }
  wrap.append(el("p", { class: "caveat" }, "Confidence describes how strong the structural evidence is. It is not a probability. In the Review 2 evaluation these roles were found precisely but often missed, so treat “not found” as “not recognised”. EA roles never change the verdict."), rawJson(d, "ea-roles"));
  return wrap;
}

/* control-flow graph: layered layout */
function layoutCFG(cfg) {
  const ids = cfg.blocks.map((b) => b.id);
  const out = new Map(ids.map((i) => [i, []]));
  cfg.edges.forEach((e) => out.get(e.from)?.push(e));
  const entry = cfg.blocks.find((b) => b.kind === "entry") || cfg.blocks[0];
  const level = new Map(), onStack = new Set(), back = new Set();
  (function dfs(id, depth) {
    onStack.add(id);
    level.set(id, Math.max(level.get(id) ?? 0, depth));
    for (const e of out.get(id) || []) {
      if (onStack.has(e.to)) back.add(e);
      else if (!level.has(e.to) || level.get(e.to) < depth + 1) dfs(e.to, depth + 1);
    }
    onStack.delete(id);
  })(entry.id, 0);
  ids.forEach((i) => { if (!level.has(i)) level.set(i, 0); });
  const rows = new Map();
  ids.forEach((i) => { const l = level.get(i); (rows.get(l) || rows.set(l, []).get(l)).push(i); });
  const W = 210, H = 40, GX = 36, GY = 46;
  const maxCols = Math.max(...[...rows.values()].map((r) => r.length));
  const pos = new Map();
  for (const [l, r] of rows) r.forEach((id, i) => pos.set(id, { x: 20 + (i + (maxCols - r.length) / 2) * (W + GX), y: 16 + l * (H + GY) }));
  return { pos, back, W, H, width: 40 + maxCols * (W + GX), height: 32 + rows.size * (H + GY) };
}
function cfgSvg(cfg) {
  const NS = "http://www.w3.org/2000/svg";
  const mk = (t, a, ...k) => { const n = document.createElementNS(NS, t); for (const [x, y] of Object.entries(a || {})) n.setAttribute(x, y); k.forEach((c) => n.append(c)); return n; };
  const L = layoutCFG(cfg);
  const svg = mk("svg", { width: L.width, height: L.height, viewBox: `0 0 ${L.width} ${L.height}`, role: "img", "aria-label": "Control-flow graph" });
  svg.append(mk("defs", {}, mk("marker", { id: "arrow", viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" }, mk("path", { d: "M0 0L10 5L0 10z", fill: "#6c7e7a" }))));
  for (const e of cfg.edges) {
    const a = L.pos.get(e.from), b = L.pos.get(e.to);
    if (!a || !b) continue;
    const isBack = L.back.has(e);
    let d;
    if (isBack || b.y <= a.y) {
      const x = Math.max(a.x, b.x) + L.W + 14;
      d = `M${a.x + L.W} ${a.y + L.H / 2} C${x} ${a.y + L.H / 2} ${x} ${b.y + L.H / 2} ${b.x + L.W} ${b.y + L.H / 2}`;
    } else {
      const x1 = a.x + L.W / 2, y1 = a.y + L.H, x2 = b.x + L.W / 2, y2 = b.y;
      d = `M${x1} ${y1} C${x1} ${y1 + 24} ${x2} ${y2 - 24} ${x2} ${y2}`;
    }
    svg.append(mk("path", { d, class: "ed" + (isBack ? " back" : ""), "marker-end": "url(#arrow)" }));
    if (e.label && e.label !== "unconditional" && e.label !== "fallthrough") {
      const x = isBack ? Math.max(a.x, b.x) + L.W + 8 : (a.x + b.x) / 2 + L.W / 2 + 4;
      const y = isBack ? (a.y + b.y) / 2 + L.H / 2 : (a.y + L.H + b.y) / 2;
      svg.append(mk("text", { x, y, class: "el" }, document.createTextNode(e.label)));
    }
  }
  for (const b of cfg.blocks) {
    const p = L.pos.get(b.id);
    const dark = b.kind === "entry" || b.kind === "exit";
    const text = (b.label || (b.stmts && b.stmts[0]) || b.kind).split("\n")[0];
    const line = b.lines && b.lines.start ? `L${b.lines.start}${b.lines.end && b.lines.end !== b.lines.start ? "–" + b.lines.end : ""}  ` : "";
    const shown = (line + text).length > 30 ? (line + text).slice(0, 29) + "…" : line + text;
    svg.append(mk("rect", { x: p.x, y: p.y, width: L.W, height: L.H, rx: 7, class: "nd " + b.kind }),
      mk("text", { x: p.x + 10, y: p.y + L.H / 2 + 4, class: dark ? "on-dark" : "" }, document.createTextNode(shown)));
    svg.lastChild.previousSibling.append(mk("title", {}, document.createTextNode([b.kind, ...(b.stmts || [])].join("\n"))));
  }
  return svg;
}
function panelCFG(d) {
  const names = ["<module>", ...Object.keys(d.functions)];
  if (!names.includes(state.cfgFn)) state.cfgFn = "<module>";
  const get = (n) => (n === "<module>" ? d.module : d.functions[n]);
  const box = el("div", { class: "cfgbox", tabindex: "0" });
  const info = el("span", {});
  const draw = () => {
    const cfg = get(state.cfgFn);
    info.textContent = `${plural(cfg.summary.total_blocks, "block")}, ${plural(cfg.summary.total_edges, "edge")}, ${plural(cfg.summary.loops, "loop")}`;
    box.replaceChildren(cfg.blocks.length > 80 ? el("p", { class: "none" }, "This graph is too large to draw. Download the JSON instead.") : cfgSvg(cfg));
  };
  const sel = el("select", { "aria-label": "Function", onchange: (e) => { state.cfgFn = e.target.value; draw(); } }, names.map((n) => el("option", { value: n, selected: n === state.cfgFn }, n === "<module>" ? "Whole module" : n)));
  const wrap = el("div", {}, el("h3", {}, "Control-flow graph"), el("p", { class: "lead" }, "The order in which statements can run. Boxes are blocks of statements; dashed lines loop back."), el("div", { class: "cfgbar" }, sel, info), box, rawJson(d, "cfg"));
  draw();
  return wrap;
}

/* syntax tree: lazy, collapsible */
const AST_SKIP = new Set(["node_type", "line", "col", "end_line", "end_col"]);
function astNode(node, label) {
  const attrs = [], kids = [];
  for (const [k, v] of Object.entries(node)) {
    if (AST_SKIP.has(k)) continue;
    if (v && typeof v === "object" && (Array.isArray(v) ? v.some((x) => x && typeof x === "object") : v.node_type)) kids.push([k, v]);
    else if (v !== null && v !== undefined && !(Array.isArray(v) && !v.length)) attrs.push(`${k}=${JSON.stringify(v)}`);
  }
  const head = [label ? label + ": " : "", node.node_type, attrs.length ? "  " : "", attrs.join(" ")].join("");
  const where = node.line ? ` (line ${node.line})` : "";
  if (!kids.length) return el("div", { class: "leaf" }, head, where);
  const d = el("details", {}, el("summary", {}, head, where));
  let built = false;
  d.addEventListener("toggle", () => {
    if (!d.open || built) return;
    built = true;
    for (const [k, v] of kids) {
      if (Array.isArray(v)) v.forEach((c, i) => c && typeof c === "object" && d.append(astNode(c, `${k}[${i}]`)));
      else d.append(astNode(v, k));
    }
  });
  return d;
}
function panelAST(d) {
  const root = astNode(d, "");
  root.open = true;
  root.dispatchEvent(new Event("toggle"));
  return el("div", {}, el("h3", {}, "Syntax tree"), el("p", { class: "lead" }, "How Python reads the code. Open a node to see what is inside it."), el("div", { class: "tree" }, root), rawJson(d, "ast"));
}

function panelManifest(d) {
  return el("div", {}, el("h3", {}, "Safety manifest"), el("p", { class: "lead" }, "A fixed-format summary of the decision. The same code always gives the same digest."),
    el("dl", { class: "kv" },
      el("dt", {}, "Verdict"), el("dd", {}, d.overall_verdict),
      el("dt", {}, "Digest"), el("dd", {}, el("code", {}, d.manifest_digest)),
      el("dt", {}, "Analysis version"), el("dd", {}, d.analysis_version),
      el("dt", {}, "Rejection reasons"), el("dd", {}, d.rejection_reasons.length ? d.rejection_reasons.map((r) => reasonText(r)).join("; ") : "none")),
    rawJson(d, "manifest"));
}

function panelIR(d) {
  const n = d.nodes || {};
  return el("div", {}, el("h3", {}, "Safety IR"), el("p", { class: "lead" }, "Everything EvoSafe learned, in one JSON document other tools can read: functions, loops, capabilities, control flow, taint flows, evidence and the decision."),
    el("p", { class: "counts" }, ...Object.entries(n).map(([k, v]) => el("span", {}, el("b", {}, String((v || []).length)), " " + k.replaceAll("_", " ")))),
    el("dl", { class: "kv" }, el("dt", {}, "IR version"), el("dd", {}, d.ir_version), el("dt", {}, "Verdict hint"), el("dd", {}, d.verdict_hint), el("dt", {}, "Evidence items"), el("dd", {}, String((d.evidence || []).length))),
    rawJson(d, "safety-ir"));
}

/* ---------- evaluation + about ---------- */
let evalData = null;
async function renderEvaluation() {
  const host = $("view-evaluation");
  if (host.dataset.ready) return;
  host.replaceChildren(el("p", {}, "Loading results…"));
  try {
    evalData = evalData || (await (await fetch("data/review2.json")).json());
  } catch {
    host.replaceChildren(el("p", { role: "alert" }, "Couldn't load the evaluation data."));
    return;
  }
  const d = evalData, s = d.safety;
  const row = (k, v) => el("tr", {}, el("th", { scope: "row" }, k), el("td", {}, v));
  const trio = (r) => el("div", { class: "trio" }, [["p", "precision"], ["r", "recall"], ["f", "f1"]].map(([c, key]) =>
    el("div", { class: "m" }, el("div", { class: "track", title: `${key} ${pct(r[key])}` }, el("div", { class: "fill " + c, style: `width:${(r[key] || 0) * 100}%` })), el("span", {}, (r[key] || 0).toFixed(2)))));
  host.replaceChildren(
    el("h1", {}, "How well does it work?"),
    el("p", { class: "lede" }, `Results from the frozen Review 2 evaluation on ${d.programs} reviewed programs (dataset ${d.dataset_version}). Every program was analysed; none failed.`),
    el("h2", {}, "Safety verdicts"),
    el("div", { class: "scroll" }, el("table", { class: "facts" }, el("tbody", {},
      row("Programs with a known answer", el("span", {}, el("b", {}, `${s.correct} of ${s.determinate}`), ` correct (${pct(s.accuracy)})`)),
      row("Unsafe programs found", el("span", {}, el("b", {}, `${pct(s.classes.UNSAFE.recall)} recall`), `, ${pct(s.classes.UNSAFE.precision)} precision. One unsafe program was called safe.`)),
      row("Safe programs recognised", el("span", {}, el("b", {}, `${pct(s.classes.SAFE.recall)} recall`), `, ${pct(s.classes.SAFE.precision)} precision.`)),
      row("Verdicts changed by EA analysis", el("b", {}, "0 of 936")),
      row("Time per program", el("span", {}, el("b", {}, "14 ms"), " on average, 44 ms for the slowest 5 percent.")))),
    ),
    el("p", { class: "callout" }, `Only ${s.determinate} of ${d.programs} programs have a confirmed safety answer. The other ${s.ground_truth_counts.UNKNOWN} come from existing open-source collections that nobody judged one by one, so their verdicts aren't scored. These numbers show a working proof of concept, not broad safety assurance.`),
    el("h2", {}, "Finding the parts of an evolutionary algorithm"),
    el("p", {}, `Across all seven roles EvoSafe is careful but misses a lot: precision ${pct(d.roles_macro.precision)}, recall ${pct(d.roles_macro.recall)}, F1 ${pct(d.roles_macro.f1)}. Replacement, crossover and selection are missed most often.`),
    el("div", { class: "legend" }, el("span", {}, el("i", { style: "background:var(--info)" }), "Precision"), el("span", {}, el("i", { style: "background:var(--cond)" }), "Recall"), el("span", {}, el("i", { style: "background:var(--ink)" }), "F1")),
    el("div", { class: "bars" }, ROLE_ORDER.map(([k, label]) => { const key = k === "fitness_evaluation" ? "fitness" : k; return el("div", { class: "bar-row" }, el("span", { class: "nm" }, label), trio(d.roles[key])); })),
    el("h2", {}, "By kind of program"),
    el("div", { class: "scroll" }, el("table", { class: "facts" }, el("thead", {}, el("tr", {}, ["Category", "Programs", "With known answer", "Safety accuracy", "EA role F1"].map((h) => el("th", { scope: "col" }, h)))),
      el("tbody", {}, Object.entries(d.categories).map(([c, v]) => el("tr", {}, el("th", { scope: "row" }, CATEGORY_NAME[c] || c), el("td", {}, String(v.programs)), el("td", {}, String(v.determinate)), el("td", {}, v.safety_accuracy == null ? "no known answers" : pct(v.safety_accuracy)), el("td", {}, pct(v.ea_macro_f1))))))),
    el("h2", {}, "Earlier benchmarks are not comparable"),
    el("p", {}, "The 18-program development set scores a perfect 1.00 because it was used to tune the detectors. A separate set of 51 held-out programs scored 0.64 F1, and the full 936-program set scores 0.32. These are different programs, so the drop is not a before-and-after comparison."),
    el("p", {}, "Full tables, the error analysis and the command that reproduces every number are in the ", el("a", { href: "https://github.com/SwarnaDharshiniS/EvoSafe/blob/main/docs/RESULTS.md", rel: "noopener" }, "results document"), "."));
  host.dataset.ready = "1";
}

function renderAbout() {
  const host = $("view-about");
  if (host.dataset.ready) return;
  const g = (t, dsc) => el("div", {}, el("dt", {}, t), el("dd", {}, dsc));
  host.replaceChildren(
    el("h1", {}, "What EvoSafe does"),
    el("p", { class: "lede" }, "EvoSafe reads Python source and decides whether it looks safe to run, without running it. It can also recognise the parts of an evolutionary algorithm."),
    el("h2", {}, "The three verdicts"),
    el("dl", { class: "glossary" }, g("Safe", "No rule found a problem."), g("Conditionally safe", "Safe only if checks hold, for example that the program may touch files or the network."), g("Unsafe", "A rule found untrusted data reaching a dangerous operation, dynamic code execution, or a loop with no end.")),
    el("h2", {}, "The analyses you can run"),
    el("dl", { class: "glossary" },
      g("Taint flows", "Tracks data from sources such as input() to sinks such as os.system()."),
      g("Capabilities", "Lists use of files, network, processes and dynamic code."),
      g("Resource risk", "Flags loops and recursion that may not end or may grow too large."),
      g("EA roles", "Finds population, fitness, selection, crossover, mutation, replacement and termination. This never changes the verdict."),
      g("Control-flow graph", "Draws the order in which statements can run."),
      g("Syntax tree", "Shows how Python parsed the code."),
      g("Safety manifest", "A fixed-format decision summary with a digest."),
      g("Safety IR", "One JSON document with everything above, for other tools to use.")),
    el("h2", {}, "Limits worth knowing"),
    el("p", {}, "Static analysis is approximate. A safe verdict means the current rules found nothing; it does not prove the code is harmless. Dynamic Python (aliases, callbacks, getattr) can hide a flow. The demo accepts up to 60,000 characters and 2,000 lines, and it only reads your code. It never runs it."),
    el("p", {}, "The code is on ", el("a", { href: "https://github.com/SwarnaDharshiniS/EvoSafe", rel: "noopener" }, "GitHub"), ", including the dataset, the tests and the script that reproduces the evaluation."));
  host.dataset.ready = "1";
}

/* ---------- boot ---------- */
async function boot() {
  $("picks").replaceChildren(...ANALYSES.map((a) => el("label", { class: "pick-chip" }, el("input", { type: "checkbox", value: a.id, checked: a.on }), el("span", {}, a.label))));
  const t = src();
  t.addEventListener("input", () => {
    if (state.result && !state.stale) { state.stale = true; state.markers = new Map(); state.picked = null; renderResults(false); }
    state.errorLine = null; $("syntax").hidden = true;
    paintEditor();
  });
  t.addEventListener("scroll", syncScroll);
  t.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(); }
    if (e.key === "Tab" && !e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey && !state.tabEscape) {
      e.preventDefault();
      const { selectionStart: s, selectionEnd: en } = t;
      t.setRangeText("    ", s, en, "end");
      t.dispatchEvent(new Event("input"));
    }
    if (e.key === "Escape") state.tabEscape = true;
  });
  t.addEventListener("blur", () => { state.tabEscape = false; });
  $("run").addEventListener("click", run);
  window.addEventListener("hashchange", route);

  try {
    const list = await (await fetch("data/examples.json")).json();
    state.examples = Array.isArray(list) ? list : [];
  } catch {
    state.examples = [];
  }
  const sel = $("example");
  sel.replaceChildren(el("option", { value: "" }, "Your own code"), ...state.examples.map((e) => el("option", { value: e.id }, e.title)));
  sel.addEventListener("change", () => {
    const ex = state.examples.find((x) => x.id === sel.value);
    if (ex) {
      t.value = ex.source;
      state.result = null; state.markers = new Map(); state.picked = null; state.stale = false;
      paintEditor();
      run();
    }
  });
  route();
  if (state.examples.length) {
    sel.value = state.examples[0].id;
    t.value = state.examples[0].source;
    paintEditor();
    run();
  } else {
    paintEditor();
  }
}
boot();
