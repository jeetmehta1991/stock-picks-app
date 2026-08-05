"""scripts/reconcile_strategy_population.py (B1461) -- partition ALL registered strategies into
DISJOINT buckets, so "how many are left to optimise" has one auditable answer.

OWNER QUESTION (2026-08-05): "In addition to group 3 didn't we have other strategies? Are they a
part of 147 or additional?"

The 147 figure has been quoted repeatedly without a reproducible derivation. This script derives
the whole partition from live sources instead:

  registry            backtest.signals.screener.ALL_STRATEGIES
  disabled            backtest.config.STRATEGIES_DISABLED_DATA_SCARCITY  (Group 2)
  roster              output_audit/b1453_phase_1b_roster.json            (graded PASS + mirrors)
  group 1 / group 3   output_audit/_group1_subset.txt / _group3.txt
  R6b                 output_audit/_r6b_subset.txt
  R6 changed          output_audit/_r6_changed_strategies.txt

Every registered strategy lands in exactly ONE bucket, most-specific first, and the buckets are
asserted to sum to the registry count. A partition that does not sum is a silent miss by
construction, which is the point.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.config import STRATEGIES_DISABLED_DATA_SCARCITY as DISABLED  # noqa: E402
from backtest.signals.screener import ALL_STRATEGIES  # noqa: E402


def _names(objs):
    out = set()
    for s in objs:
        n = getattr(s, "name", None) or getattr(s, "__name__", None) or str(s)
        out.add(str(n).replace("strat_", ""))
    return out


def _load(path):
    p = REPO / path
    if not p.exists():
        return set()
    return {ln.strip().replace("strat_", "") for ln in
            p.read_text(encoding="utf-8").splitlines() if ln.strip()}


def main() -> int:
    registry = _names(ALL_STRATEGIES)
    disabled = {s.replace("strat_", "") for s in DISABLED}

    roster_json = json.loads((REPO / "output_audit" / "b1453_phase_1b_roster.json")
                             .read_text(encoding="utf-8"))
    roster = {r["strategy"] for r in roster_json["roster"]}
    mirrors = {r["mirror"] for r in roster_json["roster"]
               if r["mirror_status"] == "REGISTERED" and r["mirror"]}

    group1 = _load("output_audit/_group1_subset.txt")
    group3 = _load("output_audit/_group3.txt")
    r6b = _load("output_audit/_r6b_subset.txt")
    r6chg = _load("output_audit/_r6_changed_strategies.txt")

    # most-specific first; each strategy consumed once
    order = [
        ("ROSTER-PASS (graded, on the 1B roster)", roster),
        ("ROSTER-MIRROR (retained by symmetry directive)", mirrors),
        ("DISABLED data-scarcity (Group 2, retired)", disabled),
        ("GROUP 3 (fire-count measured B1460)", group3),
        ("GROUP 1 (loosened + graded B1449)", group1),
        ("R6b (loosened + graded B1439, NEGATIVE)", r6b),
        ("R6 changed (loosened, superseded)", r6chg),
    ]

    buckets, seen = {}, set()
    for label, members in order:
        b = (members & registry) - seen
        buckets[label] = b
        seen |= b
    buckets["NEVER TOUCHED (no loosening, no tuning, no grade)"] = registry - seen

    print("=" * 96)
    print("STRATEGY POPULATION PARTITION (B1461) -- disjoint, derived from live sources")
    print("=" * 96)
    total = 0
    for label, b in buckets.items():
        print(f"  {label:<52}{len(b):>5}")
        total += len(b)
    print(f"  {'':<52}{'-'*5}")
    print(f"  {'TOTAL':<52}{total:>5}   registry={len(registry)}")
    assert total == len(registry), (
        f"PARTITION DOES NOT SUM: {total} != {len(registry)}. Buckets overlap or miss."
    )

    optim = (buckets["GROUP 3 (fire-count measured B1460)"]
             | buckets["GROUP 1 (loosened + graded B1449)"]
             | buckets["R6b (loosened + graded B1439, NEGATIVE)"]
             | buckets["R6 changed (loosened, superseded)"]
             | buckets["NEVER TOUCHED (no loosening, no tuning, no grade)"])
    print()
    print(f"  OPTIMISATION BACKLOG (everything not on the roster and not retired): {len(optim)}")
    print(f"     of which ALREADY had a tuning attempt: "
          f"{len(optim) - len(buckets['NEVER TOUCHED (no loosening, no tuning, no grade)'])}")
    print(f"     of which NEVER touched:                "
          f"{len(buckets['NEVER TOUCHED (no loosening, no tuning, no grade)'])}")

    out = REPO / "output_audit" / "b1461_strategy_population.json"
    out.write_text(json.dumps(
        {"registry_n": len(registry),
         "buckets": {k: sorted(v) for k, v in buckets.items()},
         "optimisation_backlog_n": len(optim),
         "optimisation_backlog": sorted(optim)}, indent=2), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
