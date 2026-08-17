#!/usr/bin/env python
"""B1610 / CHECKLIST #203 - POST-RUN band diagnostics for a factorial grid.

A swept level that changes nothing is a wasted search dimension, and nothing
in this repo checked for one. The P3 `tail_n` band [3, 5, 10, 20] was carried
through 400 graded combinations across two configs before the owner noticed
that three of its levels returned the same 68 fires.

MEASURED once the question was finally asked (B1610):

    cfg1  10 -> 20 changed the outcome in   0 of 50 parameter groups
    cfg2  10 -> 20 changed the outcome in   2 of 50 parameter groups
    cfg1  200 combinations ->  71 distinct results  (64pct redundant)
    cfg2  200 combinations ->  94 distinct results  (53pct redundant)

The band was not broken; `tail_n` moves fires from 4 to 420 across its FULL
range. The band was MISPLACED - it sampled [3, 5, 10, 20] where the parameter
had already saturated (39.8 / 68.8 / 98.6 / 100.0 pct of fires admitted), and
the region that actually discriminates is 1-3, BELOW the band's floor. The
plan's own derivation text said "measured rank of qualifying event was 1-4;
band spans that" - it did not, and nothing compared the band to its own
stated derivation.

This is the POST-RUN half of the plan's design rule 7 ("derive band values
from the measured distribution"). Rule 7 is a pre-run prose rule and it decayed
exactly as prose rules do (L464). This script is the part that runs.

Usage
-----
    python scripts/verify_grid_bands.py output_audit/b1608_cfg2_grid.json
    python scripts/verify_grid_bands.py <grid.json> --keys a,b,c --min-effect 0.10

Exit codes: 0 = every level earns its place, 2 = at least one inert level.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

# A level pair that moves the outcome in fewer than this fraction of parameter
# groups is INERT: it is spending combinations without buying information.
DEFAULT_MIN_EFFECT = 0.10
DEFAULT_KEYS = ("close_mitigation", "break_pct_max", "age_bars_max", "tail_n")
# Ordering key that puts None last regardless of the other levels' type.
_ORD = lambda v: (v is None, v if v is not None else 0)  # noqa: E731


def _sig(row: dict, keys) -> tuple:
    """The graded OUTCOME of a combination, not just its fire count.

    Two combinations that keep the same COUNT of fires but different fires are
    genuinely different points in the search. Comparing the selected exit and
    the Sharpe alongside the count is what makes "duplicate" mean duplicate.
    """
    sharpe = row.get("sharpe")
    return (row.get("fires"), row.get("exit"),
            round(sharpe, 9) if isinstance(sharpe, (int, float)) else sharpe)


def marginal_effect(results, key, keys) -> dict:
    """How often does `key` change the outcome, holding every other key fixed?"""
    others = [k for k in keys if k != key]
    groups: dict[tuple, dict] = collections.defaultdict(dict)
    for r in results:
        groups[tuple(r.get(o) for o in others)][r.get(key)] = _sig(r, keys)
    levels = sorted({r.get(key) for r in results}, key=_ORD)
    changed = sum(1 for g in groups.values() if len(set(g.values())) > 1)
    pairs = []
    for a, b in zip(levels, levels[1:]):
        n = sum(1 for g in groups.values()
                if a in g and b in g and g[a] != g[b])
        pairs.append({"from": a, "to": b, "groups": len(groups), "changed": n,
                      "effect": (n / len(groups)) if groups else 0.0})
    return {"param": key, "levels": levels, "groups": len(groups),
            "changed": changed,
            "effect": (changed / len(groups)) if groups else 0.0,
            "pairs": pairs}


def duplicate_rate(results, keys) -> tuple[int, int]:
    """(distinct outcomes, redundant combinations) over the whole grid."""
    seen = collections.Counter(_sig(r, keys) for r in results)
    return len(seen), sum(c - 1 for c in seen.values())


def analyse(results, keys, min_effect=DEFAULT_MIN_EFFECT, anchors=None) -> tuple[list, list]:
    """Return (per-param reports, failures). A failure names an inert level.

    `anchors` maps param -> the PRODUCTION value. An anchor is carried so the
    baseline stays reproducible (plan design-rule 7), not to discriminate, so a
    pair whose upper level IS the anchor is reported ANCHOR rather than INERT.
    Without this the gate fires forever on a deliberate retention and gets
    ignored - which is how a gate dies.
    """
    anchors = anchors or {}
    reports, failures = [], []
    for k in keys:
        if len({r.get(k) for r in results}) < 2:
            continue  # not actually swept in this grid
        rep = marginal_effect(results, k, keys)
        for p in rep["pairs"]:
            p["anchor"] = (k in anchors and p["to"] == anchors[k])
        reports.append(rep)
        for p in rep["pairs"]:
            if p["effect"] < min_effect and not p["anchor"]:
                failures.append(
                    f"{k}: level {p['from']} -> {p['to']} changed the outcome in "
                    f"{p['changed']}/{p['groups']} parameter groups "
                    f"({100 * p['effect']:.0f}pct < {100 * min_effect:.0f}pct). "
                    f"These levels are SATURATED - re-band toward the region "
                    f"where the parameter still separates.")
    return reports, failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("grid", help="grid JSON with a 'results' list")
    ap.add_argument("--keys", default=",".join(DEFAULT_KEYS))
    ap.add_argument("--min-effect", type=float, default=DEFAULT_MIN_EFFECT)
    ap.add_argument("--anchor", action="append", default=[],
                    help="param=value production anchor, exempt from the inert "
                         "check because it exists for reproducibility "
                         "(repeatable, e.g. --anchor tail_n=20)")
    a = ap.parse_args()

    payload = json.loads(Path(a.grid).read_text(encoding="utf-8"))
    results = payload["results"] if isinstance(payload, dict) else payload
    keys = [k.strip() for k in a.keys.split(",") if k.strip()]
    keys = [k for k in keys if any(k in r for r in results)]
    if not results or not keys:
        print("no results or no swept keys found", file=sys.stderr)
        return 2

    distinct, redundant = duplicate_rate(results, keys)
    print(f"grid: {a.grid}")
    print(f"  {len(results)} combinations -> {distinct} DISTINCT outcomes; "
          f"{redundant} redundant ({100 * redundant / len(results):.0f}pct of the search)\n")

    anchors = {}
    for spec in a.anchor:
        k, _, v = spec.partition("=")
        try:
            anchors[k.strip()] = int(v)
        except ValueError:
            anchors[k.strip()] = None if v.strip() == "None" else v.strip()
    reports, failures = analyse(results, keys, a.min_effect, anchors)
    print(f"  {'param':<20} {'levels':<28} {'changes outcome':>16}")
    for rep in reports:
        lv = ", ".join(str(x) for x in rep["levels"])
        print(f"  {rep['param']:<20} [{lv:<26}] "
              f"{rep['changed']:>5}/{rep['groups']:<4} ({100 * rep['effect']:>3.0f}pct)")
        for p in rep["pairs"]:
            mark = ("ANCHOR" if p.get("anchor") else
                    "INERT" if p["effect"] < a.min_effect else "ok")
            print(f"       {str(p['from']):>6} -> {str(p['to']):<6} "
                  f"{p['changed']:>4}/{p['groups']:<4} ({100 * p['effect']:>3.0f}pct)  {mark}")

    if failures:
        print("\nFAIL - inert levels found:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print("\nA level that changes nothing spends a combination without buying\n"
              "information. Re-band against the MEASURED distribution (plan rule 7)\n"
              "and re-grade - re-grading is offline and needs no engine run for a\n"
              "SUBSET-SAFE parameter.", file=sys.stderr)
        return 2
    print("\nPASS - every swept level changes the outcome somewhere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
