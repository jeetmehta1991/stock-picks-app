#!/usr/bin/env python
"""B1612 / CHECKLIST #207 - is every SWEPT parameter reachable by the ENGINE?

The optimisation sweep grades SUBSET-SAFE parameters OFFLINE, re-deriving fires
from cached OHLCV instead of re-running the engine. That is what makes 4,000
combinations affordable. It also means the search space can contain gates the
ENGINE CANNOT APPLY - and nothing noticed, because the grader is perfectly happy
to simulate a filter that exists only inside itself.

MEASURED 2026-08-17, four of six swept parameters are grader-only:

    P1 swing_length     IMPLEMENTED      config.SMC_SWING_LENGTH -> screener
    P2 close_mitigation NOT IMPLEMENTED  smc_ict calls _smc.ob(ohlc, swings)
    P3 tail_n           NOT IMPLEMENTED  smc_ict has a hardcoded .tail(20)
    P4 age_bars_max     NOT IMPLEMENTED  the breaker loop has no age filter
    P5 break_pct_max    NOT IMPLEMENTED  no occurrence in engine code at all
    P6 ema span         IMPLEMENTED      config.STRAT_EMA_SPAN -> screener

A winning combination on any of P2-P5 is therefore NOT DEPLOYABLE as it stands:
the engine would keep firing at its hardcoded values and the live strategy would
not reproduce its own backtest. That is the `regime_flip` failure again (L461) -
a number carrying a label whose logic never ran - moved one stage earlier, from
exits to entry gates.

This check asserts the ENGINE-side facts against live source, so drift is caught
in BOTH directions: a parameter silently losing its wiring, and a parameter
quietly gaining it without the table being updated.

Usage:  python scripts/verify_engine_implemented.py
Exit:   0 = every swept parameter is implemented or DECLARED unimplemented with
            an open ticket; 2 = an undeclared gap, or the table has drifted.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

QUEUE = Path("EXECUTION_QUEUE.md")

# param -> (implemented?, file, the exact source token that proves it, ticket)
# `token` is matched against the file's live text. For an UNIMPLEMENTED entry the
# token is the evidence it is NOT parameterised (e.g. the hardcoded literal), so
# the check fails if someone implements it without updating this table.
PARAMS = {
    "P1 swing_length": (
        True, "backtest/signals/screener.py",
        "swing_length=_cfg.SMC_SWING_LENGTH", None),
    "P2 close_mitigation": (
        False, "backtest/signals/smc_ict.py",
        "_smc.ob(ohlc, swings)", "S6-B1612f"),
    "P3 tail_n": (
        False, "backtest/signals/smc_ict.py",
        "ob_events.tail(20)", "S6-B1612f"),
    "P4 age_bars_max": (
        False, "backtest/signals/smc_ict.py",
        "ob_events.tail(20)", "S6-B1612f"),
    "P5 break_pct_max": (
        False, "backtest/signals/smc_ict.py",
        "close > float(top)", "S6-B1612f"),
    "P6 ema span": (
        True, "backtest/signals/screener.py",
        '_ema_key = f"price_above_ema_{_cfg.STRAT_EMA_SPAN}"', None),
}
# P4 has no engine expression at all; its evidence is that the breaker loop
# applies no age filter. This regex must find NOTHING inside that loop.
BREAKER_LOOP = (r"ob_events = ob_df\[ob_df\[.OB.\]\.fillna\(0\) != 0\]"
                r".*?out\[.smc_breaker_block_bullish.\]")
AGE_FILTER = r"age_bars|current_idx - (?:pos|idx)|event_recency_bars"


def check() -> list[str]:
    failures: list[str] = []
    queue = QUEUE.read_text(encoding="utf-8", errors="ignore") if QUEUE.exists() else ""
    for name, (implemented, rel, token, ticket) in PARAMS.items():
        src = Path(rel).read_text(encoding="utf-8", errors="ignore")
        present = token in src
        if implemented and not present:
            failures.append(
                f"{name}: declared ENGINE-IMPLEMENTED but `{token}` is gone from "
                f"{rel}. Either the wiring regressed or the table is stale - "
                f"a swept parameter the engine cannot apply produces a winner "
                f"that will not reproduce live (L475).")
        if not implemented:
            if not present:
                failures.append(
                    f"{name}: declared NOT-IMPLEMENTED on the evidence of "
                    f"`{token}` in {rel}, and that token is GONE. If it is now "
                    f"parameterised, update this table and close {ticket}.")
            elif ticket and ticket not in queue:
                failures.append(
                    f"{name}: NOT implemented in the engine and ticket {ticket} "
                    f"is absent from EXECUTION_QUEUE.md. An unimplemented swept "
                    f"parameter must carry an open implementation ticket.")

    # P4's evidence is an ABSENCE, so assert it directly rather than by token.
    smc = Path("backtest/signals/smc_ict.py").read_text(encoding="utf-8",
                                                        errors="ignore")
    m = re.search(BREAKER_LOOP, smc, re.S)
    if not m:
        failures.append(
            "P4 age_bars_max: could not locate the breaker-block loop in "
            "smc_ict.py - this check has gone stale and must be re-anchored.")
    elif re.search(AGE_FILTER, m.group(0)):
        failures.append(
            "P4 age_bars_max: the breaker loop now contains an age filter. It "
            "was swept as a NEW GATE with no engine counterpart; if it has been "
            "implemented, update this table and close S6-B1612f.")
    return failures


def main() -> int:
    failures = check()
    impl = [k for k, v in PARAMS.items() if v[0]]
    gap = [k for k, v in PARAMS.items() if not v[0]]
    print(f"swept parameters: {len(PARAMS)}")
    print(f"  ENGINE-IMPLEMENTED ({len(impl)}): {', '.join(impl)}")
    print(f"  GRADER-ONLY ({len(gap)}): {', '.join(gap)}")
    print("\n  A winner using a GRADER-ONLY value is NOT DEPLOYABLE until the "
          "engine\n  can apply it - the live strategy would not reproduce its "
          "own backtest.")
    if failures:
        print("\nFAIL:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 2
    print("\nPASS - every gap is DECLARED and carries an open ticket.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
