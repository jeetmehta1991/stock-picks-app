# Source: B719 SMC review + B555 panel-cache PIT-risk caveat + Decision 3 build #2 owner-approved per CHECKLIST #77
"""
smc_pit_audit.py
================

Phase-0 point-in-time (PIT) integrity audit for SMC (Smart Money Concepts) signal
producers. Direct template adaptation of `earnings_feed_pit_audit.py` (B704), with
the hazard classes re-targeted for the structural facts SMC producers compute.

WHY THIS EXISTS
---------------
SMC producers compute STRUCTURAL facts -- swing highs/lows, dealing ranges, order
blocks, fair-value gaps, breaks-of-structure -- that are defined RELATIVE to past
AND future bars. Three failure modes are easy to introduce and invisible to
fire-count / follow-through tooling because they live in the producer:

  H1  SWING-FORMATION CONFIRMATION LAG
      A swing high at bar t requires k bars AFTER t to be lower. A producer that
      labels bar t as a swing high using bars [t .. t+k] peeks: at as_of=t the
      market does not yet know t is a swing.

  H2  DEALING-RANGE EXTREMA RE-ANCHOR
      The dealing range is the bracket between the most recent confirmed swing
      high and swing low. If a LATER bar prints a more extreme high (or low) and
      the producer retroactively re-anchors the range, the range used at as_of=t
      reflects information from t+1..t+m. This is the Pattern K hazard from
      B719's SMC review.

  H3  PANEL-CACHE EDGE CONTAMINATION
      `compute_smc_panel_cache` precomputes SMC signals for a full date range.
      If the cache row at bar t was derived using a window [t-a .. t+b], then
      reading the cache at as_of=t reads b bars of future. This is the B555
      panel-cache PIT-risk caveat. The auditor builds a case where the as-known
      truth at as_of=t differs from the cache value computed with b>0 future
      bars and asserts the producer returns the AS-KNOWN value.

DESIGN: BLACK-BOX BAR-SLICED GROUND TRUTH
-----------------------------------------
Unlike the bitemporal earnings auditor (which carries value + known_from for
each fact), SMC structural facts are derivable directly from the OHLCV time
series. The auditor instead exercises the producer with EXPLICITLY-SLICED OHLCV
("the producer only sees bars <= as_of") and compares its output to a
hand-authored ground truth for each probe date. A producer that uses information
beyond `as_of` will diverge from the as-known truth.

The auditor calls the producer in TWO modes per probe and compares:
  (a) PIT mode: producer sees prices.loc[:as_of]
  (b) FULL mode: producer sees prices.loc[:] but is asked to report bar t
A PIT-honest producer returns the SAME value at probe t in both modes. A
peeking producer returns different values -- specifically, the FULL mode
value matches the as-restated/confirmed truth that wasn't yet known at t.

USAGE
-----
    from smc_pit_audit import audit_smc_producer, build_case_swing_confirmation
    report = audit_smc_producer(producer_fn, case=build_case_swing_confirmation())
    print(report)

`producer_fn(prices_df, as_of)` must return, for the as_of bar, a dict of the
signal(s) under test, e.g.
    {"swing_high_confirmed": bool, "dealing_range_high": float,
     "bullish_order_block_active": bool, "fvg_present": bool}
computed using ONLY information knowable at `as_of`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------
# Bar-sliced case structure. No bitemporal annotation needed: the structural
# fact's known_from is implicit in the bar series.
# ----------------------------------------------------------------------------
@dataclass
class SmcCase:
    name: str
    hazard: str                  # H1 / H2 / H3
    prices: pd.DataFrame         # index = dates, columns open/high/low/close
    probe_dates: list            # as_of dates to evaluate
    expected_pit: dict           # as_of -> expected as-known producer output
    note: str = ""


# ----------------------------------------------------------------------------
# Small approx helper (avoid pytest dependency at runtime).
# ----------------------------------------------------------------------------
class _approx:
    def __init__(self, val, tol=1e-6):
        self.val = val; self.tol = tol
    def __eq__(self, other):
        try:
            return abs(float(other) - self.val) <= self.tol + 1e-9 + 0.02 * abs(self.val)
        except (TypeError, ValueError):
            return False
    def __repr__(self):
        return f"~{self.val}"


def _price_frame_with_swings(swing_points, start="2024-01-02", noise_seed=0):
    """Build OHLCV where specific bars are forced to print specific highs/lows
    against a near-flat baseline. Background bars sit at 100 +/- 0.5 to avoid
    creating accidental swings the producer would detect.

    swing_points: list of (date_offset, kind, value) where kind in {"high", "low"}.
    """
    _ = noise_seed  # accepted for signature stability; not used to keep baseline flat
    n = max(off for off, _, _ in swing_points) + 30  # tail bars for confirmation
    dates = pd.bdate_range(start, periods=n)
    # Flat baseline -- no random walk that would create unintended swings
    close = np.full(n, 100.0)
    op = np.full(n, 100.0)
    hi = np.full(n, 100.5)
    lo = np.full(n, 99.5)
    # apply forced swings + guard a 5-bar buffer on each side so neighbours never
    # exceed the forced swing's extreme (ensures swing is uniquely detectable).
    BUFFER = 5
    for off, kind, val in swing_points:
        if kind == "high":
            hi[off] = val
            for k in range(max(0, off - BUFFER), min(n, off + BUFFER + 1)):
                if k != off:
                    hi[k] = min(hi[k], val - 1.0)
        elif kind == "low":
            lo[off] = val
            for k in range(max(0, off - BUFFER), min(n, off + BUFFER + 1)):
                if k != off:
                    lo[k] = max(lo[k], val + 1.0)
    return pd.DataFrame({"open": op, "high": hi, "low": lo, "close": close}, index=dates)


# ----------------------------------------------------------------------------
# H1: swing-formation confirmation lag.
# A swing high at bar t requires k right-side bars all lower than t. At as_of=t,
# those bars don't exist yet -> swing is UNCONFIRMED.
# ----------------------------------------------------------------------------
def build_case_swing_confirmation(k: int = 3) -> SmcCase:
    swings = [(50, "high", 110.0)]  # swing high at bar 50 with H=110
    px = _price_frame_with_swings(swings, noise_seed=1)
    swing_date = px.index[50]
    # at swing_date itself: producer CANNOT yet know bar 50 is a confirmed swing
    # (needs bars 51..50+k all lower)
    probe_at_swing = swing_date
    # at swing_date + k bars: confirmation window now complete -> may flag
    probe_after_confirm = px.index[50 + k]
    expected = {
        probe_at_swing: {"swing_high_confirmed": False},
        probe_after_confirm: {"swing_high_confirmed": True},
    }
    return SmcCase(
        "swing_confirmation", "H1", px,
        [probe_at_swing, probe_after_confirm],
        expected,
        note=f"swing high at bar 50 requires {k} right-side lower bars; producer must not flag at swing bar itself",
    )


# ----------------------------------------------------------------------------
# H2: dealing-range extrema re-anchor (Pattern K from B719).
# A range is bracketed by the most recent confirmed swing high + swing low. If a
# LATER swing high prints a more extreme value, the producer must NOT retroactively
# raise the range high used at as_of bars BEFORE that later swing was confirmed.
# ----------------------------------------------------------------------------
def build_case_dealing_range_reanchor(k: int = 3) -> SmcCase:
    swings = [
        (20, "low",  95.0),    # confirmed low at bar 20
        (40, "high", 108.0),   # first swing high at bar 40
        (70, "high", 115.0),   # LATER, MORE EXTREME swing high at bar 70
    ]
    px = _price_frame_with_swings(swings, noise_seed=2)
    # probe BETWEEN the two swing highs (after 40+k confirmation, before 70)
    probe_mid = px.index[55]
    # probe AFTER second swing high is confirmed
    probe_late = px.index[70 + k]
    expected = {
        # at probe_mid: range high should be 108 (first swing high), NOT 115 (the later one)
        probe_mid: {"dealing_range_high": _approx(108.0)},
        probe_late: {"dealing_range_high": _approx(115.0)},
    }
    return SmcCase(
        "dealing_range_reanchor", "H2", px,
        [probe_mid, probe_late],
        expected,
        note="later, more extreme swing high must NOT retroactively raise the range high at earlier probe dates (Pattern K)",
    )


# ----------------------------------------------------------------------------
# H3: panel-cache edge contamination (B555 caveat).
# We probe the same producer signal at the SAME bar (as_of=t) via two routes:
#   (a) feed prices.loc[:as_of]
#   (b) feed prices.loc[:] (full history, including future bars)
# A PIT-honest producer returns IDENTICAL values for both. A producer that uses
# a centered or forward-looking window leaks (b)-only information into (a)'s
# expected value.
# We surface this as a generic "as_of-stability" probe: if (a) and (b) disagree,
# the producer is non-causal at that bar.
# ----------------------------------------------------------------------------
def build_case_panel_cache_edge(k: int = 3) -> SmcCase:
    swings = [
        (30, "low", 96.0),
        (60, "high", 112.0),  # this swing high is JUST AHEAD of the probe bar
    ]
    px = _price_frame_with_swings(swings, noise_seed=3)
    # probe a bar 2 bars before the confirmed swing high (within the right-side
    # confirmation window) -> at as_of=probe, the producer should NOT yet flag
    # the swing or the range edge.
    probe = px.index[58]
    expected = {probe: {"swing_high_confirmed": False, "dealing_range_high_set": False}}
    return SmcCase(
        "panel_cache_edge", "H3", px, [probe], expected,
        note="signal computed on prices.loc[:as_of] must equal signal computed on prices.loc[:] at the same bar (cache must be causal)",
    )


CASE_BUILDERS = {
    "swing_confirmation": build_case_swing_confirmation,
    "dealing_range_reanchor": build_case_dealing_range_reanchor,
    "panel_cache_edge": build_case_panel_cache_edge,
}


PASS = "PASS_PIT_CLEAN"
FAIL_PEEK = "FAIL_PEEKED_FUTURE_BARS"
FAIL_WRONG = "FAIL_WRONG_VALUE"
ERROR = "ERROR"


@dataclass
class ProbeResult:
    as_of: pd.Timestamp
    key: str
    expected: object
    got_pit: object
    got_full: object
    ok: bool


@dataclass
class CaseResult:
    case_name: str
    hazard: str
    verdict: str
    probes: list = field(default_factory=list)
    note: str = ""


def audit_smc_producer(
    producer_fn: Callable,
    case: SmcCase,
) -> CaseResult:
    """
    producer_fn(prices, as_of) -> dict of signal outputs at as_of.

    Calls in TWO modes per probe:
      (a) PIT mode:  producer_fn(prices.loc[:as_of], as_of)
      (b) FULL mode: producer_fn(prices, as_of)
    A PIT-honest producer returns identical values for both. The expected map
    encodes the as-known truth at as_of; the verdict combines (i) match-to-truth
    and (ii) PIT-FULL agreement.
    """
    probes: list[ProbeResult] = []
    any_fail = False
    for as_of in case.probe_dates:
        try:
            sliced = case.prices.loc[:as_of]
            out_pit = producer_fn(sliced, as_of)
        except Exception as e:  # noqa
            probes.append(ProbeResult(as_of, "<call:pit>", "ok", f"EXCEPTION {e}", None, False))
            any_fail = True
            continue
        try:
            out_full = producer_fn(case.prices, as_of)
        except Exception as e:  # noqa
            probes.append(ProbeResult(as_of, "<call:full>", "ok", out_pit, f"EXCEPTION {e}", False))
            any_fail = True
            continue
        exp = case.expected_pit.get(as_of, {})
        for key, want in exp.items():
            got_pit = out_pit.get(key, "<missing>")
            got_full = out_full.get(key, "<missing>")
            # match to expected truth
            ok_truth = (want == got_pit) if isinstance(want, _approx) else (want == got_pit)
            # PIT/FULL stability
            ok_stable = (got_pit == got_full)
            ok = bool(ok_truth and ok_stable)
            probes.append(ProbeResult(as_of, key, want, got_pit, got_full, ok))
            if not ok:
                any_fail = True

    verdict = PASS if not any_fail else FAIL_PEEK
    return CaseResult(case.name, case.hazard, verdict, probes, case.note)


def format_case(r: CaseResult) -> str:
    tag = "[PASS]" if r.verdict == PASS else "[FAIL]"
    L = [f"{tag} [{r.hazard}] {r.case_name} -> {r.verdict}", f"    {r.note}"]
    for p in r.probes:
        mark = "ok " if p.ok else "FAIL"
        L.append(
            f"    [{mark}] as_of={p.as_of.date()} {p.key}: "
            f"expected {p.expected!r}, pit={p.got_pit!r}, full={p.got_full!r}"
        )
    return "\n".join(L)


def audit_all(producer_fn) -> list:
    return [audit_smc_producer(producer_fn, b()) for b in CASE_BUILDERS.values()]
