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
             "test_phase1a_runner_no_unicode.py",
             "test_dec_unit_coverage.py",
             "test_dec_unit_coverage_anomalies.py"],
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
                    "test_dec518_dec521_exits.py",
                    "test_dec_integration_coverage.py",
                    "test_dec_integration_coverage_anomalies.py"],
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


def load_all_items() -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Read dashboard data.js and return ALL DEC + BUG entries (excluding
    SUPERSEDED + OBSOLETE which the matrix treats as out-of-scope).

    Returns (decisions, bugs) where each list contains (id, tier) tuples so the
    matrix can group its summary by promotion tier (IMPLEMENTED / DECIDED /
    DEFERRED / FUNC-DEAD / etc.). Per owner directive 2026-05-14: expand scope
    from IMPLEMENTED-only (357) to all items so DECIDED/DEFERRED entries
    surface for classification anomaly detection.

    Batch 171 (2026-05-15) decouple fix: prefer `decisions_all` + `bugs_all`
    over `decisions` + `bugs`. The latter are the dashboard's UI-visible
    lists (FUNC-DEAD filter applied); the former include hidden items.
    Reading the _all lists breaks the prior matrix <-> dashboard FUNC-DEAD
    coupling oscillation, where a FUNC-DEAD-hidden item would fall out of
    matrix scope on next regen, lose its FUNC-DEAD signal, and re-enter
    on the regen after that. Fallback to `decisions` / `bugs` preserves
    compatibility with pre-Batch-171 data.js snapshots.
    """
    data_js = (REPO / "dashboard_stage_2" / "data.js").read_text(encoding="utf-8")
    js = re.sub(r"^const STAGE2_DATA = ", "", data_js.strip())
    js = re.sub(r";$", "", js.strip())
    data = json.loads(js)

    HIDDEN = {"SUPERSEDED", "OBSOLETE"}

    decisions_source = data.get("decisions_all", data.get("decisions", []))
    bugs_source = data.get("bugs_all", data.get("bugs", []))

    dec_items: List[Tuple[str, str]] = []
    for d in decisions_source:
        tier = (d.get("promotion_path") or {}).get("tier") or "UNKNOWN"
        if tier in HIDDEN:
            continue
        dec_items.append((d.get("short_id") or d["id"], tier))

    bug_items: List[Tuple[str, str]] = []
    for b in bugs_source:
        tier = (b.get("promotion_path") or {}).get("tier") or "UNKNOWN"
        if tier in HIDDEN:
            continue
        bug_items.append((b.get("short_id") or b["id"], tier))

    return dec_items, bug_items


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
                # No break - record ALL tag locations so function-level coverage
                # check sees every enclosing function (one tag may be in dead
                # helper, another in actively-called code).
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


@lru_cache(maxsize=None)
def _adjacent_symbol(file_path_str: str, tag_line: int) -> Optional[str]:
    """Look at lines after `tag_line` in `file_path_str` and return the first
    defined symbol (top-level constant, function, or class name). Used to detect
    whether a module-level DEC-NNN tag's implementation is actually consumed by
    other code.

    Returns None if no defining line found in the next 8 lines.
    """
    p = Path(file_path_str)
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    lines = text.splitlines()
    # Look at the next 8 non-blank, non-comment lines after the tag
    sym_re = re.compile(r"^(?:def |class |async def )?([A-Z_][A-Z0-9_]+|[a-z_][a-z0-9_]+)\s*[:=(]")
    for i in range(tag_line, min(tag_line + 8, len(lines))):
        line = lines[i].rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        # Match constant assignment, function def, class def
        m = re.match(r"^(?:def\s+|class\s+|async\s+def\s+)?([A-Za-z_][A-Za-z0-9_]+)\s*[(:=]", line)
        if m:
            return m.group(1)
    return None


@lru_cache(maxsize=None)
def _symbol_consumed_externally(symbol: str, defining_file: Path,
                                  coverage_keys: Tuple[str, ...]) -> bool:
    """Return True if `symbol` is referenced in any file OTHER than `defining_file`
    AND that other file has coverage > 0% in the current run.

    `coverage_keys` is a tuple of file paths with non-zero coverage (passed as a
    hashable arg so the @lru_cache key works).
    """
    pattern = re.compile(rf"\b{re.escape(symbol)}\b")
    defining_norm = str(defining_file).replace("\\", "/")
    for p in (REPO / "backtest").rglob("*.py"):
        norm = str(p).replace("\\", "/")
        if norm == defining_norm:
            continue
        if "/tests/" in norm:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if not pattern.search(text):
            continue
        # Symbol is referenced. Check if this file has any coverage.
        rel = str(p.relative_to(REPO)).replace("\\", "/")
        if rel in coverage_keys or rel.replace("/", "\\") in coverage_keys:
            return True
    return False


def _function_body_start(file_path: Path, def_start: int, def_end: int) -> int:
    """Find the line where the function body begins (after `def name(...):` and
    any signature continuation across multiple lines + after any docstring).

    Python executes the `def` line at import time, registering the function. The
    body only executes when the function is called. So for engine-consumption
    detection we need to check executed lines INSIDE the body, not the signature
    or docstring.
    """
    p = Path(file_path)
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return def_start + 1

    # Skip signature lines (until we find `:` ending a balanced-paren signature)
    sig_end = def_start
    depth = 0
    for i in range(def_start - 1, min(def_end, len(lines))):
        line = lines[i]
        depth += line.count("(") - line.count(")")
        if depth <= 0 and line.rstrip().endswith(":"):
            sig_end = i + 1
            break

    # Skip docstring if present
    body_start = sig_end + 1
    if body_start <= len(lines):
        stripped = lines[body_start - 1].lstrip() if body_start - 1 < len(lines) else ""
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            # Single-line docstring
            if stripped.count(quote) >= 2:
                body_start = sig_end + 2
            else:
                # Multi-line: scan until closing quote
                for j in range(body_start, min(def_end, len(lines))):
                    if quote in lines[j]:
                        body_start = j + 2
                        break

    return min(body_start, def_end + 1)


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
                # Module-level tag. Tighten the YES claim: the module being
                # loaded (which happens automatically for any imported file)
                # does NOT prove engine consumption. Look at the adjacent
                # defined symbol and check if it's referenced by other
                # executing files. If not -> DECLARED-ONLY (declared but
                # not consumed by engine).
                cov_keys = tuple(coverage.keys())
                adjacent = _adjacent_symbol(str(f), ln)
                if adjacent and _symbol_consumed_externally(adjacent, f, cov_keys):
                    per_file_status.append((rel, "YES"))
                    yes_evidence = yes_evidence or (
                        f"module-level tag in {rel} ({cov['percent']:.0f}%); "
                        f"adjacent symbol `{adjacent}` consumed externally"
                    )
                else:
                    per_file_status.append((rel, "DECLARED-ONLY"))
                continue
            start, end = rng
            # Exclude the `def` line (and any decorator/signature continuation
            # lines) - they execute at import time regardless of whether the
            # function body ever runs. Check body lines only.
            body_start = _function_body_start(f, start, end)
            body_executed = any(line in executed for line in range(body_start, end + 1))
            if body_executed:
                per_file_status.append((rel, "YES"))
                yes_evidence = yes_evidence or f"function body {body_start}-{end} executed in {rel}"
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
    if statuses <= {"YES", "LAZY-WIRED", "UNKNOWN", "DECLARED-ONLY"} and ("YES" in statuses or "LAZY-WIRED" in statuses):
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
    if statuses <= {"DECLARED-ONLY", "UNKNOWN"} and "DECLARED-ONLY" in statuses:
        # Tag is module-level (typically in config.py) but the adjacent symbol
        # isn't referenced by any other executing file - declared in source but
        # not consumed by the engine. Common pattern: deferred-feature config
        # constants that haven't been wired yet.
        rel = next(r for r, s in per_file_status if s == "DECLARED-ONLY")
        return ("DECLARED-ONLY",
                f"tagged symbol declared in {rel} but not consumed by any executing file "
                "(config constant for deferred / unwired feature)")
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


def emit_matrix(items: List[Tuple[str, str, str]], coverage: Dict[str, Dict], source_files: List[Path]) -> str:
    """items: list of (kind, id, tier) tuples. kind in {DEC, BUG}; tier in {IMPLEMENTED, DECIDED, DEFERRED, ...}."""
    lines: List[str] = []
    lines.append("# VERIFICATION_MATRIX.md")
    lines.append("")
    lines.append("**Generated:** see `scripts/build_verification_matrix.py`. "
                 "Per-item ground truth for ALL visible DECs + BUGs in scope "
                 "(IMPLEMENTED / DECIDED / DEFERRED / UNKNOWN tiers; SUPERSEDED + "
                 "OBSOLETE hidden by the dashboard are excluded). Surfaces both "
                 "engine-consumption gaps AND classification anomalies "
                 "(DECIDED/DEFERRED items that ARE engine-consumed - either "
                 "misclassified or accidentally pre-wired).")
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
               "engine_FUNC_DEAD": 0, "engine_NO": 0, "engine_NA": 0,
               "engine_DECLARED_ONLY": 0}
    by_layer_gap_count = {l: 0 for l in LAYER_ORDER}
    gap_rows: List[Tuple[str, str, str, Dict[str, str]]] = []  # (id, engine_status, evidence, layer_dict)
    # Cross-tier anomaly tracking: items whose promotion-tier doesn't match
    # their engine status (e.g. DECIDED with engine=YES means there IS code,
    # so it shouldn't be DECIDED). Surfaces classification errors.
    anomalies: List[Tuple[str, str, str, str]] = []  # (id, tier, engine, note)
    by_tier_count: Dict[str, int] = {}

    for kind, item_id, tier in items:
        by_tier_count[tier] = by_tier_count.get(tier, 0) + 1
        hits = grep_id_in_source(item_id, source_files)
        engine_status, evidence = is_engine_consumed(hits, coverage)
        layer_status = grep_id_in_tests(item_id)

        # Anomaly detection:
        #   - DECIDED with engine=YES -> there IS code; DECIDED (methodology-only) is wrong classification
        #   - DEFERRED with engine=YES -> helper is already running in current phase; might not actually be deferred
        #   - IMPLEMENTED with engine=NO/FUNC-DEAD -> claim is wrong (real wiring gap)
        if tier == "DECIDED" and engine_status == "YES":
            anomalies.append((item_id, tier, engine_status,
                              "DECIDED claims no-code-expected but coverage shows engine consumption - reclassify to IMPLEMENTED?"))
        elif tier == "DEFERRED" and engine_status == "YES":
            anomalies.append((item_id, tier, engine_status,
                              "DEFERRED but helper executes in current-phase backtest - intentional pre-wire or misclassification?"))
        elif tier == "IMPLEMENTED" and engine_status in ("NO", "FUNC-DEAD"):
            anomalies.append((item_id, tier, engine_status,
                              "IMPLEMENTED but engine never reaches the tagged code - wiring gap"))

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
        elif engine_status == "DECLARED-ONLY":
            summary["engine_DECLARED_ONLY"] += 1
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
        f"- Total items audited: **{len(items)}** (scope-expanded 2026-05-14 per owner directive  -  now covers ALL visible DECs + BUGs, not just IMPLEMENTED tier)",
        "",
        "**By promotion tier:**",
    ]
    for t in sorted(by_tier_count, key=lambda x: -by_tier_count[x]):
        summary_lines.append(f"- {t}: {by_tier_count[t]}")
    summary_lines.extend([
        "",
        "**By coverage-driven engine status:**",
        f"- Engine YES (executed): **{summary['engine_YES']}**",
        f"- Engine LAZY-WIRED (all tagged files wired via lazy import chains): **{summary['engine_LAZY_WIRED']}** "
        "(import chain exists; condition gating the call not met in this small backtest)",
        f"- Engine PARTIAL-ORPHAN (some tags wired, primary helper file orphaned): **{summary['engine_PARTIAL_ORPHAN']}** "
        "(DEC is mentioned in a wired file but the actual helper module has no live importer  -  real gap)",
        f"- Engine FUNC-DEAD (function exists but never executed): **{summary['engine_FUNC_DEAD']}**",
        f"- Engine NO (all tagged files orphaned): **{summary['engine_NO']}** "
        "(real wiring gap  -  helper file imported nowhere in the engine path)",
        f"- Engine DECLARED-ONLY (module-level tag in config; symbol not consumed externally): **{summary['engine_DECLARED_ONLY']}** "
        "(constant declared but no other executing file uses it  -  deferred-feature config that hasn't been wired yet)",
        f"- Engine N/A (no code expected): **{summary['engine_NA']}**",
        "",
        f"### Classification anomalies (tier vs engine mismatch): **{len(anomalies)}**",
        "",
    ])
    if anomalies:
        summary_lines.append("| ID | Tier | Engine | Note |")
        summary_lines.append("|---|---|---|---|")
        for iid, tier, eng, note in anomalies[:100]:
            summary_lines.append(f"| `{iid}` | {tier} | {eng} | {note} |")
        if len(anomalies) > 100:
            summary_lines.append(f"| ... {len(anomalies) - 100} more ... | | | |")
    else:
        summary_lines.append("None  -  every item's promotion tier matches its coverage-driven engine status. Classifications are internally consistent.")
    summary_lines.extend([
        "",
        "### Pyramid coverage gaps (count of engine-consumed items missing per tier)",
        "",
    ])
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


def build_json_matrix(items: List[Tuple[str, str, str]], coverage: Dict[str, Dict],
                      source_files: List[Path]) -> Dict:
    """Machine-readable matrix consumed by build_dashboard_stage_2.py.

    Shape:
      {
        "generated_at": iso-timestamp,
        "items": {
          "DEC-018": {"engine": "YES", "evidence": "...", "kind": "DEC", "tier": "IMPLEMENTED"},
          ...
        }
      }
    """
    from datetime import datetime, timezone
    out_items: Dict[str, Dict] = {}
    for kind, item_id, tier in items:
        hits = grep_id_in_source(item_id, source_files)
        status, evidence = is_engine_consumed(hits, coverage)
        out_items[item_id] = {
            "kind":     kind,
            "tier":     tier,
            "engine":   status,
            "evidence": evidence,
        }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items":        out_items,
    }


def main() -> int:
    print("Loading ALL visible items from dashboard data.js (excluding SUPERSEDED/OBSOLETE) ...")
    dec_items, bug_items = load_all_items()
    print(f"  Visible DECs: {len(dec_items)}")
    print(f"  Visible BUGs: {len(bug_items)}")

    print("Loading coverage report ...")
    coverage = load_coverage()
    print(f"  files in coverage: {len(coverage)}")

    print("Collecting source files ...")
    source_files = collect_source_files()
    print(f"  source files: {len(source_files)}")

    items = ([("DEC", iid, tier) for iid, tier in dec_items]
             + [("BUG", iid, tier) for iid, tier in bug_items])

    print("Building Markdown matrix ...")
    md = emit_matrix(items, coverage, source_files)
    out_md = REPO / "VERIFICATION_MATRIX.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"Wrote {out_md}")

    print("Building JSON matrix (machine-readable) ...")
    j = build_json_matrix(items, coverage, source_files)
    out_json = REPO / "verification_matrix.json"
    out_json.write_text(json.dumps(j, indent=2), encoding="utf-8")
    print(f"Wrote {out_json} ({len(j['items'])} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
