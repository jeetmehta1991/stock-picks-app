"""H3 dress rehearsal — 25-ticker x 1-year Phase 1A smoke before May 15.

Runs the full Day-9 wiring (Level 6 CB, regime_flip, 4-fold WF, 25-col context,
verdict cube) at moderate scale to catch issues smoke v3 (5 tkr) couldn't see.

Outputs to output_dress_rehearsal/. No API spend (cache only).
Pass 53 Day 9 v8 H3.
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import date
from pathlib import Path

# Diverse 25-ticker universe spanning sectors; avoids tickers known to be missing
TICKERS = [
    # Tech
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META",
    # Financials
    "JPM", "BAC", "WFC", "GS",
    # Energy
    "XOM", "CVX",
    # Healthcare
    "JNJ", "UNH", "PFE",
    # Consumer
    "WMT", "HD", "KO", "PEP",
    # Industrials
    "BA", "CAT",
    # Utilities
    "NEE", "SO",
    # Auto / discretionary
    "TSLA",
    # Broad market
    "SPY",
]

START = date(2023, 1, 1)
END = date(2023, 12, 31)


def main():
    print(f"=== H3 dress rehearsal starting at {time.strftime('%H:%M:%S')} ===")
    print(f"Tickers: {len(TICKERS)}  ({START} -> {END})")
    sys.stdout.flush()

    out_dir = Path("output_dress_rehearsal")
    out_dir.mkdir(exist_ok=True)

    # Quiet logs
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

    if len(eng.ohlcv_dict) < 10:
        print(f"ABORT: only {len(eng.ohlcv_dict)} tickers loaded — cache may be incomplete.")
        sys.exit(1)

    eng.run()
    eng.save_all_outputs()
    elapsed = time.perf_counter() - t0

    print()
    print("=" * 60)
    print("H3 DRESS REHEARSAL RESULT")
    print("=" * 60)
    print(f"  Wall time:     {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Closed trades: {len(eng.closed_trades)}")
    print(f"  Output dir:    {out_dir.resolve()}")

    # Inspect emitted artifacts
    artifacts = sorted(out_dir.glob("*.csv"))
    print(f"  CSV artifacts: {len(artifacts)}")
    must_have = ["trade_log.csv", "backtest_results.csv"]
    nice_have = ["verdict_cube.csv", "exit_method_multi_dim_cube.csv",
                 "exit_sweet_spots.csv", "exit_pairwise_dominance.csv"]
    print()
    print("Mandatory artifacts:")
    for f in must_have:
        sym = "[OK]" if (out_dir / f).exists() else "[MISSING]"
        print(f"  {sym}  {f}")
    print("Day-9 artifacts (best-effort emission):")
    for f in nice_have:
        sym = "[OK]" if (out_dir / f).exists() else "[NOT EMITTED]"
        print(f"  {sym}  {f}")

    # Verdict cube sanity
    vc = out_dir / "verdict_cube.csv"
    if vc.exists():
        import pandas as pd
        df = pd.read_csv(vc)
        if not df.empty:
            print()
            print(f"  verdict_cube rows: {len(df)}")
            if "verdict" in df.columns:
                print(f"  verdicts:          {df['verdict'].value_counts().to_dict()}")

    print()
    print(f"=== H3 done at {time.strftime('%H:%M:%S')} ===")


if __name__ == "__main__":
    main()
