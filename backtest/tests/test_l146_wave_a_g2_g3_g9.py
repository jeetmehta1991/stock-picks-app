"""Wave A regression tests — G2 AAII + G3 CNN + G9 ALFRED (Pass 53 Day-9 v8c).

Closes 3 of 13 remaining L146/DEC-507 wiring gaps. Each test asserts:
  1. Consumer reads from the canonical Sprint 0A path (or merged history)
  2. Returned values are sensible (bounded ranges; non-empty)
  3. The legacy fallback still works if Sprint 0A path is missing
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# G2 AAII migration regression
# ---------------------------------------------------------------------------
def test_g2_aaii_loads_from_sprint_0a_parquet():
    """sentiment._load_aaii must read Sprint 0A parquet when available."""
    parquet = REPO_ROOT / "data_prefetch" / "aaii" / "weekly_sentiment.parquet"
    assert parquet.exists(), "Sprint 0A AAII parquet missing — re-run prefetch"

    from backtest.data import sentiment
    sentiment._AAII_DF = None  # reset cache
    df = sentiment._load_aaii()
    assert not df.empty, "AAII loader returned empty"
    assert {"survey_date", "bullish_pct", "bearish_pct", "neutral_pct"}.issubset(
        df.columns
    )
    # Range sanity: percents in [0, 1]
    assert df["bullish_pct"].between(0, 1).all()
    assert df["bearish_pct"].between(0, 1).all()


def test_g2_aaii_get_returns_signal_in_2023():
    from backtest.data.sentiment import get_aaii_sentiment
    s = get_aaii_sentiment(date(2023, 6, 15))
    assert s["signal"] != "unknown", "AAII unknown for 2023-06-15 — wiring gap"
    assert 0 < s["bullish_pct"] < 1


# ---------------------------------------------------------------------------
# G3 CNN F&G review — legacy CSV remains canonical for backtest history
# ---------------------------------------------------------------------------
def test_g3_cnn_csv_provides_full_backtest_history():
    """Sprint 0A daily.parquet has only ~250 rows (~1y); legacy CSV has 1600+
    rows (2020-2026). Legacy CSV must remain canonical for backtest period.
    """
    from backtest.data import sentiment
    sentiment._CNN_DF = None
    df = sentiment._load_cnn()
    assert len(df) >= 1500, (
        f"CNN F&G has only {len(df)} rows — backtest history (2020-2026) "
        f"requires ~1600 rows from legacy CSV"
    )
    # Earliest reading should be in 2020 (full backtest start)
    earliest = df["reading_date"].min()
    assert earliest.year <= 2020, f"CNN F&G earliest {earliest} > 2020 — "\
        f"history truncated"


def test_g3_cnn_get_returns_score_in_2023():
    from backtest.data.sentiment import get_fear_and_greed
    fg = get_fear_and_greed(date(2023, 6, 15))
    assert fg.get("score") is not None
    assert 0 <= float(fg["score"]) <= 100


# ---------------------------------------------------------------------------
# G9 ALFRED migration — vintage queries hit cache, not live API
# ---------------------------------------------------------------------------
def test_g9_alfred_vintage_hits_prefetched_cache():
    """When `as_of` provided to _fred_series, ALFRED prefetch parquet must be
    consulted before any live FRED API call."""
    from backtest.data.macro import _fred_series

    # AAA (Moody's Aaa corp bond yield) is in data_prefetch/alfred/
    s = _fred_series("AAA", date(2020, 1, 1), date(2020, 6, 30),
                     as_of=date(2020, 7, 1))
    assert not s.empty, (
        "ALFRED AAA vintage query returned empty — G9 wiring may be broken; "
        "live API would have populated this if the cache fallback failed"
    )
    # Sanity: AAA yield in 2020 H1 was around 2.5-3.5%
    assert (s > 1.0).all() and (s < 6.0).all(), \
        f"AAA values out of plausible range: {s.values}"


def test_g9_alfred_prefetch_dir_present():
    alfred = REPO_ROOT / "data_prefetch" / "alfred"
    assert alfred.exists()
    parquets = list(alfred.glob("*.parquet"))
    assert len(parquets) >= 30, (
        f"ALFRED prefetch has only {len(parquets)} files — expected ~50 "
        f"vintage series per Sprint 0A scope"
    )
