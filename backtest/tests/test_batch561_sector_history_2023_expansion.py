"""Batch 561 (2026-06-02) -- sector_history.csv expansion for the
2023-03-17 GICS reclassification batch.

Source: per CHECKLIST #77, owner directive 2026-06-02 "Execute"
in response to B557 C-DATA owner-gated queue entry.
Queue: C-DATA (Phase 1A-beta producer-zero classification cluster).

Owner directive: laptop-local data work; cross-verify across multiple
sources before commit. B561 cross-verified the 14-name 2023-03-17
batch across:
  - S&P DJI Indexology Blog (2023-02-03)
  - LSEG Lipper Alpha 2023-03 commentary
  - Yahoo Finance, ETF Strategy, Zacks Nasdaq 2023-03-17 coverage
  - 2026-06-02 web search returned 5+ independent sources confirming
    the same 14-name list (no source dispute).

Expansion adds all 14 of 14 names. Batch 561a follow-on (2026-06-02)
fetched FLT.parquet from Polygon (706 rows 2021-06-03 to 2024-03-22,
the pre-CPAY-rename window) via `scripts/fetch_flt_one_time_b561.py`
and restored the FLT row pair in sector_history.csv.

Pins:

  (1) sector_history.csv has 13 distinct 2023-03-17 tickers in the
      added_date >= 2021-01-01 window.
  (2) For each of the 13 tickers, producer emits a non-empty signal
      dict at as_of 2023-04-01 (within 90-day window of 2023-03-17
      reclassification).
  (3) IT -> Financials cohort (7 tickers): emits
      classification_change_from_tech = True (mirrors the V/MA pin in
      B557).
  (4) IT -> Industrials cohort (3 tickers): emits from_tech = True,
      to_tech = False, to_defensive = False (Industrials is neither
      growth nor defensive bucket).
  (5) Consumer Discretionary -> Consumer Staples cohort (3 tickers):
      emits to_defensive = True, from_tech = False.
  (6) Each row pair (old-sector + new-sector) preserves the schema
      (prior_sector lookup works via removed_date matching).
  (7) Window expiry: each new ticker returns empty dict at as_of
      2023-07-01 (>90 days post 2023-03-17).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest


SECTOR_HISTORY_CSV = (
    Path(__file__).parent.parent.parent
    / "Backtesting universe" / "sector_history.csv"
)


# Cohort definitions (from S&P DJI 2023-03-17 batch, cross-verified)
IT_TO_FINANCIALS_2023 = [
    "V", "MA", "PYPL", "FISV", "FIS", "GPN", "JKHY",
    "FLT",  # B561a follow-on: restored after FLT.parquet prefetch
]
IT_TO_INDUSTRIALS_2023 = ["ADP", "PAYX", "BR"]
CONS_DISC_TO_STAPLES_2023 = ["TGT", "DG", "DLTR"]
ALL_2023_TICKERS = (
    IT_TO_FINANCIALS_2023
    + IT_TO_INDUSTRIALS_2023
    + CONS_DISC_TO_STAPLES_2023
)


@pytest.fixture(autouse=True)
def reload_sector_history():
    """sector_history.csv is module-level cached in universe.py.
    Reload to pick up CSV changes between test runs."""
    import importlib
    import backtest.data.universe as u
    importlib.reload(u)
    yield


def test_batch561_thirteen_2023_tickers_present_in_csv():
    """All 13 ticker pairs (old-sector + new-sector rows) present in
    sector_history.csv post-expansion."""
    df = pd.read_csv(SECTOR_HISTORY_CSV, comment="#")
    df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce")
    df["removed_date"] = pd.to_datetime(df["removed_date"], errors="coerce")
    # Filter to 2023-03-17 cohort
    added_2023 = df[df["added_date"] == "2023-03-17"]
    syms_added = set(added_2023["Symbol"].tolist())
    assert syms_added == set(ALL_2023_TICKERS), (
        f"2023-03-17 added rows: {syms_added} vs expected {set(ALL_2023_TICKERS)}"
    )
    # Also verify the symmetric removed-date rows exist (old sector
    # rows must match for prior_sector lookup)
    removed_2023 = df[df["removed_date"] == "2023-03-17"]
    syms_removed = set(removed_2023["Symbol"].tolist())
    assert syms_removed == set(ALL_2023_TICKERS), (
        f"2023-03-17 removed rows: {syms_removed} vs expected "
        f"{set(ALL_2023_TICKERS)} (each reclassification needs a "
        f"removed-row for prior_sector to resolve)"
    )


def test_batch561_producer_emits_for_all_13_tickers():
    """Each of the 13 new tickers emits a non-empty signal dict at
    as_of 2023-04-01 (within 90-day window)."""
    from backtest.data.universe import get_classification_change_signals
    for ticker in ALL_2023_TICKERS:
        out = get_classification_change_signals(ticker, date(2023, 4, 1))
        assert out, f"{ticker} should emit non-empty dict at 2023-04-01"
        assert out["classification_changed_recent"] is True
        assert out["days_since_classification_change"] == 15


def test_batch561_it_to_financials_cohort_from_tech_true():
    """7 IT -> Financials tickers: from_tech=True (matches V/MA pin
    in B557)."""
    from backtest.data.universe import get_classification_change_signals
    for ticker in IT_TO_FINANCIALS_2023:
        out = get_classification_change_signals(ticker, date(2023, 4, 1))
        assert out["prior_sector"] == "Information Technology"
        assert out["new_sector"] == "Financials"
        assert out["classification_change_from_tech"] is True
        assert out["classification_change_to_tech"] is False
        # Financials is neither growth nor defensive bucket
        assert out["classification_change_to_defensive"] is False


def test_batch561_it_to_industrials_cohort():
    """3 IT -> Industrials tickers: from_tech=True, to_tech=False,
    to_defensive=False (Industrials is neither bucket)."""
    from backtest.data.universe import get_classification_change_signals
    for ticker in IT_TO_INDUSTRIALS_2023:
        out = get_classification_change_signals(ticker, date(2023, 4, 1))
        assert out["prior_sector"] == "Information Technology"
        assert out["new_sector"] == "Industrials"
        assert out["classification_change_from_tech"] is True
        assert out["classification_change_to_tech"] is False
        assert out["classification_change_to_defensive"] is False


def test_batch561_cons_disc_to_staples_cohort():
    """3 Consumer Discretionary -> Consumer Staples tickers:
    to_defensive=True (Consumer Staples is in defensive bucket),
    from_tech=False."""
    from backtest.data.universe import get_classification_change_signals
    for ticker in CONS_DISC_TO_STAPLES_2023:
        out = get_classification_change_signals(ticker, date(2023, 4, 1))
        assert out["prior_sector"] == "Consumer Discretionary"
        assert out["new_sector"] == "Consumer Staples"
        assert out["classification_change_to_defensive"] is True
        assert out["classification_change_from_tech"] is False
        assert out["classification_change_to_tech"] is False


def test_batch561_window_expiry_at_91_days():
    """At as_of 2023-06-17 (92 days post-reclassification), all 13
    tickers' signal expires (lookback_days=90 default)."""
    from backtest.data.universe import get_classification_change_signals
    for ticker in ALL_2023_TICKERS:
        out = get_classification_change_signals(ticker, date(2023, 6, 17))
        assert out == {}, (
            f"{ticker} signal should expire by 2023-06-17 (92d "
            f"post-event > 90d window); got {out}"
        )


def test_batch561a_flt_restored_with_parquet():
    """B561a follow-on: FLT.parquet was fetched + FLT row pair restored
    in sector_history.csv. Verify both invariants."""
    df = pd.read_csv(SECTOR_HISTORY_CSV, comment="#")
    syms = set(df["Symbol"].tolist())
    assert "FLT" in syms, (
        "FLT row pair should be present post-B561a follow-on"
    )
    # FLT.parquet must exist with pre-2024-03-25 history
    flt_parquet = (
        SECTOR_HISTORY_CSV.parent.parent
        / "data_prefetch" / "polygon" / "ohlcv_daily" / "FLT.parquet"
    )
    assert flt_parquet.exists(), (
        f"FLT.parquet must exist at {flt_parquet} per B561a; if missing, "
        f"re-run scripts/fetch_flt_one_time_b561.py"
    )
    flt_df = pd.read_parquet(flt_parquet)
    flt_df["date"] = pd.to_datetime(flt_df["date"])
    # FLT pre-rename data should end on/around 2024-03-22 (last FLT
    # trading day before CPAY rename on 2024-03-25)
    last_date = flt_df["date"].max()
    assert last_date.year == 2024 and last_date.month <= 3, (
        f"FLT.parquet last date {last_date} -- expected pre-CPAY-rename "
        f"(March 2024 or earlier)"
    )


def test_batch561_existing_2018_events_preserved():
    """Pre-existing 2018-09-24 Communication Services creation event
    rows must NOT be altered by the B561 expansion."""
    df = pd.read_csv(SECTOR_HISTORY_CSV, comment="#")
    df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce")
    df["removed_date"] = pd.to_datetime(df["removed_date"], errors="coerce")
    events_2018 = df[
        (df["added_date"] == "2018-09-24")
        | (df["removed_date"] == "2018-09-24")
    ]
    # 8 tickers x 2 rows each = 16 rows for the 2018-09-24 event
    assert len(events_2018) == 16, (
        f"expected 16 rows for 2018-09-24 event (8 tickers x 2 rows); "
        f"got {len(events_2018)}"
    )
    syms_2018 = set(events_2018["Symbol"].tolist())
    expected_2018 = {"META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA",
                     "T", "VZ"}
    assert syms_2018 == expected_2018, (
        f"2018-09-24 tickers: {syms_2018} vs expected {expected_2018}"
    )
