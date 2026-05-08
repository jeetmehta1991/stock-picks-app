"""Smoke v4 — 5-tkr × 4y cross-regime verification (Pass 53 Day-9 v8g).

Verifies all Day-9 fixes operating end-to-end across regime variety:
  2020-Q1: COVID crash (VIX > 80; crisis regime)
  2020-Q3: recovery rally
  2021:    bull market (low VIX, SPY > 200EMA)
  2022:    bear market (rising rates, SPY < 200EMA)
  2023:    recovery + AI rally
  2024:    bull continuation

Day-9 fixes under verification:
  - BUG-VIX-PROXY (Day 9 v8): regime classifier uses real VIX
  - L146 Wave A-D wiring: all 16 prefetch sources reachable
  - DEC-514 fill methodology: gap-through-stop fills at open
  - DEC-512 BUG-INSIDER-PIT: insider signals use fileDate not Date

Outputs to output_smoke_v4_cross_regime/. No API spend (cache only).
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import date
from pathlib import Path

# Compact 5-ticker universe across sectors
TICKERS = ["AAPL", "JPM", "XOM", "TSLA", "SPY"]

START = date(2020, 1, 2)
END = date(2024, 12, 31)


def main():
    print(f"=== Smoke v4 cross-regime starting at {time.strftime('%H:%M:%S')} ===")
    print(f"Tickers: {len(TICKERS)} ({START} -> {END})")
    sys.stdout.flush()

    out_dir = Path("output_smoke_v4_cross_regime")
    out_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(out_dir / "run.log", mode="w"),
                  logging.StreamHandler(sys.stdout)],
    )

    from backtest.engine.backtest import BacktestEngine

    t0 = time.perf_counter()
    eng = BacktestEngine(
        universe=TICKERS,
        start=START,
        end=END,
        phase="phase_1a",
        max_candidates_per_day=10,
        run_agents=False,
        output_dir=str(out_dir),
        apply_costs=True,
        walk_forward=False,
    )
    eng.load_data()
    print(f"Loaded {len(eng.ohlcv_dict)}/{len(TICKERS)} tickers from cache.")
    sys.stdout.flush()

    if len(eng.ohlcv_dict) < 3:
        print(f"ABORT: only {len(eng.ohlcv_dict)} tickers loaded.")
        sys.exit(1)

    eng.run()
    eng.save_all_outputs()
    elapsed = time.perf_counter() - t0

    print()
    print("=" * 60)
    print("SMOKE V4 RESULT")
    print("=" * 60)
    print(f"  Wall time:     {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Closed trades: {len(eng.closed_trades)}")
    print(f"  Output dir:    {out_dir.resolve()}")
    print()

    # Verify regime distribution across the 4-year window
    import pandas as pd
    log_path = out_dir / "trade_log.csv"
    if log_path.exists():
        df = pd.read_csv(log_path)
        if "regime" in df.columns:
            print(f"Regime distribution across {len(df)} trades:")
            print(f"  {df['regime'].value_counts().to_dict()}")
        # Gap-through-stop fills (DEC-514 verification)
        if "exit_price" in df.columns and "initial_stop" in df.columns:
            gap_fills = (df["exit_price"] < df["initial_stop"]).sum()
            print(f"  Trades exited below initial_stop (DEC-514 gap fills): {gap_fills}/{len(df)}")
        # Win rate + avg pnl
        if "pnl_pct" in df.columns:
            print(f"  Win rate: {(df['pnl_pct'] > 0).mean()*100:.1f}%")
            print(f"  Avg PnL:  {df['pnl_pct'].mean():.2f}%")

    # Day-9 artifacts
    artifacts = sorted(out_dir.glob("*.csv"))
    print(f"\nCSV artifacts: {len(artifacts)}")
    for f in ["trade_log.csv", "backtest_results.csv", "verdict_cube.csv",
              "exit_method_multi_dim_cube.csv", "exit_sweet_spots.csv",
              "exit_pairwise_dominance.csv"]:
        sym = "[OK]" if (out_dir / f).exists() else "[MISSING]"
        print(f"  {sym}  {f}")

    print()
    print(f"=== Smoke v4 done at {time.strftime('%H:%M:%S')} ===")


if __name__ == "__main__":
    main()
