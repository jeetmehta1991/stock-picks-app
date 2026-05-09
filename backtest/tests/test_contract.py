"""Contract tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Contract = our parser code handles the actual response shape that the
external API returns. Catches "API silently changed shape, our parser
silently broke" failures.

We test against frozen mock fixtures that mirror real API responses we have
captured. When an API actually changes (e.g. Polygon adds a new field), the
fix is: refresh the fixture + update the parser if needed.

Markers:
    pytest -m contract
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


pytestmark = pytest.mark.contract


# -- Contract 1: Polygon dividends response shape -----------------------
def test_contract_polygon_dividends_shape() -> None:
    """Polygon /v3/reference/dividends results have 10 fixed fields
    (verified 2026-05-08 against current Polygon docs + cached files)."""
    sample_dir = REPO_ROOT / "data_prefetch" / "polygon" / "dividends_full"
    if not sample_dir.is_dir():
        pytest.skip("dividends_full cache not present")
    sample = next(sample_dir.glob("AAPL.parquet"), None)
    if sample is None:
        sample = next(sample_dir.glob("*.parquet"))
    df = pd.read_parquet(sample)
    if df.empty:
        pytest.skip("sample empty")
    expected = {"cash_amount", "currency", "declaration_date", "dividend_type",
                "ex_dividend_date", "frequency", "id", "pay_date",
                "record_date", "ticker"}
    assert set(df.columns) == expected, (
        f"Polygon dividends contract drift. Expected {expected}; got "
        f"{set(df.columns)}. Either API changed (refresh fixture) or our "
        f"parser dropped/added fields."
    )


# -- Contract 2: Quiver congressional shape -----------------------------
def test_contract_quiver_congressional_shape() -> None:
    """Quiver historical/congressional has 16 fixed fields."""
    sample_dir = REPO_ROOT / "data_prefetch" / "quiver" / "congressional"
    if not sample_dir.is_dir():
        pytest.skip("quiver/congressional not present")
    sample = next((p for p in sample_dir.glob("*.parquet") if p.stat().st_size > 1000), None)
    if sample is None:
        pytest.skip("no non-empty sample")
    df = pd.read_parquet(sample)
    expected = {"Amount", "BioGuideID", "Description", "ExcessReturn", "House",
                "Party", "PriceChange", "Range", "ReportDate", "Representative",
                "SPYChange", "Ticker", "TickerType", "Transaction",
                "TransactionDate", "last_modified"}
    assert set(df.columns) == expected, (
        f"Quiver congressional contract drift; got {set(df.columns)}"
    )


# -- Contract 3: Finnhub earnings shape ---------------------------------
def test_contract_finnhub_earnings_shape() -> None:
    sample_dir = REPO_ROOT / "data_prefetch" / "finnhub" / "earnings"
    if not sample_dir.is_dir():
        pytest.skip("finnhub/earnings not present")
    sample = next((p for p in sample_dir.glob("*.parquet") if p.stat().st_size > 1000), None)
    if sample is None:
        pytest.skip("no non-empty sample")
    df = pd.read_parquet(sample)
    expected = {"actual", "estimate", "period", "quarter",
                "surprise", "surprisePercent", "symbol", "year"}
    assert set(df.columns) == expected, (
        f"Finnhub earnings contract drift; got {set(df.columns)}"
    )


# -- Contract 4: Polygon options chain reference shape ------------------
def test_contract_polygon_options_chain_shape() -> None:
    """Polygon /v3/reference/options/contracts results."""
    sample_dir = REPO_ROOT / "data_prefetch" / "polygon" / "options_chains"
    if not sample_dir.is_dir():
        pytest.skip("options_chains not present")
    sample = next((p for p in sample_dir.glob("*.parquet") if p.stat().st_size > 1000), None)
    if sample is None:
        pytest.skip("no non-empty sample")
    df = pd.read_parquet(sample)
    must_have = {"cfi", "contract_type", "exercise_style", "expiration_date",
                 "primary_exchange", "shares_per_contract", "strike_price",
                 "ticker", "underlying_ticker"}
    missing = must_have - set(df.columns)
    assert not missing, (
        f"Polygon options/contracts missing fields: {missing}; got {set(df.columns)}"
    )


# -- Contract 5: SEC EDGAR per-form shape -------------------------------
def test_contract_sec_edgar_form_shape() -> None:
    sample_dir = REPO_ROOT / "data_prefetch" / "sec_edgar" / "10_K"
    if not sample_dir.is_dir():
        pytest.skip("sec_edgar/10_K not present")
    sample = next((p for p in sample_dir.glob("*.parquet") if p.stat().st_size > 200), None)
    if sample is None:
        pytest.skip("no non-empty sample")
    df = pd.read_parquet(sample)
    expected = {"ticker", "cik", "form", "filing_date",
                "accession_number", "primary_doc"}
    missing = expected - set(df.columns)
    assert not missing, f"SEC EDGAR 10-K contract drift; missing {missing}"


# -- Contract 6: AAII extended sentiment shape --------------------------
def test_contract_aaii_extended_sentiment_shape() -> None:
    p = REPO_ROOT / "data_prefetch" / "aaii" / "weekly_sentiment.parquet"
    if not p.exists():
        pytest.skip("AAII parquet not present")
    df = pd.read_parquet(p)
    must_have = {"date", "bullish", "neutral", "bearish",
                 "bull_bear_spread", "bullish_8wk_ma"}
    missing = must_have - set(df.columns)
    assert not missing, f"AAII sentiment contract drift; missing {missing}"


# -- Contract 7: Polygon news insights_json preserved (INV-027) ---------
def test_contract_polygon_news_insights_json_preserved() -> None:
    """INV-027 RESOLVED 2026-05-08 v8h+1: Polygon news cache must preserve
    the per-ticker insights array as JSON-encoded `insights_json` column.
    Regression: any future re-prefetch that drops this field re-introduces
    the per-ticker-sentiment-loss bug."""
    sample_dir = REPO_ROOT / "data_prefetch" / "polygon" / "news"
    if not sample_dir.is_dir():
        pytest.skip("polygon/news cache not present")
    sample = sample_dir / "AAPL.parquet"
    if not sample.exists():
        sample = next((p for p in sample_dir.glob("*.parquet") if p.stat().st_size > 1000), None)
    if sample is None:
        pytest.skip("no non-empty Polygon news sample")
    df = pd.read_parquet(sample)
    assert "insights_json" in df.columns, (
        f"polygon news {sample.name} missing 'insights_json' column "
        f"- INV-027 regression. Re-prefetch needed with current "
        f"scripts/prefetch_polygon_news.py."
    )


# -- Contract 8: AUDIT_INDEX table row shape ----------------------------
def test_contract_audit_index_row_shape() -> None:
    """Each | **DECISION-NNN** row in AUDIT_INDEX must have at least the
    minimum column set parse_decisions expects."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from build_dashboard_stage_2 import parse_decisions
    except ImportError:
        pytest.skip("dashboard module not importable")
    decs = parse_decisions(REPO_ROOT / "AUDIT_INDEX.md")
    if not decs:
        pytest.skip("AUDIT_INDEX produced no decisions")
    # Every parsed decision must have id + title + status fields populated
    for d in decs[:50]:
        assert d.get("id"), f"decision missing id: {d}"
        assert "title" in d, f"decision missing title field: {d}"
        assert "status" in d, f"decision missing status field: {d}"
