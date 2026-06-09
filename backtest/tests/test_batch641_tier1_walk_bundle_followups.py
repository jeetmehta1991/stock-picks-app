"""Batch 641 (2026-06-09) -- Tier 1 narrow-scope ships from B640 walk
bundle follow-on per external-AI audit + owner directive 2026-06-09.

Owner directives applied:
  (2) Ship narrow-scope Tier 1 now:
      W3 + pin_bar fix:  F3 regime delete + F2 docstring + F1 producer-
                         additive bullish_pin_bar / bearish_pin_bar +
                         LONG swap pin_bar -> bullish_pin_bar.
      W4 F3-only:        regime entry delete only; F1+F2+RSI-mislabel
                         queued separately per CHECKLIST (g)
                         (S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL).
      W8 F1+F1b:         positive symmetric below_avwap_50low (B612
                         producer) + below_ema_200 (B630 producer)
                         replace NOT-pattern silent-gaps on SHORT side.
      W10 R3 -> R4:      rename strat_camarilla_r3_breakout to
                         strat_camarilla_r4_breakout + swap producer
                         signals above_cam_r3/below_cam_s3 ->
                         above_cam_r4/below_cam_s4 per Slim Khan /
                         Nick Scott Camarilla source-system (R3=fade,
                         R4=breakout). Resolves W9/W10 same-level
                         opposite-direction conflict.
  (3) CHECKLIST.md adds (r) timeframe-mismatch, (s) EVENT-STATE-wired-
      to-finding, Step 1.5 restore avoid-branch dead-code check.

Strategy count: 221 unchanged (W10 was a rename not delete/add).

Pins:
  (1)  bullish_pin_bar / bearish_pin_bar producers exist in technical.py
  (2)  bullish_pin_bar fires on dominant lower wick, NOT on dominant upper
  (3)  bearish_pin_bar fires on dominant upper wick, NOT on dominant lower
  (4)  strat_pivot_s1_bounce LONG fires on bullish_pin_bar
  (5)  strat_pivot_s1_bounce LONG does NOT fire on bearish_pin_bar
       (closes pre-B641 direction-contamination bug)
  (6)  strat_pivot_s1_bounce regime entry deleted
  (7)  strat_pivot_s1_bounce B291 default applies (LONG -> bull/neutral)
  (8)  strat_pivot_s2_bounce regime entry deleted
  (9)  strat_pivot_s2_bounce B291 default applies
  (10) strat_cpr_narrow_bullish SHORT no longer uses NOT-pattern
  (11) strat_cpr_narrow_bullish SHORT fires on positive below_avwap_50low
       + below_ema_200
  (12) strat_cpr_narrow_bullish SHORT blocked when both missing
       (fail-safe to no-fire)
  (13) strat_camarilla_r3_breakout no longer importable (renamed)
  (14) strat_camarilla_r4_breakout importable + callable
  (15) Registry: camarilla_r3_breakout deleted; camarilla_r4_breakout
       added
  (16) strat_camarilla_r4_breakout LONG fires on above_cam_r4 + vol_spike_2x
  (17) strat_camarilla_r4_breakout SHORT fires on below_cam_s4 + vol_spike_2x
  (18) CHECKLIST.md contains (r) timeframe-mismatch rule
  (19) CHECKLIST.md contains (s) EVENT-STATE-wired-finding rule
  (20) CHECKLIST.md contains Step 1.5 avoid-branch restore note
"""
from __future__ import annotations


# =================== W3 producer-additive + LONG swap ===================

def _fixture_with_bullish_pin_last_bar():
    """6-bar fixture; last bar has dominant lower wick (bullish pin).
    compute_candles requires len(df) >= 5."""
    import pandas as pd
    return pd.DataFrame({
        "open":   [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "high":   [101.0, 101.0, 101.0, 101.0, 101.0, 100.5],   # small upper wick
        "low":    [ 99.0,  99.0,  99.0,  99.0,  99.0,  95.0],   # large lower wick
        "close":  [100.0, 100.0, 100.0, 100.0, 100.0, 100.2],   # body small, near top
        "volume": [1e6, 1e6, 1e6, 1e6, 1e6, 1e6],
    })


def _fixture_with_bearish_pin_last_bar():
    """6-bar fixture; last bar has dominant upper wick (bearish pin)."""
    import pandas as pd
    return pd.DataFrame({
        "open":   [100.0, 100.0, 100.0, 100.0, 100.0,  95.0],
        "high":   [101.0, 101.0, 101.0, 101.0, 101.0, 100.0],   # large upper wick
        "low":    [ 99.0,  99.0,  99.0,  99.0,  99.0,  94.5],   # small lower wick
        "close":  [100.0, 100.0, 100.0, 100.0, 100.0,  95.2],
        "volume": [1e6, 1e6, 1e6, 1e6, 1e6, 1e6],
    })


def test_batch641_w3_bullish_pin_bar_producer_present():
    """Pin (1)."""
    from backtest.signals.technical import compute_candles
    sig = compute_candles(_fixture_with_bullish_pin_last_bar())
    assert "bullish_pin_bar" in sig
    assert "bearish_pin_bar" in sig


def test_batch641_w3_bullish_pin_bar_fires_on_dominant_lower_wick():
    """Pin (2)."""
    from backtest.signals.technical import compute_candles
    sig = compute_candles(_fixture_with_bullish_pin_last_bar())
    assert bool(sig["bullish_pin_bar"]) is True
    assert bool(sig["bearish_pin_bar"]) is False


def test_batch641_w3_bearish_pin_bar_fires_on_dominant_upper_wick():
    """Pin (3)."""
    from backtest.signals.technical import compute_candles
    sig = compute_candles(_fixture_with_bearish_pin_last_bar())
    assert bool(sig["bearish_pin_bar"]) is True
    assert bool(sig["bullish_pin_bar"]) is False


def test_batch641_w3_long_fires_on_bullish_pin():
    """Pin (4): LONG fires on near_s1 + bullish_pin_bar + obv_bullish."""
    from backtest.signals.screener import strat_pivot_s1_bounce
    s = {"near_s1": True, "bullish_pin_bar": True, "obv_bullish": True}
    out = strat_pivot_s1_bounce(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch641_w3_long_blocked_on_bearish_pin_only():
    """Pin (5): the direction-contamination bug. Bearish pin at support
    must NOT fire LONG. Pre-B641 it did (pin_bar was direction-agnostic)."""
    from backtest.signals.screener import strat_pivot_s1_bounce
    s = {"near_s1": True, "bearish_pin_bar": True, "obv_bullish": True}
    # No hammer + no bullish_pin_bar + bearish_pin_bar = MUST NOT FIRE LONG
    out = strat_pivot_s1_bounce(s)
    assert out["fires"] is False, (
        "B641 W3 F1 regression: bearish_pin_bar at support fired LONG"
    )


def test_batch641_w3_regime_entry_deleted():
    """Pin (6) F3."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert "pivot_s1_bounce" not in STRATEGY_REGIME_AFFINITY


def test_batch641_w3_b291_default_applies():
    """Pin (7)."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime("pivot_s1_bounce", r, direction="long") is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime("pivot_s1_bounce", r, direction="long") is False
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime("pivot_s1_bounce", r, direction="short") is True


# =================== W4 F3-only regime delete ===================

def test_batch641_w4_regime_entry_deleted():
    """Pin (8): F3 only; F1+F2+RSI-mislabel queued separately."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert "pivot_s2_bounce" not in STRATEGY_REGIME_AFFINITY


def test_batch641_w4_b291_default_applies():
    """Pin (9)."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime("pivot_s2_bounce", r, direction="long") is True
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime("pivot_s2_bounce", r, direction="short") is True


# =================== W8 F1+F1b positive symmetric ===================

def test_batch641_w8_short_no_not_pattern():
    """Pin (10). Check the EXECUTABLE code body only, not the docstring
    (which narrates the pre-B641 state for context). We split on the
    triple-quoted docstring close and inspect lines after it."""
    import inspect
    from backtest.signals.screener import strat_cpr_narrow_bullish
    src = inspect.getsource(strat_cpr_narrow_bullish)
    # Strip the docstring -- only check the code body
    # Docstring is the first triple-quoted block; everything after the
    # 2nd triple-quote is executable.
    parts = src.split('"""')
    assert len(parts) >= 3, "Expected docstring + body"
    body = "".join(parts[2:])
    # NOT pattern on above_avwap_50low must be GONE from SHORT side BODY
    assert 'not s.get("above_avwap_50low"' not in body, (
        "B641 W8 F1 regression: SHORT NOT-pattern still in executable code"
    )
    # NOT above_200 local must be gone from BODY
    assert "(not above_200)" not in body, (
        "B641 W8 F1b regression: SHORT (not above_200) still in code"
    )
    # Positive symmetric producers consumed
    assert "below_avwap_50low" in body
    assert "below_ema_200" in body


def test_batch641_w8_short_fires_with_positive_symmetric():
    """Pin (11)."""
    from backtest.signals.screener import strat_cpr_narrow_bullish
    s = {
        "cpr_narrow": True, "below_cpr": True, "rsi_14": 40,
        "below_avwap_50low": True, "below_ema_200": True,
    }
    out = strat_cpr_narrow_bullish(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch641_w8_short_blocked_when_keys_missing():
    """Pin (12): both new positive gates default-False -> fail-safe."""
    from backtest.signals.screener import strat_cpr_narrow_bullish
    s = {"cpr_narrow": True, "below_cpr": True, "rsi_14": 40}
    # no below_avwap_50low, no below_ema_200 -- must NOT auto-pass
    assert strat_cpr_narrow_bullish(s)["fires"] is False


# =================== W10 R3 -> R4 rename ===================

def test_batch641_w10_r3_not_importable():
    """Pin (13)."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_camarilla_r3_breakout")


def test_batch641_w10_r4_importable():
    """Pin (14)."""
    from backtest.signals.screener import strat_camarilla_r4_breakout
    assert callable(strat_camarilla_r4_breakout)


def test_batch641_w10_registry_renamed():
    """Pin (15)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "camarilla_r3_breakout" not in ALL_STRATEGIES
    assert "camarilla_r4_breakout" in ALL_STRATEGIES


def test_batch641_w10_long_fires_on_r4():
    """Pin (16): LONG fires on above_cam_r4 + vol_spike_2x."""
    from backtest.signals.screener import strat_camarilla_r4_breakout
    s = {"above_cam_r4": True, "vol_spike_2x": True}
    out = strat_camarilla_r4_breakout(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch641_w10_short_fires_on_s4():
    """Pin (17)."""
    from backtest.signals.screener import strat_camarilla_r4_breakout
    s = {"below_cam_s4": True, "vol_spike_2x": True}
    out = strat_camarilla_r4_breakout(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch641_w10_old_r3_signal_does_not_fire():
    """W10 R3->R4: the rename means above_cam_r3 alone (without above_cam_r4)
    must NOT trigger LONG. This proves the swap actually happened, not just
    that the function was renamed."""
    from backtest.signals.screener import strat_camarilla_r4_breakout
    # above_cam_r3 present but above_cam_r4 absent (price between R3 and R4)
    s = {"above_cam_r3": True, "vol_spike_2x": True}
    out = strat_camarilla_r4_breakout(s)
    assert out["fires"] is False, (
        "B641 W10 regression: above_cam_r3 fired LONG; must require above_cam_r4"
    )


# =================== CHECKLIST extensions (r), (s), Step 1.5 ===================

def test_batch641_checklist_r_timeframe_mismatch_present():
    """Pin (18)."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    text = (root / "CHECKLIST.md").read_text(encoding="utf-8", errors="replace")
    assert "Timeframe-mismatch check" in text or "timeframe-mismatch" in text.lower()
    assert "intraday-by-design" in text.lower()
    # Cross-ref to B640 audit
    assert "C1" in text and "B640" in text


def test_batch641_checklist_s_event_state_wired_present():
    """Pin (19)."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    text = (root / "CHECKLIST.md").read_text(encoding="utf-8", errors="replace")
    assert "F-timing-fragility" in text
    assert "EVENT-gates per direction" in text or "EVENT gates per direction" in text


def test_batch641_checklist_step1_5_avoid_branch_restored():
    """Pin (20)."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    text = (root / "CHECKLIST.md").read_text(encoding="utf-8", errors="replace")
    assert "Step 1.5" in text and "avoid-branch" in text.lower()


def test_batch641_execution_queue_13_new_tickets():
    """Verify the 13 capture-audit tickets are present in EXECUTION_QUEUE.md."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    text = (root / "EXECUTION_QUEUE.md").read_text(encoding="utf-8", errors="replace")
    expected_tickets = [
        "S5-FIRE-COUNT-MEASURED-RUN",
        "S5-MULTIPLE-TESTING-CORRECTION",
        "S5-MARGINAL-CONTRIBUTION-SCORING",
        "S4-CORPORATE-ACTION-POLICY",
        "S4-SURVIVORSHIP-T1A-VERIFY",
        "S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL",
        "S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY",
        "S4-W8-RSI-NOOP-GATE",
        "S4-OBV-LOCATION-TENSION-DESIGN",
        "S4-FIB-ANCHOR-LOOKAHEAD-AUDIT",
        "S5-REGIME-BETA-ASSUMPTION",
        "S4-REGIME-AAII-PIT",
        "S4-REGIME-FRED-VINTAGE",
        "S4-REGIME-SECTOR-ELIGIBILITY-TIME-VARYING",
        "S4-REGIME-COMPOSITE-FAIL-POLICY",
        "S4-REGIME-HYSTERESIS-PARITY-TEST",
        "S5-REGIME-WALK-FORWARD-VALIDATION",
    ]
    missing = [t for t in expected_tickets if t not in text]
    assert not missing, f"Missing B641 capture-audit tickets: {missing}"


# =================== Strategy count unchanged ===================

def test_batch641_all_strategies_count_221_unchanged():
    """W10 rename is net-zero count change; no Class 7 NEW wired this batch."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
