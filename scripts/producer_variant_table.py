"""Standard producer-variant table - S6-OPT-196 reporting contract (B1506).

ONE repeatable artifact per strategy, so every optimisation run is reported the
same way and results are comparable across strategies. Two tables:

  TABLE A - PARAMETER INVENTORY. Every producer parameter the strategy touches,
            whether it was TESTED, and WHY its band holds those values. This is
            the CHECKLIST #182 denominator made explicit: the verdict must cite
            "N of M producers" and M is the row count of Table A.

  TABLE B - COMBINATION RESULTS. Every combination actually graded, with the
            gates it passed and the gates it failed.

SUBSET-SAFE is the field that decides cost. A parameter that can only REMOVE
fires keeps every variant inside the R5 cube, so it grades for free. One that
can ADD fires needs engine resimulation, because the cube holds no P&L for a
trade R5 never took.

Adding a strategy = adding a SPECS entry. The renderer is strategy-agnostic.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

# --------------------------------------------------------------------------
# SPECS - the parameter inventory per strategy. Every value here is READ from
# source; `evidence` cites where. Never populate a row from memory.
# --------------------------------------------------------------------------
SPECS: dict[str, dict] = {
    "smc_breaker_block_long": {
        "gate": "(breaker_bullish) AND (price_above_ema_200)",
        "formula": """=============================== PRODUCER LAYER ===============================

P1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )
                   -> a bar is a swing high if its high is the highest
                      across swing_length bars BEFORE and AFTER it
                   PARAMETER: swing_length = 20   (library default is 50)

P2  ob_df   =  ob( ohlc, swings, close_mitigation = False )
                   -> emits, per detected block:  OB (+1 bull / -1 bear),
                      Top, Bottom, MitigatedIndex
                   PARAMETER: close_mitigation = False
                      False -> a block counts as mitigated when the HIGH/LOW
                               pierces it
                      True  -> only when the CLOSE pierces it  (stricter)

P3  events  =  ob_df[ OB != 0 ].tail( 20 )
                   PARAMETER: tail N = 20     (hardcoded literal, not an argument)

P4  per event e:   e.is_mitigated = ( MitigatedIndex > 0 )
                                    AND ( MitigatedIndex < today_index )
                   -> no parameter; derived from P2's MitigatedIndex
                   -> MitigatedIndex = the BAR INDEX of the candle that broke
                      through the zone (smc.py:69); 0 means never mitigated.
                      It is an INDEX, not a flag - which is why an ancient block
                      stays eligible forever with no age check (S6-B1500a).

P5  per event e:   e.broken_up    = ( close > e.Top )
                   -> no parameter; strict inequality, zero buffer

P6  ema_50_200 =  compute_ema_sma( df )      # pairs (9,21),(20,50),(50,200)
       price_above_ema_200  =  close > EMA(close, span = 200)
                   PARAMETER: span = 200, emitted only from the (50,200) pair

=============================== STRATEGY LAYER ===============================

breaker_bullish  =  AT LEAST ONE event e in P3 satisfies ALL of:
                        ( e.OB == -1 )          <- bearish block      [from P2]
                        AND ( e.is_mitigated )                        [from P4]
                        AND ( e.broken_up )                           [from P5]

fires            =  ( breaker_bullish )  AND  ( price_above_ema_200 ) [from P6]""",
        # B1575: baseline artifact corrected per L445 - rung4_chunk1 was an
        # abandoned A-C chunk. Fire count is from that defective cube and is
        # NOT comparable to merged_1_7; re-measure before citing it.
        "baseline": {"artifact": "output_r5_merged_1_7", "fires": None,
                     "tickers": 161, "holdout_n": 147,
                     "window": "2022-05-06..2026-05-04"},
        "params": [
            {"id": "P1", "producer": "_smc.swing_highs_lows", "param": "swing_length",
             "production": 20, "type": "int", "band": [10, 20, 30, 50],
             "derivation": "library default is 50; production overrides to 20. Band brackets both.",
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "smc.py:137"},
            {"id": "P2", "producer": "_smc.ob", "param": "close_mitigation",
             "production": False, "type": "bool", "band": [False, True],
             "derivation": "boolean - both values ARE the band. True = mitigated on CLOSE only.",
             "subset_safe": True, "status": "TESTED",
             "evidence": "smc.py:380"},
            {"id": "P3", "producer": "ob_events.tail(N)", "param": "tail_n",
             "production": 20, "type": "int", "band": [3, 5, 10, 20],
             "derivation": "B1610 DEFECT - this text says the band spans the measured "
                           "rank range 1-4, and it does NOT: its floor is 3, the TOP of "
                           "that range. MEASURED on 420 cfg2 fires: levels 3/5/10/20 admit "
                           "39.8/68.8/98.6/100.0pct, so 10->20 moved 0 of 50 cfg1 groups. "
                           "The discriminating region is 1-3 (tail_n=2 alone cuts 73pct). "
                           "Also COLLINEAR with P4 age_bars_max, Spearman +0.881. "
                           "RE-BAND PROPOSED, OWNER APPROVAL PENDING (S6-B1610b).",
             "subset_safe": True, "status": "BAND-DEFECTIVE",
             "evidence": "smc_ict.py:266-268"},
            {"id": "P4", "producer": "recency filter on OB age", "param": "age_bars_max",
             "production": None, "type": "int|None", "band": [60, 120, 180, 250, None],
             "derivation": "measured real retests 45-134 bars, latches 294-469, gap 134-294 (B1501).",
             "subset_safe": True, "status": "TESTED",
             "evidence": "smc_ict.py:252 (event_recency_bars, S6-B1500a)"},
            {"id": "P5", "producer": "break test (close > top)", "param": "break_pct_max",
             "production": None, "type": "float|None", "band": [0.01, 0.02, 0.03, 0.05, None],
             "derivation": "NEW-GATE, OWNER-APPROVED B1507 (was N/A - production has no such "
                           "parameter; `close > top` is a strict inequality). Band from the "
                           "B1501 measurement: real retests 0.5-2.7pct from the zone, stale "
                           "latches 7.5-60pct, empty gap 3-7pct. Caps at 1/2/3pct bracket the "
                           "retest population; 5pct sits in the gap; None = production. "
                           "Direction is an UPPER bound (L359: a breaker block is a RETEST, so "
                           "CLOSER is stricter).",
             "subset_safe": True, "status": "PENDING",
             "evidence": "smc_ict.py:283-284 (no parameter today)"},
            {"id": "P6", "producer": "compute_ema_sma", "param": "span",
             "production": 200, "type": "int", "band": [9, 20, 21, 50, 200],
             "derivation": "ALL spans the producer emits (READ technical.py:750 pairs "
                           "(9,21),(20,50),(50,200)). B1507 widened from [50,200] - the "
                           "earlier band silently dropped 9/20/21 with no stated rule "
                           "(#165). 9/20/21 are short-horizon and weak trend filters "
                           "economically, but exclusion must be a MEASURED result, not a "
                           "pre-judgement. Spans 100/250 do NOT exist -> NEW-GATE, ask owner.",
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "technical.py:750"},
        ],
    },
}

GATE_ORDER = ("pooled_sharpe", "profit_factor", "sortino", "psr",
              "min_trades_holdout", "min_trades_full_period")


def validate_spec(spec: dict) -> list[str]:
    """Formula and Table A must not drift apart. Every P-id in the formula needs
    a params row and every params row needs a formula step - a mechanical check,
    because a hand-maintained pair of views silently diverges (L368 class)."""
    import re as _re
    ids_formula = set(_re.findall(r"^(P\d+)\s", spec.get("formula", ""), _re.M))
    ids_params = {p["id"] for p in spec["params"]}
    errs = []
    for i in sorted(ids_formula - ids_params):
        errs.append(f"{i} appears in the formula but has no Table A row")
    for i in sorted(ids_params - ids_formula):
        errs.append(f"{i} has a Table A row but no formula step")
    if not spec.get("formula"):
        errs.append("SPEC has no `formula` - it is REQUIRED (B1510 standard)")
    return errs


def _fmt(v) -> str:
    if v is None:
        return "none"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def table_a(spec: dict) -> list[str]:
    rows = ["| ID | producer | parameter | production | band tested | subset-safe | status | why this band |",
            "|---|---|---|---|---|---|---|---|"]
    for p in spec["params"]:
        band = ", ".join(_fmt(b) for b in p["band"]) or "-"
        ss = {True: "YES - cube-gradable, free",
              False: "NO - needs engine resim",
              None: "-"}[p["subset_safe"]]
        rows.append(f"| {p['id']} | `{p['producer']}` | `{p['param']}` | "
                    f"{_fmt(p['production'])} | {band} | {ss} | **{p['status']}** | "
                    f"{p['derivation']} |")
    return rows


def table_b(results: list[dict], keys: list[str]) -> list[str]:
    """Every metric roster_core.evaluate() computes, split GATED vs DIAGNOSTIC.

    GATED (6) decide PASS/FAIL. DIAGNOSTIC are computed and reported but do NOT
    gate - per CLAUDE.md, win_rate was demoted at B1387 and max_drawdown /
    calmar / deflated_sharpe at B1436-B1437. Reporting them keeps a cell's
    character visible even when the verdict is FAIL.
    """
    hdr = " | ".join(keys)
    rows = [f"| {hdr} | fires | ho n | full n | exit | **Sharpe** | **PF** | "
            f"**Sortino** | **PSR** | win% | payoff | expectancy | p | CI-lo | "
            f"gates | failing | verdict |",
            "|" + "---|" * (len(keys) + 16)]
    for r in results:
        vals = " | ".join(_fmt(r.get(k)) for k in keys)
        fail = ", ".join(k for k, v in (r.get("gates") or {}).items() if not v) or "-"
        rows.append(
            f"| {vals} | {r.get('fires', 0)} | {_fmt(r.get('holdout_n'))} | "
            f"{_fmt(r.get('full_period_n'))} | {r.get('exit', '-')} | "
            f"{_fmt(r.get('sharpe'))} | {_fmt(r.get('profit_factor'))} | "
            f"{_fmt(r.get('sortino'))} | {_fmt(r.get('psr'))} | "
            f"{_fmt(r.get('win_rate'))} | {_fmt(r.get('payoff'))} | "
            f"{_fmt(r.get('expectancy'))} | {_fmt(r.get('p'))} | "
            f"{_fmt(r.get('ci_lo'))} | "
            f"{r.get('gates_passed', '-')}/{len(GATE_ORDER)} | {fail} | {r['verdict']} |")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--results", default="", help="grid results JSON")
    # B1523 owner directive: "Everytime you show factorial you need to show
    # boolean producer formula again." This mode emits the FORMULA and the
    # FACTORIAL together and cannot emit one without the other - the coupling is
    # in the tool, not in anyone remembering.
    ap.add_argument("--factorial", action="store_true",
                    help="print Section 1 formula + factorial breakdown; no results needed")
    ap.add_argument("--keys", default="close_mitigation,age_bars_max,tail_n")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    spec = SPECS.get(a.strategy)
    if spec is None:
        print(f"no SPEC for {a.strategy}; add one to SPECS (never infer at runtime)")
        return 1
    if a.factorial:
        errs = validate_spec(spec)
        if errs:
            print("SPEC VALIDATION FAILED:")
            for e in errs:
                print(f"  {e}")
            return 1
        applicable = [p for p in spec["params"] if p["status"] != "N/A"]
        fact = math.prod(len(p["band"]) for p in applicable)
        free = math.prod(len(p["band"]) for p in applicable if p["subset_safe"])
        runs = math.prod(len(p["band"]) for p in applicable if not p["subset_safe"])
        print(f"# {a.strategy} - FORMULA + FACTORIAL (never shown apart)")
        print("")
        print("## Boolean producer formula (READ from source)")
        print("")
        print("```")
        print(spec["formula"])
        print("```")
        print("")
        print("## Factorial")
        print("")
        print("| | parameter | production | band VALUES | n | class | own engine run? |")
        print("|---|---|---|---|---|---|---|")
        for p in applicable:
            cls = "subset-safe" if p["subset_safe"] else "**FIRE-ADDING**"
            need = "no - derives offline" if p["subset_safe"] else "**YES**"
            vals = ", ".join(_fmt(b) for b in p["band"]) or "-"
            print(f"| {p['id']} | `{p['param']}` | {_fmt(p['production'])} | {vals} | {len(p['band'])} | {cls} | {need} |")
        expr = " x ".join(str(len(p["band"])) for p in applicable)
        print("")
        print("```")
        print(f"FULL FACTORIAL   {expr} = {fact}")
        print(f"offline per run  {free}")
        print(f"ENGINE RUNS      {runs}")
        print(f"check            {runs} x {free} = {runs * free}")
        print("```")
        return 0

    if not a.results:
        print("--results is required unless --factorial is passed")
        return 1
    data = json.loads(Path(a.results).read_text())
    results = data["results"]
    keys = a.keys.split(",")

    tested = [p for p in spec["params"] if p["status"] == "TESTED"]
    applicable = [p for p in spec["params"] if p["status"] != "N/A"]
    # Factorial + free subspace computed from the inventory, never hand-counted
    # (L368: hand-counting reintroduces the error #182 exists to prevent).
    factorial = math.prod(len(p["band"]) for p in applicable)
    free_space = math.prod(len(p["band"]) for p in applicable if p["subset_safe"])
    gradable = [r for r in results if r["verdict"] in ("PASS", "FAIL")]
    passed = [r for r in results if r["verdict"] == "PASS"]

    errs = validate_spec(spec)
    if errs:
        print("SPEC VALIDATION FAILED (formula <-> Table A drift):")
        for e in errs:
            print(f"  {e}")
        return 1

    out = [f"# Producer variant table - `{a.strategy}`", "",
           f"**Gate:** `{spec['gate']}`", "",
           "## Section 1 - boolean formula (READ from source, never recalled)", "",
           "```", spec["formula"], "```", "",
           f"**R5 baseline:** {spec['baseline']['fires']} fires / "
           f"{spec['baseline']['tickers']} tickers / holdout n="
           f"{spec['baseline']['holdout_n']} / {spec['baseline']['window']} "
           f"(`{spec['baseline']['artifact']}`)", "",
           "## Section 2 - Table A: parameter inventory", ""]
    out += table_a(spec)
    out += ["", "## Section 3 - Table B: combination results", ""]
    out += table_b(results, keys)
    out += ["", "## Verdict (CHECKLIST #182 - denominator required)", "",
            f"**{len(passed)} of {len(results)} combinations passed, across "
            f"{len(tested)} of {len(applicable)} applicable producers.**", "",
            f"- graded: {len(gradable)} | non-gradable: {len(results) - len(gradable)}",
            f"- **FULL FACTORIAL = {factorial}** "
            f"({' x '.join(str(len(p['band'])) + ' (' + p['id'] + ')' for p in applicable)}); "
            f"combinations run = {len(results)} = **{100 * len(results) / factorial:.0f}% of factorial**",
            f"- free (subset-safe) subspace = {free_space} | "
            f"needs engine resim = {factorial - free_space}",
            f"- UNTESTED producers: "
            f"{', '.join(p['id'] + ' ' + p['param'] for p in spec['params'] if p['status'] == 'UNTESTED') or 'none'}",
            "", "*Generated by `scripts/producer_variant_table.py` - regenerate, do not hand-edit.*"]

    text = "\n".join(out)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
