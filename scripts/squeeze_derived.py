"""scripts/squeeze_derived.py - S6-B3248 / S6-B3289 step 6: the DERIVED keys
that make squeeze_breakout's two approved offline levels gradable.

The gate reads one producer boolean, squeeze_fire_up, whose squeeze test is
`in_squeeze = bb_20_20_lower > kc_lower and bb_20_20_upper < kc_upper`
(technical.py compute_squeeze) at the production geometry: Bollinger (20,
2.0) and Keltner (20, 2.0 x ATR20). The fire requires NOT in_squeeze on the
fire bar. The persisted keys are the four band edges and kc_mid, so the
squeeze test at ANOTHER multiplier re-derives from them:

  ATR20            = (kc_upper - kc_mid) / 2.0          (production KC mult 2.0)
  kc_room          = max((bb_upper - kc_mid), (kc_mid - bb_lower)) / ATR20
                     - the largest Keltner multiplier at which the fire bar is
                       still OUTSIDE the squeeze; a fire survives KC mult m iff
                       kc_room >= m  (axis op ge; tighter = higher: 2.0 -> 2.5)
  sd20             = (bb_upper - bb_lower) / 4.0        (production BB mult 2.0)
  bb_mid           = (bb_upper + bb_lower) / 2.0
  bb_room          = min((kc_upper - bb_mid), (bb_mid - kc_lower)) / sd20
                     - the smallest Bollinger multiplier at which the fire bar
                       is still outside the squeeze; a fire survives BB mult k
                       iff bb_room <= k  (axis op le; tighter = lower: 2.0 -> 1.5)

Both are None when any edge is missing or a width is zero, so the sweep's
coverage refusal sees the gap instead of a silent default. Used through
offline_level_sweep.py --derive scripts/squeeze_derived.py (S6-B3290b).
"""
from __future__ import annotations

KEYS = ("bb_20_20_lower", "bb_20_20_upper", "kc_lower", "kc_upper", "kc_mid")
PRODUCTION_KC_MULT = 2.0
PRODUCTION_BB_MULT = 2.0


def derive(sig: dict) -> dict:
    """Add kc_room and bb_room to a copy of the persisted signal dict."""
    out = dict(sig)
    try:
        bl, bu, kl, ku, km = (float(sig[k]) for k in KEYS)
    except (KeyError, TypeError, ValueError):
        out["kc_room"] = None
        out["bb_room"] = None
        return out
    atr = (ku - km) / PRODUCTION_KC_MULT
    sd = (bu - bl) / (2.0 * PRODUCTION_BB_MULT)
    bmid = (bu + bl) / 2.0
    out["kc_room"] = (max(bu - km, km - bl) / atr) if atr > 0 else None
    out["bb_room"] = (min(ku - bmid, bmid - kl) / sd) if sd > 0 else None
    return out
