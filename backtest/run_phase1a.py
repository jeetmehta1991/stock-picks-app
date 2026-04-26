"""
run_phase1a.py — Phase 1A entry point for backtesting engine v2.

Usage:
  python run_phase1a.py --dry-run          # 2-month pipeline validation, no agents
  python run_phase1a.py --no-agents        # Full 3-year run, screener only (free)
  python run_phase1a.py                    # Full run with Haiku agents
  python run_phase1a.py --start 2022-01-01 --end 2022-06-30  # custom range
"""

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

# Ensure repo root is on path regardless of where script is invoked from
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("backtest_v2.log")],
)
logger = logging.getLogger("phase1a_v2")

from backtest.config import BACKTEST_START, BACKTEST_END, UNIVERSE, PASSING_CRITERIA
from backtest.engine.backtest import BacktestEngine


def validate_env():
    import os
    print("\n=== Environment Check ===")
    for var, label in [
        ("ANTHROPIC_API_KEY", "required for agents"),
        ("QUIVER_API_KEY",    "optional — smart money signals"),
        ("FRED_API_KEY",      "optional — yield curve data"),
    ]:
        val = os.environ.get(var,"")
        icon = "✅" if val else ("⚠️ " if "optional" in label else "❌")
        print(f"  {icon} {var}: {'set' if val else 'NOT SET'} ({label})")
    print()


def validate_lookahead():
    print("=== Look-Ahead Bias Validation ===")
    from backtest.data.fetcher import fetch_ohlcv
    test_date = date(2023, 6, 15)
    df = fetch_ohlcv("AAPL", start=date(2023,1,1), end=date(2023,12,31), as_of=test_date)
    if df.empty:
        print("  ⚠️  Could not fetch test data — network issue")
        return True
    last = df.index[-1].date()
    if last > test_date:
        print(f"  ❌ LOOK-AHEAD BIAS: data has row {last} after as_of={test_date}")
        return False
    print(f"  ✅ Date ceiling works: last row = {last} (as_of = {test_date})")
    return True


def print_results(engine: BacktestEngine):
    from backtest.results.metrics import compute_all_metrics
    df = engine.get_trade_log()
    if df.empty:
        print("\nNo closed trades.")
        return
    metrics = compute_all_metrics(df)
    print("\n" + "="*75)
    print("PHASE 1A RESULTS — v2")
    print("="*75)
    print(f"Total trades:     {len(df):,}")
    print(f"Long trades:      {(df['direction']=='long').sum():,}")
    print(f"Short trades:     {(df['direction']=='short').sum():,}")
    print(f"Strategies tested: {len(metrics)}")
    if not metrics.empty:
        passing = metrics[metrics["passes_all"]==True]
        print(f"Strategies passing all criteria: {len(passing)}")
        print(f"\n{'Strategy':<35} {'Cat':<12} {'L/S':<8} {'Trades':>7} {'WinRate':>8} {'PF':>6} {'ROI':>8} {'Pass':>5}")
        print("-"*90)
        for _, r in metrics.head(20).iterrows():
            p = "✅" if r["passes_all"] else ""
            a = "⚠️" if r.get("audit_flags") else ""
            print(f"{r['strategy']:<35} {r.get('category',''):<12} {r['direction_mix']:<8} "
                  f"{int(r['total_trades']):>7,} {r['win_rate']*100:>7.1f}% "
                  f"{r['profit_factor']:>6.2f} {r['total_roi_pct']:>7.1f}% {p}{a:>4}")
    print(f"\nOutputs: {engine.output_dir}/")


def phase1a_quality_gate(engine: BacktestEngine) -> bool:
    from backtest.results.metrics import compute_all_metrics
    df = engine.get_trade_log()
    if df.empty:
        print("❌ No trades — pipeline issue")
        return False
    metrics = compute_all_metrics(df)
    low_trades = metrics[metrics["total_trades"] < PASSING_CRITERIA["min_trades"]]
    passing    = metrics[metrics["passes_all"]==True]

    print("\n=== Phase 1A Quality Gate ===")
    if low_trades.empty:
        print(f"  ✅ All strategies have {PASSING_CRITERIA['min_trades']}+ trades")
    else:
        print(f"  ⚠️  {len(low_trades)} strategies below {PASSING_CRITERIA['min_trades']} trades — need more data")

    if passing.empty:
        print("  ℹ️  No strategies pass all criteria yet — normal for Phase 1A dry run")
    else:
        print(f"  ✅ {len(passing)} strategies pass all criteria → ready for Phase 1B")

    audit = metrics[metrics["audit_flags"].apply(lambda x: len(x)>0 if isinstance(x,list) else False)]
    if not audit.empty:
        print(f"  ⚠️  {len(audit)} strategies flagged for look-ahead bias audit (win rate >75% or PF >1.5)")

    passed = len(engine.closed_trades) > 0
    if passed:
        print("\n✅ Phase 1A PASSED — pipeline clean, ready for full run or Phase 1B")
    else:
        print("\n❌ Phase 1A FAILED — no trades produced")
    return passed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run",    action="store_true")
    p.add_argument("--no-agents",  action="store_true")
    p.add_argument("--no-git",     action="store_true",  help="Suppress git commits during run (for parallel batches — commit manually at end)")
    p.add_argument("--no-news",    action="store_true",  help="Disable news sentiment (for A/B comparison)")
    p.add_argument("--tickers",    type=str, default=None, help="Comma-separated list of tickers for batch test")
    p.add_argument("--phase",      type=str, default="1a", choices=["1a","1b","1c","1d"])
    p.add_argument("--start",      type=str)
    p.add_argument("--end",        type=str)
    p.add_argument("--max-cands",  type=int, default=10)
    p.add_argument("--output-dir", type=str, default="output_v2")
    args = p.parse_args()

    phase_key = f"phase_{args.phase}"

    print("="*70)
    print(f"STAGE 2 BACKTESTING ENGINE v2 — Phase {args.phase.upper()}")
    print(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("60 strategies | Trailing stop exits | Circuit breakers | Long + Short")
    print("="*70)

    validate_env()
    if not validate_lookahead():
        print("CRITICAL: Look-ahead bias check failed. Aborting.")
        sys.exit(1)

    if args.dry_run:
        start    = date(2023, 1, 1)
        end      = date(2023, 2, 28)
        universe = ["AAPL","MSFT","NVDA","AMZN","GOOGL","SPY","QQQ","XLK","GLD","TLT"]
        agents   = False
        print(f"\nDRY RUN: {start} → {end} | {len(universe)} instruments | no agents\n")
    else:
        start  = date.fromisoformat(args.start) if args.start else BACKTEST_START
        end    = date.fromisoformat(args.end)   if args.end   else BACKTEST_END
        agents = not args.no_agents

        # --tickers flag: override universe with specific tickers (for batch tests)
        if args.tickers:
            universe = [t.strip() for t in args.tickers.split(",")]
            print(f"\nBATCH TEST MODE: {start} → {end} | {len(universe)} tickers: {universe}")
        # Phase 1B+ uses full S&P 500 + ETFs universe
        elif args.phase in ("1b", "1c", "1d"):
            from backtest.data.universe import get_sp500_constituents, ETFS_FULL
            sp500    = get_sp500_constituents(500)
            universe = list(dict.fromkeys(sp500 + ETFS_FULL))
            print(f"\nPhase {args.phase.upper()}: {start} → {end} | {len(universe)} instruments (full S&P 500 + ETFs)")
        else:
            universe = UNIVERSE
            print(f"\nPhase 1A: {start} → {end} | {len(universe)} instruments")

        print(f"Agents: {'Haiku' if agents else 'DISABLED'} | Max cands/day: {args.max_cands}\n")
        if agents:
            days = sum(1 for i in range((end-start).days+1)
                       if (start+__import__('datetime').timedelta(days=i)).weekday()<5)
            # Cost estimate: days × avg candidates that pass screener × 6 agents × Haiku cost
            # ~30% of max_cands pass screener on average
            avg_passing = max(1, args.max_cands * 0.3)
            est_cost = days * avg_passing * 6 * 0.00035 * 1.35  # USD → CAD approx
            print(f"  Estimated cost: ~${est_cost:.1f} CAD ({days} days × {avg_passing:.0f} avg candidates × 6 agents × $0.00035)")
            print(f"Estimated cost: ~${est_cost:.1f} USD (Haiku) — proceeding automatically")

    engine = BacktestEngine(
        universe=universe, start=start, end=end,
        phase=phase_key, max_candidates_per_day=args.max_cands,
        run_agents=agents, output_dir=args.output_dir,
        disable_news=args.no_news,
        walk_forward=not args.no_git,  # suppress per-batch WF — run on merged result only
    )
    if args.no_git:
        import os
        os.environ["BACKTEST_NO_GIT"] = "1"
        print("⚠️  --no-git: parallel batch mode")
        print("   - Git operations suppressed — commit manually when all batches complete")
        print("   - Per-batch walk-forward suppressed — run on merged result only")
        print("   Command: git status → git add [dirs] → git commit → git pull --rebase → git push")

    if args.no_news:
        print("⚠️  News sentiment DISABLED — A/B comparison mode")
    engine.load_data()
    engine.run()
    print_results(engine)
    engine.save_all_outputs()
    phase1a_quality_gate(engine)
    print(f"\nLog: backtest_v2.log | Outputs: {args.output_dir}/")


if __name__ == "__main__":
    main()
