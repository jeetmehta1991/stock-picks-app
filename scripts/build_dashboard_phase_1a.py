"""
scripts/build_dashboard_phase_1a.py — Phase 1A Trade Summary Dashboard data emitter.

Source of truth (per CHECKLIST #77): output_v2/* artifacts produced by
backtest/run_phase1a.py (writer.py). This script collects them into a
single data.js consumed by dashboard_phase_1a/index.html.

Per DETAILED_PROJECT_PLAN.md §7.6 Sprint 6.5 spec: 9 tabs port of legacy
analysis_dashboard_1a.html.

Run:
  python scripts/build_dashboard_phase_1a.py
Output:
  dashboard_phase_1a/data.js     (const STAGE2_DATA = ...; for browser <script>)
  dashboard_phase_1a/data.json   (same payload, plain JSON)
  dashboard_phase_1a/last_run.txt
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
# Batch 180: support --source flag for swapping between output_v2 (dev-mode
# canonical AAPL 130-day backtest) and richer runs (smoke v4, dress rehearsal).
# Default remains output_v2 for compatibility with the canonical regen flow.
import argparse
_parser = argparse.ArgumentParser()
_parser.add_argument("--source", default="output_v2",
                     help="Source output directory (e.g. output_smoke_v4_cross_regime)")
_args, _ = _parser.parse_known_args()
OUT_DIR = REPO / _args.source
DASH = REPO / "dashboard_phase_1a"
DASH.mkdir(parents=True, exist_ok=True)


def load_csv(name: str, head: int | None = None) -> list[dict]:
    p = OUT_DIR / name
    if not p.exists():
        return []
    try:
        df = pd.read_csv(p)
    except Exception:
        return []
    if head is not None:
        df = df.head(head)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def load_json(name: str) -> dict | list:
    p = OUT_DIR / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_parquet(name: str, head: int | None = None) -> list[dict]:
    p = OUT_DIR / name
    if not p.exists():
        return []
    try:
        df = pd.read_parquet(p)
    except Exception:
        return []
    if head is not None:
        df = df.head(head)
    # Date typing -> ISO string for JS
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
        elif df[col].dtype == "object":
            df[col] = df[col].astype(str).where(df[col].notna(), None)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def build() -> dict:
    # ---- Tab 1: per-strategy ranking ----
    backtest_results = load_csv("backtest_results.csv")
    winning = load_json("winning_strategies.json") or {}

    # ---- Tab 2: regime heatmap (per-strategy x regime verdicts) ----
    regime_matrix = load_json("strategy_regime_matrix.json") or {}
    regime_summary = load_json("regime_stratified_summary.json") or {}

    # ---- Tab 3: MAE / MFE distribution ----
    mae_bucket = load_csv("exit_by_mae_bucket.csv")
    mfe_bucket = load_csv("exit_by_mfe_bucket.csv")

    # ---- Tab 4: equity curve ----
    equity = load_parquet("equity_curve.parquet")
    portfolio_summary = load_json("portfolio_summary.json") or {}
    portfolio_metrics = load_json("portfolio_metrics.json") or {}

    # ---- Tab 5: walk-forward + improvements ----
    improvements = load_json("improvements_summary.json") or {}
    rolling_sharpe = load_json("rolling_sharpe_stability.json") or {}
    bootstrap_ci = load_csv("bootstrap_ci.csv")
    stress = load_json("stress_metrics.json") or {}

    # ---- Tab 6: smart money lift ----
    smart_money = load_csv("exit_by_smart_money_signal_present.csv")
    congressional = load_csv("congressional_correlation.csv")

    # ---- Tab 7: sector breakdown ----
    by_sector = load_csv("exit_by_sector.csv")
    sector_conc = load_csv("sector_concentration.csv")

    # ---- Tab 8: skipped trades ----
    skipped = load_csv("skipped_trades.csv", head=5000)

    # ---- Tab 9: circuit breaker log ----
    cb_log = load_csv("circuit_breaker_log.csv")
    cb_by_active = load_csv("exit_by_circuit_breaker_active_during_hold.csv")

    # ---- Trade-level + exit breakdowns (cross-tab) ----
    # Batch 180: fall back to CSV if parquet missing (smoke runs emit CSV-only)
    trade_log = load_parquet("trade_log.parquet", head=10000) or load_csv("trade_log.csv", head=10000)
    exit_methods = load_csv("exit_method_multi_dim_cube.csv")
    exit_best = load_csv("exit_strategy_best.csv")
    exit_comparison = load_csv("exit_strategy_comparison.csv")

    # ---- Per-dimension exit breakdowns (extra optional tabs) ----
    other_breakdowns: dict[str, list] = {}
    for csv in OUT_DIR.glob("exit_by_*.csv"):
        # Skip the ones already used in dedicated tabs
        if csv.name in (
            "exit_by_mae_bucket.csv", "exit_by_mfe_bucket.csv",
            "exit_by_smart_money_signal_present.csv", "exit_by_sector.csv",
            "exit_by_circuit_breaker_active_during_hold.csv",
        ):
            continue
        other_breakdowns[csv.stem.replace("exit_by_", "")] = load_csv(csv.name)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": str(OUT_DIR.relative_to(REPO)),
        # Tab 1
        "backtest_results": backtest_results,
        "winning_strategies": winning,
        # Tab 2
        "strategy_regime_matrix": regime_matrix,
        "regime_stratified_summary": regime_summary,
        # Tab 3
        "mae_bucket": mae_bucket,
        "mfe_bucket": mfe_bucket,
        # Tab 4
        "equity_curve": equity,
        "portfolio_summary": portfolio_summary,
        "portfolio_metrics": portfolio_metrics,
        # Tab 5
        "improvements_summary": improvements,
        "rolling_sharpe_stability": rolling_sharpe,
        "bootstrap_ci": bootstrap_ci,
        "stress_metrics": stress,
        # Tab 6
        "smart_money_exit": smart_money,
        "congressional_correlation": congressional,
        # Tab 7
        "by_sector": by_sector,
        "sector_concentration": sector_conc,
        # Tab 8
        "skipped_trades": skipped,
        # Tab 9
        "circuit_breaker_log": cb_log,
        "cb_by_active": cb_by_active,
        # Cross-tab
        "trade_log_preview": trade_log,
        "exit_methods": exit_methods,
        "exit_best": exit_best,
        "exit_comparison": exit_comparison,
        "exit_breakdowns": other_breakdowns,
    }


def main() -> int:
    print(f"Phase 1A dashboard build -> {DASH}")
    if not OUT_DIR.exists():
        print(f"ERROR: {OUT_DIR} not found; run backtest first")
        return 1
    payload = build()

    # Plain JSON (audit / consumers)
    (DASH / "data.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    # Browser-loadable JS module
    js = "const PHASE_1A_DATA = " + json.dumps(payload, default=str) + ";"
    (DASH / "data.js").write_text(js, encoding="utf-8")
    (DASH / "last_run.txt").write_text(payload["generated_at"] + "\n", encoding="utf-8")

    # Summary
    print(f"  generated_at: {payload['generated_at']}")
    print(f"  backtest_results rows:  {len(payload['backtest_results'])}")
    print(f"  trade_log preview rows: {len(payload['trade_log_preview'])}")
    print(f"  equity_curve points:    {len(payload['equity_curve'])}")
    print(f"  skipped_trades rows:    {len(payload['skipped_trades'])}")
    print(f"  exit_breakdowns kinds:  {len(payload['exit_breakdowns'])}")
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
