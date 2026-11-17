"""scripts/tema_derived.py - S6-B3423: the DERIVED key that makes tema_dema's
registered offline buffer levels gradable (SPECS_PHASE0 tema_dema P5, 'buffer
above TEMA (LONG)', free_band 0.0 / 0.01 / 0.02 / 0.03).

The long gate reads one producer boolean, price_above_tema, computed by
technical.compute_dema_tema as close > tema (tema persisted at 4 dp). Today's
close is not persisted; it is recovered as vwap x (1 + pct_from_vwap / 100)
(technical.py rounds pct_from_vwap to 3 dp and vwap to 4 dp - the
camarilla_derived precedent, S6-B3304). So the gate at ANOTHER buffer
re-derives from the persisted keys:

  tema_buffer = close / tema - 1  - the largest buffer b at which the bar still
                closes ABOVE tema x (1 + b); a long fire survives buffer b iff
                tema_buffer > b (axis op gt; tighter = higher: 0.0 -> 0.01 /
                0.02 / 0.03, the registered band). At b = 0.0 the axis is the
                production gate itself, which the sweep's reproduction gate
                checks on every run.

None when an input is missing or tema is not positive, so the sweep's coverage
refusal sees the gap instead of a silent default. Used through
offline_level_sweep.py --derive scripts/tema_derived.py (S6-B3290b).
"""
from __future__ import annotations

KEYS = ("vwap", "pct_from_vwap", "tema")


def derive(sig: dict) -> dict:
    """Add tema_buffer to a copy of the persisted signal dict."""
    out = dict(sig)
    try:
        vwap, pfv, tema = (float(sig[k]) for k in KEYS)
    except (KeyError, TypeError, ValueError):
        out["tema_buffer"] = None
        return out
    if tema <= 0:
        out["tema_buffer"] = None
        return out
    close = vwap * (1.0 + pfv / 100.0)
    out["tema_buffer"] = close / tema - 1.0
    return out
