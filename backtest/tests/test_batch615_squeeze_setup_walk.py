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


def test_batch615_btwin_fires_with_event_only_l1c():
    """Pin (3): B-twin requires EVENT-only smart-money; insider_cluster
    _active suffices."""
    from backtest.signals.screener import strat_squeeze_setup_event_only_long
    s = _full_l1ab_l2_l3()
    s["insider_cluster_active"] = True
    out = strat_squeeze_setup_event_only_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch615_btwin_does_not_fire_on_state_only_institutional_buy():
    """Pin (4): KEY A/B isolation - 13F STATE alone does NOT fire B-twin
    (would have fired the original via the OR composite)."""
    from backtest.signals.screener import (
        strat_squeeze_setup_long,
        strat_squeeze_setup_event_only_long,
    )
    s = _full_l1ab_l2_l3()
    s["institutional_buy"] = True   # STATE half only
    # Sanity: original fires
    assert strat_squeeze_setup_long(s)["fires"] is True
    # B-twin must NOT fire (dropped the STATE half from L1c)
    assert strat_squeeze_setup_event_only_long(s)["fires"] is False, (
        "B615 B-twin must drop the 13F institutional_buy STATE half; "
        "must NOT fire when only STATE half is True"
    )


def test_batch615_btwin_blocks_without_any_smart_money():
    """Pin (5): no smart-money signal at all blocks B-twin."""
    from backtest.signals.screener import strat_squeeze_setup_event_only_long
    s = _full_l1ab_l2_l3()
    # NO smart-money signal True
    assert strat_squeeze_setup_event_only_long(s)["fires"] is False


def test_batch615_btwin_fires_on_large_dollar_buy_event():
    """Pin (6a): B-twin fires when large_dollar_buy EVENT is the L1c."""
    from backtest.signals.screener import strat_squeeze_setup_event_only_long
    s = _full_l1ab_l2_l3()
    s["large_dollar_buy"] = True
    assert strat_squeeze_setup_event_only_long(s)["fires"] is True


def test_batch615_btwin_fires_on_cfo_buy_event():
    """Pin (6b): B-twin fires when cfo_buy EVENT is the L1c."""
    from backtest.signals.screener import strat_squeeze_setup_event_only_long
    s = _full_l1ab_l2_l3()
    s["cfo_buy"] = True
    assert strat_squeeze_setup_event_only_long(s)["fires"] is True


def test_batch615_btwin_requires_l1ab_si_dtc():
    """Pin (6c): L1ab gates still required - SI < 20% blocks."""
    from backtest.signals.screener import strat_squeeze_setup_event_only_long
    s = _full_l1ab_l2_l3()
    s["insider_cluster_active"] = True
    s["short_interest_pct"] = 0.10   # below 0.20 floor
    assert strat_squeeze_setup_event_only_long(s)["fires"] is False


def test_batch615_btwin_requires_l2_catalyst():
    """Pin (6d): L2 catalyst still required - no shift + no PEAD blocks."""
    from backtest.signals.screener import strat_squeeze_setup_event_only_long
    s = _full_l1ab_l2_l3()
    s["insider_cluster_active"] = True
    s["news_sentiment_shift"] = 0.0   # below 0.4 floor; no PEAD either
    assert strat_squeeze_setup_event_only_long(s)["fires"] is False


def test_batch615_btwin_requires_l3_confirmation():
    """Pin (6e): L3 vol_spike_15x still required."""
    from backtest.signals.screener import strat_squeeze_setup_event_only_long
    s = _full_l1ab_l2_l3()
    s["insider_cluster_active"] = True
    s["vol_spike_15x"] = False
    assert strat_squeeze_setup_event_only_long(s)["fires"] is False


def test_batch615_both_registered_in_all_strategies():
    """Pin (7): both A + B-twin in registry."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "squeeze_setup_long" in ALL_STRATEGIES
    assert "squeeze_setup_event_only_long" in ALL_STRATEGIES


def test_batch615_all_strategies_count_222():
    """Pin (8): 221 + 1 B-twin = 222."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 222
