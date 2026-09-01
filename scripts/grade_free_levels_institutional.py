"""S6-B2504 (implements S6-B2501): grade the P7/P8 FREE levels off the R5 cube.

ZERO ENGINE HOURS. Both counts the levels threshold on are persisted in
signals_at_entry, so raising the primary bar (P7: 5/11/14) or the fallback bar
(P8: 6) selects a STRICT SUBSET of trades already in the cube (SPECS
derivation, producer_variant_table.py P7/P8) and re-scores offline.

FAITHFUL TO THE ENGINE, measured not assumed:
  * the gate (screener.py:6646-6648) reads BOTH counts via s.get(key, 0), and
    3.8 pct of this strategy's 1,941 fired rows carry NO committed key (the
    B1230 no-artifact-row fallback) - so absent keys default to 0 HERE TOO,
    or the re-score grades a different gate than the engine ran.
  * keep_row mirrors the OR exactly: raising P7 never removes fallback-arm
    trades; raising P8 never removes primary-arm trades.

METHOD SCOPE, disclosed: these are subset re-scores of the R5 merged cube
(544 tickers x 4 years), comparable to the BASELINE re-derived on the same
cube in the same pass - NOT to b2197-style Step-1 configs (200 x 1y shape).
IS-window only via roster_core.in_sample(); the holdout is never read.

MULTIPLICITY EXPOSURE (S6-B2444's recording rule): 4 levels are searched in
this pass and the artifact records that denominator.

Usage:
  python scripts/grade_free_levels_institutional.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
OUT = ROOT / "output_audit" / "b2504_free_levels_institutional.json"
STRAT = "institutional_committed_growth_long"

# production thresholds (screener.py:6648) and the FREE levels (SPECS P7/P8)
P7_PROD, P8_PROD = 3, 5
LEVELS = [("baseline_p7_3", 3, 5), ("p7_5", 5, 5), ("p7_11", 11, 5),
          ("p7_14", 14, 5), ("p8_6", 3, 6)]


def keep_row(committed: float, increased: float, p7: int, p8: int) -> bool:
    """The strategy's OR gate at (p7, p8) - mirrors screener.py:6646-6648.

    Raising p7 leaves the fallback arm untouched (committed==0 rows still
    pass via increased); raising p8 leaves the primary arm untouched. A row
    with 0 < committed < P7_PROD never fired and never reaches this filter.
    """
    return (committed >= p7) or (committed == 0 and increased >= p8)


def trade_flags() -> pd.DataFrame:
    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["ticker", "strategy", "entry_date", "direction",
                              "signals_at_entry"])
    tl = tl[tl["strategy"] == STRAT].copy()
    assert len(tl) == 1941, (
        f"baseline fires {len(tl)} != 1941 - the artifact moved under the "
        "SPECS baseline; re-derive before grading (L639)")

    def parse(s):
        d = json.loads(s)
        # ENGINE SEMANTICS: absent key reads 0 (s.get default) - the B1230
        # fallback rows carry no committed key at all, measured 3.8 pct.
        return (float(d.get("committed_growth_holders", 0) or 0),
                float(d.get("institutional_increased", 0) or 0))

    flags = tl["signals_at_entry"].map(parse)
    tl["committed"] = [a for a, _ in flags]
    tl["increased"] = [b for _, b in flags]
    tl["entry_date"] = pd.to_datetime(tl["entry_date"]).dt.date
    return tl[["ticker", "entry_date", "direction", "committed", "increased"]]


def main() -> int:
    flags = trade_flags()
    cube = rc.load_cube(CUBE, chunksize=500_000)  # engine is running: bound RSS
    cube = cube[cube["strategy"] == STRAT].copy()
    merged = cube.merge(flags, on=["ticker", "entry_date", "direction"],
                        how="left", validate="many_to_one")
    unmatched = merged["committed"].isna().sum()
    assert unmatched == 0, (
        f"{unmatched} cube rows failed the trade-log join - the (ticker, "
        "entry_date, direction) key is not the trade identity here")

    doc = {"ticket": "S6-B2504", "strategy": STRAT,
           "method": ("subset re-score of output_r5_merged_1_7 per SPECS "
                      "P7/P8 free_band; IS window only (roster_core.in_sample); "
                      "holdout never read; absent signal keys default to 0 "
                      "exactly as the engine's s.get did"),
           "multiplicity_exposure": {"levels_searched_this_pass": 4,
                                     "note": "S6-B2444 recording rule"},
           "levels": {}}

    for name, p7, p8 in LEVELS:
        keep = merged[[keep_row(c, i, p7, p8) for c, i in
                       zip(merged["committed"], merged["increased"])]]
        is_rows = rc.in_sample(keep)
        fires_is = is_rows[["ticker", "entry_date"]].drop_duplicates().shape[0]
        per_exit = []
        for ex, g in is_rows.groupby("exit_method", observed=True):
            stats = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=1)
            if stats is None:
                continue
            per_exit.append({"exit": str(ex), "n": int(len(g)),
                             "is_sharpe": stats.get("sharpe"),
                             "is_ci_lo": stats.get("ci_lo"),
                             "below_step1_floor": bool(len(g) < 10)})
        per_exit.sort(key=lambda r: (-(r["is_ci_lo"]
                                       if r["is_ci_lo"] is not None else -9e9),
                                     -r["n"]))
        pick, pick_stats = rc.select_exit(keep, objective="sharpe", min_n=10)
        doc["levels"][name] = {
            "p7": p7, "p8": p8, "is_fires": int(fires_is),
            "is_rows_all_exits": int(len(is_rows)),
            "sharpe_selected_exit": pick,
            "sharpe_selected_stats": ({k: pick_stats.get(k) for k in
                                       ("sharpe", "ci_lo")} if pick_stats
                                      else None),
            "per_exit_ranked_by_ci_lo": per_exit,
        }
        base = doc["levels"].get("baseline_p7_3")
        top = per_exit[0] if per_exit else None
        print(f"{name:>14}: IS fires {fires_is:>5}"
              + (f" ({fires_is - base['is_fires']:+d} vs baseline)"
                 if base and name != "baseline_p7_3" else "")
              + (f" | top ci_lo {top['is_ci_lo']:+.3f} n={top['n']} {top['exit']}"
                 if top and top["is_ci_lo"] is not None else " | no gradable exit"))

    OUT.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
