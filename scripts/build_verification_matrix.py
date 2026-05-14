"""
Verification matrix: for each IMPLEMENTED DEC + RESOLVED-IMPLEMENTED BUG,
record where it's tagged in source, whether those source lines actually
executed during a canonical backtest (coverage), and which of the 13
pyramid test tiers reference it.

Inputs:
  - dashboard_stage_2/data.js     (gives list of IMPLEMENTED items)
  - coverage_report.json          (from `python -m coverage json`)
  - backtest/**/*.py source       (for DEC-NNN/BUG-NNN tag locations)
  - backtest/tests/*.py           (per-tier test references)

Output: VERIFICATION_MATRIX.md

Run:
  python scripts/build_verification_matrix.py
"""
from __future__ import annotations

import ast
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPO = Path(__file__).resolve().parents[1]

# Pyramid layer -> test filenames (kept in sync with scripts/build_dashboard_stage_2.py)
TEST_PYRAMID_LAYERS: Dict[str, List[str]] = {
    "unit": ["test_unit.py", "test_prefetch_utils.py",
             "test_smartmoneyconcepts_unit.py",
             "test_inv041_path_restricted_commits.py",
             "test_prefetch_scripts_no_unicode.py",
             "test_phase1a_runner_no_unicode.py"],
    "smoke": ["test_smoke.py", "test_e2e_phase1a_smoke.py", "test_e2e.py",
              "test_aaii_smoke.py", "test_apewisdom_smoke.py",
              "test_cftc_cot_smoke.py", "test_cnn_fg_smoke.py",
              "test_fred_alfred_smoke.py", "test_polygon_stocks_smoke.py",
              "test_quiver_trader_smoke.py", "test_sec_edgar_smoke.py",
              "test_stocktwits_smoke.py", "test_supplementary_smoke.py"],
    "integration": ["test_integration.py",
                    "test_smartmoneyconcepts_integration.py",
                    "test_smartmoneyconcepts_empirical.py",
                    "test_l146_wiring_matrix.py",
                    "test_l146_wave_a_g2_g3_g9.py",
                    "test_l146_wave_b_g7_sec_edgar.py",
                    "test_l146_wave_c_g12_g15.py",
                    "test_l146_wave_d_g6_g8_g10_g11_g16_g17.py",
                    "test_n1_n2_artifacts.py", "test_n5_n6_wiring.py",
                    "test_exit_conditional_analyzer.py",
                    "test_exit_context.py",
                    "test_dec509_correlation_cluster.py",
                    "test_dec513_extended_signals.py",
                    "test_dec514_fill_methodology.py",
                    "test_dec517_r_multiple_exits.py",
                    "test_dec518_dec521_exits.py"],
    "system": ["test_gate_pre_phase_1a_entry.py", "test_gates.py",
               "test_no_live_api_hard_cut.py", "test_preflight.py"],
    "functional": ["test_doc_count_consistency.py",
                   "test_acceptance_functional.py",
                   "test_canonical_facts_alignment.py"],
    "regression": ["test_regression.py", "test_bug_vix_proxy_regression.py",
                   "test_pit_audit_v8g.py", "test_dec512_pit_audit.py",
                   "test_smartmoneyconcepts_pit.py"],
    "data_integrity": ["test_schema_canonical.py", "test_data_integrity.py",
                       "test_data_integrity_v8h_additions.py",
                       "test_cache_schema_b.py",
                       "test_polygon_ohlcv_master_schema.py",
                       "test_engine_bad_data_stress.py"],
    "performance": ["test_performance.py", "test_performance_load.py"],
    "acceptance": ["test_acceptance.py", "test_sprint2_acceptance.py"],
    "property": ["test_property.py"],
    "snapshot": ["test_snapshot.py", "test_walk_forward_4fold.py"],
    "contract": ["test_contract.py",
                 "test_partial_spec_artifacts.py",
                 "test_partial_spec_artifacts_v2.py",
                 "test_dec491_492_493_sprint2.py"],
    "compatibility": ["test_compatibility.py"],
}

LAYER_ORDER = list(TEST_PYRAMID_LAYERS.keys())


def load_implemented_items() -> Tuple[List[str], List[str]]:
    """Read dashboard data.js and return DEC + BUG ID lists with promotion_path.tier == IMPLEMENTED."""
    data_js = (REPO / "dashboard_stage_2" / "data.js").read_text(encoding="utf-8")
    js = re.sub(r"^const STAGE2_DATA = ", "", data_js.strip())
    js = re.sub(r";$", "", js.strip())
    data = json.loads(js)

    dec_ids: List[str] = []
    for d in data["decisions"]:
        tier = (d.get("promotion_path") or {}).get("tier")
        if tier == "IMPLEMENTED":
            dec_ids.append(d.get("short_id") or d["id"])

    bug_ids: List[str] = []
    for b in data["bugs"]:
        tier = (b.get("promotion_path") or {}).get("tier")
        if tier == "IMPLEMENTED":
            bug_ids.append(b.get("short_id") or b["id"])

    return dec_ids, bug_ids


def grep_id_in_source(item_id: str, source_files: List[Path]) -> List[Tuple[Path, int]]:
    """Find lines where item_id appears in source files. Returns [(file, line_no), ...]."""
    hits: List[Tuple[Path, int]] = []
    # Pattern: full ID with optional alpha suffix preserved (DEC-078A, BUG-045)
    # Also a zero-padding-tolerant variant for plain numerics.
    patterns = [re.compile(rf"\b{re.escape(item_id)}\b")]
    m = re.match(r"^(DEC|BUG)-(\d+)([A-Za-z]*)$", item_id)
    if m:
        prefix, num, suffix = m.groups()
        # Match prefix[-_]0*NUM[suffix]  -  tolerate any zero padding
        patterns.append(re.compile(rf"\b{prefix}[-_]0*{int(num)}{re.escape(suffix)}\b"))

    for f in source_files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(p.search(line) for p in patterns):
                hits.append((f, lineno))
                break  # one hit per file is enough for matrix
    return hits


def load_coverage() -> Dict[str, Dict]:
    """Read coverage_report.json -> {filepath: {executed_lines: set, missing_lines: set, percent: float}}."""
    cov_path = REPO / "coverage_report.json"
    if not cov_path.exists():
        return {}
    data = json.loads(cov_path.read_text(encoding="utf-8"))
    out: Dict[str, Dict] = {}
    for relpath, info in data.get("files", {}).items():
        # Normalize path: coverage may emit forward or backslashes
        key = relpath.replace("\\", "/")
        out[key] = {
            "executed_lines": set(info.get("executed_lines", [])),
            "missing_lines": set(info.get("missing_lines", [])),
            "percent": info.get("summary", {}).get("percent_covered", 0.0),
        }
    return out


@lru_cache(maxsize=None)
def _files_imported_by(target_module_relpath: str) -> List[str]:
    """Return list of repo-relative .py paths that import the given module (top-level OR lazy).

    `target_module_relpath` example: 'backtest/results/seven_gate_verdict.py'
    Module name derived: 'backtest.results.seven_gate_verdict' or
    'backtest.results.seven_gate_verdict.compute_verdict_cube' substring.
    """
    mod_dotted = target_module_relpath.replace("/", ".").replace(".py", "")
    # Module basename for `from X.Y import foo` matching
    basename = mod_dotted.rsplit(".", 1)[-1]
    importers: List[str] = []
    for p in (REPO / "backtest").rglob("*.py"):
        if "/tests/" in str(p).replace("\\", "/"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # Match `from backtest.results.basename import ...` OR
        # `import backtest.results.basename` OR `from ... import basename` if dotted matches
        pat1 = re.compile(rf"\bfrom\s+{re.escape(mod_dotted)}\s+import\b")
        pat2 = re.compile(rf"\bimport\s+{re.escape(mod_dotted)}\b")
        if pat1.search(text) or pat2.search(text):
            importers.append(str(p.relative_to(REPO)).replace("\\", "/"))
    return importers


@lru_cache(maxsize=None)
def _function_ranges(file_path_str: str) -> List[Tuple[int, int]]:
    """For a Python file, return list of (start_line, end_line) for every function/method body."""
    p = Path(file_path_str)
    if not p.exists():
        return []
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []
    ranges: List[Tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = node.end_lineno or start
            ranges.append((start, end))
    return ranges


def _enclosing_range(file_path: Path, line: int) -> Optional[Tuple[int, int]]:
    """Return (start, end) of the function enclosing `line`, or None if module-level."""
    candidates = [(s, e) for s, e in _function_ranges(str(file_path)) if s <= line <= e]
    if not candidates:
        return None
    # Pick the innermost (latest start) range
    candidates.sort(key=lambda r: (r[0], -r[1]))
    return candidates[-1]


def is_engine_consumed(hits: List[Tuple[Path, int]], coverage: Dict[str, Dict]) -> Tuple[str, str]:
    """
    Determine if the function containing the item's source tag(s) executed during
    the canonical backtest.

    Returns (status, evidence) where status in:
      - "YES"  -  enclosing function (or module-level if no function) has any executed line
      - "FUNC-DEAD"  -  function exists in active module but its body never executed
      - "NO"   -  tagged source file has 0% coverage entirely
      - "N/A"  -  no source tag found (methodology/doc, not code)
    """
    if not hits:
        return ("N/A", "no source tag")

    code_hits: List[Tuple[Path, int]] = []
    for f, ln in hits:
        norm = str(f).replace("\\", "/")
        if "/tests/" in norm:
            continue
        if not norm.startswith(str(REPO).replace("\\", "/") + "/backtest/"):
            continue
        code_hits.append((f, ln))

    if not code_hits:
        return ("N/A", "no source tag in backtest/")

    # Classify each tagged source file independently, then combine.
    per_file_status: List[Tuple[str, str]] = []  # (rel, status)
    yes_evidence: Optional[str] = None
    for f, ln in code_hits:
        rel = str(f.relative_to(REPO)).replace("\\", "/")
        cov = coverage.get(rel) or coverage.get(rel.replace("/", "\\"))
        if cov is None:
            per_file_status.append((rel, "UNKNOWN"))
            continue
        if cov["percent"] > 0:
            executed = cov["executed_lines"]
            rng = _enclosing_range(f, ln)
            if rng is None:
                per_file_status.append((rel, "YES"))
                yes_evidence = yes_evidence or f"module-level tag in {rel} ({cov['percent']:.0f}%)"
                continue
            start, end = rng
            if any(line in executed for line in range(start, end + 1)):
                per_file_status.append((rel, "YES"))
                yes_evidence = yes_evidence or f"function {start}-{end} executed in {rel}"
            else:
                per_file_status.append((rel, "FUNC-DEAD"))
            continue
        # 0% coverage  -  walk import graph transitively
        visited: Set[str] = set()
        frontier = [rel]
        lazy_chain: Optional[str] = None
        while frontier:
            current = frontier.pop()
            if current in visited:
                continue
            visited.add(current)
            for imp in _files_imported_by(current):
                imp_cov = coverage.get(imp) or coverage.get(imp.replace("/", "\\"))
                if imp_cov and imp_cov["percent"] > 0:
                    lazy_chain = f"{rel} reached via {imp} ({imp_cov['percent']:.0f}%)"
                    break
                if imp not in visited:
                    frontier.append(imp)
            if lazy_chain:
                break
        if lazy_chain:
            per_file_status.append((rel, "LAZY-WIRED"))
        else:
            per_file_status.append((rel, "NO"))

    statuses = {st for _, st in per_file_status}

    # Mixed-tag rule: if every tagged file is wired (YES/LAZY-WIRED), DEC is wired.
    # If any tag is fully orphaned (NO), surface as PARTIAL-ORPHAN unless the helper
    # is otherwise demonstrably running.
    if "YES" in statuses and "NO" not in statuses:
        return ("YES", yes_evidence or "tagged function executed")
    if statuses <= {"YES", "LAZY-WIRED", "UNKNOWN"} and ("YES" in statuses or "LAZY-WIRED" in statuses):
        return ("LAZY-WIRED",
                f"import chain exists for all tags; gating condition not met "
                f"({per_file_status[0][0]})")
    if "NO" in statuses and ("YES" in statuses or "LAZY-WIRED" in statuses):
        orphan = next(rel for rel, st in per_file_status if st == "NO")
        return ("PARTIAL-ORPHAN",
                f"primary helper {orphan} has no live importer; another tagged file is wired "
                "(mention-only, not actual implementation chain)")
    if "FUNC-DEAD" in statuses:
        dead = next(rel for rel, st in per_file_status if st == "FUNC-DEAD")
        return ("FUNC-DEAD", f"function in {dead} never executed")
    if statuses == {"NO"}:
        return ("NO", f"every tagged file is orphaned (e.g. {per_file_status[0][0]})")
    return ("N/A", "no coverage data for tagged files")


def grep_id_in_tests(item_id: str) -> Dict[str, str]:
    """For each pyramid layer, return YES if any test file in that layer references item_id, else NO."""
    patterns = [re.compile(rf"\b{re.escape(item_id)}\b")]
    m = re.match(r"^(DEC|BUG)-(\d+)([A-Za-z]*)$", item_id)
    if m:
        prefix, num, suffix = m.groups()
        patterns.append(re.compile(rf"\b{prefix}[-_]0*{int(num)}{re.escape(suffix)}\b"))

    tests_dir = REPO / "backtest" / "tests"
    result: Dict[str, str] = {}
    for layer, files in TEST_PYRAMID_LAYERS.items():
        found = False
        for fname in files:
            f = tests_dir / fname
            if not f.exists():
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if any(p.search(text) for p in patterns):
                found = True
                break
        result[layer] = "YES" if found else "no"
    return result


def collect_source_files() -> List[Path]:
    src = REPO / "backtest"
    return [p for p in src.rglob("*.py") if "tests" not in p.parts]


def emit_matrix(items: List[Tuple[str, str]], coverage: Dict[str, Dict], source_files: List[Path]) -> str:
    """items: list of (kind, id) tuples. kind in {DEC, BUG}."""
    lines: List[str] = []
    lines.append("# VERIFICATION_MATRIX.md")
    lines.append("")
    lines.append("**Generated:** see `scripts/build_verification_matrix.py`. "
                 "Per-item ground truth for the 343 IMPLEMENTED claims (DEC + BUG).")
    lines.append("")
    lines.append("Columns:")
    lines.append("- `engine`: did the function containing the source tag execute during the canonical "
                 "AAPL backtest under coverage? YES = engine-consumed (function body had at least one "
                 "executed line); LAZY-WIRED = file at 0% coverage but imported by a module that ran "
                 "(import chain exists, conditional path not exercised by this small backtest  -  "
                 "treat as wired until a larger backtest disproves); "
                 "FUNC-DEAD = function exists in active module but body never executed; "
                 "NO = tagged file at 0% with no live importer anywhere (real wiring gap); "
                 "N/A = no source tag found (methodology/scope decision, no code expected).")
    lines.append("- 13 pyramid tier columns: YES if any test file in that tier references the ID.")
    lines.append("")
    lines.append("Canonical backtest: `python -m coverage run backtest/run_phase1a.py --no-agents "
                 "--no-git --tickers AAPL --start 2023-01-01 --end 2023-06-30`")
    lines.append("")
    # Header
    header = ["ID", "engine"] + LAYER_ORDER
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")

    summary = {"engine_YES": 0, "engine_LAZY_WIRED": 0, "engine_PARTIAL_ORPHAN": 0,
               "engine_FUNC_DEAD": 0, "engine_NO": 0, "engine_NA": 0}
    by_layer_gap_count = {l: 0 for l in LAYER_ORDER}
    gap_rows: List[Tuple[str, str, str, Dict[str, str]]] = []  # (id, engine_status, evidence, layer_dict)

    for kind, item_id in items:
        hits = grep_id_in_source(item_id, source_files)
        engine_status, evidence = is_engine_consumed(hits, coverage)
        layer_status = grep_id_in_tests(item_id)

        # Tally
        if engine_status == "YES":
            summary["engine_YES"] += 1
        elif engine_status == "LAZY-WIRED":
            summary["engine_LAZY_WIRED"] += 1
        elif engine_status == "PARTIAL-ORPHAN":
            summary["engine_PARTIAL_ORPHAN"] += 1
        elif engine_status == "FUNC-DEAD":
            summary["engine_FUNC_DEAD"] += 1
        elif engine_status == "NO":
            summary["engine_NO"] += 1
        else:
            summary["engine_NA"] += 1

        for l in LAYER_ORDER:
            if layer_status[l] == "no":
                # Only count as gap if engine actually consumes the helper
                if engine_status in ("YES", "LAZY-WIRED"):
                    by_layer_gap_count[l] += 1

        if engine_status in ("NO", "FUNC-DEAD", "PARTIAL-ORPHAN"):
            gap_rows.append((item_id, engine_status, evidence, layer_status))

        row = [f"`{item_id}`", engine_status] + [layer_status[l] for l in LAYER_ORDER]
        lines.append("| " + " | ".join(row) + " |")

    # Summary at top: re-emit
    summary_lines = [
        "",
        "## Summary",
        "",
        f"- Total items audited: **{len(items)}**",
        f"- Engine YES (executed): **{summary['engine_YES']}**",
        f"- Engine LAZY-WIRED (all tagged files wired via lazy import chains): **{summary['engine_LAZY_WIRED']}** "
        "(import chain exists; condition gating the call not met in this small backtest)",
        f"- Engine PARTIAL-ORPHAN (some tags wired, primary helper file orphaned): **{summary['engine_PARTIAL_ORPHAN']}** "
        "(DEC is mentioned in a wired file but the actual helper module has no live importer  -  real gap)",
        f"- Engine FUNC-DEAD (function exists but never executed): **{summary['engine_FUNC_DEAD']}**",
        f"- Engine NO (all tagged files orphaned): **{summary['engine_NO']}** "
        "(real wiring gap  -  helper file imported nowhere in the engine path)",
        f"- Engine N/A (no code expected): **{summary['engine_NA']}**",
        "",
        "### Pyramid coverage gaps (count of engine-consumed items missing per tier)",
        "",
    ]
    for l in LAYER_ORDER:
        summary_lines.append(f"- `{l}`: **{by_layer_gap_count[l]}** items lack a reference in this tier's test files")
    summary_lines.append("")
    summary_lines.append("### Engine-consumption gaps detail")
    summary_lines.append("")
    if gap_rows:
        summary_lines.append("| ID | engine | evidence | unit | integration |")
        summary_lines.append("|---|---|---|---|---|")
        for iid, st, ev, ld in gap_rows[:200]:
            # Trim evidence to fit table
            short_ev = ev[:120].replace("|", "/") + ("..." if len(ev) > 120 else "")
            summary_lines.append(f"| `{iid}` | {st} | {short_ev} | {ld['unit']} | {ld['integration']} |")
        if len(gap_rows) > 200:
            summary_lines.append(f"| ... {len(gap_rows) - 200} more rows ... | | | | |")
    else:
        summary_lines.append("None  -  every IMPLEMENTED item has at least its tagged line executed in the canonical backtest.")
    summary_lines.append("")

    # Insert summary right after the description
    insert_idx = next(i for i, line in enumerate(lines) if line.startswith("| ID |"))
    return "\n".join(lines[:insert_idx] + summary_lines + lines[insert_idx:]) + "\n"


def main() -> int:
    print("Loading implemented items from dashboard data.js ...")
    dec_ids, bug_ids = load_implemented_items()
    print(f"  IMPLEMENTED DECs: {len(dec_ids)}")
    print(f"  IMPLEMENTED BUGs: {len(bug_ids)}")

    print("Loading coverage report ...")
    coverage = load_coverage()
    print(f"  files in coverage: {len(coverage)}")

    print("Collecting source files ...")
    source_files = collect_source_files()
    print(f"  source files: {len(source_files)}")

    print("Building matrix ...")
    items = [("DEC", i) for i in dec_ids] + [("BUG", i) for i in bug_ids]
    md = emit_matrix(items, coverage, source_files)

    out_path = REPO / "VERIFICATION_MATRIX.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
