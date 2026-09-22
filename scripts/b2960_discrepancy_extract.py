#!/usr/bin/env python
"""S6-B2960: extract the date-level evidence behind the S6-B2949 discrepancy.

WHY DATES AND NOT COUNTS. Counts never explain themselves. This run landed
560 three_white_soldiers trades where output_r5_merged_1_7 holds 137 in the
identical window and the identical 200-ticker file, and two independent
strategies show the same 3-4x. A per-(ticker, date) diff separates the
hypotheses that a count cannot:

  - dates the RUN has and R5 does not, where R5 carries a SKIPPED row on the
    same (ticker, date)  -> OCCUPANCY or another engine-side block
  - dates the RUN has and R5 has NEITHER landed NOR skipped               -> the fire did not
    exist in R5 at all: a moved GATE, or a universe/PIT difference
  - dates R5 has and the RUN does not                                     -> the reverse drift
  - tickers R5 never ran in this window                                   -> COVERAGE

The third bucket is the one that decides between a code change and an
accounting change, and nothing measured so far can see it.

DELIBERATELY NO CAUSE IS NAMED HERE. This writes an artifact; the reading is
a separate step, because a probe that also concludes is where the L644 class
lives.

    python scripts/b2960_discrepancy_extract.py --strategy three_white_soldiers
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R5 = ROOT / "output_r5_merged_1_7"


def _load(path: Path, cols: list[str]) -> pd.DataFrame:
    have = pd.read_csv(path, nrows=0).columns.tolist()
    use = [c for c in cols if c in have]
    df = pd.read_csv(path, usecols=use, low_memory=False)
    for c in cols:
        if c not in df.columns:
            df[c] = None
    return df


def _dates(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="the landed cube directory")
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--start", default="2024-05-05")
    ap.add_argument("--end", default="2025-05-05")
    ap.add_argument("--tickers", default="output_audit/_sweep_200.txt")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    run_dir = ROOT / a.run
    tickers = {t.strip() for t in (ROOT / a.tickers).read_text().split()
               if t.strip() and not t.startswith("#")}

    # ---- the RUN's landed and blocked sets
    run_l = _dates(_load(run_dir / "trade_log.csv",
                         ["ticker", "entry_date", "strategy"]), "entry_date")
    run_l = run_l[run_l["strategy"] == a.strategy]
    run_s = _dates(_load(run_dir / "skipped_trades.csv",
                         ["ticker", "date", "strategy", "reason"]), "date")
    run_s = run_s[run_s["strategy"] == a.strategy]

    # ---- R5's landed and blocked sets, restricted to the same scope
    r5_l = _dates(_load(R5 / "trade_log.csv",
                        ["ticker", "entry_date", "strategy"]), "entry_date")
    r5_l = r5_l[r5_l["strategy"] == a.strategy]
    r5_l_scope = r5_l[(r5_l["entry_date"] >= a.start)
                      & (r5_l["entry_date"] <= a.end)
                      & (r5_l["ticker"].isin(tickers))]

    r5_s_path = R5 / "skipped_trades.csv"
    r5_s_scope = pd.DataFrame(columns=["ticker", "date", "strategy", "reason"])
    r5_s_any_window = 0
    if r5_s_path.exists():
        r5_s = _dates(_load(r5_s_path,
                            ["ticker", "date", "strategy", "reason"]), "date")
        r5_s_strat = r5_s[r5_s["strategy"] == a.strategy]
        r5_s_scope = r5_s_strat[(r5_s_strat["date"] >= a.start)
                                & (r5_s_strat["date"] <= a.end)
                                & (r5_s_strat["ticker"].isin(tickers))]
        r5_s_any_window = int(((r5_s["date"] >= a.start)
                               & (r5_s["date"] <= a.end)).sum())

    def keyset(df, col):
        return {(str(t), d.date().isoformat())
                for t, d in zip(df["ticker"], df[col]) if pd.notna(d)}

    run_keys = keyset(run_l, "entry_date")
    r5_keys = keyset(r5_l_scope, "entry_date")
    r5_skip_keys = keyset(r5_s_scope, "date")

    run_only = run_keys - r5_keys
    r5_only = r5_keys - run_keys
    both = run_keys & r5_keys

    # the load-bearing split: of the run-only fires, which does R5 BLOCK and
    # which does R5 not know about at all?
    # S6-B2962 (L837): REFUSE A BUCKET THIS FILTER CANNOT POPULATE.
    # All 391,782 occupancy rows in output_r5_merged_1_7 carry the
    # literal '(same-strategy)' in the strategy column (pre-B2905;
    # S6-B2904 records it as UNQUANTIFIABLE), so filtering them by
    # strategy NAME can only ever return zero - and a zero that is
    # decidable by construction reads exactly like a measurement.
    _occ = r5_s_scope
    _attributable = True
    if r5_s_path.exists():
        _all_occ = _dates(_load(r5_s_path,
                                ["ticker", "date", "strategy",
                                 "reason"]), "date")
        _occ_rows = _all_occ[_all_occ["reason"].astype(str).str.contains(
            "ticker_already_open", na=False)]
        if len(_occ_rows) and _occ_rows["strategy"].nunique() <= 1:
            _attributable = False
    run_only_r5_blocked = run_only & r5_skip_keys
    run_only_r5_absent = run_only - r5_skip_keys

    # COVERAGE: which of the 200 did R5 run AT ALL in this window, on ANY
    # strategy? A ticker R5 never touched cannot have held this fire.
    r5_any = _dates(_load(R5 / "trade_log.csv", ["ticker", "entry_date"]),
                    "entry_date")
    r5_win_tickers = set(
        r5_any[(r5_any["entry_date"] >= a.start)
               & (r5_any["entry_date"] <= a.end)]["ticker"].astype(str))
    run_tickers = {str(t) for t in run_l["ticker"]}
    absent_from_r5_window = sorted(
        {t for t, _ in run_only_r5_absent} - r5_win_tickers)

    doc = {
        "ticket": "S6-B2960 (evidence for S6-B2949 / S6-B2950)",
        "strategy": a.strategy,
        "run": a.run,
        "baseline": "output_r5_merged_1_7",
        "window": {"start": a.start, "end": a.end},
        "ticker_file": a.tickers,
        "tickers_in_file": len(tickers),
        "counts": {
            "run_landed": len(run_keys),
            "r5_landed_in_scope": len(r5_keys),
            "run_skipped_rows": int(len(run_s)),
            "r5_skipped_rows_in_scope": int(len(r5_s_scope)),
            "r5_skipped_rows_any_strategy_in_window": r5_s_any_window,
        },
        "date_level_diff": {
            "in_both": len(both),
            "run_only": len(run_only),
            "r5_only": len(r5_only),
            "run_only_that_R5_BLOCKED": (
                len(run_only_r5_blocked) if _attributable else
                "REFUSED - the baseline's occupancy rows carry ONE "
                "literal strategy value, so a strategy-name filter "
                "cannot populate this bucket and a zero here would be "
                "decidable by construction (S6-B2904 / L837)"),
            "run_only_that_R5_NEVER_SAW": (
                len(run_only_r5_absent) if _attributable else
                "REFUSED - same reason; absence from an unattributable "
                "record is not evidence of absence"),
            "baseline_occupancy_attributable": _attributable,
        },
        "coverage": {
            "r5_distinct_tickets_in_window_any_strategy":
                len(r5_win_tickers),
            "run_distinct_tickers": len(run_tickers),
            "run_only_fires_on_tickers_R5_NEVER_RAN_in_window":
                len(absent_from_r5_window),
            "examples": absent_from_r5_window[:15],
        },
        "r5_block_reasons_in_scope":
            (r5_s_scope["reason"].value_counts().head(8).to_dict()
             if len(r5_s_scope) else {}),
        "run_block_reasons":
            run_s["reason"].value_counts().head(8).to_dict() if len(run_s)
            else {},
        "sample_run_only_never_seen": sorted(run_only_r5_absent)[:25],
        "sample_r5_only": sorted(r5_only)[:15],
        "interpretation": "DELIBERATELY ABSENT - this artifact is evidence, "
                          "not a verdict. See S6-B2949 for the hypotheses.",
    }

    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"b2960_{a.strategy}_date_diff.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")

    print(f"=== {a.strategy}: {a.run} vs R5, {a.start}..{a.end} ===")
    for k, v in doc["counts"].items():
        print(f"  {k:48s} {v}")
    print("  --- date-level")
    for k, v in doc["date_level_diff"].items():
        print(f"  {k:48s} {v}")
    print("  --- coverage")
    for k, v in doc["coverage"].items():
        if k != "examples":
            print(f"  {k:48s} {v}")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
