"""Rebuild the (strategy x exit_method) cube from a Phase 1A-beta trade_log.

Source (per CHECKLIST #77 canonical-source attribution):
- Discovery 2026-05-25 Batch 359: the cube engine ALREADY EXISTS
  (backtest/engine/exit_strategies.py::run_exit_comparison) and IS called
  from BacktestEngine.save_all_outputs (backtest.py:1996-2051), producing
  trade_exit_detail.csv natively. BUT the merge job
  (scripts/merge_batch_outputs.py) does NOT propagate trade_exit_detail
  through to the merged output — see BUILD_PLAN_PROGRESS.md line 63.
- The 2026-05-24 Phase 1A-beta run produced trade_exit_detail per batch
  but the merge dropped it; output_phase_1a_beta_merged_local/ has the
  trade_log but no cube. The cube was reconstructable post-hoc from
  trade_log + OHLCV cache.

This script rebuilds the cube locally from the merged trade_log by
calling run_exit_comparison on each trade. Output goes to
output_audit/trade_exit_detail_phase_1a_beta_rebuilt.csv with the canonical
schema: one row per (trade, exit_method).

Usage:
  python scripts/rebuild_cube_from_trade_log.py \
      --trade-log output_phase_1a_beta_merged_local/trade_log.csv \
      --ohlcv-dir data_prefetch/polygon/ohlcv_daily \
      --output-dir output_audit
"""
from __future__ import annotations

import argparse
import ast
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

# Make repo root importable when invoked as `python scripts/...`.
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from backtest.engine.exit_strategies import run_exit_comparison  # noqa: E402


logger = logging.getLogger(__name__)


def _parse_entry_date(raw) -> date:
    """Convert entry_date string/date/datetime to a date object.

    NB: `isinstance(datetime_obj, date)` is True (datetime is a date subclass),
    so the datetime check MUST come before the date check.
    """
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    if hasattr(raw, "date") and callable(getattr(raw, "date", None)):
        return raw.date()
    s = str(raw)[:10]
    return datetime.strptime(s, "%Y-%m-%d").date()


def _parse_signals_at_entry(raw) -> dict:
    """signals_at_entry is stored as a JSON / Python-repr string in trade_log."""
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    try:
        s = str(raw)
        if not s or s.lower() == "nan":
            return {}
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return {}


def _load_ohlcv(ticker: str, ohlcv_dir: Path, _cache: dict) -> pd.DataFrame | None:
    """Lazy-load + cache OHLCV parquet per ticker."""
    if ticker in _cache:
        return _cache[ticker]
    safe = ticker.replace(".", "-")
    p = ohlcv_dir / f"{safe}.parquet"
    if not p.exists():
        _cache[ticker] = None
        return None
    try:
        df = pd.read_parquet(p)
    except Exception as e:
        logger.debug("Failed to load %s: %s", ticker, e)
        _cache[ticker] = None
        return None
    # Ensure DatetimeIndex for run_exit_comparison contract
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
    elif not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
        except Exception:
            _cache[ticker] = None
            return None
    _cache[ticker] = df
    return df


def rebuild_cube(trade_log_path: Path, ohlcv_dir: Path,
                  output_dir: Path) -> pd.DataFrame:
    """Rebuild the cube; returns the trade_detail_df and writes CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tl = pd.read_csv(trade_log_path, low_memory=False)
    logger.info("Loaded %d trades from %s", len(tl), trade_log_path)

    ohlcv_cache: dict = {}
    all_detail_frames: list = []

    # Group by strategy so run_exit_comparison receives all that strategy's
    # trades together (matches the engine's per-strategy call pattern at
    # backtest.py:2042 + supports its per-strategy summary stats).
    n_strategies = tl["strategy"].nunique()
    for i_strat, (strategy, strat_df) in enumerate(tl.groupby("strategy"), 1):
        trades_data: list = []
        missing_ohlcv = 0
        for _, row in strat_df.iterrows():
            ticker = row["ticker"]
            df_full = _load_ohlcv(ticker, ohlcv_dir, ohlcv_cache)
            if df_full is None:
                missing_ohlcv += 1
                continue
            entry_date = _parse_entry_date(row["entry_date"])
            sig = _parse_signals_at_entry(row.get("signals_at_entry"))
            atr = sig.get("atr", row["entry_price"] * 0.02)
            trades_data.append({
                "ticker":      ticker,
                "df":          df_full,
                "entry_date":  entry_date,
                "entry_price": float(row["entry_price"]),
                "direction":   row["direction"],
                "atr":         float(atr),
                "signals":     {**sig, "ticker": ticker, "strategy_name": strategy},
            })
        if not trades_data:
            logger.warning("[%d/%d] %s: 0 trades after OHLCV resolution",
                           i_strat, n_strategies, strategy)
            continue
        try:
            _, td = run_exit_comparison(strategy, trades_data)
        except Exception as e:
            logger.warning("[%d/%d] %s: exit-comparison failed: %s",
                           i_strat, n_strategies, strategy, e)
            continue
        if not td.empty:
            all_detail_frames.append(td)
        logger.info("[%d/%d] %s: %d trades -> %d cube rows (missing_ohlcv=%d)",
                    i_strat, n_strategies, strategy,
                    len(trades_data), len(td), missing_ohlcv)

    if not all_detail_frames:
        logger.error("No cube rows produced")
        return pd.DataFrame()
    cube = pd.concat(all_detail_frames, ignore_index=True)
    out_path = output_dir / "trade_exit_detail_phase_1a_beta_rebuilt.csv"
    cube.to_csv(out_path, index=False)
    logger.info("Wrote %s (%d rows)", out_path, len(cube))
    return cube


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade-log",
                    default="output_phase_1a_beta_merged_local/trade_log.csv")
    ap.add_argument("--ohlcv-dir",
                    default="data_prefetch/polygon/ohlcv_daily")
    ap.add_argument("--output-dir", default="output_audit")
    args = ap.parse_args()

    cube = rebuild_cube(Path(args.trade_log), Path(args.ohlcv_dir),
                         Path(args.output_dir))
    if cube.empty:
        return 1

    # Sanity summary
    print()
    print("=" * 60)
    print("  CUBE REBUILD SUMMARY")
    print("=" * 60)
    print(f"Total cube rows:        {len(cube)}")
    print(f"Unique strategies:      {cube['strategy'].nunique()}")
    print(f"Unique exit methods:    {cube['exit_method'].nunique()}")
    print(f"Cells (strat x exit):   {cube.groupby(['strategy','exit_method']).ngroups}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
