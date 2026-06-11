"""
pattern_producer_audit.py
=========================

# Source: external reviewer 2026-06-11 per CHECKLIST #77

Phase-0 producer audit for chart-pattern detection producers (compute_chart_patterns,
compute_flag_break_retest_signals, and friends).

WHY THIS EXISTS
---------------
Every prior cluster fired on bar-local signals (RSI today, a cross today). Chart
patterns are categorically different: they are defined by SWING POINTS (local
highs/lows), and the standard way to confirm a swing is to see future bars move
away from it. That creates two failure modes that NO fire-count or follow-through
tool can catch, because they live INSIDE the producer:

  HAZARD 1  REPAINT / SWING LOOKAHEAD
    The pattern "detected at bar t" was only knowable at bar t+k (the producer
    used bars after t to confirm the swing). A double-bottom cannot be known on
    the day the second low prints -- you only know it was a low once price rises
    afterward. If the producer flags it on the low bar, it peeked. Every backtest
    built on it is lookahead-contaminated, and NO downstream correction fixes it.

  HAZARD 2  PHANTOM-BREAKOUT (detection-vs-confirmation gap)
    The producer flags the pattern SHAPE before the confirming BREAKOUT occurs.
    B618 already proved this for flags (flag_bull_detected fired while price was
    still inside the flag, because the detection window included today, so today's
    close <= flag_high by construction -- the breakout could not have happened).
    The same structure applies to double-bottom (neckline break), H&S (neckline),
    triangle (apex break). Firing on shape-complete is firing EARLY, before the
    trigger the thesis actually depends on.

KEY DESIGN: BLACK-BOX BEHAVIOURAL PROBING
-----------------------------------------
We do NOT need the producer's source. We feed it synthetic OHLC series where WE
control the exact bar on which each pattern (a) becomes geometrically complete and
(b) becomes confirmable without hindsight, and (c) actually breaks out. Then we
ask the producer when it first flags the pattern and compare:

  - flagged BEFORE the confirmable bar            -> REPAINT  (Hazard 1)  FAIL
  - flagged on shape-complete but BEFORE breakout -> PHANTOM  (Hazard 2)  FAIL
  - flagged on/after the breakout bar             -> CLEAN

This catches the bug behaviourally regardless of HOW detection is implemented
(scipy argrelextrema, find_peaks, hand-rolled) -- which is more robust than
reading source, because the source can look innocent while a centered window or
an inclusive .iloc slice quietly peeks.

USAGE
-----
    from pattern_producer_audit import audit_producer, PATTERN_BUILDERS

    # producer_fn(df) -> dict[str, pd.Series]  (bool series per pattern key, indexed like df)
    report = audit_producer(producer_fn,
                            pattern_key="double_bottom_detected",
                            builder=PATTERN_BUILDERS["double_bottom"])
    print(report)

The builders below construct ground-truth series with KNOWN landmark bars. They
are intentionally clean/idealized: if a producer repaints even on a textbook
pattern, it will certainly repaint on noisy real data.

INTEGRATION NOTE
----------------
This is the gating artifact for the chart-pattern cluster. Until a producer passes
(CLEAN on its pattern), the B660 / B689 re-run numbers for strategies consuming
that pattern are PENDING-PRODUCER-AUDIT -- a nonzero fire count from a repainting
producer is WORSE than a zero, because it is fake edge that looks real.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------
# A "landmark" describes the three bars that matter for PIT-honesty of a pattern.
#   complete_bar     : the bar at which the pattern SHAPE is geometrically done
#                      (e.g. the second bottom prints; the right shoulder prints)
#   confirmable_bar  : the earliest bar at which the shape could be known WITHOUT
#                      using any later bar (usually complete_bar + swing_confirm_k)
#   breakout_bar     : the bar at which the confirming breakout occurs (neckline /
#                      apex / flag-high break). This is the only honest entry bar.
# A producer is:
#   REPAINT  if it first flags True at index < confirmable_bar
#   PHANTOM  if it first flags True in [confirmable_bar, breakout_bar)
#   CLEAN    if it first flags True at index >= breakout_bar
#   MISS     if it never flags True (pattern not detected at all)
# ----------------------------------------------------------------------------
@dataclass
class Landmark:
    name: str
    df: pd.DataFrame
    complete_bar: int
    confirmable_bar: int
    breakout_bar: int


def _bar(o, h, l, c):
    return dict(open=o, high=h, low=l, close=c)


def _series_from_bars(bars):
    df = pd.DataFrame(bars)
    return df[["open", "high", "low", "close"]]


# ----------------------------------------------------------------------------
# Ground-truth pattern builders. Each returns a Landmark with KNOWN bar indices.
# swing_confirm_k = how many bars after a swing we deem it "confirmable" (a
# reasonable detector needs at least this many; a detector that flags earlier is
# repainting). Default 3.
# ----------------------------------------------------------------------------
def build_double_bottom(swing_confirm_k: int = 3, pad: int = 30) -> Landmark:
    """W-shape: low1, recovery to neckline, low2 (== low1), break above neckline.
    complete   = low2 bar
    confirmable= low2 + k   (need k up-bars to know low2 was a bottom)
    breakout   = the bar that closes above the neckline (intervening peak).

    Construction is deliberately monotone on each leg so the ONLY pair of equal
    swing lows is (low1, low2) -- no incidental troughs that a detector could
    latch onto earlier (which would confound the repaint-vs-phantom distinction)."""
    bars = []
    px = 100.0
    # strictly-descending pre-amble into low1 (no intermediate troughs)
    for _ in range(pad):
        nxt = px - 0.6
        bars.append(_bar(px, px + 0.2, nxt - 0.1, nxt)); px = nxt
    low1_i = len(bars)
    low1 = px - 0.1
    bars.append(_bar(px, px + 0.1, low1, low1 + 0.05)); px = low1 + 0.05     # low1 trough (the global min so far)
    # strictly-ascending recovery to neckline (no troughs)
    neckline = low1 + 8.0
    for _ in range(9):
        nxt = px + 1.0
        bars.append(_bar(px, nxt + 0.1, px - 0.1, nxt)); px = nxt
    # strictly-descending pullback to low2 (~= low1); stays ABOVE low1 until the trough
    while px > low1 + 1.0:
        nxt = px - 0.9
        bars.append(_bar(px, px + 0.1, nxt - 0.1, nxt)); px = nxt
    low2_i = len(bars)
    bars.append(_bar(px, px + 0.1, low1, low1 + 0.05)); px = low1 + 0.05     # low2 trough (== low1)
    confirmable_i = low2_i + swing_confirm_k
    # strictly-ascending rise back toward neckline, then BREAK above it
    while px < neckline - 0.5:
        nxt = px + 0.9
        bars.append(_bar(px, nxt + 0.1, px - 0.1, nxt)); px = nxt
    breakout_i = len(bars)
    bars.append(_bar(px, neckline + 1.5, px - 0.1, neckline + 1.2)); px = neckline + 1.2  # neckline break
    for _ in range(pad):
        nxt = px + 0.6
        bars.append(_bar(px, nxt + 0.1, px - 0.2, nxt)); px = nxt
    return Landmark("double_bottom", _series_from_bars(bars), low2_i, confirmable_i, breakout_i)


def build_head_shoulders_bottom(swing_confirm_k: int = 3, pad: int = 25) -> Landmark:
    """Inverse H&S: left shoulder, head (deepest), right shoulder, neckline break.
    complete   = right-shoulder trough bar
    confirmable= right_shoulder + k
    breakout   = neckline break bar."""
    bars = []
    px = 100.0
    for _ in range(pad):
        bars.append(_bar(px, px + 0.3, px - 0.7, px - 0.5)); px -= 0.5
    neckline = px + 6.0
    def trough(depth):
        nonlocal px
        # go down to a trough `depth` below neckline, then back up to neckline
        target = neckline - depth
        while px > target:
            bars.append(_bar(px, px + 0.2, px - 1.0, px - 0.8)); px -= 0.8
        ti = len(bars) - 1
        while px < neckline - 0.2:
            bars.append(_bar(px, px + 1.0, px - 0.2, px + 0.8)); px += 0.8
        return ti
    trough(4.0)                       # left shoulder
    trough(7.0)                       # head (deepest)
    rs_i = trough(4.0)                # right shoulder
    confirmable_i = rs_i + swing_confirm_k
    while px < neckline:
        bars.append(_bar(px, px + 1.0, px - 0.2, px + 0.8)); px += 0.8
    breakout_i = len(bars)
    bars.append(_bar(px, neckline + 1.5, px - 0.1, neckline + 1.2)); px = neckline + 1.2
    for _ in range(pad):
        bars.append(_bar(px, px + 0.9, px - 0.4, px + 0.5)); px += 0.5
    return Landmark("head_shoulders_bottom", _series_from_bars(bars), rs_i, confirmable_i, breakout_i)


def build_ascending_triangle(swing_confirm_k: int = 3, pad: int = 25) -> Landmark:
    """Flat top (resistance) + rising lows; breakout above the flat top.
    complete   = last higher-low bar before breakout
    confirmable= last_higher_low + k
    breakout   = close above the flat resistance."""
    bars = []
    px = 100.0
    for _ in range(pad):
        bars.append(_bar(px, px + 0.5, px - 0.5, px + 0.2)); px += 0.2
    resistance = px + 5.0
    # build 3 rising lows, each touching resistance then pulling back less
    low = px
    last_low_i = len(bars)
    for k in range(3):
        # up to resistance
        while px < resistance - 0.2:
            bars.append(_bar(px, px + 1.0, px - 0.2, px + 0.8)); px += 0.8
        bars.append(_bar(px, resistance, px - 0.1, resistance - 0.3)); px = resistance - 0.3
        # pull back to a HIGHER low each time
        low = low + 1.2
        while px > low:
            bars.append(_bar(px, px + 0.2, px - 0.9, px - 0.7)); px -= 0.7
        last_low_i = len(bars) - 1
    confirmable_i = last_low_i + swing_confirm_k
    while px < resistance:
        bars.append(_bar(px, px + 1.0, px - 0.2, px + 0.8)); px += 0.8
    breakout_i = len(bars)
    bars.append(_bar(px, resistance + 1.6, px - 0.1, resistance + 1.3)); px = resistance + 1.3
    for _ in range(pad):
        bars.append(_bar(px, px + 0.9, px - 0.4, px + 0.5)); px += 0.5
    return Landmark("ascending_triangle", _series_from_bars(bars), last_low_i, confirmable_i, breakout_i)


def build_bull_flag(swing_confirm_k: int = 2, pad: int = 25) -> Landmark:
    """Pole up, tight flag (slight pullback), breakout above flag high.
    complete   = last flag bar
    confirmable= last_flag_bar + k
    breakout   = close above flag_high (the B618 case)."""
    bars = []
    px = 100.0
    for _ in range(pad):
        bars.append(_bar(px, px + 0.4, px - 0.4, px + 0.1)); px += 0.1
    # pole: sharp rally
    for _ in range(8):
        bars.append(_bar(px, px + 2.2, px - 0.2, px + 2.0)); px += 2.0
    flag_high = px
    # flag: small downward drift
    for _ in range(6):
        bars.append(_bar(px, px + 0.3, px - 0.6, px - 0.4)); px -= 0.4
    last_flag_i = len(bars) - 1
    confirmable_i = last_flag_i + swing_confirm_k
    # rise back to flag_high then break
    while px < flag_high:
        bars.append(_bar(px, px + 1.0, px - 0.2, px + 0.8)); px += 0.8
    breakout_i = len(bars)
    bars.append(_bar(px, flag_high + 1.5, px - 0.1, flag_high + 1.2)); px = flag_high + 1.2
    for _ in range(pad):
        bars.append(_bar(px, px + 0.9, px - 0.4, px + 0.5)); px += 0.5
    return Landmark("bull_flag", _series_from_bars(bars), last_flag_i, confirmable_i, breakout_i)


PATTERN_BUILDERS: dict[str, Callable[..., Landmark]] = {
    "double_bottom": build_double_bottom,
    "head_shoulders_bottom": build_head_shoulders_bottom,
    "ascending_triangle": build_ascending_triangle,
    "bull_flag": build_bull_flag,
}


REPAINT = "REPAINT_LOOKAHEAD"      # Hazard 1 -- flagged before confirmable
PHANTOM = "PHANTOM_BREAKOUT"       # Hazard 2 -- flagged after confirmable but before breakout
CLEAN = "CLEAN"                    # flagged at/after breakout
MISS = "MISS"                      # never flagged


@dataclass
class AuditResult:
    pattern_key: str
    pattern_name: str
    first_flag_bar: int
    complete_bar: int
    confirmable_bar: int
    breakout_bar: int
    verdict: str
    note: str = ""
    detail: dict = field(default_factory=dict)


def audit_producer(
    producer_fn: Callable[[pd.DataFrame], dict],
    pattern_key: str,
    builder: Callable[..., Landmark],
    *,
    swing_confirm_k: int = 3,
    require_breakout: bool = True,
) -> AuditResult:
    """
    producer_fn(df) -> dict mapping pattern keys to boolean pd.Series (df-indexed).
    We feed the FULL series once (mimicking how the precompute runs over history),
    then inspect the first bar the producer set pattern_key True.

    NOTE on honest simulation: a truly PIT-safe producer, run over the full df,
    must still only set True on bar i using df.iloc[:i+1]. If it sets True at a
    bar that our ground truth says wasn't yet confirmable, it peeked -- regardless
    of whether it "intended" to. That is exactly the bug we want to surface.
    """
    lm = builder(swing_confirm_k=swing_confirm_k) if "swing_confirm_k" in builder.__code__.co_varnames else builder()
    out = producer_fn(lm.df)
    if pattern_key not in out:
        return AuditResult(pattern_key, lm.name, -1, lm.complete_bar, lm.confirmable_bar,
                           lm.breakout_bar, MISS, f"producer emitted no key '{pattern_key}'")
    flags = np.asarray(pd.Series(out[pattern_key]).fillna(False).astype(bool))
    fired = np.flatnonzero(flags)
    if fired.size == 0:
        return AuditResult(pattern_key, lm.name, -1, lm.complete_bar, lm.confirmable_bar,
                           lm.breakout_bar, MISS, "producer never flagged the textbook pattern -> detection too strict or broken")
    first = int(fired[0])

    if first < lm.confirmable_bar:
        v = REPAINT
        note = (f"flagged at bar {first} but pattern not confirmable until {lm.confirmable_bar} "
                f"(complete at {lm.complete_bar}); producer used >= {lm.confirmable_bar - first} future bar(s) -> LOOKAHEAD")
    elif require_breakout and first < lm.breakout_bar:
        v = PHANTOM
        note = (f"flagged at bar {first} (shape complete/confirmable) but BEFORE the breakout at "
                f"{lm.breakout_bar} -> fires early, before the confirming trigger (B618 phantom-breakout class)")
    else:
        v = CLEAN
        note = f"flagged at bar {first} >= breakout bar {lm.breakout_bar} -> PIT-honest, fires on confirmed breakout"
    return AuditResult(pattern_key, lm.name, first, lm.complete_bar, lm.confirmable_bar,
                       lm.breakout_bar, v, note,
                       detail={"n_bars": len(lm.df), "n_flags": int(fired.size)})


def format_audit(r: AuditResult) -> str:
    tag = {REPAINT: "[FAIL-REPAINT]", PHANTOM: "[FAIL-PHANTOM]", CLEAN: "[CLEAN]", MISS: "[MISS]"}.get(r.verdict, "?")
    return (f"{tag} {r.pattern_key} [{r.pattern_name}] -> {r.verdict}\n"
            f"    first_flag={r.first_flag_bar}  complete={r.complete_bar}  "
            f"confirmable={r.confirmable_bar}  breakout={r.breakout_bar}\n"
            f"    {r.note}")


def audit_all(producer_fn, key_map: dict) -> list:
    """key_map: {pattern_key_in_producer_output: builder_name_in_PATTERN_BUILDERS}."""
    results = []
    for key, builder_name in key_map.items():
        results.append(audit_producer(producer_fn, key, PATTERN_BUILDERS[builder_name]))
    return results
