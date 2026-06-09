"""Batch 663 (2026-06-09) -- `price_above_ema_200` default-True silent-gap
family-bug sweep per owner directive option (delta) "full screener sweep"
2026-06-09.

This is the largest single-pattern family-bug fix to date. Owner-approved
(delta) full-screener-scope after pre-flight grep revealed 70 occurrences
of `s.get("price_above_ema_200", True)` -- 70 strategies with the same
B659-class silent-gap pattern (LONG side auto-passes regime-gate when
key absent).

ALSO addresses 7 (not above_200) NOT-pattern silent-gap cases (originally
5 identified from default-True local-vars + 2 additional surfaced during
pre-flight that had default-False local-var but still used NOT-pattern --
ALL violated `feedback_never_use_NOT_s_get_pattern` regardless of default).

NOT addressed in this batch (per F3 audit during pre-flight):
- 10 exclude-crisis regime affinity entries in regime_selector.py. All
  10 have documented lineage (B263 empirical Phase 1A-alpha override of
  literature thesis OR B271 SMC framework consistency). No deletions.
  SM-1 walk's original F3 finding was a CHECKLIST violation -- should
  have grep'd lineage comments BEFORE proposing the delete; corrected
  in this batch.

Pins:
  Direct-gate sample pins (5):
  (1)  strat_insider_cluster_long (SM-1) does NOT fire LONG without
       price_above_ema_200 key (post-B663 default-False)
  (2)  strat_xs_momentum_top_decile does NOT fire LONG without
       price_above_ema_200 key
  (3)  strat_pivot_s1_bounce (W3) does NOT fire LONG without
       price_above_ema_200 key
  (4)  strat_pead_long does NOT fire LONG without price_above_ema_200 key
  (5)  strat_institutional_cluster_long (SM-7 13F sleeve sample) does
       NOT fire LONG without price_above_ema_200 key

  Local-var NOT-pattern isolation pins (7 strategies):
  (6)  strat_stochrsi_oversold SHORT does NOT fire on (rsi cross + below_sma)
       without below_ema_200 key (post-B663 positive symmetric)
  (7)  strat_rsi_oversold SHORT does NOT fire without below_ema_200 key
  (8)  strat_bollinger_lower SHORT does NOT fire without below_ema_200 key
  (9)  strat_bollinger_tight SHORT does NOT fire without below_ema_200 key
  (10) strat_smc_inverse_fvg SHORT does NOT fire without below_ema_200 key
  (11) strat_williams_r_oversold SHORT does NOT fire without below_ema_200 key
       (was default-False local-var but still NOT-pattern; pre-flight surfaced)
  (12) strat_cpr_narrow_momentum SHORT does NOT fire without below_ema_200 key
       (was default-False local-var but still NOT-pattern; pre-flight surfaced)

  Bundle assertions:
  (13) screener.py executable code contains 0 `s.get("price_above_ema_200", True)`
       patterns (regression-block: family-bug must not recur)
  (14) screener.py executable code contains 0 `(not above_200)` patterns
       (positive-symmetric required per feedback_never_use_NOT_s_get_pattern)
"""
from __future__ import annotations


# ============ Direct-gate sample pins (5) ============

def test_batch663_insider_cluster_long_blocked_without_ema_200_key():
    """Pin (1): SM-1 insider_cluster_long does NOT fire LONG when
    price_above_ema_200 key is absent (post-B663 default-False)."""
    from backtest.signals.screener import strat_insider_cluster_long
    # All gates satisfied EXCEPT regime gate key absent
    s = {
        "insider_cluster_active": True,
        "insider_unique_buyers_30d": 3,
        # No price_above_ema_200 key -- post-B663 default-False -> fail-safe
    }
    assert strat_insider_cluster_long(s)["fires"] is False


def test_batch663_xs_momentum_top_decile_blocked_without_ema_200_key():
    """Pin (2): xs_momentum_top_decile factor strategy does NOT fire LONG
    without price_above_ema_200 key (post-B663 default-False)."""
    from backtest.signals.screener import strat_xs_momentum_top_decile
    s = {
        "xs_momentum_top_decile": True,
        # No price_above_ema_200 key
    }
    assert strat_xs_momentum_top_decile(s)["fires"] is False


def test_batch663_xs_quality_top_quintile_long_blocked_without_ema_200_key():
    """Pin (3): strat_xs_quality_top_quintile_long (2-gate factor) does
    NOT fire LONG without price_above_ema_200 key.

    Note: original pin-3 target was pivot_s1_bounce (W3) but that
    strategy uses near_s1+hammer+obv gates, NOT price_above_ema_200 --
    fixture would not exercise the B663 fix. Swapped to
    xs_quality_top_quintile_long which is a clean 2-gate strategy with
    explicit price_above_ema_200 consumption."""
    from backtest.signals.screener import strat_xs_quality_top_quintile_long
    s = {
        "xs_quality_top_quintile": True,
        # No price_above_ema_200 key -- post-B663 default-False -> fail-safe
    }
    out = strat_xs_quality_top_quintile_long(s)
    assert out["fires"] is False


def test_batch663_pead_long_blocked_without_ema_200_key():
    """Pin (4): strat_pead_long does NOT fire LONG without
    price_above_ema_200 key."""
    from backtest.signals.screener import strat_pead_long
    s = {
        "pead_positive_surprise": True,
        # No price_above_ema_200 key
    }
    out = strat_pead_long(s)
    assert out["fires"] is False


def test_batch663_institutional_cluster_long_blocked_without_ema_200_key():
    """Pin (5): SM-7 institutional_cluster_long does NOT fire LONG
    without price_above_ema_200 key."""
    from backtest.signals.screener import strat_institutional_cluster_long
    s = {
        "institutional_cluster_active": True,
        # No price_above_ema_200 key
    }
    out = strat_institutional_cluster_long(s)
    assert out["fires"] is False


# ============ Local-var NOT-pattern isolation pins (7) ============

def test_batch663_stochrsi_oversold_short_blocked_without_below_ema_200_key():
    """Pin (6): strat_stochrsi_oversold SHORT does NOT fire without
    below_ema_200 key (post-B663 positive symmetric replaces
    `(not above_200)` NOT-pattern silent-gap)."""
    from backtest.signals.screener import strat_stochrsi_oversold
    s = {
        "stochrsi_overbought": True,
        "stochrsi_cross_dn": True,
        "rsi_14": 50.0,  # > 45 condition
        # No price_above_ema_200 key AND no below_ema_200 key
    }
    out = strat_stochrsi_oversold(s)
    assert out["fires"] is False


def test_batch663_rsi_oversold_short_blocked_without_below_ema_200_key():
    """Pin (7): strat_rsi_oversold SHORT does NOT fire without below_ema_200."""
    from backtest.signals.screener import strat_rsi_oversold
    s = {
        "rsi_2": 96.0,  # > 95 condition
        "below_sma_50": True,
        # No below_ema_200 key
    }
    out = strat_rsi_oversold(s)
    assert out["fires"] is False


def test_batch663_bollinger_lower_short_blocked_without_below_ema_200_key():
    """Pin (8): strat_bollinger_lower SHORT does NOT fire without below_ema_200."""
    from backtest.signals.screener import strat_bollinger_lower
    s = {
        "bb_20_20_touch_upper": True,
        "rsi_2": 96.0,
        "adx": 25.0,
        # No below_ema_200 key
    }
    out = strat_bollinger_lower(s)
    assert out["fires"] is False


def test_batch663_bollinger_tight_short_blocked_without_below_ema_200_key():
    """Pin (9): strat_bollinger_tight SHORT does NOT fire without below_ema_200."""
    from backtest.signals.screener import strat_bollinger_tight
    s = {
        "bb_20_15_touch_upper": True,
        "rsi_2": 96.0,
        # No below_ema_200 key
    }
    out = strat_bollinger_tight(s)
    assert out["fires"] is False


def test_batch663_smc_inverse_fvg_short_blocked_without_below_ema_200_key():
    """Pin (10): strat_smc_inverse_fvg SHORT does NOT fire without below_ema_200."""
    from backtest.signals.screener import strat_smc_inverse_fvg
    s = {
        "smc_inverse_fvg_bearish": True,
        "vol_spike_2x": True,
        # No below_ema_200 key
    }
    out = strat_smc_inverse_fvg(s)
    assert out["fires"] is False


def test_batch663_williams_r_oversold_short_blocked_without_below_ema_200_key():
    """Pin (11): strat_williams_r_oversold SHORT does NOT fire without
    below_ema_200 key (was pre-flight-surfaced NOT-pattern case despite
    default-False local-var)."""
    from backtest.signals.screener import strat_williams_r_oversold
    s = {
        "rsi_2": 96.0,  # > 95
        "cmf_negative": True,
        # No below_ema_200 key (and Williams %R defaults to 0 which is > -20)
    }
    out = strat_williams_r_oversold(s)
    assert out["fires"] is False


def test_batch663_cpr_narrow_momentum_short_blocked_without_below_ema_200_key():
    """Pin (12): strat_cpr_narrow_momentum SHORT does NOT fire without
    below_ema_200 key (was pre-flight-surfaced NOT-pattern case despite
    default-False local-var)."""
    from backtest.signals.screener import strat_cpr_narrow_momentum
    s = {
        "cpr_narrow": True,
        "below_cpr": True,
        "rsi_14": 40.0,  # < 50
        "macd_12_26_9_bearish": True,
        # No below_ema_200 key
    }
    out = strat_cpr_narrow_momentum(s)
    assert out["fires"] is False


# ============ Bundle assertions (2) ============

def test_batch663_no_default_true_price_above_ema_200_pattern_remains():
    """Pin (13): screener.py executable code contains 0
    `s.get("price_above_ema_200", True)` patterns. Family-bug
    regression-block."""
    from pathlib import Path
    src = (Path(__file__).parent.parent / "signals" / "screener.py").read_text(
        encoding="utf-8")
    # Strip the module docstring + per-function docstrings + comments before
    # the executable-code grep. Naive: find triple-quoted strings + comment
    # lines, exclude them.
    import re
    # Remove triple-quoted strings
    src_no_doc = re.sub(r'"""[\s\S]*?"""', "", src)
    # Remove comment lines
    code_lines = [
        ln for ln in src_no_doc.splitlines() if not ln.strip().startswith("#")
    ]
    code = "\n".join(code_lines)
    bad_pattern = 's.get("price_above_ema_200", True)'
    assert bad_pattern not in code, (
        f"B663 regression: `{bad_pattern}` still present in executable code -- "
        "family-bug must not recur. Use default-False symmetric with B659 policy."
    )


def test_batch663_no_not_above_200_pattern_remains():
    """Pin (14): screener.py executable code contains 0 `(not above_200)`
    patterns -- positive-symmetric `below_200` from `below_ema_200` is
    required per feedback_never_use_NOT_s_get_pattern."""
    from pathlib import Path
    src = (Path(__file__).parent.parent / "signals" / "screener.py").read_text(
        encoding="utf-8")
    import re
    # Strip docstrings (triple-quoted strings) first
    src_no_doc = re.sub(r'"""[\s\S]*?"""', "", src)
    # Then strip everything from `#` to end-of-line per line (catches both
    # leading-# comment lines AND inline trailing-# comments where the
    # B659/B663 history mentions `(not above_200)` in narration)
    code_lines = []
    for ln in src_no_doc.splitlines():
        # Find first `#` not inside a string literal -- naive split is OK
        # because earlier docstring-strip removed triple-quoted blocks
        if "#" in ln:
            ln = ln.split("#", 1)[0]
        code_lines.append(ln)
    code = "\n".join(code_lines)
    bad_pattern = "(not above_200)"
    assert bad_pattern not in code, (
        f"B663 regression: `{bad_pattern}` still present in executable code -- "
        "use positive symmetric `below_200 = s.get('below_ema_200', False)` per "
        "feedback_never_use_NOT_s_get_pattern. NOT-pattern silent-gap risk."
    )
