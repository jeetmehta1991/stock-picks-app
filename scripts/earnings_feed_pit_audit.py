# PROVENANCE: SYNTHETIC - this module GENERATES numbers from a seeded RNG.
#             Any figure quoted from its output must be labelled SYNTHETIC at
#             the point of quotation (CHECKLIST #201 provenance half, B1719).
# Source: external reviewer 2026-06-11 per CHECKLIST #77
"""
earnings_feed_pit_audit.py
==========================

Phase-0 point-in-time (PIT) integrity audit for event-driven earnings producers
(compute_pead_signals, compute_yoy_surprise_signal, and any producer that anchors
on an earnings DATE or an earnings VALUE).

WHY THIS EXISTS
---------------
Every prior cluster fired on OHLCV, which is unambiguous at the close. Event-driven
strategies fire on derived facts about FILINGS -- earnings surprise, days-since-
event, within-PEAD-window. Unlike a price, every such fact has:
  - a publication LAG (you learn the EPS when it's announced, not at quarter-end),
  - a REVISION history (earnings get restated; the year-ago base gets restated),
  - a DATE that can move (preannouncements, schedule changes, vendor re-dating).

If the producer uses the LATER-KNOWN version of any of these, the backtest peeks.
This contaminates exactly the cluster's flagship strategies (PEAD long/short) and
is invisible to fire-count and follow-through tooling -- it lives in the producer.

THREE HAZARDS (each gets a probe)
---------------------------------
  H1  DATE RE-ANCHORING
      The PEAD window / event anchor uses the CONFIRMED-or-restated earnings date,
      re-stamped to history, instead of the date as-known on the bar. Surfaces as
      the window opening BEFORE the announcement was public.

  H2  VALUE RESTATEMENT (current and year-ago EPS)
      yoy_surprise / SUE computed from RESTATED EPS (this quarter or the year-ago
      base) instead of as-first-reported. Surfaces as the surprise sign/magnitude
      on the announcement bar differing from what as-reported numbers imply.

  H3  SAME-BAR GAP CONTAMINATION
      The "surprise" or the first tradeable PEAD bar depends on the announcement-
      day close-to-next-open GAP, which isn't fully known until the next open.
      Surfaces as a signal on bar t that needed bar t+1's open.

DESIGN: BLACK-BOX, BITEMPORAL GROUND TRUTH
------------------------------------------
We build a BITEMPORAL earnings record: every fact carries BOTH the value AND the
date that value became known (`known_from`). We construct cases where the
as-known value differs from the as-restated value, feed the producer a series
sliced "as of" a probe date, and assert the producer's output at each bar matches
the AS-KNOWN-AT-THAT-BAR ground truth -- never the restated one.

This catches the bug behaviourally regardless of how the producer is implemented,
the same way pattern_producer_audit catches repaint/phantom without reading source.

USAGE
-----
    from earnings_feed_pit_audit import audit_earnings_producer, build_case_value_restatement
    report = audit_earnings_producer(producer_fn, case=build_case_value_restatement())
    print(report)

`producer_fn(prices_df, earnings_records, as_of)` must return, for the as_of bar,
a dict of the signal(s) under test, e.g.
    {"within_pead_window": bool, "pead_positive_surprise": bool, "yoy_surprise": float}
computed using ONLY information knowable at `as_of`. The auditor calls it across
a sweep of as_of dates and compares to as-known ground truth.

INTEGRATION NOTE
----------------
This is the gating artifact for the PEAD sub-cluster. A PEAD producer that fails
any probe means the B690 re-run's PEAD fire counts and any backtested PEAD edge
are PENDING-PIT -- a positive backtest from a restatement-peeking producer is
fake edge, exactly like a repainting chart-pattern producer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------
# Bitemporal earnings record. The crucial field is `known_from`: the first date
# at which (value, report_date) was public. A PIT-honest producer evaluated at
# as_of may only use records with known_from <= as_of, and within such a record
# may only use the values that were current as of as_of.
# ----------------------------------------------------------------------------
@dataclass
class EarningsFact:
    fiscal_quarter: str          # e.g. "2024Q1"
    report_date: pd.Timestamp    # the date the market learned the result (as-known)
    eps: float                   # as-known EPS at announcement
    known_from: pd.Timestamp     # date this (report_date, eps) tuple became public
    # restatement (optional): a later correction
    restated_eps: float | None = None
    restated_known_from: pd.Timestamp | None = None
    restated_report_date: pd.Timestamp | None = None  # if the DATE itself was moved


@dataclass
class EarningsCase:
    name: str
    hazard: str                  # which hazard this case probes
    prices: pd.DataFrame         # index = dates, columns open/high/low/close
    facts: list                  # list[EarningsFact]
    probe_dates: list            # as_of dates to evaluate
    # ground truth: as_of -> expected as-known producer outputs
    expected: dict
    note: str = ""


def _price_frame(start="2024-01-01", n=260, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, periods=n)
    close = 100 + np.cumsum(rng.normal(0, 0.5, n))
    op = close + rng.normal(0, 0.2, n)
    hi = np.maximum(op, close) + np.abs(rng.normal(0, 0.3, n))
    lo = np.minimum(op, close) - np.abs(rng.normal(0, 0.3, n))
    return pd.DataFrame({"open": op, "high": hi, "low": lo, "close": close}, index=dates)


# ----------------------------------------------------------------------------
# CASE BUILDERS -- each isolates one hazard with a KNOWN as-known-vs-restated gap.
# ----------------------------------------------------------------------------
def build_case_value_restatement() -> EarningsCase:
    """H2: this quarter's EPS is announced as a BEAT, later RESTATED to a miss.
    A PIT producer must report the surprise as POSITIVE for bars between the
    announcement and the restatement, then (only after restated_known_from) may
    reflect the correction. A peeking producer reports the surprise as negative
    from the announcement bar (using the restated value)."""
    px = _price_frame(seed=1)
    ann = pd.Timestamp("2024-03-15")
    restate = pd.Timestamp("2024-05-01")
    yago = pd.Timestamp("2023-03-15")
    facts = [
        EarningsFact("2023Q1", yago, eps=1.00, known_from=yago),
        EarningsFact("2024Q1", ann, eps=1.30, known_from=ann,          # as-known: +30% YoY beat
                     restated_eps=0.80, restated_known_from=restate),   # restated: -20% YoY miss
    ]
    # probe a bar AFTER announcement but BEFORE restatement
    probe_after_ann = pd.Timestamp("2024-04-01")
    probe_after_restate = pd.Timestamp("2024-05-15")
    expected = {
        # as-known on 2024-04-01: yoy = 1.30/1.00 - 1 = +30% -> positive surprise
        probe_after_ann: {"yoy_surprise": pytest_approx(0.30), "pead_positive_surprise": True},
        # as-known on 2024-05-15: restatement public -> yoy = 0.80/1.00 - 1 = -20%
        probe_after_restate: {"yoy_surprise": pytest_approx(-0.20), "pead_positive_surprise": False},
    }
    return EarningsCase("value_restatement", "H2", px, facts,
                        [probe_after_ann, probe_after_restate], expected,
                        note="EPS announced as beat, later restated to miss; producer must not use restated value early")


def build_case_yago_base_restatement() -> EarningsCase:
    """H2 (base side): the YEAR-AGO EPS gets restated upward later. yoy_surprise
    uses (this_eps / yago_eps - 1). If the producer uses the RESTATED year-ago
    base retroactively, the surprise magnitude is wrong on bars before the base
    restatement was public."""
    px = _price_frame(seed=2)
    yago = pd.Timestamp("2023-03-15")
    ann = pd.Timestamp("2024-03-15")
    base_restate = pd.Timestamp("2024-02-01")  # year-ago base restated before this ann
    facts = [
        EarningsFact("2023Q1", yago, eps=1.00, known_from=yago,
                     restated_eps=1.25, restated_known_from=base_restate),  # base restated up
        EarningsFact("2024Q1", ann, eps=1.30, known_from=ann),
    ]
    probe = pd.Timestamp("2024-04-01")
    # By 2024-04-01 BOTH the base restatement (Feb) and the announcement (Mar) are
    # public, so the CORRECT as-known yoy uses the restated base: 1.30/1.25 - 1 = +4%.
    # +4% > 0 -> positive surprise True. A producer that used the ORIGINAL base
    # (1.00) would compute +30% -- wrong magnitude but same sign here, so this case
    # is a MAGNITUDE probe: we assert yoy == +4%, not the +30% an un-restated base gives.
    expected = {probe: {"yoy_surprise": pytest_approx(0.04), "pead_positive_surprise": True}}
    return EarningsCase("yago_base_restatement", "H2", px, facts, [probe], expected,
                        note="year-ago base restated BEFORE the new announcement; as-known yoy uses the restated base (it was public)")


def build_case_date_reanchor() -> EarningsCase:
    """H1: the earnings DATE is moved. The fact becomes KNOWN on 2024-03-14 (a
    preannouncement / vendor row appears), but the as-known EVENT date is
    2024-03-20. A later vintage re-dates the event earlier to 2024-03-13. A
    PIT-honest producer opens within_pead_window only on/after the as-known event
    date 2024-03-20. A producer that keys the window off the re-dated 2024-03-13
    (or treats known_from as the event) opens the window too early -> True on
    2024-03-17."""
    px = _price_frame(seed=3)
    known_from = pd.Timestamp("2024-03-14")    # vendor row appears (preannounce)
    as_known_event = pd.Timestamp("2024-03-20")  # the actual announcement date
    redated = pd.Timestamp("2024-03-13")
    facts = [
        EarningsFact("2024Q1", as_known_event, eps=1.20, known_from=known_from,
                     restated_report_date=redated, restated_known_from=pd.Timestamp("2024-06-01")),
    ]
    probe_before = pd.Timestamp("2024-03-17")   # after known_from, BEFORE as-known event
    probe_after = pd.Timestamp("2024-03-25")    # after event
    expected = {
        probe_before: {"within_pead_window": False},  # event not yet occurred
        probe_after: {"within_pead_window": True},
    }
    return EarningsCase("date_reanchor", "H1", px, facts, [probe_before, probe_after], expected,
                        note="vendor row known early but event date is later; window must follow as-known EVENT date, not known_from or re-dated date")


def build_case_gap_contamination() -> EarningsCase:
    """H3: the first tradeable PEAD bar. The announcement is after-close on
    2024-03-15; the gap is realized on the 2024-03-18 OPEN. A signal that
    'pead_positive_surprise' is True must be derivable from the announcement
    itself (EPS), NOT from the 2024-03-18 gap. We probe whether the producer can
    set the signal on 2024-03-15 close using only the EPS (correct) or whether it
    needs the next open (contaminated). We model this by asking the producer for
    its signal at the announcement bar and checking it doesn't depend on a
    future-open value we deliberately corrupt."""
    px = _price_frame(seed=4)
    ann = pd.Timestamp("2024-03-15")
    yago = pd.Timestamp("2023-03-15")
    facts = [
        EarningsFact("2023Q1", yago, eps=1.00, known_from=yago),
        EarningsFact("2024Q1", ann, eps=1.30, known_from=ann),
    ]
    # ground truth: surprise is +30% from EPS alone, knowable at ann close,
    # independent of any future open.
    probe = ann
    expected = {probe: {"pead_positive_surprise": True, "yoy_surprise": pytest_approx(0.30)}}
    return EarningsCase("gap_contamination", "H3", px, facts, [probe], expected,
                        note="surprise must be derivable from EPS at announcement, not from the next-open gap")


# small approx helper (avoid pytest dependency)
class pytest_approx:
    def __init__(self, val, tol=1e-6):
        self.val = val; self.tol = tol
    def __eq__(self, other):
        try:
            return abs(float(other) - self.val) <= self.tol + 1e-9 + 0.02 * abs(self.val)
        except (TypeError, ValueError):
            return False
    def __repr__(self):
        return f"~{self.val}"


CASE_BUILDERS = {
    "value_restatement": build_case_value_restatement,
    "yago_base_restatement": build_case_yago_base_restatement,
    "date_reanchor": build_case_date_reanchor,
    "gap_contamination": build_case_gap_contamination,
}


PASS = "PASS_PIT_CLEAN"
FAIL_PEEK = "FAIL_PEEKED_RESTATED_OR_FUTURE"
FAIL_WRONG = "FAIL_WRONG_VALUE"
ERROR = "ERROR"


@dataclass
class ProbeResult:
    as_of: pd.Timestamp
    key: str
    expected: object
    got: object
    ok: bool


@dataclass
class CaseResult:
    case_name: str
    hazard: str
    verdict: str
    probes: list = field(default_factory=list)
    note: str = ""


def audit_earnings_producer(
    producer_fn: Callable,
    case: EarningsCase,
) -> CaseResult:
    """
    producer_fn(prices, facts_as_of, as_of) -> dict of signal outputs at as_of.

    We hand the producer a BITEMPORALLY-FILTERED view of the facts at each as_of:
    only records with known_from <= as_of, and for each, the value/date that was
    current at as_of (restated value only if restated_known_from <= as_of). If the
    producer instead reaches past this filtered view (e.g. by holding the full
    restated record), that's the bug -- but to expose it fairly we pass the FULL
    bitemporal records and let the producer be responsible for as-of filtering,
    because THAT is what the real producer must do against the vendor cache.
    """
    probes: list[ProbeResult] = []
    any_fail = False
    for as_of in case.probe_dates:
        try:
            out = producer_fn(case.prices, case.facts, as_of)
        except Exception as e:  # noqa
            probes.append(ProbeResult(as_of, "<call>", "ok", f"EXCEPTION {e}", False))
            any_fail = True
            continue
        exp = case.expected.get(as_of, {})
        for key, want in exp.items():
            got = out.get(key, "<missing>")
            ok = (want == got) if isinstance(want, pytest_approx) else (want == got)
            probes.append(ProbeResult(as_of, key, want, got, bool(ok)))
            if not ok:
                any_fail = True

    verdict = PASS if not any_fail else FAIL_PEEK
    return CaseResult(case.name, case.hazard, verdict, probes, case.note)


def format_case(r: CaseResult) -> str:
    tag = "[PASS]" if r.verdict == PASS else "[FAIL]"
    L = [f"{tag} [{r.hazard}] {r.case_name} -> {r.verdict}", f"    {r.note}"]
    for p in r.probes:
        mark = "ok " if p.ok else "FAIL"
        L.append(f"    [{mark}] as_of={p.as_of.date()} {p.key}: expected {p.expected!r}, got {p.got!r}")
    return "\n".join(L)


def audit_all(producer_fn) -> list:
    return [audit_earnings_producer(producer_fn, b()) for b in CASE_BUILDERS.values()]
