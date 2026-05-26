"""Batch 371 Bucket D3: cProfile harness for _process_day hot-path identification.

Source (per CHECKLIST #77): owner directive 2026-05-26 bucket D Speedup
Lever C: profile-first per Batch 315a finding (existing compute_all_signals
runs once per ticker-day; the original "N-times-per-ticker" plan premise
does not match current screener flow). Real Lever-C win likely comes from
CROSS-ticker vectorization (compute panel-level signals for all 1937 tkrs
in one pandas op vs 1937 separate calls).

Methodology
-----------
1. Load 20 mega-cap T1a tickers from existing Polygon OHLCV cache.
2. Run a 30-trading-day backtest slice through BacktestEngine._process_day
   under cProfile.
3. Emit stats sorted by cumulative + tottime; top 30 hot-path entries.
4. Cross-reference findings against the planned Lever-C refactor target
   (cross-ticker vectorization vs single-ticker compute).

Why 20 x 30: keeps profile under 5min while exercising the full
screener + cross-sectional + exit_manager + portfolio_gate path.
"""
from __future__ import annotations

import cProfile
import io
import pstats
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _build_engine_args():
    """Construct argparse Namespace equivalent for run_phase1a CLI."""
    import argparse
    ns = argparse.Namespace(
        dry_run=False,
        no_agents=True,
        no_git=True,
        no_walk_forward=True,
        no_news=False,
        tickers="AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,JPM,UNH,XOM,JNJ,WMT,PG,V,MA,HD,BAC,KO,PFE,AVGO",
        phase="1a",
        start="2024-01-02",
        end="2024-02-15",  # ~30 trading days
        max_cands=30,
        screen_pool_workers=0,  # sequential for profiling clarity
        output_dir="output_profile_lever_c",
    )
    return ns


def main():
    args = _build_engine_args()
    out_dir = REPO / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    prof_path = out_dir / "process_day.prof"
    stats_path = out_dir / "process_day_stats.txt"

    print(f"[profile] target tickers: {len(args.tickers.split(','))}")
    print(f"[profile] window: {args.start} -> {args.end}")
    print(f"[profile] output: {prof_path}")

    # Import inside profiling so module-init work shows up; entry point mirrors
    # run_phase1a.main() but invoked programmatically.
    from backtest import run_phase1a

    profiler = cProfile.Profile()
    profiler.enable()
    try:
        # Monkey-patch parse_args to inject our namespace
        import argparse as _ap
        original_parse_args = _ap.ArgumentParser.parse_args
        _ap.ArgumentParser.parse_args = lambda self, *a, **kw: args  # noqa
        try:
            run_phase1a.main()
        finally:
            _ap.ArgumentParser.parse_args = original_parse_args
    finally:
        profiler.disable()
        profiler.dump_stats(str(prof_path))

    # Stats: cumulative time + tottime
    buf = io.StringIO()
    ps = pstats.Stats(profiler, stream=buf).strip_dirs().sort_stats("cumulative")
    ps.print_stats(40)
    print("\n=== TOP 40 BY CUMULATIVE TIME ===", file=buf)
    buf.seek(0)
    cumulative_text = buf.read()

    buf = io.StringIO()
    ps2 = pstats.Stats(profiler, stream=buf).strip_dirs().sort_stats("tottime")
    ps2.print_stats(40)
    tottime_text = buf.read()

    stats_path.write_text(
        "=== Bucket D3 (Lever C) cProfile - process_day hot path ===\n\n"
        "Profile scenario: 20 mega-cap T1a tickers x 30 trading days "
        "(2024-01-02 -> 2024-02-15) sequential (workers=0).\n"
        "Sub-systems exercised: screen_universe + compute_all_signals + "
        "cross_sectional + exit_manager + portfolio_gate + writer.\n\n"
        "=== SORTED BY CUMULATIVE ===\n" + cumulative_text + "\n\n"
        "=== SORTED BY TOTTIME ===\n" + tottime_text,
        encoding="utf-8",
    )
    print(f"[OK] stats written to {stats_path}")
    print(f"[OK] raw profile at {prof_path}")
    print()
    # Print top 20 cumulative to stdout for inline reading
    print("=== TOP 20 CUMULATIVE (snippet) ===")
    ps3 = pstats.Stats(profiler).strip_dirs().sort_stats("cumulative")
    ps3.print_stats(20)


if __name__ == "__main__":
    main()
