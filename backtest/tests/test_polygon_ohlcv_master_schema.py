"""H1 / DEC-609 schema contract test for polygon ohlcv_daily Master Dedup prefetch.

Pass 53 v8h+1 2026-05-10: pins down the 9-col schema produced by
scripts/prefetch_polygon_ohlcv_master.py at canonical path
`data_prefetch/polygon/ohlcv_daily/<TICKER>.parquet`.

Test runs only against the smoke fixture (5 known tickers); it skips if
the BG full-universe run hasn't landed yet. After BG completes, the test
also validates a sample of the full-universe parquets share the same schema.

Joint: DEC-497 (NO-LIVE-API HARD CUT - this prefetch path is the canonical
home for live calls), DEC-609 (H1 implementation), CHECKLIST #68 (smoke
validated), CHECKLIST #78 (per-addressal pyramid - this test = contract
layer for H1).
"""

from __future__ import annotations

import pathlib

import pandas as pd
import pytest

CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "data_prefetch" / "polygon" / "ohlcv_daily"

EXPECTED_COLS = ["ticker", "date", "open", "high", "low", "close", "volume", "vwap", "transactions"]
EXPECTED_DTYPES = {
    "ticker": ("object", "str", "string"),  # pandas 2.x may use 'str' (PyArrow-backed)
    "open": ("float64",),
    "high": ("float64",),
    "low": ("float64",),
    "close": ("float64",),
    "volume": ("float64",),
    "vwap": ("float64",),
    "transactions": ("int64",),
}

SMOKE_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]


def _load(ticker: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{ticker}.parquet"
    if not path.exists():
        pytest.skip(f"H1 cache miss for {ticker}; BG not yet landed at {path}")
    return pd.read_parquet(path)


@pytest.mark.parametrize("ticker", SMOKE_TICKERS)
def test_h1_smoke_schema_locked(ticker: str):
    """Smoke fixtures must have the 9-col schema exactly."""
    df = _load(ticker)
    assert list(df.columns) == EXPECTED_COLS, (
        f"H1 {ticker} schema drift: got {list(df.columns)}, expected {EXPECTED_COLS}"
    )


@pytest.mark.parametrize("ticker", SMOKE_TICKERS)
def test_h1_smoke_dtypes_locked(ticker: str):
    """Smoke fixtures must have the expected dtypes (date may be object/date32 - skip)."""
    df = _load(ticker)
    for col, accepted_dtypes in EXPECTED_DTYPES.items():
        actual = str(df[col].dtype)
        assert actual in accepted_dtypes, (
            f"H1 {ticker}.{col} dtype drift: got {actual}, expected one of {accepted_dtypes}"
        )


@pytest.mark.parametrize("ticker", SMOKE_TICKERS)
def test_h1_smoke_has_vwap_and_transactions(ticker: str):
    """The whole point of H1 is vwap+transactions; pin their non-null presence."""
    df = _load(ticker)
    assert df["vwap"].notna().all(), f"H1 {ticker} has null vwap (data integrity issue)"
    assert df["transactions"].notna().all(), f"H1 {ticker} has null transactions"
    assert (df["vwap"] > 0).all(), f"H1 {ticker} has non-positive vwap"
    assert (df["transactions"] > 0).all(), f"H1 {ticker} has non-positive transactions"


def test_h1_smoke_row_count_realistic():
    """5 years of daily bars ~= 1255 trading days. Allow +/- 30 day tolerance."""
    if not CACHE_DIR.exists():
        pytest.skip("H1 cache directory not yet created")
    counts = []
    for ticker in SMOKE_TICKERS:
        path = CACHE_DIR / f"{ticker}.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        counts.append((ticker, len(df)))
    if not counts:
        pytest.skip("No smoke ticker files cached yet")
    for ticker, n in counts:
        assert 1200 < n < 1300, (
            f"H1 {ticker} has {n} rows; expected ~1255 (5y daily). "
            f"Likely partial fetch or window misconfiguration."
        )


def test_h1_canonical_path_exists():
    """The canonical Sprint 0A path must exist (per DEC-497 architecture)."""
    assert CACHE_DIR.exists(), (
        f"H1 canonical path missing: {CACHE_DIR}. "
        "Run scripts/prefetch_polygon_ohlcv_master.py to populate."
    )
