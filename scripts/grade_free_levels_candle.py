"""S6-B2904: grade the candle P6 FREE levels off a landed cube. Zero engine hours.

WHY IT EXISTS. B2569 (owner directive 2026-09-02) made free-level grading a
leg of EVERY landing: grading a band's free levels once at strategy level was
the N1 class bug (L752 / #290). Both candle entries carry a P6 free_band and
neither declared a `free_levels` leg, and MEASURED at B2904 a missing leg
produces NO row and NO FAIL - `_GRADER_CHECKS` is used only to exclude grader
failures from the cube_sanity roll-up - so 54 configs would have landed with
those levels silently ungraded.

THE AXIS. P6 is the rsi_14 bound, and it is OFFLINE: no env knob, and the
engine's gate reads a value persisted per trade.
  * three_white_soldiers  screener.py:2607  rsi_14 < 60   (a CEILING)
  * three_black_crows_short screener.py:2637 rsi_14 > 40  (a FLOOR)
Every free level TIGHTENS (the ceiling drops, the floor rises), so each level
selects a STRICT SUBSET of trades already in the cube. MEASURED at B2904 on
output_r5_merged_1_7/trade_log.csv: rsi_14 is present in signals_at_entry for
1596 of 1596 soldiers rows and 1674 of 1674 crows rows - coverage 1.0000 - so
the re-score is possible without touching the engine.

THE GATE IS MIRRORED EXACTLY, STRICT COMPARISONS INCLUDED. The producer uses
`<` and `>`, not `<=` and `>=`; using the wrong one silently moves every
boundary trade.

REPRODUCTION GATE (owner, 2026-09-02: "If the re-scorer can't reproduce
baseline, nothing it reports about any level is believable"). Before any level
is graded, every covered row must RE-PASS at the PRODUCTION bound. A covered
row that fails means the logged signal disagrees with the gate the engine ran;
this exits 2 and grades nothing. Rows whose signals_at_entry is empty or
unparseable are counted, EXCLUDED from the graded population and reported as
unverifiable - never silently failed and never silently kept.

THE OCCUPANCY DISCLOSURE, WHICH IS THE HONEST LIMIT OF THIS WHOLE METHOD.
A subset of SIGNALS is not a subset of TRADES (L812). Under cube_isolation the
engine drops a candidate when the same strategy already holds that ticker
(backtest.py:2497-2511), so REMOVING trades at a tighter level FREES occupancy
and would admit trades that exist in no cube. This tool cannot simulate that -
only the engine can - so it REPORTS the bound rather than pretending to it.
MEASURED on output_r5_merged_1_7: 391,782 of 444,226 skip rows are occupancy
blocks, outnumbering landed trades 2.07x, and every one is stamped
"(same-strategy)" because the writer discarded the name - so on a pre-B2905
cube the per-strategy correction is UNQUANTIFIABLE and the artifact says so.
B2905 fixed the stamp forward-only, so cubes written after it carry a real
count and this tool reports it.

Every number graded here is therefore a LOWER BOUND on the level's trade
count, and the verdicts are candidates, never admissions.

Usage (the battery passes exactly this):
  python scripts/grade_free_levels_candle.py --cube <dir> --out <grid.json>
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

BULLISH = "three_white_soldiers"
BEARISH = "three_black_crows_short"

# the live gate, read from the producer - direction included
GATE = {BULLISH: ("lt", 60.0), BEARISH: ("gt", 40.0)}
KEY = "rsi_14"


def keep_row(value, direction: str, bound: float) -> bool:
    """Mirror the producer's gate EXACTLY, strict comparison included."""
    return (value < bound) if direction == "lt" else (value > bound)


def parse_signals(raw):
    """(dict or None). None means unverifiable - not empty, not failing."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        d = ast.literal_eval(raw)
    except Exception:                                   # noqa: BLE001
        try:
            d = json.loads(raw)
        except Exception:                               # noqa: BLE001
            return None
    return d if isinstance(d, dict) and d else None


def occupancy_note(cube_dir: Path, strategy: str) -> dict:
    """The correction term this tool cannot compute - reported, not assumed.

    A tighter level frees occupancy and admits trades present in no cube
    (L812). Returns a quantified count where B2905's attribution exists, and
    says UNQUANTIFIED where the pre-B2905 literal destroyed it."""
    f = cube_dir / "skipped_trades.csv"
    out = {"artifact": f.name, "blocked_rows_attributable": None,
           "attribution_available": False}
    if not f.exists():
        out["note"] = ("no skipped_trades.csv in the cube - the occupancy "
                       "correction cannot be bounded at all")
        return out
    try:
        sk = pd.read_csv(f, usecols=["strategy", "reason"], low_memory=False)
    except (OSError, ValueError) as exc:
        out["note"] = f"skipped_trades.csv unreadable: {exc!r}"
        return out
    occ = sk[sk["reason"].astype(str).str.contains("already_open", na=False)]
    out["blocked_rows_total"] = int(len(occ))
    names = occ["strategy"].astype(str)
    literal = int(names.str.startswith("(").sum())
    if literal:
        out["note"] = (
            f"{literal} of {len(occ)} occupancy rows carry a LITERAL stamp "
            "instead of a strategy name (the pre-B2905 writer), so the "
            "per-strategy correction is UNQUANTIFIABLE on this cube. Every "
            "count below is a LOWER BOUND on the level's trade set: a tighter "
            "bound frees occupancy and admits trades present in no cube "
            "(L812). B2905 fixed the stamp forward-only.")
        return out
    out["attribution_available"] = True
    out["blocked_rows_attributable"] = int(
        names.str.split(",").apply(lambda xs: strategy in xs).sum())
    out["note"] = (
        f"{out['blocked_rows_attributable']} occupancy blocks name this "
        "strategy. A tighter bound frees some of them, so each level's trade "
        "count below is a LOWER BOUND by at most that many (L812).")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--strategy", default=None,
                    help="override the manifest's graded strategy (hand runs)")
    a = ap.parse_args()

    cube_dir = Path(a.cube)
    tl_path = cube_dir / "trade_log.csv"
    ted_path = cube_dir / "trade_exit_detail.csv"
    for p in (tl_path, ted_path):
        if not p.exists():
            print(f"[FAIL] no {p.name} in {cube_dir}")
            return 2

    strat = a.strategy
    if strat is None:
        try:
            import run_postconfig as rp
            strat, _riders = rp.graded_and_riders(cube_dir)
        except Exception:                               # noqa: BLE001
            strat = None
    if strat not in GATE:
        print(f"[FAIL] graded strategy {strat!r} is not one of "
              f"{sorted(GATE)} - this leg grades the candle P6 axis only "
              "(fail closed, L642)")
        return 2

    direction, production = GATE[strat]
    import producer_variant_table as pvt
    p6 = [x for x in pvt.SPECS[strat]["params"] if x["id"] == "P6"][0]
    levels = list(p6["free_band"])
    assert float(p6["production"]) == production, (p6["production"], production)

    tl = pd.read_csv(tl_path, low_memory=False)
    tl = tl[tl["strategy"].astype(str) == strat].copy()
    if tl.empty:
        print(f"[FAIL] no {strat} rows in {tl_path.name}")
        return 2

    # ---- reproduction gate, at the PRODUCTION bound ----------------------
    vals, unverifiable = [], 0
    for raw in tl["signals_at_entry"]:
        d = parse_signals(raw)
        if d is None or KEY not in d:
            vals.append(None)
            unverifiable += 1
        else:
            vals.append(float(d[KEY]))
    tl["_rsi"] = vals
    covered = tl[tl["_rsi"].notna()]
    failed = covered[~covered["_rsi"].apply(
        lambda v: keep_row(v, direction, production))]
    repro = {"covered_rows": int(len(covered)),
             "unverifiable_rows": int(unverifiable),
             "rows_total": int(len(tl)),
             "production_bound": production, "direction": direction,
             "failed_reproduction": int(len(failed))}
    if len(failed):
        print(f"[FAIL] reproduction gate: {len(failed)} of {len(covered)} "
              f"covered rows do NOT re-pass {KEY} {direction} {production} - "
              "the logged signals disagree with the gate the engine ran, so "
              "nothing this tool reports about any level is believable "
              "(owner ruling 2026-09-02). Grading nothing.")
        return 2

    # ---- grade each free level on the exit-expanded cube -----------------
    ted = pd.read_csv(ted_path, low_memory=False)
    ted = ted[ted["strategy"].astype(str) == strat].copy()
    ted["entry_date"] = ted["entry_date"].astype(str).str[:10]
    covered = covered.copy()
    covered["entry_date"] = covered["entry_date"].astype(str).str[:10]

    results = []
    for lvl in [production] + levels:
        keep = covered[covered["_rsi"].apply(
            lambda v: keep_row(v, direction, float(lvl)))]
        ids = set(zip(keep["ticker"].astype(str), keep["entry_date"]))
        sub = ted[[(t, d) in ids for t, d in
                   zip(ted["ticker"].astype(str), ted["entry_date"])]]
        per_exit = []
        for ex, g in sub.groupby("exit_method", observed=True):
            st = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=a.min_n)
            if st is None:
                continue
            per_exit.append({"exit": str(ex), "n": int(len(g)),
                             "sharpe": st.get("sharpe"),
                             "ci_lo": st.get("ci_lo")})
        per_exit.sort(key=lambda r: -(r["ci_lo"] if r["ci_lo"] is not None
                                      else -9e9))
        results.append({
            "level": float(lvl),
            "is_production": float(lvl) == production,
            "trades_kept": int(len(keep)),
            "trades_kept_is_a_lower_bound": True,
            "exit_rows": int(len(sub)),
            "exits_evaluable": len(per_exit),
            "best": per_exit[0] if per_exit else None,
            "per_exit": per_exit[:6],
        })

    doc = {
        "strategy": strat, "axis": "P6 " + str(p6["param"]),
        "grader": "scripts/grade_free_levels_candle.py (S6-B2904)",
        "cube": str(cube_dir).replace("\\", "/"),
        "gate_mirrored": f"{KEY} {direction} <level> (strict, per screener.py)",
        "levels_searched": [production] + [float(x) for x in levels],
        "reproduction": repro,
        "occupancy": occupancy_note(cube_dir, strat),
        "results": results,
        "multiplicity_exposure": (
            f"{len(levels)} free levels searched on this axis, each a max over "
            f"{max((r['exits_evaluable'] for r in results), default=0)} exits, "
            "nested inside ONE engine run - the levels are not independent "
            "trials and no correction is applied here (S6-B2444 recording "
            "rule)"),
        "verdict_status": ("CANDIDATES, never admissions - every trade count "
                           "is a lower bound while the occupancy correction "
                           "is unsimulated (L812)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube_dir.name}_free_levels.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    base = results[0]
    print(f"[OK] {strat} P6 {direction} - reproduction {repro['covered_rows']} "
          f"covered / {repro['unverifiable_rows']} unverifiable / 0 failed; "
          f"production {base['level']} keeps {base['trades_kept']} trades")
    for r in results[1:]:
        b = r["best"]
        print(f"     level {r['level']:<8} keeps {r['trades_kept']:<5} "
              + (f"best {b['exit']} ci_lo {b['ci_lo']} n {b['n']}"
                 if b else "no exit cleared the power floor"))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
