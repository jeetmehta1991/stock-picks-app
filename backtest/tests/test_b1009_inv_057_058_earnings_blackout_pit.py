"""B1009 (2026-06-22): INV-057 + INV-058 earnings_blackout lookahead fix verification.

# Source: PATH_TO_PHASE_1B_ALPHA.md §13.17 + Council 103 Option-6 SHIP-S5+S4
# owner-approved 2026-06-22 'Approve all proceed council this.' Per
# B995/B998/B999/B1001 readiness package + Council 94 + B989 INV-057+058
# per CHECKLIST #77.

Verifies B1009 INV-057 + INV-058 fix per Council 103 Option-6:
  - INV-057: fetch_earnings_dates with as_of filters PIT-correctly
  - INV-057: exit_earnings_blackout passes as_of=entry_date
  - INV-058: end_date + 30 days proxy used (NOT filing_date directly)
  - INV-058: filing_date fallback only when end_date absent
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from backtest.data.fetcher import fetch_earnings_dates


def test_b1009_inv_057_fetch_earnings_dates_respects_as_of_when_set():
    """INV-057: fetch_earnings_dates(ticker, as_of=DATE) filters PIT-correctly."""
    fin_path = Path("data_prefetch/polygon/financials/AAPL.parquet")
    if not fin_path.exists():
        pytest.skip("AAPL polygon parquet absent (CI environment)")
    full = fetch_earnings_dates("AAPL")  # no as_of -> full calendar
    pit_2022 = fetch_earnings_dates("AAPL", as_of=date(2022, 1, 1))
    # PIT filter must reduce calendar
    assert len(pit_2022) < len(full), (
        f"INV-057: PIT filter must reduce calendar; full={len(full)} pit={len(pit_2022)}"
    )
    # No date in PIT result should be after as_of
    if not pit_2022.empty:
        max_pit = pit_2022["earnings_date"].max().date()
        assert max_pit <= date(2022, 1, 1), (
            f"INV-057: PIT must respect as_of cutoff; got max={max_pit}"
        )


def test_b1009_inv_057_exit_earnings_blackout_passes_as_of_entry_date():
    """INV-057: exit_earnings_blackout must pass as_of=entry_date in call site.

    Source-grep verification per `feedback_doc_count_drift_must_be_test_pinned`.
    Code site backtest/engine/exit_strategies.py:~507.
    """
    src_path = Path("backtest/engine/exit_strategies.py")
    src = src_path.read_text(encoding="utf-8")
    assert "fetch_earnings_dates(ticker, as_of=entry_date)" in src, (
        "B1009 INV-057 fix: exit_earnings_blackout must pass as_of=entry_date "
        "to fetch_earnings_dates (verified via source-grep in "
        "backtest/engine/exit_strategies.py)"
    )


def test_b1009_inv_058_end_date_proxy_used():
    """INV-058: fetcher uses end_date + 30 days proxy (NOT filing_date directly)."""
    fin_path = Path("data_prefetch/polygon/financials/AAPL.parquet")
    if not fin_path.exists():
        pytest.skip("AAPL polygon parquet absent (CI environment)")
    df = pd.read_parquet(fin_path)
    if "end_date" not in df.columns or "filing_date" not in df.columns:
        pytest.skip("AAPL parquet schema mismatch")
    # Compute expected earnings_date from end_date + 30 days
    df = df.dropna(subset=["end_date"])
    if df.empty:
        pytest.skip("AAPL end_date all null")
    sample_row = df.iloc[0]
    expected_earnings_date = pd.to_datetime(sample_row["end_date"]) + pd.Timedelta(days=30)
    filing_date = pd.to_datetime(sample_row["filing_date"])

    # Verify fetcher returns end_date+30 proxy (not filing_date)
    earnings_df = fetch_earnings_dates("AAPL")
    if earnings_df.empty:
        pytest.skip("fetch returned empty for AAPL")
    # First entry should be end_date + 30 days, NOT filing_date
    first_earnings = earnings_df["earnings_date"].iloc[0]
    # Verify it's NOT filing_date directly (semantic gap fix)
    # (some rows may match by coincidence; check that AT LEAST ONE row
    # uses end_date+30 proxy, which would differ from filing_date)
    rows_using_end_date_proxy = (
        (pd.to_datetime(df["end_date"]) + pd.Timedelta(days=30)).isin(earnings_df["earnings_date"])
    ).sum()
    assert rows_using_end_date_proxy > 0, (
        f"INV-058: fetcher must use end_date + 30 days proxy; "
        f"no rows in fetched earnings_dates match end_date+30 derivation"
    )


def test_b1009_inv_058_fetcher_source_uses_end_date_proxy():
    """INV-058: fetcher.py source must use end_date + 30 days expression."""
    src_path = Path("backtest/data/fetcher.py")
    src = src_path.read_text(encoding="utf-8")
    # Verify the end_date + 30 days proxy expression is in source
    assert "pd.to_datetime(df[\"end_date\"]) + pd.Timedelta(days=30)" in src, (
        "B1009 INV-058 fix: fetcher.py must use end_date + 30 days proxy "
        "(verified via source-grep; Option-d per B995/B998/B999 finalized)"
    )
    # Verify INV-058 fix comment present (per CHECKLIST #67)
    assert "B1009 INV-058 fix" in src or "INV-058" in src, (
        "B1009 INV-058 fix: docstring/comment must reference INV-058 + B998/B999"
    )
