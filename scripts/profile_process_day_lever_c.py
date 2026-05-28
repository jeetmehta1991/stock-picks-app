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


def _build_engine_args(scenario: str = "1a"):
    """Construct argparse Namespace equivalent for run_phase1a CLI.

    Batch 394 (2026-05-27): added `1a-beta` scenario for Option A audit.
    Larger universe + longer window + caps-off to identify whether the
    real bottleneck is screen / exit_manager / cube / checkpoint when
    Phase 1A-beta gates are bypassed.
    """
    import argparse
    if scenario == "1a-beta":
        # 1A-beta hot-path identification: 50 tkrs x 6mo, caps off, max
        # cands 200. Wall-time target ~10-15min on Windows. Exercises
        # the unconstrained candidate flow that the production cube run
        # will see.
        return argparse.Namespace(
            dry_run=False, no_agents=True, no_git=True, no_walk_forward=True,
            no_news=False,
            tickers=("AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,JPM,UNH,XOM,"
                     "JNJ,WMT,PG,V,MA,HD,BAC,KO,PFE,AVGO,"
                     "ABBV,CRM,ADBE,COST,CSCO,TMO,ABT,ACN,DHR,LLY,"
                     "MRK,NKE,ORCL,PEP,QCOM,T,TXN,UNP,UPS,VZ,"
                     "WFC,DIS,BMY,CAT,CMCSA,GE,IBM,INTC,MCD,NFLX"),
            phase="1a-beta",
            start="2024-01-02",
            end="2024-06-28",  # ~6 months
            max_cands=30,  # let 1a-beta auto-raise to 200 (Batch 386)
            screen_pool_workers=0,  # sequential to see TRUE hot-path
            output_dir="output_profile_lever_c_1a_beta",
            no_portfolio_cap=False,    # let 1a-beta auto-enable
            no_dd_halt=False,          # let 1a-beta auto-enable
            no_regime_affinity=False,  # let 1a-beta auto-enable
            no_event_suppression=False, # let 1a-beta auto-enable
            warn_run_hours=None,        # let 1a-beta auto-set
            max_run_hours=None,         # let 1a-beta auto-set
            vectorized_cube_exits=False, # Batch 412
        )
    # Default: original Batch 371 scenario (small + fast)
    return argparse.Namespace(
        dry_run=False, no_agents=True, no_git=True, no_walk_forward=True,
        no_news=False,
        tickers="AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,JPM,UNH,XOM,JNJ,WMT,PG,V,MA,HD,BAC,KO,PFE,AVGO",
        phase="1a",
        start="2024-01-02",
        end="2024-02-15",
        max_cands=30,
        screen_pool_workers=0,
        output_dir="output_profile_lever_c",
        no_portfolio_cap=False,
        no_dd_halt=False,
        no_regime_affinity=False,
        no_event_suppression=False,
        warn_run_hours=None,
        max_run_hours=None,
        vectorized_cube_exits=False,
    )


def main():
    scenario = "1a-beta" if "--1a-beta" in sys.argv else "1a"
    args = _build_engine_args(scenario)
    print(f"[profile] scenario: {scenario}")
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
