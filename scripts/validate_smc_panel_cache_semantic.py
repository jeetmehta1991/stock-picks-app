"""Batch 560 OPT-C Phase 4 (A): SMC panel-cache semantic validation.

Source: per CHECKLIST #77, owner directive 2026-06-02 "C then A".
Queue: OPT-C Phase 4 (A) validation pass.

Runs the existing 20-ticker x 33-bar profile harness TWICE:
  1. USE_SMC_PANEL_CACHE = False (baseline, production semantics)
  2. USE_SMC_PANEL_CACHE = True  (cached path)

Compares the two trade_log.csv outputs and surfaces verdict-shift
counts so the owner can decide whether the empirical impact of the
cache is acceptable to flip the flag in production.

Outputs (under `output_smc_cache_compare/`):
  baseline/trade_log.csv  -- flag OFF run
  cached/trade_log.csv    -- flag ON run
  diff_summary.txt        -- per-strategy fire-count delta + per-ticker
                              shift summary
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

import backtest.config as cfg
from backtest.signals.smc_panel_cache import reset_cache


def _load_trade_log(out_dir: Path) -> pd.DataFrame:
    p = out_dir / "trade_log.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def _run_profile_pass(flag_value: bool, out_dir: Path) -> None:
    """Run the profile harness with cache flag = flag_value."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg.USE_SMC_PANEL_CACHE = flag_value
    reset_cache()  # ensure prime happens fresh per run

    # Adapt the existing harness: build a small backtest run + write
    # trade_log into out_dir.
    from datetime import date
    from backtest.engine.backtest import BacktestEngine

    # 20 mega-cap tickers as in profile_process_day_lever_c.py
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "BRK.B", "JPM", "V", "MA", "JNJ", "UNH", "XOM", "WMT",
        "PG", "HD", "BAC", "PFE", "KO",
    ]

    engine = BacktestEngine(
        universe=tickers,
        start=date(2024, 5, 1),
        end=date(2024, 6, 30),  # ~33 trading days
        phase="phase_1a",
        run_agents=False,
        output_dir=str(out_dir),
        no_portfolio_cap=True,
        no_regime_affinity=True,
    )
    t0 = time.perf_counter()
    engine.run()
    elapsed = time.perf_counter() - t0
    print(f"[{out_dir.name}] elapsed: {elapsed:.1f}s "
          f"(flag={cfg.USE_SMC_PANEL_CACHE})")


def _diff_trade_logs(baseline: pd.DataFrame, cached: pd.DataFrame) -> str:
    """Produce a text summary of the diff between the two trade_logs."""
    lines: list[str] = []
    lines.append(f"baseline rows: {len(baseline)}")
    lines.append(f"cached   rows: {len(cached)}")
    if baseline.empty and cached.empty:
        lines.append("BOTH trade_logs empty -- nothing to compare")
        return "\n".join(lines)
    # Per-strategy fire count delta
    if "strategy" in baseline.columns and "strategy" in cached.columns:
        b_strat = baseline["strategy"].value_counts()
        c_strat = cached["strategy"].value_counts()
        all_strat = sorted(set(b_strat.index) | set(c_strat.index))
        lines.append("\n=== Per-strategy fire count: baseline vs cached ===")
        lines.append(f"{'strategy':40s} {'base':>6s} {'cached':>7s} {'delta':>6s}")
        for s in all_strat:
            b = int(b_strat.get(s, 0))
            c = int(c_strat.get(s, 0))
            d = c - b
            if d == 0:
                continue
            lines.append(f"{s:40s} {b:6d} {c:7d} {d:+6d}")
    # Trade-level intersection on (ticker, entry_date, strategy)
    keys = ["ticker", "entry_date", "strategy"]
    common = [k for k in keys if k in baseline.columns and k in cached.columns]
    if common:
        b_keyset = set(map(tuple, baseline[common].astype(str).values))
        c_keyset = set(map(tuple, cached[common].astype(str).values))
        only_baseline = b_keyset - c_keyset
        only_cached = c_keyset - b_keyset
        common_keys = b_keyset & c_keyset
        lines.append(f"\n=== (ticker, entry_date, strategy) keyset ===")
        lines.append(f"  common:        {len(common_keys)}")
        lines.append(f"  only baseline: {len(only_baseline)}")
        lines.append(f"  only cached:   {len(only_cached)}")
    return "\n".join(lines)


def main() -> int:
    base_dir = REPO_ROOT / "output_smc_cache_compare"
    baseline_dir = base_dir / "baseline"
    cached_dir = base_dir / "cached"

    # Clean prior runs
    if baseline_dir.exists():
        shutil.rmtree(baseline_dir)
    if cached_dir.exists():
        shutil.rmtree(cached_dir)

    print("=== Run 1: USE_SMC_PANEL_CACHE = False (baseline) ===")
    _run_profile_pass(False, baseline_dir)
    print("\n=== Run 2: USE_SMC_PANEL_CACHE = True  (cached) ===")
    _run_profile_pass(True, cached_dir)

    print("\n=== Diff ===")
    baseline_log = _load_trade_log(baseline_dir)
    cached_log = _load_trade_log(cached_dir)
    diff_text = _diff_trade_logs(baseline_log, cached_log)
    print(diff_text)

    diff_path = base_dir / "diff_summary.txt"
    diff_path.write_text(diff_text, encoding="utf-8")
    print(f"\nDiff summary saved to {diff_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
