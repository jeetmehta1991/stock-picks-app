"""Batch 665 (2026-06-09) -- 2nd-wave-redux critique response: 12-item
bundled batch (#1-#10 doc revisions; #6 + #8 code changes; #11 = this
test file; #12 = pyramid+commit).

This file pins the two CODE changes (#6 + #8). Doc revisions are not
test-pinnable (informational text).

Pins:

  #6 W5 regime affinity tighten (revert B651 over-correction):
    (1)  STRATEGY_REGIME_AFFINITY['pivot_s3_capitulation'] is now
         {neutral, bear, crisis} (NOT {bull, neutral, bear, crisis})
    (2)  should_strategy_fire_in_regime returns False for bull
         (the bull-tape S3 capitulation = idiosyncratic falling-knife
         per 2nd-wave-redux #6 + C5 survivorship class)
    (3)  should_strategy_fire_in_regime returns True for neutral/bear/crisis

  #8 R3 EMA-cross hysteresis revert (unvalidated directional bet):
    (4)  EMA_CROSS_HYSTERESIS_PCT == 0.0 (symmetric baseline; was 2.0
         asymmetric sticky-bear)
    (5)  classify_regime_with_hysteresis with prev_regime='bear' AND
         spy_above_200ema=True returns 'neutral'/'bull' (NOT 'bear') --
         the +2% sticky-bear delay is now off
    (6)  classify_regime_with_hysteresis with prev_regime='bear' AND
         spy_above_200ema=False returns 'bear' (entry-side still works)

  Bundle / regression-block:
    (7)  No `EMA_CROSS_HYSTERESIS_PCT = 2.0` literal in regime_filter.py
         (would re-introduce the sticky-bear bet without owner approval)
"""
from __future__ import annotations


# ============ #6 W5 regime tighten pins (3) ============

def test_batch665_w5_regime_affinity_excludes_bull():
    """Pin (1): post-B665 W5 regime affinity is {neutral, bear, crisis}.

    Reverts B651 expansion to all-regimes per 2nd-wave-redux critique #6.
    The bull-tape S3 capitulation with RSI<30 is an idiosyncratic falling-
    knife event (C5 survivorship class)."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    expected = {"neutral", "bear", "crisis"}
    actual = STRATEGY_REGIME_AFFINITY.get("pivot_s3_capitulation")
    assert actual == expected, (
        f"B665 regression: W5 regime affinity is {actual} but should be "
        f"{expected} per 2nd-wave-redux #6 (bull-tape S3 = falling-knife)."
    )


def test_batch665_w5_does_not_fire_in_bull_regime():
    """Pin (2): W5 should NOT fire in bull per the regime-affinity gate."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    fires = should_strategy_fire_in_regime(
        "pivot_s3_capitulation", "bull", direction="long"
    )
    assert fires is False, (
        "B665 regression: W5 fires in bull regime; should be blocked per "
        "the {neutral, bear, crisis} affinity"
    )


def test_batch665_w5_fires_in_neutral_bear_crisis():
    """Pin (3): W5 fires in the 3 approved regimes."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for regime in ("neutral", "bear", "crisis"):
        fires = should_strategy_fire_in_regime(
            "pivot_s3_capitulation", regime, direction="long"
        )
        assert fires is True, (
            f"B665 regression: W5 does NOT fire in {regime}; should fire per "
            "the {neutral, bear, crisis} affinity"
        )


# ============ #8 R3 hysteresis revert pins (3) ============

def test_batch665_ema_cross_hysteresis_pct_is_zero():
    """Pin (4): EMA_CROSS_HYSTERESIS_PCT == 0.0 (symmetric).

    Reverts B642 sticky-bear directional bet per 2nd-wave-redux #8.
    Unvalidated curve-fit-to-2022 bets default OFF in pre-deployment
    systems; the asymmetry returns only if S5-REGIME-WALK-FORWARD-
    VALIDATION shows it earns its keep OOS."""
    from backtest.engine.regime_filter import EMA_CROSS_HYSTERESIS_PCT
    assert EMA_CROSS_HYSTERESIS_PCT == 0.0, (
        f"B665 regression: EMA_CROSS_HYSTERESIS_PCT = {EMA_CROSS_HYSTERESIS_PCT} "
        "but should be 0.0 (symmetric baseline) per 2nd-wave-redux #8. "
        "If walk-forward validates the asymmetry, re-enable with documented "
        "empirical support."
    )


def test_batch665_bear_exits_immediately_when_spy_above_200ema():
    """Pin (5): prev_regime='bear' + spy_above_200ema=True exits bear
    immediately (no +2% sticky-bear delay).

    With +2%% off, a SPY close of +0.5%% above 200-EMA exits bear --
    pre-B665 it would have held bear until +2%% confirmed."""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    # VIX in neutral range; SPY just barely above 200-EMA (+0.5%)
    regime = classify_regime_with_hysteresis(
        vix_value=22.0,  # neutral range
        spy_above_200ema=True,
        prev_regime="bear",
        spy_pct_from_200ema=0.5,  # within pre-B665 sticky-bear band
    )
    assert regime != "bear", (
        f"B665 regression: prev=bear + SPY +0.5%% above EMA stayed in bear "
        f"(got {regime}). Post-B665 symmetric: any close above 200-EMA "
        "exits bear; the +2%% delay is off."
    )


def test_batch665_bear_entry_still_works_on_below_200ema():
    """Pin (6): symmetric revert preserves FAST entry into bear when SPY
    closes below 200-EMA. (Asymmetric design wasn't bidirectional --
    only sticky on EXIT, not on ENTRY -- so this test just regresses
    against breakage on the entry side.)"""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    regime = classify_regime_with_hysteresis(
        vix_value=25.0,
        spy_above_200ema=False,
        prev_regime="neutral",
        spy_pct_from_200ema=-2.0,
    )
    assert regime in ("bear", "crisis"), (
        f"B665 regression: prev=neutral + SPY below 200-EMA did NOT enter "
        f"bear (got {regime}). Bear entry should still trigger on below-EMA "
        "close (B665 only reverts the EXIT-side hysteresis)."
    )


# ============ Bundle / regression-block (1) ============

def test_batch665_no_sticky_bear_literal_remains():
    """Pin (7): regime_filter.py contains no `EMA_CROSS_HYSTERESIS_PCT = 2.0`
    literal in executable code.

    Regression-block: any future edit that re-introduces the sticky-bear
    bet without owner approval (and without walk-forward validation
    landing) trips this pin."""
    from pathlib import Path
    src = (Path(__file__).parent.parent / "engine" / "regime_filter.py").read_text(
        encoding="utf-8"
    )
    # Strip docstrings (triple-quoted strings) + comment lines first
    import re
    src_no_doc = re.sub(r'"""[\s\S]*?"""', "", src)
    code_lines = []
    for ln in src_no_doc.splitlines():
        if "#" in ln:
            ln = ln.split("#", 1)[0]
        code_lines.append(ln)
    code = "\n".join(code_lines)
    bad_pattern = "EMA_CROSS_HYSTERESIS_PCT = 2.0"
    assert bad_pattern not in code, (
        f"B665 regression: `{bad_pattern}` is back in executable code. "
        "Reverting B665 #8 (sticky-bear directional bet) without owner "
        "approval and walk-forward validation is not permitted."
    )
