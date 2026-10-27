"""scripts/camarilla_derived.py - S6-B3304: the DERIVED keys that make
camarilla_r4_breakout's approved offline distance levels gradable.

The gate reads two producer booleans, above_cam_r4 (long) and below_cam_s4
(short), computed by technical.compute_pivots from the PRIOR bar:

  range = prev_high - prev_low
  R4    = prev_close + 1.1 / 2 x range        (production multiplier 0.55)
  S4    = prev_close - 1.1 / 2 x range
  above_cam_r4 = close > R4 ;  below_cam_s4 = close < S4

Today's close is not persisted; it is recovered as vwap x (1 + pct_from_vwap /
100) (technical.py rounds pct_from_vwap to 3 dp and vwap to 4 dp - the
derivability record output_audit/b3304_camarilla_distance_derivability.json
reproduces both legs on 5774 of 5774 R5 fires, 2 inside the rounding bound).
So the breakout at ANOTHER multiplier re-derives from the persisted keys:

  cam_r4_room = (close - prev_close) / range  - the largest multiplier at
                which the bar still closes ABOVE R4; a long fire survives
                multiplier m iff cam_r4_room > m  (axis op gt; tighter =
                higher: 0.55 -> 0.75 / 1.0 / 1.25, the owner's T3 band)
  cam_s4_room = (prev_close - close) / range  - the short mirror; a short
                fire survives m iff cam_s4_room > m

Both are None when an input is missing or the range is zero, so the sweep's
coverage refusal sees the gap instead of a silent default. Used through
offline_level_sweep.py --derive scripts/camarilla_derived.py (S6-B3290b).
"""
from __future__ import annotations

KEYS = ("vwap", "pct_from_vwap", "prev_close", "prev_high", "prev_low")
PRODUCTION_MULT = 1.1 / 2.0


def derive(sig: dict) -> dict:
    """Add cam_r4_room and cam_s4_room to a copy of the persisted signal dict."""
    out = dict(sig)
    try:
        vwap, pfv, pc, ph, pl = (float(sig[k]) for k in KEYS)
    except (KeyError, TypeError, ValueError):
        out["cam_r4_room"] = None
        out["cam_s4_room"] = None
        return out
    rng = ph - pl
    close = vwap * (1.0 + pfv / 100.0)
    out["cam_r4_room"] = ((close - pc) / rng) if rng > 0 else None
    out["cam_s4_room"] = ((pc - close) / rng) if rng > 0 else None
    return out
