"""Batch 656 (2026-06-09) -- T3 strat_hull_rsi redundancy-audit option
A+C per 2nd-wave external-AI critique #2 + owner directive 2026-06-09.

AUDIT FINDING (different from W8/T10): T3 hull_rsi has NO extreme
no-op gate. All 5 marginals 38-53% True. Pairwise correlations
honest-confluence (hull_bullish x price_above_hull = +0.41 because
both measure Hull-MA uptrend semantics from distinct angles -- slope
vs current position; not redundant). Per critique #2 corrected
methodology: T3 is honest STATE composite, NOT redundancy.

OPTION A: status quo on 4-distinct-gate confluence structure.
OPTION C: drop rsi_9>50/<50 strict-inequality on default-50 -- same
accidentally-safe no-op pattern that B654 closed for W8 RSI.
Combined as A+C.

POST-B656 GATE SET (4 distinct gates per direction):
  LONG:  hull_bullish + price_above_hull + adx>20 + price_above_ema_200
  SHORT: hull_bearish + price_below_hull + adx>20 + below-200-EMA

OPEN (queued, not auto-fixed B656 per CHECKLIST g):
  SHORT side still uses `(not above_200)` NOT-pattern silent-gap.
  Queued as `S4-T3-NOT-ABOVE-200-EMA-PATTERN` for separate decision.

Pins:
  (1)  strat_hull_rsi LONG fires WITHOUT rsi_9 in fixture
       (gate dropped; other 4 gates True -> fires)
  (2)  strat_hull_rsi LONG fires when rsi_9 = 50 (boundary value
       that pre-B656 would have failed strict > check)
  (3)  strat_hull_rsi LONG does NOT fire on rsi_9 alone (no other
       gates True; proves the strategy doesn't fire just on rsi_9)
  (4)  strat_hull_rsi SHORT fires WITHOUT rsi_9 in fixture
  (5)  strat_hull_rsi executable body no longer reads rsi_9
  (6)  Strategy still requires ADX>20 (B207 gate preserved)
  (7)  Strategy still requires price_above_ema_200 LONG / NOT
       above_ema_200 SHORT (B358 gate preserved)
"""
from __future__ import annotations


def test_batch656_long_fires_without_rsi_9_in_fixture():
    """Pin (1)."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bullish": True,
        "price_above_hull": True,
        "adx": 25.0,
        "price_above_ema_200": True,
        # NO rsi_9 key -- B656 strategy no longer reads it
    }
    out = strat_hull_rsi(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch656_long_fires_at_rsi_9_boundary_50():
    """Pin (2): rsi_9 = 50 boundary value. Pre-B656 the strict
    `rsi_9>50` check would fail (50 > 50 is False); post-B656 the
    gate is gone so strategy fires anyway."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bullish": True,
        "price_above_hull": True,
        "adx": 25.0,
        "price_above_ema_200": True,
        "rsi_9": 50.0,
    }
    out = strat_hull_rsi(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch656_long_does_NOT_fire_with_only_rsi_9_no_other_gates():
    """Pin (3): rsi_9>50 alone doesn't fire (strategy still requires
    hull + price_above_hull + adx + 200_ema)."""
    from backtest.signals.screener import strat_hull_rsi
    s = {"rsi_9": 75.0}
    # No hull / no price_above_hull / no adx / no 200ema
    assert strat_hull_rsi(s)["fires"] is False


def test_batch656_short_fires_without_rsi_9():
    """Pin (4). B659 update: SHORT side now uses positive symmetric
    `below_ema_200` (was `(not above_200)` NOT-pattern silent-gap pre
    -B659). Fixture extended."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25.0,
        "below_ema_200": True,  # B659: positive symmetric replaces `(not above_200)`
    }
    out = strat_hull_rsi(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch656_executable_body_no_longer_reads_rsi_9():
    """Pin (5): strategy code body must not read rsi_9 (was the only
    rsi_9 consumer; drop is clean)."""
    import inspect
    from backtest.signals.screener import strat_hull_rsi
    src = inspect.getsource(strat_hull_rsi)
    parts = src.split('"""')
    body = "".join(parts[2:]) if len(parts) >= 3 else src
    # Strip comment lines
    code_lines = [ln for ln in body.splitlines() if not ln.strip().startswith("#")]
    code = "\n".join(code_lines)
    assert 's.get("rsi_9"' not in code, (
        "B656 regression: rsi_9 still read in T3 hull_rsi executable code"
    )


def test_batch656_adx_gate_preserved():
    """Pin (6): B207 ADX>20 gate must still be enforced post-B656."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bullish": True,
        "price_above_hull": True,
        "adx": 15.0,  # below B207 threshold
        "adx_trending": False,
        "price_above_ema_200": True,
    }
    assert strat_hull_rsi(s)["fires"] is False


def test_batch656_b358_200_ema_gate_preserved_long():
    """Pin (7) LONG: B358 200-EMA bear-block gate must still be
    enforced post-B656."""
    from backtest.signals.screener import strat_hull_rsi
    s = {
        "hull_bullish": True,
        "price_above_hull": True,
        "adx": 25.0,
        "price_above_ema_200": False,  # B358 gate FAILS
    }
    assert strat_hull_rsi(s)["fires"] is False
