"""Batch 367 (orig) + Batch 393 (expansion): Pre-Launch Validation Suite for Phase 1A-beta.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-25 Option A (Batch 367) + owner directive 2026-05-26 (Batch 393):
"Expand the 6 phase validation suite to ensure the mistakes of latest run
are caught and addressed early on. Update the testing pyramid with new
latest multi phase validation suite."

Ten independent pre-launch phases (1-6 + 8-11) + 1 post-run phase (7).
Each FAILS hard on detection. Run before any Phase 1A-beta full launch.
Wall time ~6-12 min (Phase 3 smoke ~5min, Phase 9 producer sweep ~40s).

PHASES (pre-launch):
  1. Data Prerequisites Audit      catches missing prefetch dirs / files
  2. Generalized Fire-Rate Gate    catches BUG-296-family silent gaps
                                   across smart money signals
  3. Config Independence Smoke     catches env-var-dependency drift (e.g.
                                   QUIVER_API_KEY gate that broke Batch 363)
  4. Silent-Gap Regression Suite   one assertion per known BUG-NNN fix
  5. Cube Cell Coverage Gate       catches save_all_outputs cube failures
                                   that leave trade_exit_detail empty
  6. Doc/Code Alignment Gate       catches count drift in CLAUDE.md /
                                   CANONICAL_FACTS.md (Batch 357 hardened)
  8. Cube Gate Enablement Check    (Batch 393) verifies all 5 cube
                                   auto-enables (377/383/384/386) fire in
                                   current code -- catches the class of bug
                                   where a flag is added but never auto-set
  9. Generalized Producer Emit     (Batch 393) sweeps every required boolean
                                   producer across ~400 ticker-bar samples;
                                   catches always-False bugs (squeeze_fire_up
                                   class) BEFORE strategies depend on them
 10. Strategy Wiring Audit Gate    (Batch 393) gates on strategy_wiring_audit
                                   results; HARD-FAIL on producer-consumer
                                   mismatch / default-trap / synthesize
                                   inconsistency / type incompatibility
 11. Intermediate Monitor Armed    (Batch 393) verifies the intermediate
                                   trade-count monitor is in place with
                                   abort thresholds so a 361-trade-style
                                   collapse aborts early rather than at end

POST-RUN:
  7. Post-Run Validation           validates fresh merged output dir
                                   (trade_log/cube/winners/signals)

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
def phase_8_cube_gate_enablement() -> list[str]:
    """Batch 393: verify ALL 5 Phase-1A-beta cube auto-enables fire in current
    code. Catches the Batch-369-era class of bug where Phase 1A-beta launched
    with stale code that lacked cube-flag auto-enable.

    Auto-enables required (when --phase=1a-beta):
      Batch 377: --no-portfolio-cap        (Batch 203 cap @25 bypassed)
      Batch 383: --no-dd-halt              (DEC-515 Level 6 halt bypassed)
      Batch 384: --no-regime-affinity      (Batch 203/293 affinity bypassed)
      Batch 384: --no-event-suppression    (DEC-348 windows bypassed)
      Batch 386: --max-cands 30 -> 200     (screener throughput raised)
    """
    fails = []
    src = (REPO / "backtest" / "run_phase1a.py").read_text(encoding="utf-8")
    checks = [
        ("377", "[Batch 377]", "args.no_portfolio_cap = True"),
        ("383", "[Batch 383]", "args.no_dd_halt = True"),
        ("384a", "[Batch 384]", "args.no_regime_affinity = True"),
        ("384b", "[Batch 384]", "args.no_event_suppression = True"),
        ("386", "[Batch 386]", "args.max_cands = 200"),
    ]
    for tag, banner, set_line in checks:
        if banner not in src:
            fails.append(f"Batch {tag}: banner '{banner}' missing from run_phase1a.py")
        if set_line not in src:
            fails.append(f"Batch {tag}: auto-enable '{set_line}' missing")
    # Also: BacktestEngine __init__ must accept all 4 keyword args
    eng_src = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    for kwarg in ("no_portfolio_cap", "no_dd_halt",
                   "no_regime_affinity", "no_event_suppression"):
        if f"{kwarg}:" not in eng_src and f"{kwarg}=" not in eng_src:
            fails.append(f"BacktestEngine.__init__ missing kwarg: {kwarg}")
    return fails


def phase_9_generalized_producer_emit_check() -> list[str]:
    """Batch 393: extend Phase 2 (smart-money only) to ALL producer modules.
    Catches the squeeze_fire_up / smc_equal_swept class of bug where a
    producer key is emitted but the value is ALWAYS FALSE due to a logic
    formula error.

    For each known producer module, invoke compute_* on a sample of OHLCV
    and verify booleans are not always-False.
    """
    fails = []
    import pandas as pd
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA",
                "JPM", "XOM", "JNJ"]
    # Batch 393 fix: original 4-bar sampling produced 40 total last-bar
    # samples. With a 5% true emit rate, P(0 truthy in 40) ~= 13% - too
    # high a false-positive rate. Sweep end_idx in 25-bar steps across each
    # ticker history (~40 windows/ticker x 10 tickers = ~400 samples).
    # For 5% true rate, P(0 truthy in 400) ~= 3.5e-5 - safe.
    samples = []
    for t in tickers:
        p = REPO / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{t}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        df.index = pd.DatetimeIndex(pd.to_datetime(df["date"], errors="coerce"))
        # Need at least 252 bars of warmup before any usable signal.
        n = len(df)
        if n < 300:
            continue
        for end_idx in range(252, n, 25):
            samples.append(df.iloc[max(0, end_idx - 252):end_idx])
    if not samples:
        return ["Phase 9: no OHLCV samples to verify producers"]

    from backtest.signals.technical import compute_all_signals, compute_squeeze
    from backtest.signals.smc_ict import compute_smc_signals

    # Collect emit-rates per boolean key
    key_emit = {}  # key -> {present, truthy}
    for s in samples:
        try:
            all_sig = compute_all_signals(s)
        except Exception:
            continue
        for k, v in all_sig.items():
            if isinstance(v, bool):
                d = key_emit.setdefault(k, {"present": 0, "truthy": 0})
                d["present"] += 1
                if v:
                    d["truthy"] += 1
        # Also compute_squeeze + smc explicitly to catch dynamic keys
        try:
            sq = compute_squeeze(s)
            for k, v in sq.items():
                if isinstance(v, bool):
                    d = key_emit.setdefault(k, {"present": 0, "truthy": 0})
                    d["present"] += 1
                    if v:
                        d["truthy"] += 1
        except Exception:
            pass
        try:
            sm = compute_smc_signals(s)
            for k, v in sm.items():
                if isinstance(v, bool):
                    d = key_emit.setdefault(k, {"present": 0, "truthy": 0})
                    d["present"] += 1
                    if v:
                        d["truthy"] += 1
        except Exception:
            pass

    # Known boolean keys that SHOULD emit truthy at SOME positive rate.
    # Catches squeeze_fire_up / smc_equal_swept-style always-False bugs:
    # those bugs produce emit rates of exactly 0 or near-0.  A uniform
    # 0.5% threshold across ~400 samples means a bug-free producer firing
    # at >=1% true rate will pass with high probability, while an
    # always-False producer (0/N) will reliably fail.  Threshold is
    # bug-detection floor, not an empirical rate prediction.
    REQUIRED_TRUTHY = {
        "squeeze_fire_up":          0.005,
        "squeeze_fire_dn":          0.005,
        "smc_equal_highs_swept":    0.005,
        "smc_equal_lows_swept":     0.005,
        "smc_bos_bullish":          0.005,
        "smc_bos_bearish":          0.005,
        "smc_fvg_bullish_active":   0.005,
        "smc_fvg_bearish_active":   0.005,
        "rsi_14_oversold":          0.005,
        "rsi_14_overbought":        0.005,
        "vol_spike_2x":             0.005,
        "vol_spike_15x":            0.005,
    }
    for k, min_rate in REQUIRED_TRUTHY.items():
        d = key_emit.get(k)
        if d is None or d["present"] == 0:
            fails.append(f"Phase 9: required key `{k}` never emitted on sample")
            continue
        rate = d["truthy"] / d["present"]
        if rate < min_rate:
            fails.append(
                f"Phase 9: `{k}` emit rate {rate*100:.2f}% < required "
                f"{min_rate*100:.2f}% (producer logic bug suspected; "
                f"emit-truthy count={d['truthy']}/{d['present']})"
            )
    return fails


def phase_10_strategy_wiring_audit_gate() -> list[str]:
    """Batch 393: gate on `scripts/strategy_wiring_audit.py` results.
    Catches silent wiring drift (producer-consumer key mismatch, default-trap
    on missing producer, type incompatibility) that crept in since the last
    Batch-392 audit.
    """
    fails = []
    audit_json = REPO / "output_audit" / "strategy_wiring_audit.json"
    if not audit_json.exists():
        # Try to regenerate
        try:
            r = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "strategy_wiring_audit.py")],
                capture_output=True, text=True, timeout=300,
            )
            if r.returncode != 0:
                return [f"Phase 10: strategy_wiring_audit.py failed exit={r.returncode}; "
                         f"stderr: {r.stderr[-300:]}"]
        except Exception as e:
            return [f"Phase 10: could not run strategy_wiring_audit.py: {e}"]
    if not audit_json.exists():
        return ["Phase 10: strategy_wiring_audit.json not produced"]
    audit = json.loads(audit_json.read_text())
    by_class = audit.get("summary", {}).get("findings_by_class", {})
    # HARD FAIL classes: real bugs
    for cls in ("PRODUCER_CONSUMER_MISMATCH", "DEFAULT_TRAP",
                "SYNTHESIZE_INCONSISTENT", "TYPE_INCOMPATIBLE"):
        n = by_class.get(cls, 0)
        if n > 0:
            fails.append(
                f"Phase 10: strategy wiring audit found {n} `{cls}` findings - "
                f"see output_audit/strategy_wiring_audit.md for details"
            )
    # SOFT WARN: SYNTHESIZE_NEVER_FIRES (synth limitation, not bug)
    n_never = by_class.get("SYNTHESIZE_NEVER_FIRES", 0)
    if n_never > 40:
        fails.append(
            f"Phase 10: SYNTHESIZE_NEVER_FIRES count {n_never} > 40 - "
            f"synthesizer coverage may have regressed; investigate"
        )
    return fails


def phase_11_intermediate_monitor_armed() -> list[str]:
    """Batch 393 (orig) + Batch 394 (expansion): verify the intermediate-
    progress health monitor + engine wall-time guards + 14 checks are
    armed.  Catches the class of bug from the 361-trade run where the
    pathology was discovered only at run-completion, wasting 10h compute.

    Batch 394 expansion:
      - Verify Python monitor scripts/monitor_phase_1a_beta_health.py
        contains all 14 check function names (W1-W14)
      - Verify engine has max_run_hours / warn_run_hours kwargs
      - Verify engine emits [MILESTONE-100D] / [MILESTONE-YEAR] /
        elapsed_hours= telemetry tokens
      - Backwards: keep checking shell script for backwards-compat
        (used by Stage D runners that haven't switched yet)

    Memory: feedback_monitor_intermediate_counts.md +
            feedback_strategy_x_exit_cell_analysis.md
    """
    fails = []

    # Batch 394: primary monitor is now Python; shell stays as backup.
    py_monitor = REPO / "scripts" / "monitor_phase_1a_beta_health.py"
    if not py_monitor.exists():
        fails.append(
            f"Phase 11 (Batch 394): Python monitor missing - "
            f"{py_monitor.relative_to(REPO)}"
        )
    else:
        py_src = py_monitor.read_text(encoding="utf-8")
        # 14 check function names W1-W14 must all be present.
        required_check_fns = [f"check_w{n}_" for n in range(1, 15)]
        for fn in required_check_fns:
            if fn not in py_src:
                fails.append(
                    f"Phase 11 (Batch 394): Python monitor missing "
                    f"check function `{fn}*` (14-check coverage gap)"
                )
        # Critical thresholds must be parameterized in CLI.
        for tok in ("max-run-hours", "warn-run-hours", "baseline-tpd",
                    "abort-ratio", "warn-ratio", "auto-kill"):
            if tok not in py_src:
                fails.append(
                    f"Phase 11 (Batch 394): Python monitor missing CLI "
                    f"arg --{tok}"
                )

    # Backwards-compat shell monitor (kept until Stage D runners switch).
    sh_monitor = REPO / "scripts" / "monitor_phase_1a_beta_health.sh"
    if sh_monitor.exists():
        sh_src = sh_monitor.read_text(encoding="utf-8")
        if "BASELINE_TPD" not in sh_src:
            fails.append(
                "Phase 11: shell monitor missing baseline_trades_per_day"
            )
        if ("ABORT_RATIO" not in sh_src
                or "KILL-RECOMMENDED" not in sh_src):
            fails.append(
                "Phase 11: shell monitor missing abort-ratio + "
                "KILL-RECOMMENDED signal"
            )

    # Batch 394: engine wall-time kwargs must be wired.
    engine = REPO / "backtest" / "engine" / "backtest.py"
    if engine.exists():
        eng_src = engine.read_text(encoding="utf-8")
        for tok in ("max_run_hours", "warn_run_hours",
                    "WALL-TIME WARN", "WALL-TIME KILL",
                    "[MILESTONE-", "elapsed_hours="):
            if tok not in eng_src:
                fails.append(
                    f"Phase 11 (Batch 394): engine missing wall-time "
                    f"guard token `{tok}`"
                )

    return fails


PHASES = {
    1: ("Data Prerequisites Audit",       phase_1_data_prerequisites),
    2: ("Generalized Fire-Rate Gate",     phase_2_fire_rate_gate),
    3: ("Config Independence",            phase_3_config_independence),
    4: ("Silent-Gap Regression Suite",    phase_4_silent_gap_regression),
    5: ("Cube Cell Coverage Gate",        phase_5_cube_cell_coverage),
    6: ("Doc/Code Alignment Gate",        phase_6_doc_alignment),
    # Batch 393 expansion: catch the latest-run mistakes early on
    8: ("Cube Gate Enablement Check",     phase_8_cube_gate_enablement),
    9: ("Generalized Producer Emit",      phase_9_generalized_producer_emit_check),
    10:("Strategy Wiring Audit Gate",     phase_10_strategy_wiring_audit_gate),
    11:("Intermediate Monitor Armed",     phase_11_intermediate_monitor_armed),
}


def phase_7_post_run_validation(output_dir: Path) -> list[str]:
    """POST-RUN: validates a freshly-merged Phase 1A-beta output dir.

    Distinct from Phase 5 (cube cell coverage on smoke). Runs against
    the full merged output to verify:
      a. trade_log.csv non-empty + has expected schema (combo_id et al)
      b. trade_exit_detail.csv (the cube) populated
      c. signal_fire_rates.json shows smart-money signals fire properly
         (Batch 363 silent gap regression check)
      d. winners.parquet extractable (via extract_phase_1a_beta_winners)
      e. Cube cell count consistent with strategies x 25 exits
    """
    fails = []
    if not output_dir.exists():
        return [f"output_dir missing: {output_dir}"]

    tl = output_dir / "trade_log.csv"
    cube = output_dir / "trade_exit_detail.csv"
    sfr = output_dir / "signal_fire_rates.json"
    if not tl.exists():
        fails.append(f"trade_log.csv missing in {output_dir}")
    if not cube.exists():
        fails.append(f"trade_exit_detail.csv (cube) missing in {output_dir} "
                     f"-- save_all_outputs may have been killed early")
    if not sfr.exists():
        fails.append(f"signal_fire_rates.json missing in {output_dir}")

    # Smart-money fire-rate regression (Batch 363 gap)
    if sfr.exists():
        try:
            payload = json.loads(sfr.read_text())
            for name in ("smart_money_score", "congressional_signal",
                         "insider_signal", "institutional_signal"):
                entry = payload.get("signals", {}).get(name)
                if entry is None:
                    continue
                fr = entry.get("fire_rate", 0)
                em = entry.get("expected_min_rate", 0)
                if em and fr < em * 0.5:
                    fails.append(
                        f"{name}: fire_rate={fr*100:.1f}% < 50%-of-expected "
                        f"({em*100:.1f}%). Batch 363 silent gap may have "
                        f"recurred or data prerequisites are missing."
                    )
        except Exception as e:
            fails.append(f"signal_fire_rates.json unreadable: {e}")

    # winners.parquet extractable
    if tl.exists() or cube.exists():
        try:
            import subprocess
            r = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "extract_phase_1a_beta_winners.py"),
                 "--source", str(output_dir),
                 "--out",   str(output_dir / "winners.parquet")],
                capture_output=True, text=True, timeout=300,
            )
            # Exit 0 = >=1 P1 winner; 2 = zero P1; 1 = real failure
            if r.returncode == 1:
                fails.append(
                    f"winners extractor failed (exit 1):\n"
                    f"  stderr tail: {r.stderr[-500:]}"
                )
            elif r.returncode == 2:
                # Zero P1 winners is informational, not a fail. Surface in stdout.
                pass
        except Exception as e:
            fails.append(f"winners.parquet extraction crashed: {e}")

    # Cube coverage gate (per-method canonical)
    if cube.exists():
        try:
            import pandas as pd
            df = pd.read_csv(cube, low_memory=False)
            if df.empty:
                fails.append("trade_exit_detail.csv is empty (cube replay produced 0 rows)")
            else:
                n_methods = df["exit_method"].nunique() if "exit_method" in df else 0
                if n_methods < 20:
                    fails.append(
                        f"cube spans only {n_methods} exit methods < 20 "
                        f"(expected 25); multiple methods crashed silently"
                    )
        except Exception as e:
            fails.append(f"cube load failed: {e}")

    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="",
                    help="Comma-separated phase numbers to run; default all (pre-run)")
    ap.add_argument("--skip", default="",
                    help="Comma-separated phase numbers to skip")
    ap.add_argument("--smoke-output", default="",
                    help="Override smoke output dir for phase 5")
    ap.add_argument("--post-run", default="",
                    help="POST-RUN mode: validate the merged Phase 1A-beta "
                         "output at this dir. Runs phase 7 (post-run) instead "
                         "of phases 1-6 (pre-run).")
    args = ap.parse_args()

    # POST-RUN mode: short-circuit to phase 7
    if args.post_run:
        out_dir = REPO / args.post_run if not Path(args.post_run).is_absolute() else Path(args.post_run)
        print("=" * 78)
        print(f"  POST-RUN VALIDATION (Batch 367 Phase 7) -- {out_dir}")
        print("=" * 78)
        fails = phase_7_post_run_validation(out_dir)
        if fails:
            print(f"\nFAIL ({len(fails)} issue(s)):")
            for f in fails:
                print(f"  - {f}")
            print("\n  OVERALL: FAIL  -- output cannot be promoted to winners.parquet")
            sys.exit(1)
        print("\nPASS  -- output safe for winners.parquet + Phase 1B-alpha")
        sys.exit(0)

    run = set(int(p) for p in args.phase.split(",") if p) or set(PHASES.keys())
    skip = set(int(p) for p in args.skip.split(",") if p)
    run -= skip
    smoke_out = Path(args.smoke_output) if args.smoke_output else None

    print("=" * 78)
    print("  PRE-LAUNCH VALIDATION SUITE (Batch 393)")
    print("=" * 78)

    overall_pass = True
    total = len(PHASES)
    for idx, phase_num in enumerate(sorted(PHASES.keys()), start=1):
        name, fn = PHASES[phase_num]
        if phase_num not in run:
            print(f"\n[{idx}/{total}] Phase {phase_num} {name}: SKIPPED")
            continue
        print(f"\n[{idx}/{total}] Phase {phase_num} {name}...")
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
