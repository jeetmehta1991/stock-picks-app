# Source: B747 + owner question 2026-06-13 "why does there need to be any delisting?" + revised C5 scope per CHECKLIST #77
"""B747 pin tests: PIT-universe discipline audit.

Owner question 2026-06-13 reframed B747 from 'calibrate survivor-bias direction'
to 'verify each engine respects the PIT universe per-bar vs collapsing to the
END-snapshot'. T1a already tracks 111 historical-removed names with
`removed_date` populated; the question is whether consumers honor it.

These pins lock the headline findings + script invariants:
- T1a still has its 503/111 active/removed split (drift guard)
- measure_fire_count.py is flagged PIT_INCORRECT (the actual finding)
- backtest.py is flagged PIT_CORRECT (the positive control)
- 8 OHLCV-missing names are flagged (independent data-quality finding)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from scripts.pit_universe_discipline_audit import (
    AuditReport,
    ConsumerAuditRow,
    HistoricalTicker,
    _classify_consumer,
    audit_pit_discipline,
)


# -------------------------------------------------------------------------
# T1a roster invariants (drift guards)
# -------------------------------------------------------------------------
def test_b747_pin1_t1a_roster_split():
    """T1a roster as of 2026-06-13: 614 total = 503 active + 111 historical-removed.
    Drift here means the T1a CSV was updated; intentional, but the audit must
    be re-validated against the new distribution.
    """
    rep = audit_pit_discipline()
    assert rep.t1a_total == 614, f"T1a total drift: {rep.t1a_total} (expected 614)"
    assert rep.t1a_active == 503
    assert rep.t1a_historical_removed == 111


def test_b747_pin2_ohlcv_missing_names_snapshot():
    """The 8 historical-removed names without OHLCV parquets: AGN, CXO, ETFC,
    NBL, RTN, TIF, VAR, WCG. These cannot be simulated even after a PIT fix.

    Reasoning per name (sanity vs prefetch decisions):
    - RTN: Raytheon merged into RTX (UTX) April 2020; the ticker continued as
      `RTX` -- the gap is acceptable IF backtests use RTX going forward.
    - AGN: Allergan acquired by AbbVie 2020-05-08; same merger-continuation
      situation.
    - ETFC: E*Trade acquired by Morgan Stanley 2020-10-02.
    - CXO: Concho Resources acquired by ConocoPhillips 2021-01-15.
    - NBL: Noble Energy acquired by Chevron 2020-10-05.
    - TIF: Tiffany acquired by LVMH 2021-01-07.
    - VAR: Varian acquired by Siemens Healthineers 2021-04-15.
    - WCG: WellCare acquired by Centene 2020-01-23.

    All 8 are M&A absorption -- no continuing ticker on US exchanges. OHLCV
    truncates at the M&A close; PIT-honest simulation up to the removal date
    needs these parquets.
    """
    rep = audit_pit_discipline()
    expected = {"AGN", "CXO", "ETFC", "NBL", "RTN", "TIF", "VAR", "WCG"}
    actual = set(rep.ohlcv_missing_for_removed)
    assert actual == expected, (
        f"OHLCV-missing set drift: actual={actual}, expected={expected}. "
        f"Either OHLCV was backfilled (good; remove names from expected) or new "
        f"removals lack OHLCV (investigate)."
    )


# -------------------------------------------------------------------------
# Headline finding: per-consumer PIT discipline
# -------------------------------------------------------------------------
def test_b747_pin3_measure_fire_count_is_pit_correct_post_b748a():
    """B748a (2026-06-13) FIXED the headline finding: measure_fire_count.py
    now uses `_load_t1a_tickers_union_over_window(start, end)` and the 111
    historical-removed names are included in the universe. Per-bar PIT is
    enforced implicitly by OHLCV parquet truncation at the removal date.

    This pin LOCKS the POST-B748a state. If verdict ever regresses to
    PIT_INCORRECT, the fix was reverted -- surface immediately.
    """
    rep = audit_pit_discipline()
    mfc = next((c for c in rep.consumers if c.consumer == "scripts/measure_fire_count.py"), None)
    assert mfc is not None
    assert mfc.verdict == "PIT_CORRECT", (
        f"measure_fire_count.py verdict regressed to {mfc.verdict}; B748a fix was reverted"
    )
    assert mfc.universe_load_pattern == "PIT_WINDOW_UNION"


def test_b747_pin4_backtest_engine_is_pit_correct():
    """Positive control: backtest/engine/backtest.py uses
    `get_sp500_constituents_pit(ref_date)` in a per-year loop. PIT-correct.
    If this regresses, survivor bias becomes universal.
    """
    rep = audit_pit_discipline()
    eng = next((c for c in rep.consumers if c.consumer == "backtest/engine/backtest.py"), None)
    assert eng is not None
    assert eng.verdict == "PIT_CORRECT"


def test_b747_pin5_pre_b748a_excluded_ticker_bars_magnitude_historical():
    """HISTORICAL RECORD pin: the magnitude of bias the pre-B748a
    measure_fire_count.py introduced was ~55K (ticker, bar) cells silently
    excluded. The estimator is unchanged by B748a (still computes the
    counterfactual "what would have been excluded if PIT-at-end were used"),
    so this number is preserved as a magnitude record.

    If this drops below 30K, either OHLCV coverage shrank or the estimator
    is broken.
    """
    rep = audit_pit_discipline()
    assert rep.estimated_excluded_ticker_bars >= 30_000, (
        f"estimated counterfactual excluded ticker-bars dropped to {rep.estimated_excluded_ticker_bars}; "
        f"either coverage shrank or estimator is broken"
    )


def test_b747_pin6_coverage_through_removal_majority():
    """Of the 103 historical-removed names WITH OHLCV, the majority should
    have data through the removal date (within 1 trading day). If many have
    OHLCV that truncates BEFORE removal_date, that's a separate data-quality
    finding worth surfacing.
    """
    rep = audit_pit_discipline()
    n_with_ohlcv = sum(1 for h in rep.historical_tickers if h.ohlcv_exists)
    n_through = sum(1 for h in rep.historical_tickers if h.coverage_through_removal)
    assert n_with_ohlcv > 0
    coverage_pct = n_through / n_with_ohlcv
    assert coverage_pct >= 0.5, (
        f"only {coverage_pct:.0%} of OHLCV-present removed-names have data through removal date. "
        f"Below 50% suggests systemic truncation at acquisition close (data-quality finding)."
    )


# -------------------------------------------------------------------------
# Classifier sanity (the static heuristic must catch obvious patterns)
# -------------------------------------------------------------------------
def test_b747_pin7_classifier_catches_end_date_pit_pattern():
    """The static classifier must catch `_load_t1a_tickers(end)` as PIT_INCORRECT.
    Sanity guard: if the heuristic is broken, the audit silently passes.
    """
    code = "tickers_full = _load_t1a_tickers(end)\n"
    row = _classify_consumer("test.py", code)
    assert row.verdict == "PIT_INCORRECT"
    assert row.universe_load_pattern == "PIT_AT_END_DATE"


def test_b747_pin8_classifier_catches_per_year_pit_pattern():
    """Sanity: per-year PIT pattern classifies as PIT_CORRECT."""
    code = """
    for ref_date in check_dates:
        _t1a_pit_at_year = set(get_sp500_constituents_pit(ref_date))
    """
    row = _classify_consumer("test.py", code)
    assert row.verdict == "PIT_CORRECT"
    assert row.universe_load_pattern == "PIT_PER_YEAR"


# -------------------------------------------------------------------------
# Output artifacts
# -------------------------------------------------------------------------
def test_b747_pin9_audit_artifacts_exist():
    """The audit script writes report + JSON. These artifacts feed the
    follow-on dispositions (B690b gating, OHLCV backfill, methodology fix).
    """
    out_dir = Path(__file__).resolve().parents[2] / "output_audit" / "b747_pit_discipline_audit"
    assert (out_dir / "b747_audit_report.md").exists(), "audit report not written"
    assert (out_dir / "b747_audit_results.json").exists(), "audit JSON not written"
