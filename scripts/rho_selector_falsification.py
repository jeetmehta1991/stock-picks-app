#!/usr/bin/env python
"""B1770: is the -0.8 IS/OOS rank correlation caused by the EXIT SELECTOR?

L502 recorded rho = -0.779 / -0.865 (p < 0.001) between in-sample and holdout
Sharpe across step-1 producer combinations, and named the falsification test:

    "re-grade with the exit FIXED to production instead of selected; if rho
     moves toward 0 the selector is the cause, and if it stays at -0.8 the
     hypothesis is wrong."

That test is computable OFFLINE from the cached step-1 artifacts, which carry
`is_sharpe`, holdout `sharpe` and the `exit` used, per combination. No re-run.

The mechanism under test: each combination's exit is chosen from ~26 candidates
ON IN-SAMPLE DATA. A high IS Sharpe then partly measures how well the selector
fitted in-sample noise, which cannot persist. Holding the exit FIXED removes the
selection step; if the inversion is selection-induced, the within-exit
correlation should be much closer to zero than the pooled one.

Pooled-vs-within is also a textbook confound check (Simpson's paradox): a
pooled correlation can be dominated by BETWEEN-GROUP structure that has nothing
to do with the within-group relationship.

HAND-RUN: python scripts/rho_selector_falsification.py
"""
from __future__ import annotations

import collections
import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def spearman(xs, ys):
    """Spearman rho with average ranks for ties. No scipy dependency."""
    n = len(xs)
    if n < 4:
        return None, n

    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    if dx == 0 or dy == 0:
        return None, n
    return num / (dx * dy), n


def analyse(path: pathlib.Path) -> None:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = [r for r in d.get("results", [])
            if isinstance(r, dict)
            and r.get("is_sharpe") is not None
            and r.get("sharpe") is not None]
    if not rows:
        print(f"{path.name}: no gradable rows")
        return

    print(f"\n=== {path.name}  ({len(rows)} gradable rows) ===")
    pooled, n = spearman([r["is_sharpe"] for r in rows],
                         [r["sharpe"] for r in rows])
    print(f"  POOLED across all exits ....... rho = {pooled:+.3f}  (n={n})")

    by = collections.defaultdict(list)
    for r in rows:
        by[r.get("exit")].append(r)

    print(f"  WITHIN each exit (selector held fixed):")
    withins = []
    for ex, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        rho, m = spearman([r["is_sharpe"] for r in rs], [r["sharpe"] for r in rs])
        if rho is None:
            print(f"    {str(ex)[:26]:<28} n={m:<4} (too few / no variance)")
            continue
        withins.append((rho, m))
        print(f"    {str(ex)[:26]:<28} n={m:<4} rho = {rho:+.3f}")

    if withins:
        wsum = sum(r * m for r, m in withins)
        wtot = sum(m for _, m in withins)
        print(f"  n-weighted mean WITHIN-exit rho = {wsum/wtot:+.3f}")
        print(f"  pooled {pooled:+.3f}  ->  within {wsum/wtot:+.3f}   "
              f"(shift {wsum/wtot - pooled:+.3f})")


def main() -> int:
    files = sorted(glob.glob(str(ROOT / "output_audit" / "b17*_*span*.json")))
    if not files:
        print("no cached step-1 artifacts found")
        return 1
    print("B1770 FALSIFICATION TEST (L502): does holding the EXIT fixed move rho?")
    print("  selector-induced  => within-exit rho much closer to 0 than pooled")
    print("  hypothesis wrong  => within-exit rho stays strongly negative")
    for f in files:
        analyse(pathlib.Path(f))
    return 0


if __name__ == "__main__":
    sys.exit(main())
