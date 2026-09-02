"""S6-B2504 / B2569: grade the P7/P8 FREE levels off a landed cube.

ZERO ENGINE HOURS. Both counts the levels threshold on are persisted in
signals_at_entry, so raising the primary bar (P7) or the fallback bar (P8)
selects a STRICT SUBSET of trades already in the cube (SPECS derivation,
producer_variant_table.py P7/P8) and re-scores offline.

B2569 (owner directive 2026-09-02): parameterised per-config. The S6-B2504
run graded the R5 merged cube ONCE at strategy level; the ruled Step-1 design
counts the free levels as part of EVERY config's band, so this tool now takes
--cube and the battery (run_postconfig.run_institutional) invokes it on every
landing. Levels come from SPECS free_band - one source, no hand-typed copy.

REPRODUCTION GATE (owner, 2026-09-02: "If the re-scorer can't reproduce
baseline, nothing it reports about any level is believable"):
  before any level is graded, every covered trade-log row must RE-PASS the
  production gate (P7=3, P8=5). A covered row that fails means the logged
  signals disagree with the gate the engine ran - the tool exits 2 and grades
  nothing. Rows with EMPTY signals_at_entry (the S6-B2512 resume-restore
  class) are counted, excluded from the graded population, and reported as
  unverifiable - never silently failed and never silently kept.

FAITHFUL TO THE ENGINE, measured not assumed:
  * the gate (screener.py:6646-6648) reads BOTH counts via s.get(key, 0), so
    an absent KEY inside a present dict defaults to 0 HERE TOO (the B1230
    no-artifact-row fallback, 3.8 pct of R5 fired rows) - the engine read the
    same 0. An absent/empty DICT is different: the engine read live signals
    the log lost, so the row is unverifiable, not failing.
  * keep_row mirrors the OR exactly: raising P7 never removes fallback-arm
    trades; raising P8 never removes primary-arm trades.

L751 note: kept counts are COMPUTED from keep_row over parsed signals - this
tool is structurally unable to stamp a level it did not apply. Contrast
grade_institutional_config.py, whose P7/P8 flags are artifact stamps and now
REFUSE non-production values.

MULTIPLICITY EXPOSURE (S6-B2444 recording rule): the artifact records the
levels searched per pass AND that the graded object is a max over 24 exits,
nested inside one engine run per cube.

Usage:
  python scripts/grade_free_levels_institutional.py                 # legacy S6-B2504 R5 run
  python scripts/grade_free_levels_institutional.py --cube output_icg_span9_span9
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402
from producer_variant_table import SPECS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
OUT = ROOT / "output_audit" / "b2504_free_levels_institutional.json"
STRAT = "institutional_committed_growth_long"

# production thresholds (screener.py:6648) and the FREE levels (SPECS P7/P8)
P7_PROD, P8_PROD = 3, 5


def spec_levels() -> list[tuple[str, int, int]]:
    """Baseline + free levels, derived from SPECS - the pre-registered band.

    Asserts SPECS production values match this module's screener-pinned
    constants so a drift in either place is an alarm, not a silent regrade.
    """
    rows = {r["id"]: r for r in SPECS[STRAT]["params"]}
    p7, p8 = rows["P7"], rows["P8"]
    assert (p7["production"], p8["production"]) == (P7_PROD, P8_PROD), (
        f"SPECS production {(p7['production'], p8['production'])} != "
        f"screener-pinned {(P7_PROD, P8_PROD)} - re-verify screener.py:6648")
    levels = [(f"baseline_p7_{P7_PROD}", P7_PROD, P8_PROD)]
    levels += [(f"p7_{v}", int(v), P8_PROD)
               for v in p7["free_band"] if v != P7_PROD]
    levels += [(f"p8_{v}", P7_PROD, int(v))
               for v in p8["free_band"] if v != P8_PROD]
    return levels


def keep_row(committed: float, increased: float, p7: int, p8: int) -> bool:
    """The strategy's OR gate at (p7, p8) - mirrors screener.py:6646-6648.

    Raising p7 leaves the fallback arm untouched (committed==0 rows still
    pass via increased); raising p8 leaves the primary arm untouched. A row
    with 0 < committed < P7_PROD never fired and never reaches this filter.
    """
    return (committed >= p7) or (committed == 0 and increased >= p8)


def _parse_sig(s) -> tuple[float, float] | None:
    """(committed, increased) with s.get-default-0 semantics; None when the
    whole dict is empty/absent - the S6-B2512 unverifiable class."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return None
    t = str(s).strip()
    if t in ("", "{}", "nan", "None"):
        return None
    try:
        d = json.loads(t)
    except ValueError:
        return None
    if not d:
        return None
    return (float(d.get("committed_growth_holders", 0) or 0),
            float(d.get("institutional_increased", 0) or 0))


def load_trade_flags(trade_log: Path) -> pd.DataFrame:
    cols = ["ticker", "strategy", "entry_date", "direction", "signals_at_entry"]
    if trade_log.suffix == ".parquet":
        tl = pd.read_parquet(trade_log, columns=cols)
    else:
        tl = pd.read_csv(trade_log, low_memory=False, usecols=cols)
    tl = tl[tl["strategy"] == STRAT].copy()
    parsed = tl["signals_at_entry"].map(_parse_sig)
    tl["covered"] = parsed.map(lambda p: p is not None)
    tl["committed"] = parsed.map(lambda p: p[0] if p else 0.0)
    tl["increased"] = parsed.map(lambda p: p[1] if p else 0.0)
    tl["entry_date"] = pd.to_datetime(tl["entry_date"]).dt.date
    return tl[["ticker", "entry_date", "direction",
               "committed", "increased", "covered"]]


def reproduction_gate(flags: pd.DataFrame) -> dict:
    """Every COVERED landed trade must re-pass the production gate offline.

    Returns the reproduction record; raises SystemExit(2) on disagreement -
    a covered row failing production means the re-scorer and the engine
    disagree about a trade the engine took, and nothing graded downstream
    would be believable (owner ruling 2026-09-02).
    """
    n = len(flags)
    cov = flags[flags["covered"]]
    repassed = cov[[keep_row(c, i, P7_PROD, P8_PROD)
                    for c, i in zip(cov["committed"], cov["increased"])]]
    disagree = len(cov) - len(repassed)
    rec = {"landed_fires": int(n), "empty_signals": int(n - len(cov)),
           "covered": int(len(cov)), "repassed_at_production": int(len(repassed)),
           "production": {"p7": P7_PROD, "p8": P8_PROD},
           "empty_disposition": ("S6-B2512 class: excluded from the graded "
                                 "population, counted here, never silently "
                                 "failed" if n > len(cov) else "none"),
           "verdict": "PASS" if disagree == 0 else "FAIL"}
    print(f"REPRODUCTION: landed {n}, covered {len(cov)} "
          f"({n - len(cov)} empty signals_at_entry), re-passed at production "
          f"(P7={P7_PROD}, P8={P8_PROD}) {len(repassed)} -> {rec['verdict']}")
    if disagree:
        bad = cov[[not keep_row(c, i, P7_PROD, P8_PROD)
                   for c, i in zip(cov["committed"], cov["increased"])]]
        print(bad.head(10).to_string())
        raise SystemExit(2)
    return rec


def grade_levels(cube_csv: Path, flags: pd.DataFrame, *, min_n: int = 10,
                 ticket: str, method: str) -> dict:
    levels = spec_levels()
    cube = rc.load_cube(cube_csv, chunksize=500_000)  # bound RSS beside engine
    cube = cube[cube["strategy"] == STRAT].copy()
    merged = cube.merge(flags, on=["ticker", "entry_date", "direction"],
                        how="left", validate="many_to_one")
    unmatched = merged["committed"].isna().sum()
    assert unmatched == 0, (
        f"{unmatched} cube rows failed the trade-log join - the (ticker, "
        "entry_date, direction) key is not the trade identity here")
    merged = merged[merged["covered"]]  # S6-B2512 rows never graded

    doc = {"ticket": ticket, "strategy": STRAT, "cube": str(cube_csv),
           "method": method,
           "multiplicity_exposure": {
               "levels_searched_this_pass": len(levels) - 1,
               "note": ("S6-B2444 recording rule; each level's headline is a "
                        "max over the exits graded, and every level is a "
                        "nested subset of ONE engine run - levels are not "
                        "independent measurements")},
           "levels": {}}

    for name, p7, p8 in levels:
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
                             "verdict": ("RANKED" if len(g) >= min_n
                                         else "BELOW_POWER_FLOOR")})
        per_exit.sort(key=lambda r: (-(r["is_ci_lo"]
                                       if r["is_ci_lo"] is not None else -9e9),
                                     -r["n"]))
        pick, pick_stats = rc.select_exit(keep, objective="sharpe", min_n=min_n)
        doc["levels"][name] = {
            "p7": p7, "p8": p8, "is_fires": int(fires_is),
            "is_rows_all_exits": int(len(is_rows)),
            "sharpe_selected_exit": pick,
            "sharpe_selected_stats": ({k: pick_stats.get(k) for k in
                                       ("sharpe", "ci_lo")} if pick_stats
                                      else None),
            "per_exit_ranked_by_ci_lo": per_exit,
        }
        base = doc["levels"].get(levels[0][0])
        top = per_exit[0] if per_exit else None
        print(f"{name:>14}: IS fires {fires_is:>5}"
              + (f" ({fires_is - base['is_fires']:+d} vs baseline)"
                 if base and name != levels[0][0] else "")
              + (f" | top ci_lo {top['is_ci_lo']:+.3f} n={top['n']} {top['exit']}"
                 if top and top["is_ci_lo"] is not None else " | no gradable exit"))
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", default=None,
                    help="cube dir (reads trade_log.parquet/csv + "
                         "trade_exit_detail.csv); default = legacy S6-B2504 "
                         "R5 run")
    ap.add_argument("--out", default=None,
                    help="default output_audit/<cube dir>_free_levels.json "
                         "(never a *_grid_auto.json landing artifact, B2567)")
    ap.add_argument("--min-n", type=int, default=10)
    a = ap.parse_args()

    if a.cube:
        cube_dir = Path(a.cube)
        cube_csv = cube_dir / "trade_exit_detail.csv"
        tl = cube_dir / "trade_log.parquet"
        if not tl.exists():
            tl = cube_dir / "trade_log.csv"
        if not (cube_csv.exists() and tl.exists()):
            print(f"[FAIL] {cube_dir} lacks trade_exit_detail.csv or a trade log")
            return 2
        out = Path(a.out) if a.out else (
            ROOT / "output_audit" / f"{cube_dir.name}_free_levels.json")
        flags = load_trade_flags(tl)
        repro = reproduction_gate(flags)
        doc = grade_levels(
            cube_csv, flags, min_n=a.min_n, ticket="B2569",
            method=("per-config subset re-score per SPECS P7/P8 free_band; "
                    "reproduction gate at production PASSED before grading; "
                    "IS window only (roster_core.in_sample); holdout never "
                    "read; absent signal keys default to 0 exactly as the "
                    "engine's s.get did; empty signals_at_entry excluded and "
                    "counted (S6-B2512)"))
        doc["reproduction"] = repro
    else:
        flags = load_trade_flags(TRADE_LOG)
        assert len(flags) == 1941, (
            f"baseline fires {len(flags)} != 1941 - the artifact moved under "
            "the SPECS baseline; re-derive before grading (L639)")
        repro = reproduction_gate(flags)
        out = Path(a.out) if a.out else OUT
        doc = grade_levels(
            CUBE, flags, min_n=a.min_n, ticket="S6-B2504",
            method=("subset re-score of output_r5_merged_1_7 per SPECS "
                    "P7/P8 free_band; IS window only (roster_core.in_sample); "
                    "holdout never read; absent signal keys default to 0 "
                    "exactly as the engine's s.get did"))
        doc["reproduction"] = repro

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
