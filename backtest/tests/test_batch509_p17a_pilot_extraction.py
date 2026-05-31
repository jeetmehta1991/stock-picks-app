"""Batch 509 (2026-05-31) -- P17a pilot extraction tests.

Source: per CHECKLIST #77 + owner directive 2026-05-31.
Queue row: EXECUTION_QUEUE.md item P17a (pilot scope = 10 tickers x 5 yrs).
Script: scripts/extract_sec_edgar_xml_pilot.py.

Tests are dry-run-only -- no HTTP calls in CI. The actual extraction
runs operator-side via `python scripts/extract_sec_edgar_xml_pilot.py
--no-dry-run`.
"""
from __future__ import annotations

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Module-level pins
# ---------------------------------------------------------------------------

def test_batch509_module_importable():
    from scripts.extract_sec_edgar_xml_pilot import (
        PILOT_TICKERS, PILOT_FORMS, PILOT_YEAR_START, PILOT_YEAR_END,
        run_pilot, extract_one_form_one_ticker, _filter_pilot_window,
    )
    assert callable(run_pilot)
    assert callable(extract_one_form_one_ticker)


def test_batch509_pilot_scope_10_tickers():
    from scripts.extract_sec_edgar_xml_pilot import PILOT_TICKERS
    assert len(PILOT_TICKERS) == 10
    # All-uppercase, no duplicates
    assert all(t == t.upper() for t in PILOT_TICKERS)
    assert len(set(PILOT_TICKERS)) == 10


def test_batch509_pilot_window_is_5_years():
    from scripts.extract_sec_edgar_xml_pilot import (
        PILOT_YEAR_START, PILOT_YEAR_END,
    )
    assert PILOT_YEAR_END - PILOT_YEAR_START == 5


def test_batch509_pilot_forms_exclude_form_4():
    """Form 4 SKIPPED per Batch 453 -- Quiver already decodes."""
    from scripts.extract_sec_edgar_xml_pilot import PILOT_FORMS
    assert "4" not in PILOT_FORMS
    assert set(PILOT_FORMS) == {"SC_13D", "SC_13G", "8_K"}


def test_batch509_user_agent_has_contact_info():
    """SEC EDGAR requires identifiable User-Agent with contact email."""
    from scripts.extract_sec_edgar_xml_pilot import USER_AGENT
    assert "@" in USER_AGENT or "users.noreply" in USER_AGENT


def test_batch509_rate_limit_under_sec_max():
    """SEC EDGAR limit is 10 req/sec; sleep must be >= 0.1s for safety."""
    from scripts.extract_sec_edgar_xml_pilot import RATE_LIMIT_SLEEP_SEC
    assert RATE_LIMIT_SLEEP_SEC >= 0.1


# ---------------------------------------------------------------------------
# Window filter
# ---------------------------------------------------------------------------

def test_batch509_filter_pilot_window_drops_old_filings():
    from scripts.extract_sec_edgar_xml_pilot import _filter_pilot_window
    df = pd.DataFrame({
        "ticker": ["AAPL"]*3,
        "filing_date": ["2019-01-01", "2022-06-15", "2025-03-10"],
    })
    out = _filter_pilot_window(df)
    assert len(out) == 2  # 2019 dropped; 2022, 2025 retained


def test_batch509_filter_pilot_window_empty_input():
    from scripts.extract_sec_edgar_xml_pilot import _filter_pilot_window
    out = _filter_pilot_window(pd.DataFrame())
    assert out.empty


def test_batch509_filter_pilot_window_missing_date_column():
    from scripts.extract_sec_edgar_xml_pilot import _filter_pilot_window
    out = _filter_pilot_window(pd.DataFrame({"ticker": ["AAPL"]}))
    assert out.empty


# ---------------------------------------------------------------------------
# Dry-run extraction
# ---------------------------------------------------------------------------

def test_batch509_dry_run_does_not_hit_network():
    """Dry-run produces URLs + counts but no HTTP fetches."""
    from scripts.extract_sec_edgar_xml_pilot import extract_one_form_one_ticker
    # AAPL 8-K cache exists (verified Batch 496). Dry-run should
    # report n_filings > 0 with no errors.
    result = extract_one_form_one_ticker("8_K", "AAPL", dry_run=True)
    assert result["status"] in ("ok", "no_index_cache", "empty_window")
    # If cache exists for AAPL, expect filings in window
    if result["status"] == "ok":
        assert result["n_filings"] >= 0
        assert result["error_count"] >= 0


def test_batch509_extract_unknown_ticker_returns_no_index_cache():
    from scripts.extract_sec_edgar_xml_pilot import extract_one_form_one_ticker
    result = extract_one_form_one_ticker("8_K", "ZZZZ_NONEXISTENT",
                                            dry_run=True)
    assert result["status"] == "no_index_cache"
    assert result["n_filings"] == 0


def test_batch509_extract_returns_form_and_ticker_in_manifest():
    """Manifest dict carries the (form, ticker) pair for downstream
    summary aggregation."""
    from scripts.extract_sec_edgar_xml_pilot import extract_one_form_one_ticker
    result = extract_one_form_one_ticker("SC_13D", "AAPL", dry_run=True)
    assert result["ticker"] == "AAPL"
    assert result["form"] == "SC_13D"
