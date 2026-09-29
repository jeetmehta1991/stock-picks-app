"""S6-B3119: grade the bollinger_lower P9 FREE levels off a landed cube.
Zero engine hours.

WHY IT EXISTS. B2569 (owner directive 2026-09-02) made free-level grading a
leg of EVERY landing (L752 / #290): a missing leg produces NO row and NO
FAIL, so the span campaign's cubes would land with the approved adx levels
silently ungraded. Modelled on grade_free_levels_candle.py (S6-B2904), the
L754 second-family extraction.

THE AXIS GRADED HERE. P9 is the adx ceiling, and it is OFFLINE: no env knob,
and the engine's gate reads a value persisted per trade -
  bollinger_lower  screener.py (strat_bollinger_lower)  adx < 35  (a CEILING)
Every free level TIGHTENS (the ceiling drops), so each level selects a
STRICT SUBSET of trades already in the cube. Coverage on the R5 baseline:
adx present at 100.0% of the strategy's 1,622 fires (the charter's measured
free-band line).

AXIS SCOPE, DISCLOSED (#290 - scheduled-with-mechanism, never dropped):
this leg grades P9, P11-tight and P8-tight (S6-B3117, the T3 band word's
single-axis enumerations, added B3120 Batch C). The B-row companion axes
ride the per-leg Step-1 grid instrument (scripts/breadth_step1_grid.py
--cube-dir <landing> --leg long|short, the b3119 pattern), and the P8xP11
JOINT composite remains S6-B3118a's dedicated grader (the band-coverage
gate names it at any Step-2 declaration). One leg per axis family; each
named; none silent.

P11 TIGHT (each rsi edge -5 long / +5 short, T3-approved): the production
leg is rsi_2<5 or rsi_14<thr_long per vix band {low:40, mid:45, high:50}
(short: rsi_2>95 or rsi_14>thr_short {60,55,50}), screener.py:1855-1863
verbatim. Tightening kills the rsi_2 escape arm outright (<0 / >100 are
unsatisfiable - DISCLOSED, not hidden), so the tight level is effectively
rsi_14 vs thr-/+5. The vix band re-derives from PERSISTED vix_percentile
(technical.py:2727-2731: low pct<1/3, mid <2/3, else high); vix_percentile
is persisted ROUNDED to 4dp, so rows within 0.00005 of either boundary are
BOUNDARY-AMBIGUOUS - excluded and counted, never guessed.

P8 TIGHT (quartile edges 0.25/0.75 replacing terciles, T3-approved): a
RE-BANDING is not a pure subset - it reassigns fires between threshold
regimes, so a variant can admit rows production rejected. Offline grades
the INTERSECTION population only (fired under production AND passing under
the re-banding); variant-only admissions are UNMEASURABLE offline and the
rejected count is reported (L812 semantics, stated in the artifact).

THE GATE IS MIRRORED EXACTLY, STRICT COMPARISON INCLUDED: the producer uses
`<` (adx_ok = s.get("adx", 30) < 35).

REPRODUCTION GATE (owner, 2026-09-02): before any level is graded, every
covered row must RE-PASS at the PRODUCTION bound; a covered row that fails
means the logged signal disagrees with the gate the engine ran - exit 2,
grade nothing. Unparseable rows are counted, excluded and reported.

THE OCCUPANCY DISCLOSURE (L812): a subset of SIGNALS is not a subset of
TRADES - removing trades at a tighter level frees occupancy the engine alone
can simulate. Every count here is a LOWER BOUND; verdicts are candidates,
never admissions.

Usage (the battery passes exactly this):
  python scripts/grade_free_levels_bollinger.py --cube <dir> --out <grid.json>
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
from occupancy_disclosure import (  # noqa: E402
    occupancy_disclosure)

ROOT = Path(__file__).resolve().parent.parent

STRAT = "bollinger_lower"

# the live gate, read from the producer - a strict ceiling
DIRECTION, PRODUCTION = "lt", 35.0
KEY = "adx"


def keep_row(value, direction: str, bound: float) -> bool:
    """Mirror the producer's gate EXACTLY, strict comparison included."""
    return (value < bound) if direction == "lt" else (value > bound)


def score_reproduction(prod_per_exit, grid_path) -> dict:
    """S6-B3120f (L877): the reproduction gate covers the SCORE, not only
    the fire set. The production row's per-exit sharpe / ci_lo (net basis,
    min_n=1) must EQUAL the landed family grade's is_sharpe / is_ci_lo on
    every exit the family grid carries, with matching trade counts - or the
    leg fails closed (owner ruling 2026-09-02: a re-scorer that cannot
    reproduce the landed baseline is believable about nothing). Returns the
    artifact block; the caller exits 2 on any mismatch, and a missing or
    unreadable grid IS a mismatch (fail closed, L642)."""
    try:
        grid = json.loads(Path(grid_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"family_grid": str(grid_path).replace("\\", "/"),
                "basis": "net (roster_core.py:181 mirrored)",
                "compared_exits": 0,
                "mismatches": [f"family grid unreadable: {exc!r}"]}
    mine = {str(r["exit"]): r for r in prod_per_exit}
    compared, mismatches = 0, []
    for row in grid.get("per_exit") or []:
        ex = str(row.get("exit"))
        fam_sh, fam_cl = row.get("is_sharpe"), row.get("is_ci_lo")
        if fam_sh is None and fam_cl is None:
            continue
        m = mine.get(ex)
        if m is None:
            mismatches.append(f"{ex}: in the family grid, absent here")
            continue
        compared += 1
        if int(row.get("fires", -1)) != int(m["n"]):
            mismatches.append(
                f"{ex}: n {m['n']} vs family fires {row.get('fires')}")
            continue
        for key, fam in (("sharpe", fam_sh), ("ci_lo", fam_cl)):
            v = m.get(key)
            same = (v is None and fam is None) or (
                v is not None and fam is not None
                and round(float(v), 3) == round(float(fam), 3))
            if not same:
                mismatches.append(f"{ex}: {key} {v} vs family {fam}")
    if compared == 0:
        mismatches.append(
            "no exit compared - the family grid carries no graded rows")
    return {"family_grid": str(grid_path).replace("\\", "/"),
            "basis": "net (roster_core.py:181 mirrored)",
            "compared_exits": compared, "mismatches": mismatches}


# ---- S6-B3117: the P11 / P8 single-axis enumerations (T3-approved) --------
THR_LONG = {"low": 40.0, "mid": 45.0, "high": 50.0}    # screener.py:1866-1871
THR_SHORT = {"low": 60.0, "mid": 55.0, "high": 50.0}
BOUNDARY_EPS = 0.00005      # vix_percentile persists round(pct, 4)


def vix_band(vp: float, lo: float, hi: float) -> str | None:
    """Band from the persisted percentile, producer comparisons verbatim
    (technical.py:2727-2731); None = BOUNDARY-AMBIGUOUS within the 4dp
    rounding sliver of either edge."""
    if abs(vp - lo) <= BOUNDARY_EPS or abs(vp - hi) <= BOUNDARY_EPS:
        return None
    if vp < lo:
        return "low"
    if vp < hi:
        return "mid"
    return "high"


def rsi_leg(direction: str, rsi2: float, rsi14: float, band: str,
            edge_shift: float) -> bool:
    """The strategy's rsi leg (screener.py:1891/1894 verbatim), with the
    T3 tight shift applied to BOTH edges of the row's direction. At -5/+5
    the rsi_2 escape arm (5 -> 0 / 95 -> 100) is unsatisfiable - kept in
    the expression so the disclosure is the arithmetic, not a footnote."""
    if direction == "long":
        thr = THR_LONG[band] - edge_shift
        return (rsi2 < 5.0 - edge_shift) or (rsi14 < thr)
    thr = THR_SHORT[band] + edge_shift
    return (rsi2 > 95.0 + edge_shift) or (rsi14 > thr)


def grade_kept(ted, keep_ids, min_n):
    """Per-exit grades over the exit-expanded rows of the kept entries."""
    sub = ted[[(t, d) in keep_ids for t, d in
               zip(ted["ticker"].astype(str), ted["entry_date"])]]
    per_exit = []
    for ex, g in sub.groupby("exit_method", observed=True):
        st = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=min_n)
        if st is None:
            continue
        per_exit.append({"exit": str(ex), "n": int(len(g)),
                         "sharpe": st.get("sharpe"),
                         "ci_lo": st.get("ci_lo")})
    per_exit.sort(key=lambda r: -(r["ci_lo"] if r["ci_lo"] is not None
                                  else -9e9))
    return per_exit


def p11_p8_sections(tl, ted, min_n) -> dict:
    """Both T3 single-axis enumerations on the covered fires. Rows missing
    any of rsi_2 / rsi_14 / vix_percentile, carrying an unknown direction,
    or boundary-ambiguous on the vix edge are EXCLUDED AND COUNTED. The
    production leg is re-passed first (reproduction discipline); a covered,
    unambiguous row failing it is a hard reproduction failure."""
    rows = []
    n_missing = n_baddir = 0
    for _, r in tl.iterrows():
        d = parse_signals(r.get("signals_at_entry"))
        if d is None or "rsi_2" not in d or "rsi_14" not in d:
            n_missing += 1
            continue
        direction = str(r.get("direction", "")).lower()
        if direction not in ("long", "short"):
            n_baddir += 1
            continue
        # the PRODUCTION band is the engine's own branch on the PERSISTED
        # flags (screener.py:1866-1871): low if vix_band_low, elif high,
        # ELSE mid - absent flags mean mid there too, mirrored exactly.
        # (First draft re-derived it from vix_percentile and drew 22
        # reproduction failures on span 9 - the flags are the branch input,
        # the percentile is P8's re-banding input only.)
        if d.get("vix_band_low"):
            flag_band = "low"
        elif d.get("vix_band_high"):
            flag_band = "high"
        else:
            flag_band = "mid"
        vp = d.get("vix_percentile")
        rows.append({"ticker": str(r["ticker"]),
                     "entry_date": str(r["entry_date"])[:10],
                     "direction": direction, "band": flag_band,
                     "rsi2": float(d["rsi_2"]), "rsi14": float(d["rsi_14"]),
                     "vp": float(vp) if vp is not None else None})

    def run(name, edge_shift):
        ambiguous = repro_fail = no_vp = 0
        kept, rejected = set(), 0
        for r in rows:
            if not rsi_leg(r["direction"], r["rsi2"], r["rsi14"],
                           r["band"], 0.0):
                repro_fail += 1
                continue
            if name == "p11_tight":
                variant_band = r["band"]
            else:
                if r["vp"] is None:
                    no_vp += 1
                    continue
                variant_band = vix_band(r["vp"], 0.25, 0.75)
                if variant_band is None:
                    ambiguous += 1
                    continue
            if rsi_leg(r["direction"], r["rsi2"], r["rsi14"],
                       variant_band, edge_shift):
                kept.add((r["ticker"], r["entry_date"]))
            else:
                rejected += 1
        return {"covered_rows": len(rows), "excluded_missing": n_missing,
                "excluded_direction": n_baddir,
                "excluded_no_vix_percentile": no_vp,
                "boundary_ambiguous": ambiguous,
                "reproduction_failures_at_production": repro_fail,
                "kept": len(kept), "rejected_by_level": rejected,
                "per_exit": grade_kept(ted, kept, min_n)[:6]}

    out = {
        "p11_tight": {
            "axis": "P11 vix-conditional rsi edges, TIGHT -5 long / +5 short "
                    "(T3-approved single-axis enumeration)",
            "note": "rsi_2 escape arm unsatisfiable at the shift (0/100) - "
                    "the tight level is effectively rsi_14 vs thr-/+5",
            **run("p11_tight", 5.0),
        },
        "p8_tight": {
            "axis": "P8 vix band edges at QUARTILES 0.25/0.75 (T3-approved); "
                    "INTERSECTION population only",
            "note": "a re-banding reassigns fires between threshold regimes; "
                    "variant-only admissions are UNMEASURABLE offline (L812) "
                    "and every count is a lower bound",
            **run("p8_tight", 0.0),
        },
    }
    return out


def parse_signals(raw):
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--family-grid", default=None,
                    help="the landed family grid this leg must reproduce "
                         "(default output_audit/<cube>_grid_auto.json)")
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
    if strat != STRAT:
        print(f"[FAIL] graded strategy {strat!r} is not {STRAT!r} - this leg "
              "grades the bollinger P9 axis only (fail closed, L642)")
        return 2

    import producer_variant_table as pvt
    p9 = [x for x in pvt.SPECS[strat]["params"] if x["id"] == "P9"][0]
    assert float(p9["production"]) == PRODUCTION, (p9["production"], PRODUCTION)
    levels = [float(x) for x in p9["free_band"]
              if float(x) != PRODUCTION]

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
    tl["_adx"] = vals
    covered = tl[tl["_adx"].notna()]
    failed = covered[~covered["_adx"].apply(
        lambda v: keep_row(v, DIRECTION, PRODUCTION))]
    repro = {"covered_rows": int(len(covered)),
             "unverifiable_rows": int(unverifiable),
             "rows_total": int(len(tl)),
             "production_bound": PRODUCTION, "direction": DIRECTION,
             "failed_reproduction": int(len(failed))}
    if len(failed):
        print(f"[FAIL] reproduction gate: {len(failed)} of {len(covered)} "
              f"covered rows do NOT re-pass {KEY} {DIRECTION} {PRODUCTION} - "
              "the logged signals disagree with the gate the engine ran, so "
              "nothing this tool reports about any level is believable "
              "(owner ruling 2026-09-02). Grading nothing.")
        return 2

    # ---- grade each free level on the exit-expanded cube -----------------
    ted = pd.read_csv(ted_path, low_memory=False)
    ted = ted[ted["strategy"].astype(str) == strat].copy()
    # S6-B3120f (L877): score on the FAMILY GRADER'S basis - the winsorize +
    # COST_BPS/100 deduction roster_core.load_cube applies (roster_core.py:181
    # is the definition of record). The raw read stays only because this leg
    # needs signal columns load_cube's usecols drop.
    ted["pnl_pct"] = (ted["pnl_pct"].astype(float)
                      .clip(-rc.WINSORIZE, rc.WINSORIZE)
                      - rc.COST_BPS / 100.0)
    ted["entry_date"] = ted["entry_date"].astype(str).str[:10]
    covered = covered.copy()
    covered["entry_date"] = covered["entry_date"].astype(str).str[:10]

    results = []
    for lvl in [PRODUCTION] + levels:
        keep = covered[covered["_adx"].apply(
            lambda v: keep_row(v, DIRECTION, float(lvl)))]
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
        if float(lvl) == PRODUCTION:
            prod_sub = sub
        results.append({
            "level": float(lvl),
            "is_production": float(lvl) == PRODUCTION,
            "trades_kept": int(len(keep)),
            "trades_kept_is_a_lower_bound": True,
            "exit_rows": int(len(sub)),
            "exits_evaluable": len(per_exit),
            "best": per_exit[0] if per_exit else None,
            "per_exit": per_exit[:6],
        })

    # ---- S6-B3120f: SCORE reproduction against the landed family grade --
    prod_check = []
    for ex, g in prod_sub.groupby("exit_method", observed=True):
        st = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=1)
        if st is not None:
            prod_check.append({"exit": str(ex), "n": int(len(g)),
                               "sharpe": st.get("sharpe"),
                               "ci_lo": st.get("ci_lo")})
    fam_grid = Path(a.family_grid) if a.family_grid else (
        ROOT / "output_audit" / f"{cube_dir.name}_grid_auto.json")
    srep = score_reproduction(prod_check, fam_grid)
    if srep["mismatches"]:
        print("[FAIL] score reproduction (S6-B3120f): the production row does "
              "not reproduce the landed family grade ("
              + "; ".join(str(x) for x in srep["mismatches"][:6])
              + ") - grading nothing.")
        return 2

    # S6-B3117 (B3120 Batch C): the T3 single-axis enumerations ride the
    # same landing leg - battery-wired, never executed-once (L752/#290)
    t3 = p11_p8_sections(tl, ted, a.min_n)

    doc = {
        "strategy": strat, "axis": "P9 " + str(p9["param"]),
        "grader": "scripts/grade_free_levels_bollinger.py (S6-B3119)",
        "cube": str(cube_dir).replace("\\", "/"),
        "gate_mirrored": f"{KEY} {DIRECTION} <level> (strict, per screener.py)",
        "levels_searched": [PRODUCTION] + levels,
        "axis_scope": ("P9 graded here; B-row companions ride "
                       "breadth_step1_grid --cube-dir per leg; the P8xP11 "
                       "composite is S6-B3118a's grader - each axis family "
                       "has a named instrument (#290)"),
        "basis": ("net: pnl_pct clipped to +/-WINSORIZE then minus "
                  "COST_BPS/100 - roster_core.py:181 mirrored (S6-B3120f)"),
        "reproduction": repro,
        "score_reproduction": srep,
        "occupancy": occupancy_disclosure(cube_dir, strat),
        "p11_tight": t3["p11_tight"],
        "p8_tight": t3["p8_tight"],
        "results": results,
        "levels": {str(r["level"]): {"p9": r["level"],
                                     "is_fires": r["trades_kept"],
                                     "per_exit_ranked_by_ci_lo": r["per_exit"]}
                   for r in results},
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
    print(f"[OK] {strat} P9 {DIRECTION} - reproduction {repro['covered_rows']} "
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
