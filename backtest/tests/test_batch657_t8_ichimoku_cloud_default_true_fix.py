"""Batch 657 (2026-06-09) -- T8 strat_ichimoku_cloud_breakout
redundancy-audit option E per 2nd-wave external-AI critique #2 +
owner directive 2026-06-09.

AUDIT FINDING: T8 has NO extreme NO-OP gate (all 4 gates 38-51%
True; honest confluence like T3). Per option A: status quo on
confluence structure. BUT the weekly Kumo gate had DEFAULT-TRUE
silent-gap (same class as W6/W7/W8 LONG AVWAP defaults queued in
S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY). Per option D: swap default
True -> False on both weekly_long_ok / weekly_short_ok.

Pins:
  (1)  strat_ichimoku_cloud_breakout LONG no longer fires when
       weekly Kumo signals MISSING (default-False enforces multi-TF
       confirmation)
  (2)  strat_ichimoku_cloud_breakout LONG fires when weekly Kumo
       signals EMITTED + other 3 gates True
  (3)  strat_ichimoku_cloud_breakout SHORT no longer fires when
       weekly Kumo MISSING (mirror of pin 1)
  (4)  strat_ichimoku_cloud_breakout SHORT fires when weekly Kumo
       below_cloud emitted + other 3 gates
  (5)  Executable code uses `s.get("ichi_weekly_above_cloud", False)`
       not `True`
  (6)  Existing 4-gate confluence structure preserved (no other
       changes; option A status-quo)
"""
from __future__ import annotations


def test_batch657_long_blocked_when_weekly_missing():
    """Pin (1): default-False semantics. Pre-B657 missing weekly key
    auto-passed; post-B657 it fail-safes to no-fire."""
    from backtest.signals.screener import strat_ichimoku_cloud_breakout
    s = {
        "ichi_above_cloud": True,
        "ichi_tk_bullish": True,
        "adx_trending": True,
        # NO ichi_weekly_above_cloud -- defaults False now
    }
    out = strat_ichimoku_cloud_breakout(s)
    assert out["fires"] is False, (
        "B657 regression: T8 LONG fires when weekly Kumo data missing "
        "(pre-B657 default-True silent-gap pattern)"
    )


def test_batch657_long_fires_when_weekly_emitted():
    """Pin (2): with all 4 gates True the strategy fires LONG.
    B820 update: B725 STATE -> EVENT conversion -- ichi_above_cloud ->
    ichi_above_cloud_break_recent_5d."""
    from backtest.signals.screener import strat_ichimoku_cloud_breakout
    s = {
        "ichi_above_cloud_break_recent_5d": True,  # B725 EVENT
        "ichi_tk_bullish": True,
        "adx_trending": True,
        "ichi_weekly_above_cloud": True,
    }
    out = strat_ichimoku_cloud_breakout(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch657_short_blocked_when_weekly_missing():
    """Pin (3): mirror of pin 1 for SHORT side."""
    from backtest.signals.screener import strat_ichimoku_cloud_breakout
    s = {
        "ichi_below_cloud": True,
        "ichi_tk_bearish": True,
        "adx_trending": True,
        # NO ichi_weekly_below_cloud
    }
    assert strat_ichimoku_cloud_breakout(s)["fires"] is False


def test_batch657_short_fires_when_weekly_below_cloud():
    """Pin (4). B820: B725 STATE -> EVENT -- ichi_below_cloud ->
    ichi_below_cloud_break_recent_5d."""
    from backtest.signals.screener import strat_ichimoku_cloud_breakout
    s = {
        "ichi_below_cloud_break_recent_5d": True,  # B725 EVENT
        "ichi_tk_bearish": True,
        "adx_trending": True,
        "ichi_weekly_below_cloud": True,
    }
    out = strat_ichimoku_cloud_breakout(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch657_executable_code_uses_default_false():
    """Pin (5): the executable code body must use default-False
    (`s.get(..., False)`) on both weekly Kumo gates, not the pre-
    B657 default-True silent-gap pattern."""
    import inspect
    from backtest.signals.screener import strat_ichimoku_cloud_breakout
    src = inspect.getsource(strat_ichimoku_cloud_breakout)
    parts = src.split('"""')
    body = "".join(parts[2:]) if len(parts) >= 3 else src
    # Strip comment lines
    code_lines = [ln for ln in body.splitlines() if not ln.strip().startswith("#")]
    code = "\n".join(code_lines)
    assert 's.get("ichi_weekly_above_cloud", True)' not in code, (
        "B657 regression: default-True pattern still in T8 LONG weekly"
    )
    assert 's.get("ichi_weekly_below_cloud", True)' not in code, (
        "B657 regression: default-True pattern still in T8 SHORT weekly"
    )
    assert 's.get("ichi_weekly_above_cloud", False)' in code
    assert 's.get("ichi_weekly_below_cloud", False)' in code


def test_batch657_confluence_structure_preserved():
    """Pin (6): option A status-quo on the 4-gate confluence
    structure. B820: B725 STATE -> EVENT -- ichi_above_cloud_break
    _recent_5d replaces ichi_above_cloud."""
    from backtest.signals.screener import strat_ichimoku_cloud_breakout
    # Verify each individual gate still blocks LONG when missing
    # (preserves confluence semantics)
    base = {
        "ichi_above_cloud_break_recent_5d": True,  # B725 EVENT
        "ichi_tk_bullish": True,
        "adx_trending": True,
        "ichi_weekly_above_cloud": True,
    }
    # All True -> fires
    assert strat_ichimoku_cloud_breakout(base)["fires"] is True
    # Each gate individually missing -> blocks
    for gate in ("ichi_above_cloud_break_recent_5d", "ichi_tk_bullish", "adx_trending"):
        s = {k: v for k, v in base.items() if k != gate}
        assert strat_ichimoku_cloud_breakout(s)["fires"] is False, (
            f"B657: missing {gate} should block LONG (confluence preserved)"
        )
