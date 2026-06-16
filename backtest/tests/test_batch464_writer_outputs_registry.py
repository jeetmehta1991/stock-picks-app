"""Batch 464 (2026-05-29) -- AU8 writer.py output-consumer registry.

QUEUE FRAMING (claim was 18; actual is 30):
  The queue claimed 18 writer.py outputs were write-only. A strict scan
  (read_csv / read_parquet / json.load / load_json / load_csv / load_parquet
  / open(..., "r") across backtest/* + scripts/* non-test code) shows 30
  filenames written by writer.py have ZERO python read site.

NO AUTONOMOUS DELETION:
  Per CLAUDE.md owner-approval rule, deleting writer outputs is a behavior
  change that requires owner sign-off. Many "stub" files were created per
  prior DEC skeletons and serve as the dashboard data.js catalog's
  placeholder for that DEC's eventual artifact. Deleting them silently
  would surprise downstream dashboard generation.

  What lands here is the REGISTRY classifying each write-only output +
  drift-guard tests forcing future contributors who add a new write-only
  artifact to classify it before merge.

REGISTRY classification letters:
  a -- "active artifact, missing python reader" : a real output whose
       consumer is the dashboard data.js catalog or a downstream tool
       outside the scanned tree. Keep writing; the lack of a python
       reader is OK if the file is genuinely consumed elsewhere.
  b -- "DEC-stub placeholder" : a stub JSON the writer emits as a
       placeholder for a DEC's eventual artifact. Either fully wire
       the producer (later batch) or remove the stub. Tracked here so
       the obligation surfaces.
  c -- "engine-internal artifact" : intermediate output the engine
       writes for debug / forensic use; never consumed downstream but
       lives in the run output dir as evidence. Keep until next
       deliverable rationalization sweep.
  d -- "true write-only -- candidate for removal" : no plausible
       downstream consumer; flagged for owner review.

FOLLOW-UP:
  Each (b) entry is a candidate producer-wiring task; each (c) is a
  candidate for explicit "debug-only" labeling; each (d) is a candidate
  for owner-approved removal. This batch surfaces the inventory; the
  decisions are owner's.
"""
from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# CLASSIFICATION REGISTRY  (one entry per write-only output)
# --------------------------------------------------------------------------
# (class_letter, one_line_reason)
CLASSIFICATION: dict[str, tuple[str, str]] = {
    # --- a: active artifact, missing python reader (catalog or external consumer) ---
    "agent_performance.csv":         ("a", "agent A/B output; Phase 1B consumer when agents wire in"),
    "backtest_report.html":          ("a", "static HTML report opened by humans, not by code"),
    "edge_decay_metrics.csv":        ("a", "DEC-250 catalog entry; dashboard data.js references"),
    "regime_performance.csv":        ("a", "regime breakdown; dashboard catalog mention"),
    "sizing_log.csv":                ("a", "BUG-95 sizing audit; written for forensic + later analysis"),
    "slippage_advanced.csv":         ("a", "DEC-092 advanced slippage; pre-1B+ work to consume"),
    "smart_money_combined.csv":      ("a", "smart-money combined feed; downstream toolkit consumer"),
    "tier_adjustment_analysis.csv":  ("a", "agent tier upgrade/downgrade audit; pre-1B"),
    "top_losers_per_strategy.json":  ("a", "DEC-015/089/120 loser analysis -- candidate for dashboard tab wire"),
    "trade_pnl_decomposition.csv":   ("a", "DEC-214/279 pnl decomposition; analyst-pass candidate"),
    "verdict_cube.csv":              ("a", "DEC-422 cube verdicts -- candidate consumer in dashboard Tab 13"),
    "trade_exit_detail.csv":         ("a", "exit-method-x-cell detail; consumed via cube pipeline (post-merge)"),
    "exit_sweet_spots.csv":          ("a", "exit-method tier-A sweet-spot summary; pre-1B consumer"),
    "exit_pairwise_dominance.csv":   ("a", "exit-method dominance matrix; pre-1B consumer"),
    "insider_correlation.csv":       ("a", "smart-money insider correlation; dashboard catalog mention"),
    "signal_fire_rates.json":        ("a", "DEC-296 fire rate diagnostic; human inspection"),
    "trade_log_in_sample.csv":       ("a", "DEC-505 walk-forward IS split -- walk-forward consumer reads"),
    "trade_log_out_of_sample.csv":   ("a", "DEC-505 walk-forward OOS split -- walk-forward consumer reads"),

    # --- b: DEC-stub placeholder (skeleton emitted for a DEC's eventual artifact) ---
    "analyst_data_stub.json":        ("b", "DEC-461 / BUG-271 analyst data stub"),
    "batch163_stub_results.json":    ("b", "Batch 163 stub-skeleton infrastructure"),
    "cache_freshness_checksum_stub.json": ("b", "DEC-260/330 cache freshness stub"),
    "chart_pattern_skeleton_stub.json": ("b", "DEC-148 chart-pattern skeleton stub"),
    "fx_exposure_stub.json":         ("b", "DEC-134/255 FX exposure stub (Stage 4)"),
    "sector_neutral_hedge_stub.json": ("b", "DEC-141 sector-neutral hedge stub (Phase 1B+)"),
    "short_long_conversion_stub.json": ("b", "DEC-338 short/long conversion stub (Phase 1B+)"),
    "dec_constants_verification.json": ("b", "Batch 166 DEC-constants verification (61 constants checked at write time; debug artifact)"),
    "yfinance_hardcut_verify.json":  ("b", "BUG-228 yfinance hard-cut verifier (asserts 0 yfinance calls)"),
    "test_coverage_gate.json":       ("b", "DEC-095/225 test-coverage gate skeleton"),

    # --- c: engine-internal / forensic only (no downstream consumer, debug evidence) ---
    "benchmark_curve.parquet":       ("c", "BUG-95 benchmark curve -- alongside equity_curve; debug + dashboard reads via load_parquet helper if present"),
    "stop_cluster_pattern.json":     ("c", "DEC-216 stop-cluster forensic; lives in output dir for inspection"),
    "cube_compose_verdict.csv":      ("a", "B822: DEC-422 cube-compose verdict (per-strategy x exit-method composed PASS/FAIL); pre-1B+ consumer for cube replay pipeline"),
}


def _scan_write_only_outputs() -> list[str]:
    """Replicate the AU8 scan: filenames written by writer.py with ZERO
    python read site across backtest/* + scripts/* (excluding tests/ +
    writer.py itself)."""
    src = (REPO / "backtest" / "results" / "writer.py").read_text(
        encoding="utf-8"
    )
    outs = set()
    file_pattern = re.compile(
        r"""['"]\s*([a-zA-Z0-9_\-]+\.(?:csv|parquet|json|html|txt))\s*['"]"""
    )
    for m in file_pattern.finditer(src):
        outs.add(m.group(1))

    read_kw = re.compile(
        r"(read_csv|read_parquet|read_json|read_text|read_bytes|"
        r"json\.load|json\.loads|load_json|load_csv|load_parquet|loads|"
        r"open\([^)]+['\"]r)"
    )
    py_files = []
    for sub in ("backtest", "scripts"):
        root = REPO / sub
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if "tests" in p.parts or p.name == "writer.py":
                continue
            py_files.append(p)

    write_only = []
    for o in sorted(outs):
        needle = re.compile(re.escape(o))
        found = False
        for p in py_files:
            try:
                t = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for ln in t.splitlines():
                if needle.search(ln) and read_kw.search(ln):
                    found = True
                    break
            if found:
                break
        if not found:
            write_only.append(o)
    return write_only


def test_registry_covers_all_write_only_outputs():
    """Drift guard: every actually-write-only output must have a
    CLASSIFICATION entry. Forces any new write-only artifact to get
    classified before merge."""
    write_only = set(_scan_write_only_outputs())
    classified = set(CLASSIFICATION.keys())
    missing = sorted(write_only - classified)
    assert not missing, \
        f"{len(missing)} write-only outputs are not in CLASSIFICATION: " \
        f"{missing}. Add each to the registry with class letter + reason."


def test_registry_has_no_stale_entries():
    """Reverse guard: if a classified output now has a python reader,
    remove it from CLASSIFICATION."""
    write_only = set(_scan_write_only_outputs())
    classified = set(CLASSIFICATION.keys())
    stale = sorted(classified - write_only)
    assert not stale, \
        f"{len(stale)} CLASSIFICATION entries now have python readers " \
        f"(remove from registry): {stale}"


def test_every_class_letter_in_legal_set():
    """All classification letters must be one of a/b/c/d."""
    legal = {"a", "b", "c", "d"}
    bad = {k: v for k, v in CLASSIFICATION.items() if v[0] not in legal}
    assert not bad, f"Illegal classification letters: {bad}"


def test_classification_distribution_matches_scan_size():
    """Sanity: registry total must equal the actual scan count."""
    write_only_count = len(_scan_write_only_outputs())
    assert len(CLASSIFICATION) == write_only_count, \
        f"registry size {len(CLASSIFICATION)} != actual write-only {write_only_count}"
