"""Schema regression test - Tier J4 (Pass 53 Day-9 v8h+1 owner-mandated 2026-05-08).

Owner directive: 'all data in prefetch needs to be standardized and normalized'.

For each high-volume cache directory, the canonical column set is locked from
empirical observation (51,300+ parquets across 20 dirs, all 1-schema CONSISTENT
as of 2026-05-08). Any future write that drifts from this schema must:
  (a) update CANONICAL_SCHEMAS here AND
  (b) be approved as an intentional schema change (not silent prefetch-script bug)

This test catches: prefetch script writing extra/missing columns, API field
rename silently propagating into cache, incomplete migration touching some
files but not others.

Source: derived 2026-05-08 v8h+1 via stratified scan
(see commit `de3dc1a9d` predecessor work).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# Empirically-locked schemas - DO NOT EDIT WITHOUT APPROVAL.
# Each value: frozenset of expected column names (order-independent).
CANONICAL_SCHEMAS: dict[str, frozenset[str]] = {
    # Polygon corporate-actions full prefetch (Pass 53 H3)
    "data_prefetch/polygon/splits_full": frozenset({
        "execution_date", "id", "split_from", "split_to", "ticker",
    }),
    "data_prefetch/polygon/dividends_full": frozenset({
        "cash_amount", "currency", "declaration_date", "dividend_type",
        "ex_dividend_date", "frequency", "id", "pay_date", "record_date", "ticker",
    }),
    "data_prefetch/polygon/ipos_full": frozenset({
        "announced_date", "currency_code", "final_issue_price", "highest_offer_price",
        "ipo_status", "isin", "issuer_name", "last_updated", "listing_date",
        "lot_size", "lowest_offer_price", "max_shares_offered", "min_shares_offered",
        "primary_exchange", "security_description", "security_type",
        "shares_outstanding", "ticker", "total_offer_size", "us_code",
    }),

    # OHLCV (yfinance prefetch + Polygon refresh)
    "backtest/data/cache/ohlcv": frozenset({
        "close", "date", "high", "low", "open", "volume",
    }),

    # Quiver (Trader plan, full re-prefetch Pass 53)
    "data_prefetch/quiver/congressional": frozenset({
        "Amount", "BioGuideID", "Description", "ExcessReturn", "House", "Party",
        "PriceChange", "Range", "ReportDate", "Representative", "SPYChange",
        "Ticker", "TickerType", "Transaction", "TransactionDate", "last_modified",
    }),
    "data_prefetch/quiver/gov_contracts": frozenset({
        "Amount", "Qtr", "Ticker", "Year",
    }),
    "data_prefetch/quiver/insider": frozenset({
        "AcquiredDisposedCode", "Date", "Name", "PricePerShare", "Shares",
        "SharesOwnedFollowing", "Ticker", "TransactionCode",
        "directOrIndirectOwnership", "fileDate", "isDirector", "isOfficer",
        "isOther", "isTenPercentOwner", "officerTitle", "uploaded",
    }),
    "data_prefetch/quiver/institutional": frozenset({
        "Class", "Date", "Direction", "Fund", "Name", "Put/Call",
        "ReportPeriod", "SH/PRN", "Shares", "Ticker", "Value",
    }),
    "data_prefetch/quiver/lobbying": frozenset({
        "Amount", "Client", "Date", "Issue", "Registrant",
        "Specific_Issue", "Ticker",
    }),
    "data_prefetch/quiver/wallstreetbets": frozenset({
        "Date", "Mentions", "Rank", "Sentiment", "Ticker",
    }),
    "data_prefetch/quiver/housetrading": frozenset({
        "Amount", "BioGuideID", "Date", "Range", "Representative",
        "Ticker", "Transaction", "last_modified",
    }),
    "data_prefetch/quiver/senatetrading": frozenset({
        "Amount", "BioGuideID", "Date", "Range", "Senator",
        "Ticker", "Transaction", "last_modified",
    }),
    "data_prefetch/quiver/spacs": frozenset({
        "Date", "Mentions", "Rank", "Sentiment", "Ticker",
    }),
    "data_prefetch/quiver/topshareholders": frozenset({
        "ownership", "ownership_options",
    }),

    # Polygon fundamentals (Pass 53 H1)
    "data_prefetch/polygon/financials": frozenset({
        "cik", "company_name", "end_date", "filing_date", "financials_json",
        "fiscal_period", "fiscal_year", "period_of_report_date",
        "source_filing_url", "start_date", "ticker",
    }),

    # Polygon indicators (Pass 53 H6)
    "data_prefetch/polygon/indicators/ema_20": frozenset({"date", "value"}),
    "data_prefetch/polygon/indicators/ema_50": frozenset({"date", "value"}),
    "data_prefetch/polygon/indicators/sma_50": frozenset({"date", "value"}),
    "data_prefetch/polygon/indicators/sma_200": frozenset({"date", "value"}),
    "data_prefetch/polygon/indicators/rsi_14": frozenset({"date", "value"}),

    # Polygon Benzinga partner endpoints
    "data_prefetch/polygon/benzinga/analyst_insights": frozenset({
        "benzinga_firm_id", "benzinga_id", "benzinga_rating_id", "company_name",
        "date", "firm", "insight", "last_updated", "price_target", "rating",
        "rating_action", "ticker",
    }),

    # Finnhub
    "data_prefetch/finnhub/company_news": frozenset({
        "category", "datetime", "headline", "id", "image",
        "related", "source", "summary", "url",
    }),
    "data_prefetch/finnhub/earnings": frozenset({
        "actual", "estimate", "period", "quarter",
        "surprise", "surprisePercent", "symbol", "year",
    }),
}


# Sample budget - cap per-dir to keep test fast (full check still ~3-5 sec).
SAMPLE_BUDGET = 25


def _audit_dir(dir_path: Path, expected: frozenset[str]) -> tuple[int, int, list[str]]:
    """Returns (non_empty_checked, drift_count, drift_examples)."""
    files = sorted(dir_path.glob("*.parquet"))
    non_empty_checked = 0
    drift_count = 0
    drift_examples: list[str] = []

    for f in files:
        if non_empty_checked >= SAMPLE_BUDGET:
            break
        try:
            df = pd.read_parquet(f)
        except Exception:
            continue
        if df.empty:
            continue
        non_empty_checked += 1
        actual = frozenset(df.columns)
        if actual != expected:
            drift_count += 1
            if len(drift_examples) < 3:
                missing = expected - actual
                extra = actual - expected
                drift_examples.append(
                    f"{f.name}: missing={sorted(missing)} extra={sorted(extra)}"
                )

    return non_empty_checked, drift_count, drift_examples


@pytest.mark.parametrize("rel_dir,expected", sorted(CANONICAL_SCHEMAS.items()))
def test_canonical_schema(rel_dir: str, expected: frozenset[str]) -> None:
    dir_path = REPO_ROOT / rel_dir
    if not dir_path.is_dir():
        pytest.skip(f"{rel_dir} not present (cache may be on another machine)")

    non_empty, drift, examples = _audit_dir(dir_path, expected)
    if non_empty == 0:
        pytest.skip(f"{rel_dir} has no non-empty parquets in first {SAMPLE_BUDGET}")

    assert drift == 0, (
        f"{rel_dir}: {drift}/{non_empty} sampled parquets have schema drift.\n"
        f"Expected columns: {sorted(expected)}\n"
        f"Examples:\n  " + "\n  ".join(examples) + "\n"
        f"Action: either fix the prefetch script that wrote bad files OR update "
        f"CANONICAL_SCHEMAS in this test if the schema change is intentional."
    )
