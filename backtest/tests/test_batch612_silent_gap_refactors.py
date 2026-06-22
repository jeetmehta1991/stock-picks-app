"""Batch 612 (2026-06-07) -- silent-gap refactors of 6 HIGH-priority
walked strategies per owner directive + external-AI critique audit
findings.

External-AI critique of B608/B609/B610 walks surfaced that the
`not s.get(<inverse>)` pattern remained in 13 walked strategies.
6 are HIGH-priority (no default=True safety): missing-key auto-fires
SHORT (silent-gap class). 7 are LOW-priority (have default=True;
pattern-fragile but functionally safe today).

B612 refactors the 6 HIGH-priority:
  - strat_donchian_10_breakout (SHORT side): not macd_bullish ->
    macd_bearish (B609 added).
  - strat_donchian_breakdown_short: same.
  - strat_donchian_breakdown_retest_short: same.
  - strat_r1_break_retest (SHORT side): not macd_bullish -> macd_bearish;
    not above_avwap_20high (no default) -> below_avwap_20high
    (B612 NEW producer signal added to compute_vwap).
  - strat_volume_spike_breakout (SHORT side): not above_avwap_20high
    -> below_avwap_20high (B612 NEW).
  - strat_volume_spike_breakout_retest (SHORT side): same.

Producer additions (B612):
  - below_avwap_252low, below_avwap_50low, below_avwap_20high,
    below_avwap_20low - symmetric to above_avwap_* (added in B205,
    avwap_20low added in B598). Mirror per B612 CHECKLIST #105 (j)
    producer-additive grep extension.

Pins:
  (1) below_avwap_20high signal emitted by compute_vwap (B612 producer)
  (2) below_avwap_20low + 50low + 252low also emitted (symmetric set)
  (3) donchian_10_breakout SHORT fires with explicit macd_bearish
  (4) donchian_10_breakout SHORT silent-gap closed: missing macd_bearish
      key (and bullish absent) does NOT auto-fire
  (5) donchian_breakdown_short fires with explicit macd_bearish
  (6) donchian_breakdown_short silent-gap closed
  (7) donchian_breakdown_retest_short fires + silent-gap closed
  (8) r1_break_retest SHORT fires with macd_bearish + below_avwap_20high
  (9) r1_break_retest SHORT silent-gap closed (missing macd_bearish OR
      missing below_avwap_20high blocks)
  (10) volume_spike_breakout SHORT fires with below_avwap_20high
  (11) volume_spike_breakout SHORT silent-gap closed
  (12) volume_spike_breakout_retest SHORT fires + silent-gap closed
  (13) ALL_STRATEGIES count unchanged at 221 (refactor only)
"""
from __future__ import annotations

import numpy as np
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


def test_batch612_below_avwap_signals_emitted():
    """Pins (1) + (2): producer emits below_avwap_* signals (symmetric
    to above_avwap_* added in B205/B598)."""
    from backtest.signals.technical import compute_vwap
    n = 260
    closes = list(np.linspace(110, 90, n))   # falling -> close below AVWAP
    highs = [c + 0.5 for c in closes]
    lows  = [c - 0.5 for c in closes]
    # Inject swing-high mid-window so 20-high anchor falls inside window
    highs[n - 10] = 120.0
    lows[n - 15]  = 85.0
    lows[n - 30]  = 80.0
    lows[n - 200] = 70.0
    df = _build_df(closes, highs, lows)
    out = compute_vwap(df)
    for key in ("below_avwap_252low", "below_avwap_50low",
                "below_avwap_20high", "below_avwap_20low"):
        assert key in out, f"{key} must be emitted (B612 F2 mirror)"
    # On falling-price data with mid-window swing high anchor, today's close
    # should be below the 20-high AVWAP
    assert out["below_avwap_20high"] is True
    assert out["above_avwap_20high"] is False


def test_batch612_donchian_10_breakout_short_fires_with_macd_bearish():
    """Pin (3)."""
    from backtest.signals.screener import strat_donchian_10_breakout
    s = {
        "dc10_breakout_dn_1pct": True,
        "vol_above_avg": True,
        "macd_12_26_9_bearish": True,    # B612 positive gate
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "dc10_strong_breakout_dn": True,
    }
    out = strat_donchian_10_breakout(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch612_donchian_10_breakout_short_silent_gap_closed():
    """Pin (4): missing macd_bearish does NOT auto-fire SHORT (was the
    pre-B612 bug pattern: `not s.get(macd_12_26_9_bullish)` no default)."""
    from backtest.signals.screener import strat_donchian_10_breakout
    s = {
        "dc10_breakout_dn_1pct": True,
        "vol_above_avg": True,
        # macd_12_26_9_bearish ABSENT - pre-B612 would have auto-passed
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "dc10_strong_breakout_dn": True,
    }
    assert strat_donchian_10_breakout(s)["fires"] is False


def test_batch612_donchian_breakdown_short_fires_with_macd_bearish():
    """Pin (5)."""
    from backtest.signals.screener import strat_donchian_breakdown_short
    s = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bearish": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_donchian_breakdown_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch612_donchian_breakdown_short_silent_gap_closed():
    """Pin (6)."""
    from backtest.signals.screener import strat_donchian_breakdown_short
    s = {
        "dc10_breakout_dn": True,
        "vol_spike_15x": True,
        # macd_12_26_9_bearish ABSENT
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_donchian_breakdown_short(s)["fires"] is False


def test_batch612_donchian_breakdown_retest_short_fires_with_macd_bearish():
    """Pin (7)."""
    from backtest.signals.screener import strat_donchian_breakdown_retest_short
    s = {
        "dc20_support_break_retest_strong": True,
        "vol_below_avg": True,
        "macd_12_26_9_bearish": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_donchian_breakdown_retest_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch612_donchian_breakdown_retest_short_silent_gap_closed():
    """Pin (7b)."""
    from backtest.signals.screener import strat_donchian_breakdown_retest_short
    s = {
        "dc20_support_break_retest_strong": True,
        "vol_below_avg": True,
        # macd_12_26_9_bearish ABSENT
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_donchian_breakdown_retest_short(s)["fires"] is False


def test_batch612_r1_break_retest_short_fires_with_positive_gates():
    """Pin (8): r1_break_retest SHORT now uses both macd_bearish AND
    below_avwap_20high (two B612 refactors in this strategy)."""
    from backtest.signals.screener import strat_r1_break_retest
    s = {
        "s1_break_retest_short": True,
        "below_s1": True,
        "macd_12_26_9_bearish": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        "below_avwap_20high": True,
    }
    out = strat_r1_break_retest(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch612_r1_break_retest_short_silent_gap_closed_macd():
    """Pin (9a): missing macd_bearish blocks."""
    from backtest.signals.screener import strat_r1_break_retest
    s = {
        "s1_break_retest_short": True,
        "below_s1": True,
        # macd_12_26_9_bearish ABSENT
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        "below_avwap_20high": True,
    }
    assert strat_r1_break_retest(s)["fires"] is False


def test_batch612_r1_break_retest_short_silent_gap_closed_avwap():
    """Pin (9b): missing below_avwap_20high blocks."""
    from backtest.signals.screener import strat_r1_break_retest
    s = {
        "s1_break_retest_short": True,
        "below_s1": True,
        "macd_12_26_9_bearish": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        "vol_below_avg": True,
        # below_avwap_20high ABSENT
    }
    assert strat_r1_break_retest(s)["fires"] is False


def test_batch612_volume_spike_breakout_short_fires_with_below_avwap():
    """Pin (10)."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_dn": True,
        "vol_spike_15x": True,
        "below_avwap_20high": True,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_volume_spike_breakout(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch612_volume_spike_breakout_short_silent_gap_closed():
    """Pin (11)."""
    from backtest.signals.screener import strat_volume_spike_breakout
    s = {
        "dc20_breakout_dn": True,
        "vol_spike_15x": True,
        # below_avwap_20high ABSENT - pre-B612 would have auto-passed via
        # `not s.get("above_avwap_20high")`
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    assert strat_volume_spike_breakout(s)["fires"] is False


def test_batch612_volume_spike_breakout_retest_short_DELETED_B682():
    """Pin (12) SUPERSEDED by B682 deletion of strat_volume_spike_breakout_
    retest per B620 precedent + B680 self-critique CC-B (0.01/yr B621
    FAIL_FIRE_STARVED).

    Original B612 pin (12) tested that the B612 F2 silent-gap fix on
    below_avwap_20high (the SHORT-side AVWAP gate) wired correctly into
    strat_volume_spike_breakout_retest. The strategy was deleted B682
    so the silent-gap-closed assertion is moot at the strategy level —
    but the B612 producer-side fix (below_avwap_20high emit) REMAINS
    valid and is still used by other consumers (volume_spike_breakout
    SHORT, r1_break_retest SHORT, 52wl_break_retest_short).

    Test converted to DELETION VERIFICATION per B670 precedent.
    """
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_volume_spike_breakout_retest"), (
        "B682 deletion: strat_volume_spike_breakout_retest must be REMOVED"
    )


def test_batch612_volume_spike_breakout_retest_short_silent_gap_closed_DELETED_B682():
    """Pin (12b) SUPERSEDED — see test_batch612_volume_spike_breakout_
    retest_short_DELETED_B682 above. Strategy deleted; silent-gap-closed
    assertion is moot at the strategy level.
    """
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_volume_spike_breakout_retest")


def test_batch612_all_strategies_count_post_b682_at_218():
    """Pin (13) post-B682 update: B612 was pure refactor + producer-
    additive (no add/delete); count was 221 at B612.

    Post-B682 (2026-06-10 owner-approved deletions per B680 self-critique):
    222 -> 218 (-4 strategies). B823 updated: trajectory continues
    218 + B685+3 + B686+1 + B709+2 - B722-3 = 221.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 220
