# Source: external reviewer 2026-06-11 per CHECKLIST #77
"""
validate_earnings_feed_pit_audit.py

Two reference producers whose behaviour we control:

  honest_producer : at as_of, uses ONLY records public by then, and within each
                    record uses the value/date current as_of (restated only if
                    restated_known_from <= as_of). Derives surprise from EPS at
                    the announcement (no future-open dependency). Must PASS all 4
                    hazard cases.

  peeking_producer: uses the RESTATED eps / RE-DATED report_date whenever a
                    restatement exists, regardless of restated_known_from; i.e.
                    it reads the "final" vendor row. Must FAIL H1 (date_reanchor)
                    and H2 (value_restatement). It happens to be correct on the
                    yago-base case (the base restatement was already public) and
                    on the gap case (it derives from EPS) -- so a good auditor
                    flags it on exactly the cases where peeking changes the answer
                    and not elsewhere. That selectivity is itself a correctness
                    check on the auditor.
"""

import pandas as pd

from earnings_feed_pit_audit import (
    audit_earnings_producer, CASE_BUILDERS, format_case, PASS, FAIL_PEEK,
)


def _as_of_value(fact, as_of, field):
    """Return the as-known value of `field` ('eps' or 'report_date') at as_of,
    honoring restatement visibility."""
    if field == "eps":
        if fact.restated_eps is not None and fact.restated_known_from is not None \
                and as_of >= fact.restated_known_from:
            return fact.restated_eps
        return fact.eps
    if field == "report_date":
        if fact.restated_report_date is not None and fact.restated_known_from is not None \
                and as_of >= fact.restated_known_from:
            return fact.restated_report_date
        return fact.report_date
    raise KeyError(field)


def _visible_facts(facts, as_of):
    return [f for f in facts if f.known_from <= as_of]


def honest_producer(prices, facts, as_of):
    vis = _visible_facts(facts, as_of)
    # latest announcement whose as-known report_date <= as_of
    anns = []
    for f in vis:
        rd = _as_of_value(f, as_of, "report_date")
        if rd <= as_of:
            anns.append((rd, f))
    out = {"within_pead_window": False, "pead_positive_surprise": False, "yoy_surprise": float("nan")}
    if not anns:
        return out
    anns.sort()
    rd, latest = anns[-1]
    window_open = (as_of - rd).days <= 90  # ~60 trading days
    out["within_pead_window"] = bool(window_open)
    # yoy surprise from as-known EPS of this quarter and the year-ago quarter
    this_eps = _as_of_value(latest, as_of, "eps")
    # find year-ago fact (~1 year earlier fiscal), as-known
    yago = None
    for f in vis:
        if abs((latest.report_date - f.report_date).days - 365) < 40:
            yago = f
    if yago is not None:
        base = _as_of_value(yago, as_of, "eps")
        if base not in (0, None):
            yoy = this_eps / base - 1.0
            out["yoy_surprise"] = yoy
            out["pead_positive_surprise"] = bool(window_open and yoy > 0.0)
    return out


def peeking_producer(prices, facts, as_of):
    """BUGGY: always uses the FINAL (restated) eps and report_date if present,
    ignoring restated_known_from -> peeks. For the date case it uses the EARLIER
    re-dated announcement, opening the window before it was public."""
    vis = _visible_facts(facts, as_of)
    anns = []
    for f in vis:
        rd = f.restated_report_date if f.restated_report_date is not None else f.report_date  # PEEK on date
        anns.append((rd, f))
    out = {"within_pead_window": False, "pead_positive_surprise": False, "yoy_surprise": float("nan")}
    if not anns:
        return out
    anns.sort()
    rd, latest = anns[-1]
    out["within_pead_window"] = bool(0 <= (as_of - rd).days <= 90)  # uses peeked (earlier) date
    this_eps = latest.restated_eps if latest.restated_eps is not None else latest.eps  # PEEK on value
    yago = None
    for f in vis:
        if abs((latest.report_date - f.report_date).days - 365) < 40:
            yago = f
    if yago is not None:
        base = yago.restated_eps if yago.restated_eps is not None else yago.eps  # PEEK on base
        if base not in (0, None):
            yoy = this_eps / base - 1.0
            out["yoy_surprise"] = yoy
            out["pead_positive_surprise"] = bool(out["within_pead_window"] and yoy > 0.0)
    return out


print("=" * 80)
print("HONEST producer (must PASS all hazard cases):")
print("=" * 80)
honest_ok = True
for name, builder in CASE_BUILDERS.items():
    r = audit_earnings_producer(honest_producer, builder())
    print(format_case(r)); print()
    honest_ok &= (r.verdict == PASS)

print("=" * 80)
print("PEEKING producer (must FAIL H1 date_reanchor + H2 value_restatement):")
print("=" * 80)
peek_caught = {}
for name, builder in CASE_BUILDERS.items():
    r = audit_earnings_producer(peeking_producer, builder())
    print(format_case(r)); print()
    peek_caught[name] = r.verdict

# expectations: honest passes everything; peeker fails the two cases where the
# restated value/date is NOT yet public but changes the answer.
peek_expected_fail = {"value_restatement", "date_reanchor"}
peek_ok = all((peek_caught[n] == FAIL_PEEK) == (n in peek_expected_fail) for n in CASE_BUILDERS)

print("=" * 80)
print(f"honest producer all-PASS:            {'PASS' if honest_ok else 'FAIL'}")
print(f"peeker caught on exactly H1+H2:       {'PASS' if peek_ok else 'FAIL'}  ({ {k:v for k,v in peek_caught.items()} })")
print(f"\nALL CHECKS: {'PASS' if (honest_ok and peek_ok) else 'FAIL'}")
