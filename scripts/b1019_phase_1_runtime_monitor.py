# Source: Council 108 Option-5 Modified Enhancements A1+B2+D1+F1 +
# owner approval 2026-06-26 "Approve all 7" per CHECKLIST #77.
"""B1019 RUNTIME MONITOR: 100-day checkpoint armed monitor for Phase 1.

Surfaces 4 anomaly classes per 100-day checkpoint cadence:
  A1: per-strategy fire-rate vs B660 measured baseline (>2x deviation)
  B2: trade_log schema-invariant violations
  D1: cube-cell completion progress + ETA
  F1: periodic owner chatback (structured summary line)

# Source: Council 108 4/4 RECOMMEND Option-5 Modified per owner
# directive 2026-06-26 "Approve all 7" -> A1 fire-rate + B2 schema
# + D1 progress + F1 chatback runtime monitoring.

USAGE
-----
    # In Phase 1 cube run, point this monitor at the running engine:
    python scripts/b1019_phase_1_runtime_monitor.py \\
        --engine-state output_batch_phase1/engine_state.json \\
        --trade-log output_batch_phase1/trade_log.parquet \\
        --baseline output_audit/b660_fire_count_measured.json \\
        --checkpoint-cadence 100

DESIGN
------
This script is consumed by the Bash Monitor tool. It polls engine
state at checkpoint cadence, prints one line per checkpoint with
structured fields. Each line is a notification event. STOP-S3 tier
emits prefixed with HALT-CRITICAL / WARN-HIGH / LOG-MEDIUM.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--engine-state", required=True,
                        help="Engine state JSON path (incremental checkpoint output)")
    parser.add_argument("--trade-log", required=True,
                        help="Trade log parquet path")
    parser.add_argument("--baseline",
                        default="output_audit/fire_count_measured_b660_full_universe.json",
                        help="B660 per-strategy fire-rate baseline JSON "
                             "(B1043 F-03: corrected default path)")
    parser.add_argument("--checkpoint-cadence", type=int, default=100,
                        help="Days between checkpoints (default 100)")
    parser.add_argument("--total-days", type=int, default=1610,
                        help="Total simulated days (default ~6.41yr * 251)")
    parser.add_argument("--total-cells", type=int, default=5642,
                        help="Total cube cells (default 217 strategies * 26 exits)")
    parser.add_argument("--poll-seconds", type=int, default=30,
                        help="Poll interval seconds (default 30)")
    # B1059 PIVOT #36 fix: scale A1 baseline by active-vs-baseline ticker ratio
    parser.add_argument("--total-tickers-active", type=int, default=503,
                        help="Active tickers in current run (Phase 1=1, "
                             "Phase 2=10, Phase 3=50, Phase 4=503). Used to "
                             "scale A1 fire-rate baseline. Default 503 = full "
                             "T1a (no scaling).")
    parser.add_argument("--baseline-universe-size", type=int, default=503,
                        help="Universe size of B660 baseline measurement "
                             "(default 503 = T1a). Used as denominator in "
                             "A1 scaling: expected_fpy_scaled = expected_fpy "
                             "* (total_tickers_active / baseline_universe_size).")
    args = parser.parse_args()

    baseline = _load_baseline(REPO / args.baseline)
    # B1059 PIVOT #36 fix: scale A1 baseline by ticker ratio.
    # Phase D B1058 HALTed at Phase 1 sim_day 100 (2 min runtime) because
    # A1 fire-rate compared single-ticker NVDA Phase 1 fires to B660 full-
    # universe (503-ticker) baseline. 88 strategies flagged as anomalous
    # (ratio < 0.5) -> HALT-CRITICAL fire. Engine was healthy (~0.6 sec/day).
    # Fix: scale expected_fpy by ratio (active / baseline_universe). For
    # Phase 1 NVDA: ratio = 1/503 = 0.002 -> baseline scales to ~0.2pct of
    # full-universe rate, matching what NVDA-only would emit.
    # Per Council 158 Option-1.
    if args.total_tickers_active != args.baseline_universe_size and baseline:
        scale = float(args.total_tickers_active) / float(args.baseline_universe_size)
        baseline = {k: v * scale for k, v in baseline.items()}
        print(f"B1059 PIVOT #36: A1 baseline scaled by {scale:.6f} "
              f"({args.total_tickers_active}/{args.baseline_universe_size}); "
              f"effective per-strategy fpy reduced by this factor")
    last_checkpoint_day = -1
    start_ts = time.time()

    print(f"B1019 MONITOR ARMED: engine_state={args.engine_state} "
          f"trade_log={args.trade_log} cadence={args.checkpoint_cadence}d "
          f"total_days={args.total_days} total_cells={args.total_cells}")

    while True:
        state = _read_engine_state(REPO / args.engine_state)
        if state is None:
            time.sleep(args.poll_seconds)
            continue
        current_day = int(state.get("simulated_day", 0))
        if current_day < last_checkpoint_day + args.checkpoint_cadence:
            if state.get("status") == "complete":
                print(f"COMPLETE day={current_day} cells={state.get('cells_completed', 0)} "
                      f"runtime_min={(time.time() - start_ts) / 60:.1f}")
                return 0
            time.sleep(args.poll_seconds)
            continue
        last_checkpoint_day = current_day

        a1 = _check_a1_fire_rate(REPO / args.trade_log, baseline, current_day)
        b2 = _check_b2_schema(REPO / args.trade_log)
        d1 = _check_d1_progress(state, args.total_cells, args.total_days,
                                current_day, start_ts)

        tier = _classify_tier(a1, b2, d1)
        print(_format_checkpoint_line(tier, current_day, a1, b2, d1))

        if tier == "HALT-CRITICAL":
            print(f"HALT-CRITICAL: stopping monitor at day={current_day}")
            return 1

        if state.get("status") == "complete":
            print(f"COMPLETE day={current_day} runtime_min={(time.time() - start_ts) / 60:.1f}")
            return 0


def _load_baseline(path: Path) -> dict[str, float]:
    """B1043 Council 138 F-03 fix: dispatch by actual baseline schema.

    Original code assumed `per_strategy` top-level dict {strategy: {fires_per_year: N}}.
    Actual B660 file (fire_count_measured_b660_full_universe.json) uses
    `results` top-level list [{strategy, n_fires_long, n_fires_short, ...,
    calendar_year_span}]. Compute fires_per_year per strategy: total fires
    (long+short+avoid) / calendar_year_span.

    Falls back to per_strategy legacy schema if results key absent (forward-
    compat). Both schemas produce {strategy_name: fires_per_year_float}.

    Source: B1043 Sub-A adversarial review F-03 BLOCK finding.
    """
    if not path.exists():
        print(f"WARN: baseline not found at {path}; A1 fire-rate checks degraded")
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        # B660 schema: top-level `results` list
        if "results" in data and isinstance(data["results"], list):
            out: dict[str, float] = {}
            for row in data["results"]:
                if not isinstance(row, dict):
                    continue
                strat = row.get("strategy")
                if not strat:
                    continue
                total_fires = (
                    int(row.get("n_fires_long", 0)) +
                    int(row.get("n_fires_short", 0)) +
                    int(row.get("n_fires_avoid", 0))
                )
                yspan = float(row.get("calendar_year_span", 1.0)) or 1.0
                out[strat] = total_fires / yspan
            return out
        # Legacy per_strategy fallback
        return {k: float(v.get("fires_per_year", 0))
                for k, v in data.get("per_strategy", {}).items()}
    except Exception as exc:
        print(f"WARN: baseline load error {type(exc).__name__}: {exc}")
        return {}


def _read_engine_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _check_a1_fire_rate(trade_log_path: Path, baseline: dict[str, float],
                        current_day: int) -> dict[str, Any]:
    """A1: per-strategy fire-rate vs B660 baseline."""
    result = {"check": "a1_fire_rate", "anomaly_count": 0, "anomalies": []}
    if not baseline:
        result["status"] = "DEGRADED-no-baseline"
        return result
    try:
        import pandas as pd
        if not trade_log_path.exists():
            result["status"] = "PENDING-no-trade-log"
            return result
        # B1043 Council 138 F-04 fix: dispatch reader by file extension.
        # Engine emits trade_log_checkpoint.csv (not parquet). Previous
        # hardcoded pd.read_parquet() threw ArrowInvalid every poll +
        # _classify_tier upgraded to false HALT-CRITICAL.
        # Source: B1043 Sub-A adversarial review F-04 BLOCK finding.
        suffix = str(trade_log_path).lower()
        if suffix.endswith(".csv"):
            df = pd.read_csv(trade_log_path)
        elif suffix.endswith(".parquet"):
            df = pd.read_parquet(trade_log_path)
        else:
            # Try parquet first, fall back to csv (defensive default)
            try:
                df = pd.read_parquet(trade_log_path)
            except Exception:
                df = pd.read_csv(trade_log_path)
        if "strategy" not in df.columns:
            result["status"] = "ERROR-schema-missing-strategy-column"
            return result
        years_elapsed = max(current_day / 251.0, 0.01)
        fires_so_far = df.groupby("strategy").size().to_dict()
        for strat, expected_fpy in baseline.items():
            actual = fires_so_far.get(strat, 0)
            actual_fpy = actual / years_elapsed
            if expected_fpy > 1.0:
                ratio = actual_fpy / expected_fpy
                if ratio > 2.0 or ratio < 0.5:
                    result["anomaly_count"] += 1
                    result["anomalies"].append({
                        "strategy": strat,
                        "expected_fpy": expected_fpy,
                        "actual_fpy": actual_fpy,
                        "ratio": ratio,
                    })
        result["status"] = "OK" if result["anomaly_count"] == 0 else "ANOMALY"
    except Exception as exc:
        result["status"] = f"ERROR-{type(exc).__name__}-{exc}"
    return result


def _check_b2_schema(trade_log_path: Path) -> dict[str, Any]:
    """B2: trade_log schema-invariant sentinel."""
    result = {"check": "b2_schema_invariants", "violations": []}
    try:
        import pandas as pd
        if not trade_log_path.exists():
            result["status"] = "PENDING-no-trade-log"
            return result
        # B1043 Council 138 F-04 fix: dispatch reader by extension (csv or parquet)
        suffix = str(trade_log_path).lower()
        if suffix.endswith(".csv"):
            df = pd.read_csv(trade_log_path)
        elif suffix.endswith(".parquet"):
            df = pd.read_parquet(trade_log_path)
        else:
            try:
                df = pd.read_parquet(trade_log_path)
            except Exception:
                df = pd.read_csv(trade_log_path)
        required = ["strategy", "ticker", "entry_date", "exit_date", "exit_method"]
        for col in required:
            if col not in df.columns:
                result["violations"].append(f"missing_column_{col}")
        if len(df) > 0 and "entry_date" in df.columns and "exit_date" in df.columns:
            ed = pd.to_datetime(df["entry_date"], errors="coerce")
            xd = pd.to_datetime(df["exit_date"], errors="coerce")
            invalid = (xd < ed).sum()
            if invalid > 0:
                result["violations"].append(f"exit_before_entry_count_{invalid}")
        if "trade_id" in df.columns:
            dup = df["trade_id"].duplicated().sum()
            if dup > 0:
                result["violations"].append(f"duplicate_trade_id_count_{dup}")
        result["status"] = "OK" if not result["violations"] else "VIOLATION"
    except Exception as exc:
        result["status"] = f"ERROR-{type(exc).__name__}-{exc}"
    return result


def _check_d1_progress(state: dict[str, Any], total_cells: int,
                       total_days: int, current_day: int,
                       start_ts: float) -> dict[str, Any]:
    """D1: cube-cell completion progress + ETA."""
    cells_done = int(state.get("cells_completed", 0))
    pct_cells = cells_done / max(total_cells, 1)
    pct_days = current_day / max(total_days, 1)
    runtime_sec = time.time() - start_ts
    if pct_cells > 0.01:
        eta_sec = runtime_sec * (1.0 - pct_cells) / pct_cells
    else:
        eta_sec = 0
    return {
        "check": "d1_progress",
        "current_day": current_day,
        "cells_completed": cells_done,
        "total_cells": total_cells,
        "pct_cells": round(pct_cells, 4),
        "pct_days": round(pct_days, 4),
        "runtime_min": round(runtime_sec / 60, 2),
        "eta_min": round(eta_sec / 60, 2),
        "status": "OK",
    }


def _classify_tier(a1: dict[str, Any], b2: dict[str, Any],
                   d1: dict[str, Any]) -> str:
    """STOP-S3 severity tier classification."""
    if str(b2.get("status", "")).startswith("ERROR"):
        return "HALT-CRITICAL"
    if b2.get("violations"):
        return "HALT-CRITICAL"
    if a1.get("anomaly_count", 0) >= 5:
        return "WARN-HIGH"
    if a1.get("anomaly_count", 0) > 0:
        return "LOG-MEDIUM"
    return "OK"


def _format_checkpoint_line(tier: str, day: int, a1: dict[str, Any],
                            b2: dict[str, Any], d1: dict[str, Any]) -> str:
    """F1: structured periodic owner-chatback line."""
    return (
        f"{tier} day={day} cells={d1['cells_completed']}/{d1['total_cells']} "
        f"pct={d1['pct_cells']:.1%} eta_min={d1['eta_min']:.1f} "
        f"a1_anom={a1.get('anomaly_count', 0)} "
        f"b2_viol={len(b2.get('violations', []))} "
        f"runtime_min={d1['runtime_min']:.1f}"
    )


if __name__ == "__main__":
    sys.exit(main())
