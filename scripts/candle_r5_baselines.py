#!/usr/bin/env python
# Source: output_r5_merged_1_7/trade_log.csv (the R5 baseline cube) and the
# per-(ticker,date) diff artifacts output_audit/b2960_*_date_diff.json; per
# CHECKLIST #77 every figure here is derived from those at run time and none
# is stored in this file.
"""S6-B2973 / L839: the candle R5 baselines, BOTH GRAINS, each stamped.

WHY THIS EXISTS. The hourly chain monitor's prompt told me to check landed
trades against "the R5 baselines: 1,596 for three_white_soldiers, 1,674 for
three_black_crows_short". Those are FULL-WINDOW figures - 4 years across
544 tickers. Every Step-1 candle config runs 1 year across 200 tickers, so
setting a landed count against them compares populations differing by about
4x in window and 2.7x in universe. On that comparison a run landing 4.09x
the matched baseline reads as landing 0.35x of it.

The figure was not wrong. Its GRAIN was unstated, and a count carries no
unit to betray the omission (L836, L664).

THE PART A REPO SWEEP CANNOT REACH. Sweeping the tree for those two numbers
returns exactly ONE hit, in the skill's own tripwire row, where the figure
is used correctly as an example. The live wrong-grain instance lives in a
CRON PROMPT - a scheduled artifact outside the working tree - so no grep
over the repo could ever have found it, and the schedule re-asserts it every
hour.

SO THE MECHANISM IS AN ARTIFACT TO QUOTE FROM, not a detector. Any
instrument that needs a candle baseline takes it from here, where each
figure is stamped with the window and universe it was counted over and
neither grain can be quoted bare.

    python scripts/candle_r5_baselines.py
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R5 = ROOT / "output_r5_merged_1_7"
OUT = ROOT / "output_audit" / "candle_r5_baselines.json"

LEGS = {
    "three_white_soldiers": "b2960_three_white_soldiers_date_diff.json",
    "three_black_crows_short": "b2960_three_black_crows_short_date_diff.json",
}


def _full_window(strategy: str) -> dict:
    """R5's landed count over its OWN full window and universe."""
    df = pd.read_csv(R5 / "trade_log.csv",
                     usecols=["ticker", "entry_date", "strategy"],
                     low_memory=False)
    df = df[df["strategy"] == strategy]
    dates = pd.to_datetime(df["entry_date"], errors="coerce")
    return {
        "count": int(len(df)),
        "window_start": str(dates.min().date()) if len(df) else None,
        "window_end": str(dates.max().date()) if len(df) else None,
        "universe_distinct_tickers": int(df["ticker"].nunique()),
        "grain": "R5 FULL WINDOW - not comparable to a Step-1 cube",
    }


def _matched(strategy: str, fname: str) -> dict:
    """R5's landed count restricted to the Step-1 window and universe."""
    p = ROOT / "output_audit" / fname
    if not p.exists():
        return {"count": None,
                "note": "diff artifact absent - run b2960_discrepancy_extract"}
    d = json.loads(io.open(p, encoding="utf-8").read())
    return {
        "count": d["counts"]["r5_landed_in_scope"],
        "window_start": d["window"]["start"],
        "window_end": d["window"]["end"],
        "universe_distinct_tickers": d["tickers_in_file"],
        "grain": "MATCHED to a Step-1 cube - this is the comparable figure",
        "source": fname,
    }


def build() -> dict:
    out = {
        "ticket": "S6-B2973 (L839)",
        "why": ("a baseline quoted without its window and universe is a "
                "count with no denominator; both grains are stamped here so "
                "neither can be quoted bare"),
        "legs": {},
    }
    for strategy, fname in LEGS.items():
        out["legs"][strategy] = {
            "full_window": _full_window(strategy),
            "matched_to_step1": _matched(strategy, fname),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()

    doc = build()
    p = Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(doc, indent=1))

    print("=== candle R5 baselines, both grains ===")
    for strategy, legs in doc["legs"].items():
        f, m = legs["full_window"], legs["matched_to_step1"]
        print(f"  {strategy}")
        print(f"    full window   {f['count']} over "
              f"{f['window_start']}..{f['window_end']}, "
              f"{f['universe_distinct_tickers']} tickers")
        print(f"    matched       {m['count']} over "
              f"{m['window_start']}..{m['window_end']}, "
              f"{m['universe_distinct_tickers']} tickers")
    print(f"  -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
