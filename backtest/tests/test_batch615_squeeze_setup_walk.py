"""Batch 615 (2026-06-07) -- MEDIUM-priority 13F-staleness Stage 4 re-walk
of squeeze_setup_long (B601 redesign) per CHECKLIST #105 a-j.

Owner-directed: a + d approved.

  (a) F1 docstring reframe: prior docstring described L1c smart-money
      OR as "the squeeze fuel that turns SI from a paper-position into
      actual upside risk for shorts". Overclaimed for the
      institutional_buy 13F STATE half (which is 90d+45d stale). B611
      staleness playbook applied: L1 reframed as POSITIONING
      ELIGIBILITY FILTER; timing alpha comes from L2+L3 EVENT layers.
  (d) B-twin added: strat_squeeze_setup_event_only_long. Identical
      8-gate architecture EXCEPT L1c tightened to EVENT-only smart-money
      (insider_cluster_active OR large_dollar_buy OR cfo_buy). Drops
      the 13F institutional_buy STATE half. Cube replay A/B vs broader
      OR composite.

Per feedback_asymmetric_data_sources_break_mechanical_inverse: SI, 13F,
insider buying are ALL structurally long-side data sources; no SHORT
mirror considered. short_borrow_trap_avoid (B519) already provides the
complementary protection rule.

Pins:
  (1) original strat_squeeze_setup_long fires with 8 gates True (incl.
      institutional_buy STATE-only L1c half)
  (2) original strat_squeeze_setup_long fires with insider_cluster
      _active EVENT-only L1c half (validates OR composite works on
      EVENT side too)
  (3) B-twin fires with EVENT-only smart-money (insider_cluster_active)
  (4) B-twin does NOT fire when only institutional_buy is True
      (validates the STATE half is dropped)
  (5) B-twin does NOT fire when L1c smart-money entirely absent
  (6) B-twin requires same L1ab + L2 + L3 gates as original
  (7) Both strategies registered in ALL_STRATEGIES
  (8) ALL_STRATEGIES count = 222 (+1 B-twin vs prior 221)
"""
from __future__ import annotations

import pytest


def _full_l1ab_l2_l3():
    """Common fixture: L1ab (SI + DTC) + L2 catalyst (news_sentiment_shift)
    + L3 confirmation. Caller adds L1c smart-money permutation."""
    return {
        "short_interest_pct": 0.25,
        "days_to_cover": 9.0,
        "news_sentiment_shift": 0.5,
        "above_avwap_20low": True,
        "vol_spike_15x": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }


def test_batch615_original_fires_with_state_only_l1c():
    """Pin (1): institutional_buy alone (STATE half) satisfies L1c."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_l1ab_l2_l3()
    s["institutional_buy"] = True   # STATE half only
    out = strat_squeeze_setup_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch615_original_fires_with_event_only_l1c():
    """Pin (2): insider_cluster_active alone (EVENT half) also satisfies."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_l1ab_l2_l3()
    s["insider_cluster_active"] = True   # EVENT half only
    out = strat_squeeze_setup_long(s)
    assert out["fires"] is True and out["direction"] == "long"


# Pins (3)-(6) SUPERSEDED-by-deletion in Batch 620:
# B619 fire-count estimator surfaced strat_squeeze_setup_event_only_long
# as FAIL_FIRE_STARVED (~2.5 fires/yr universe-wide upper bound; below
# min_trades=30/regime by an order of magnitude). Per CHECKLIST (k)
# resolution + owner direction (C delete), B-twin DELETED in B620. The
# A/B test of EVENT-only L1c can be answered offline post-cube from
# strat_squeeze_setup_long's trade log filtered by insider_cluster
# _active=True at fire bar - no separate registered strategy needed.
# Pins (3)-(6) replaced with the deletion checks below.


def test_batch615_btwin_deleted_in_b620():
    """Pin (3) SUPERSEDED by B620: B-twin DELETED (FAIL_FIRE_STARVED).
    Strategy function + ALL_STRATEGIES entry must both be absent."""
    from backtest.signals import screener
    assert not hasattr(screener, "strat_squeeze_setup_event_only_long"), (
        "B620 deletion: strat_squeeze_setup_event_only_long must be "
        "removed from screener.py per B619 fire-count finding"
    )
    assert "squeeze_setup_event_only_long" not in screener.ALL_STRATEGIES, (
        "B620 deletion: B-twin registry entry must be removed"
    )


def test_batch615_original_strategy_preserved():
    """Pin (4) SUPERSEDED by B620: the ORIGINAL strat_squeeze_setup_long
    remains registered and active. The B620 deletion only removed the
    B-twin; the OR-composite original is preserved and the EVENT-only
    L1c A/B question is answerable offline post-cube."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "squeeze_setup_long" in ALL_STRATEGIES


def test_batch615_all_strategies_count_221_post_b620():
    """Pin (8) updated for B620 deletion: 222 -> 221."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
