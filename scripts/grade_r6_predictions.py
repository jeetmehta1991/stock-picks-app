"""scripts/grade_r6_predictions.py (B1428) -- grade the 25 pre-registered R6 predictions.

WHAT MAKES THIS A TEST AND NOT A SEARCH
The change list (b1410) and the exit reassignments (b1415) were both written BEFORE
R6 ran, each carrying its expected effect inline.  This script only reads those
predictions and scores them.  It fits nothing.

COMPARISON BASIS (the thing that would otherwise be wrong)
R5 ran 614 tickers; R6 ran a 150-ticker seeded sample.  Comparing raw fire COUNTS
would conflate the change with the universe shrink.  Two defences:
  1 restrict R5 to the SAME 150 tickers -> the fires ratio becomes a measurement,
    not a scaling assumption;
  2 report fires as a RATIO (r6/r5) rather than as counts, per the owner's
    standing units directive.

IS vs HOLDOUT
The predictions were fitted on IS only (2022-05-05 -> 2025-05-05); the holdout
(2025-05-05 -> 2026-05-05) was never read.  R6 re-ran the SAME window, so:
  - IS agreement is near-tautological for the tightening changes (they were fitted
    there).  It is reported for completeness but carries little evidential weight.
  - HOLDOUT agreement is the actual test.
Any strategy whose holdout n falls below --min-holdout-n is graded INSUFFICIENT_DATA
rather than PASS/FAIL - the engine's own walk-forward already flagged INSUFF=10 of 23.

Conventions match the ones the predictions were built under (build_exit_reassignment.py):
winsorize +/-300%, 20bps round-trip cost.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent

# B1977: direct execution puts scripts/ on sys.path automatically; an import
# from another cwd does not. Same two-line setup as the sibling scripts.
import sys                                                   # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))

from roster_core import rank_key                             # noqa: E402
IS_START, IS_END = date(2022, 5, 5), date(2025, 5, 5)
OOS_END = date(2026, 5, 5)
WINSORIZE, COST_BPS = 300.0, 20.0

USE = ["ticker", "strategy", "entry_date", "exit_method", "pnl_pct"]


def load(path: Path, tickers: set[str], strats: set[str]) -> pd.DataFrame:
    frames = []
    for ch in pd.read_csv(path, usecols=USE, chunksize=500_000, low_memory=False):
        ch = ch[ch.strategy.isin(strats) & ch.ticker.isin(tickers)]
        if len(ch):
            frames.append(ch)
    d = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=USE)
    d["entry_date"] = pd.to_datetime(d["entry_date"]).dt.date
    d["pnl_pct"] = d["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
    return d


def slice_window(d: pd.DataFrame, lo: date, hi: date) -> pd.DataFrame:
    return d[(d.entry_date >= lo) & (d.entry_date < hi)]


def stats(d: pd.DataFrame, exit_method: str | None) -> dict:
    """fires = distinct (ticker, entry_date) signals -- ROWS, not cells."""
    if exit_method is not None:
        d = d[d.exit_method == exit_method]
    if not len(d):
        return {"fires": 0, "exp": None, "wr": None}
    return {
        "fires": int(d.groupby(["ticker", "entry_date"]).ngroups),
        "exp": round(float(d.pnl_pct.mean()), 4),
        "wr": round(float((d.pnl_pct > 0).mean()), 4),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--r5", default="output_r5_merged_1_7/trade_exit_detail.csv")
    ap.add_argument("--r6", default="output_r6_local_150/trade_exit_detail.csv")
    ap.add_argument("--tickers", default="output_audit/_r6_ticker_sample.txt")
    ap.add_argument("--min-holdout-n", type=int, default=30,
                    help="below this many holdout fires -> INSUFFICIENT_DATA, not PASS/FAIL")
    ap.add_argument("--output", default="output_audit/b1428_r6_prediction_grades.json")
    args = ap.parse_args()

    changes = json.loads((REPO / "output_audit/b1410_r6_change_list.json").read_text(encoding="utf-8"))
    exits = json.loads((REPO / "output_audit/b1415_exit_reassignment.json").read_text(encoding="utf-8"))
    applied = json.loads((REPO / "output_audit/b1425_r6_changed_strategies.json").read_text(encoding="utf-8"))

    tickers = set(t.strip() for t in
                  (REPO / args.tickers).read_text(encoding="utf-8").replace("\n", ",").split(",")
                  if t.strip())
    strats = set(applied["changed"])
    print(f"[INFO] {len(tickers)} tickers, {len(strats)} strategies")

    print("[INFO] loading R5 (restricted to the same tickers) ...")
    r5 = load(REPO / args.r5, tickers, strats)
    print("[INFO] loading R6 ...")
    r6 = load(REPO / args.r6, tickers, strats)
    print(f"[INFO] r5 rows={len(r5)} r6 rows={len(r6)}")

    # exit assigned in R6: for reassigned strategies the proposed exit, else R5 modal exit
    reassigned = {p["strategy"]: p for p in exits["proposals"]}
    entry_changes = {c["strategy"]: c for c in changes["changes"]}

    grades = []
    for s in sorted(strats):
        kinds = []
        if s in applied["entry_or_loosen"]:
            kinds.append("ENTRY")
        if s in applied["exit_reassigned"]:
            kinds.append("EXIT")

        prop = reassigned.get(s)
        exit_m = prop["proposed_exit"] if prop else None
        if exit_m is None:
            r5s = r5[r5.strategy == s]
            exit_m = r5s.exit_method.mode().iloc[0] if len(r5s) else None

        row = {"strategy": s, "change_kinds": kinds, "evaluated_at_exit": exit_m}
        if prop:
            row["exit_change"] = {"from": prop["current_exit"], "to": prop["proposed_exit"],
                                  "predicted_margin": prop["margin"],
                                  "predicted_exp": prop["exp_proposed"],
                                  "predicted_wr": prop["wr_proposed"]}
        if s in entry_changes:
            c = entry_changes[s]
            row["entry_change"] = {"treatment": c["treatment"], "segment": c["segment"],
                                   "change": c["change"],
                                   "prediction": c["prediction_for_r6"],
                                   "expected": c.get("expected", {})}

        for label, lo, hi in [("is", IS_START, IS_END), ("holdout", IS_END, OOS_END)]:
            a = stats(slice_window(r5[r5.strategy == s], lo, hi), exit_m)
            b = stats(slice_window(r6[r6.strategy == s], lo, hi), exit_m)
            row[label] = {
                "r5": a, "r6": b,
                "fires_ratio": (round(b["fires"] / a["fires"], 3) if a["fires"] else None),
                "d_exp": (round(b["exp"] - a["exp"], 4)
                          if a["exp"] is not None and b["exp"] is not None else None),
                "d_wr": (round(b["wr"] - a["wr"], 4)
                         if a["wr"] is not None and b["wr"] is not None else None),
            }

        h = row["holdout"]
        if h["r6"]["fires"] < args.min_holdout_n:
            row["verdict"] = "INSUFFICIENT_DATA"
            row["verdict_why"] = f"holdout fires={h['r6']['fires']} < {args.min_holdout_n}"
        else:
            de, dw = h["d_exp"], h["d_wr"]
            if de is None:
                row["verdict"] = "INSUFFICIENT_DATA"
                row["verdict_why"] = "no comparable R5 holdout rows at this exit"
            else:
                row["verdict"] = "CONFIRMED" if de > 0 else "REFUTED"
                row["verdict_why"] = f"holdout d_exp={de:+.3f}pp d_wr={dw:+.3f}"
        grades.append(row)

    n_conf = sum(1 for g in grades if g["verdict"] == "CONFIRMED")
    n_ref = sum(1 for g in grades if g["verdict"] == "REFUTED")
    n_ins = sum(1 for g in grades if g["verdict"] == "INSUFFICIENT_DATA")

    print(f"\n{'strategy':<42}{'kinds':<12}{'hold n':>7}{'fires x':>9}"
          f"{'d_exp':>9}{'d_wr':>8}  verdict")
    # B1977: `or -99` is the same falsy-coalescing class as the Sharpe
    # sentinel (S6-B1972b) on a different metric - a d_exp of EXACTLY 0.0
    # (no expectancy change, a legitimate grade) sorted below every
    # NEGATIVE delta. Display order only, fixed for one-definition parity.
    for g in sorted(grades, key=lambda x: (x["verdict"],
                                           -rank_key(x["holdout"]["d_exp"]))):
        h = g["holdout"]
        fr = f"{h['fires_ratio']:.2f}" if h["fires_ratio"] is not None else "  -"
        de = f"{h['d_exp']:+.2f}" if h["d_exp"] is not None else "   -"
        dw = f"{h['d_wr']:+.3f}" if h["d_wr"] is not None else "    -"
        print(f"  {g['strategy']:<40}{'+'.join(g['change_kinds']):<12}"
              f"{h['r6']['fires']:>7}{fr:>9}{de:>9}{dw:>8}  {g['verdict']}")
    print(f"\n[RESULT] CONFIRMED={n_conf}  REFUTED={n_ref}  INSUFFICIENT_DATA={n_ins}"
          f"  (of {len(grades)} strategies / {len(applied['entry_or_loosen'])} entry + "
          f"{len(applied['exit_reassigned'])} exit changes)")

    out = REPO / args.output
    out.write_text(json.dumps({
        "generated": "B1428",
        "basis": "R5 restricted to the same 150 tickers; fires reported as ratio, not counts",
        "conventions": {"winsorize": WINSORIZE, "cost_bps": COST_BPS,
                        "min_holdout_n": args.min_holdout_n},
        "windows": {"is": [str(IS_START), str(IS_END)],
                    "holdout": [str(IS_END), str(OOS_END)]},
        "summary": {"CONFIRMED": n_conf, "REFUTED": n_ref, "INSUFFICIENT_DATA": n_ins},
        "grades": grades}, indent=2), encoding="utf-8")
    print(f"[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
