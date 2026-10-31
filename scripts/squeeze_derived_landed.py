"""scripts/squeeze_derived_landed.py - S6-B3248 (B3139q-r163): squeeze_breakout's
derived squeeze rooms at the LANDED knob vector of an engine run, for the
free-level leg of every landing (B2569).

WHY A SECOND MODULE. scripts/squeeze_derived.py derives the rooms at the
production geometry (Keltner multiplier 2.0, Bollinger std 2.0), and the
depth sweep that pre-registered squeeze's holdout read recorded that file's
sha256 - offline_holdout_read refuses a read whose derivation changed since
(S6-B3294). Editing it would void that record, so it stays byte-identical
and this module generalises it; at production the two agree exactly
(test_b3248g).

THE ALGEBRA. The persisted keys are compute_bollinger's bb_20_20 edges and
compute_keltner's kc_lower / kc_upper / kc_mid - production geometry, the
published keys no SQUEEZE_* knob moves (test_b3248d). From them:
  atr  = (kc_upper - kc_mid) / 2.0          sd = (bb_upper - bb_lower) / 4.0
  bmid = (bb_upper + bb_lower) / 2.0
A bar is OUT of the squeeze at Keltner multiplier m and Bollinger std k iff
bmid - k sd <= kc_mid - m atr  or  bmid + k sd >= kc_mid + m atr, so at the
landed pair (m0, k0):
  kc_room = max(bmid + k0 sd - kc_mid, kc_mid - bmid + k0 sd) / atr
            - a fire survives Keltner multiplier m iff kc_room >= m
  bb_room = min(kc_mid + m0 atr - bmid, bmid - kc_mid + m0 atr) / sd
            - a fire survives Bollinger std k iff bb_room <= k
At (2.0, 2.0) these are squeeze_derived.derive's kc_room and bb_room.

WHEN IT CANNOT DERIVE (derivable): the persisted channel is the 20-bar one,
so a run at another Keltner period squeezed on a channel no key records; and
a run with a prior-squeeze requirement (SQUEEZE_PRIOR_N > 0) also needs the
prior bars' state at the tighter level, which is not persisted. The momentum
window does not touch the squeeze state, so it never blocks the derivation.
"""
from __future__ import annotations

KEYS = ("bb_20_20_lower", "bb_20_20_upper", "kc_lower", "kc_upper", "kc_mid")
PRODUCTION = {"SQUEEZE_KC_MULT": 2.0, "SQUEEZE_BB_STD": 2.0,
              "SQUEEZE_KC_PERIOD": 20, "SQUEEZE_PRIOR_N": 0}


def _landed(knobs) -> dict:
    """The landed values by env name, production where the arm is silent or
    blank (an unset knob runs at production, the engine's parse)."""
    out = dict(PRODUCTION)
    for k in PRODUCTION:
        v = (knobs or {}).get(k)
        if v is not None and str(v).strip() != "":
            out[k] = float(v)
    return out


def derivable(knobs) -> str:
    """'' when the rooms derive at this landed vector; else the reason."""
    v = _landed(knobs)
    if v["SQUEEZE_KC_PERIOD"] != 20:
        return (f"the run's Keltner period is {v['SQUEEZE_KC_PERIOD']:g}, the "
                "persisted channel is the 20-bar one - its squeeze state is "
                "not derivable from the recorded keys")
    if v["SQUEEZE_PRIOR_N"] != 0:
        return (f"the run requires a prior squeeze (N {v['SQUEEZE_PRIOR_N']:g}); "
                "a tighter level needs the prior bars' state, which is not persisted")
    return ""


def derive(sig: dict, knobs=None) -> dict:
    """Add kc_room and bb_room at the landed (m0, k0) to a copy of the
    persisted signal dict; None when an edge is missing, a width is zero, or
    the landed vector is not derivable."""
    out = dict(sig)
    v = _landed(knobs)
    try:
        bl, bu, kl, ku, km = (float(sig[k]) for k in KEYS)
    except (KeyError, TypeError, ValueError):
        out["kc_room"] = out["bb_room"] = None
        return out
    if derivable(knobs):
        out["kc_room"] = out["bb_room"] = None
        return out
    m0, k0 = v["SQUEEZE_KC_MULT"], v["SQUEEZE_BB_STD"]
    if (m0, k0) == (2.0, 2.0):
        # production: the original module's own expressions, so the two agree
        # to the last bit (the general form re-adds bmid + 2 sd for bu)
        import squeeze_derived as _sd
        d = _sd.derive(sig)
        out["kc_room"], out["bb_room"] = d["kc_room"], d["bb_room"]
        return out
    atr = (ku - km) / 2.0
    sd = (bu - bl) / 4.0
    bmid = (bu + bl) / 2.0
    out["kc_room"] = (max(bmid + k0 * sd - km, km - bmid + k0 * sd) / atr) if atr > 0 else None
    out["bb_room"] = (min(km + m0 * atr - bmid, bmid - km + m0 * atr) / sd) if sd > 0 else None
    return out
