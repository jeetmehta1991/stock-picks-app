#!/usr/bin/env python
"""B1772: MANDATORY POST-CONFIG step - which exits are not doing what they say?

The runbook (STRATEGY_OPTIMISATION_PLAN 'MANDATORY POST-CONFIG ANALYSIS', step 3)
carries three rows this script finally executes mechanically:

    "measure DEGRADED exits per cube"       (L483)
    "exits_effective vs 26 - duplicates"    (L461)
    "any PASS selecting regime_flip"        (a hand-maintained caveat)

That third row says regime_flip "was a time stop PRE-B1593". B1771 measured it
firing `regime_flip_max_days_20` on 100.0pct of 8,374 trades in a POST-B1593
cube, in both halves of the sample. **A hand-maintained caveat about which
exits are degraded goes stale silently; this measures it per cube instead.**

THREE LENSES
------------
1. DEGENERATE - one `exit_reason` dominates. An exit that always fires the same
   way is not the exit it is named after. `regime_flip` never flips.

2. TEMPORAL STEP - the reason mix changes sharply across the sample. This is the
   B1771 defect: `next_pivot_target` was 100pct silent 3x-ATR fallback for
   eleven quarters (signals_at_entry was not persisted before 2025-02-06) and
   ~20-40pct after. **An exit whose identity changes mid-sample makes every
   IS/OOS comparison across that boundary meaningless** - it ranks one exit and
   grades another.

3. DUPLICATE - two exits produce identical outcomes on most shared trades, so
   "best of 26" is really best of fewer.

Nothing here changes an exit. Changing one is a rule change and needs owner
approval; this reports.

HAND-RUN:
    python scripts/measure_degraded_exits.py <dir-or-trade_exit_detail.csv> [...]
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

DEGENERATE_AT = 0.95     # one reason this dominant => the exit never varies
STEP_AT = 0.40           # reason-share swing this large across halves => step
DUP_AT = 0.90            # identical outcomes on this share => duplicate


def _load(p: pathlib.Path) -> pd.DataFrame:
    if p.is_dir():
        p = p / "trade_exit_detail.csv"
    if not p.exists():
        raise SystemExit(f"not found: {p}")
    d = pd.read_csv(p, low_memory=False)
    need = {"exit_method", "exit_reason", "entry_date", "pnl_pct"}
    missing = need - set(d.columns)
    if missing:
        raise SystemExit(f"{p}: missing columns {sorted(missing)}")
    d["_dt"] = pd.to_datetime(d["entry_date"], errors="coerce")
    return d


def _name_tokens(s: str) -> set[str]:
    import re as _re
    return {t for t in _re.split(r"[^a-z0-9]+", s.lower()) if len(t) >= 2}


def _stem_overlap(a: set[str], b: set[str]) -> bool:
    """Tokens match on a STEM, not on exact equality.

    B1772c: exact token matching called `atr_trail_1x` firing `atr_trailing_stop`
    a mismatch, because `trail` != `trailing`. **That is CHECKLIST #239 - encode
    the stem, not the conjugation - inside a check written minutes after citing
    it.** The rule keeps re-appearing because every new matcher is a fresh place
    to forget it.
    """
    for x in a:
        for y in b:
            if x == y or (len(x) >= 4 and y.startswith(x)) or                     (len(y) >= 4 and x.startswith(y)):
                return True
    return False


def degenerate(d: pd.DataFrame) -> list[tuple]:
    """Dominant reason that does NOT correspond to the exit's own name.

    B1772b: the first version flagged any exit with one dominant reason, which
    caught `time_stop_20d` firing `time_stop_20d` on 100pct of trades - that is
    the exit working, not failing. **A lens that flags 14 of 26 exits including
    the correct ones is noise.** What matters is a MISMATCH: `regime_flip`
    firing `regime_flip_max_days_20` shares a token, so name-overlap alone is
    not enough either - the reason must also not be the exit's OWN action.
    """
    out = []
    for ex, g in d.groupby("exit_method"):
        vc = g.exit_reason.value_counts(normalize=True)
        if not len(vc) or vc.iloc[0] < DEGENERATE_AT:
            continue
        reason = str(vc.index[0])
        # the exit is doing something OTHER than its name when the dominant
        # reason contributes tokens the name does not have (max_days on a
        # regime-flip exit), or shares no token at all.
        rt, nt = _name_tokens(reason), _name_tokens(ex)
        # FALLBACK-ish tokens the exit's own name does not carry: the exit
        # ended for a reason unrelated to what it is named after.
        alien = {"max", "days", "safety", "fallback"} & (rt - nt)
        if not _stem_overlap(rt, nt) or alien:
            out.append((ex, reason, vc.iloc[0], len(g)))
    return sorted(out, key=lambda r: -r[2])


def temporal_step(d: pd.DataFrame) -> list[tuple]:
    """Largest per-reason share swing between the two halves of the sample."""
    cut = d["_dt"].median()
    out = []
    for ex, g in d.groupby("exit_method"):
        a = g[g["_dt"] <= cut].exit_reason.value_counts(normalize=True)
        b = g[g["_dt"] > cut].exit_reason.value_counts(normalize=True)
        if not len(a) or not len(b):
            continue
        reasons = set(a.index) | set(b.index)
        swing, which = 0.0, ""
        for r in reasons:
            delta = abs(float(b.get(r, 0.0)) - float(a.get(r, 0.0)))
            if delta > swing:
                swing, which = delta, r
        if swing >= STEP_AT:
            out.append((ex, which, float(a.get(which, 0.0)),
                        float(b.get(which, 0.0)), swing, cut.date()))
    return sorted(out, key=lambda r: -r[4])


def duplicates(d: pd.DataFrame) -> list[tuple]:
    """Exits whose (pnl, exit_date) agree on >= DUP_AT of shared trades."""
    keys = ["ticker", "entry_date"]
    if not set(keys).issubset(d.columns):
        return []
    piv = {}
    for ex, g in d.groupby("exit_method"):
        s = g.set_index(keys)[["pnl_pct"]].rename(columns={"pnl_pct": ex})
        piv[ex] = s[~s.index.duplicated()]
    exits = sorted(piv)
    out = []
    for i, a in enumerate(exits):
        for b in exits[i + 1:]:
            j = piv[a].join(piv[b], how="inner")
            if len(j) < 30:
                continue
            same = float(np.isclose(j[a], j[b], atol=1e-9, equal_nan=True).mean())
            if same >= DUP_AT:
                out.append((a, b, same, len(j)))
    return sorted(out, key=lambda r: -r[2])


def report(path: pathlib.Path) -> int:
    d = _load(path)
    n_ex = d.exit_method.nunique()
    print(f"\n{'='*74}\n{path}\n{'='*74}")
    print(f"trades {len(d)} | strategies {d.strategy.nunique() if 'strategy' in d else '?'}"
          f" | exits {n_ex} | {d['_dt'].min().date()} -> {d['_dt'].max().date()}")

    deg = degenerate(d)
    print(f"\n1. DEGENERATE (one reason >= {DEGENERATE_AT:.0%}) - the exit never varies")
    if not deg:
        print("   none")
    for ex, r, share, n in deg:
        print(f"   {ex:<26} {r:<26} {share:6.1%}  n={n}")

    step = temporal_step(d)
    print(f"\n2. TEMPORAL STEP (reason share swings >= {STEP_AT:.0%} across halves)")
    print("   an exit whose identity changes mid-sample invalidates IS/OOS across it")
    if not step:
        print("   none")
    for ex, r, a, b, sw, cut in step:
        print(f"   {ex:<26} {r:<22} {a:6.1%} -> {b:6.1%}  swing {sw:5.1%}  @{cut}")

    dup = duplicates(d)
    print(f"\n3. DUPLICATE (identical outcomes on >= {DUP_AT:.0%} of shared trades)")
    if not dup:
        print("   none")
    for a, b, same, n in dup:
        print(f"   {a:<26} == {b:<26} {same:6.1%}  n={n}")
    eff = n_ex - len(dup)
    print(f"\n   exits_effective ~ {eff} of {n_ex} "
          f"(\"best of {n_ex}\" is really best of ~{eff})")

    flagged = {e for e, *_ in deg} | {e for e, *_ in step}
    print(f"\nSUMMARY: {len(flagged)} of {n_ex} exits flagged -> {sorted(flagged)}")
    return 1 if flagged else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args()
    rc = 0
    for p in a.paths:
        rc |= report(pathlib.Path(p))
    print("\nNOTHING WAS CHANGED. Fixing an exit is a rule change and needs owner "
          "approval - see S6-B1771b / S6-B1771c.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
