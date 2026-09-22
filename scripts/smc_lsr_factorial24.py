#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} via
# smc_lsr_step1.build (CHECKLIST #77 - every figure derived at run time).
"""S6-B2990 (owner ruled 2026-09-22, both parts): the 24-combination
factorial over smc_liquidity_sweep_reversal's three PHASE0-only axes,
with the promotion bar ENFORCED IN CODE.

THE RULING. Part (i): the three env=None axes of the merged registry entry
(S6-B2910) - B1 monthly_momentum_6m at its 4 quantile levels, P4
confirmation_arm at 3, P5 leg at 2 - may be swept offline, 24 combinations
at zero engine hours, with the 24 trials priced into the multiplicity
block. Part (ii): the promotion bar is enforced IN CODE, not by a written
note - this script computes `promotable_for_future_prereg` itself and
REFUSES to run with a null too small to price the bar.

WHAT A CANDIDATE HERE CAN NEVER BE. output_audit/b2701_smc_lsr_step2.json
records, verbatim: "the pre-registration is spent - no other cell can ever
carry admission from this campaign's Step-1 grid." Every holdout row for
this strategy was read in that Step-2; the read is one-way (B2136). So the
best this factorial can produce is a CANDIDATE FOR A FUTURE
PRE-REGISTRATION, and the artifact says so on every row that clears the
bar. There is no admission field, deliberately.

OVERLAP WITH THE STEP-1 GRID, disclosed and CORRECTED (B2999): b2694
graded leg x arm as 9 depth cells - but its breadth pass SKIPPED
monthly_momentum_6m at IS coverage 0.942 against its 0.98 floor, so THIS
IS THE AXIS'S FIRST GRADING, not a re-read. The owner's S6-B2990 part (i)
ruling is why it runs at that coverage: the floor here is a 0.90 sanity
refusal, and the artifact carries the coverage, the per-cell NaN drops,
and the note that step1's own convention would have skipped the axis.

THE BAR, exactly: the observed grid maximum (best is_ci_lo over the 24
cells' best-exit rows) is priced against >= 200 permutations of the
momentum column across the base's IS fires (leg and arm stay real - their
9-cell sub-grid was priced and peeked in the Step-1/Step-2 pass; the
momentum cross is what is new and what the null must price). A cell is
promotable_for_future_prereg only when it IS the observed argmax, the
null's p is <= 0.05, and its is_ci_lo is positive. Anything else is
RANKED, full stop (B1608: Step-1 emits ranked lists, not gates).

    python scripts/smc_lsr_factorial24.py --null-perms 200 \
        --out output_audit/b2990_smc_lsr_factorial24.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "scripts" / "roster_core.py").exists():
    ROOT = Path.cwd()   # draft run from the scratchpad; repo is the cwd
assert (ROOT / "scripts" / "roster_core.py").exists(), ROOT
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
from smc_lsr_step1 import (ARM_KEYS, STRAT, SWEEP_KEYS, build,  # noqa: E402
                           current_gate_rows)

MOM = "monthly_momentum_6m"
QUANTS_B1 = (0.20, 0.40, 0.60, 0.80)   # the registry band [q20,q40,q60,q80]
BARRED_EXIT = "next_pivot_target"      # npt barred from ranking (B2014 D7)
SPENT_NOTE = ("HOLDOUT SPENT for this campaign (b2701_smc_lsr_step2.json): "
              "no cell here can carry admission; promotable rows are "
              "candidates for a FUTURE pre-registration only")


def arm_rows(base: pd.DataFrame, leg: str, arm: str) -> pd.DataFrame:
    """Rows of `base` in `leg` whose confirmation matches `arm` exactly."""
    sub = base[base.direction == leg]
    ck, bk = ARM_KEYS[leg]
    if arm == "either":
        return sub
    key = ck if arm == "choch_only" else bk
    return sub[sub[key] == 1.0]


def factorial_rows(base: pd.DataFrame, levels: dict[float, float],
                   min_n: int) -> list[dict]:
    """One RANKED row per (leg, arm, momentum-quantile) cell: the best
    non-npt exit by is_ci_lo, with its n and the cell's fire count."""
    rows = []
    for leg in ("long", "short"):                       # P5 band
        for arm in ("either", "choch_only", "bos_only"):  # P4 band
            cell0 = arm_rows(base, leg, arm)
            for q, lev in levels.items():               # B1 band
                cell = cell0[cell0[MOM].notna() & (cell0[MOM] >= lev)]
                best = None
                for ex, grp in cell.groupby("exit_method"):
                    if ex == BARRED_EXIT:
                        continue
                    si = rc.in_sample(grp)
                    r = rc._sharpe(si["pnl_pct"].values, si["hold_days"],
                                   min_n=min_n)
                    if r is None:
                        continue
                    if best is None or (r.get("ci_lo") or -9) > (
                            best["is_ci_lo"] or -9):
                        best = {"exit": ex, "is_sharpe": r["sharpe"],
                                "is_ci_lo": r.get("ci_lo"),
                                "is_n": int(len(si))}
                row = {"cell": f"{leg}/{arm}/q{int(q * 100)}",
                       "leg": leg, "arm": arm,
                       "momentum_quantile": f"q{int(q * 100)}",
                       "momentum_floor": float(lev),
                       "fires": int(cell.drop_duplicates(
                           ["ticker", "entry_date"]).shape[0]),
                       "verdict": "RANKED" if best else "BELOW_POWER_FLOOR"}
                row.update(best or {"exit": None, "is_sharpe": None,
                                    "is_ci_lo": None, "is_n": 0})
                rows.append(row)
    return rows


def factorial_null(base: pd.DataFrame, levels: dict, min_n: int,
                   n_perms: int, seed: int) -> list:
    """SYNTHETIC maxima: momentum shuffled across the base's fires, the
    full 24-cell grid re-graded, the best is_ci_lo kept per permutation."""
    rng = np.random.default_rng(seed)
    fires = base.drop_duplicates(["ticker", "entry_date"])[
        ["ticker", "entry_date", MOM]].reset_index(drop=True)
    stripped = base.drop(columns=[MOM])
    maxima = []
    for _ in range(n_perms):
        idx = rng.permutation(len(fires))
        shuf = fires[["ticker", "entry_date"]].join(
            fires.loc[idx, [MOM]].reset_index(drop=True))
        mm = stripped.merge(shuf, on=["ticker", "entry_date"], how="left")
        best = None
        for r in factorial_rows(mm, levels, min_n):
            v = r.get("is_ci_lo")
            if v is not None and (best is None or v > best):
                best = v
        maxima.append(best)
    return maxima


def decide_promotable(rows: list[dict], p_max: float,
                      alpha: float = 0.05) -> list[str]:
    """THE BAR, IN CODE (owner ruling part ii): the observed argmax cell,
    and only it, and only when the 24-trial-priced null clears alpha and
    the cell's own is_ci_lo is positive."""
    graded = [r for r in rows if r.get("is_ci_lo") is not None]
    if not graded or p_max is None or p_max > alpha:
        return []
    top = max(graded, key=lambda r: r["is_ci_lo"])
    if (top["is_ci_lo"] or 0) <= 0:
        return []
    return [top["cell"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--null-perms", type=int, default=200)
    ap.add_argument("--null-seed", type=int, default=13)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.null_perms < 200:
        raise SystemExit(
            "REFUSED: --null-perms %d < 200 - the promotion bar is priced "
            "by this null (S6-B2990 part ii, enforced in code); an unpriced "
            "ranking is exactly the written note the owner rejected"
            % a.null_perms)

    t0 = time.time()
    m = build()
    fires = m.drop_duplicates(["ticker", "entry_date"])
    pre = json.loads((ROOT / "output_audit" / "b2690_smc_pregate.json")
                     .read_text(encoding="utf-8"))
    want = pre["members"][STRAT]["n_trades"]
    if len(fires) != want:
        raise SystemExit(f"REFUSED: {len(fires)} unique fires != pre-gate "
                         f"{want} (R5 reproduction gate)")
    base = current_gate_rows(m)

    # Levels are derived ONCE, from the FULL frame's IS fires - the same
    # population and 0.98 coverage convention smc_lsr_step1's breadth leg
    # used (its momentum axis passed that floor at B2694), so the quantile
    # levels are comparable across the two artifacts. The gated base's own
    # momentum coverage is DISCLOSED rather than gated: cells drop NaN
    # momentum rows by construction.
    vals = rc.in_sample(m).drop_duplicates(["ticker", "entry_date"])[MOM]
    cov = float(vals.notna().mean())
    # Owner ruling S6-B2990(i) orders this sweep; step1's 0.98 convention
    # would SKIP the axis (it did, at this same 0.942 - the b2694 SKIP row),
    # and a convention whose outcome was "do not measure" cannot override an
    # explicit instruction to measure. 0.90 stays as the sanity refusal
    # below which quantile levels stop meaning anything.
    if cov < 0.90:
        raise SystemExit(f"REFUSED: {MOM} coverage {cov:.3f} < 0.90 on the "
                         "full frame's IS fires - quantile levels would be "
                         "meaningless")
    base_vals = rc.in_sample(base).drop_duplicates(
        ["ticker", "entry_date"])[MOM]
    base_cov = float(base_vals.notna().mean())
    levels = {q: float(np.round(vals.quantile(q), 4)) for q in QUANTS_B1}

    rows = factorial_rows(base, levels, a.min_n)
    assert len(rows) == 24, f"factorial emitted {len(rows)} cells, not 24"

    maxima = [x for x in factorial_null(base, levels, a.min_n,
                                        a.null_perms, a.null_seed)
              if x is not None]
    graded = [r for r in rows if r.get("is_ci_lo") is not None]
    obs = max((r["is_ci_lo"] for r in graded), default=None)
    p_max = (None if obs is None or not maxima
             else float(np.mean([x >= obs for x in maxima])))
    promotable = decide_promotable(rows, p_max)

    doc = {
        "ticket": "S6-B2990 (owner ruled 2026-09-22, parts i and ii)",
        "strategy": STRAT,
        "axes": {"P5_leg": ["long", "short"],
                 "P4_confirmation_arm": ["either", "choch_only", "bos_only"],
                 "B1_monthly_momentum_6m": {f"q{int(q*100)}": lv
                                            for q, lv in levels.items()}},
        "trials_priced": 24,
        "grain": {"window": "R5 in-sample leg only (holdout untouched here; "
                            "already SPENT by b2701)",
                  "base": f"current-gate rows, {len(base.drop_duplicates(['ticker','entry_date']))} unique fires "
                          f"of {len(fires)} recorded",
                  "momentum_coverage": {"full_frame_is": round(cov, 4),
                                        "gated_base_is": round(base_cov, 4),
                                        "step1_convention": "would SKIP at "
                                                            "< 0.98 - and did "
                                                            "(b2694 SKIP row at "
                                                            "0.942), so this is "
                                                            "the axis's FIRST "
                                                            "grading",
                                        "runs_by": "owner ruling 2026-09-22, "
                                                   "S6-B2990 part (i)",
                                        "note": "levels from the full frame's "
                                                "IS fires; cells drop NaN "
                                                "momentum rows"}},
        "spent_note": SPENT_NOTE,
        "overlap_note": ("leg x arm at no momentum floor re-reads the "
                         "b2694 step1 depth cells by the same builder; the "
                         "momentum cross inside each cell is the new "
                         "measurement"),
        "multiplicity": {"method": "permutation null, momentum shuffled "
                                   "across base fires, full 24-cell grid "
                                   "re-graded per perm (SYNTHETIC maxima)",
                         "n_perms": a.null_perms, "seed": a.null_seed,
                         "observed_max_is_ci_lo": obs,
                         "p_max": p_max},
        "promotable_for_future_prereg": promotable,
        "results": rows,
        "elapsed_s": round(time.time() - t0, 1),
    }
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")

    print(f"=== S6-B2990 factorial24: {STRAT} ===")
    print(f"  base fires {doc['grain']['base']}")
    for r in sorted(graded, key=lambda r: -(r["is_ci_lo"] or -9))[:5]:
        print(f"  {r['cell']:24s} is_ci_lo {r['is_ci_lo']:+.3f} "
              f"is_n {r['is_n']:4d} exit {r['exit']}")
    print(f"  graded {len(graded)} of 24 cells; observed max {obs}; "
          f"p_max {p_max} over {a.null_perms} perms")
    print(f"  promotable_for_future_prereg: {promotable or 'NONE'}")
    print(f"  {SPENT_NOTE}")
    print(f"  -> {out} ({doc['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
