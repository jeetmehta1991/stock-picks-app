"""Batch 601 (2026-06-05) -- Option A redesign of strat_squeeze_setup_long
per owner desk-research directive 2026-06-05.

Eliminates the Donchian primitive from the strategy. Replaces with a
3-layer professional-firm squeeze-detection composite:

  LAYER 1 - POSITIONING (leading, weeks-ahead):
    short_interest_pct >= 0.20
    days_to_cover >= 8.0  (owner directive; was unused for long side)
    institutional_buy OR insider_cluster_active

  LAYER 2 - CATALYST (leading, hours-to-days):
    news_sentiment_shift > 0.4
    OR (within_pead_window AND pead_positive_surprise)

  LAYER 3 - CONFIRMATION (entry timing):
    above_avwap_20low (replaces dc20_breakout_up)
    vol_spike_15x (replaces vol_above_avg)
    close_above_open (NEW - B589 family)
    close_in_top_40pct_of_range (NEW - B589 family)

Academic & professional backing: Cohen-Diether-Malloy 2007 JF,
Boehmer-Jones-Zhang 2008 JF, Diether-Lee-Werner 2009 RFS; S3
Partners / Ortex / Hazeltree industry composite scoring.

Pins:
  (1) Full 8-gate fixture (all 3 layers) -> fires LONG
  (2) Layer 1 - missing SI threshold -> blocked
  (3) Layer 1 - missing DTC threshold -> blocked (owner directive)
  (4) Layer 1 - missing smart-money flow -> blocked
  (5) Layer 1 - insider_cluster_active alone (without institutional_buy)
      still satisfies the OR
  (6) Layer 2 - news sentiment catalyst alone satisfies OR
  (7) Layer 2 - PEAD catalyst alone satisfies OR
  (8) Layer 2 - NEITHER catalyst -> blocked
  (9) Layer 3 - missing AVWAP reclaim -> blocked
  (10) Layer 3 - missing vol_spike_15x -> blocked
  (11) Legacy B519 fixture (dc20_breakout_up + vol_above_avg + SI=0.20
       only) does NOT fire post-B601
  (12) Donchian decoupling: dc20_breakout_up is NOT in signals_used
"""
from __future__ import annotations

import pytest


def _full_fixture():
    return {
        "short_interest_pct": 0.25,
        "days_to_cover": 9.0,
        "institutional_buy": True,
        "insider_cluster_active": False,
        "news_sentiment_shift": 0.5,
        "within_pead_window": False,
        "pead_positive_surprise": False,
        "above_avwap_20low": True,
        "vol_spike_15x": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }


def test_batch601_full_fixture_fires():
    """Pin (1): all 3 layers satisfied -> fires long."""
    from backtest.signals.screener import strat_squeeze_setup_long
    out = strat_squeeze_setup_long(_full_fixture())
    assert out["fires"] is True
    assert out["direction"] == "long"


def test_batch601_layer1_missing_si_blocks():
    """Pin (2)."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture(); s["short_interest_pct"] = 0.15
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch601_layer1_missing_dtc_blocks():
    """Pin (3): owner-directive DTC >= 8 gate."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture(); s["days_to_cover"] = 5.0
    assert strat_squeeze_setup_long(s)["fires"] is False, (
        "DTC < 8 should block fire per owner-framework 'DTC 8-10' threshold"
    )


def test_batch601_layer1_missing_smart_money_blocks():
    """Pin (4): no institutional_buy AND no insider_cluster_active -> blocked."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture()
    s["institutional_buy"] = False
    s["insider_cluster_active"] = False
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch601_layer1_insider_cluster_alone_satisfies_or():
    """Pin (5): insider_cluster_active alone (without institutional_buy)
    still satisfies the OR."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture()
    s["institutional_buy"] = False
    s["insider_cluster_active"] = True
    assert strat_squeeze_setup_long(s)["fires"] is True


def test_batch601_layer2_news_catalyst_alone():
    """Pin (6): news shift > 0.4 alone (no PEAD) satisfies catalyst OR."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture()
    s["news_sentiment_shift"] = 0.5
    s["within_pead_window"] = False
    s["pead_positive_surprise"] = False
    assert strat_squeeze_setup_long(s)["fires"] is True


def test_batch601_layer2_pead_catalyst_alone():
    """Pin (7): PEAD window + positive surprise alone (no news shift)
    satisfies catalyst OR."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture()
    s["news_sentiment_shift"] = 0.0
    s["within_pead_window"] = True
    s["pead_positive_surprise"] = True
    assert strat_squeeze_setup_long(s)["fires"] is True


def test_batch601_layer2_no_catalyst_blocks():
    """Pin (8): no catalyst on either branch -> blocked."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture()
    s["news_sentiment_shift"] = 0.0
    s["within_pead_window"] = False
    s["pead_positive_surprise"] = False
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch601_layer3_missing_avwap_blocks():
    """Pin (9): no AVWAP reclaim -> blocked."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture(); s["above_avwap_20low"] = False
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch601_layer3_missing_vol_spike_blocks():
    """Pin (10): no 1.5x vol -> blocked."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture(); s["vol_spike_15x"] = False
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch601_layer3_missing_strong_close_blocks():
    """Pin (10b): no top-40pct close -> blocked."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = _full_fixture(); s["close_in_top_40pct_of_range"] = False
    assert strat_squeeze_setup_long(s)["fires"] is False


def test_batch601_legacy_b519_fixture_blocked():
    """Pin (11): legacy 3-gate fixture (SI + dc20_breakout_up +
    vol_above_avg) does NOT fire post-B601."""
    from backtest.signals.screener import strat_squeeze_setup_long
    s = {
        "short_interest_pct": 0.25,
        "dc20_breakout_up": True,
        "vol_above_avg": True,
    }
    assert strat_squeeze_setup_long(s)["fires"] is False, (
        "Legacy B519 3-gate fixture must not fire post-B601 redesign"
    )


def test_batch601_donchian_decoupled():
    """Pin (12): strat output signals_used should NOT reference any
    dc{10,20}_ signal post-B601."""
    from backtest.signals.screener import strat_squeeze_setup_long
    out = strat_squeeze_setup_long(_full_fixture())
    sig_str = ", ".join(out.get("signals_used", []))
    assert "dc10_" not in sig_str and "dc20_" not in sig_str, (
        f"B601 must eliminate Donchian from squeeze_setup_long; signals_used={sig_str}"
    )


def test_batch601_all_strategies_count_preserved_at_217():
    """No add/delete in B601."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 217
