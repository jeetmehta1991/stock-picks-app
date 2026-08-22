"""scripts/measure_exit_selection_noise.py (B1467, ticket S6-B1466a) -- how much of a cell's
graded Sharpe is EDGE, and how much is exit-selection luck?

THE NATURAL EXPERIMENT
The roster pipeline chooses each cell's exit by argmax over ~26 candidates on the in-sample folds,
then grades that single choice on the holdout. Whether that selection step is informative or noisy
has never been measured -- there was no control.

B1463's redundancy audit accidentally created one. Near-duplicate strategies fire on the SAME
entries (some at jaccard 1.000) yet had their exits selected INDEPENDENTLY, because the pipeline
treats them as unrelated cells. Each duplicate pair is therefore a replicate of the selection step
with the trade population held fixed:

    same entries + independent selection -> ANY holdout difference is selection variance

The first pair read by hand (B1466) diverged by 0.365 Sharpe -- against a 0.50 gate -- with the
in-sample winner losing 2.6x out of sample. This measures all of them.

WHY IT MUST RUN NOW
Regenerating the cube with the B1465 duplicate disables removes these cells and destroys the
replicates (S6-B1466b). The control exists only until then.

WHAT IS REPORTED
  agreement rate      how often the two twins picked the SAME exit (selection stability)
  |dSharpe|           holdout Sharpe gap when they picked DIFFERENTLY = selection noise
  IS-winner accuracy  did the twin with the higher IS Sharpe also win out of sample?
                      50% = the selection carries no information
  verdict flips       pairs where one twin cleared all five live gates and the twin did not,
                      on the same trades -- the concrete cost of the noise

LIMITATIONS, stated up front
  * Jaccard < 1.0 means entries are near-identical, not identical; some of the gap is real
    difference in trades. Reported by jaccard tier so the reader can see the trend.
  * Small n (7 pairs at >=0.95). Widened to >=0.70 for a second tier, where the entry difference
    is larger and the estimate is correspondingly more contaminated -- an upper bound.
  * A pair is not independent of the roster it informs; this measures the pipeline's stability,
    not an out-of-sample forecast.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.config import PASSING_CRITERIA as PC  # noqa: E402

# B2009 (D3): the gap is contextualized against the LIVE pooled gate the
# roster cells must clear (min_sharpe_overall, B1493-armed) - the old line
# printed the per-regime 0.5, understating how large the noise is relative
# to the bar actually in force.
GATE = PC["min_sharpe_overall"]


def main() -> int:
    red = json.loads((REPO / "output_audit" / "b1463_registration_redundancy.json")
                     .read_text(encoding="utf-8"))
    roster = json.loads((REPO / "output_audit" / "b1453_phase_1b_roster.json")
                        .read_text(encoding="utf-8"))
    cells = {f"{r['strategy']}|{r['direction']}": r for r in roster["all_rows"]}

    print("=" * 104)
    print("EXIT-SELECTION NOISE (B1467 / S6-B1466a) -- duplicate pairs as natural replicates")
    print("=" * 104)
    print(f"  live Sharpe gate = {GATE}. Any |dSharpe| approaching it is noise the size of the bar.\n")

    tiers = [("NEAR-IDENTICAL  jaccard >= 0.95", 0.95, 1.01),
             ("REDUNDANT       0.70 <= j < 0.95", 0.70, 0.95)]
    out = {}
    for label, lo, hi in tiers:
        rows = []
        for p in red["pairs"]:
            if not (lo <= p["jaccard"] < hi):
                continue
            a, b = cells.get(p["a"]), cells.get(p["b"])
            if not a or not b:
                continue
            ha, hb = a.get("holdout"), b.get("holdout")
            if not ha or not hb or ha.get("sharpe") is None or hb.get("sharpe") is None:
                continue
            same_exit = a["exit"] == b["exit"]
            d = abs(ha["sharpe"] - hb["sharpe"])
            # which twin looked better IN SAMPLE, and did it win OUT of sample?
            is_a, is_b = a.get("is_sharpe"), b.get("is_sharpe")
            is_winner_won = None
            if is_a is not None and is_b is not None and is_a != is_b:
                is_winner_won = ((is_a > is_b) == (ha["sharpe"] > hb["sharpe"]))
            flip = ha["all_live_gates"] != hb["all_live_gates"]
            rows.append({"a": p["a"], "b": p["b"], "jaccard": p["jaccard"],
                         "same_exit": same_exit, "exit_a": a["exit"], "exit_b": b["exit"],
                         "ho_a": ha["sharpe"], "ho_b": hb["sharpe"], "d_sharpe": d,
                         "is_a": is_a, "is_b": is_b, "is_winner_won": is_winner_won,
                         "verdict_flip": flip})
        if not rows:
            print(f"--- {label}: no measurable pairs\n")
            continue

        diff = [r for r in rows if not r["same_exit"]]
        flips = [r for r in rows if r["verdict_flip"]]
        judged = [r for r in rows if r["is_winner_won"] is not None]
        won = [r for r in judged if r["is_winner_won"]]

        print(f"--- {label}   ({len(rows)} measurable pairs)")
        print(f"    picked the SAME exit          {len(rows)-len(diff)} of {len(rows)}"
              f"   ({100*(len(rows)-len(diff))/len(rows):.0f}% selection agreement)")
        if diff:
            ds = [r["d_sharpe"] for r in diff]
            print(f"    |dSharpe| when they differ    median {statistics.median(ds):.3f}"
                  f"  mean {statistics.mean(ds):.3f}  max {max(ds):.3f}")
            print(f"                                  -> {100*statistics.median(ds)/GATE:.0f}%"
                  f" of the {GATE} gate, at the median")
        if judged:
            print(f"    IS winner also won OOS        {len(won)} of {len(judged)}"
                  f"   ({100*len(won)/len(judged):.0f}%; 50% = selection carries no information)")
        print(f"    VERDICT FLIPS on same trades  {len(flips)} of {len(rows)}")
        for r in flips:
            wa = "PASS" if cells[r["a"]]["holdout"]["all_live_gates"] else "fail"
            wb = "PASS" if cells[r["b"]]["holdout"]["all_live_gates"] else "fail"
            print(f"      j={r['jaccard']:.4f}  {r['a']:<42}{wa}  ({r['exit_a']}, {r['ho_a']:.3f})")
            print(f"                 {r['b']:<42}{wb}  ({r['exit_b']}, {r['ho_b']:.3f})")
        print()
        out[label] = rows

    p = REPO / "output_audit" / "b1467_exit_selection_noise.json"
    p.write_text(json.dumps({"gate": GATE, "tiers": out}, indent=2, default=str), encoding="utf-8")
    print(f"[OK] wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
