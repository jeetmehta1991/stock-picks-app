"""Build PASSED_STRATEGY_EXIT_LIST.md (B1375; F1+F6 B1377; F2+F3+F4 B1378).

Source attribution (per CHECKLIST #77):
  - Candidate pool: strategies in the LOOSE OOS pool (>=0.7 annualized OOS Sharpe
    in >=1 DEC-505 fold) from walk_forward_r5_all_cells_annualized.json, split into
    non-conditional + the regime-conditional survivors.
  - Regime-conditional survivors: validate_conditional_exit_regime.json
    (IS-pick 2022-2025 / OOS-measure 2025-2026, delta>=0.3) + the per-regime exit
    map best_exit_per_strategy_by_regime.json.
  - Entry gates + direction: STRATEGY_ROSTER.md (auto-generated from screener.py).
  - Per-(strategy x direction x exit) metrics: recomputed here from
    output_r5_merged_1_7/trade_exit_detail.csv via walk_forward_r5_cells._sharpe
    (ANNUALIZED, identical to metrics.py::_sharpe; B1371 fix) on NET, winsorized pnl.

GRADING (B1378 - the review's F3/F2 fixes):
  - The best exit is picked using IS folds 1-3 ONLY (2022-05 -> 2025-05); fold 4
    (2025-05 -> 2026-05) is a TRUE HOLDOUT that no selection decision saw. The old
    "best single fold out of 4" picked and graded on the same data.
  - Every Sharpe carries a Lo(2002) 95% CI; the holdout family is BH-FDR corrected.
Dual strategies (trade both long and short) get TWO rows with per-leg entry gates.
"""
from __future__ import annotations
import json
import re
import sys
from datetime import date
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from walk_forward_r5_cells import _sharpe, bh_fdr   # noqa: E402  (shared stats: annualized Sharpe + CI + BH-FDR)

REPO = Path(__file__).resolve().parent.parent
CUBE = REPO / "output_r5_merged_1_7"
IS_FOLDS = [("F1", date(2022, 5, 5), date(2023, 5, 5)),
            ("F2", date(2023, 5, 5), date(2024, 5, 5)),
            ("F3", date(2024, 5, 5), date(2025, 5, 5))]
HOLDOUT = ("F4", date(2025, 5, 5), date(2026, 5, 5))
MIN_N = 30
GATE = 0.7
WINSORIZE = 300.0   # F6 (B1377): cap collapse-priced outliers (SBNY)
COST_BPS = 20.0     # F1 (B1377): T1a round-trip cost (5bps slippage + 1bp commission + spread)
FDR_Q = 0.05


def parse_roster():
    r = {}
    for ln in open(REPO / "STRATEGY_ROSTER.md", encoding="utf-8"):
        if ln.startswith("|") and "`" in ln:
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) >= 11:
                r[c[1].strip("`")] = {"direction": c[3], "fires": c[5], "signals": c[6],
                                      "compact": c[8], "affinity": c[9], "category": c[2]}
    return r


def _is_long(direction) -> bool:
    return str(direction).strip().lower().startswith("l")


def split_fires(fires: str, direction) -> str:
    """F4 (B1378): a dual strategy's roster `fires` is `fl = <long-leg> <br> fs = <short-leg>`.
    Pre-B1378 BOTH direction rows displayed the pooled expression, i.e. the short row
    showed the LONG leg's gates - wrong gates against the row's own metrics. Split on the
    fl/fs markers and show only this leg."""
    if not fires:
        return "?"
    txt = fires.strip().strip("`")
    parts = [p.strip() for p in re.split(r"<br\s*/?>", txt) if p.strip()]
    want = "fl" if _is_long(direction) else "fs"
    for p in parts:
        if re.match(r"^" + want + r"\s*=", p):
            return p
    return txt if len(parts) == 1 else txt


def split_compact(compact: str, direction) -> str:
    """Same F4 split for the human-readable compact column ('LONG: ... \\ SHORT: ...')."""
    if not compact:
        return "?"
    c = compact.replace("\\", " ").strip()
    if _is_long(direction):
        m = re.search(r"LONG:(.*?)(?:SHORT:|$)", c, re.S)
        return ("LONG:" + m.group(1)).strip() if m else c
    m = re.search(r"SHORT:(.*)$", c, re.S)
    return ("SHORT:" + m.group(1)).strip() if m else c


def _fold_stats(g, lo, hi):
    m = g[(g.entry_date >= lo) & (g.entry_date < hi)]
    return _sharpe(m.pnl_pct.values, m.hold_days.values)


def cell_metrics(sub):
    """F3 (B1378) HONEST-HOLDOUT selection: choose the exit on IS folds 1-3 ONLY
    (by MEAN evaluable IS Sharpe - the mean, not the max, so a single lucky IS year
    can't win the pick), then report fold 4 as a never-selected-on holdout."""
    best = None
    for ex, g in sub.groupby("exit_method"):
        perfold = {}
        is_sh = []
        for name, lo, hi in IS_FOLDS:
            st = _fold_stats(g, lo, hi)
            perfold[name] = st
            if st:
                is_sh.append(st["sharpe"])
        if not is_sh:
            continue                      # no evaluable IS fold -> cannot pick this exit
        is_mean = sum(is_sh) / len(is_sh)
        hold = _fold_stats(g, HOLDOUT[1], HOLDOUT[2])
        perfold["F4"] = hold
        full = _sharpe(g.pnl_pct.values, g.hold_days.values)
        cum = {"sharpe": full["sharpe"] if full else None, "n": int(len(g)),
               "wr": full["wr"] if full else round(float((g.pnl_pct.values > 0).mean()), 3),
               "ret": round(float(g.pnl_pct.sum()), 1)}
        rec = {"exit": ex, "is_mean": round(is_mean, 3), "n_is_folds": len(is_sh),
               "is_folds_ge_gate": sum(1 for s in is_sh if s >= GATE),
               "holdout": hold, "perfold": perfold, "cum": cum}
        if best is None or is_mean > best["is_mean"]:
            best = rec
    return best


def main():
    roster = parse_roster()
    allc = json.load(open(CUBE / "walk_forward_r5_all_cells_annualized.json"))
    loose_strats = sorted({c["strategy"] for c in allc["cells"] if c["n_folds_ge_0.7"] >= 1})
    val = json.load(open(CUBE / "validate_conditional_exit_regime.json"))
    ov = {r["strategy"]: r for r in val["strategies"] if r["oos_delta"] >= 0.3}
    regmap = json.load(open(CUBE / "best_exit_per_strategy_by_regime.json"))["best_exit_per_strategy_by_value"]
    noncond = sorted(set(loose_strats) - set(ov))
    cond = sorted(ov)
    print(f"[INFO] candidate pool: {len(noncond)} non-conditional + {len(cond)} conditional")

    print("[INFO] reading cube ...")
    df = pd.read_csv(CUBE / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date", "pnl_pct", "hold_days"],
                     low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    # F6 winsorize + F1 net-of-cost (B1377): every metric below is on NET, de-outliered pnl.
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
    print(f"[INFO] friction applied: winsorize +/-{WINSORIZE}, cost {COST_BPS}bps (NET Sharpes)")

    # B1378 LEAK FIX: do NOT pre-screen to the loose pool. That pool was selected on
    # >=0.7 in >=1 of ALL FOUR folds - including F4 - so a strategy could enter it
    # *because of* the holdout year, and grading it on F4 would be circular. Grade
    # EVERY (strategy x direction) in the cube; pool membership becomes a column, and
    # the BH family becomes the full universe (the honest denominator).
    pool = set(loose_strats)
    rows = []
    for strat in sorted(df.strategy.dropna().unique()):
        conditional = strat in ov
        sd = df[df.strategy == strat]
        for d in sorted(sd.direction.dropna().unique()):
            m = cell_metrics(sd[sd.direction == d])
            if m is None:
                continue
            ro = roster.get(strat, {})
            rmap = regmap.get(strat, {}) if conditional else {}
            rows.append({"strategy": strat, "direction": d, "conditional": conditional,
                         "in_loose_pool": strat in pool, **m,
                         "regimes": ", ".join(f"{k}:{v['exit_method']}({v['sharpe']})"
                                              for k, v in sorted(rmap.items(), key=lambda kv: -kv[1]["sharpe"])),
                         "gate_leg": split_compact(ro.get("compact", ""), d),
                         "fires_leg": split_fires(ro.get("fires", ""), d),
                         "category": ro.get("category", "?")})

    # F3: BH-FDR across the HOLDOUT family. Selection happened on IS only, so each row
    # contributes exactly ONE holdout test -> the family is the evaluable holdout rows.
    ev = [r for r in rows if r["holdout"]]
    rej, thr = bh_fdr([r["holdout"]["p"] for r in ev], q=FDR_Q)
    for r, ok in zip(ev, rej):
        r["bh"] = bool(ok)
    for r in rows:
        h = r["holdout"]
        r.setdefault("bh", False)
        if not h:
            r["verdict"] = "UNEVAL"       # holdout n<30 -> no honest verdict
        elif h["sharpe"] >= GATE and r["bh"]:
            r["verdict"] = "PASS"
        elif h["sharpe"] >= GATE:
            r["verdict"] = "PASS-noFDR"   # cleared the bar but not survivable to multiple testing
        else:
            r["verdict"] = "DROP"

    n_ev = len(ev)
    passed = [r for r in rows if r["verdict"] == "PASS"]
    pass_nofdr = [r for r in rows if r["verdict"] == "PASS-noFDR"]
    dropped = [r for r in rows if r["verdict"] == "DROP"]
    uneval = [r for r in rows if r["verdict"] == "UNEVAL"]
    ci_pos = [r for r in passed if r["holdout"]["ci_lo"] > 0]
    S = lambda rs: len({r["strategy"] for r in rs})   # noqa: E731
    print(f"[RESULT] rows={len(rows)} strategies={S(rows)} | holdout-evaluable rows={n_ev} "
          f"| PASS={len(passed)} rows / {S(passed)} strategies | PASS-noFDR={len(pass_nofdr)} "
          f"| DROP={len(dropped)} | UNEVAL={len(uneval)} | of PASS with CI_lo>0: {len(ci_pos)}")

    order = {"PASS": 0, "PASS-noFDR": 1, "DROP": 2, "UNEVAL": 3}
    rows.sort(key=lambda r: (order[r["verdict"]], -(r["holdout"]["sharpe"] if r["holdout"] else -99)))

    def fcell(st):
        return f"{st['sharpe']}({st['n']})" if st else "n<30"

    def hcell(st):
        return f"**{st['sharpe']}**({st['n']})" if st else "n<30"

    def table(rs):
        out = ["| Strategy | Dir | Best Exit (IS-picked) | Cond | IS F1 | IS F2 | IS F3 | "
               "HOLDOUT F4 | 95% CI lo | BH q<0.05 | Verdict | Cum Sharpe/n/WR/ret% | Entry gate (this leg) |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rs:
            pf, h, cum = r["perfold"], r["holdout"], r["cum"]
            out.append(
                f"| `{r['strategy']}` | {r['direction']} | `{r['exit']}` | "
                f"{'Y' if r['conditional'] else 'N'} | "
                f"{fcell(pf['F1'])} | {fcell(pf['F2'])} | {fcell(pf['F3'])} | {hcell(h)} | "
                f"{h['ci_lo'] if h else '-'} | {'YES' if r['bh'] else 'no'} | {r['verdict']} | "
                f"{cum['sharpe']}/{cum['n']}/{cum['wr']}/{cum['ret']}% | "
                f"{(r['regimes'] + ' || ') if r['conditional'] and r['regimes'] else ''}{r['gate_leg']} |")
        return out

    md = []
    md.append("<!-- Source: per CHECKLIST #77; auto-built by scripts/build_passed_strategy_exit_list.py "
              "from the R5 cube (output_r5_merged_1_7) + STRATEGY_ROSTER.md. Do NOT hand-edit; regenerate. -->\n")
    md.append("# Passed Strategy -> Exit List (R5, TRUE-HOLDOUT graded)\n")
    md.append(f"**Generated:** B1378 | **Cube:** `output_r5_merged_1_7` (614 tickers, 7 batches, "
              f"2022-05-05 -> 2026-05-05)\n")
    md.append("> **This list is graded on a TRUE HOLDOUT (B1378).** The exit is picked using ONLY "
              "2022-05 -> 2025-05 (IS folds 1-3); the final year 2025-05 -> 2026-05 (F4) is a holdout no "
              "selection decision ever saw, and the **Verdict column is decided by the holdout alone**. "
              "Sharpes are ANNUALIZED, NET of 20bps round-trip cost, winsorized +/-300% (F1+F6, B1377), "
              "and carry a Lo(2002) 95% CI. Deep review: `R5_ANALYSIS_DEEP_REVIEW.md`.\n")
    md.append("## Headline\n")
    md.append(f"| Outcome | Rows (strategy x direction) | Strategies |\n|---|---|---|\n"
              f"| **PASS** (holdout Sharpe >= 0.7 AND survives BH-FDR q<0.05) | **{len(passed)}** | **{S(passed)}** |\n"
              f"| PASS-noFDR (cleared 0.7 but not multiple-testing-survivable) | {len(pass_nofdr)} | {S(pass_nofdr)} |\n"
              f"| DROP (holdout Sharpe < 0.7 - selected-in-sample, failed live-forward) | {len(dropped)} | {S(dropped)} |\n"
              f"| UNEVAL (holdout n<30 - no honest verdict) | {len(uneval)} | {S(uneval)} |\n"
              f"| TOTAL graded rows (every strategy x direction in the cube) | {len(rows)} | {S(rows)} |\n")
    pool_ev = [r for r in ev if r["in_loose_pool"]]
    out_ev = [r for r in ev if not r["in_loose_pool"]]
    hit = lambda rs: (sum(1 for r in rs if r["holdout"]["sharpe"] >= GATE) / len(rs)) if rs else 0.0  # noqa: E731
    md.append(f"**Does the old screen have predictive power?** Holdout hit-rate (Sharpe >= 0.7) is "
              f"**{hit(pool_ev):.1%}** for rows the pre-holdout LOOSE screen selected ({len(pool_ev)} rows) "
              f"vs **{hit(out_ev):.1%}** for rows it rejected ({len(out_ev)} rows). The screen carries real "
              f"but modest signal - it roughly doubles the hit rate; it does not identify winners on its own.\n")
    md.append(f"Of the {len(passed)} PASS rows, **{len(ci_pos)}** also have a 95% CI lower bound above 0 "
              f"(F2: the rest are point-estimate passes whose CI still straddles 0 at this n).\n")
    md.append("**How to read a row:** IS F1-F3 are the selection folds (the exit was chosen to maximise "
              "their MEAN, not their max - a single lucky year cannot win the pick). HOLDOUT F4 is the "
              "verdict fold. `n<30` = below the statistical-power floor, un-evaluable. Cum = full-window "
              "Sharpe / trades / win-rate / summed per-trade return% (includes IS; context only, not a gate).\n")
    md.append("**Method / caveats:**\n"
              "- Sharpe = ANNUALIZED per-trade x sqrt(252/avg_hold), matching `metrics.py::_sharpe` (B1371 fix).\n"
              "- NET of 20bps T1a round-trip (config.py DEC-612) + winsorized +/-300% (SBNY delisting collapse).\n"
              "- **BH-FDR** (Benjamini-Hochberg, q=0.05) across the holdout family; the repo's canonical "
              "correction per B982. Selection used IS only, so each row contributes exactly ONE holdout test.\n"
              "- **Regime-conditional rows (Cond=Y):** exit varies by `regime_at_entry`, assigned once at "
              "entry and held to close; the regime->exit map is shown before `||` in the last column.\n"
              "- Dual strategies appear as TWO rows, each showing **its own leg's** entry gates (F4 fix).\n")
    md.append("\n**KNOWN LIMITATIONS (what is still NOT proven):**\n"
              "1. **[APPLIED B1377] Net-of-cost + winsorized.** REMAINING: shorts exclude borrow cost "
              "(short rows are optimistic); the formal cost-sensitivity RATIO gate is not computed.\n"
              "2. **[APPLIED B1378 - F2] Sharpe CIs** are reported. At n=30-40 the CI half-width is large; "
              "prefer rows whose CI lower bound clears 0, and treat point Sharpes above 2 at low n as noise.\n"
              "3. **[APPLIED B1378 - F3] True holdout + BH-FDR.** REMAINING: the holdout is ONE year "
              "(2025-26, a bull-leaning tape) - it is a real out-of-sample test but not a multi-regime one.\n"
              "4. **[APPLIED B1378 - F4] Per-leg entry gates** now render per direction.\n"
              "5. **Crisis regime absent** (n<30 in the 2022-26 window) - this system is meant to buy dips "
              "in crisis; NO crisis-regime evidence exists in this set.\n"
              "6. **Not a deploy list.** Exit assignment (`STRATEGY_EXIT_OVERRIDE`) is a strategy change and "
              "requires explicit owner approval; paper trading is the next filter, not this table.\n")
    keep = [r for r in rows if r["verdict"] in ("PASS", "PASS-noFDR")]
    md.append("\n## A. SURVIVORS - cleared the holdout (the only rows with forward evidence)\n")
    md.append("`PASS` = holdout Sharpe >= 0.7 AND survives BH-FDR. `PASS-noFDR` = cleared 0.7 but "
              "not distinguishable from multiple-testing luck; treat as watchlist, not deploy.\n")
    md += table(keep)
    md.append("\n## B. DROP - selected in-sample, FAILED the holdout year\n")
    md.append("These are the rows the pre-holdout method would have handed you. They are the reason "
              "the holdout exists; each was picked on 2022-2025 and did not clear 0.7 on 2025-2026.\n")
    md += table([r for r in rows if r["verdict"] == "DROP"])
    md.append("\n## C. UNEVAL - holdout n<30 (no honest verdict possible)\n")
    md += table([r for r in rows if r["verdict"] == "UNEVAL"])
    md.append("\n## Appendix - entry-gate formulas for SURVIVORS (exact per-leg `fires` expression)\n")
    for r in keep:
        md.append(f"- **`{r['strategy']}`** [{r['direction']}, {r['category']}, {r['verdict']}]: "
                  f"`{r['fires_leg']}`")
    out = REPO / "PASSED_STRATEGY_EXIT_LIST.md"
    out.write_text("\n".join(md), encoding="utf-8")

    js = CUBE / "passed_strategy_exit_holdout_graded.json"
    js.write_text(json.dumps({
        "generated": "B1378", "gate_sharpe": GATE, "fdr_q": FDR_Q, "bh_threshold": thr,
        "winsorize": WINSORIZE, "cost_bps": COST_BPS,
        "is_folds": [f[0] for f in IS_FOLDS], "holdout_fold": HOLDOUT[0],
        "counts": {"rows": len(rows), "strategies": S(rows), "holdout_evaluable_rows": n_ev,
                   "pass_rows": len(passed), "pass_strategies": S(passed),
                   "pass_ci_lo_gt_0_rows": len(ci_pos),
                   "pass_nofdr_rows": len(pass_nofdr), "drop_rows": len(dropped),
                   "uneval_rows": len(uneval)},
        "rows": [{k: v for k, v in r.items() if k not in ("perfold",)} for r in rows],
    }, indent=2, default=str), encoding="utf-8")
    print(f"[OK] wrote {out}")
    print(f"[OK] wrote {js}")


if __name__ == "__main__":
    main()
