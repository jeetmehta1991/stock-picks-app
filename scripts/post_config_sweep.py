#!/usr/bin/env python
"""B1775: execute MANDATORY POST-CONFIG step 3 mechanically.

The runbook's step-3 "outlier + discrepancy sweep" is a ten-row table that has
always been HAND-RUN. `S6-B1680f` recorded it as "still 3 of 9" and
`S6-B1647b` has sat open since wave 1 finished. **A checklist that is hand-run
is a checklist that gets skipped** - the skill says it outright: prose rules
without an executable verifier decay, and the only no-silent-miss catches that
have worked here were programmatic.

Each row returns PASS / FAIL / N/A with its own evidence, so a skipped row is
visible instead of absent.

    1  cube entries == grid max fires        silent diagnosis loss (L454)
    2  verdict distribution                  NO_EXIT_SELECTABLE is a SAMPLE-SIZE
                                             verdict, not exit quality
    3  rank by ci_lo, NOT sharpe             the higher Sharpe can have a
                                             NEGATIVE lower bound (L455)
    4  exits_effective vs 26                 duplicates collapse (L461)
    5  PASS rows with marginal ci_lo         5 of 200 at +0.08 is WEAK
    6  any PASS selecting a DEGRADED exit    regime_flip is a time stop (B1771)
    7  every swept LEVEL changes the outcome a level that changes nothing is a
                                             wasted dimension (L473)
    8  top-N holds N DISTINCT fire-sets      cfg2's top 10 was 4 candidates
                                             wearing 10 rows (L473)
    9  equivalence-class members keep the    a (fires, exit, sharpe) de-dup key
       SAME FIRES                            can merge different fire-sets
   10  DEGRADED exits per cube               delegated to measure_degraded_exits

HAND-RUN:
    python scripts/post_config_sweep.py --cube output_w1_sw20_span50 \
                                        --grid output_audit/b1718_p0fix_span50.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

MARGINAL_CI = 0.15
DEGRADED = ("regime_flip", "smart_money_reversal", "reverse_signal")


class Sweep:
    def __init__(self, cube: pathlib.Path | None, grid: pathlib.Path | None):
        self.rows: list[tuple[str, str, str]] = []
        self.cube = cube
        self.g = json.loads(grid.read_text(encoding="utf-8")) if grid else None
        self.res = (self.g or {}).get("results", []) or []
        self.entries = None
        if cube:
            import pandas as pd
            p = cube / "trade_exit_detail.csv" if cube.is_dir() else cube
            d = pd.read_csv(p, low_memory=False)
            self.entries = d.groupby(["ticker", "entry_date"]).ngroups
            self.d = d

    def add(self, name, status, evidence):
        self.rows.append((name, status, evidence))

    # ---- rows -------------------------------------------------------------
    def r1_entries_vs_fires(self):
        if self.entries is None or not self.res:
            return self.add("1 entries == grid max fires", "N/A", "cube or grid absent")
        mx = max(int(r.get("fires") or 0) for r in self.res)
        loss = (self.entries - mx) / self.entries if self.entries else 0
        ok = abs(loss) <= 0.02
        # B1775: this row is ALSO the PROVENANCE check (#255). A grid graded
        # against a DIFFERENT cube shows up here as a large mismatch, which is
        # exactly how the b1715/b1718 grids were identified as wave 1 (302/320)
        # rather than output_batch_A_150 (164) - after I had already used a
        # defect from the latter to explain a number from the former.
        self.add("1 entries == grid max fires", "PASS" if ok else "FAIL",
                 f"cube entries {self.entries} vs grid max fires {mx} "
                 f"({loss:+.1%}; gate aborts above 2%) - ALSO the provenance "
                 f"check (#255): a grid from another cube mismatches here")

    def r2_verdicts(self):
        if not self.res:
            return self.add("2 verdict distribution", "N/A", "grid absent")
        c = collections.Counter(r.get("verdict", "(none)") for r in self.res)
        nes = c.get("NO_EXIT_SELECTABLE", 0)
        self.add("2 verdict distribution", "INFO",
                 f"{dict(c)} - NO_EXIT_SELECTABLE={nes} is a SAMPLE-SIZE verdict, "
                 "not a statement about exit quality")

    def r3_rank_by_ci_lo(self):
        gr = [r for r in self.res if r.get("ci_lo") is not None
              and r.get("sharpe") is not None]
        if not gr:
            return self.add("3 rank by ci_lo not sharpe", "N/A", "no graded rows")
        top_s = sorted(gr, key=lambda r: -r["sharpe"])[:5]
        neg = [r for r in top_s if r["ci_lo"] < 0]
        self.add("3 rank by ci_lo not sharpe", "FAIL" if neg else "PASS",
                 f"{len(neg)} of top-5-by-sharpe have a NEGATIVE ci_lo"
                 + (f" (best sharpe {top_s[0]['sharpe']:+.3f} has ci_lo "
                    f"{top_s[0]['ci_lo']:+.3f})" if top_s else ""))

    def r4_exits_effective(self):
        if not self.res:
            return self.add("4 exits_effective vs 26", "N/A", "grid absent")
        sel = {r.get("exit") for r in self.res if r.get("exit")}
        self.add("4 exits_effective vs 26", "INFO",
                 f"{len(sel)} distinct exits actually selected across {len(self.res)} "
                 f"rows: {sorted(sel)}")

    def r5_marginal_pass(self):
        p = [r for r in self.res if r.get("verdict") == "PASS"]
        if not p:
            return self.add("5 PASS rows with marginal ci_lo", "N/A",
                            "no PASS rows in this grid")
        marg = [r for r in p if (r.get("ci_lo") or 0) < MARGINAL_CI]
        self.add("5 PASS rows with marginal ci_lo",
                 "FAIL" if marg else "PASS",
                 f"{len(marg)} of {len(p)} PASS rows sit below ci_lo {MARGINAL_CI}")

    def r6_degraded_pass(self):
        p = [r for r in self.res if r.get("verdict") == "PASS"]
        if not p:
            return self.add("6 PASS selecting a DEGRADED exit", "N/A",
                            "no PASS rows in this grid")
        bad = [r for r in p if r.get("exit") in DEGRADED]
        self.add("6 PASS selecting a DEGRADED exit", "FAIL" if bad else "PASS",
                 f"{len(bad)} PASS rows select one of {DEGRADED}")

    def r7_levels_matter(self):
        if not self.res:
            return self.add("7 every swept LEVEL changes the outcome", "N/A",
                            "grid absent")
        knobs = [k for k in ("close_mitigation", "break_pct_max", "age_bars_max",
                             "tail_n") if k in self.res[0]]
        dead = []
        for k in knobs:
            by = collections.defaultdict(set)
            for r in self.res:
                by[r.get(k)].add((r.get("fires"), r.get("exit")))
            if len(by) > 1 and len({frozenset(v) for v in by.values()}) == 1:
                dead.append(k)
        self.add("7 every swept LEVEL changes the outcome",
                 "FAIL" if dead else "PASS",
                 f"knobs {knobs}; dimensions that change NOTHING: {dead or 'none'}")

    def r8_topn_distinct(self, n=10):
        gr = [r for r in self.res if r.get("ci_lo") is not None]
        if not gr:
            return self.add("8 top-N holds N DISTINCT fire-sets", "N/A",
                            "no graded rows")
        top = sorted(gr, key=lambda r: -r["ci_lo"])[:n]
        distinct = len({(r.get("fires"), r.get("exit")) for r in top})
        self.add("8 top-N holds N DISTINCT fire-sets",
                 "PASS" if distinct == len(top) else "FAIL",
                 f"top-{len(top)} by ci_lo holds {distinct} distinct (fires, exit) "
                 "pairs")

    def r9_equivalence_classes(self):
        gr = [r for r in self.res if r.get("fires") is not None]
        if not gr:
            return self.add("9 equivalence-class members keep SAME FIRES", "N/A",
                            "grid absent")
        key = collections.defaultdict(set)
        for r in gr:
            key[(r.get("fires"), r.get("exit"), r.get("sharpe"))].add(
                tuple(sorted((k, str(r.get(k))) for k in
                             ("close_mitigation", "break_pct_max",
                              "age_bars_max", "tail_n") if k in r)))
        merged = {k: v for k, v in key.items() if len(v) > 1}
        self.add("9 equivalence-class members keep SAME FIRES", "INFO",
                 f"{len(merged)} de-dup keys cover >1 parameter combination "
                 "(expected: identical outcomes DO tie; the risk is different "
                 "fire-sets tying, which fires cannot distinguish here)")

    def r10_degraded(self):
        if not self.cube:
            return self.add("10 DEGRADED exits per cube", "N/A", "cube absent")
        self.add("10 DEGRADED exits per cube", "SEE",
                 f"run: python scripts/measure_degraded_exits.py {self.cube}")

    def run(self):
        for m in (self.r1_entries_vs_fires, self.r2_verdicts, self.r3_rank_by_ci_lo,
                  self.r4_exits_effective, self.r5_marginal_pass,
                  self.r6_degraded_pass, self.r7_levels_matter,
                  self.r8_topn_distinct, self.r9_equivalence_classes,
                  self.r10_degraded):
            try:
                m()
            except Exception as exc:  # noqa: BLE001
                self.add(m.__name__, "ERROR", f"{type(exc).__name__}: {exc}")
        return self.rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube")
    ap.add_argument("--grid")
    a = ap.parse_args()
    s = Sweep(pathlib.Path(a.cube) if a.cube else None,
              pathlib.Path(a.grid) if a.grid else None)
    rows = s.run()
    print(f"MANDATORY POST-CONFIG - step 3 sweep")
    print(f"  cube: {a.cube}\n  grid: {a.grid}\n")
    w = max(len(r[0]) for r in rows)
    for name, status, ev in rows:
        print(f"  {status:<5} {name:<{w}}  {ev}")
    bad = [r for r in rows if r[1] in ("FAIL", "ERROR")]
    print(f"\n  {len(bad)} FAIL/ERROR of {len(rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
