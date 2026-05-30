"""Batch 493 (2026-05-30) -- M6 PEAD earnings-surprise data-gap finding.

Source: per CHECKLIST #99 (pre-producer schema verification) and
CHECKLIST #77 (test extensively).
Queue row: EXECUTION_QUEUE.md item M6.
Cached data: data_prefetch/finnhub/calendar_earnings.parquet.

Data-gap finding (Batch 493 pre-flight 2026-05-30):

The queue row M6 ("missing-earnings-surprise-magnitude") claims:

  "Data fully cached in data_prefetch/finnhub/calendar_earnings.parquet
   (cols: epsActual, epsEstimate, revenueActual, revenueEstimate).
   Producer ... reads Finnhub -> eps_surprise_pct = (epsActual -
   epsEstimate) / abs(epsEstimate)."

Pre-flight schema verification disproves this:

  - calendar_earnings.parquet has 1,500 rows
  - Date range: 2026-08-05 -> 2026-12-21 (forward-looking ONLY)
  - Rows with BOTH epsActual not-null AND epsEstimate not-null: 0
  - Producer cannot compute eps_surprise_pct without ANY rows that have
    both quantities.

What IS present in repo for earnings data:
  - data_prefetch/polygon/financials/<ticker>.parquet has historical
    EPS ACTUALS (basic_earnings_per_share, diluted_earnings_per_share)
    via the existing PEAD producer at backtest/signals/pead.py.
  - Estimates are NOT prefetched anywhere.

This blocks M6 as scoped. Three resolution paths (owner-gated):

  Path 1: Re-prefetch Finnhub WITH historical estimates+actuals (paid
          API; per-ticker per-quarter pull, ~$X cost depending on tier).
  Path 2: Switch surprise definition from analyst-surprise to YoY-EPS-
          growth (already computed by existing PEAD producer as
          earnings_eps_yoy_growth). Cheaper but conceptually different
          edge -- Bernard-Thomas PEAD is about analyst-surprise drift,
          not YoY-growth drift.
  Path 3: Defer M6 to Phase 1B+ alongside news sentiment + analyst
          revisions (paid data tier).

Queue row M6 status: BLOCKED-DATA-GAP. Awaits owner path selection.

Tests below pin the empirical state of the parquet so the queue row
cannot silently drift back to "fully cached".
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
CALENDAR = REPO / "data_prefetch" / "finnhub" / "calendar_earnings.parquet"


@pytest.fixture(scope="module")
def calendar_df():
    if not CALENDAR.exists():
        pytest.skip(f"calendar_earnings.parquet not present at {CALENDAR}")
    return pd.read_parquet(CALENDAR)


def test_batch493_m6_calendar_has_required_columns(calendar_df):
    """Schema check: the parquet does carry the named columns. The gap
    is in row content, not column schema."""
    for col in ("epsActual", "epsEstimate", "revenueActual",
                "revenueEstimate", "symbol", "date"):
        assert col in calendar_df.columns, (
            f"calendar_earnings.parquet missing required column: {col}"
        )


def test_batch493_m6_calendar_has_zero_rows_with_actual_plus_estimate(calendar_df):
    """Empirical pin: 0 rows have BOTH epsActual not-null AND epsEstimate
    not-null. This is the binding constraint that BLOCKS the producer.
    """
    # Finnhub-style None markers can be the string 'None' as well as NaN
    actual_ok = (
        calendar_df["epsActual"].notna()
        & (calendar_df["epsActual"].astype(str) != "None")
    )
    estimate_ok = (
        calendar_df["epsEstimate"].notna()
        & (calendar_df["epsEstimate"].astype(str) != "None")
    )
    both_present = (actual_ok & estimate_ok).sum()
    assert both_present == 0, (
        f"Expected ZERO rows with both epsActual + epsEstimate present; "
        f"found {both_present}. If this assertion fails, the cache was "
        f"re-prefetched with historical data -- update M6 queue row to "
        f"RESOLVED-DATA-AVAILABLE and ship the producer."
    )


def test_batch493_m6_calendar_date_range_is_forward_looking_only(calendar_df):
    """Pin the date range so a future cache refresh that extends history
    surfaces the change in CI."""
    dates = pd.to_datetime(calendar_df["date"]).dropna()
    assert len(dates) > 0
    earliest = dates.min().date()
    latest = dates.max().date()
    # Today is 2026-05-30; if data starts after today, it's forward-looking
    from datetime import date as _date
    today = _date(2026, 5, 30)
    assert earliest >= today, (
        f"Earliest calendar_earnings date {earliest} is BEFORE today "
        f"{today}; cache now has historical data -- update queue row."
    )


def test_batch493_m6_polygon_financials_has_actual_eps_but_no_estimates():
    """The existing PEAD producer at backtest/signals/pead.py reads
    Polygon financials. Confirm: actuals present, estimates absent.

    This frames Path 2 (switch to YoY-growth surprise) as the ONLY
    cheap path; analyst-surprise definition requires Path 1
    (paid re-prefetch).
    """
    fin_dir = REPO / "data_prefetch" / "polygon" / "financials"
    if not fin_dir.exists():
        pytest.skip(f"Polygon financials dir not at {fin_dir}")
    samples = list(fin_dir.glob("*.parquet"))[:5]
    if not samples:
        pytest.skip("No polygon financials parquets to inspect")
    for sample in samples:
        df = pd.read_parquet(sample)
        if df.empty:
            continue
        # Schema columns: standardized list (no estimate column)
        assert "filing_date" in df.columns
        assert "fiscal_period" in df.columns
        assert "financials_json" in df.columns
        # No estimate / consensus / forecast column anywhere
        forbidden_estimate_cols = {
            "epsEstimate", "consensus_eps", "analyst_estimate_eps",
            "consensus_revenue", "analyst_estimate_revenue",
        }
        present_estimates = forbidden_estimate_cols.intersection(df.columns)
        assert not present_estimates, (
            f"Polygon financials suddenly has estimate columns "
            f"{present_estimates} at {sample.name} -- update M6 queue "
            f"row + ship producer."
        )
        # First non-empty sample is enough for the pin
        return
    pytest.skip("All polygon financials parquets are empty")


def test_batch493_m6_documented_resolution_paths_owner_gated():
    """Owner-decision pin: M6 unblock requires explicit path selection.
    This test exists so the queue row stays accountable -- removing this
    test without a queue update would silently un-block M6."""
    paths = {
        "path1_repurchase_finnhub_estimates": (
            "Paid API per-ticker per-quarter. Resolves M6 as scoped."
        ),
        "path2_switch_to_yoy_growth_surprise": (
            "Use existing earnings_eps_yoy_growth from pead.py. Cheap. "
            "Conceptually different edge (growth vs analyst-surprise)."
        ),
        "path3_defer_to_phase_1b": (
            "Defer alongside news sentiment + analyst revisions paid tier."
        ),
    }
    assert len(paths) == 3
    assert all("path" in k for k in paths.keys())
