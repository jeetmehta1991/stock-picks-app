"""scripts/audit_registration_redundancy.py (B1463, ticket S6-B1455a) -- find duplicate
strategies across the WHOLE roster, independent of performance.

THE STRUCTURAL DEFECT THIS FIXES
Redundancy detection lived INSIDE the promotion pipeline: `build_phase_1b_roster.py` applies
Jaccard >= 0.70 only to cells that already cleared the holdout gates. A gate placed downstream
of a performance filter can only ever see survivors, so **duplicate FAILING strategies are
invisible by construction**. That is how `macd_crossover`'s short leg and `macd_crossover_short`
sat at **jaccard 1.000 over 1,524 trades** -- literally the same trades under two registrations --
without anything flagging it, and how `macd_ichimoku` sat at 0.999 with an ichimoku gate that is
a no-op on the short side.

The same class produced B874's deletion of `camarilla_rsi_obv` (a dual's short branch duplicating
a separately-registered standalone short). Two instances, one cause: nothing compares strategies
to each other except after they win.

WHAT THIS DOES INSTEAD
Compares EVERY (strategy x direction) cell present in the cube against every other, on the
(ticker, entry_date) trade set, with no reference to returns, gates or verdicts. A duplicate is a
duplicate whether it makes money or not -- and a duplicate that loses money is worse, because it
doubles the drag while looking like two independent failures in every count.

Thresholds:
  >= 0.95  NEAR-IDENTICAL -- two registrations of one signal. Should be deleted or merged.
  >= 0.70  REDUNDANT      -- the roster's de-dup bar; keep one, and know which.

Run standalone for the report; `test_b1463_no_new_near_identical_pairs` pins the result so a NEW
duplicate registration fails the pyramid instead of surviving to a cube run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from roster_core import load_cube  # noqa: E402

NEAR_IDENTICAL, REDUNDANT = 0.95, 0.70
MIN_TRADES = 50          # below this a jaccard is noise, not evidence


def compute_pairs(cube: str = "output_r5_merged_1_7",
                  min_jaccard: float = REDUNDANT) -> list[dict]:
    """Every (strategy x direction) pair at or above `min_jaccard`. Performance-blind."""
    # S6-B1548a: chunked so test_b1463 can run beside an engine run (L425).
    # MEASURED unchunked: 5,036 MB peak for a 266 MB frame.
    df = load_cube(REPO / cube / "trade_exit_detail.csv", chunksize=500_000)
    # one exit per cell keeps the comparison about the SIGNAL, not the exit: entries are
    # identical across exits by construction (the cube replays exits over the same entries).
    first_exit = df.groupby(["strategy", "direction"], observed=True)["exit_method"].first()
    sets: dict[tuple[str, str], set] = {}
    for (s, d), g in df.groupby(["strategy", "direction"], observed=True):
        ex = first_exit.loc[(s, d)]
        gg = g[g.exit_method == ex]
        if len(gg) < MIN_TRADES:
            continue
        sets[(str(s), str(d))] = set(map(tuple, gg[["ticker", "entry_date"]]
                                         .drop_duplicates().values))
    keys = sorted(sets)
    out = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = sets[keys[i]], sets[keys[j]]
            if keys[i][1] != keys[j][1]:      # compare like directions only
                continue
            inter = len(a & b)
            if not inter:
                continue
            jac = inter / len(a | b)
            if jac >= min_jaccard:
                out.append({"a": f"{keys[i][0]}|{keys[i][1]}",
                            "b": f"{keys[j][0]}|{keys[j][1]}",
                            "jaccard": round(jac, 4),
                            "n_a": len(a), "n_b": len(b), "shared": inter})
    out.sort(key=lambda r: -r["jaccard"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", default="output_r5_merged_1_7")
    ap.add_argument("--output", default="output_audit/b1463_registration_redundancy.json")
    args = ap.parse_args()

    print("=" * 100)
    print("REGISTRATION-TIME REDUNDANCY AUDIT (B1463 / S6-B1455a) -- performance-blind")
    print("=" * 100)
    pairs = compute_pairs(args.cube)
    near = [p for p in pairs if p["jaccard"] >= NEAR_IDENTICAL]
    red = [p for p in pairs if REDUNDANT <= p["jaccard"] < NEAR_IDENTICAL]

    print(f"  NEAR-IDENTICAL (jaccard >= {NEAR_IDENTICAL}): {len(near)}")
    for p in near:
        print(f"    {p['jaccard']:.4f}  {p['a']:<44} x  {p['b']}   "
              f"(n {p['n_a']}/{p['n_b']}, shared {p['shared']})")
    print(f"\n  REDUNDANT ({REDUNDANT} <= jaccard < {NEAR_IDENTICAL}): {len(red)}")
    for p in red[:25]:
        print(f"    {p['jaccard']:.4f}  {p['a']:<44} x  {p['b']}")
    if len(red) > 25:
        print(f"    ... +{len(red)-25} more")

    print(f"\n  These are found WITHOUT reference to returns or gates -- which is the point:")
    print(f"  the roster's de-dup only ever saw cells that had already passed.")

    out = REPO / args.output
    out.write_text(json.dumps({"cube": args.cube, "near_identical_bar": NEAR_IDENTICAL,
                               "redundant_bar": REDUNDANT, "min_trades": MIN_TRADES,
                               "n_near_identical": len(near), "n_redundant": len(red),
                               "pairs": pairs}, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
