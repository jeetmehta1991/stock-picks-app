#!/usr/bin/env python
"""S6-B1248-OR-ARM-ATTRIBUTION: which arm of an OR gate actually fires?

THE QUESTION. B1202 (Council 278, owner-approved 2026-07-06) loosened two
SHORT strategies by adding `smc_bos_bearish` as an OR-ALTERNATIVE, to raise
fire counts after the B1186 SPY probe found the library treating price action
as break-of-structure rather than as a sweep:

  strat_smc_equal_highs_sweep_short (screener.py:4584)
      (smc_equal_highs_swept OR smc_bos_bearish) AND smc_fvg_bearish_active
  strat_turtle_soup_short (screener.py:4812)
      (smc_liquidity_swept_up OR smc_bos_bearish) AND below_prev_high
      AND close_below_open

If the ADDED arm dominates, each strategy is a break-of-structure strategy
wearing a stop-hunt thesis's name - the thesis-dilution question the ticket
was opened to answer.

WHY THIS RUNS NOW. The ticket sat BLOCKED reading "the analysis slices the
BATCH B trade log, and Batch B launch is owner-gated". But the question is
about the STRATEGIES, not about Batch B: any cube carrying them with a
persisted `signals_at_entry` answers it. MEASURED: 25 cubes do, the largest
holding 2,718 rows of the pair. The blocker was a property of the plan, not
of the question (the S6-B2533 class - a stated cause that does not hold).

WHAT IT CANNOT SAY. This attributes LANDED trades, so it measures the arms
among fires that became trades, not among all signal fires - occupancy and
the candidate cap sit in between (L812). It is an attribution of the traded
population and says so in the artifact.

    python scripts/or_arm_attribution.py --cube output_r5_merged_1_7
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# strategy -> (thesis arm, arm added at B1202)
GATES = {
    "smc_equal_highs_sweep_short": ("smc_equal_highs_swept", "smc_bos_bearish"),
    "turtle_soup_short": ("smc_liquidity_swept_up", "smc_bos_bearish"),
    # S6-B3037 (owner ruled RE-DERIVE 2026-09-23): the B2931 split
    # gave the B1202 arm its own registration. Each carries its
    # PARENT's signal pair so the same classifier runs on both.
    "smc_equal_highs_bos_short": ("smc_equal_highs_swept", "smc_bos_bearish"),
    "turtle_soup_bos_short": ("smc_liquidity_swept_up", "smc_bos_bearish"),
}

# S6-B3037: the PAIR is the unit of analysis after the split - the
# question 'how much of this name rests on the added arm' is answered
# by the two populations, not by one name's internal split.
SPLIT_PAIRS = {
    "turtle_soup_short": "turtle_soup_bos_short",
    "smc_equal_highs_sweep_short": "smc_equal_highs_bos_short",
}


def _signals(raw):
    """L824: a probe reporting absence must prove it can see presence. The
    column appears in BOTH python-repr and JSON dialects across cube
    generations; literal_eval alone fails on every JSON-style row, which is
    indistinguishable from the field being absent."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        d = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        try:
            d = json.loads(raw)
        except ValueError:
            return None
    return d if isinstance(d, dict) else None


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cube", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    cube = Path(a.cube)
    tl = cube / "trade_log.csv"
    if not tl.exists():
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no trade_log.csv at {tl}"}))
        return 2

    df = pd.read_csv(tl)
    out_rows = []
    for strat, (thesis, added) in GATES.items():
        sub = df[df["strategy"] == strat] if "strategy" in df.columns else df
        if sub.empty:
            out_rows.append({"strategy": strat, "verdict": "NO_ROWS",
                             "landed": 0,
                             "regime": "NO_READABLE_ROWS",
                             "regime_note": (
                                 "no rows for this registration in this "
                                 "cube - expected on a PRE-split cube for "
                                 "the two B2931 registrations"),
                             "split_pair": SPLIT_PAIRS.get(strat)})
            continue
        both = thesis_only = added_only = neither = unparsed = 0
        for raw in sub.get("signals_at_entry", pd.Series([None] * len(sub))):
            d = _signals(raw)
            if d is None or thesis not in d or added not in d:
                unparsed += 1
                continue
            t, x = bool(d.get(thesis)), bool(d.get(added))
            if t and x:
                both += 1
            elif t:
                thesis_only += 1
            elif x:
                added_only += 1
            else:
                neither += 1
        readable = both + thesis_only + added_only + neither
        # S6-B3037: a share that CANNOT be wrong is not evidence.
        # After the split each registration's classification is fixed
        # by its own gate - the parent cannot fire without the thesis
        # signal, the bos arm cannot fire with it - so the share is
        # STRUCTURAL, not measured. Say which regime produced it.
        if not readable:
            regime = "NO_READABLE_ROWS"
        elif added_only == 0 and (both + thesis_only) == readable:
            regime = "POST_SPLIT_STRUCTURAL_THESIS_SIDE"
        elif added_only == readable:
            regime = "POST_SPLIT_STRUCTURAL_BOS_SIDE"
        else:
            regime = "PRE_SPLIT_INFORMATIVE"
        # the dilution figure: of the trades the gate ADMITTED, how many rest
        # on the ADDED arm alone - those are trades the pre-B1202 thesis
        # would never have taken
        share = (added_only / readable) if readable else None
        out_rows.append({
            "strategy": strat,
            "thesis_arm": thesis,
            "added_arm_b1202": added,
            "landed": int(len(sub)),
            "readable": readable,
            "unparsed_or_missing_keys": unparsed,
            "both_arms": both,
            "thesis_arm_only": thesis_only,
            "added_arm_only": added_only,
            "neither_arm": neither,
            "added_arm_only_share": None if share is None else round(share, 4),
            "regime": regime,
            "regime_note": (
                "share is structural, fixed by this registration's own "
                "gate, not measured from the data"
                if regime.startswith("POST_SPLIT") else
                "share is measured: both arms could have fired"),
            "split_pair": SPLIT_PAIRS.get(strat),
        })

    doc = {
        "ticket": "S6-B1248-OR-ARM-ATTRIBUTION",
        "question": ("B1202 added smc_bos_bearish as an OR-alternative on two "
                     "SHORT strategies. Does the added arm dominate the "
                     "landed population - i.e. is the thesis diluted?"),
        "cube": str(cube).replace("\\", "/"),
        "rows": out_rows,
        "scope": ("LANDED TRADES, not signal fires. Occupancy and the "
                  "candidate cap sit between a fire and a trade (L812), so "
                  "this attributes the traded population only."),
        "neither_arm_note": ("A `neither` row means the gate fired on a "
                             "signal dict where both arms read False - which "
                             "should be impossible and, if non-zero, is a "
                             "finding about persistence, not about the "
                             "thesis."),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.name}_or_arm_attribution.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")

    print(f"OR-arm attribution on {cube.name}")
    for r in out_rows:
        if r.get("verdict") == "NO_ROWS":
            print(f"  {r['strategy']:<32} no rows")
            continue
        print(f"  {r['strategy']}")
        print(f"    landed {r['landed']}, readable {r['readable']}, "
              f"unreadable/missing {r['unparsed_or_missing_keys']}")
        print(f"    both {r['both_arms']} | thesis-only {r['thesis_arm_only']}"
              f" | ADDED-ONLY {r['added_arm_only']} | neither "
              f"{r['neither_arm']}")
        print(f"    added-arm-only share: {r['added_arm_only_share']}")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
