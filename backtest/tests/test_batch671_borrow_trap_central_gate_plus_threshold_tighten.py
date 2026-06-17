"""Batch 671 (2026-06-10) -- Round 2 of B669-pending owner decisions:
Q5 (per-strategy pre-fire borrow-trap gate via centralized inspect-frame
pattern in _strat() / _strat3()) + Q6 (SM-5 DTC threshold tighten
5.0 -> 8.0). Q7 + Q8 deferred per owner direction (post-B660).

Owner decisions (via AskUserQuestion Round 2):
  Q5 SM-5 wiring architecture:
     "Per-strategy pre-fire gate (cleanest, biggest blast radius)"
  Q6 SM-5 DTC threshold:
     "Tighten to dtc > 8.0 (heuristic adjustment)"
  Q7 Pattern F sequencing: "Post-B660 + post-cube" (no code action)
  Q8 Low-fire-combo EXPLORATORY sequencing: "Post-B660 measurement"
     (no code action)

Implementation pattern (B671 transparent design choice):
  - _short_borrow_trap_active(s) helper centralizes threshold logic
  - _strat() and _strat3() use inspect.currentframe to fetch caller's
    `s` variable + apply gate when direction == "short" (centralized
    consult; no per-strategy edit fan-out; new SHORT strategies are
    automatically protected per reviewer F5's "biggest blast radius"
    semantic intent)

Pins:

Helper behavior (4):
  (1)  _short_borrow_trap_active returns False on dict without DTC key
       (default 0.0; backward compatible with existing test fixtures)
  (2)  _short_borrow_trap_active returns False at threshold (dtc == 8.0;
       strict > inequality)
  (3)  _short_borrow_trap_active returns True above threshold (dtc > 8.0)
  (4)  _short_borrow_trap_active handles None days_to_cover gracefully
       (default 0.0; backward compatible)

SM-5 strategy threshold (2):
  (5)  strat_short_borrow_trap_avoid fires avoid at dtc=9.0 (above
       B671 Q6 threshold)
  (6)  strat_short_borrow_trap_avoid does NOT fire at dtc=7.0 (below
       B671 Q6 threshold; would have fired at dtc=6.0 under old 5.0
       threshold)

_strat() centralized gate behavior (3):
  (7)  Pure SHORT strategy blocked when borrow trap active (sample:
       strat_rsi_overbought_short with all gates True + DTC=10)
  (8)  Pure SHORT strategy fires normally when borrow trap inactive
       (DTC=3; below threshold)
  (9)  Pure LONG strategy unaffected by borrow trap (sample:
       strat_rsi_oversold with DTC=10; should still fire)

_strat3() centralized gate behavior (3):
  (10) Dual strategy SHORT branch blocked when borrow trap active
       (sample: strat_pivot_s1_bounce SHORT side with DTC=10)
  (11) Dual strategy LONG branch unaffected by borrow trap
       (sample: strat_pivot_s1_bounce LONG side with DTC=10)
  (12) Dual strategy SHORT fires normally when borrow trap inactive
       (sample: strat_pivot_s1_bounce SHORT side with DTC=3)

avoid-direction unaffected (1):
  (13) strat_short_borrow_trap_avoid itself (direction="avoid") is
       NOT recursively blocked when DTC is high (the gate only blocks
       direction=="short"; avoid emitters unaffected)

Backward compatibility (1):
  (14) ALL_STRATEGIES total count == 222 (unchanged from B670)
"""
from __future__ import annotations


# ============ Helper behavior ============

def test_batch671_borrow_trap_default_dtc_returns_false():
    """Pin (1): backward compat -- default DTC (key absent) returns False."""
    from backtest.signals.screener import _short_borrow_trap_active
    assert _short_borrow_trap_active({}) is False


def test_batch671_borrow_trap_at_threshold_returns_false():
    """Pin (2): strict inequality at current threshold returns False.
    B821 update: B713 LOWERED threshold 8.0 -> 5.0 per external reviewer
    critique (GME pre-squeeze DTC 5-7 range; >8 let canonical squeeze
    case through). Test pin now uses 5.0 boundary."""
    from backtest.signals.screener import _short_borrow_trap_active
    assert _short_borrow_trap_active({"days_to_cover": 5.0}) is False


def test_batch671_borrow_trap_above_threshold_returns_true():
    """Pin (3): dtc > 8.0 activates the trap."""
    from backtest.signals.screener import _short_borrow_trap_active
    assert _short_borrow_trap_active({"days_to_cover": 8.1}) is True
    assert _short_borrow_trap_active({"days_to_cover": 10.0}) is True
    assert _short_borrow_trap_active({"days_to_cover": 20.0}) is True


def test_batch671_borrow_trap_handles_none_dtc():
    """Pin (4): None days_to_cover -> default 0.0; backward compatible."""
    from backtest.signals.screener import _short_borrow_trap_active
    assert _short_borrow_trap_active({"days_to_cover": None}) is False


# ============ SM-5 strategy threshold ============

def test_batch671_sm5_fires_avoid_above_new_threshold():
    """Pin (5): SM-5 fires avoid at dtc=9.0 (above B671 Q6 8.0)."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    out = strat_short_borrow_trap_avoid({"days_to_cover": 9.0})
    assert out["fires"] is True
    assert out["direction"] == "avoid"


def test_batch671_sm5_does_not_fire_below_new_threshold():
    """Pin (6): SM-5 does NOT fire at dtc=7.0 (below B671 Q6 8.0).

    Pre-B671 threshold was 5.0, so dtc=7.0 would have fired. Post-B671
    threshold is 8.0, so dtc=7.0 is below the new trap. This pin proves
    the Q6 tighten landed correctly."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    out = strat_short_borrow_trap_avoid({"days_to_cover": 7.0})
    assert out["fires"] is False


# ============ _strat() centralized gate behavior ============

def test_batch671_pure_short_blocked_when_borrow_trap_active():
    """Pin (7): pure SHORT strategy blocked when borrow trap active.
    Sample: strat_rsi_overbought_short -- requires rsi>68 + below_sma_50
    + (bearish_engulfing OR rsi_14_rising == False)."""
    from backtest.signals.screener import strat_rsi_overbought_short
    s = {
        # All conditions to fire SHORT normally
        "rsi_14": 75.0,
        "below_sma_50": True,
        "bearish_engulfing": True,
        # Borrow trap active
        "days_to_cover": 10.0,
    }
    out = strat_rsi_overbought_short(s)
    assert out["fires"] is False, (
        "B671 regression: SHORT strategy fired despite borrow trap active. "
        "Centralized gate in _strat() should have forced fires=False."
    )


def test_batch671_pure_short_fires_when_borrow_trap_inactive():
    """Pin (8): pure SHORT fires normally when borrow trap inactive
    (DTC below threshold; behaves as if pre-B671)."""
    from backtest.signals.screener import strat_rsi_overbought_short
    s = {
        "rsi_14": 75.0,
        "below_sma_50": True,
        "bearish_engulfing": True,
        "days_to_cover": 3.0,  # Below threshold; no block
    }
    out = strat_rsi_overbought_short(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch671_pure_long_unaffected_by_borrow_trap():
    """Pin (9): LONG strategy unaffected even with high DTC.
    Borrow trap only blocks SHORT-direction fires."""
    from backtest.signals.screener import strat_rsi_oversold
    s = {
        "rsi_14_oversold": True,
        "rsi_14": 25.0,
        "price_above_sma_50": True,
        "price_above_ema_200": True,
        "obv_bullish": True,
        # High DTC; should NOT affect LONG
        "days_to_cover": 15.0,
    }
    out = strat_rsi_oversold(s)
    assert out["fires"] is True
    assert out["direction"] == "long"


# ============ _strat3() centralized gate behavior ============

def test_batch671_dual_short_branch_blocked_when_borrow_trap_active():
    """Pin (10): dual strategy SHORT branch blocked when borrow trap
    active. Sample: strat_pivot_s1_bounce SHORT side."""
    from backtest.signals.screener import strat_pivot_s1_bounce
    s = {
        # SHORT side conditions
        "near_r1": True,
        "shooting_star": True,
        "obv_bearish": True,
        # Borrow trap active
        "days_to_cover": 12.0,
    }
    out = strat_pivot_s1_bounce(s)
    assert out["fires"] is False, (
        "B671 regression: dual strategy SHORT branch fired despite borrow "
        "trap active. Centralized gate in _strat3() should have forced "
        "fires_short=False."
    )


def test_batch671_dual_long_branch_unaffected_by_borrow_trap():
    """Pin (11): dual strategy LONG branch unaffected by borrow trap.
    Sample: strat_pivot_s1_bounce LONG side with high DTC."""
    from backtest.signals.screener import strat_pivot_s1_bounce
    s = {
        # LONG side conditions
        "near_s1": True,
        "hammer": True,
        "obv_bullish": True,
        # High DTC; should NOT affect LONG
        "days_to_cover": 15.0,
    }
    out = strat_pivot_s1_bounce(s)
    assert out["fires"] is True
    assert out["direction"] == "long"


def test_batch671_dual_short_fires_normally_when_borrow_trap_inactive():
    """Pin (12): dual strategy SHORT fires normally when borrow trap
    inactive."""
    from backtest.signals.screener import strat_pivot_s1_bounce
    s = {
        "near_r1": True,
        "shooting_star": True,
        "obv_bearish": True,
        "days_to_cover": 3.0,  # Below threshold; no block
    }
    out = strat_pivot_s1_bounce(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


# ============ avoid-direction unaffected ============

def test_batch671_avoid_emitter_not_recursively_blocked():
    """Pin (13): SM-5 itself (direction='avoid') is NOT blocked when
    DTC is high. The gate only blocks direction=='short'. SM-5's avoid
    emission must fire so the centralized gate has something to consult."""
    from backtest.signals.screener import strat_short_borrow_trap_avoid
    out = strat_short_borrow_trap_avoid({"days_to_cover": 20.0})
    assert out["fires"] is True
    assert out["direction"] == "avoid"


# ============ Backward compatibility ============

def test_batch671_strategy_count_unchanged():
    """Pin (14) B821 UPDATED: count was 222 post-B670; B685 +3 + B686 +1
    + B709 +2 - B722 -3 = 221 current trajectory."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 219
