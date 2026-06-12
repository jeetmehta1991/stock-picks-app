# Source: B737 Decision 4 verdicts + owner approval "Approve 1 and 2" 2026-06-12 per CHECKLIST #77
"""B738 pin tests: Decision 4 routing approvals (1 + 2).

Routing 1: C2 ADD wire `days_since_last_earnings > 2` to ICT-11/12
  - strat_week_opening_gap_fill_up
  - strat_week_opening_gap_fill_down
  Empirical: B737 C2 test FT lift +3.3pp OOS; train gap NEGATIVE (OOS BETTER than train).
  Production uses real days_since_last_earnings from compute_pead_signals
  (defaults 999 = no earnings data; gate passes).

Routing 2: EXPLORATORY tagging on FOMC strategies (B652 W5m + B722 po3 precedent)
  - strat_pre_fomc_long_sleeve
  - strat_pre_fomc_quality_momentum_long
  Empirical: B737 B1 FOMC SPY test FAIL (+5.7bp; p=0.401; Lucca-Moench dead).

Note: All 4 strategies remain REGISTERED (EXPLORATORY != deletion). The
EXPLORATORY tag is a docstring marker for cube-routing discipline; B738 ships
no roster-count change.
"""
from __future__ import annotations


# -------------------------------------------------------------------------
# Routing 1: C2 ADD wire (week-gap earnings filter)
# -------------------------------------------------------------------------
def test_b738_pin1_week_open_gap_up_requires_no_recent_earnings():
    """strat_week_opening_gap_fill_down must require days_since_last_earnings > 2."""
    from backtest.signals.screener import strat_week_opening_gap_fill_down
    # within last 2 days of earnings -> should NOT fire even with valid gap
    s_recent = {
        "week_open_gap_up_15pct": True,
        "days_since_last_earnings": 1,
    }
    result = strat_week_opening_gap_fill_down(s_recent)
    assert result["fires"] is False, (
        f"Should NOT fire with earnings in last 2 days post-B738; got {result}"
    )


def test_b738_pin2_week_open_gap_down_requires_no_recent_earnings():
    """strat_week_opening_gap_fill_up (gap-down-fade-long) symmetric mirror."""
    from backtest.signals.screener import strat_week_opening_gap_fill_up
    s_recent = {
        "week_open_gap_down_15pct": True,
        "days_since_last_earnings": 2,
    }
    result = strat_week_opening_gap_fill_up(s_recent)
    assert result["fires"] is False, (
        f"Should NOT fire with earnings in last 2 days (boundary); got {result}"
    )


def test_b738_pin3_week_open_gap_up_fires_when_clean():
    """Fires when gap valid AND earnings>2d ago."""
    from backtest.signals.screener import strat_week_opening_gap_fill_down
    s_clean = {
        "week_open_gap_up_15pct": True,
        "days_since_last_earnings": 10,
    }
    result = strat_week_opening_gap_fill_down(s_clean)
    assert result["fires"] is True
    assert result["direction"] == "short"


def test_b738_pin4_week_open_gap_up_default_no_earnings_data_passes():
    """If days_since_last_earnings missing from signal dict (default 999),
    gate must pass (treats no-data as not-recent-earnings)."""
    from backtest.signals.screener import strat_week_opening_gap_fill_down
    s_no_data = {"week_open_gap_up_15pct": True}  # no earnings field at all
    result = strat_week_opening_gap_fill_down(s_no_data)
    assert result["fires"] is True, (
        f"Default 999 must let the gate pass; got {result}"
    )


def test_b738_pin5_week_open_gap_signals_used_declares_new_gate():
    """signals_used must declare the new earnings-recency gate."""
    from backtest.signals.screener import strat_week_opening_gap_fill_down, strat_week_opening_gap_fill_up
    s = {"week_open_gap_up_15pct": True, "days_since_last_earnings": 10}
    r_down = strat_week_opening_gap_fill_down(s)
    s2 = {"week_open_gap_down_15pct": True, "days_since_last_earnings": 10}
    r_up = strat_week_opening_gap_fill_up(s2)
    assert "days_since_last_earnings>2" in r_down["signals_used"]
    assert "days_since_last_earnings>2" in r_up["signals_used"]


# -------------------------------------------------------------------------
# Routing 2: EXPLORATORY docstring tags
# -------------------------------------------------------------------------
def test_b738_pin6_pre_fomc_long_sleeve_exploratory():
    from backtest.signals.screener import strat_pre_fomc_long_sleeve
    doc = strat_pre_fomc_long_sleeve.__doc__ or ""
    assert "EXPLORATORY" in doc, (
        "strat_pre_fomc_long_sleeve must declare EXPLORATORY status post-B738"
    )
    assert "DO NOT DEPLOY" in doc


def test_b738_pin7_pre_fomc_quality_momentum_exploratory():
    from backtest.signals.screener import strat_pre_fomc_quality_momentum_long
    doc = strat_pre_fomc_quality_momentum_long.__doc__ or ""
    assert "EXPLORATORY" in doc
    assert "DO NOT DEPLOY" in doc


def test_b738_pin8_fomc_strategies_still_registered():
    """EXPLORATORY != deletion; both strategies must remain in ALL_STRATEGIES."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "pre_fomc_long_sleeve" in ALL_STRATEGIES
    assert "pre_fomc_quality_momentum_long" in ALL_STRATEGIES


def test_b738_pin9_no_strategy_count_change():
    """B738 ships docstring edits + earnings gate add; no roster delta.
    F-002 count assertion guard: live `len(ALL_STRATEGIES)` is the canonical
    count and pin tests for it live in test_unit.py F-002 (test_canonical_facts).
    Here we just sanity-check that the 4 affected strategies are still
    registered with their expected directions.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    assert "week_opening_gap_fill_up" in ALL_STRATEGIES
    assert "week_opening_gap_fill_down" in ALL_STRATEGIES
    assert "pre_fomc_long_sleeve" in ALL_STRATEGIES
    assert "pre_fomc_quality_momentum_long" in ALL_STRATEGIES
    # spot direction
    sample_up = {"week_open_gap_down_15pct": True, "days_since_last_earnings": 10}
    assert ALL_STRATEGIES["week_opening_gap_fill_up"](sample_up)["direction"] == "long"
    sample_dn = {"week_open_gap_up_15pct": True, "days_since_last_earnings": 10}
    assert ALL_STRATEGIES["week_opening_gap_fill_down"](sample_dn)["direction"] == "short"
