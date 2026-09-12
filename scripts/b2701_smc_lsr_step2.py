#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2701 (S6-B2701; owner word verbatim 2026-09-12: "proceed, engulfing +
momentum q40 both pre-registered"): hub-1 STEP-2 - ONE holdout read.

FAIL-CLOSED on the ruling and on the COMMITTED pre-registration artifact
(output_audit/b2701_prereg.json, commit 301cded1a - F4: committed BEFORE
this file existed). The holdout six-gate line (roster_core.evaluate,
tier=pooled) is computed for EVERY Step-1 cell x exit in this one read;
ONLY the two pre-registered cells are ADMISSION-BEARING - every other line
is PEEKED-BY-CONSTRUCTION / DIAGNOSTIC and can never pick a different
winner, because the pre-registration is spent the moment this runs (the
icg challenge-bound pattern, runbook F5).

PROVENANCE on the artifact's face: DISCLOSED-RE-READ (the strategy's
holdout window was read historically by the R5 roster grading passes).
Cell B is judged on the COVERED subpopulation only (WIDENED-COVERAGE-0.942;
the 5.8% gap is excluded from the cell in BOTH windows - the same
population its IS selection was made on).

CONTROL-FAMILY COMPARISON (11.2b2 promoted rule, B2658): each pre-registered
cell's axis/level/exit applied to the control strategy's recorded fires;
control-shared lift = general structure, reported beside the subject.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
from breadth_step1_grid import _parse  # noqa: E402
from smc_lsr_step1 import build, STRAT, B_AXES, ARM_KEYS  # noqa: E402

PREREG = ROOT / "output_audit" / "b2701_prereg.json"
CONTROL = "pead_long_high_yoy_growth_only"
CONTROL_KEYS = ["bullish_engulfing", "monthly_momentum_6m"]


def grade_holdout(sub: pd.DataFrame) -> dict | None:
    ho = rc.holdout(sub)
    return rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=15,
                       full_period_n=len(sub))


def subset_for_row(m: pd.DataFrame, r: dict) -> pd.DataFrame | None:
    """Reconstruct a Step-1 row's subset from its RECORDED fields, mirroring
    smc_lsr_step1.grade_cells / b2698 exactly (subset-safe filters only)."""
    tag = r.get("cell", "")
    if tag.startswith("depth:"):
        leg, arm = tag.split(":", 1)[1].split("/")
        base = m if leg == "both" else m[m.direction == leg]
        if arm == "either":
            sub = base
        else:
            want = 0 if arm == "choch_only" else 1
            parts = []
            for lg, keys in ARM_KEYS.items():
                part = base[(base.direction == lg) & (base[keys[want]] == 1.0)]
                parts.append(part)
            sub = pd.concat(parts) if parts else base.iloc[0:0]
    elif r.get("axis"):
        key = r["axis"]
        op = dict(B_AXES).get(key)
        lev = r["level"]
        if op == "eq_true_long" or lev == "True(long)":
            sub = m[(m.direction == "long") & (m[key] == 1.0)]
        elif op == "eq_false" or lev == "False":
            sub = m[m[key] == 0.0]
        elif op == "ge":
            sub = m[m[key].notna() & (m[key] >= float(lev))]
        else:
            sub = m[m[key].notna() & (m[key] <= float(lev))]
    else:
        return None
    return sub[sub.exit_method == r["exit"]]


def load_control(keys: list) -> pd.DataFrame:
    tl = pd.read_csv(ROOT / "output_r5_merged_1_7" / "trade_log.csv",
                     low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    fam = tl[tl.strategy == CONTROL].drop_duplicates(["ticker", "entry_date"]).copy()
    sigs = [_parse(s) for s in fam["signals_at_entry"]]
    for k in keys:
        fam[k] = pd.to_numeric(
            pd.Series([float(d.get(k)) if isinstance(d.get(k), bool)
                       else d.get(k) for d in sigs]), errors="coerce").values
    fam = fam.drop(columns=["signals_at_entry"])
    cube = pd.read_csv(ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv",
                       low_memory=False,
                       usecols=["strategy", "ticker", "entry_date",
                                "exit_method", "pnl_pct", "hold_days"])
    cube = cube[cube.strategy == CONTROL]
    mm = cube.merge(fam, on=["strategy", "ticker", "entry_date"], how="left")
    mm["entry_date"] = pd.to_datetime(mm["entry_date"], errors="coerce").dt.date
    return mm


def control_lift(cm: pd.DataFrame, key: str, mask, exit_name: str) -> dict:
    base = cm[cm.exit_method == exit_name]
    filt = base[mask(base)]
    def _ho_sharpe(g):
        ho = rc.holdout(g)
        r = rc._sharpe(ho["pnl_pct"].values, ho["hold_days"], min_n=10)
        return (r["sharpe"] if r else None, int(len(ho)))
    b_sh, b_n = _ho_sharpe(base)
    f_sh, f_n = _ho_sharpe(filt)
    return {"control": CONTROL, "axis": key, "exit": exit_name,
            "holdout_sharpe_unfiltered": b_sh, "n_unfiltered": b_n,
            "holdout_sharpe_filtered": f_sh, "n_filtered": f_n,
            "lift": (round(f_sh - b_sh, 3)
                     if (f_sh is not None and b_sh is not None) else None),
            "label": "DISCLOSED-RE-READ (control's holdout read in its own campaign)"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruling", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not a.ruling.strip():
        raise SystemExit("REFUSED: empty --ruling")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg["ruling_verbatim"] not in a.ruling:
        raise SystemExit("REFUSED: --ruling does not carry the committed "
                         "pre-registration's verbatim word")
    t0 = time.time()

    m = build()
    fires = m.drop_duplicates(["ticker", "entry_date"])
    pre = json.loads((ROOT / "output_audit" / "b2690_smc_pregate.json").read_text(encoding="utf-8"))
    if len(fires) != pre["members"][STRAT]["n_trades"]:
        raise SystemExit("REFUSED: fire-count reproduction failed")
    print(f"reproduction OK: {len(fires)} fires ({time.time()-t0:.0f}s)")

    # the Step-1 grid rows, from the COMMITTED artifacts (never re-derived)
    step1_rows = []
    for name in ("b2694_smc_lsr_step1.json", "b2698_momentum_resweep.json"):
        art = json.loads((ROOT / "output_audit" / name).read_text(encoding="utf-8"))
        step1_rows += [r for r in art["rows"] if r.get("is_sharpe") is not None]

    # the two pre-registered subsets, built from the PREREG artifact's predicates
    reg_a = m[(m.direction == "long") & (m.bullish_engulfing == 1.0)
              & (m.exit_method == "class_time_stop")]
    reg_b = m[m.monthly_momentum_6m.notna() & (m.monthly_momentum_6m >= -0.1122)
              & (m.exit_method == "breakeven_plus_trail")]
    admission = {}
    for cid, sub in (("A", reg_a), ("B", reg_b)):
        g = grade_holdout(sub)
        admission[cid] = {"prereg": prereg["admission_bearing_cells"][0 if cid == "A" else 1],
                          "holdout": g, "full_n": int(len(sub)),
                          "status": "ADMISSION-BEARING"}
        print(f"cell {cid}: all_live_gates={g and g.get('all_live_gates')} "
              f"ho_sharpe={g and g.get('sharpe')} ho_n={g and g.get('n')}")

    # every other Step-1 line: holdout computed, PEEKED label
    peeked = []
    for r in step1_rows:
        sub = subset_for_row(m, r)
        if sub is None:
            continue
        g = grade_holdout(sub)
        peeked.append({"cell": r["cell"], "axis": r.get("axis"),
                       "level": r.get("level"), "exit": r["exit"],
                       "is_sharpe": r["is_sharpe"],
                       "holdout": g, "full_n": int(len(sub)),
                       "label": "PEEKED-BY-CONSTRUCTION / DIAGNOSTIC",
                       "npt_barred": r.get("npt_barred", False)})
    print(f"{len(peeked)} peeked lines graded ({time.time()-t0:.0f}s)")

    # control comparison for the two pre-registered cells (11.2b2)
    cm = load_control(CONTROL_KEYS)
    controls = [
        control_lift(cm, "bullish_engulfing",
                     lambda g: g["bullish_engulfing"] == 1.0, "class_time_stop"),
        control_lift(cm, "monthly_momentum_6m",
                     lambda g: g["monthly_momentum_6m"].notna()
                     & (g["monthly_momentum_6m"] >= -0.1122), "breakeven_plus_trail"),
    ]
    print(f"control rows done ({time.time()-t0:.0f}s)")

    rec = {"strategy": STRAT,
           "ruling_verbatim": a.ruling,
           "prereg_artifact": "output_audit/b2701_prereg.json (commit 301cded1a, "
                              "committed before this reader existed - F4)",
           "provenance": ["DISCLOSED-RE-READ - the strategy's holdout window was read "
                          "historically by the R5 roster grading passes",
                          "cell B judged on the COVERED subpopulation only "
                          "(WIDENED-COVERAGE-0.942; 5.8% gap excluded in both windows)"],
           "gates": "six LIVE_GATES, roster_core.evaluate tier=pooled, "
                    "min_trades_holdout>=15, min_trades_full_period>75 (strict)",
           "admission_bearing": admission,
           "control_comparison": controls,
           "peeked_lines": peeked,
           "spent": "the pre-registration is spent - no other cell can ever carry "
                    "admission from this campaign's Step-1 grid"}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out} ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
