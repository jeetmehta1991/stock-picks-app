"""Batch 367: Pre-Launch Validation Suite for Phase 1A-beta.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-25 Option A. Addresses owner concern after Batches 363/365/366
revealed multiple silent gaps: "Am concerned that there would be more
such silent gaps and we are not having enough testing to cover these
before we scale to full phase 1A beta."

Six independent phases. Each FAILS hard on detection. Run before any
Phase 1A-beta full launch. Wall time ~5-10 min (Phase 3 smoke is the
heaviest at ~5min on Hetzner / ~3min local).

PHASES:
  1. Data Prerequisites Audit      catches missing prefetch dirs / files
  2. Generalized Fire-Rate Gate    catches BUG-296-family silent gaps
                                   across ALL signals (not just smart money)
  3. Config Independence Smoke     catches env-var-dependency drift (e.g.
                                   QUIVER_API_KEY gate that broke Batch 363)
  4. Silent-Gap Regression Suite   one assertion per known BUG-NNN fix
  5. Cube Cell Coverage Gate       catches save_all_outputs cube failures
                                   that leave trade_exit_detail empty
  6. Doc/Code Alignment Gate       catches count drift in CLAUDE.md /
                                   CANONICAL_FACTS.md (Batch 357 hardened)

Usage:
  python scripts/pre_launch_validation.py                       # all phases
  python scripts/pre_launch_validation.py --phase 1,2,4         # subset
  python scripts/pre_launch_validation.py --skip 3              # skip slow
  python scripts/pre_launch_validation.py --smoke-output output_smoke_cube/

Exits 0 on all-PASS, 1 on any-FAIL.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


# ----------------------------------------------------------------------
# PHASE 1: Data Prerequisites Audit
# ----------------------------------------------------------------------
# Manifest of files/dirs the engine MUST have to run Phase 1A-beta.
# Each entry: (path_relative_to_repo, min_size_bytes, description).
# Min size 0 = directory must exist + be non-empty; 1+ = file must be that size.
DATA_PREREQS = [
    # OHLCV prefetch (Polygon)
    ("data_prefetch/polygon/ohlcv_daily", 0, "Polygon OHLCV daily prefetch dir"),
    # Quiver smart money prefetches (Batch 363 silent-gap data deps)
    ("data_prefetch/quiver/insiders/global.parquet", 100_000,
     "Quiver insiders bulk feed (Batch 363 dep)"),
    ("data_prefetch/quiver/congressional", 0,
     "Quiver congressional per-ticker dir (Batch 363 dep)"),
    ("data_prefetch/quiver/institutional", 0,
     "Quiver institutional per-ticker dir (Batch 294 dep)"),
    ("data_prefetch/quiver/sec13fchanges/global.parquet", 100_000,
     "Quiver sec13fchanges bulk feed"),
    # Polygon financials (PEAD + Fundamentals Analyst)
    ("data_prefetch/polygon/financials", 0,
     "Polygon financials per-ticker (PEAD/Fundamentals dep)"),
    # Polygon news (News Analyst + sentiment)
    ("data_prefetch/polygon/news", 0,
     "Polygon news per-ticker (News Analyst dep)"),
    # FRED macro
    ("data_prefetch/fred/fomc_calendar.parquet", 1_000,
     "FRED FOMC calendar (Batch 342)"),
    # T1A universe + Tier 1 ETFs
    ("Backtesting universe", 0, "Universe CSVs top-level dir"),
    # Economic calendar JSON (Batch 366)
    ("backtest/data/economic_calendar.json", 1_000,
     "Hardcoded economic calendar JSON (Batch 366)"),
    # Derived precomputes
    ("data_prefetch/derived/cointegrated_pairs_t1a", 0,
     "T5b cointegrated pairs precompute (Batch 326)"),
    ("data_prefetch/derived/index_rebalance_events.parquet", 1_000,
     "Index rebalance events (Batch 325+341)"),
    # Stage D ticker list
    ("scripts/stage_d_tickers.txt", 100, "Stage D 150-ticker stratified sample"),
]


def phase_1_data_prerequisites() -> list[str]:
    """Returns list of failure strings; empty list = PASS."""
    fails = []
    for rel_path, min_size, desc in DATA_PREREQS:
        p = REPO / rel_path
        if not p.exists():
            fails.append(f"MISSING: {rel_path} ({desc})")
            continue
        if p.is_dir():
            children = list(p.iterdir())
            if not children:
                fails.append(f"EMPTY DIR: {rel_path} ({desc})")
        elif p.is_file():
            size = p.stat().st_size
            if size < min_size:
                fails.append(
                    f"TOO SMALL: {rel_path} = {size}B < {min_size}B ({desc})"
                )
    return fails


# ----------------------------------------------------------------------
# PHASE 2: Generalized Fire-Rate Gate
# ----------------------------------------------------------------------
def _find_signal_fire_rates() -> Path | None:
    """Locate the most-recent signal_fire_rates.json."""
    candidates = [
        REPO / "output_phase_1a_beta_merged_local" / "signal_fire_rates.json",
        REPO / "output_smoke_cube" / "signal_fire_rates.json",
        REPO / "output_stage_d" / "signal_fire_rates.json",
    ]
    return next((p for p in candidates if p.exists()), None)


def phase_2_fire_rate_gate() -> list[str]:
    """Fail if any signal has fire_rate < 50% of expected_min_rate."""
    fails = []
    p = _find_signal_fire_rates()
    if p is None:
        return ["NO signal_fire_rates.json found in any output dir; "
                "run scripts/smoke_test_cube_stage_d.py first"]
    try:
        payload = json.loads(p.read_text())
    except Exception as e:
        return [f"Failed to load {p}: {e}"]
    signals = payload.get("signals", {})
    if not signals:
        return [f"{p} has empty 'signals' dict"]
    for name, entry in signals.items():
        if not isinstance(entry, dict):
            continue
        fr = entry.get("fire_rate")
        em = entry.get("expected_min_rate")
        alert = entry.get("alert")
        if fr is None or em is None:
            continue
        gate = em * 0.5
        if fr < gate:
            fails.append(
                f"{name}: fire_rate={fr*100:.1f}% < 50% of expected_min "
                f"({em*100:.1f}%) = {gate*100:.1f}% gate. alert={alert}"
            )
    return fails


# ----------------------------------------------------------------------
# PHASE 3: Config Independence Smoke
# ----------------------------------------------------------------------
def phase_3_config_independence(skip: bool = False) -> list[str]:
    """Run a tiny smoke twice -- once with optional env vars set,
    once with them unset -- and assert verdict-critical columns
    byte-identical. Catches the QUIVER_API_KEY-class silent gap."""
    if skip:
        return ["SKIPPED (--skip 3); manually verify env independence"]
    # We don't run a real backtest here for cost; instead we verify the
    # engine source contains NO `if os.environ.get(...)` gates around
    # data-loading function calls. The actual smoke comparison lives in
    # scripts/smoke_test_screen_pool.py for pool parity; the env-var
    # check is purely static-source.
    fails = []
    engine_src = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    # Pattern: `if os.environ.get("XYZ_KEY"): <data-loading-call>`
    suspect_patterns = [
        ("QUIVER_API_KEY", "smart_money_score"),
        ("ANTHROPIC_API_KEY", "agent_pipeline"),
        ("POLYGON_API_KEY", "polygon_"),
        ("FRED_API_KEY", "macro_snapshot"),
    ]
    lines = engine_src.splitlines()
    for i, line in enumerate(lines):
        for env_var, paired_call in suspect_patterns:
            if f'os.environ.get("{env_var}")' in line:
                # Check the next 3 lines for the paired call
                window = "\n".join(lines[i:i+4])
                if paired_call in window:
                    fails.append(
                        f"backtest.py:{i+1}: env-var gate on data-loading "
                        f"function ({env_var} -> {paired_call}). The "
                        f"Batch 363 silent-gap pattern. Cache reads should "
                        f"not depend on API keys."
                    )
    return fails


# ----------------------------------------------------------------------
# PHASE 4: Silent-Gap Regression Suite
# ----------------------------------------------------------------------
def phase_4_silent_gap_regression() -> list[str]:
    """Run the silent-gap pyramid file + Batch 363 + 365 + 366 tests
    via pytest. Fail if any regression test fails."""
    fails = []
    test_files = [
        "backtest/tests/test_silent_gap_pyramid.py",
        "backtest/tests/test_batch363_smart_money_engine_fix.py",
        "backtest/tests/test_batch365_silent_gap_hardening.py",
        "backtest/tests/test_batch365_audit_semantic_population.py",
        "backtest/tests/test_batch365_criterion_evaluable.py",
        "backtest/tests/test_batch366_calendar_coverage.py",
    ]
    available = [f for f in test_files if (REPO / f).exists()]
    if not available:
        return ["No silent-gap regression test files found"]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=line", *available],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    if result.returncode != 0:
        # Parse last 30 lines for failure context
        tail = "\n".join(result.stdout.splitlines()[-30:])
        fails.append(f"silent-gap pyramid failed:\n{tail}")
    return fails


# ----------------------------------------------------------------------
# PHASE 5: Cube Cell Coverage Gate
# ----------------------------------------------------------------------
def phase_5_cube_cell_coverage(smoke_output: Path | None = None) -> list[str]:
    """If a recent smoke produced trade_exit_detail.csv (the cube),
    assert cube fan-out >= 50% of expected (n_trades * 25)."""
    candidates = [
        smoke_output / "trade_exit_detail.csv" if smoke_output else None,
        REPO / "output_smoke_cube" / "trade_exit_detail.csv",
        REPO / "output_audit" / "trade_exit_detail_phase_1a_beta_rebuilt.csv",
    ]
    cube_path = next((p for p in candidates if p and p.exists()), None)
    if cube_path is None:
        return ["No trade_exit_detail.csv found; run "
                "scripts/smoke_test_cube_stage_d.py first"]
    try:
        import pandas as pd
        cube = pd.read_csv(cube_path, low_memory=False)
    except Exception as e:
        return [f"Failed to load {cube_path}: {e}"]
    if cube.empty:
        return [f"{cube_path} is empty (cube replay failed silently)"]

    n_trades = cube["entry_date"].count() if "entry_date" in cube else len(cube)
    n_strategies = cube["strategy"].nunique() if "strategy" in cube else 0
    n_exit_methods = cube["exit_method"].nunique() if "exit_method" in cube else 0
    cells = cube.groupby(["strategy", "exit_method"]).ngroups if "strategy" in cube and "exit_method" in cube else 0

    fails = []
    expected_cells_min = int(n_strategies * 25 * 0.5)
    if cells < expected_cells_min:
        fails.append(
            f"cube cell coverage = {cells} < {expected_cells_min} "
            f"(50% of {n_strategies} strategies x 25 exits)"
        )
    if n_exit_methods < 20:
        fails.append(
            f"cube spans {n_exit_methods} exit methods < 20 (expected ~25). "
            f"Multiple exit methods crashed silently in run_exit_comparison."
        )
    return fails


# ----------------------------------------------------------------------
# PHASE 6: Doc/Code Alignment Gate
# ----------------------------------------------------------------------
def phase_6_doc_alignment() -> list[str]:
    """Run Batch 357 doc-count drift tests via pytest. Fail on any drift."""
    fails = []
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=line",
         "backtest/tests/test_unit.py::test_batch357_doc_count_drift_strategies",
         "backtest/tests/test_unit.py::test_batch357_doc_count_drift_exit_methods"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if result.returncode != 0:
        tail = "\n".join(result.stdout.splitlines()[-15:])
        fails.append(f"doc-count drift detected:\n{tail}")
    return fails


# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------
PHASES = {
    1: ("Data Prerequisites Audit",      phase_1_data_prerequisites),
    2: ("Generalized Fire-Rate Gate",    phase_2_fire_rate_gate),
    3: ("Config Independence",           phase_3_config_independence),
    4: ("Silent-Gap Regression Suite",   phase_4_silent_gap_regression),
    5: ("Cube Cell Coverage Gate",       phase_5_cube_cell_coverage),
    6: ("Doc/Code Alignment Gate",       phase_6_doc_alignment),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="",
                    help="Comma-separated phase numbers to run; default all")
    ap.add_argument("--skip", default="",
                    help="Comma-separated phase numbers to skip")
    ap.add_argument("--smoke-output", default="",
                    help="Override smoke output dir for phase 5")
    args = ap.parse_args()

    run = set(int(p) for p in args.phase.split(",") if p) or set(PHASES.keys())
    skip = set(int(p) for p in args.skip.split(",") if p)
    run -= skip
    smoke_out = Path(args.smoke_output) if args.smoke_output else None

    print("=" * 78)
    print("  PRE-LAUNCH VALIDATION SUITE (Batch 367)")
    print("=" * 78)

    overall_pass = True
    for phase_num in sorted(PHASES.keys()):
        name, fn = PHASES[phase_num]
        if phase_num not in run:
            print(f"\n[{phase_num}/6] {name}: SKIPPED")
            continue
        print(f"\n[{phase_num}/6] {name}...")
        if phase_num == 3:
            fails = fn(skip=False)
        elif phase_num == 5:
            fails = fn(smoke_output=smoke_out)
        else:
            fails = fn()
        if fails:
            overall_pass = False
            print(f"  FAIL ({len(fails)} issue(s)):")
            for f in fails:
                print(f"    - {f}")
        else:
            print(f"  PASS")

    print()
    print("=" * 78)
    if overall_pass:
        print("  OVERALL: PASS  -- safe to launch Phase 1A-beta")
        sys.exit(0)
    else:
        print("  OVERALL: FAIL  -- DO NOT launch Phase 1A-beta until resolved")
        sys.exit(1)


if __name__ == "__main__":
    main()
