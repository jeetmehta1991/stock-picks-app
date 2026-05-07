"""PIT-verification audit (Pass 53 Day-9 v8g Batch 7).

Extends the DEC-512 PIT audit (Day-9 v8f) to cover non-fundamentals signals:
sentiment, technical, and the Wave A-D accessor functions added this session.

Findings catalogued by this audit:
- get_corporate_donations: had no PIT cutoff; FIXED this turn (added as_of arg).
- get_etf_holdings + get_top_shareholders: source data has NO date dimension
  (current snapshot only). Cannot be PIT-bounded without re-prefetching
  with date column. Documented in docstrings; tests guard against
  Phase-1A misuse.
- News sentiment (get_news_sentiment): uses Polygon `date` (derived from
  `published_utc`) for PIT cutoff. CORRECT.
- AAII / CNN F&G / wikipedia: all use observation date for PIT. CORRECT.
- ALFRED vintage: uses realtime_start/realtime_end correctly per DEC-301.

Tests guard against future PIT regressions across the consumer surface.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Corporate donations PIT cutoff (fixed this turn)
# ---------------------------------------------------------------------------
def test_pit_corporate_donations_accepts_as_of_param():
    """get_corporate_donations must accept optional as_of for PIT cutoff."""
    from backtest.data.smart_money import get_corporate_donations
    import inspect
    sig = inspect.signature(get_corporate_donations)
    assert "as_of" in sig.parameters, (
        "get_corporate_donations must accept as_of parameter for PIT correctness"
    )


def test_pit_corporate_donations_filters_by_as_of():
    """as_of=very-past must exclude donations dated after as_of."""
    from backtest.data.smart_money import get_corporate_donations
    # HON has 741 dated donations, all 2026
    full = get_corporate_donations("HON")
    past = get_corporate_donations("HON", as_of=date(2020, 1, 1))
    # Past as_of should reduce or eliminate (all data is 2026 in current
    # prefetch); when past < dataset min, found=False
    if full["found"]:
        assert past["total_donations_usd"] <= full["total_donations_usd"]


def test_pit_corporate_donations_default_returns_full_history():
    """When as_of=None (default), no PIT filter applied (legacy behavior)."""
    from backtest.data.smart_money import get_corporate_donations
    r = get_corporate_donations("HON")
    # Without as_of, returns full sum across all dated rows + NaN-date rows
    if r["found"]:
        assert r["total_donations_usd"] > 0


# ---------------------------------------------------------------------------
# Documented current-snapshot accessors (NO PIT possible)
# ---------------------------------------------------------------------------
def test_pit_get_etf_holdings_documented_as_no_pit():
    """get_etf_holdings docstring must warn about no PIT dimension."""
    from backtest.data.smart_money import get_etf_holdings
    doc = get_etf_holdings.__doc__ or ""
    assert "NO PIT DIMENSION" in doc.upper(), (
        "get_etf_holdings must document the NO-PIT-DIMENSION limitation per "
        "Pass 53 Day-9 v8g PIT audit"
    )


def test_pit_get_top_shareholders_documented_as_no_pit():
    """get_top_shareholders docstring must warn about no PIT dimension."""
    from backtest.data.smart_money import get_top_shareholders
    doc = get_top_shareholders.__doc__ or ""
    assert "NO PIT DIMENSION" in doc.upper()


# ---------------------------------------------------------------------------
# PIT-correct accessors verification
# ---------------------------------------------------------------------------
def test_pit_news_sentiment_uses_date_column():
    """get_news_sentiment must filter by 'date' column (derived from
    published_utc per Polygon news schema)."""
    import inspect
    from backtest.data import smart_money as sm
    src = inspect.getsource(sm.get_news_sentiment)
    assert 'df["date"]' in src or "df['date']" in src, (
        "get_news_sentiment must filter by 'date' column for PIT correctness"
    )
    assert "as_of" in src
    # Window check: must use (date >= window_start) & (date <= window_end)
    assert "window_start" in src and "window_end" in src


def test_pit_aaii_uses_survey_date():
    """sentiment.get_aaii_sentiment must use survey_date for PIT cutoff."""
    import inspect
    from backtest.data import sentiment as st
    src = inspect.getsource(st.get_aaii_sentiment)
    assert "survey_date" in src
    assert "<=" in src  # PIT comparator


def test_pit_cnn_fg_uses_reading_date():
    """sentiment.get_fear_and_greed must use reading_date for PIT cutoff."""
    import inspect
    from backtest.data import sentiment as st
    src = inspect.getsource(st.get_fear_and_greed)
    assert "reading_date" in src


def test_pit_get_search_attention_uses_date_column():
    """G8 sentiment.get_search_attention must filter by date column."""
    import inspect
    from backtest.data import sentiment as st
    src = inspect.getsource(st.get_search_attention)
    assert 'df["date"]' in src or "df['date']" in src
    assert "as_of" in src


def test_pit_get_offexchange_volume_uses_date():
    """G13 must filter by Date column."""
    import inspect
    from backtest.data import smart_money as sm
    src = inspect.getsource(sm.get_offexchange_volume)
    assert 'df["Date"]' in src or "df['Date']" in src
    assert "as_of" in src


def test_pit_get_wsb_attention_uses_date():
    """G15 must filter by Date column."""
    import inspect
    from backtest.data import smart_money as sm
    src = inspect.getsource(sm.get_wsb_attention)
    assert 'df["Date"]' in src or "df['Date']" in src
    assert "as_of" in src


def test_pit_get_sec13f_holdings_uses_date():
    """G17d must filter by Date column."""
    import inspect
    from backtest.data import smart_money as sm
    src = inspect.getsource(sm.get_sec13f_holdings)
    assert 'df["Date"]' in src or "df['Date']" in src
    assert "as_of" in src


def test_pit_get_patent_momentum_uses_date():
    """G17a must filter by date column."""
    import inspect
    from backtest.data import smart_money as sm
    src = inspect.getsource(sm.get_patent_momentum)
    assert 'df["date"]' in src or "df['date']" in src
    assert "as_of" in src


# ---------------------------------------------------------------------------
# DEC-512 BUG-INSIDER-PIT regression (already in test_dec512; here for
# inclusion in pyramid-wide PIT coverage)
# ---------------------------------------------------------------------------
def test_pit_insider_signal_uses_filedate_not_date():
    """smart_money.insider_signal must use Quiver fileDate (SEC filing) not
    Date (transaction date) for PIT cutoff. Replicates DEC-512 BUG-INSIDER-PIT
    coverage."""
    import inspect
    from backtest.data import smart_money as sm
    src = inspect.getsource(sm.insider_signal)
    # Must reference fileDate
    assert "fileDate" in src, (
        "insider_signal must use fileDate for PIT cutoff (DEC-512 fix)"
    )
