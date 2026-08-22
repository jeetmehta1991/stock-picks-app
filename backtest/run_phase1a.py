"""
run_phase1a.py - Phase 1A entry point for backtesting engine v2.

Usage:
  python run_phase1a.py --dry-run          # 2-month pipeline validation, no agents
  python run_phase1a.py --no-agents        # Full 3-year run, screener only (free)
  python run_phase1a.py                    # Full run with Haiku agents
  python run_phase1a.py --start 2022-01-01 --end 2022-06-30  # custom range
"""

import argparse
import json  # B1431: run-mode provenance emission
import logging
import os
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
from backtest.signals.screener import ALL_STRATEGIES
# B1084 Council 206: Phase 4 strategy-band chunk filter (8 chunks A-H).
# When PHASE_4_CHUNK env var set, narrows ALL_STRATEGIES to chunk subset
# via screener.get_strategy_chunk(idx). Leaves ALL_STRATEGIES unmodified
# at module level; engine uses what run_phase1a passes to it. Sum across
# 8 chunks = full 220 (sum-verified by B1084 pin test).
import backtest.signals.screener as _screener_mod
# B1425: explicit strategy-subset filter, generalising the B1084 chunk mechanism above.
# STRATEGY_SUBSET_FILE=<path> narrows ALL_STRATEGIES to the newline-separated names in that
# file. Motivation: a TARGETED re-run over only the strategies whose gates changed, so the
# pre-registered predictions can be tested without paying for the full 222-strategy cube.
# Deliberately a file rather than a comma list - the subsets in play are 20+ names and belong
# in a committed artifact, not a shell line. Unknown names are reported and skipped rather than
# silently dropped, because a typo that quietly shrinks the run is exactly the failure mode
# this repo keeps hitting.
_subset_path = os.environ.get("STRATEGY_SUBSET_FILE")
if _subset_path:
    _want = [ln.strip() for ln in Path(_subset_path).read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.startswith("#")]
    _known = {n: f for n, f in ALL_STRATEGIES.items() if n in set(_want)}
    _missing = sorted(set(_want) - set(_known))
    print(f"[B1425 STRATEGY_SUBSET_FILE] {_subset_path}: requested {len(_want)}, "
          f"matched {len(_known)}/{len(ALL_STRATEGIES)}")
    if _missing:
        print(f"[B1425 WARNING] {len(_missing)} requested name(s) not in ALL_STRATEGIES "
              f"and were SKIPPED: {_missing}")
    if not _known:
        raise SystemExit("[B1425 FATAL] strategy subset resolved to ZERO strategies - refusing "
                         "to run a backtest that would silently measure nothing.")
    _screener_mod.ALL_STRATEGIES = _known
    ALL_STRATEGIES = _known

_chunk_idx = _screener_mod.get_chunk_index_from_env()
if _chunk_idx is not None:
    _chunk_strategies = _screener_mod.get_strategy_chunk(_chunk_idx, n_chunks=8)
    print(f"[B1084 Council 206] PHASE_4_CHUNK={_chunk_idx} (chunk {chr(65 + _chunk_idx)}): "
          f"filtered {len(_chunk_strategies)}/{len(ALL_STRATEGIES)} strategies")
    # Replace module-level ALL_STRATEGIES with chunk subset (in-place
    # so engine + screen_universe see filtered dict).
    _screener_mod.ALL_STRATEGIES = _chunk_strategies
    ALL_STRATEGIES = _chunk_strategies  # rebind local import


def validate_env():
    """Pass 53 Day-9 v8h fix: replaced Unicode emoji icons ([OK] / [WARN] /
    [FAIL]) with ASCII labels - Windows cp1252 console encoding crashed on
    these characters, blocking the production runner. Caught by P1.runner
    integration test 2026-05-07 (would have blocked Phase 1A May 15).
    """
    import os
    print("\n=== Environment Check ===")
    for var, label in [
        ("ANTHROPIC_API_KEY", "required for agents"),
        ("QUIVER_API_KEY",    "optional - smart money signals"),
        ("FRED_API_KEY",      "optional - yield curve data"),
    ]:
        val = os.environ.get(var,"")
        icon = "[OK]" if val else ("[WARN]" if "optional" in label else "[FAIL]")
        print(f"  {icon} {var}: {'set' if val else 'NOT SET'} ({label})")

    # DEC-606 -- defensive Finnhub financials guard. Permanent supersedence
    # per Pass 53 v8h+1 owner-approved 2026-05-10. Run on a known-safe path
    # at startup to verify the guard is in the active path; raises if a
    # caller ever references the excluded path.
    try:
        from backtest.engine.improvements import assert_no_finnhub_financials
        assert_no_finnhub_financials("data_prefetch/polygon/financials/")
        print("  [OK] DEC-606: Finnhub financials guard active")
    except Exception as exc:
        print(f"  [WARN] DEC-606: guard check failed: {exc}")
    print()


def validate_lookahead():
    print("=== Look-Ahead Bias Validation ===")
    from backtest.data.fetcher import fetch_ohlcv
    test_date = date(2023, 6, 15)
    df = fetch_ohlcv("AAPL", start=date(2023,1,1), end=date(2023,12,31), as_of=test_date)
    if df.empty:
        print("  [WARN] Could not fetch test data - network issue")
        return True
    last = df.index[-1].date()
    if last > test_date:
        print(f"  [FAIL] LOOK-AHEAD BIAS: data has row {last} after as_of={test_date}")
        return False
    print(f"  [OK] Date ceiling works: last row = {last} (as_of = {test_date})")
    return True


def print_results(engine: BacktestEngine):
    from backtest.results.metrics import compute_all_metrics
    df = engine.get_trade_log()
    if df.empty:
        print("\nNo closed trades.")
        return
    metrics = compute_all_metrics(df)
    print("\n" + "="*75)
    print("PHASE 1A RESULTS - v2")
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
            p = "[OK]" if r["passes_all"] else ""
            a = "[WARN]" if r.get("audit_flags") else ""
            print(f"{r['strategy']:<35} {r.get('category',''):<12} {r['direction_mix']:<8} "
                  f"{int(r['total_trades']):>7,} {r['win_rate']*100:>7.1f}% "
                  f"{r['profit_factor']:>6.2f} {r['total_roi_pct']:>7.1f}% {p}{a:>4}")
    print(f"\nOutputs: {engine.output_dir}/")


def phase1a_quality_gate(engine: BacktestEngine) -> bool:
    from backtest.results.metrics import compute_all_metrics
    df = engine.get_trade_log()
    if df.empty:
        print("[FAIL] No trades - pipeline issue")
        return False
    metrics = compute_all_metrics(df)
    low_trades = metrics[metrics["total_trades"] < PASSING_CRITERIA["min_trades"]]
    passing    = metrics[metrics["passes_all"]==True]

    print("\n=== Phase 1A Quality Gate ===")
    if low_trades.empty:
        print(f"  [OK] All strategies have {PASSING_CRITERIA['min_trades']}+ trades")
    else:
        print(f"  [WARN]  {len(low_trades)} strategies below {PASSING_CRITERIA['min_trades']} trades - need more data")

    if passing.empty:
        print("  [INFO] No strategies pass all criteria yet - normal for Phase 1A dry run")
    else:
        print(f"  [OK] {len(passing)} strategies pass all criteria -> ready for Phase 1B")

    audit = metrics[metrics["audit_flags"].apply(lambda x: len(x)>0 if isinstance(x,list) else False)]
    if not audit.empty:
        print(f"  [WARN]  {len(audit)} strategies flagged for look-ahead bias audit (win rate >75% or PF >1.5)")

    passed = len(engine.closed_trades) > 0
    if passed:
        print("\n[OK] Phase 1A PASSED - pipeline clean, ready for full run or Phase 1B")
    else:
        print("\n[FAIL] Phase 1A FAILED - no trades produced")
    return passed


def _install_sigterm_handler():
    """B1043 Council 138 F-06 fix: install SIGTERM handler so kill -15 from
    phase_watchdog OR B1019 HALT-CRITICAL flushes checkpoint before exit.

    Source: Sub-A adversarial review found kill -15 + kill -9 both lose
    checkpoint flush + partial cube. Per feedback_silent_failure_pairing_rule
    + feedback_monitor_design_vs_operational_gap.

    Engine writes a TERMINATE sentinel so writer can detect graceful kill
    and flush in-memory trades to trade_log_checkpoint_emergency.csv.
    """
    import signal as _signal
    import os as _os
    def _handler(signum, frame):
        try:
            from pathlib import Path as _Path
            # Best-effort emergency flush; uses CWD as fallback if output_dir
            # not in scope (signal handlers run outside engine instance scope).
            sentinel_dir = _Path(_os.environ.get("ENGINE_OUTPUT_DIR", "."))
            sentinel_dir.mkdir(parents=True, exist_ok=True)
            (sentinel_dir / "ENGINE_SIGTERM_RECEIVED").write_text(
                f"signal={signum} pid={_os.getpid()}\n"
            )
            print(f"[B1043 F-06] SIGTERM received pid={_os.getpid()} -- "
                  "engine flushing checkpoint + exiting clean")
        except Exception:
            pass
        raise SystemExit(143)  # 128 + SIGTERM(15)
    try:
        _signal.signal(_signal.SIGTERM, _handler)
        _signal.signal(_signal.SIGINT, _handler)
    except (ValueError, AttributeError):
        pass  # not in main thread; skip silently


def main():
    _install_sigterm_handler()
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run",    action="store_true")
    p.add_argument("--no-agents",  action="store_true")
    p.add_argument("--no-git",     action="store_true",  help="Suppress git commits during run (for parallel batches - commit manually at end)")
    # Batch 187 (INV-050): decouple walk-forward suppression from --no-git.
    # Prior: walk_forward=not args.no_git -- coupled WF to git suppression.
    # Now: WF runs by default; explicit --no-walk-forward needed to disable
    # (used in parallel-batch mode where merge_batch_outputs.py recomputes WF).
    p.add_argument("--no-walk-forward", action="store_true",
                   help="Disable per-run walk-forward (use for parallel-batch mode; merge recomputes on combined trade log)")
    p.add_argument("--no-news",    action="store_true",  help="Disable news sentiment (for A/B comparison)")
    p.add_argument("--tickers",    type=str, default=None, help="Comma-separated list of tickers for batch test")
    p.add_argument("--tickers-file", type=str, default=None,
                   help="Path to file containing comma-separated OR newline-separated tickers. "
                        "Council 224 mandate 2026-07-01: bypasses Windows cmd.exe 8191-char limit "
                        "for large ticker sets (e.g., Batch B 1787 tickers = 8051 chars). "
                        "Mutually exclusive with --tickers; takes precedence if both given.")
    p.add_argument("--phase",      type=str, default="1a", choices=["1a","1a-beta","1b","1c","1d"])
    p.add_argument("--start",      type=str)
    p.add_argument("--end",        type=str)
    p.add_argument("--max-cands",  type=int, default=30,
                   help="Max screener candidates accepted per day. "
                        "Batch 314 Cat-5 A loosen: 10 -> 30 (owner-approved 2026-05-24) "
                        "to admit Phase 1A-beta strategies starved by per-day cap. "
                        "Batch 386 (owner 2026-05-26): AUTO-OVERRIDDEN to 200 when "
                        "--phase=1a-beta (cube cost is $0 without agents; the 30 "
                        "default was sized for live-agent cost control which does "
                        "not apply to cube evaluation). Phase 1B-alpha returns to 30.")
    p.add_argument("--screen-pool-workers", type=int, default=0,
                   help="Batch 322 (2026-05-25): number of process-pool workers "
                        "for per-ticker screen_instrument parallelization. "
                        "0 (default) = sequential (pre-Batch-322 behavior). "
                        "On Hetzner CPX62 16 vCPU, --screen-pool-workers=16 "
                        "is the recommended setting. Worker initializer "
                        "loads full ohlcv_dict + info_dict so per-day IPC "
                        "stays small.")
    p.add_argument("--no-portfolio-cap", action="store_true",
                   help="Batch 377 (owner 2026-05-26): bypass Batch 203 "
                        "regime cap + LIVE_TRADING_RULES max_open_positions "
                        "for Phase 1A-beta cube evaluation. Drawdown halt + "
                        "ticker-uniqueness + cash-sufficiency still apply. "
                        "AUTO-ENABLED for phase=1a-beta; pass explicitly for "
                        "other phases. Phase 1B-alpha re-engages the cap.")
    p.add_argument("--cube-isolation", action="store_true",
                   help="B1321 (Council 353, M2 pure-signal isolation): every "
                        "valid signal opens a trade; bypasses ALL cross-strategy "
                        "PORTFOLIO gates (candidate cap, cross-strategy ticker "
                        "block, cooldown, max-loss, factor-concentration, "
                        "can_open, portfolio mirror). Per-(strategy x exit) cube "
                        "cells become independent. Keep OFF for portfolio-sim "
                        "(BUG-61 shared book). Pass explicitly for the cube.")
    p.add_argument("--no-dd-halt", action="store_true",
                   help="Batch 383 (owner 2026-05-26): bypass DEC-515 Level 6 "
                        "DD halt + Portfolio.can_open drawdown_suspend gate "
                        "for Phase 1A-beta cube evaluation. Capital-protection "
                        "gate does not apply to per-(strategy x exit x regime) "
                        "cell-verdict computation. AUTO-ENABLED for "
                        "phase=1a-beta. Phase 1B-alpha re-engages the halt.")
    p.add_argument("--no-regime-affinity", action="store_true",
                   help="Batch 384 Gate 2 opt (owner 2026-05-26): bypass Batch "
                        "203/293 STRATEGY_REGIME_AFFINITY filter for Phase 1A-beta "
                        "cube. Every strategy evaluated in every regime to "
                        "produce empirical per-regime cube verdicts. AUTO-ENABLED "
                        "for phase=1a-beta. Phase 1B-alpha re-engages affinity.")
    p.add_argument("--no-event-suppression", action="store_true",
                   help="Batch 384 Gate 3 opt (owner 2026-05-26): bypass DEC-348 "
                        "event suppression (FOMC/CPI/NFP/earnings blackouts) for "
                        "Phase 1A-beta cube. Cube measures strategy robustness "
                        "through events. AUTO-ENABLED for phase=1a-beta. Phase "
                        "1B-alpha re-engages event suppression.")
    p.add_argument("--warn-run-hours", type=float, default=None,
                   help="Batch 394 (owner 2026-05-27): wall-time WARN "
                        "threshold in hours. Engine logs a single WARN "
                        "line when run exceeds this. AUTO-SET to 4.0 for "
                        "--phase=1a-beta. None=disabled.")
    p.add_argument("--max-run-hours", type=float, default=None,
                   help="Batch 394 (owner 2026-05-27): wall-time HARD-KILL "
                        "threshold in hours. Engine flushes a final "
                        "checkpoint and sys.exit(1). External monitor "
                        "watchdog backs this up at +5min. AUTO-SET to "
                        "6.0 for --phase=1a-beta. None=disabled.")
    p.add_argument("--output-dir", type=str, default="output_v2")
    # B1076 Council 191 Option 1: resume-from-checkpoint MVP (Sub-B F-13.1
    # + S5-B1073 ticket). Local directory containing engine_state.json +
    # trade_log_checkpoint.csv from prior interrupted run. Engine skips
    # to last completed sim_day + 1. Open trades at interruption point
    # dropped (acknowledged caveat; B1075 had 0 open at interruption).
    p.add_argument("--resume-from-checkpoint", type=str, default=None,
                   help="B1076 Council 191 Option 1: Local directory "
                        "containing engine_state.json + trade_log_checkpoint.csv "
                        "from prior interrupted run. Engine reads sim_day_index + "
                        "trades_so_far + closed trades; skips sim_day loop up to "
                        "resume_sim_day + 1; continues from there. Open trades "
                        "dropped (warned). Operator: aws s3 sync prior RUN_ID "
                        "output_phase_N/ <local-dir>/ pre-launch.")
    p.add_argument("--vectorized-cube-exits", action="store_true",
                   help="Batch 412 (owner 2026-05-28 owner-approved): activate "
                        "the numpy-vectorized cube-exit fast path "
                        "(exit_strategies_vectorized.EXIT_STRATEGIES_VECTORIZED). "
                        "Default OFF for byte-identical fallback to the scalar "
                        "iterrows() loop. Tier 1 ships in 412 (9 methods: "
                        "time_stop_10d/20d, class_time_stop, trailing_5/10/15pct, "
                        "fixed_4r_2r, r_multiple_2r/3r) with ~10-12pct engine "
                        "speedup. Tier 2 follows in Batch 413.")
    args = p.parse_args()

    # Batch 377: auto-enable --no-portfolio-cap for 1a-beta cube evaluation
    if args.phase == "1a-beta" and not args.no_portfolio_cap:
        print("[Batch 377] Phase 1a-beta detected -> auto-enabling --no-portfolio-cap "
              "(cube evaluation mode). Pass --no-portfolio-cap=False to override.")
        args.no_portfolio_cap = True
    # Batch 383: same auto-enable for --no-dd-halt
    if args.phase == "1a-beta" and not args.no_dd_halt:
        print("[Batch 383] Phase 1a-beta detected -> auto-enabling --no-dd-halt "
              "(cube evaluation mode, capital-protection gates re-engage in 1B-alpha).")
        args.no_dd_halt = True
    # Batch 384: Gate 2 + 3 auto-enable for phase=1a-beta
    if args.phase == "1a-beta" and not args.no_regime_affinity:
        print("[Batch 384] Phase 1a-beta detected -> auto-enabling --no-regime-affinity "
              "(Gate 2 opt; every strategy x regime gets empirical cube cells).")
        args.no_regime_affinity = True
    if args.phase == "1a-beta" and not args.no_event_suppression:
        print("[Batch 384] Phase 1a-beta detected -> auto-enabling --no-event-suppression "
              "(Gate 3 opt; cube measures strategy robustness through events).")
        args.no_event_suppression = True
    # Batch 386 (owner 2026-05-26 option B): raise --max-cands default 30 -> 200
    # for phase=1a-beta cube evaluation. With --no-agents the original
    # cost-control rationale for 30 cap does not apply. 200 admits ~6.7x
    # more candidates/day, supporting empirical cube fires for the now-29+
    # strategies competing for slots.
    # B1543 (owner-approved): in OPTIMIZATION_MODE the 200 cap is NOT applied.
    # It was sized for ~29 strategies competing for slots; a parameter sweep
    # cannot know how many combinations fire, and a binding cap makes tickers
    # compete - which would break the disjoint-universe APPEND design.
    from backtest.config import OPTIMIZATION_MODE as _OPT_MODE
    if _OPT_MODE and args.max_cands == 30:
        print("[B1543] OPTIMIZATION_MODE -> max-cands UNCAPPED (10000) "
              "so the candidate cap cannot bind during a parameter sweep.")
        args.max_cands = 10000
    elif args.phase == "1a-beta" and args.max_cands == 30:
        print("[Batch 386] Phase 1a-beta detected -> raising --max-cands 30 -> 200 "
              "(cube evaluation needs more candidate throughput; cost is $0 without "
              "agents). Pass --max-cands explicitly to override.")
        args.max_cands = 200
    # Batch 394 (owner 2026-05-27): auto-set 4h warn / 6h hard-kill for 1a-beta.
    # Defense-in-depth pairs with the external monitor watchdog (+5min backup).
    # Batch 1094-B Q3-v2 (Council 229 Option A owner-approved 2026-07-02):
    # FAIL-LOUD replaces prior auto-set behavior. Batch 394 6.0-hr auto-set was
    # designed as AWS cost guard 2026-05-27; on laptop (no per-hour cost) it
    # killed Batch A at day=720/1044 = 68.9% (PIVOT #50). Owner rejected raised
    # auto-set (48.0 was proposed then rejected as still-a-time-bomb) in favor
    # of fail-loud: every phase=1a-beta invocation MUST pass --max-run-hours
    # explicitly. Prevents silent inheritance of wrong-env defaults; enforces
    # per-invocation conscious choice per CHECKLIST #129 env-config-drift audit.
    if args.phase == "1a-beta" and args.max_run_hours is None:
        print(
            "\nERROR: --max-run-hours is REQUIRED for --phase=1a-beta.\n"
            "\n"
            "  Prior behavior (auto-set) removed 2026-07-02 (Council 229 Option A)\n"
            "  after Batch A PIVOT #50 (6.0-hr AWS guard silently killed laptop\n"
            "  run at 68.9%).\n"
            "\n"
            "  Recommended values by environment:\n"
            "    Laptop, small batch (<200 tickers, <8hr projected):  24.0\n"
            "    Laptop, medium batch (150-500 tickers, <24hr):       48.0\n"
            "    Laptop, full universe (1500+ tickers, ~100hr):      120.0-168.0\n"
            "    AWS spot instance (cost-controlled):                   6.0\n"
            "    AWS on-demand r6a.4xlarge single run:                  24.0\n"
            "\n"
            "  Also pass --warn-run-hours (auto-derived to 80% of --max-run-hours\n"
            "  if omitted).\n"
            "\n"
            "  Example: --max-run-hours 120.0 --warn-run-hours 100.0\n",
            file=sys.stderr,
        )
        sys.exit(2)
    if args.phase == "1a-beta" and args.warn_run_hours is None:
        # Auto-derive warn as 80% of max (max already validated non-None above).
        # This is safe because warn is INFO-tier (logs once, does not kill), so
        # a sensible default preserves owner ergonomics without silent time-bombs.
        args.warn_run_hours = round(0.8 * args.max_run_hours, 1)
        print(
            f"[Batch 1094-B] --warn-run-hours not set -> auto-derived to "
            f"{args.warn_run_hours} (80% of --max-run-hours={args.max_run_hours}). "
            f"Pass explicit value to override."
        )

    # Batch 412: opt-in vectorized cube-exit fast path. Default OFF preserves
    # byte-identical scalar fallback - flip via --vectorized-cube-exits when
    # ready (after current run completes per owner directive 2026-05-28).
    if args.vectorized_cube_exits:
        from backtest.engine import exit_strategies as _exit_mod
        _exit_mod.USE_VECTORIZED_EXITS = True
        print("[Batch 412] --vectorized-cube-exits ON -> Tier 1 cube exits "
              "dispatched to exit_strategies_vectorized (9 methods; ~10-12% "
              "engine speedup; byte-identical to scalar).")

    phase_key = f"phase_{args.phase}"

    print("="*70)
    print(f"STAGE 2 BACKTESTING ENGINE v2 - Phase {args.phase.upper()}")
    print(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    # B2017: the parenthetical here carried a hand-maintained roster range,
    # stale since B1003 corrected F-002 - counts in output must be DERIVED (#221).
    print(f"{len(ALL_STRATEGIES)} strategy classes active this run | Trailing stop exits | Circuit breakers | Long + Short")
    print("="*70)

    # Batch 270 (Tier 2.3 of T1A_COMPREHENSIVE_REVIEW_2026_05_20):
    # Roster sanity gate. Verifies all 148 ALL_STRATEGIES entries are callable
    # + return valid dicts. Raises before launching the 17h backtest if any
    # strategy fails to load. Prevents recurrence of the 2026-05-19 T1a
    # stale-roster bug (Batches 252-255 registered 16h after launch -> 25
    # silent zero-fire strategies across the entire run).
    from backtest.signals.screener import validate_strategy_roster as _validate_roster
    try:
        _roster_summary = _validate_roster()
        print(f"Roster sanity: {_roster_summary['callable_ok']}/{_roster_summary['total_registered']} "
              f"callable OK | {_roster_summary['active_count']} active | "
              f"{_roster_summary['deprecated_count']} deprecated (DEC-218 filter)")
    except RuntimeError as exc:
        print(f"CRITICAL: Roster sanity gate failed: {exc}")
        sys.exit(1)

    validate_env()
    if not validate_lookahead():
        print("CRITICAL: Look-ahead bias check failed. Aborting.")
        sys.exit(1)

    if args.dry_run:
        start    = date(2023, 1, 1)
        end      = date(2023, 2, 28)
        universe = ["AAPL","MSFT","NVDA","AMZN","GOOGL","SPY","QQQ","XLK","GLD","TLT"]
        agents   = False
        print(f"\nDRY RUN: {start} -> {end} | {len(universe)} instruments | no agents\n")
    else:
        start  = date.fromisoformat(args.start) if args.start else BACKTEST_START
        end    = date.fromisoformat(args.end)   if args.end   else BACKTEST_END
        agents = not args.no_agents

        # B1043 Council 138 Sub-B + B1045 Council 140 HONEST-FINDING PIVOT #27:
        # holdout_guard wire CORRECTED. Phase C v2.5 smoke FAIL revealed the
        # original B1043 fix was over-aggressive: Phase 1A-beta backtest is
        # the LEGITIMATE OOS evaluation (its purpose IS to test that window).
        # Wrong scope was the agent training path, not the backtest engine.
        #
        # B1045 fix: wrap engine entry in HoldoutUnlock context with explicit
        # reason. This preserves enforcement (any rogue non-backtest caller
        # still HALTed) while allowing the legitimate backtest evaluation.
        # M4 holdout still locks for agent training paths per
        # feedback_monitor_design_vs_operational_gap.
        try:
            from backtest.util.holdout_guard import (
                HoldoutUnlock as _HoldoutUnlock,
                FINAL_OOS_HOLDOUT_START, FINAL_OOS_HOLDOUT_END,
            )
            _holdout_unlock_ctx = _HoldoutUnlock(
                "phase_1a_beta_backtest_evaluation_per_design"
            )
            _holdout_unlock_ctx.__enter__()
            print(f"[B1045 Sub-B] HoldoutUnlock active: phase 1A-beta "
                  f"backtest evaluating window incl "
                  f"{FINAL_OOS_HOLDOUT_START}..{FINAL_OOS_HOLDOUT_END}")
        except ImportError:
            print("[B1045 Sub-B WARN] holdout_guard not importable; "
                  "M4 OOS protection inactive this run")
            _holdout_unlock_ctx = None

        # Council 224 laptop-execution 2026-07-01: --tickers-file bypasses
        # Windows cmd.exe 8191-char limit. Takes precedence over --tickers.
        # Accepts comma-separated OR newline-separated tickers.
        if args.tickers_file:
            with open(args.tickers_file, "r") as _tf:
                _raw = _tf.read().strip()
            # Handle both comma and newline separators (any mix)
            _parts = [p.strip() for p in _raw.replace("\n", ",").split(",") if p.strip()]
            universe = _parts
            print(f"\nBATCH TEST MODE (file): {start} -> {end} | {len(universe)} tickers from {args.tickers_file}")
        # --tickers flag: override universe with specific tickers (for batch tests)
        elif args.tickers:
            universe = [t.strip() for t in args.tickers.split(",")]
            print(f"\nBATCH TEST MODE: {start} -> {end} | {len(universe)} tickers: {universe[:10]}{'...' if len(universe) > 10 else ''}")
        # Phase 1A-beta: full 1937-ticker Master Dedup (DEC-504 5-tier resolved precedence)
        # Owner-approved 2026-05-15 Batch 181 - supersedes the legacy 67-ticker
        # config.UNIVERSE for the production-scale validation run.
        elif args.phase == "1a-beta":
            from backtest.data.universe import get_master_universe
            universe = get_master_universe()
            print(f"\nPhase 1A-beta: {start} -> {end} | {len(universe)} instruments (Master Dedup 5-tier per DEC-504)")
        # Phase 1B+ uses full S&P 500 + ETFs universe
        elif args.phase in ("1b", "1c", "1d"):
            from backtest.data.universe import get_sp500_constituents, ETFS_FULL
            sp500    = get_sp500_constituents(500)
            universe = list(dict.fromkeys(sp500 + ETFS_FULL))
            print(f"\nPhase {args.phase.upper()}: {start} -> {end} | {len(universe)} instruments (full S&P 500 + ETFs)")
        else:
            universe = UNIVERSE
            print(f"\nPhase 1A: {start} -> {end} | {len(universe)} instruments")

        print(f"Agents: {'Haiku' if agents else 'DISABLED'} | Max cands/day: {args.max_cands}\n")
        if agents:
            days = sum(1 for i in range((end-start).days+1)
                       if (start+__import__('datetime').timedelta(days=i)).weekday()<5)
            # Cost estimate: days x avg candidates that pass screener x 11 active agents x Haiku cost
            # 11 agents per DEC-057 + DETAILED_PROJECT_PLAN.md sec 2.6 (3 analysts + Bull/Bear/RM + Trader + 3 Risk Debaters + Portfolio Manager)
            # ~30% of max_cands pass screener on average
            avg_passing = max(1, args.max_cands * 0.3)
            est_cost = days * avg_passing * 11 * 0.00035 * 1.35  # USD -> CAD approx
            print(f"  Estimated cost: ~${est_cost:.1f} CAD ({days} days x {avg_passing:.0f} avg candidates x 11 agents x $0.00035)")
            print(f"Estimated cost: ~${est_cost:.1f} USD (Haiku) - proceeding automatically")

    # Batch 187 (INV-050): walk-forward decoupled from --no-git. WF runs by
    # default; --no-walk-forward needed to disable. This fixes the bug where
    # baseline canonical runs (which use --no-git for clean output) silently
    # skipped walk-forward and reported walk_forward_summary {total: 0}.
    walk_forward_enabled = not args.no_walk_forward

    # B1431 (2026-08-01, owner-approved): RUN MODE PROVENANCE + MODE ASSERT.
    #
    # Why this exists: the B1425 R6 local run was launched WITHOUT --cube-isolation
    # and WITHOUT --no-dd-halt while R5 had both. 23.6h of compute measured a
    # capital-constrained portfolio simulation, not a per-(strategy x exit) cube:
    # 42,763 of 48,559 signals (88%) were suppressed by execution-layer gates, and
    # 29.2 candidates/day were processed against max_cands=30 while 66/day were
    # offered. NONE of that was recoverable from the log, because run_phase1a.py
    # never recorded how it was invoked - the mode had to be reverse-engineered
    # from skip-reason fingerprints days later.
    #
    # Class (not instance): ANY long-running run must be able to state its own
    # configuration from its own artifacts. Both halves ship together -
    # provenance without the assert would still have let the run start wrong.
    _mode = {
        "argv": sys.argv,
        "cube_isolation": bool(args.cube_isolation),
        "no_dd_halt": bool(args.no_dd_halt),
        "no_portfolio_cap": bool(args.no_portfolio_cap),
        "no_regime_affinity": bool(args.no_regime_affinity),
        "no_event_suppression": bool(args.no_event_suppression),
        "max_candidates_per_day": args.max_cands,
        "strategy_subset_file": os.environ.get("STRATEGY_SUBSET_FILE"),
        "universe_size": len(universe),
        "start": str(start), "end": str(end),
    }
    print(f"[B1431 RUN MODE] {json.dumps(_mode)}")
    logger.info("[B1431 RUN MODE] %s", json.dumps(_mode))

    # B1432 MODE ASSERT (generalized from B1431, which checked only 2 of 6 gates).
    #
    # CUBE_MODE_REQUIRED is the SINGLE definition of what a cube run is, derived
    # from the canonical R5 invocation at scripts/aws_chunk_launch.py:92-95 - not
    # from memory, and not from whichever flags last caused harm. Every entry is
    # correctness-critical for per-(strategy x exit) measurement:
    #
    #   cube_isolation      every valid signal opens a trade; no cross-strategy
    #                       candidate cap, so cells do not depend on the roster
    #   no_dd_halt          the L6 drawdown halt is equity-path-dependent, so it
    #                       suppresses DIFFERENT signals depending on prior P&L
    #   no_portfolio_cap    open-position cap is portfolio construction, not
    #                       per-cell edge
    #   no_regime_affinity  cube must produce cells for every strategy x regime,
    #                       including regimes the affinity table would block
    #   no_event_suppression cube measures robustness THROUGH events
    #   run_agents=False    PROVEN CONTAMINATION (B1432): with agents on but the
    #                       API unavailable, the failed score (<=40, the downgrade
    #                       threshold) knocked EVERY candidate above LOW down one
    #                       tier - measured live as MEDIUM_HIGH 3->0, MEDIUM 2->3,
    #                       LOW 11->13. Tier drives position sizing, so every
    #                       trade was mis-sized and all P&L was wrong.
    #
    # NOTE: --phase 1a-beta auto-enables four of these (portfolio_cap, dd_halt,
    # regime_affinity, event_suppression) and raises max-cands 30 -> 200, but does
    # NOT set cube_isolation or no_agents. That partial auto-enable is exactly the
    # trap: `--phase 1a` plus two hand-picked flags LOOKS like a cube run and is not.
    CUBE_MODE_REQUIRED = {
        "cube_isolation":       (args.cube_isolation,       True,  "--cube-isolation"),
        "no_dd_halt":           (args.no_dd_halt,           True,  "--no-dd-halt"),
        "no_portfolio_cap":     (args.no_portfolio_cap,     True,  "--no-portfolio-cap"),
        "no_regime_affinity":   (args.no_regime_affinity,   True,  "--no-regime-affinity"),
        "no_event_suppression": (args.no_event_suppression, True,  "--no-event-suppression"),
        "agents_disabled":      (not agents,                True,  "--no-agents"),
    }
    _cube_intent = bool(_mode["strategy_subset_file"]) or args.cube_isolation
    if _cube_intent:
        _violations = [(k, flag) for k, (actual, want, flag) in CUBE_MODE_REQUIRED.items()
                       if actual != want]
        if _violations:
            raise SystemExit(
                "[B1432 MODE ASSERT] This is a CUBE run (STRATEGY_SUBSET_FILE set "
                "and/or --cube-isolation) but the cube gate set is incomplete.\n"
                "  MISSING: " + ", ".join(f for _, f in _violations) + "\n"
                "  A partial cube configuration silently produces a PORTFOLIO artifact "
                "that will later be read as a cube (LEARNINGS L260/L264/L266).\n"
                "  Canonical invocation: scripts/aws_chunk_launch.py:92-95 -\n"
                "    --phase 1a-beta --cube-isolation --no-agents --no-news \\\n"
                "    --no-walk-forward --no-git --max-run-hours <H>\n"
                "  (--phase 1a-beta auto-enables portfolio_cap/dd_halt/regime_affinity/"
                "event_suppression; cube_isolation and no_agents are NOT auto-enabled.)"
            )

    engine = BacktestEngine(
        universe=universe, start=start, end=end,
        phase=phase_key, max_candidates_per_day=args.max_cands,
        run_agents=agents, output_dir=args.output_dir,
        disable_news=args.no_news,
        walk_forward=walk_forward_enabled,
        screen_pool_workers=args.screen_pool_workers,  # Batch 322
        no_portfolio_cap=args.no_portfolio_cap,        # Batch 377
        no_dd_halt=args.no_dd_halt,                    # Batch 383
        cube_isolation=args.cube_isolation,           # B1321 Council 353 M2

        no_regime_affinity=args.no_regime_affinity,    # Batch 384 Gate 2
        no_event_suppression=args.no_event_suppression, # Batch 384 Gate 3
        warn_run_hours=args.warn_run_hours,             # Batch 394 WARN at 4h
        max_run_hours=args.max_run_hours,               # Batch 394 KILL at 6h
        resume_from_checkpoint=args.resume_from_checkpoint, # B1076 Council 191
    )
    if args.no_git:
        # B1431: removed a redundant `import os` here. `os` is imported at module
        # scope (line 14), and this function-local import made `os` a LOCAL name
        # for the whole of main() - so any earlier reference raised
        # UnboundLocalError. That is precisely what broke the B1431 run-mode
        # block on its first execution. Class: a function-local re-import of a
        # module-scope name silently rebinds it for the entire function.
        os.environ["BACKTEST_NO_GIT"] = "1"
        print("[WARN]  --no-git: parallel batch mode")
        print("   - Git operations suppressed - commit manually when all batches complete")
        print("   Command: git status -> git add [dirs] -> git commit -> git pull --rebase -> git push")
    if args.no_walk_forward:
        print("[INFO] --no-walk-forward: WF disabled for this run (use merge_batch_outputs.py to compute WF on combined trade log)")

    if args.no_news:
        print("[WARN]  News sentiment DISABLED - A/B comparison mode")
    engine.load_data()
    engine.run()
    print_results(engine)
    engine.save_all_outputs()
    phase1a_quality_gate(engine)
    print(f"\nLog: backtest_v2.log | Outputs: {args.output_dir}/")


if __name__ == "__main__":
    main()
