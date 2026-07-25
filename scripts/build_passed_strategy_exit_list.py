"""Build PASSED_STRATEGY_EXIT_LIST.md (B1375).

Source attribution (per CHECKLIST #77):
  - Passed set: the 82 strategies in the LOOSE OOS pool (>=0.7 annualized OOS
    Sharpe in >=1 DEC-505 fold) from walk_forward_r5_all_cells_annualized.json,
    split into 70 non-conditional + 12 that overlap the 17 regime-conditional
    survivors; PLUS 5 conditional-only rescues = 70 non-conditional + 17
    conditional (per owner).
  - Regime-conditional survivors: validate_conditional_exit_regime.json
    (IS-pick 2022-2025 / OOS-measure 2025-2026, delta>=0.3) + the per-regime exit
    map best_exit_per_strategy_by_regime.json.
  - Entry gates + direction: STRATEGY_ROSTER.md (auto-generated from screener.py).
  - Per-(strategy x direction x exit) OOS metrics: recomputed here from
    output_r5_merged_1_7/trade_exit_detail.csv with ANNUALIZED Sharpe
    (per_trade * sqrt(252/avg_hold), identical to metrics.py::_sharpe; B1371 fix).

Dual strategies (trade both long and short) get TWO rows, per owner directive.
"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
CUBE = REPO / "output_r5_merged_1_7"
FOLDS = [("F1", date(2022, 5, 5), date(2023, 5, 5)), ("F2", date(2023, 5, 5), date(2024, 5, 5)),
         ("F3", date(2024, 5, 5), date(2025, 5, 5)), ("F4", date(2025, 5, 5), date(2026, 5, 5))]
MIN_N = 30
GATE = 0.7


def ann_sharpe(pnl, hold):
    n = len(pnl)
    if n < MIN_N:
        return None
    std = pnl.std(ddof=1) if n > 1 else 0.0
    if std <= 0:
        return None
    avg_hold = float(hold.mean()) if len(hold) else 10.0
    tpy = max(1.0, 252.0 / max(avg_hold, 1e-9))
    return {"sharpe": round(float(pnl.mean() / std) * tpy ** 0.5, 3), "n": int(n),
            "wr": round(float((pnl > 0).mean()), 3), "avg_hold": round(avg_hold, 1)}


def parse_roster():
    r = {}
    for ln in open(REPO / "STRATEGY_ROSTER.md", encoding="utf-8"):
        if ln.startswith("|") and "`" in ln:
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) >= 11:
                r[c[1].strip("`")] = {"direction": c[3], "fires": c[5], "signals": c[6],
                                      "compact": c[8], "affinity": c[9], "category": c[2]}
    return r


def cell_metrics(sub):
    """best exit for a (strategy[,direction]) subframe: per-exit best-fold OOS Sharpe."""
    best = None
    for ex, g in sub.groupby("exit_method"):
        folds = []
        for _, o0, o1 in FOLDS:
            m = g[(g.entry_date >= o0) & (g.entry_date < o1)]
            st = ann_sharpe(m.pnl_pct.values, m.hold_days.values)
            if st:
                folds.append(st["sharpe"])
        if not folds:
            continue
        bestfold = max(folds)
        nge = sum(1 for s in folds if s >= GATE)
        full = ann_sharpe(g.pnl_pct.values, g.hold_days.values)
        rec = {"exit": ex, "best_oos": bestfold, "folds_ge_07": nge, "n_qual_folds": len(folds),
               "n": full["n"] if full else int(len(g)), "wr": full["wr"] if full else None,
               "full_sharpe": full["sharpe"] if full else None}
        if best is None or bestfold > best["best_oos"]:
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
    print(f"[INFO] {len(noncond)} non-conditional + {len(cond)} conditional = {len(noncond)+len(cond)}")

    print("[INFO] reading cube for per-(strategy x direction x exit) metrics ...")
    df = pd.read_csv(CUBE / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date", "pnl_pct", "hold_days"],
                     low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date

    def rows_for(strat, conditional):
        out = []
        sd = df[df.strategy == strat]
        dirs = sorted(sd.direction.dropna().unique())
        for d in dirs:
            sub = sd[sd.direction == d]
            m = cell_metrics(sub)
            if m is None:
                continue
            rmap = regmap.get(strat, {}) if conditional else {}
            regimes = ", ".join(f"{k}:{v['exit_method']}({v['sharpe']})"
                                for k, v in sorted(rmap.items(), key=lambda kv: -kv[1]["sharpe"])) if rmap else ""
            out.append({"strategy": strat, "direction": d, **m, "regimes": regimes,
                        "roster": roster.get(strat, {})})
        return out

    def table(strats, conditional):
        lines = ["| Strategy | Dir | Best Exit | Regime-Cond | Regimes->Exit | OOS Sharpe (best fold) | Folds>=0.7 | n | WR | Entry gate (compact) |",
                 "|---|---|---|---|---|---|---|---|---|---|"]
        appendix = []
        for s in strats:
            for r in rows_for(s, conditional):
                ro = r["roster"]
                cflag = "Y" if conditional else "N"
                reg = r["regimes"] if conditional else (ro.get("affinity", "") or "all")
                lines.append(f"| `{r['strategy']}` | {r['direction']} | `{r['exit']}` | {cflag} | "
                             f"{reg if conditional else '-'} | {r['best_oos']} | {r['folds_ge_07']}/{r['n_qual_folds']} | "
                             f"{r['n']} | {r['wr']} | {ro.get('compact','?')} |")
            ro = roster.get(s, {})
            appendix.append(f"- **`{s}`** ({ro.get('direction','?')}, {ro.get('category','?')}): "
                            f"`{ro.get('fires','?')}` | signals: {ro.get('signals','?')}")
        return lines, appendix

    nc_t, nc_a = table(noncond, False)
    c_t, c_a = table(cond, True)
    md = []
    md.append("<!-- Source: per CHECKLIST #77; B1375 auto-built by scripts/build_passed_strategy_exit_list.py from the R5 cube (output_r5_merged_1_7) + STRATEGY_ROSTER.md. Do NOT hand-edit; regenerate. -->\n")
    md.append("# Passed Strategy -> Exit List (R5, 2026-07-25)\n")
    md.append("**What this is:** the strategies whose (strategy x exit) cleared the LOOSE OOS gate "
              "(annualized OOS Sharpe >= 0.7 in >=1 of 4 DEC-505 folds) on the full 614-ticker R5 cube, "
              "with each strategy's best backtested exit, entry-gate formula, and OOS metrics. Dual "
              "strategies (trade long and short) appear as two rows.\n")
    md.append("**Method / caveats (read before deploying):**\n"
              "- Sharpe is ANNUALIZED (per-trade x sqrt(252/avg_hold), matching `metrics.py::_sharpe`; the B1371 fix).\n"
              "- **LOOSE gate** = >=0.7 in >=1 fold: a cell can clear in a single lucky year -> higher false-positive rate than the strict >=2-fold set. This is a wide candidate pool; the 1B agent layer + paper trading are the downstream filters.\n"
              "- **Regime-conditional (17):** the regime-varying exit BEAT the single best exit OUT-OF-SAMPLE (IS-pick 2022-2025 / OOS-measure 2025-2026, DeltaSharpe >= 0.3). Exit is assigned once at entry from `regime_at_entry`, held to close.\n"
              "- Metrics recomputed per (strategy x direction x exit); best exit = highest single-fold OOS Sharpe (n>=30 per fold).\n")
    md.append("\n**KNOWN LIMITATIONS (self-review B1375 - this is a CANDIDATE list, not a deploy list):**\n"
              "1. **GROSS Sharpe - no transaction costs/slippage.** The cube `pnl_pct` carries no friction; net-of-cost Sharpes are lower and some cells will fail. The AUTO-FAIL cost-sensitivity gate (`metrics.py`) was NOT applied here -> S6-B1375-NET-OF-COST.\n"
              "2. **Small-sample noise, no confidence intervals.** ~14% of qualifying cells are n=30-40, where a Sharpe's 95% CI is ~+/-1.6 - a 0.7 point estimate is statistically indistinguishable from 0. Point Sharpes (incl. the 2.0-2.7 tops) are unreliable at low n -> S6-B1375-SHARPE-CI.\n"
              "3. **The LOOSE 613 lacks a true train/test holdout.** They are 'consistent across >=1 annual slice' selected from the SAME window (multiple-testing across 4758 cells x 4 folds, uncorrected). Only the 17 regime-conditional overrides have a genuine IS-pick/OOS-measure split -> the 613 is weaker evidence than the 17 -> S6-B1375-OOS-HOLDOUT.\n"
              "4. **Dual per-direction:** a strategy can clear the POOLED gate yet have neither direction clear individually (pooling averages long+short). Rows show per-direction metrics - a direction with best-fold OOS < 0.7 is a candidate to DROP, not deploy. The 'Entry gate' column currently shows the strategy-level compact for both direction rows (dual `fires` split by direction is TODO -> S6-B1375-DUAL-FORMULA).\n"
              "5. **Crisis regime absent** (n<30 in the 2022-26 window) - this system is meant to buy dips in crisis; no crisis-regime evidence exists here.\n")
    md.append(f"**Counts:** {len(noncond)} non-conditional + {len(cond)} regime-conditional strategies "
              f"(dual strategies split by direction).\n")
    md.append("\n## A. Non-conditional strategies (single best exit)\n")
    md += nc_t
    md.append("\n## B. Regime-conditional strategies (exit varies by entry regime)\n")
    md += c_t
    md.append("\n## Appendix - entry-gate formulas (exact `fires` expression)\n")
    md.append("### Non-conditional\n")
    md += nc_a
    md.append("\n### Regime-conditional\n")
    md += c_a
    out = REPO / "PASSED_STRATEGY_EXIT_LIST.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"[OK] wrote {out} ({len(nc_t)-2} non-cond rows + {len(c_t)-2} cond rows)")


if __name__ == "__main__":
    main()
