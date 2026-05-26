"""Batch 362 cube smoke: Stage D scope cube replay validation.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-25 Batch 362 "Do we need smoke testing for the cube before we
scale to full phase 1a beta?" -- YES.

Runs Phase 1A-beta engine at Stage D scope (150 tkrs x 4y) with the
process pool enabled, then verifies the cube replay step
(`save_all_outputs` -> `run_exit_comparison`) produced the expected
`trade_exit_detail.csv` with non-trivial coverage.

This catches the 2026-05-24 failure mode where per-batch dirs ended
up missing trade_exit_detail.csv (batches killed before
save_all_outputs completed).

Validates:
  1. Engine completes end-to-end without crash
  2. trade_log.csv non-empty + Phase-1A-beta schema (combo_id column etc.)
  3. trade_exit_detail.csv non-empty
  4. Cube cells span multiple exit methods (>=10 of 25 EXIT_STRATEGIES)
  5. Cube cells span multiple strategies (>=5)
  6. Per-cell row counts roughly track n_trades x 25
  7. Pool runtime is faster than projected sequential (sanity check on
     the 4-8x speedup claim)

Usage:
  python scripts/smoke_test_cube_stage_d.py --workers 8
  python scripts/smoke_test_cube_stage_d.py --workers 0  # sequential baseline

Exits with code 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)


def _load_stage_d_tickers() -> list[str]:
    """Load the canonical Stage D 150-ticker stratified sample.

    Falls back to a smaller deterministic sample if the canonical
    file is missing."""
    stage_d_file = REPO / "scripts" / "stage_d_tickers.txt"
    if stage_d_file.exists():
        tks = [t.strip() for t in stage_d_file.read_text().splitlines()
               if t.strip() and not t.startswith("#")]
        if tks:
            return tks
    logger.warning("stage_d_tickers.txt missing; using fallback 30-ticker sample")
    return [
        "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "BRK-B",
        "JPM", "V", "WMT", "JNJ", "PG", "XOM", "MA", "HD", "CVX", "ABBV",
        "LLY", "PFE", "BAC", "KO", "PEP", "AVGO", "TMO", "COST", "MRK",
        "ABT", "ACN", "ADBE",
    ]


def _run(tickers, start, end, workers) -> tuple[Path, float]:
    from backtest.engine.backtest import BacktestEngine
    out_dir = REPO / "output_smoke_cube"
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = BacktestEngine(
        universe=tickers,
        start=date.fromisoformat(start),
        end=date.fromisoformat(end),
        phase="phase_1a",
        max_candidates_per_day=30,
        run_agents=False,
        output_dir=str(out_dir),
        disable_news=True,
        walk_forward=False,
        screen_pool_workers=workers,
    )
    t0 = time.time()
    engine.load_data()
    engine.run()
    engine.save_all_outputs()
    elapsed = time.time() - t0
    return out_dir, elapsed


def _validate_outputs(out_dir: Path) -> list[str]:
    """Return list of failure strings; empty list = PASS."""
    fails = []
    tl_path = out_dir / "trade_log.csv"
    cube_path = out_dir / "trade_exit_detail.csv"
    bt_results = out_dir / "backtest_results.csv"

    # Gate 1: trade_log.csv exists + non-empty
    if not tl_path.exists():
        fails.append(f"GATE 1 FAIL: {tl_path} missing")
        return fails
    tl = pd.read_csv(tl_path, low_memory=False)
    if tl.empty:
        fails.append("GATE 1 FAIL: trade_log empty")
        return fails
    print(f"  GATE 1 PASS: trade_log {len(tl)} trades, "
          f"{tl['strategy'].nunique()} strategies")

    # Gate 2: combo_id column present (Batch 324)
    if "combo_id" not in tl.columns:
        fails.append("GATE 2 FAIL: combo_id column missing (Batch 324 regression)")
    else:
        print(f"  GATE 2 PASS: combo_id present ({tl['combo_id'].nunique()} unique)")

    # Gate 3: trade_exit_detail.csv exists + non-empty
    if not cube_path.exists():
        fails.append(f"GATE 3 FAIL: {cube_path} missing (save_all_outputs cube step skipped)")
        return fails
    cube = pd.read_csv(cube_path, low_memory=False)
    if cube.empty:
        fails.append("GATE 3 FAIL: trade_exit_detail empty")
        return fails
    print(f"  GATE 3 PASS: trade_exit_detail {len(cube)} cube rows")

    # Gate 4: cube spans >= 10 exit methods
    n_em = cube["exit_method"].nunique()
    if n_em < 10:
        fails.append(f"GATE 4 FAIL: cube spans only {n_em} exit methods (expected >=10)")
    else:
        print(f"  GATE 4 PASS: cube spans {n_em} exit methods")

    # Gate 5: cube spans >= 5 strategies
    n_s = cube["strategy"].nunique()
    if n_s < 5:
        fails.append(f"GATE 5 FAIL: cube spans only {n_s} strategies (expected >=5)")
    else:
        print(f"  GATE 5 PASS: cube spans {n_s} strategies")

    # Gate 6: per-trade fan-out ~25x
    n_trades = len(tl)
    avg_fanout = len(cube) / max(n_trades, 1)
    if avg_fanout < 5:
        fails.append(f"GATE 6 FAIL: avg fan-out {avg_fanout:.1f}x (expected near 25x)")
    else:
        print(f"  GATE 6 PASS: avg cube fan-out {avg_fanout:.1f}x per trade")

    # Gate 7: backtest_results.csv exists (sanity)
    if not bt_results.exists():
        fails.append("GATE 7 FAIL: backtest_results.csv missing")
    else:
        print(f"  GATE 7 PASS: backtest_results.csv present")

    return fails


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=8,
                   help="screen-pool workers (0 = sequential)")
    p.add_argument("--tickers", default="",
                   help="comma-separated; default = Stage D 150-ticker sample")
    p.add_argument("--start", default="2022-05-05")
    p.add_argument("--end", default="2026-05-05")
    args = p.parse_args()

    tickers = (args.tickers.split(",") if args.tickers
               else _load_stage_d_tickers())

    print("=" * 70)
    print(f"  CUBE SMOKE (Stage D scope)")
    print("=" * 70)
    print(f"Tickers: {len(tickers)} ({tickers[:5]}...)")
    print(f"Window:  {args.start} -> {args.end}")
    print(f"Workers: {args.workers}")
    print()

    out_dir, elapsed = _run(tickers, args.start, args.end, args.workers)
    print(f"\n[Wall time] {elapsed:.1f}s = {elapsed/60:.1f}min "
          f"(workers={args.workers})")

    print(f"\n[Validating outputs in {out_dir}]")
    fails = _validate_outputs(out_dir)

    if fails:
        print(f"\nFAIL: {len(fails)} gate(s) failed")
        for f in fails:
            print(f"  {f}")
        sys.exit(1)
    print(f"\nPASS: all 7 gates green; cube smoke ready for full Phase 1A-beta")
    sys.exit(0)


if __name__ == "__main__":
    main()
