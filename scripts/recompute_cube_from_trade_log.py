#!/usr/bin/env python
"""Council 233 Batch A recovery (2026-07-02): standalone cube fan-out recompute.

Fixes needed WERE applied to `backtest/engine/backtest.py` (Bugs A + B in
BacktestEngine.save_all_outputs cube path). This script uses the fixed code
paths to REGENERATE the missing trade_exit_detail.csv for a completed batch
WITHOUT re-running the 4.6 hr backtest.

How it works:
  1. Load closed trades from batch_dir/trade_log.csv (skip open trades - they
     have no exit yet)
  2. Load OHLCV cache via cached_ohlcv_bulk for all unique tickers +
     required window
  3. For each strategy, build trades_data_full (with df attached from ohlcv_dict)
  4. Call run_exit_comparison(strategy_name, trades_data_full) per strategy
  5. Concatenate all trade_detail_frames -> trade_exit_detail.csv
  6. Write to batch_dir/trade_exit_detail.csv

Post-run, run scripts/verify_batch_completion.py to confirm Gate 1 EQUAL-count
verification passes.

B2615 (S6-B2611e): ATR comes from signals_at_entry or is DERIVED from the
reloaded OHLCV (scripts/replay_atr.py); a trade with neither makes the script
exit 1 before writing - the former `entry_price * 0.02` proxy was silent.
The OHLCV window is loaded from `--start-date` minus `--atr-warmup-days`
(default 365: the engine's own 1y warmup, config.DATA_LOAD_START), so the
Wilder EWM seeds on the same first bar the engine's producer saw and the
derived value reproduces the recorded one.

Usage:
  python scripts/recompute_cube_from_trade_log.py --batch-dir output_batch_A_150
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure repo root is on path
_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("recompute_cube")


def load_closed_trades(batch_dir: Path) -> pd.DataFrame:
    """Load closed trades from trade_log.csv or parquet."""
    for name in ("trade_log.parquet", "trade_log.csv"):
        p = batch_dir / name
        if p.exists():
            df = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
            logger.info(f"Loaded {p.name}: {len(df)} rows")
            # Filter to closed trades
            if "exit_date" in df.columns:
                closed = df[df["exit_date"].notna() & (df["exit_date"] != "")]
                logger.info(f"Closed trades: {len(closed)}; Open trades: {len(df) - len(closed)}")
                return closed
            return df
    raise FileNotFoundError(f"No trade log in {batch_dir}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch-dir", required=True)
    ap.add_argument("--start-date", default="2022-05-05", help="OHLCV cache window start")
    ap.add_argument("--end-date", default="2026-05-05", help="OHLCV cache window end")
    ap.add_argument("--atr-warmup-days", type=int, default=365,
                    help="B2615: calendar days loaded BEFORE --start-date (365 = "
                         "the engine's DATA_LOAD_START warmup) so a derived ATR "
                         "seeds its EWM on the engine's first bar")
    args = ap.parse_args()

    batch_dir = Path(args.batch_dir)
    if not batch_dir.exists():
        logger.error(f"{batch_dir} not found")
        return 2

    # 1. Load closed trades
    df_trades = load_closed_trades(batch_dir)
    if df_trades.empty:
        logger.error("No closed trades to recompute")
        return 2

    unique_tickers = sorted(df_trades["ticker"].unique())
    unique_strategies = sorted(df_trades["strategy"].unique())
    logger.info(f"Unique tickers: {len(unique_tickers)}; Unique strategies: {len(unique_strategies)}")

    # 2. Load OHLCV cache via bulk fetch
    logger.info(f"Loading OHLCV for {len(unique_tickers)} tickers ({args.start_date} -> {args.end_date})")
    from backtest.data.cache import get_ohlcv_bulk
    from datetime import date, timedelta
    start = date.fromisoformat(args.start_date) - timedelta(days=args.atr_warmup_days)
    end = date.fromisoformat(args.end_date)
    ohlcv_dict = get_ohlcv_bulk(unique_tickers, start, end)
    loaded = sum(1 for t in unique_tickers if ohlcv_dict.get(t) is not None and not ohlcv_dict[t].empty)
    logger.info(f"OHLCV loaded: {loaded}/{len(unique_tickers)} tickers")

    # 3. Build entry_context for each trade + call run_exit_comparison per strategy
    from backtest.engine.exit_context import build_entry_context
    from backtest.engine.exit_strategies import run_exit_comparison
    from datetime import datetime as _dt
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import replay_atr  # noqa: E402  (B2615 S6-B2611e)
    atr_counters = replay_atr.new_counters()

    # For SPY reference (needed by build_entry_context)
    spy_df = ohlcv_dict.get("SPY")
    if spy_df is None or spy_df.empty:
        logger.warning("SPY OHLCV missing; entry_context may have degraded regime context")

    exit_frames = []
    trade_detail_frames = []
    total_strategies = len(unique_strategies)
    for idx, strategy in enumerate(unique_strategies, 1):
        strat_df = df_trades[df_trades["strategy"] == strategy]
        trades_data_full = []
        for _, row in strat_df.iterrows():
            ticker = row["ticker"]
            df_full = ohlcv_dict.get(ticker)
            if df_full is None or df_full.empty:
                continue
            entry_date = row["entry_date"]
            if isinstance(entry_date, str):
                entry_date = _dt.strptime(entry_date[:10], "%Y-%m-%d").date()
            sig = row.get("signals_at_entry", {})
            if isinstance(sig, str):
                # signals_at_entry may be JSON-serialized in CSV
                try:
                    import json as _json
                    sig = _json.loads(sig.replace("'", '"')) if sig else {}
                except Exception:
                    sig = {}
            # B2615 (S6-B2611e): signals_at_entry, else derived from df_full;
            # None is counted and fails the run below - never a proxy.
            atr = replay_atr.resolve_atr(sig, row["entry_price"], df_full,
                                         entry_date, atr_counters)
            if atr is None:
                continue

            entry_context = build_entry_context(
                row=row,
                ticker=ticker,
                entry_date=entry_date,
                df_full=df_full,
                spy_df=spy_df,
                signals=sig if isinstance(sig, dict) else {},
                atr=atr,
            )

            trades_data_full.append({
                "ticker":         ticker,
                "df":             df_full,
                "entry_date":     entry_date,
                "entry_price":    row["entry_price"],
                "direction":      row["direction"],
                "atr":            atr,
                "signals":        sig if isinstance(sig, dict) else {},
                "entry_context":  entry_context,
                "category":       row.get("category", "momentum"),
            })

        if trades_data_full:
            ec, td = run_exit_comparison(strategy, trades_data_full)
            if not ec.empty:
                exit_frames.append(ec)
            if not td.empty:
                trade_detail_frames.append(td)

        if idx % 20 == 0 or idx == total_strategies:
            logger.info(f"Progress: {idx}/{total_strategies} strategies processed; "
                        f"exit_frames={len(exit_frames)} trade_detail_frames={len(trade_detail_frames)}")

    logger.info(replay_atr.report(atr_counters))
    try:
        replay_atr.assert_resolved(atr_counters, "recompute_cube")
    except replay_atr.ATRUnresolved as e:
        logger.error(str(e))
        return 1

    # 4. Concatenate + write
    exit_compare = (pd.concat(exit_frames, ignore_index=True)
                    if exit_frames else pd.DataFrame())
    trade_exit_detail = (pd.concat(trade_detail_frames, ignore_index=True)
                         if trade_detail_frames else pd.DataFrame())

    logger.info(f"Aggregated: exit_compare rows={len(exit_compare)}; trade_exit_detail rows={len(trade_exit_detail)}")

    if trade_exit_detail.empty:
        logger.error("trade_exit_detail is EMPTY - cube fan-out still broken; investigate")
        return 1

    out_detail = batch_dir / "trade_exit_detail.csv"
    trade_exit_detail.to_csv(out_detail, index=False)
    logger.info(f"Wrote {out_detail}: {len(trade_exit_detail)} rows, {len(trade_exit_detail.columns)} cols")

    out_compare = batch_dir / "exit_compare.csv"
    if not exit_compare.empty:
        exit_compare.to_csv(out_compare, index=False)
        logger.info(f"Wrote {out_compare}: {len(exit_compare)} rows")

    # Sanity: rows per closed trade
    n_closed = len(df_trades)
    rows_per_trade = len(trade_exit_detail) / n_closed if n_closed > 0 else 0
    from backtest.engine.exit_strategies import EXIT_STRATEGIES  # noqa: E402  (B2616)
    logger.info(f"Rows-per-closed-trade ratio: {rows_per_trade:.2f} (target: {len(EXIT_STRATEGIES)} = count(EXIT_STRATEGIES); was hardcoded 26 pre-B2616)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
