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
        # B1689: this dict is HAND-MAINTAINED and drifted TWICE - P3 still
        # carried the pre-B1611 band [3,5,10,20] after the owner-approved
        # re-band, and engine_implemented stayed False for P2-P5 after B1616
        # implemented them. The AUTHORITIES are: tighten_breaker_block.py
        # constants (P2-P5 bands), technical.py + config.py (P1/P6), and
        # verify_engine_implemented.py (engine status). Cross-check before
        # quoting this table (#202).
        "params": [
            {"id": "P1", "producer": "_smc.swing_highs_lows", "param": "swing_length",
             "production": 20, "type": "int", "band": [5, 10, 20, 30, 50],
             # B1691 owner directive: swing_length=5 ADDED. The band had ONE level
             # below production and TWO above - built on the hypothesis that higher
             # swing_length = fewer, cleaner swings = less noise. A band shaped by a
             # directional hypothesis can only CONFIRM it. This is the tail_n mistake
             # exactly: that band floored at 3, was re-banded to [1,2,...], and 2 -
             # a level that had not existed - won BOTH wave-1 top-10s.
             "derivation": "library default is 50; production overrides to 20. Band brackets both.",
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "smc.py:137",
             "engine_implemented": True},
            {"id": "P2", "producer": "_smc.ob", "param": "close_mitigation",
             "production": False, "type": "bool", "band": [False, True],
             "derivation": "boolean - both values ARE the band. True = mitigated on CLOSE only.",
             "subset_safe": True, "status": "TESTED",
             "evidence": "smc.py:380",
             "engine_implemented": True},
            {"id": "P3", "producer": "ob_events.tail(N)", "param": "tail_n",
             "production": 20, "type": "int", "band": [1, 2, 3, 5, 10, 20],
             "derivation": "B1610 DEFECT - this text says the band spans the measured "
                           "rank range 1-4, and it does NOT: its floor is 3, the TOP of "
                           "that range. MEASURED on 420 cfg2 fires: levels 3/5/10/20 admit "
                           "39.8/68.8/98.6/100.0pct, so 10->20 moved 0 of 50 cfg1 groups. "
                           "The discriminating region is 1-3 (tail_n=2 alone cuts 73pct). "
                           "Also COLLINEAR with P4 age_bars_max, Spearman +0.881. "
                           "RE-BAND OWNER-APPROVED AND SHIPPED (B1611): band is now 1,2,3,5,10,20. VINDICATED - tail_n=2, a level that did not exist under the old floor, won BOTH wave-1 top-10s.",
             "subset_safe": True, "status": "RE-BANDED-AND-TESTED",
             "evidence": "smc_ict.py:266-268",
             "engine_implemented": True},
            {"id": "P4", "producer": "recency filter on OB age", "param": "age_bars_max",
             "production": None, "type": "int|None", "band": [60, 120, 180, 250, None],
             "derivation": "measured real retests 45-134 bars, latches 294-469, gap 134-294 (B1501).",
             "subset_safe": True, "status": "TESTED",
             "evidence": "B1614 CORRECTION - the prior citation "
                         "'smc_ict.py:252 (event_recency_bars)' was WRONG on both "
                         "counts: line 252 is `_smc.ob(ohlc, swings)` which takes no "
                         "such argument, and `event_recency_bars` (line 257) governs "
                         "`smc_ob_bullish_active` - a DIFFERENT signal. The breaker "
                         "loop (273-296) has NO age filter. P4 is a NEW GATE with no "
                         "engine counterpart; see S6-B1612f.",
             "engine_implemented": True},
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
             "evidence": "smc_ict.py:283-284 (no parameter today)",
             "engine_implemented": True},
            {"id": "P6", "producer": "compute_ema_sma", "param": "span",
             "production": 200, "type": "int", "band": [9, 20, 21, 50, 100, 150, 200],
             "derivation": "ALL spans the producer emits (READ technical.py:750 pairs "
                           "(9,21),(20,50),(50,200)). B1507 widened from [50,200] - the "
                           "earlier band silently dropped 9/20/21 with no stated rule "
                           "(#165). 9/20/21 are short-horizon and weak trend filters "
                           "economically, but exclusion must be a MEASURED result, not a "
                           "pre-judgement. B1686: spans 100 and 150 ADDED to the producer on owner "
                           "directive 2026-08-18 - they did not exist, which is why P6 could "
                           "not sweep them (S6-B1507b). Band is now 7 values; 250 still absent.",
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


def _measured_fmt(value):
    """B1899 (L580): one carrier for "this was never measured".

    Learned at B1889b when a renderer crashed on None, then broken at B1898
    when THIS renderer printed `0` for an unrecorded value. L536 - a rule
    learned on one site does not travel unless something carries it.
    """
    import importlib.util
    import pathlib as _p

    spec = importlib.util.spec_from_file_location(
        "measured_pvt", _p.Path(__file__).resolve().parent / "measured.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.fmt(value)


def table_c(grids: dict[str, dict]) -> list[str]:
    """POST RUN CONFIG TABLE - one row per config, the whole funnel across it.

    B1701, owner directive: the post-config numbers were being reported as prose
    and were "pretty much unreadable". This is the third fixed template
    alongside TABLE A (parameter inventory) and TABLE B (combination results),
    and it answers ONE question: of everything this config tried, how much
    survived, and where did the rest stop?

    The columns are the funnel IN ORDER, because every drop-off has a different
    cause and lumping them hides which one is binding:

      combos      every parameter combination enumerated
      no-exit     died at exit SELECTION - no exit cleared min_n IN-SAMPLE, so
                  grading never happened. This is the dominant loss (85pct at
                  wave 1) and it is a SAMPLE-SIZE fact, not a quality verdict.
      graded      reached evaluate() and produced a Sharpe
      distinct    graded outcomes after equivalence-class collapse - combinations
                  differing only in a SATURATED parameter are the SAME fire set,
                  so counting rows overstates the evidence (L473)
      bands       distinct VALUES this config actually exercised, summed over
                  the parameter axes. B1898 (c): a config that tried one band
                  is not evidence of the same weight as one that tried four,
                  and the old table could not tell them apart.
      best        the top distinct outcome by ci_lo, not Sharpe (L455: the higher
                  Sharpe can carry a NEGATIVE lower bound)

    B1898 (a): the PASS column is GONE. Step 1 is a ranked list with NO GATES
    (B1608) - gates belong to Step 2 (L471) - so the column reported 0 forever
    and read as a verdict on work that had not been judged yet.

    B1898 (b): `no-exit` is renamed `starved-IS`. It is a SAMPLE-SIZE fact -
    no exit cleared min_n IN-SAMPLE - and "no-exit" reads as a selection
    failure. The docstring always said so; the HEADER did not, and the header
    is what gets quoted.

    `graded + no_exit + zero_fires` must equal `combos`; the renderer asserts it
    rather than trusting the arithmetic.
    """
    # B1898 (d), owner directive: every presentation of this table defines its
    # own terms. A reader who meets `graded` or `ci_lo` for the first time in a
    # pasted table has no way to look them up.
    rows = ["_`starved-IS` = no exit cleared min_n IN-SAMPLE, a SAMPLE-SIZE fact "
            "rather than a quality verdict. `graded` = reached `evaluate()` and "
            "produced a Sharpe. `distinct` = graded outcomes after "
            "equivalence-class collapse (L473). `bands` = distinct parameter "
            "VALUES exercised. `ci_lo` = the LOWER bound of the Sharpe "
            "confidence interval, which is what `best` ranks on - a higher "
            "Sharpe can carry a NEGATIVE lower bound (L455)._",
            "",
            "| config | combos | starved-IS | no-Sharpe | graded | distinct | bands | best Sharpe | best CI-lo | best combination |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for name, g in grids.items():
        res = g.get("results", [])
        graded = [r for r in res if r.get("sharpe") is not None]
        no_exit = [r for r in res if r.get("verdict") == "NO_EXIT_SELECTABLE"]
        zero = [r for r in res if r.get("verdict") == "ZERO_FIRES"]
        # B1701: the FOURTH bucket, found because the reconciliation assert
        # fired on its first render. These rows HAVE a verdict but no Sharpe -
        # evaluate() returned a dict and `_sharpe` did not, at holdout_n 16-29.
        # Without this bucket 31-66 rows per config vanished from the funnel,
        # which is exactly the silent loss the assert exists to catch.
        no_sh = [r for r in res if r.get("sharpe") is None
                 and r.get("verdict") not in ("NO_EXIT_SELECTABLE", "ZERO_FIRES")]
        other = len(res) - len(graded) - len(no_exit) - len(zero) - len(no_sh)
        # B1898 (c): count the distinct VALUES actually exercised per axis.
        # Reading them from the enumerated combinations rather than from the
        # grid spec, because the spec is what was INTENDED and the results are
        # what ran.
        axes = {}
        for r in res:
            for k, v in (r.get("admit") or {}).items():
                axes.setdefault(k, set()).add(repr(v))
        # B1898b: render '-' when the artifact records no `admit` block.
        # The first version emitted 0, which reads as 'tested nothing'
        # when the truth is 'not recorded' - the exact rule written one
        # batch earlier at B1889b, that a value which cannot be measured
        # must not render as a number.
        bands = (sum(len(v) for v in axes.values() if len(v) > 1)
                 if axes else None)
        rank = g.get("step1_ranking") or []
        top = max(rank, key=lambda r: (r.get("ci_lo") if r.get("ci_lo") is not None else -9)) if rank else None
        if top:
            a = top["admit"]
            combo = (f"cm={a['close_mitigation']} brk={_fmt(a['break_pct_max'])} "
                     f"age={_fmt(a['age_bars_max'])} tail={a['tail_n']} / {a['exit']}")
            sh, cl = f"{top['sharpe']:.3f}", f"{top['ci_lo']:+.3f}"
        else:
            combo, sh, cl = "-", "-", "-"
        rows.append(f"| `{name}` | {len(res)} | {len(no_exit)} | {len(no_sh)} | {len(graded)} | "
                    f"{g.get('step1_distinct_outcomes', '-')} | {_measured_fmt(bands)} | {sh} | {cl} | {combo} |")
        if other:
            rows.append(f"| | | | | | | | | | **UNCLASSIFIED {other} rows - the funnel does not "
                        f"reconcile, do not trust this row** |")
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
