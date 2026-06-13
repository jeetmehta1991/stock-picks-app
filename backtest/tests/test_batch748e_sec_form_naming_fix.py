# Source: B748e SC13D-INCREMENTAL-REFRESH owner-approved 2026-06-14 + CHECKLIST #15 + #44(b) + #68 per CHECKLIST #77
"""B748e pin tests: SEC EDGAR form-naming normalization fix.

Per CHECKLIST #44(b) (investigate when default-empty returned), the
B748e SC_13D refresh smoke surfaced that the existing prefetch script
silently missed all 2025+ activist filings because SEC EDGAR changed
its form naming from `SC 13D` / `SC 13D/A` to `SCHEDULE 13D` /
`SCHEDULE 13D/A`. The strict-equality form filter rejected every new
filing despite the data being available in the submissions endpoint.

Headline empirical evidence from smoke:
  CVNA SCHEDULE 13D/A: 2026-05-01, 2025-08-01, 2025-05-13, 2025-02-28
  -- 4 filings that the unfixed script silently skipped, causing the
  SC_13D cache to max at 2024-12-16.

These pins:
  - Lock the _normalize_form helper behavior
  - Confirm the form filter accepts both naming conventions
"""
from __future__ import annotations


def test_b748e_pin1_normalize_form_handles_schedule_variant():
    """`SCHEDULE 13D/A` must normalize to the same value as `SC 13D/A`."""
    from scripts.prefetch_sec_edgar import _normalize_form
    assert _normalize_form("SCHEDULE 13D/A") == _normalize_form("SC 13D/A")
    assert _normalize_form("SCHEDULE 13D") == _normalize_form("SC 13D")
    assert _normalize_form("SCHEDULE 13G/A") == _normalize_form("SC 13G/A")


def test_b748e_pin2_normalize_form_is_case_insensitive():
    """Form names are uppercase-normalized to handle mixed-case variants."""
    from scripts.prefetch_sec_edgar import _normalize_form
    assert _normalize_form("schedule 13d/a") == _normalize_form("SC 13D/A")
    assert _normalize_form("Sc 13D") == _normalize_form("SC 13D")


def test_b748e_pin3_normalize_form_preserves_non_schedule_forms():
    """Other forms (4, 8-K, 10-K) must pass through unchanged."""
    from scripts.prefetch_sec_edgar import _normalize_form
    assert _normalize_form("8-K") == "8-K"
    assert _normalize_form("10-K") == "10-K"
    assert _normalize_form("4") == "4"


def test_b748e_pin4_parse_filings_accepts_both_naming_conventions():
    """Synthetic submissions dict with mixed naming -- both formats are
    extracted into the same form-filter target.
    """
    from scripts.prefetch_sec_edgar import parse_filings_for_form
    submissions = {
        "filings": {
            "recent": {
                "form":              ["SC 13D/A", "SCHEDULE 13D/A", "8-K"],
                "filingDate":        ["2024-06-01", "2026-05-01", "2025-01-15"],
                "accessionNumber":   ["acc-1", "acc-2", "acc-3"],
                "primaryDocument":   ["doc-1.htm", "doc-2.htm", "doc-3.htm"],
            }
        }
    }
    df = parse_filings_for_form(submissions, "SC 13D/A", "TEST", "999")
    assert len(df) == 2, f"both SC 13D/A and SCHEDULE 13D/A should be captured; got {len(df)}"
    # Verify the SCHEDULE-named one is in the result
    accs = set(df["accession_number"].tolist())
    assert "acc-1" in accs and "acc-2" in accs


def test_b748e_pin5_schedule_form_only_does_not_pollute_8k_query():
    """A query for 8-K must NOT pick up SCHEDULE 13D/A rows."""
    from scripts.prefetch_sec_edgar import parse_filings_for_form
    submissions = {
        "filings": {
            "recent": {
                "form":              ["SCHEDULE 13D/A", "8-K"],
                "filingDate":        ["2026-05-01", "2025-01-15"],
                "accessionNumber":   ["acc-1", "acc-2"],
                "primaryDocument":   ["doc-1.htm", "doc-2.htm"],
            }
        }
    }
    df = parse_filings_for_form(submissions, "8-K", "TEST", "999")
    assert len(df) == 1, f"only 8-K should match; got {len(df)}"
    assert df.iloc[0]["accession_number"] == "acc-2"
