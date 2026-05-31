"""Batch 513 (2026-05-31) -- P15 FINRA short-interest fetcher tests.

Source: per CHECKLIST #77 + owner directive 2026-05-31 (P15 URL hunt
via web search).
Queue row: EXECUTION_QUEUE.md item P15.
Script: scripts/prefetch_finra_short_interest.py.
Producer: backtest/signals/short_interest.py (already shipped Batch 494).

Tests cover URL construction, biweekly date generation, parse logic
(against a synthetic pipe-delimited blob), repartition logic. No
network calls.
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# URL + UA pins
# ---------------------------------------------------------------------------

def test_batch513_url_pattern_matches_finra_cdn():
    from scripts.prefetch_finra_short_interest import FINRA_URL_PATTERN
    assert FINRA_URL_PATTERN == (
        "https://cdn.finra.org/equity/otcmarket/biweekly/shrt{yyyymmdd}.csv"
    )


def test_batch513_user_agent_has_contact_email():
    from scripts.prefetch_finra_short_interest import USER_AGENT
    assert "@" in USER_AGENT
    # SEC-style format (Name email@domain.com); FINRA is more lenient
    # but the same UA works on both.
    assert " " in USER_AGENT  # at least Name + email


def test_batch513_rate_limit_at_least_1_sec():
    from scripts.prefetch_finra_short_interest import RATE_LIMIT_SLEEP_SEC
    assert RATE_LIMIT_SLEEP_SEC >= 1.0  # polite for FINRA CDN


# ---------------------------------------------------------------------------
# Biweekly date generation
# ---------------------------------------------------------------------------

def test_batch513_biweekly_dates_15th_and_end_of_month():
    from scripts.prefetch_finra_short_interest import biweekly_dates
    dates = biweekly_dates(
        start=date(2026, 4, 1), end=date(2026, 5, 31)
    )
    expected = [
        date(2026, 4, 15), date(2026, 4, 30),
        date(2026, 5, 15), date(2026, 5, 31),
    ]
    assert dates == expected


def test_batch513_biweekly_dates_start_default_post_jun_2021():
    """Default start = 2021-06-15 per FINRA exchange-listed coverage note."""
    from scripts.prefetch_finra_short_interest import biweekly_dates
    dates = biweekly_dates(end=date(2021, 7, 31))
    assert dates[0] == date(2021, 6, 15)
    assert dates[1] == date(2021, 6, 30)


def test_batch513_biweekly_dates_handles_year_rollover():
    from scripts.prefetch_finra_short_interest import biweekly_dates
    dates = biweekly_dates(
        start=date(2025, 12, 1), end=date(2026, 1, 31),
    )
    assert date(2025, 12, 15) in dates
    assert date(2025, 12, 31) in dates
    assert date(2026, 1, 15) in dates
    assert date(2026, 1, 31) in dates


# ---------------------------------------------------------------------------
# CSV parse logic (against synthetic pipe-delimited)
# ---------------------------------------------------------------------------

def _synthetic_finra_csv() -> bytes:
    """Mimic the FINRA pipe-delimited schema with 2 rows."""
    header = "|".join((
        "accountingYearMonthNumber", "symbolCode", "issueName",
        "issuerServicesGroupExchangeCode", "marketClassCode",
        "currentShortPositionQuantity", "previousShortPositionQuantity",
        "stockSplitFlag", "averageDailyVolumeQuantity",
        "daysToCoverQuantity", "revisionFlag", "changePercent",
        "changePreviousNumber", "settlementDate",
    ))
    rows = [
        header,
        "202604|AAPL|Apple Inc.|NYSE|N|123456789|111111111|N|"
        "100000000|1.23|N|11.11|22222|2026-04-30",
        "202604|MSFT|Microsoft Corp.|NASDAQ|N|99999999|88888888|N|"
        "50000000|2.0|N|12.5|11111|2026-04-30",
    ]
    return "\n".join(rows).encode("utf-8")


def test_batch513_parse_finra_csv_extracts_ticker():
    from scripts.prefetch_finra_short_interest import parse_finra_csv
    df = parse_finra_csv(_synthetic_finra_csv())
    assert set(df["ticker"]) == {"AAPL", "MSFT"}


def test_batch513_parse_finra_csv_extracts_short_interest():
    from scripts.prefetch_finra_short_interest import parse_finra_csv
    df = parse_finra_csv(_synthetic_finra_csv())
    aapl = df[df["ticker"] == "AAPL"].iloc[0]
    assert aapl["short_interest"] == 123456789


def test_batch513_parse_finra_csv_extracts_avg_daily_volume():
    from scripts.prefetch_finra_short_interest import parse_finra_csv
    df = parse_finra_csv(_synthetic_finra_csv())
    msft = df[df["ticker"] == "MSFT"].iloc[0]
    assert msft["avg_daily_volume"] == 50000000


def test_batch513_parse_finra_csv_settlement_date_parsed_as_date():
    from scripts.prefetch_finra_short_interest import parse_finra_csv
    df = parse_finra_csv(_synthetic_finra_csv())
    for d in df["settlement_date"]:
        assert d == date(2026, 4, 30)


def test_batch513_parse_finra_csv_shares_outstanding_is_NA():
    """FINRA feed does NOT publish shares_outstanding; producer tolerates
    missing values (only short_interest_pct goes missing in output)."""
    from scripts.prefetch_finra_short_interest import parse_finra_csv
    df = parse_finra_csv(_synthetic_finra_csv())
    assert df["shares_outstanding"].isna().all()


# ---------------------------------------------------------------------------
# Repartition logic
# ---------------------------------------------------------------------------

def test_batch513_repartition_writes_per_ticker_parquets(tmp_path):
    from scripts.prefetch_finra_short_interest import (
        repartition_by_ticker, parse_finra_csv,
    )
    df1 = parse_finra_csv(_synthetic_finra_csv())
    manifest = repartition_by_ticker([df1], output_dir=tmp_path)
    assert "AAPL" in manifest
    assert "MSFT" in manifest
    assert (tmp_path / "AAPL.parquet").exists()
    assert (tmp_path / "MSFT.parquet").exists()


def test_batch513_repartition_dedupes_same_settlement_date(tmp_path):
    """Two snapshots with the same settlement_date for AAPL -> single
    row in output (drop_duplicates keep='last')."""
    from scripts.prefetch_finra_short_interest import (
        repartition_by_ticker, parse_finra_csv,
    )
    # Same date used in both; second snapshot wins
    df = parse_finra_csv(_synthetic_finra_csv())
    manifest = repartition_by_ticker([df, df], output_dir=tmp_path)
    assert manifest["AAPL"] == 1  # deduped


def test_batch513_repartition_writes_producer_schema(tmp_path):
    """Output parquets must have the 4 columns expected by
    `compute_short_interest_signals` from Batch 494."""
    from scripts.prefetch_finra_short_interest import (
        repartition_by_ticker, parse_finra_csv,
    )
    df = parse_finra_csv(_synthetic_finra_csv())
    repartition_by_ticker([df], output_dir=tmp_path)
    saved = pd.read_parquet(tmp_path / "AAPL.parquet")
    expected_cols = {"settlement_date", "short_interest",
                     "shares_outstanding", "avg_daily_volume"}
    assert set(saved.columns) == expected_cols


# ---------------------------------------------------------------------------
# Producer round-trip via existing Batch 494 module
# ---------------------------------------------------------------------------

def test_batch513_producer_round_trip_reads_fetched_parquet(tmp_path,
                                                              monkeypatch):
    """End-to-end: write a fetched-style parquet then call the Batch 494
    producer; it should emit short_interest signals."""
    from scripts.prefetch_finra_short_interest import (
        repartition_by_ticker, parse_finra_csv,
    )
    from backtest.signals.short_interest import (
        compute_short_interest_signals,
    )
    df = parse_finra_csv(_synthetic_finra_csv())
    repartition_by_ticker([df], output_dir=tmp_path)
    # Monkeypatch the producer's cache dir
    import backtest.signals.short_interest as mod
    monkeypatch.setattr(mod, "_SI_CACHE_DIR", tmp_path)
    out = compute_short_interest_signals("AAPL", date(2026, 5, 15))
    # short_interest_pct absent (shares_outstanding is NaN);
    # days_to_cover present (we have short_interest + avg_daily_volume)
    assert "days_to_cover" in out
    assert out["short_interest_observations"] == 1
