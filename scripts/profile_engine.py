"""cProfile harness for engine hot-path identification (Batch 307).

Source: per CHECKLIST #77 canonical-source attribution. Owner directive
2026-05-24: engine optimization to target <1h Phase 1A-beta runs.
This script profiles a representative backtest run to identify the
top hot functions, so optimization batches (308, 309) target the
right code.

Methodology:
  - Run a 10-tkr x 1y backtest (small enough to profile in <10 min,
    large enough that hot paths emerge above measurement noise)
  - cProfile dumps stats to scripts/profile_stats/engine.pstats
  - Pretty-print top-30 by cumtime + top-30 by tottime
  - Re-runs are deterministic given fixed seed + fixed ticker list

Usage:
  python scripts/profile_engine.py                    # default 10 tkr x 1y
  python scripts/profile_engine.py --large            # 30 tkr x 4y (slower)
"""
from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
from io import StringIO
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROFILE_DIR = REPO / "scripts" / "profile_stats"
PROFILE_DIR.mkdir(exist_ok=True)

# Mega-cap sample with full coverage; deterministic across runs.
SMALL_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                 "META", "TSLA", "JPM", "XOM", "JNJ"]
LARGE_TICKERS = SMALL_TICKERS + [
    "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC", "ADBE", "NFLX",
    "CRM", "PFE", "KO", "PEP", "INTC", "CSCO", "WMT", "TMO", "MRK", "ABT",
]


def run_backtest(tickers, start, end):
    """Single in-process call to the engine. cProfile wraps this."""
    from datetime import date
    sys.path.insert(0, str(REPO))
    from backtest.engine.backtest import BacktestEngine

    start_d = date.fromisoformat(start) if isinstance(start, str) else start
    end_d = date.fromisoformat(end) if isinstance(end, str) else end

    eng = BacktestEngine(
        universe=tickers,
        run_agents=False,
        apply_costs=True,
        apply_slippage_model=True,
        phase="phase_1a-beta",
        start=start_d,
        end=end_d,
        output_dir=str(REPO / "output_profile_tmp"),
        walk_forward=False,
        disable_news=False,
    )
    eng.run()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--large", action="store_true",
                   help="30 tkr x 4y instead of 10 tkr x 1y")
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)
    args = p.parse_args()

    if args.large:
        tickers = LARGE_TICKERS
        start = args.start or "2022-05-01"
        end = args.end or "2026-04-30"
        label = "large_30tkr_4y"
    else:
        tickers = SMALL_TICKERS
        start = args.start or "2023-01-01"
        end = args.end or "2023-12-31"
        label = "small_10tkr_1y"

    print(f"Profiling: {len(tickers)} tkrs, {start} -> {end}")
    print(f"Output: scripts/profile_stats/engine_{label}.pstats")

    out_path = PROFILE_DIR / f"engine_{label}.pstats"
    prof = cProfile.Profile()
    prof.enable()
    try:
        run_backtest(tickers, start, end)
    except Exception as exc:
        print(f"WARN: engine raised {type(exc).__name__}: {exc}")
        # Still want the profile data
    finally:
        prof.disable()
        prof.dump_stats(str(out_path))

    print(f"\nProfile saved. Analyzing top hot functions...\n")

    # Pretty-print top 30 by cumtime
    sio = StringIO()
    stats = pstats.Stats(str(out_path), stream=sio)
    stats.strip_dirs().sort_stats("cumulative").print_stats(30)
    print("=" * 80)
    print("TOP 30 BY CUMULATIVE TIME")
    print("=" * 80)
    print(sio.getvalue())

    sio2 = StringIO()
    stats2 = pstats.Stats(str(out_path), stream=sio2)
    stats2.strip_dirs().sort_stats("tottime").print_stats(30)
    print("=" * 80)
    print("TOP 30 BY TOTAL TIME (excluding sub-calls)")
    print("=" * 80)
    print(sio2.getvalue())

    print()
    print(f"Re-analyze with: python -m pstats {out_path}")
    print(f"  In pstats prompt: sort cumtime; stats 50")


if __name__ == "__main__":
    main()
