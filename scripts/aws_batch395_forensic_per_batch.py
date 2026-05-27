"""Batch 409 (2026-05-27): per-batch forensic investigation + auto-abort.

Owner directive: monitoring framework must include investigation levels
per batch.  When a batch's _COMPLETE sentinel lands in S3, this script
runs the same forensic checks that were applied manually to batch_1
on 2026-05-27:

  Zero-fire strategy count, signal silent regressions, trade volume
  vs prior batch, win rate distribution, direction balance, cube cell
  coverage, engine traceback grep, schema validation.

Returns:
  rc=0 PASS    -- batch outputs look healthy; continue subsequent batches
  rc=1 WARN    -- minor anomalies; continue but flag in monitor
  rc=2 ABORT   -- major error; terminate subsequent batches; require fix +
                  relaunch all (because cross-batch consistency matters)

Outputs a JSON summary to s3://bucket/forensic/batch_N.json so the
monitor + merge can read it.

Usage:
    python scripts/aws_batch395_forensic_per_batch.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --batch 2 \\
        --baseline-batch 1  # compare to this batch for regression detection

Source (per CHECKLIST #77): owner directive 2026-05-27.

Pre-flight per CHECKLIST + memory (visible block per #85):
  [check] #85 pre-flight visible
  [check] feedback_strategy_x_exit_cell_analysis.md -- (strategy, exit) cells
  [check] feedback_monitor_intermediate_counts.md -- intermediate baselines
  [check] #84 verify data availability before claiming engine bug --
          checks run AFTER batch produces output so data is verified by
          existence of _COMPLETE sentinel
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Severity thresholds
# ---------------------------------------------------------------------------

ABORT_RULES = {
    "zero_trades":           "0 trades fired -- engine broken or no data",
    "engine_traceback":      "Python Traceback in engine log",
    "engine_killed_oom":     "engine_log contains 'Killed' or 'MemoryError'",
    "zero_fire_strategy_pct_above_95": "> 95% of active strategies fired 0 trades (engine broken)",
    "signal_critical_zero":  "any required signal fire_rate=0% (silent regression)",
    "schema_critical_missing": "trade_log missing critical column (pnl_pct, strategy, exit_method, etc.)",
    "trade_log_empty":       "trade_log.csv empty or missing",
    "cube_empty":            "trade_exit_detail.csv empty or missing (cube replay failed)",
}

WARN_RULES = {
    "zero_fire_strategy_pct_above_75":  "> 75% of active strategies fired 0 trades (regime-conditional, but check)",
    "win_rate_extreme":                  "aggregate WR < 10% or > 90% (anomaly)",
    "direction_balance_extreme":         "long share < 5% or > 95%",
    "signal_silent_regression_flagged":  "signal_fire_rates.json has alert(s)",
    "trade_volume_off_baseline_3x":      "trade count is < 33% or > 300% of baseline batch",
    "cube_cell_coverage_low":            "< 20% of (strategy, exit) cells have n>=5 trades",
    "all_regimes_negative_pnl":          "every regime aggregate PnL is negative (expected cap-off; flag)",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def s3_cp_local(bucket: str, key: str, local: Path) -> bool:
    """Download s3://bucket/key to local; returns True on success."""
    cmd = ["aws", "s3", "cp", f"s3://{bucket}/{key}", str(local),
           "--no-progress", "--only-show-errors"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return r.returncode == 0 and local.exists() and local.stat().st_size > 0


def s3_check_exists(bucket: str, key: str) -> bool:
    cmd = ["aws", "s3api", "head-object", "--bucket", bucket, "--key", key]
    return subprocess.run(cmd, capture_output=True, timeout=30).returncode == 0


def s3_put_json(bucket: str, key: str, data: dict) -> bool:
    """Upload a JSON dict to s3://bucket/key."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f, indent=2)
        tmp = Path(f.name)
    try:
        cmd = ["aws", "s3", "cp", str(tmp), f"s3://{bucket}/{key}",
               "--no-progress", "--only-show-errors"]
        return subprocess.run(cmd, capture_output=True, timeout=60).returncode == 0
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Check functions -- each returns (passed: bool, severity: str, message: str)
# ---------------------------------------------------------------------------

def check_complete_sentinel(bucket: str, batch_index: int) -> tuple[bool, str, str]:
    if s3_check_exists(bucket, f"outputs/batch_{batch_index}/_COMPLETE"):
        return True, "pass", "_COMPLETE sentinel present in S3"
    return False, "abort", "_COMPLETE sentinel missing -- batch did not finish"


def check_engine_log_clean(local_dir: Path) -> list[tuple[bool, str, str]]:
    """Scan engine log for traceback / killed / memory errors."""
    log = local_dir / "batch395-engine.log"
    if not log.exists():
        return [(True, "warn", "engine log not uploaded; cannot check for crash signatures")]
    src = log.read_text(encoding="utf-8", errors="replace")
    results = []
    if "Traceback (most recent call last)" in src:
        results.append((False, "abort", "engine_traceback: Python Traceback in engine log"))
    if "MemoryError" in src or "\nKilled\n" in src:
        results.append((False, "abort", "engine_killed_oom: OOM kill / MemoryError detected"))
    if not results:
        results.append((True, "pass", "engine log clean (no Traceback / Killed / MemoryError)"))
    return results


def check_trade_log(local_dir: Path, registered_strategies: int) -> list[tuple[bool, str, str]]:
    """Forensic checks on trade_log.csv."""
    import pandas as pd
    tl_path = local_dir / "trade_log.csv"
    if not tl_path.exists():
        return [(False, "abort", "trade_log_empty: trade_log.csv missing")]
    try:
        tl = pd.read_csv(tl_path, low_memory=False)
    except Exception as e:
        return [(False, "abort", f"trade_log_empty: trade_log.csv unreadable ({e})")]
    if tl.empty:
        return [(False, "abort", "zero_trades: trade_log.csv has 0 rows")]

    results = []
    # Schema check
    required = ["ticker", "strategy", "entry_date", "direction", "pnl_pct", "win"]
    missing = [c for c in required if c not in tl.columns]
    if missing:
        results.append((False, "abort", f"schema_critical_missing: missing columns {missing}"))

    # Zero-fire strategies
    fired = tl["strategy"].nunique() if "strategy" in tl.columns else 0
    zero_fire = registered_strategies - fired
    zero_fire_pct = 100 * zero_fire / max(1, registered_strategies)
    if zero_fire_pct > 95:
        results.append((False, "abort",
            f"zero_fire_strategy_pct_above_95: {zero_fire_pct:.0f}% of "
            f"{registered_strategies} strategies fired 0 trades ({zero_fire} silent)"))
    elif zero_fire_pct > 75:
        results.append((False, "warn",
            f"zero_fire_strategy_pct_above_75: {zero_fire_pct:.0f}% of "
            f"{registered_strategies} strategies fired 0 trades ({zero_fire} silent)"))
    else:
        results.append((True, "pass",
            f"strategy fire coverage healthy: {fired}/{registered_strategies} fired "
            f"({100-zero_fire_pct:.0f}% activation)"))

    # Win rate
    if "win" in tl.columns:
        wr = tl["win"].mean()
        if wr < 0.10 or wr > 0.90:
            results.append((False, "warn",
                f"win_rate_extreme: aggregate WR {wr*100:.1f}% outside [10%, 90%]"))

    # Direction balance
    if "direction" in tl.columns:
        long_pct = (tl["direction"] == "long").mean()
        if long_pct < 0.05 or long_pct > 0.95:
            results.append((False, "warn",
                f"direction_balance_extreme: long share {long_pct*100:.1f}%"))

    # All-regimes-negative
    if "regime" in tl.columns and "pnl_pct" in tl.columns:
        regime_pnl = tl.groupby("regime")["pnl_pct"].sum()
        if (regime_pnl < 0).all() and len(regime_pnl) >= 3:
            results.append((False, "warn",
                f"all_regimes_negative_pnl: every regime negative "
                f"({regime_pnl.to_dict()})"))

    return results


def check_cube(local_dir: Path) -> list[tuple[bool, str, str]]:
    """Forensic checks on trade_exit_detail.csv (cube)."""
    import pandas as pd
    cube_path = local_dir / "trade_exit_detail.csv"
    if not cube_path.exists():
        return [(False, "abort", "cube_empty: trade_exit_detail.csv missing (cube replay failed)")]
    try:
        cube = pd.read_csv(cube_path, low_memory=False)
    except Exception as e:
        return [(False, "abort", f"cube_empty: unreadable ({e})")]
    if cube.empty:
        return [(False, "abort", "cube_empty: trade_exit_detail.csv has 0 rows")]

    results = []
    # Cell coverage
    if "strategy" in cube.columns and "exit_method" in cube.columns:
        cells = cube.groupby(["strategy", "exit_method"]).size()
        n_cells_total = len(cells)
        n_cells_n5 = (cells >= 5).sum()
        coverage_pct = 100 * n_cells_n5 / max(1, n_cells_total)
        if coverage_pct < 20:
            results.append((False, "warn",
                f"cube_cell_coverage_low: {n_cells_n5}/{n_cells_total} "
                f"({coverage_pct:.0f}%) of cells have n>=5"))
        else:
            results.append((True, "pass",
                f"cube cell coverage: {n_cells_n5}/{n_cells_total} "
                f"({coverage_pct:.0f}%) cells passed n>=5 floor"))
    return results


def check_signal_fire_rates(local_dir: Path) -> list[tuple[bool, str, str]]:
    """Read signal_fire_rates.json and surface flagged regressions."""
    p = local_dir / "signal_fire_rates.json"
    if not p.exists():
        return [(True, "warn", "signal_fire_rates.json missing -- skipped")]
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        return [(True, "warn", f"signal_fire_rates.json unreadable: {e}")]
    results = []
    flags = data.get("flags", [])
    signals = data.get("signals", {})
    for sig_name, sig_info in signals.items():
        if sig_info.get("fire_rate", 1) == 0:
            results.append((False, "abort",
                f"signal_critical_zero: {sig_name} fire_rate=0% (silent regression)"))
    if flags:
        results.append((False, "warn",
            f"signal_silent_regression_flagged: {len(flags)} flag(s): "
            f"{'; '.join(flags[:3])}"))
    elif not results:
        results.append((True, "pass",
            f"signal fire rates clean ({len(signals)} signals checked)"))
    return results


def check_trade_volume_vs_baseline(local_dir: Path, baseline_dir: Path | None) -> list[tuple[bool, str, str]]:
    """Compare batch's trade count to a baseline batch."""
    if baseline_dir is None or not baseline_dir.exists():
        return [(True, "pass", "no baseline to compare; skip volume check")]
    import pandas as pd
    try:
        cur_tl = pd.read_csv(local_dir / "trade_log.csv", low_memory=False)
        base_tl = pd.read_csv(baseline_dir / "trade_log.csv", low_memory=False)
    except Exception as e:
        return [(True, "warn", f"baseline volume check skipped: {e}")]
    cur_n = len(cur_tl)
    base_n = len(base_tl)
    if base_n == 0:
        return [(True, "warn", "baseline has 0 trades; cannot compute ratio")]
    ratio = cur_n / base_n
    if ratio < 0.33 or ratio > 3.0:
        return [(False, "warn",
            f"trade_volume_off_baseline_3x: cur={cur_n} base={base_n} "
            f"ratio={ratio:.2f}x (outside [0.33x, 3x])")]
    return [(True, "pass",
        f"trade volume within range of baseline (cur={cur_n}, base={base_n}, ratio={ratio:.2f}x)")]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--batch", type=int, required=True,
                    help="batch index to forensically investigate")
    ap.add_argument("--baseline-batch", type=int, default=None,
                    help="batch index to use as baseline for volume/cell comparison")
    ap.add_argument("--registered-strategies", type=int, default=185,
                    help="expected active strategy count (default 185 per current ALL_STRATEGIES)")
    ap.add_argument("--workdir", default=None,
                    help="local download dir (default tempdir)")
    args = ap.parse_args()

    workdir = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="forensic_"))
    local_dir = workdir / f"batch_{args.batch}"
    local_dir.mkdir(parents=True, exist_ok=True)

    print(f"[FORENSIC batch_{args.batch}] workdir={workdir}")

    # Phase 1: confirm batch complete
    ok, sev, msg = check_complete_sentinel(args.bucket, args.batch)
    if not ok:
        result = {
            "batch": args.batch,
            "verdict": "ABORT",
            "ts": datetime.now(timezone.utc).isoformat(),
            "checks": [{"severity": "abort", "message": msg, "passed": False}],
        }
        s3_put_json(args.bucket, f"forensic/batch_{args.batch}.json", result)
        print(f"[FORENSIC batch_{args.batch}] verdict=ABORT ({msg})")
        return 2

    # Phase 2: download key output files
    keys = ["trade_log.csv", "trade_exit_detail.csv", "verdict_cube.csv",
            "signal_fire_rates.json", "backtest_results.csv",
            "batch395-engine.log"]
    print(f"[FORENSIC batch_{args.batch}] downloading outputs...")
    for k in keys:
        s3_cp_local(args.bucket, f"outputs/batch_{args.batch}/{k}", local_dir / k)

    # Baseline download
    baseline_dir = None
    if args.baseline_batch:
        baseline_dir = workdir / f"batch_{args.baseline_batch}_baseline"
        baseline_dir.mkdir(parents=True, exist_ok=True)
        s3_cp_local(args.bucket, f"outputs/batch_{args.baseline_batch}/trade_log.csv",
                    baseline_dir / "trade_log.csv")

    # Phase 3: run all checks
    all_checks: list[tuple[bool, str, str]] = []
    all_checks.extend(check_engine_log_clean(local_dir))
    all_checks.extend(check_trade_log(local_dir, args.registered_strategies))
    all_checks.extend(check_cube(local_dir))
    all_checks.extend(check_signal_fire_rates(local_dir))
    all_checks.extend(check_trade_volume_vs_baseline(local_dir, baseline_dir))

    # Phase 4: aggregate verdict
    aborts = [(p, s, m) for p, s, m in all_checks if s == "abort"]
    warns = [(p, s, m) for p, s, m in all_checks if s == "warn" and not p]
    passes = [(p, s, m) for p, s, m in all_checks if s == "pass"]

    if aborts:
        verdict = "ABORT"
        rc = 2
    elif warns:
        verdict = "WARN"
        rc = 1
    else:
        verdict = "PASS"
        rc = 0

    print(f"\n[FORENSIC batch_{args.batch}] verdict={verdict}")
    print(f"  abort={len(aborts)} warn={len(warns)} pass={len(passes)}")
    for p, s, m in aborts:
        print(f"  [ABORT] {m}")
    for p, s, m in warns:
        print(f"  [WARN ] {m}")
    for p, s, m in passes:
        print(f"  [PASS ] {m}")

    # Phase 5: write JSON summary to S3
    result = {
        "batch": args.batch,
        "verdict": verdict,
        "ts": datetime.now(timezone.utc).isoformat(),
        "baseline_batch": args.baseline_batch,
        "checks": [
            {"passed": p, "severity": s, "message": m}
            for p, s, m in all_checks
        ],
        "summary": {
            "abort_count": len(aborts),
            "warn_count": len(warns),
            "pass_count": len(passes),
        },
    }
    s3_put_json(args.bucket, f"forensic/batch_{args.batch}.json", result)
    print(f"\n[FORENSIC batch_{args.batch}] verdict JSON -> "
          f"s3://{args.bucket}/forensic/batch_{args.batch}.json")
    if verdict == "ABORT":
        print(f"\n[ABORT] Subsequent batches should be terminated.  Per owner")
        print(f"        directive: bug fix + relaunch ALL batches (cross-batch")
        print(f"        consistency).  See AUDIT for next-batch handler.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
