"""
validate_pattern_producer_audit.py

# Source: external reviewer 2026-06-11 per CHECKLIST #77

We hand the auditor three reference producers whose behaviour we control, and
check it classifies each correctly:

  clean_producer    : detects the pattern only after the BREAKOUT, using only
                      past bars -> must be CLEAN.
  repaint_producer  : uses a CENTERED swing window (looks k bars forward) to
                      mark the second bottom on the bottom bar itself -> must be
                      flagged REPAINT_LOOKAHEAD.
  phantom_producer  : detects the SHAPE (two equal lows) the moment the second
                      low's swing is confirmable, but does NOT wait for the
                      neckline breakout -> must be flagged PHANTOM_BREAKOUT.

If the auditor catches the repaint and phantom while passing the clean one, the
tool works. (Same validate-against-known-ground-truth discipline as the
fire-count, redundancy, and follow-through tools.)
"""

import numpy as np
import pandas as pd

from pattern_producer_audit import (
    audit_producer, build_double_bottom, format_audit,
    REPAINT, PHANTOM, CLEAN,
)

K = 3  # swing confirmation bars used by the builders


def _swing_lows_causal(low, k):
    """Mark bar i a swing low if it's the min of [i-k, i] AND the next k bars
    are all higher -> only KNOWABLE at i+k. Returns the index at which each
    swing low becomes CONFIRMABLE (i+k), causally."""
    n = len(low)
    confirmable_at = {}
    for i in range(k, n - k):
        window_back = low[i - k:i + 1]
        if low[i] == window_back.min() and np.all(low[i + 1:i + 1 + k] > low[i]):
            confirmable_at[i] = i + k
    return confirmable_at


def clean_producer(df):
    """PIT-honest: finds two roughly-equal swing lows (each confirmed k bars
    after it occurs), then fires ONLY on the bar that closes above the neckline
    (the interventing peak between the two lows). Uses only past data at each i."""
    low = df["low"].to_numpy(float)
    close = df["close"].to_numpy(float)
    high = df["high"].to_numpy(float)
    n = len(df)
    flag = np.zeros(n, bool)
    confirmable = _swing_lows_causal(low, K)          # {low_bar: confirm_bar}
    conf_items = sorted(confirmable.items())
    for i in range(n):
        # at bar i, which swing lows are ALREADY confirmable (confirm_bar <= i)?
        known = [lb for lb, cb in conf_items if cb <= i]
        if len(known) < 2:
            continue
        lb2 = known[-1]; lb1 = known[-2]
        if abs(low[lb1] - low[lb2]) > 0.5:            # not a double bottom
            continue
        neckline = high[lb1:lb2 + 1].max()            # peak between the two lows (all past)
        if close[i] > neckline:                       # BREAKOUT confirmed, causally
            flag[i] = True
    return {"double_bottom_detected": pd.Series(flag, index=df.index)}


def repaint_producer(df):
    """BUGGY (Hazard 1): marks the double-bottom True ON the second-low bar,
    using a centered window that peeks forward to 'confirm' the low. Classic
    argrelextrema-style lookahead."""
    low = df["low"].to_numpy(float)
    n = len(df)
    flag = np.zeros(n, bool)
    confirmable = _swing_lows_causal(low, K)
    lows = sorted(confirmable.keys())
    for a in range(len(lows) - 1):
        lb1, lb2 = lows[a], lows[a + 1]
        if abs(low[lb1] - low[lb2]) <= 0.5:
            flag[lb2] = True                          # <-- set True ON the low bar = peeked
    return {"double_bottom_detected": pd.Series(flag, index=df.index)}


def phantom_producer(df):
    """BUGGY (Hazard 2): fires the moment the second low is CONFIRMABLE (no
    lookahead -- causal), but does NOT wait for the neckline breakout. Fires
    early, on shape-complete. This is the B618 phantom-breakout class."""
    low = df["low"].to_numpy(float)
    n = len(df)
    flag = np.zeros(n, bool)
    confirmable = _swing_lows_causal(low, K)          # causal, no lookahead
    conf_items = sorted(confirmable.items())
    for i in range(n):
        known = [lb for lb, cb in conf_items if cb <= i]
        if len(known) >= 2 and abs(low[known[-1]] - low[known[-2]]) <= 0.5:
            flag[i] = True                            # fires on shape, not breakout
            break
    return {"double_bottom_detected": pd.Series(flag, index=df.index)}


print("=" * 78)
cases = [
    ("clean_producer", clean_producer, CLEAN),
    ("repaint_producer", repaint_producer, REPAINT),
    ("phantom_producer", phantom_producer, PHANTOM),
]
all_pass = True
for name, fn, expected in cases:
    r = audit_producer(fn, "double_bottom_detected", build_double_bottom, swing_confirm_k=K)
    print(format_audit(r))
    ok = r.verdict == expected
    all_pass &= ok
    print(f"    EXPECTED {expected} -> {'PASS' if ok else 'FAIL (got ' + r.verdict + ')'}")
    print("-" * 78)

print(f"\nALL CASES: {'PASS' if all_pass else 'FAIL'}")
