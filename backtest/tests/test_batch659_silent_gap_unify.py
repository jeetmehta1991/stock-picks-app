"""Batch 659 (2026-06-09) -- bundled silent-gap / default-pattern fixes
per owner directive 2026-06-09 "implement autonomously" on the four
remaining 2nd-wave-critique queue items:

  (1) S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY (W6/W7/W8 pivot portions
      remaining; T8 portion already RESOLVED-B657)
  (2) S4-T3-NOT-ABOVE-200-EMA-PATTERN
  (3) S4-W5M-SYMMETRIC-VOL-GATE
  (4) S5-FIRE-COUNT-MEASURED-RUN-FULL (launched in B660; doc only here)

All 5 code closures bundled per feedback_path_c_min_batch_size; per-
strategy isolation pins below + single pyramid run.

PATTERN CONFIRMED ACROSS FIXES:
  - Default-True silent-gap: any LONG gate `s.get(KEY, True)` where
    SHORT side uses `s.get(MIRROR_KEY, False)` is asymmetric auto-
    pass-on-missing. Fix: swap LONG default True -> False
    (symmetric with SHORT).
  - NOT-pattern silent-gap: `(not above_X)` where above_X defaults
    False auto-passes on missing key. Fix: positive symmetric
    `s.get("below_X", False)` (per feedback_never_use_NOT_s_get_pattern).
  - Symmetric Wyckoff gate: when LONG side requires Spring (low-volume
    Test), SHORT mirror requires Upthrust-Test (low-volume failed
    retest). Same `vol_below_avg` AND-required.

Pins:
  ==== W6 pivot_r1_breakout LONG default-True swap ====
  (1)  Pre-B659 fixture (all gates True except above_avwap_*low keys
       missing) used to fire LONG (default-True auto-pass); post-B659
       must NOT fire.
  (2)  Post-B659 fires LONG when above_avwap_*low keys explicitly True.

  ==== W7 pivot_r2_continuation LONG default-True swap ====
  (3)  Same pattern as W6 LONG.

  ==== W8 cpr_narrow_bullish LONG default-True swap ====
  (4)  Pre-B659 fixture (cpr_narrow_tight + above_cpr + above_200 +
       above_avwap_50low MISSING) auto-passed LONG via avwap default
       True; post-B659 must NOT fire without explicit above_avwap_50low.

  ==== T3 hull_rsi SHORT NOT-pattern fix ====
  (5)  Pre-B659 SHORT fired when price_above_ema_200 key MISSING (NOT
       False = True auto-pass); post-B659 must NOT fire without
       explicit below_ema_200.
  (6)  Post-B659 SHORT fires when below_ema_200 = True (explicit).

  ==== W5m vol_below_avg AND-required ====
  (7)  Pre-B659 W5m fired on recent_blowoff + bearish_engulfing alone
       (no vol gate); post-B659 must NOT fire without vol_below_avg.
  (8)  Post-B659 W5m fires when vol_below_avg + reversal-trigger +
       recent_blowoff.

  ==== Cross-fix preservation ====
  (9)  W6/W7/W8 SHORT side unchanged (still uses below_avwap_* default
       False; no regression).
  (10) T3 LONG side unchanged (above_200 still required positively).
"""
from __future__ import annotations


# ==================== W6 pivot_r1_breakout ====================

def test_batch659_w6_long_blocked_when_avwap_keys_missing():
    """Pin (1): pre-B659 default-True auto-passed; post-B659 strict."""
    from backtest.signals.screener import strat_pivot_r1_breakout
    s = {
        "above_r1": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": True,
        # NO above_avwap_252low or above_avwap_50low -- default False now
    }
    assert strat_pivot_r1_breakout(s)["fires"] is False, (
        "B659 W6 regression: LONG fires when AVWAP keys missing"
    )


def test_batch659_w6_long_fires_with_explicit_avwap():
    """Pin (2)."""
    from backtest.signals.screener import strat_pivot_r1_breakout
    s = {
        "above_r1": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": True,
        "above_avwap_252low": True,
        "above_avwap_50low": True,
    }
    out = strat_pivot_r1_breakout(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch659_w6_short_unchanged():
    """Pin (9 W6 part): SHORT side still uses default-False positive
    symmetric below_avwap_*low; behavior unchanged."""
    from backtest.signals.screener import strat_pivot_r1_breakout
    s = {
        "below_s1": True,
        "vol_spike_15x": True,
        "macd_12_26_9_bearish": True,
        "below_avwap_252low": True,
        "below_avwap_50low": True,
    }
    out = strat_pivot_r1_breakout(s)
    assert out["fires"] is True and out["direction"] == "short"


# ==================== W7 pivot_r2_continuation ====================

def test_batch659_w7_long_blocked_when_avwap_missing():
    """Pin (3)."""
    from backtest.signals.screener import strat_pivot_r2_continuation
    s = {
        "above_r2": True,
        "adx_trending": True,
        "ema_50_200_bullish": True,
        "vol_spike_2x": True,
        # NO avwap keys
    }
    assert strat_pivot_r2_continuation(s)["fires"] is False, (
        "B659 W7 regression: LONG fires when AVWAP keys missing"
    )


def test_batch659_w7_long_fires_with_explicit_avwap():
    from backtest.signals.screener import strat_pivot_r2_continuation
    s = {
        "above_r2": True,
        "adx_trending": True,
        "ema_50_200_bullish": True,
        "vol_spike_2x": True,
        "above_avwap_252low": True,
        "above_avwap_50low": True,
    }
    out = strat_pivot_r2_continuation(s)
    assert out["fires"] is True and out["direction"] == "long"


# ==================== W8 cpr_narrow_bullish ====================

def test_batch659_w8_long_blocked_when_avwap_50low_missing():
    """Pin (4): post-B654 + B659 W8 LONG strict on above_avwap_50low."""
    from backtest.signals.screener import strat_cpr_narrow_bullish
    s = {
        "cpr_narrow_tight": True,
        "above_cpr": True,
        "price_above_ema_200": True,
        # NO above_avwap_50low key -- default False now
    }
    assert strat_cpr_narrow_bullish(s)["fires"] is False, (
        "B659 W8 regression: LONG fires when above_avwap_50low missing"
    )


def test_batch659_w8_long_fires_when_avwap_present():
    """Companion to pin 4: with explicit above_avwap_50low True, fires."""
    from backtest.signals.screener import strat_cpr_narrow_bullish
    s = {
        "cpr_narrow_tight": True,
        "above_cpr": True,
        "price_above_ema_200": True,
        "above_avwap_50low": True,
    }
    out = strat_cpr_narrow_bullish(s)
    assert out["fires"] is True and out["direction"] == "long"


# ==================== T3 hull_rsi SHORT NOT-pattern ====================

def test_batch659_t3_short_blocked_when_ema200_keys_missing():
    """Pin (5): pre-B659 (not above_200) where above_200=False default
    auto-passed; post-B659 strict on below_ema_200 explicit."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25.0,
        # NO price_above_ema_200 / NO below_ema_200 -- both default False
    }
    assert strat_hull_rsi(s)["fires"] is False, (
        "B659 T3 regression: SHORT fires when ema_200 keys missing"
    )


def test_batch659_t3_short_fires_with_explicit_below_ema_200():
    """Pin (6)."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25.0,
        "below_ema_200": True,
    }
    out = strat_hull_rsi(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch659_t3_executable_no_longer_uses_not_pattern():
    """Pin: t3 source-body must NOT contain `(not above_200)` -- swap
    must have happened. Strip BOTH leading-`#` lines AND trailing-`#`
    comments before scanning."""
    import inspect
    import re
    from backtest.signals.screener import strat_hull_rsi
    src = inspect.getsource(strat_hull_rsi)
    parts = src.split('"""')
    body = "".join(parts[2:]) if len(parts) >= 3 else src
    code_lines = []
    for ln in body.splitlines():
        if ln.strip().startswith("#"):
            continue
        # Strip trailing inline comments (# outside string literals)
        ln_no_comment = re.sub(r'\s*#.*$', '', ln)
        code_lines.append(ln_no_comment)
    code = "\n".join(code_lines)
    assert "(not above_200)" not in code, (
        "B659 T3 regression: NOT-pattern silent-gap still in T3 executable code"
    )
    assert 's.get("below_ema_200"' in code, (
        "B659 T3: positive symmetric below_ema_200 read must be present in body"
    )


def test_batch659_t3_long_unchanged():
    """Pin (10): T3 LONG side unchanged (above_200 still positively required)."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bullish": True,
        "price_above_hull": True,
        "adx": 25.0,
        "price_above_ema_200": True,
    }
    out = strat_hull_rsi(s)
    assert out["fires"] is True and out["direction"] == "long"


# ==================== W5m vol_below_avg AND-required ====================

def test_batch659_w5m_blocked_without_vol_below_avg():
    """Pin (7): pre-B659 W5m fired on recent_blowoff + reversal alone;
    post-B659 requires vol_below_avg AND-gate."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    s = {
        "recent_blowoff_at_r3": True,
        "bearish_engulfing": True,
        # NO vol_below_avg
    }
    assert strat_pivot_r3_blowoff_short(s)["fires"] is False, (
        "B659 W5m regression: SHORT fires without vol_below_avg "
        "(symmetric mirror of B650 W5 Spring volume condition)"
    )


def test_batch659_w5m_fires_with_vol_below_avg_and_trigger():
    """Pin (8)."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    s = {
        "recent_blowoff_at_r3": True,
        "vol_below_avg": True,
        "bearish_engulfing": True,
    }
    out = strat_pivot_r3_blowoff_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch659_w5m_fires_with_each_reversal_trigger_plus_vol():
    """Sanity: each of 3 reversal triggers fires (with vol_below_avg)."""
    from backtest.signals.screener import strat_pivot_r3_blowoff_short
    base = {"recent_blowoff_at_r3": True, "vol_below_avg": True}
    for trigger in ("bearish_engulfing", "shooting_star", "below_prev_low"):
        s = dict(base)
        s[trigger] = True
        out = strat_pivot_r3_blowoff_short(s)
        assert out["fires"] is True and out["direction"] == "short", (
            f"B659 W5m: {trigger} should trigger SHORT with vol_below_avg"
        )
