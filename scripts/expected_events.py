#!/usr/bin/env python
"""S6-B2260 / L685: will this run produce the event it is meant to measure?

WHY THIS EXISTS. The B2207a parallel smoke ran both arms to completion and
produced ZERO trades - so no cube, no post-config battery, and no ledger write,
which meant the concurrent-write contention the smoke existed to create was
never created. The run was sized for SPEED and nothing asked whether it would
produce a trade.

The arithmetic is one line and was available before launch:

    smc_breaker_block_long fires 85 times over 200 tickers x 1 year
    the smoke bought 5 tickers x 3 months = 1.25 ticker-years
    expected fires = 85 * 1.25 / 200 = 0.53

**Zero is the modal outcome at that exposure.**

THE RULE THIS ENFORCES: a test has TWO size constraints pulling opposite ways -
small enough to be safe, and LARGE ENOUGH TO PRODUCE THE EVENT IT MEASURES.
Costing only the first is how a run gets sized into uselessness while every
safety check passes.

SCOPE, stated because it is narrow: this applies to a probe that must GENERATE
its own events. A probe that READS events which already exist - an audit over
committed cubes, say - needs no such costing, and that is the discriminator
found by sweeping this session's four probes (only one of them needed it).

Picking the RATE is a judgment this script cannot make: which cube, which
strategy, which exposure unit. It takes the rate as an argument and does the
arithmetic honestly; choosing the basis remains the caller's.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Below this many expected events, a generating probe cannot distinguish
# "the mechanism is broken" from "nothing happened to fire" - which is exactly
# the ambiguity the B2207a smoke landed in. Several, not one, and never a
# fraction.
MIN_EXPECTED_EVENTS = 5.0


def expected_events(base_events: float, base_exposure: float,
                    probe_exposure: float) -> float:
    """Scale a MEASURED event count to a probe's exposure.

    All three arguments must share an exposure unit (ticker-years here). The
    function does no unit conversion on purpose: a silent unit change is the
    L653 grain-stale defect, and the caller who knows the unit should state it.
    """
    if base_exposure <= 0:
        raise ValueError("base_exposure must be positive")
    return base_events * probe_exposure / base_exposure


def ticker_years(n_tickers: int, months: float) -> float:
    return n_tickers * (months / 12.0)


def check(base_events: float, base_exposure: float, probe_exposure: float,
          floor: float = MIN_EXPECTED_EVENTS) -> tuple[int, str]:
    """Exit 0 = enough exposure, 2 = under the floor, 1 = unusable inputs."""
    try:
        exp = expected_events(base_events, base_exposure, probe_exposure)
    except ValueError as e:
        return 1, f"CANNOT JUDGE: {e}"
    base = (f"expected {exp:.2f} events "
            f"(rate {base_events:g} per {base_exposure:g} exposure, "
            f"probe exposure {probe_exposure:g}, floor {floor:g})")
    if exp < floor:
        return 2, (f"UNDER THE SIGNAL FLOOR: {base}. At this exposure a null "
                   f"result cannot distinguish a broken mechanism from nothing "
                   f"having fired - which is what the B2207a smoke measured. "
                   f"Enlarge the probe or state that a null proves nothing.")
    return 0, f"SUFFICIENT: {base}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-events", type=float, required=True,
                    help="MEASURED event count at the base exposure")
    ap.add_argument("--base-exposure", type=float, required=True,
                    help="the exposure that produced --base-events, e.g. ticker-years")
    ap.add_argument("--tickers", type=int, help="probe ticker count")
    ap.add_argument("--months", type=float, help="probe window in months")
    ap.add_argument("--probe-exposure", type=float,
                    help="probe exposure directly, instead of --tickers/--months")
    ap.add_argument("--floor", type=float, default=MIN_EXPECTED_EVENTS)
    a = ap.parse_args()
    if a.probe_exposure is None:
        if a.tickers is None or a.months is None:
            print("give --probe-exposure, or both --tickers and --months")
            return 1
        a.probe_exposure = ticker_years(a.tickers, a.months)
    code, msg = check(a.base_events, a.base_exposure, a.probe_exposure, a.floor)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
