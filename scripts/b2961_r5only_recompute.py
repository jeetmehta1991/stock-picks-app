#!/usr/bin/env python
"""S6-B2961: does TODAY's producer still fire on the fires only R5 has?

THE SURVIVING EVIDENCE, after S6-B2960's occupancy reading was retracted.
Churn between the baseline and a fresh run goes BOTH ways:

    soldiers   79 in both, 481 run-only, 58 R5-only
    crows      94 in both, 437 run-only, 63 R5-only

If the story were "R5 under-recorded", R5 would be a SUBSET of the run and
the R5-only bucket would be empty. It is not. A non-empty R5-only bucket is
the signature of a CHANGED CONDITION - the two runs evaluated different
predicates, or different bars - and it is the one bucket that discriminates
without needing R5's unattributable occupancy rows.

THE TEST. Take the (ticker, date) pairs only R5 has. Recompute the candle
anatomy at those exact bars with TODAY's producer, at PRODUCTION parameters.

    fires today  -> the producer still agrees; R5's fire was real and the
                    run lost it DOWNSTREAM (occupancy, PIT, liquidity,
                    blackout) - an accounting difference
    does NOT     -> the CONDITION moved between R5 and now. The date and
                    the commit are then findable, and every R5-derived
                    figure for this strategy is scoped to the old condition

ONE DEFINITION OF THE ANATOMY: leg A of spot_check_candle is imported, never
reimplemented (L593), the same source candle_grid_feasibility.py uses.

    python scripts/b2961_r5only_recompute.py --strategy three_white_soldiers
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

BULLISH = "three_white_soldiers"
PROD = {"n_bars": 3, "body": 0.0, "step": 0.0, "wick": None}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strategy", default=BULLISH)
    ap.add_argument("--diff", default=None,
                    help="the b2960 date-diff artifact; default by strategy")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    from spot_check_candle import _leg_a
    from spot_check_trades import load_ohlcv

    diff_p = Path(a.diff) if a.diff else (
        ROOT / "output_audit" / f"b2960_{a.strategy}_date_diff.json")
    diff = json.loads(diff_p.read_text(encoding="utf-8"))
    pairs = [tuple(x) for x in diff["sample_r5_only"]]
    if not pairs:
        print("no R5-only sample in the artifact - nothing to test")
        return 2

    bullish = a.strategy == BULLISH
    cache: dict = {}
    rows = []
    for tk, d in pairs:
        if tk not in cache:
            try:
                cache[tk] = load_ohlcv(tk)
            except Exception:                              # noqa: BLE001
                cache[tk] = None
        o = cache[tk]
        if o is None:
            rows.append({"ticker": tk, "date": d, "verdict": "NO_BARS"})
            continue
        hit = o.index.searchsorted(pd.Timestamp(d))
        if hit >= len(o) or o.index[hit].date().isoformat() != d:
            rows.append({"ticker": tk, "date": d, "verdict": "DATE_ABSENT"})
            continue
        fired = _leg_a(o, int(hit), bullish, PROD["n_bars"], PROD["body"],
                       PROD["step"], PROD["wick"])
        rows.append({"ticker": tk, "date": d,
                     "verdict": "FIRES_TODAY" if fired is True
                                else "DOES_NOT_FIRE_TODAY"})

    tally: dict[str, int] = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1

    doc = {
        "ticket": "S6-B2961 (evidence for S6-B2949 / S6-B2950)",
        "strategy": a.strategy,
        "question": "does today's producer fire at the bars only R5 landed?",
        "production_params": PROD,
        "sample_size": len(rows),
        "sample_is_a_sample": ("the b2960 artifact stores the FIRST 15 "
                               "R5-only pairs, so this is a SAMPLE of the 58 "
                               "/ 63 population, not the population - the "
                               "verdict below is scoped to it"),
        "tally": tally,
        "reading": (
            "FIRES_TODAY dominant -> the condition is unchanged and the run "
            "lost these DOWNSTREAM; an accounting difference. "
            "DOES_NOT_FIRE_TODAY dominant -> the CONDITION MOVED since R5 "
            "and every R5-derived figure for this strategy is scoped to the "
            "old condition."),
        "rows": rows,
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"b2961_{a.strategy}_r5only_recompute.json")
    out.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")

    print(f"=== {a.strategy}: today's producer at R5-only bars ===")
    print(f"  sample {len(rows)} of the R5-only population (a SAMPLE)")
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {k:24s} {v}")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
