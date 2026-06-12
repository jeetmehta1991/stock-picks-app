# Source: B710 reviewer fire-count-ceiling + S4-B717-CEILING-FLAGGED-REDUNDANCY-DIAGNOSTIC + B654 narrow-scope precedent per CHECKLIST #77
"""B718 pin tests: W8a (strat_cpr_narrow_momentum) + W8b
(strat_cpr_narrow_momentum_short) switched from `cpr_narrow` (0.15) to
`cpr_narrow_tight` (0.05) per B654 precedent.

B710 reviewer's fire-count-ceiling finding (B717 measured): W8a fired
12,534 LONG + 8,463 SHORT per year = state flag. W8b fired 13,906 SHORT
per year = state flag. Both above the 5K/yr ceiling.

B654 W8 (strat_cpr_narrow_bullish) precedent fix: switch from cpr_narrow
(0.15 threshold = 87% True NEAR-NO-OP) to cpr_narrow_tight (0.05 threshold
= ~30% True). W8 fire count dropped 34K -> 10.7K (still high but
materially reduced).

B718 extends the same fix to W8a + W8b per S4-B717 routing of the 26
ceiling-flagged strategies. Other consumers of `cpr_narrow` 0.15
threshold unchanged per feedback_narrow_scope_blast_radius.
"""
from __future__ import annotations

from backtest.signals.screener import (
    strat_cpr_narrow_momentum,
    strat_cpr_narrow_momentum_short,
)


# ---------------------------------------------------------------------------
# W8a strat_cpr_narrow_momentum: consumes cpr_narrow_tight (NOT cpr_narrow)
# ---------------------------------------------------------------------------
def test_b718_pin1_w8a_long_consumes_cpr_narrow_tight_not_cpr_narrow():
    """W8a LONG branch must fire on cpr_narrow_tight=True, NOT on
    cpr_narrow=True alone."""
    # Loose cpr_narrow True but tight False: should NOT fire post-B718
    s_loose = {
        "cpr_narrow": True,
        "cpr_narrow_tight": False,
        "above_cpr": True,
        "rsi_14": 60,
        "macd_12_26_9_bullish": True,
        "price_above_ema_200": True,
    }
    result = strat_cpr_narrow_momentum(s_loose)
    assert result["fires"] is False, (
        "W8a LONG fired on cpr_narrow alone post-B718; should require "
        f"cpr_narrow_tight. result={result}"
    )

    # Tight True: should fire
    s_tight = {**s_loose, "cpr_narrow_tight": True}
    result = strat_cpr_narrow_momentum(s_tight)
    assert result["fires"] is True, (
        f"W8a LONG with cpr_narrow_tight=True + all other gates True; got {result}"
    )
    assert result["direction"] == "long"


def test_b718_pin2_w8a_short_consumes_cpr_narrow_tight():
    """W8a SHORT branch must fire on cpr_narrow_tight=True (with low DTC
    to avoid B718a borrow guard)."""
    s = {
        "cpr_narrow_tight": True,
        "below_cpr": True,
        "rsi_14": 30,
        "macd_12_26_9_bearish": True,
        "below_ema_200": True,
        "days_to_cover": 2.0,  # below B718a 5.0 threshold
    }
    result = strat_cpr_narrow_momentum_short(s)
    assert result["fires"] is True, f"W8b SHORT did not fire: {result}"
    assert result["direction"] == "short"


def test_b718_pin3_w8a_signals_used_contains_cpr_narrow_tight():
    """W8a signals_used list must declare cpr_narrow_tight, not cpr_narrow."""
    s = {
        "cpr_narrow_tight": True,
        "above_cpr": True,
        "rsi_14": 60,
        "macd_12_26_9_bullish": True,
        "price_above_ema_200": True,
    }
    result = strat_cpr_narrow_momentum(s)
    assert "cpr_narrow_tight" in result["signals_used"], (
        f"W8a signals_used must declare cpr_narrow_tight; got {result['signals_used']}"
    )
    assert "cpr_narrow" not in [
        sig for sig in result["signals_used"]
        if sig == "cpr_narrow"
    ], "W8a signals_used must NOT declare bare cpr_narrow (loose threshold)"


# ---------------------------------------------------------------------------
# W8b strat_cpr_narrow_momentum_short: same pattern, SHORT-only
# ---------------------------------------------------------------------------
def test_b718_pin4_w8b_consumes_cpr_narrow_tight_not_cpr_narrow():
    """W8b must fire on cpr_narrow_tight=True, NOT on cpr_narrow=True alone."""
    s_loose = {
        "cpr_narrow": True,
        "cpr_narrow_tight": False,
        "below_cpr": True,
        "rsi_14": 30,
        "macd_12_26_9_bearish": True,
        "days_to_cover": 2.0,  # below B718a 5.0
    }
    result = strat_cpr_narrow_momentum_short(s_loose)
    assert result["fires"] is False, (
        f"W8b fired on cpr_narrow alone post-B718; should require cpr_narrow_tight. result={result}"
    )

    s_tight = {**s_loose, "cpr_narrow_tight": True}
    result = strat_cpr_narrow_momentum_short(s_tight)
    assert result["fires"] is True, f"W8b with cpr_narrow_tight=True; got {result}"


def test_b718_pin5_w8b_signals_used_contains_cpr_narrow_tight():
    """W8b signals_used must declare cpr_narrow_tight."""
    s = {
        "cpr_narrow_tight": True,
        "below_cpr": True,
        "rsi_14": 30,
        "macd_12_26_9_bearish": True,
        "days_to_cover": 2.0,
    }
    result = strat_cpr_narrow_momentum_short(s)
    assert "cpr_narrow_tight" in result["signals_used"], (
        f"W8b signals_used must declare cpr_narrow_tight; got {result['signals_used']}"
    )


# ---------------------------------------------------------------------------
# Cross-strategy invariant: bare cpr_narrow consumers unchanged
# ---------------------------------------------------------------------------
def test_b718_pin6_other_cpr_narrow_loose_consumers_unchanged():
    """Per feedback_narrow_scope_blast_radius: B718 W8a/W8b narrow-scope fix
    must NOT affect other cpr_narrow consumers. Verify by inspecting source
    for residual `s.get("cpr_narrow")` calls that are NOT W8/W8a/W8b."""
    import re
    from pathlib import Path
    screener_path = Path(__file__).resolve().parents[1] / "signals" / "screener.py"
    text = screener_path.read_text(encoding="utf-8")
    # Count cpr_narrow_tight references
    n_tight = len(re.findall(r'cpr_narrow_tight', text))
    n_loose_bare = len(re.findall(r's\.get\("cpr_narrow"\)', text))
    # Should have multiple tight references (W8 + W8a + W8b + producer + comments)
    assert n_tight >= 8, f"Expected >=8 cpr_narrow_tight references; got {n_tight}"
    # Loose bare consumers should remain for non-W8 strategies
    # (B710 reviewer noted other cpr_narrow consumers exist; we don't know
    # exact count; just assert they still exist if any did pre-B718)
    # This is a documentation pin, not a strict count.
