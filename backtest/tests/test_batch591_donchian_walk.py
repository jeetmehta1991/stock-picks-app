"""Batch 591 (2026-06-04) -- Stage 4 walk for donchian_10_breakout
family per owner directives 2026-06-04.

Owner directives:
  (a) Eliminate donchian_breakdown_short; add strat_donchian_breakout_long
      to restore long/short symmetry on the tight variant
  (b) Increase breakout tolerance to 1pct (LOCAL signals
      dc10_breakout_up_1pct / dc10_breakout_dn_1pct consumed by
      strat_donchian_10_breakout alone)
  (c) Add close_above_open / close_below_open gates
  (d) Add close_in_top_40pct_of_range / close_in_bottom_40pct_of_range
  (e) SKIPPED for breakout-entry (filters were retest-specific; flagged
      for clarification)
  A: yes - delete donchian_breakdown_retest_short, add
     donchian_breakout_retest_long
  B: LOCAL signals only
  C: apply (c)+(d) to retest too; skip (e) for retest

Pins:
  (1) dc10_breakout_up_1pct fires when close >= prior 10d high * 0.99
      and NOT when close < prior 10d high * 0.99
  (2) strat_donchian_breakdown_short DELETED from ALL_STRATEGIES
  (3) strat_donchian_breakdown_retest_short DELETED from ALL_STRATEGIES
  (4) strat_donchian_breakout_long REGISTERED with tight gates
  (5) strat_donchian_breakout_retest_long REGISTERED with tight gates
  (6) strat_donchian_10_breakout requires all 5 LONG gates
  (7) strat_donchian_10_breakout requires all 5 SHORT gates
  (8) strat_donchian_10_breakout_retest requires all 5 LONG gates
  (9) ALL_STRATEGIES count == 216 (preserved by -2 +2 swap)
"""
from __future__ import annotations

import pandas as pd
import pytest


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def test_batch591_dc10_breakout_up_1pct_emitted():
    """Pin (1): 1pct tolerance variant fires when close >= prior_high * 0.99."""
    from backtest.signals.technical import compute_donchian
    # 12 bars: prior 10d highs ~= 100; today close = 99.5 (within 1pct = pass)
    closes = [98.0] * 11 + [99.5]
    highs  = [100.0] * 11 + [99.7]
    lows   = [97.0] * 11 + [99.3]
    df = _build_df(closes, highs, lows)
    out = compute_donchian(df)
    # prior 10d high = max of df.iloc[:-1].tail(10).high = 100
    # close 99.5 vs 100*0.99 = 99 -> 99.5 >= 99 -> True
    assert out["dc10_breakout_up_1pct"] == True, (
        f"close 99.5 should pass 1pct tolerance (99.0); got {out['dc10_breakout_up_1pct']}"
    )
    # 0.2pct tolerance variant (existing): close 99.5 vs 100*0.998 = 99.8 ->
    # 99.5 < 99.8 -> existing strict variant should NOT fire here
    assert out["dc10_breakout_up"] == False, (
        f"close 99.5 should FAIL 0.2pct tolerance (99.8); got {out['dc10_breakout_up']}"
    )


def test_batch591_dc10_breakout_up_1pct_blocks_far_close():
    """Pin (1) inverse: close 1.5pct below prior_high should NOT fire."""
    from backtest.signals.technical import compute_donchian
    closes = [98.0] * 11 + [98.5]  # 98.5 vs prior_high 100 -> 1.5pct below
    highs  = [100.0] * 11 + [99.0]
    lows   = [97.0] * 11 + [98.0]
    df = _build_df(closes, highs, lows)
    out = compute_donchian(df)
    # close 98.5 vs 100*0.99 = 99 -> 98.5 < 99 -> False
    assert out["dc10_breakout_up_1pct"] == False


def test_batch591_donchian_breakdown_short_restored_in_b592():
    """Pin (2) post-B592/B595: donchian_breakdown_short was deleted in
    B591 then RESTORED in B592. Batch 595 walk added 2 gates for
    long/short symmetry with donchian_breakout_long (close_below_open
    + close_in_bottom_40pct_of_range). Now requires 5 gates."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_donchian_breakdown_short
    assert "donchian_breakdown_short" in ALL_STRATEGIES
    s = {"dc10_breakout_dn": True, "vol_spike_15x": True,
         "macd_12_26_9_bullish": False,
         "close_below_open": True,
         "close_in_bottom_40pct_of_range": True}
    out = strat_donchian_breakdown_short(s)
    assert out["fires"] == True
    assert out["direction"] == "short"


def test_batch591_donchian_breakdown_retest_short_restored_in_b592():
    """Pin (3) post-B592/B596: retest mirror RESTORED in B592 then
    walked in B596 (a)+(b)+(c)+(e). New 5-gate fixture:
    dc20_support_break_retest_strong + vol_below_avg + NOT macd_bullish
    + close_below_open + close_in_bottom_40pct_of_range."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_donchian_breakdown_retest_short
    assert "donchian_breakdown_retest_short" in ALL_STRATEGIES
    s = {"dc20_support_break_retest_strong": True,
         "vol_below_avg": True,
         "macd_12_26_9_bullish": False,
         "close_below_open": True,
         "close_in_bottom_40pct_of_range": True}
    out = strat_donchian_breakdown_retest_short(s)
    assert out["fires"] == True
    assert out["direction"] == "short"


def test_batch591_donchian_breakout_long_registered():
    """Pin (4): new tight long variant registered with 5 gates."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_donchian_breakout_long
    assert "donchian_breakout_long" in ALL_STRATEGIES
    # All 5 gates True -> fires
    s_all = {"dc10_breakout_up": True, "vol_spike_15x": True,
             "macd_12_26_9_bullish": True, "close_above_open": True,
             "close_in_top_40pct_of_range": True}
    out = strat_donchian_breakout_long(s_all)
    assert out["fires"] == True
    assert out["direction"] == "long"
    # Missing any gate -> no fire
    for missing in s_all.keys():
        s_missing = dict(s_all); s_missing[missing] = False
        assert strat_donchian_breakout_long(s_missing)["fires"] == False, (
            f"Missing {missing} should block fire"
        )


def test_batch591_donchian_breakout_retest_long_registered():
    """Pin (5) post-B596: retest mirror registered + walked. New
    5-gate fixture per B596 (b)+(c): dc20_resistance_break_retest_strong
    + vol_below_avg + macd_bullish + close_above_open +
    close_in_top_40pct_of_range."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_donchian_breakout_retest_long
    assert "donchian_breakout_retest_long" in ALL_STRATEGIES
    s_all = {"dc20_resistance_break_retest_strong": True,
             "vol_below_avg": True,
             "macd_12_26_9_bullish": True, "close_above_open": True,
             "close_in_top_40pct_of_range": True}
    assert strat_donchian_breakout_retest_long(s_all)["fires"] == True
    s_no_vol = dict(s_all); s_no_vol["vol_below_avg"] = False
    assert strat_donchian_breakout_retest_long(s_no_vol)["fires"] == False


def test_batch591_donchian_10_breakout_long_requires_6_gates():
    """Pin (6): LONG side needs ALL 6 gates post-B592 (5 from B591 +
    dc10_strong_breakout_up from B592)."""
    from backtest.signals.screener import strat_donchian_10_breakout
    s_all = {"dc10_breakout_up_1pct": True, "vol_above_avg": True,
             "macd_12_26_9_bullish": True, "close_above_open": True,
             "close_in_top_40pct_of_range": True,
             "dc10_strong_breakout_up": True}
    out = strat_donchian_10_breakout(s_all)
    assert out["fires"] == True
    assert out["direction"] == "long"
    # Legacy dc10_breakout_up (0.2pct tolerance) alone should NOT fire now
    # since strategy consumes _1pct variant
    s_legacy = dict(s_all); s_legacy["dc10_breakout_up_1pct"] = False
    s_legacy["dc10_breakout_up"] = True
    assert strat_donchian_10_breakout(s_legacy)["fires"] == False, (
        "Legacy dc10_breakout_up (0.2pct) should NOT trigger 1pct-consuming strategy"
    )
    # Missing close_above_open -> no fire
    s_no_co = dict(s_all); s_no_co["close_above_open"] = False
    assert strat_donchian_10_breakout(s_no_co)["fires"] == False
    # B592: missing strong-breakout gate -> no fire (trivial breakout)
    s_no_strong = dict(s_all); s_no_strong["dc10_strong_breakout_up"] = False
    assert strat_donchian_10_breakout(s_no_strong)["fires"] == False, (
        "B592 strong-breakout gate should block fire when missing"
    )


def test_batch591_donchian_10_breakout_short_requires_6_gates():
    """Pin (7): SHORT side mirror gates (6 post-B592)."""
    from backtest.signals.screener import strat_donchian_10_breakout
    s_all = {"dc10_breakout_dn_1pct": True, "vol_above_avg": True,
             "macd_12_26_9_bullish": False, "close_below_open": True,
             "close_in_bottom_40pct_of_range": True,
             "dc10_strong_breakout_dn": True}
    out = strat_donchian_10_breakout(s_all)
    assert out["fires"] == True
    assert out["direction"] == "short"
    s_no_bot = dict(s_all); s_no_bot["close_in_bottom_40pct_of_range"] = False
    assert strat_donchian_10_breakout(s_no_bot)["fires"] == False
    # B592: missing strong-breakdown gate -> no fire
    s_no_strong = dict(s_all); s_no_strong["dc10_strong_breakout_dn"] = False
    assert strat_donchian_10_breakout(s_no_strong)["fires"] == False


def test_batch591_donchian_20_breakout_retest_requires_5_gates():
    """Pin (8): renamed B594 from donchian_10_breakout_retest. Post-B594
    consumes dc20_resistance_break_retest_strong (LOCAL strong-breakout
    variant) + vol_below_avg (flipped from above; Bulkowski thesis) +
    macd_bullish + close_above_open + close_in_top_40pct_of_range."""
    from backtest.signals.screener import strat_donchian_20_breakout_retest
    s_all = {"dc20_resistance_break_retest_strong": True,
             "vol_below_avg": True,
             "macd_12_26_9_bullish": True, "close_above_open": True,
             "close_in_top_40pct_of_range": True}
    out = strat_donchian_20_breakout_retest(s_all)
    assert out["fires"] == True
    assert out["direction"] == "long"
    s_no_top = dict(s_all); s_no_top["close_in_top_40pct_of_range"] = False
    assert strat_donchian_20_breakout_retest(s_no_top)["fires"] == False


def test_batch591_all_strategies_count_after_b592_restoration():
    """Pin (9) post-B592: B591 was -2 +2 (216 -> 216); B592 restored the
    2 deletions per owner correction -> +2 net (216 -> 218)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 218, (
        f"Expected 218 after B592 restoration; got {len(ALL_STRATEGIES)}"
    )
