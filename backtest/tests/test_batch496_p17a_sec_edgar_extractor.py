"""Batch 496 (2026-05-30) -- P17a SEC EDGAR extractor scaffold tests.

Source: per CHECKLIST #77 (test extensively).
Queue row: EXECUTION_QUEUE.md item P17a.
Producer module: backtest/signals/sec_edgar_extractor.py.

Tests:
  - URL construction matches EDGAR's canonical pattern
  - 8-K item-code regex catches the standard codes + ignores false hits
  - SC 13D field extraction handles cover-page conventions
  - Consumer signal helpers degrade gracefully without decoded cache
  - Consumer math + PIT filter works against mock decoded DataFrames

The network-fetching extractor script (scripts/extract_sec_edgar_xml.py)
is owner-gated and runs once-off. This batch ships the producer +
consumer that the future decoded cache feeds into.
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

def test_batch496_p17a_url_strips_leading_zeros_from_cik():
    """AAPL CIK 0000320193 -> 320193 in URL (no leading zeros)."""
    from backtest.signals.sec_edgar_extractor import build_edgar_filing_url
    url = build_edgar_filing_url(
        cik="0000320193",
        accession_number="0001193125-15-258464",
        primary_doc="d927923d8k.htm",
    )
    assert url == (
        "https://www.sec.gov/Archives/edgar/data/320193/"
        "000119312515258464/d927923d8k.htm"
    )


def test_batch496_p17a_url_strips_dashes_from_accession():
    """0001193125-15-258464 -> 000119312515258464."""
    from backtest.signals.sec_edgar_extractor import build_edgar_filing_url
    url = build_edgar_filing_url(320193, "0001193125-15-258464", "x.htm")
    assert "000119312515258464" in url
    assert "0001193125-15-258464" not in url


def test_batch496_p17a_url_handles_integer_cik():
    """CIK accepted as int OR string with leading zeros."""
    from backtest.signals.sec_edgar_extractor import build_edgar_filing_url
    url_int = build_edgar_filing_url(320193, "0001193125-15-258464", "x.htm")
    url_str = build_edgar_filing_url("0000320193", "0001193125-15-258464",
                                       "x.htm")
    assert url_int == url_str


def test_batch496_p17a_url_raises_on_missing_accession():
    from backtest.signals.sec_edgar_extractor import build_edgar_filing_url
    with pytest.raises(ValueError, match="accession_number"):
        build_edgar_filing_url(320193, "", "x.htm")


def test_batch496_p17a_url_raises_on_missing_primary_doc():
    from backtest.signals.sec_edgar_extractor import build_edgar_filing_url
    with pytest.raises(ValueError, match="primary_doc"):
        build_edgar_filing_url(320193, "0001193125-15-258464", "")


# ---------------------------------------------------------------------------
# 8-K item-code extraction
# ---------------------------------------------------------------------------

def test_batch496_p17a_8k_extracts_known_item_codes():
    """Standard 8-K cover page mentions item codes as 'Item X.YY'."""
    from backtest.signals.sec_edgar_extractor import extract_8k_item_codes
    html = """
    <html><body>
    <p>Item 1.01 Entry into a Material Definitive Agreement.</p>
    <p>The Company entered into ...</p>
    <p>Item 5.02 Departure of Directors.</p>
    </body></html>
    """
    items = extract_8k_item_codes(html)
    assert "1.01" in items
    assert "5.02" in items
    assert items == sorted(items)


def test_batch496_p17a_8k_ignores_non_item_decimals():
    """A bare '1.01 million' or '5.02%' must NOT be picked up."""
    from backtest.signals.sec_edgar_extractor import extract_8k_item_codes
    html = "<p>Revenue was 1.01 million dollars. Margin 5.02 percent.</p>"
    items = extract_8k_item_codes(html)
    assert items == []


def test_batch496_p17a_8k_filters_unknown_item_codes():
    """Made-up code like 'Item 9.99' (not in 17 CFR 249.308) is dropped."""
    from backtest.signals.sec_edgar_extractor import extract_8k_item_codes
    html = "<p>Item 9.99 Wholly Made Up.</p><p>Item 1.01 Real.</p>"
    items = extract_8k_item_codes(html)
    assert items == ["1.01"]


def test_batch496_p17a_8k_returns_empty_on_empty_input():
    from backtest.signals.sec_edgar_extractor import extract_8k_item_codes
    assert extract_8k_item_codes("") == []
    assert extract_8k_item_codes("    ") == []


def test_batch496_p17a_8k_unique_codes():
    """Repeated mentions of same code -> single occurrence in result."""
    from backtest.signals.sec_edgar_extractor import extract_8k_item_codes
    html = """
    Item 1.01 Material Agreement.
    See Item 1.01 above.
    Item 1.01 details:
    """
    items = extract_8k_item_codes(html)
    assert items == ["1.01"]


# ---------------------------------------------------------------------------
# SC 13D field extraction
# ---------------------------------------------------------------------------

def test_batch496_p17a_sc13d_extracts_filer_identity():
    from backtest.signals.sec_edgar_extractor import extract_sc_13d_fields
    html = """
    NAMES OF REPORTING PERSONS
    Pershing Square Capital Management, L.P.
    I.R.S. Identification No.
    """
    out = extract_sc_13d_fields(html)
    assert "Pershing Square" in out["filer_identity"]


def test_batch496_p17a_sc13d_extracts_percent_owned():
    from backtest.signals.sec_edgar_extractor import extract_sc_13d_fields
    html = """
    PERCENT OF CLASS REPRESENTED BY AMOUNT
    9.5%
    TYPE OF REPORTING PERSON
    """
    out = extract_sc_13d_fields(html)
    assert out["percent_owned"] == 9.5


def test_batch496_p17a_sc13d_extracts_item_4_purpose():
    from backtest.signals.sec_edgar_extractor import extract_sc_13d_fields
    html = """
    ITEM 4. PURPOSE OF TRANSACTION
    The Reporting Persons believe that the shares are undervalued and
    represent an attractive investment opportunity. The Reporting Persons
    may engage in discussions with management.
    ITEM 5. INTEREST IN SECURITIES
    """
    out = extract_sc_13d_fields(html)
    assert "undervalued" in out["item_4_purpose"].lower() or \
           "attractive" in out["item_4_purpose"].lower() or \
           "discussions" in out["item_4_purpose"].lower()


def test_batch496_p17a_sc13d_empty_on_empty_input():
    from backtest.signals.sec_edgar_extractor import extract_sc_13d_fields
    out = extract_sc_13d_fields("")
    assert out["filer_identity"] == ""
    assert out["percent_owned"] is None
    assert out["item_4_purpose"] == ""


def test_batch496_p17a_sc13d_degrades_gracefully_on_garbage():
    """Random HTML without 13D conventions -> empty values, no raise."""
    from backtest.signals.sec_edgar_extractor import extract_sc_13d_fields
    out = extract_sc_13d_fields("<html><body>random text</body></html>")
    assert out["filer_identity"] == ""
    assert out["percent_owned"] is None


# ---------------------------------------------------------------------------
# Consumer signal helpers (decoded-cache absent today)
# ---------------------------------------------------------------------------

def test_batch496_p17a_decoded_cache_dir_present():
    """Pin: data_prefetch/sec_edgar_decoded/ EXISTS post-extractor-run
    (originally pinned absence until owner ran the extractor batch job;
    B815 flipped to existence pin since extractor has since run).
    """
    from pathlib import Path
    decoded = Path(__file__).resolve().parent.parent.parent / \
        "data_prefetch" / "sec_edgar_decoded"
    assert decoded.exists(), (
        f"Decoded cache directory {decoded} should exist post-extractor-run. "
        f"If absent, re-run the SEC EDGAR extractor batch job (queue P17a)."
    )


def test_batch496_p17a_sc_13d_consumer_returns_empty_on_no_cache():
    from backtest.signals.sec_edgar_extractor import sc_13d_filed_within_days
    out = sc_13d_filed_within_days("AAPL", date(2024, 6, 1))
    assert out == {}


def test_batch496_p17a_sc_13d_consumer_false_when_window_empty():
    from backtest.signals.sec_edgar_extractor import sc_13d_filed_within_days
    df = pd.DataFrame({
        "filing_date":    [date(2024, 1, 1)],
        "filer_identity": ["Test Holder"],
        "percent_owned":  [7.5],
    })
    out = sc_13d_filed_within_days("ZZZZ", date(2024, 6, 1),
                                     lookback_days=30, df=df)
    # Jan filing is outside Jun-30d window
    assert out["sc_13d_filed_within_30d"] is False


def test_batch496_p17a_sc_13d_consumer_true_when_in_window():
    from backtest.signals.sec_edgar_extractor import sc_13d_filed_within_days
    df = pd.DataFrame({
        "filing_date":    [date(2024, 5, 20)],
        "filer_identity": ["Pershing Square"],
        "percent_owned":  [9.5],
    })
    out = sc_13d_filed_within_days("ZZZZ", date(2024, 6, 1),
                                     lookback_days=30, df=df)
    assert out["sc_13d_filed_within_30d"] is True
    assert out["sc_13d_latest_filer_identity"] == "Pershing Square"
    assert out["sc_13d_latest_percent_owned"] == 9.5


def test_batch496_p17a_8k_consumer_detects_item_code():
    from backtest.signals.sec_edgar_extractor import eight_k_item_filed_within_days
    df = pd.DataFrame({
        "filing_date": [date(2024, 5, 25)],
        "item_codes":  ["1.01,8.01"],
    })
    out = eight_k_item_filed_within_days(
        "ZZZZ", date(2024, 6, 1), item_code="1.01",
        lookback_days=30, df=df,
    )
    assert out["8k_item_1_01_filed_within_30d"] is True


def test_batch496_p17a_8k_consumer_misses_when_code_not_present():
    from backtest.signals.sec_edgar_extractor import eight_k_item_filed_within_days
    df = pd.DataFrame({
        "filing_date": [date(2024, 5, 25)],
        "item_codes":  ["2.02,8.01"],
    })
    out = eight_k_item_filed_within_days(
        "ZZZZ", date(2024, 6, 1), item_code="1.01",
        lookback_days=30, df=df,
    )
    assert out["8k_item_1_01_filed_within_30d"] is False
