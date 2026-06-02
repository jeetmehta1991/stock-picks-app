"""Batch 543 (2026-06-02) -- OPT-C Polars panel engine first stake.

Source: per CHECKLIST #77 + owner directive 2026-06-01 "3. commit to
6-8 weeks" for the OPT-C Polars panel engine.
Queue: EXECUTION_QUEUE.md OPT-C.

SCOPE: this module is the FIRST stake in a 6-8 week migration from
pandas to Polars for the panel-style signal computation hot path.
Polars uses Rust-backed columnar evaluation with parallel execution
out of the box; benchmarks consistently show 3-10x speedup vs pandas
on the operations that dominate our screen-step (groupby + window +
arithmetic over per-ticker columns).

This batch ships ONE indicator (RSI) as a Polars panel implementation
+ benchmark harness. If benchmark shows >= 3x speedup vs the existing
pandas panel (technical_panel.compute_rsi_panel), expand to remaining
indicators incrementally over subsequent batches.

NOT YET WIRED. The pandas panel from B537 stays as the production
path. This module is a prototype + measurement tool. Production
swap happens after full Polars panel coverage + parity validation
against pandas panel (mirrors B538 wire-in pattern).

Migration roadmap (6-8 week target):
  Week 1: RSI Polars (this batch) + benchmark + design doc in
          module docstring
  Week 2-3: EMA/SMA/MACD/Bollinger Polars equivalents
  Week 4-5: ATR/StochRSI/Stochastic/Williams_R/ROC/AO Polars
  Week 6: SMC ICT panel wrapper (calls vendored library per-ticker
          but parallelizes via Polars groupby_dynamic if applicable)
  Week 7: technical_panel.compute_panel_signals_for_as_of swap to
          Polars internals (preserving public API contract)
  Week 8: Parity gate + production wire-in
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import polars as pl


def compute_rsi_panel_polars(
    close_df_pandas,
    as_of_idx: Optional[int] = None,
) -> dict[str, dict]:
    """Polars-backed RSI computation across all tickers.

    Args:
        close_df_pandas: pandas DataFrame indexed by date, cols=tickers
                          (same shape as technical_panel.compute_rsi_panel
                          takes -- for drop-in benchmark comparison)
        as_of_idx:       row index to extract (default = last row)

    Returns: {ticker: {rsi_2, rsi_2_oversold, ..., rsi_21_extreme_ob}}
             matches technical.compute_rsi schema bit-for-bit.

    Implementation: pandas DataFrame -> Polars LazyFrame -> compute
    Wilder ewm RSI per period using `pl.col().ewm_mean(alpha=1/p)`
    + arithmetic -> collect last row + previous row -> assemble result.
    """
    if close_df_pandas is None or len(close_df_pandas) < 3:
        return {ticker: {} for ticker in close_df_pandas.columns}
    if as_of_idx is None:
        as_of_idx = len(close_df_pandas) - 1
    if as_of_idx < 1:
        return {ticker: {} for ticker in close_df_pandas.columns}

    tickers = list(close_df_pandas.columns)
    # Convert pandas -> polars (efficient via from_pandas)
    pl_df = pl.from_pandas(close_df_pandas.reset_index(drop=True))

    out: dict[str, dict] = {ticker: {} for ticker in tickers}
    for p in (2, 9, 14, 21):
        if as_of_idx < p + 1:
            continue
        # Build per-ticker RSI columns
        rsi_exprs = []
        for ticker in tickers:
            delta = pl.col(ticker).diff()
            gain = pl.when(delta > 0).then(delta).otherwise(0)
            loss = pl.when(delta < 0).then(-delta).otherwise(0)
            avg_gain = gain.ewm_mean(alpha=1 / p, adjust=False)
            avg_loss = loss.ewm_mean(alpha=1 / p, adjust=False)
            rs = avg_gain / pl.when(avg_loss == 0).then(None).otherwise(avg_loss)
            rsi = 100 - 100 / (1 + rs)
            rsi_exprs.append(rsi.alias(f"_rsi_{ticker}"))
        rsi_df = pl_df.with_columns(rsi_exprs).select(
            [f"_rsi_{t}" for t in tickers]
        )
        # Extract last + prev as Python floats
        last_row = rsi_df.row(as_of_idx)
        prev_row = rsi_df.row(as_of_idx - 1)
        for i, ticker in enumerate(tickers):
            v = last_row[i] if last_row[i] is not None else 50.0
            pv = prev_row[i] if prev_row[i] is not None else 50.0
            try:
                v = float(v) if not (isinstance(v, float) and np.isnan(v)) else 50.0
            except (TypeError, ValueError):
                v = 50.0
            try:
                pv = float(pv) if not (isinstance(pv, float) and np.isnan(pv)) else 50.0
            except (TypeError, ValueError):
                pv = 50.0
            out[ticker][f"rsi_{p}"]            = round(v, 2)
            out[ticker][f"rsi_{p}_oversold"]   = v < 30
            out[ticker][f"rsi_{p}_overbought"] = v > 70
            out[ticker][f"rsi_{p}_bullish"]    = v > 50
            out[ticker][f"rsi_{p}_rising"]     = v > pv
            out[ticker][f"rsi_{p}_extreme_os"] = v < 20
            out[ticker][f"rsi_{p}_extreme_ob"] = v > 80
    return out


__all__ = ["compute_rsi_panel_polars"]
