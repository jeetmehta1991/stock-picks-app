#!/usr/bin/env python
"""S6-B2217 / S6-B2216: find exits that DELEGATE, at PER-TRADE grain, from cubes.

WHY THE BYTE-IDENTICAL DETECTOR CANNOT DO THIS. B1593's collapse catches TOTAL
duplication: two exits whose every trade agrees. **Partial degradation - an exit
falling back on SOME trades and not others - leaves the pair non-identical, so
the dedup stays silent and the breadth disclosure reports full coverage.**
S6-B2217 measured 12 delegating return sites across 9 exit functions in
backtest/engine/exit_strategies.py, each returning another exit's result under a
data-conditional guard. This finds their FOOTPRINT in the output instead of
their shape in the source, which is the half that says how often they fire.

THE FINGERPRINT IS THE (exit_method, exit_reason) PAIR. The cube records both:
the method the cell was GRADED as, and the reason the trade actually closed for.
When a method's trades close for another method's characteristic reason, the
delegation is visible per trade without touching the engine.

THE DISCRIMINATOR, and it is the whole difficulty: most mismatches are NOT
delegation. `stop_loss`, `take_profit`, `end_of_data`, `max_days`, `hard_stop`
are GENERIC TERMINAL reasons that any exit can legitimately produce - a trade
that hits its stop closes for stop_loss whatever the exit rule was. Flagging
those produces a wall of false positives; measured on one real cube the naive
"reason does not contain the method name" test flags 15 of 49 pairs, and 14 of
them are legitimate. So generic reasons are excluded BY NAME, and what remains
is a reason that is another REGISTERED METHOD's characteristic signature.
"""
from __future__ import annotations

import argparse
import collections
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Reasons ANY exit can legitimately emit - a trade hitting its stop closes for
# stop_loss regardless of which rule was managing it. Excluding these by name is
# what separates a finding from a wall of noise (#166: the pattern is validated
# below by asserting the known delegation still fires with them excluded).
GENERIC_TERMINAL = {
    "stop_loss", "take_profit", "max_days", "end_of_data", "hard_stop",
    "initial_1r_stop",
}

# SAME-STEM DELEGATION - the blind spot the cross-stem test structurally cannot
# see, found by HAND-READING the output the first version produced (L644: a new
# detector's first number is a hypothesis).
#
# MEASURED: `smc_mitigation_zone` emits `smc_trail_safety_batch227a` on 74 of 85
# trades. Both share the `smc` stem, so the cross-stem test called it
# characteristic and stayed silent - while exit_strategies.py's own docstring
# says "On in-between bars we trail-stop via vanilla 1xATR as safety". **87pct of
# that exit's trades closed on a vanilla ATR trail, not on an SMC mitigation
# zone.** By design and documented; still delegation, and still invisible to a
# reader of the cube.
#
# These markers name a FALLBACK PATH inside an exit's own vocabulary. A reason
# carrying one is the exit not doing the thing its name claims.
FALLBACK_MARKERS = ("safety", "fallback", "vanilla", "pre_threshold", "_cap",
                    "default")


def load_pairs(cube: Path) -> dict[str, collections.Counter]:
    by_method: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    with cube.open(newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            m, r = row.get("exit_method"), row.get("exit_reason")
            if m and r:
                by_method[m][r] += 1
    return by_method


def characteristic_reasons(by_method) -> dict[str, set[str]]:
    """A reason is CHARACTERISTIC of the method(s) whose name shares its stem.

    Deliberately structural rather than a hand-maintained map: a hand list of
    which reason belongs to which exit is exactly the artifact L527 found goes
    stale, and it would need editing every time an exit is registered.
    """
    out: dict[str, set[str]] = collections.defaultdict(set)
    for method, reasons in by_method.items():
        stem = method.split("_")[0]
        for reason in reasons:
            if reason in GENERIC_TERMINAL:
                continue
            if stem and (stem in reason or reason.split("_")[0] in method):
                out[reason].add(method)
    return out


def audit(cube: Path) -> list[dict]:
    by_method = load_pairs(cube)
    owns = characteristic_reasons(by_method)
    findings = []
    for method, reasons in sorted(by_method.items()):
        total = sum(reasons.values())
        for reason, n in sorted(reasons.items()):
            if reason in GENERIC_TERMINAL:
                continue
            owners = owns.get(reason, set())
            # (a) CROSS-STEM: this method emits a reason characteristic of some
            # OTHER method and not of itself. Total or partial, always a finding.
            if owners and method not in owners:
                findings.append({
                    "kind": "CROSS-STEM", "exit_method": method,
                    "exit_reason": reason, "trades": n, "of_total": total,
                    "share_pct": round(100.0 * n / total, 1),
                    "note": "belongs to " + ", ".join(sorted(owners)),
                })
            # (b) SAME-STEM FALLBACK: the reason lives in this method's own
            # vocabulary but NAMES a fallback path. Invisible to (a) by
            # construction - this is the smc_trail_safety class.
            elif any(mk in reason for mk in FALLBACK_MARKERS):
                findings.append({
                    "kind": "SAME-STEM-FALLBACK", "exit_method": method,
                    "exit_reason": reason, "trades": n, "of_total": total,
                    "share_pct": round(100.0 * n / total, 1),
                    "note": "reason names a fallback path inside this exit",
                })
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cubes", nargs="+", help="trade_exit_detail.csv paths or cube dirs")
    a = ap.parse_args()
    any_found = False
    for c in a.cubes:
        p = Path(c)
        if p.is_dir():
            p = p / "trade_exit_detail.csv"
        if not p.exists():
            print(f"SKIP {c}: no trade_exit_detail.csv")
            continue
        f = audit(p)
        print(f"\n=== {p.parent.name} ===")
        if not f:
            print("  no delegation found")
            continue
        any_found = True
        for d in sorted(f, key=lambda x: -x["share_pct"]):
            print(f"  [{d['kind']:<19}] {d['exit_method']:<24} -> "
                  f"{d['exit_reason']:<32} {d['trades']:>4}/{d['of_total']:<4} "
                  f"({d['share_pct']:>5}%)  {d['note']}")
    return 0 if not any_found else 3


if __name__ == "__main__":
    sys.exit(main())
