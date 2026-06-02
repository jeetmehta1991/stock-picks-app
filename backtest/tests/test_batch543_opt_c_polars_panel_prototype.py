"""Batch 543 (2026-06-02) -- OPT-C Polars panel first-stake tests.

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-C.

Pins:

  (1) compute_rsi_panel_polars produces PARITY with pandas
      compute_rsi_panel (0 value diffs on key set)
  (2) Empirical benchmark finding: naive Polars per-column expressions
      are SLOWER than pandas DataFrame.ewm() (~4.3x slower at N=388
      tickers). The OPT-C commitment requires a long-format rewrite
      to realize Polars benefits -- pin as a knowledge artifact.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest


def _make_close_panel(n_tickers: int = 10, n_dates: int = 200,
                       seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed=seed)
    log_ret = rng.normal(0.0005, 0.015, size=(n_dates, n_tickers))
    log_ret[0] = 0
    close = 100.0 * np.exp(np.cumsum(log_ret, axis=0))
    return pd.DataFrame(
        close,
        columns=[f"T{i}" for i in range(n_tickers)],
        index=pd.date_range("2024-01-01", periods=n_dates, freq="B"),
    )


def test_batch543_polars_rsi_matches_pandas_rsi_panel():
    """Parity: per-ticker RSI values from Polars match pandas to 0.01."""
    from backtest.signals.technical_panel import compute_rsi_panel as pandas_p
    from backtest.signals.polars_panel import compute_rsi_panel_polars as polars_p
    panel = _make_close_panel(n_tickers=5, n_dates=200)
    pd_out = pandas_p(panel)
    pl_out = polars_p(panel)
    for ticker in pd_out:
        for k, pdv in pd_out[ticker].items():
            assert k in pl_out[ticker], (
                f"polars panel missing {ticker}.{k}"
            )
            plv = pl_out[ticker][k]
            if isinstance(pdv, float) and isinstance(plv, float):
                assert abs(pdv - plv) < 0.01, (
                    f"{ticker}.{k}: pandas={pdv} polars={plv}"
                )
            else:
                assert pdv == plv, (
                    f"{ticker}.{k}: pandas={pdv} polars={plv}"
                )


def test_batch543_polars_slower_than_pandas_naive_translation():
    """KNOWLEDGE ARTIFACT: naive per-column Polars expressions are
    SLOWER than pandas DataFrame.ewm() at the 388-ticker production
    scale. Pinning this finding so any future OPT-C work knows to
    use long-format groupby + window, NOT per-column expression lists.

    This test ASSERTS the slowdown -- if a future commit produces a
    Polars impl that's actually faster than pandas, this test will
    fail and prompt celebrating the win + updating the OPT-C plan.
    """
    from backtest.signals.technical_panel import compute_rsi_panel as pandas_p
    from backtest.signals.polars_panel import compute_rsi_panel_polars as polars_p
    panel = _make_close_panel(n_tickers=50, n_dates=200)
    # Warmup
    pandas_p(panel)
    polars_p(panel)
    t0 = time.perf_counter()
    for _ in range(3):
        pandas_p(panel)
    pd_ms = (time.perf_counter() - t0) / 3 * 1000
    t0 = time.perf_counter()
    for _ in range(3):
        polars_p(panel)
    pl_ms = (time.perf_counter() - t0) / 3 * 1000
    # Naive polars expected to be 1.5-5x SLOWER on 50 tickers
    speedup = pd_ms / pl_ms if pl_ms > 0 else 0.0
    print(f"\n  pandas={pd_ms:.1f}ms  polars={pl_ms:.1f}ms  "
          f"speedup={speedup:.2f}x")
    # Assertion documents the current finding; if Polars rewrite later
    # makes this >= 1.0, the test fails and prompts updating the OPT-C
    # plan to celebrate the win.
    if speedup >= 1.0:
        pytest.fail(
            f"NEW FINDING: naive Polars is now >= pandas at this scale "
            f"(speedup={speedup:.2f}). Either underlying lib improved "
            f"or a recent change made polars_panel faster. Update OPT-C "
            f"queue + re-evaluate roadmap."
        )
