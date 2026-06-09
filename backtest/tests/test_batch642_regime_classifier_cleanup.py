"""Batch 642 (2026-06-09) -- Regime classifier follow-on per B640
external-AI regime audit findings #2 + #3 + owner directive 2026-06-09 #4.

Two changes shipped:

  (1) DEAD CANONICAL BEAR LINE REMOVED -- per audit finding #2.
      Pre-B642 classify_regime ladder had:
          if vix_value >= 40:               return "crisis"
          if vix_value >= 30 and spy_above_200ema is False: return "bear"
          if spy_above_200ema is False:     return "bear"
          ...
      Line 2 was DEAD CODE: any (vix>=30, below_200ema) case was also
      caught by line 3 (below_200ema, any vix). VIX no longer contributed
      to bear classification post-B288; the canonical line just made it
      look like it did. B642 removes line 2 for honest semantics.

  (2) EMA-CROSS HYSTERESIS BAND -- per audit finding #3.
      Pre-B642 the SPY-vs-200-EMA condition was binary at every
      threshold. A 0.1% close above then 0.1% below the 200-EMA flipped
      bear<->neutral day-by-day. Hysteresis architecture buffered VIX
      (+/- 5 points) but left the dominant input (EMA cross) unbuffered.
      B642 adds EMA_CROSS_HYSTERESIS_PCT = 2.0: when prev_regime is bear,
      require SPY to close >= +2% above its 200-EMA to confirm exit.
      Asymmetric: SLOW to exit risk-off, FAST to enter (any below-EMA
      close still triggers bear immediately to not delay risk reduction).
      New parameter `spy_pct_from_200ema` passed via get_regime_context;
      legacy callers without it degrade gracefully to pre-B642 behavior.

Pins:
  (1)  classify_regime crisis at VIX>=40
  (2)  classify_regime bear at SPY<200EMA any VIX
  (3)  classify_regime no longer has the dead VIX>=30 line in source
  (4)  classify_regime bear unchanged at VIX>=30 (since SPY<200EMA still
       catches it via Batch 288 SPY-only gate)
  (5)  classify_regime bull at VIX<20 + SPY>200EMA
  (6)  classify_regime neutral as fallback
  (7)  EMA_CROSS_HYSTERESIS_PCT exists at 2.0
  (8)  with_hysteresis stays bear when SPY just barely above EMA
       (+0.5%, below 2% band)
  (9)  with_hysteresis EXITS bear when SPY decisively above EMA (+3%)
  (10) with_hysteresis enters bear immediately when SPY drops below EMA
       (no entry hysteresis -- fast risk-off)
  (11) with_hysteresis falls back to pre-B642 binary gate when
       spy_pct_from_200ema is None (legacy caller compatibility)
  (12) get_regime_context computes spy_pct_from_200ema from spy_close +
       spy_ema200 and passes to classify_regime_with_hysteresis
"""
from __future__ import annotations


# =================== Dead canonical bear line removed ===================

def test_batch642_crisis_at_vix_40():
    """Pin (1)."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(40.0, True) == "crisis"
    assert classify_regime(45.0, False) == "crisis"


def test_batch642_bear_at_spy_below_200ema_any_vix():
    """Pin (2)."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(15.0, False) == "bear"  # low VIX + below EMA
    assert classify_regime(25.0, False) == "bear"
    assert classify_regime(35.0, False) == "bear"
    assert classify_regime(39.9, False) == "bear"  # just under crisis


def test_batch642_dead_canonical_line_removed_from_source():
    """Pin (3): the executable code body of classify_regime must NOT
    contain the dead `vix_value >= 30 and spy_above_200ema is False`
    conjunction (the dead canonical line). Pre-B642 the function had
    this line; post-B642 it's gone."""
    import inspect
    from backtest.engine.regime_filter import classify_regime
    src = inspect.getsource(classify_regime)
    # Skip the docstring -- check executable body only
    parts = src.split('"""')
    body = "".join(parts[2:]) if len(parts) >= 3 else src
    # The dead canonical conjunction
    dead_line = "vix_value >= 30 and spy_above_200ema is False"
    assert dead_line not in body, (
        "B642 regression: dead canonical bear line still in classify_regime body"
    )


def test_batch642_bear_at_vix_30_unchanged_via_spy_only_gate():
    """Pin (4): the canonical line being dead code means removing it
    doesn't change behavior. VIX=30 + SPY<200EMA -> bear via the
    Batch 288 SPY-only gate (which catches the same cases)."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(30.0, False) == "bear"
    assert classify_regime(31.5, False) == "bear"


def test_batch642_bull_at_low_vix_above_ema():
    """Pin (5)."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(15.0, True) == "bull"
    assert classify_regime(19.9, True) == "bull"


def test_batch642_neutral_fallback():
    """Pin (6)."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(25.0, True) == "neutral"  # mid-VIX + above EMA


# =================== EMA-cross hysteresis band ===================

def test_batch642_ema_hysteresis_constant_exists():
    """Pin (7)."""
    from backtest.engine.regime_filter import EMA_CROSS_HYSTERESIS_PCT
    assert EMA_CROSS_HYSTERESIS_PCT == 2.0


def test_batch642_with_hysteresis_stays_bear_when_just_barely_above_ema():
    """Pin (8): pre-B642 SPY closing +0.5% above 200-EMA would have
    exited bear immediately. Post-B642 requires >= +2% to confirm exit."""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    # prev=bear, SPY above EMA by 0.5% -- not enough to exit
    out = classify_regime_with_hysteresis(
        vix_value=20.0, spy_above_200ema=True, prev_regime="bear",
        spy_pct_from_200ema=0.5,
    )
    assert out == "bear", f"Expected bear (sticky), got {out}"


def test_batch642_with_hysteresis_exits_bear_when_decisively_above():
    """Pin (9): SPY >= +2% above 200-EMA confirms exit."""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    out = classify_regime_with_hysteresis(
        vix_value=20.0, spy_above_200ema=True, prev_regime="bear",
        spy_pct_from_200ema=3.0,  # > 2%
    )
    # Exits bear; should fall through to bull/neutral
    assert out != "bear", f"Expected exit from bear, got {out}"


def test_batch642_with_hysteresis_enters_bear_immediately():
    """Pin (10): no entry hysteresis -- below-EMA close triggers bear
    immediately (fast risk-off; asymmetric design)."""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    out = classify_regime_with_hysteresis(
        vix_value=22.0, spy_above_200ema=False, prev_regime="neutral",
        spy_pct_from_200ema=-0.3,  # just below EMA
    )
    assert out == "bear", f"Expected immediate bear, got {out}"


def test_batch642_with_hysteresis_legacy_no_pct_falls_back():
    """Pin (11): callers passing spy_pct_from_200ema=None get pre-B642
    binary-gate behavior (backward compat for tests + analytics)."""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    # SPY above EMA, prev=bear, spy_pct=None -> exits via pre-B642 path
    out = classify_regime_with_hysteresis(
        vix_value=20.0, spy_above_200ema=True, prev_regime="bear",
        spy_pct_from_200ema=None,
    )
    # Without the pct, classifier can't enforce the 2% band; falls back
    # to "above 200-EMA exits bear" pre-B642 behavior
    assert out != "bear", f"Legacy no-pct should exit bear; got {out}"


def test_batch642_get_regime_context_computes_pct_from_inputs():
    """Pin (12): get_regime_context computes spy_pct_from_200ema from
    spy_close + spy_ema200 and passes to classifier. We verify by
    constructing a scenario where the EMA hysteresis matters: prev=bear,
    SPY just barely above 200-EMA."""
    from backtest.engine.regime_filter import get_regime_context
    # spy_close = 410, spy_ema200 = 408 -> +0.49% above (below 2% band)
    ctx = get_regime_context(
        vix_value=20.0,
        spy_close=410.0,
        spy_ema200=408.0,
        prev_regime="bear",
        use_hysteresis=True,
    )
    # Should stay bear due to EMA hysteresis (only 0.49% above)
    assert ctx["regime"] == "bear", (
        f"Expected bear sticky via EMA hysteresis; got {ctx['regime']}. "
        f"spy_pct_from_200ema should be ~0.49% (below 2% band)."
    )

    # Confirm a decisive cross does exit
    ctx2 = get_regime_context(
        vix_value=20.0,
        spy_close=425.0,  # > 4% above 408
        spy_ema200=408.0,
        prev_regime="bear",
        use_hysteresis=True,
    )
    assert ctx2["regime"] != "bear", (
        f"Expected exit from bear at +4% cross; got {ctx2['regime']}"
    )
