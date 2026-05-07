"""DEC-512 PIT-fundamentals filing-date audit — regression tests
(Pass 53 Day-9 v8f).

Audit findings (executed 2026-05-07):
- Items 1-4 (Polygon financials + 4 SEC EDGAR forms): ALL PASS — code already
  uses filing_date for as-of cutoffs.
- Item 5 (forward earnings calendar): not a lookahead bug; Polygon Stocks
  Starter does not include forward calendar; days_to_next_earnings returns
  None gracefully.
- Item 6 (Quiver insiders Date vs fileDate): **REAL BUG FOUND.** Code used
  `Date` (transaction date) for PIT cutoff instead of `fileDate` (SEC filing
  date). Mean filing lag 6 days; max 116 days. 43% of AAPL transactions had
  >2-day lag. Fixed via BUG-INSIDER-PIT this turn.
- Item 7 (signal_age_days field): DEC-513 #10 enhancement, not a lookahead
  bug; out of DEC-512 scope.

Spec: TRADING_RULES_AND_INFORMATION.md §2A.9.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Item 1: Polygon financials filing_date column populated
# ---------------------------------------------------------------------------
def test_dec512_item1_polygon_financials_has_filing_date():
    p = REPO_ROOT / "data_prefetch" / "polygon" / "financials" / "AAPL.parquet"
    if not p.exists():
        pytest.skip("Polygon financials AAPL not prefetched")
    df = pd.read_parquet(p)
    assert "filing_date" in df.columns, (
        "Polygon financials missing filing_date — DEC-512 item 1 FAIL"
    )
    populated = df["filing_date"].notna().sum()
    assert populated > 50, (
        f"Polygon financials filing_date sparse: {populated}/{len(df)} populated"
    )


def test_dec512_item1_polygon_financials_pit_sanity():
    """filing_date must be ON OR AFTER period_of_report_date (filings are
    filed AFTER the period they describe)."""
    p = REPO_ROOT / "data_prefetch" / "polygon" / "financials" / "AAPL.parquet"
    if not p.exists():
        pytest.skip("Polygon financials AAPL not prefetched")
    df = pd.read_parquet(p)
    if "period_of_report_date" not in df.columns:
        pytest.skip("period_of_report_date column not present")
    df = df.dropna(subset=["filing_date", "period_of_report_date"]).copy()
    if df.empty:
        pytest.skip("No rows with both dates populated")
    df["filing_date"] = pd.to_datetime(df["filing_date"])
    df["period_of_report_date"] = pd.to_datetime(df["period_of_report_date"])
    violations = (df["filing_date"] < df["period_of_report_date"]).sum()
    assert violations == 0, (
        f"PIT sanity: {violations} rows have filing_date < period_of_report_date "
        f"(filing should never precede the period it describes)"
    )


# ---------------------------------------------------------------------------
# Items 2-4: SEC EDGAR filing_date populated for all 4 form types
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("form_dir", ["4", "8_K", "SC_13D", "SC_13G"])
def test_dec512_item234_sec_edgar_filing_date_populated(form_dir):
    p = REPO_ROOT / "data_prefetch" / "sec_edgar" / form_dir / "AAPL.parquet"
    if not p.exists():
        pytest.skip(f"SEC EDGAR {form_dir} AAPL not prefetched")
    df = pd.read_parquet(p)
    assert "filing_date" in df.columns
    assert df["filing_date"].notna().all(), (
        f"SEC EDGAR {form_dir} has NULL filing_date entries"
    )


# ---------------------------------------------------------------------------
# Item 6: BUG-INSIDER-PIT regression — insider_signal must use fileDate
# ---------------------------------------------------------------------------
def test_dec512_item6_insider_signal_no_lookahead():
    """Replicate the pre-fix lookahead scenario:
    AAPL transaction by Katherine Adams on 2021-05-14, but SEC filing not until
    2021-08-04 (82-day lag). At as_of=2021-05-16, the signal should NOT include
    this transaction (public didn't know yet)."""
    from backtest.data.smart_money import insider_signal

    # 2 days after the trade but ~3 months before SEC filing
    r = insider_signal("AAPL", date(2021, 5, 16), lookback_days=30)
    # Pre-fix: would return signal="sell" (this was a sell)
    # Post-fix: returns "none" because fileDate > as_of filters it out
    assert r["sell_count"] == 0, (
        f"BUG-INSIDER-PIT regression: insider_signal on 2021-05-16 returned "
        f"sell_count={r['sell_count']}; AAPL transaction on 2021-05-14 was "
        f"not SEC-filed until 2021-08-04 (82-day lag). Public could not have "
        f"known about it on 2021-05-16."
    )


def test_dec512_item6_get_insider_transactions_pertkr_no_lookahead():
    """Same regression for the Wave D accessor."""
    from backtest.data.smart_money import get_insider_transactions_pertkr

    r = get_insider_transactions_pertkr("AAPL", date(2021, 5, 16), lookback_days=30)
    assert r["sell_count"] == 0, (
        f"BUG-INSIDER-PIT regression in get_insider_transactions_pertkr: "
        f"sell_count={r['sell_count']} on date with no PIT-visible transactions"
    )


def test_dec512_item6_filing_lag_distribution_sanity():
    """Verify the prefetch contains >2-day filing lags so the fix is testable.
    If Quiver schema changes and lag goes to 0, this test fails so we know
    to revisit."""
    p = REPO_ROOT / "data_prefetch" / "quiver" / "insider" / "AAPL.parquet"
    if not p.exists():
        pytest.skip("Quiver insider AAPL not prefetched")
    df = pd.read_parquet(p)
    if "fileDate" not in df.columns or "Date" not in df.columns:
        pytest.skip("Quiver schema missing fileDate or Date")
    df = df.copy()
    df["fileDate"] = pd.to_datetime(df["fileDate"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["fileDate", "Date"])
    df["lag"] = (df["fileDate"] - df["Date"]).dt.days
    # Mean lag should be > 1 day (typical SEC 4-day window + weekends)
    assert df["lag"].mean() > 1, (
        f"Filing lag suspiciously low (mean={df['lag'].mean():.2f}d) — "
        f"check Quiver data quality"
    )
    # Some transactions should have lag > 5 days
    assert (df["lag"] > 5).any(), "No high-lag transactions found in sample"


# ---------------------------------------------------------------------------
# Item 8: code-level scan — no consumer joins on period_of_report_date
# ---------------------------------------------------------------------------
def test_dec512_item8_no_consumer_uses_period_of_report():
    """Defensive: future code must not join fundamentals on
    period_of_report_date (would re-introduce lookahead)."""
    consumers = [
        REPO_ROOT / "backtest" / "data" / "fetcher.py",
        REPO_ROOT / "backtest" / "data" / "smart_money.py",
        REPO_ROOT / "backtest" / "data" / "macro.py",
        REPO_ROOT / "backtest" / "data" / "sentiment.py",
    ]
    violations = []
    for c in consumers:
        if not c.exists():
            continue
        text = c.read_text(errors="ignore")
        if "period_of_report" in text and "filing_date" not in text.split("period_of_report")[0][-200:]:
            # Allow comment mentions; check actual usage
            for line in text.splitlines():
                if "period_of_report" in line and not line.lstrip().startswith("#"):
                    if "<=" in line or ">=" in line or "==" in line:
                        violations.append(f"{c.name}: {line.strip()}")
    assert not violations, (
        f"DEC-512 item 8 regression: consumer code uses period_of_report_date "
        f"for joins. Violations: {violations}"
    )
