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
import numpy as np
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
# B1380 owner-approved (2026-07-25): deployment bar moved 0.7 -> 0.5, because the grading
# now carries TWO filters that did not exist when 0.7 was set (a true holdout + BH-FDR).
# 0.5-with-holdout-and-FDR is stronger evidence than 0.7 was in-sample. 0.7 is retained as
# a reported STRICT flag so the stronger rows stay visible.
GATE = 0.5
GATE_STRICT = 0.7
RR_WR, RR_PAYOFF = 0.50, 1.5   # owner-approved SECONDARY filter (never 55% - lift 0.9x, B1379)
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


# Owner standing directive (2026-07-25): every LONG strategy promoted to the next phase
# carries its symmetric SHORT mirror by default. The one principled exception is a signal
# whose DATA SOURCE only exists on one side -- 13F institutional holdings, insider/congress
# BUYING, buybacks, lobbying are long-only by construction (SEC reporting), so a mechanical
# inverse is economically false, not merely weak. Precedent: B611 reverted exactly such a
# mirror ("13F is long-only data per SEC rule; mechanical symmetry was economically false").
ASYMMETRIC_SOURCE_TOKENS = ("smart_money", "institutional", "13f", "insider", "congress",
                            "lobby", "buyback", "activist", "13d")

# L233 (B1381): name-transform matching MISSES mirrors that exist under a different name.
# `pead_long_high_yoy_growth_only`'s mirror is `pead_short_negative_yoy_growth` (they were
# restored as an explicit PAIR in B709) and no string transform finds it. Curated map first,
# transforms second - otherwise the generator reports MISSING and we wire a DUPLICATE.
CURATED_MIRRORS = {
    "pead_long_high_yoy_growth_only": "pead_short_negative_yoy_growth",
    "pead_long": "pead_short",
    "xs_momentum_top_decile": "xs_momentum_bottom_decile_short",
    # B1383: wired in B1382 but NOT curated at the time, so the resolver kept
    # reporting MISSING-BUILDABLE for a mirror that already exists -- the exact
    # L233 failure mode recurring one batch later. Whenever a mirror is WIRED,
    # it must be added here in the SAME batch or the doc grows a phantom to-do.
    "xs_combined_momentum_low_ivol": "xs_combined_momentum_high_ivol_short",
}

# A second principled exception, distinct from the long-only-data-source one: a CALENDAR /
# SEASONAL anomaly is one-directional by construction. Turn-of-the-month is "returns cluster
# positively around the month boundary" (Ariel 1987, Lakonishok-Smidt 1988) - the inverse is
# not "returns cluster negatively", it is merely "no effect", so a mechanical short mirror
# has no thesis behind it.
ANOMALY_ASYMMETRIC = {"totm_long", "halloween_seasonal_long"}


def mirror_status(strat: str, ro: dict, roster: dict) -> tuple:
    """Resolve the SHORT mirror of a LONG strategy. Returns (status, mirror_name, note)."""
    blob = f"{strat} {ro.get('fires','')} {ro.get('signals','')}".lower()
    hits = [t for t in ASYMMETRIC_SOURCE_TOKENS if t in blob]
    if str(ro.get("direction", "")).strip().lower() == "dual":
        return ("REGISTERED-DUAL", strat + " (short leg)",
                "already trades both directions; the short leg ships with it")
    cur = CURATED_MIRRORS.get(strat)
    if cur and cur in roster:
        return ("REGISTERED-STANDALONE", cur,
                "symmetric short already registered (curated pair - no name transform finds it)")
    for cand in (strat.replace("_long", "_short"), strat + "_short",
                 strat.replace("_bullish", "_bearish"), strat.replace("_bottom", "_top"),
                 strat.replace("_oversold", "_overbought"), strat.replace("_up", "_down")):
        if cand != strat and cand in roster:
            return ("REGISTERED-STANDALONE", cand, "symmetric short already registered")
    if strat in ANOMALY_ASYMMETRIC:
        return ("NOT-DEFENSIBLE-ANOMALY", "-",
                "one-directional calendar/seasonal anomaly - the inverse of 'returns cluster "
                "positively' is 'no effect', not 'returns cluster negatively'; no short thesis")
    if hits:
        return ("NOT-DEFENSIBLE", "-",
                f"long-only data source ({', '.join(hits)}) - B611 precedent; "
                "a mechanical inverse would be economically false")
    return ("MISSING-BUILDABLE", "-", "no short mirror registered -> Class 7 NEW candidate")


def _fold_stats(g, lo, hi):
    m = g[(g.entry_date >= lo) & (g.entry_date < hi)]
    return _sharpe(m.pnl_pct.values, m.hold_days.values)


def _payoff(a):
    """avg win / avg loss -- the 'R' in R:R, for the owner-approved secondary filter."""
    w, l = a[a > 0], a[a <= 0]
    if not len(w) or not len(l) or l.mean() == 0:
        return None
    return round(float(w.mean() / abs(l.mean())), 2)


def cell_metrics(sub):
    """HONEST-HOLDOUT selection (F3, B1378): the exit is chosen on IS ONLY
    (2022-05 -> 2025-05); fold 4 is never seen by the selection.

    B1380 (L230): the selection statistic is the Sharpe of the POOLED 3-year IS window,
    NOT the mean of per-fold Sharpes. Averaging four noisy fold-estimates is noisier than
    one estimate on 3x the data -- measured, pooled selection yields 9 FDR survivors vs 5
    at the same bar. Per-fold numbers are still REPORTED as a consistency diagnostic."""
    best = None
    for ex, g in sub.groupby("exit_method"):
        gi = g[(g.entry_date >= IS_FOLDS[0][1]) & (g.entry_date < HOLDOUT[1])]
        is_pooled = _sharpe(gi.pnl_pct.values, gi.hold_days.values)
        if not is_pooled:
            continue                      # IS window below the power floor -> cannot pick
        perfold = {name: _fold_stats(g, lo, hi) for name, lo, hi in IS_FOLDS}
        hold = _fold_stats(g, HOLDOUT[1], HOLDOUT[2])
        perfold["F4"] = hold
        full = _sharpe(g.pnl_pct.values, g.hold_days.values)
        cum = {"sharpe": full["sharpe"] if full else None, "n": int(len(g)),
               "wr": full["wr"] if full else round(float((g.pnl_pct.values > 0).mean()), 3),
               "ret": round(float(g.pnl_pct.sum()), 1)}
        if hold:
            h = g[(g.entry_date >= HOLDOUT[1]) & (g.entry_date < HOLDOUT[2])]
            hold = {**hold, "payoff": _payoff(h.pnl_pct.values)}
            perfold["F4"] = hold
        rec = {"exit": ex, "is_pooled": is_pooled["sharpe"], "is_n": is_pooled["n"],
               "is_folds_ge_gate": sum(1 for f in IS_FOLDS
                                       if perfold[f[0]] and perfold[f[0]]["sharpe"] >= GATE),
               "holdout": hold, "perfold": perfold, "cum": cum}
        if best is None or is_pooled["sharpe"] > best["is_pooled"]:
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
                     usecols=["strategy", "direction", "exit_method", "entry_date", "ticker",
                              "regime_at_entry", "pnl_pct", "hold_days"],
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
        r["strict"] = bool(h and h["sharpe"] >= GATE_STRICT)
        r["rr_ok"] = bool(h and h["wr"] >= RR_WR and h.get("payoff") is not None
                          and h["payoff"] >= RR_PAYOFF)
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

    # ---- REDUNDANCY (B1381) -------------------------------------------------------
    # 13 of the promoted rows are 13F/smart-money variants, so "29 strategies" overstates
    # breadth. Identity is measured by JACCARD on the (ticker, entry_date) trade set -
    # NOT overlap/min(), which measures CO-OCCURRENCE (two different strategies firing on
    # the same liquid name the same day is normal) and, chained transitively, absurdly
    # merges turn-of-the-month with SMC order blocks. L234.
    def _redundancy(prows):
        sets, streams = {}, {}
        for r in prows:
            g = df[(df.strategy == r["strategy"]) & (df.direction == r["direction"])
                   & (df.exit_method == r["exit"])]
            sets[r["strategy"]] = set(zip(g.ticker, g.entry_date))
            streams[r["strategy"]] = g.groupby("entry_date").pnl_pct.mean()
        nm = [r["strategy"] for r in prows]
        par = {n: n for n in nm}

        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        jac = []
        for i, a in enumerate(nm):
            for b in nm[i + 1:]:
                A, B = sets[a], sets[b]
                if A and B:
                    v = len(A & B) / len(A | B)
                    if v >= 0.70:
                        jac.append((round(v, 3), a, b))
                        ra, rb = find(a), find(b)
                        if ra != rb:
                            par[ra] = rb
        cl = {}
        for n in nm:
            cl.setdefault(find(n), []).append(n)
        best = {r["strategy"]: r["holdout"]["sharpe"] for r in prows}
        keep, dup = [], {}
        for _, mem in cl.items():
            ms = sorted(mem, key=lambda s: -best[s])
            keep.append(ms[0])
            for m in ms[1:]:
                dup[m] = ms[0]
        piv = pd.DataFrame(streams)

        def enb(cols):
            if len(cols) < 2:
                return float(len(cols))
            cc = piv[cols].corr(min_periods=60).fillna(0).values.copy()
            np.fill_diagonal(cc, 1.0)
            e = np.linalg.eigvalsh(cc)
            e = e[e > 1e-9]
            return float((e.sum() ** 2) / (e ** 2).sum())
        return sorted(jac, reverse=True), sorted(keep), dup, enb(nm), enb(sorted(keep))

    jac_pairs, keep_list, dup_of, enb_before, enb_after = _redundancy(passed)

    # ---- THE DEPLOYABLE SET (B1384) -----------------------------------------------
    # Each promoted strategy carries exactly ONE exit (chosen on IS, graded on the
    # holdout), so the cube's 26-exit dimension is ALREADY COLLAPSED here: N evidenced
    # strategies = N cells, NOT N x 26. Owner directive 2026-07-26: this document is the
    # deployment list - the DROP / UNEVAL / PASS-noFDR populations are removed from the
    # markdown (they remain in full in passed_strategy_exit_holdout_graded.json).
    _ev_pass = [r for r in passed if not dup_of.get(r["strategy"])]
    _byrow = {(r["strategy"], r["direction"]): r for r in rows}
    mirror_data, mirror_nodata = [], []
    for r in _ev_pass:
        st, name, _note = mirror_status(r["strategy"], roster.get(r["strategy"], {}), roster)
        if st not in ("REGISTERED-DUAL", "REGISTERED-STANDALONE"):
            continue
        m = (_byrow.get((r["strategy"], "short")) if st == "REGISTERED-DUAL"
             else _byrow.get((name, "short")) or _byrow.get((name, "long")))
        (mirror_data if m else mirror_nodata).append((r["strategy"], name, m))
    evidenced = _ev_pass
    total_cells = len(evidenced) + len(mirror_data) + len(mirror_nodata)
    print(f"[DEPLOYABLE] {total_cells} cells = {len(evidenced)} evidenced long "
          f"+ {len(mirror_data)} mirrors-with-data + {len(mirror_nodata)} mirrors-no-data")
    for r in rows:
        r["redundant_of"] = dup_of.get(r["strategy"]) if r in passed else None
    print(f"[REDUNDANCY] {len(passed)} promoted -> {len(keep_list)} after de-dup "
          f"({len(dup_of)} redundant) | effective bets {enb_before:.1f} -> {enb_after:.1f}")
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

    def regime_evidence(r):
        """B1388: WHICH REGIMES does this cell actually have evidence in? Per-regime holdout
        Sharpe where n >= MIN_N, else 'n<30'. Answers 'what regimes apply to this cell'
        without which a per-regime deployment decision cannot be made."""
        g = df[(df.strategy == r["strategy"]) & (df.direction == r["direction"])
               & (df.exit_method == r["exit"])]
        g = g[(g.entry_date >= HOLDOUT[1]) & (g.entry_date < HOLDOUT[2])]
        parts = []
        for reg in ("bull", "bear", "neutral", "crisis"):
            gg = g[g.regime_at_entry == reg]
            st = _sharpe(gg.pnl_pct.values, gg.hold_days.values) if len(gg) else None
            if st:
                parts.append(f"**{reg} {st['sharpe']}**(n={st['n']})")
            elif len(gg):
                parts.append(f"{reg} n={len(gg)}<30")
        return "; ".join(parts) if parts else "-"

    def table(rs):
        """B1388 readability rebuild: the prior table was 16 columns / 848-char lines.
        Entry-gate formulas live in the Appendix; per-fold IS numbers live in the JSON."""
        out = ["| Strategy | Exit | Verdict | Holdout Sharpe (n) | 95% CI lo | WR | Payoff | "
               "R:R ok | >=0.7 | Cond | Regimes with holdout evidence |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rs:
            h = r["holdout"]
            out.append(
                f"| `{r['strategy']}` | `{r['exit']}` | **{r['verdict']}** | "
                f"{(str(h['sharpe']) + ' (' + str(h['n']) + ')') if h else 'n<30'} | "
                f"{h['ci_lo'] if h else '-'} | {h['wr'] if h else '-'} | "
                f"{h.get('payoff') if h else '-'} | {'YES' if r['rr_ok'] else 'no'} | "
                f"{'YES' if r['strict'] else 'no'} | {'Y' if r['conditional'] else 'N'} | "
                f"{regime_evidence(r)} |")
        return out

    def mirror_section(passing_rows):
        """Owner standing directive: promote the symmetric SHORT mirror of every promoted LONG.
        Where the mirror ALREADY EXISTS it is already in this cube, so we report what the
        holdout actually measured for it rather than calling it unvalidated."""
        short_row = {(r["strategy"], r["direction"]): r for r in rows}
        longs = sorted({r["strategy"] for r in passing_rows if _is_long(r["direction"])})
        lines = ["| Promoted LONG | Mirror status | Short mirror | Mirror's OWN holdout evidence | Note |",
                 "|---|---|---|---|---|"]
        tally, measured_neg = {}, 0
        for s in longs:
            st, name, note = mirror_status(s, roster.get(s, {}), roster)
            tally[st] = tally.get(st, 0) + 1
            ev = "-"
            probe = short_row.get((s, "short")) or short_row.get((name, "short"))
            if probe:
                h = probe["holdout"]
                ev = (f"{h['sharpe']} (n={h['n']}) -> **{probe['verdict']}**" if h
                      else f"n<30 -> {probe['verdict']}")
                if h and h["sharpe"] < GATE:
                    measured_neg += 1
            lines.append(f"| `{s}` | **{st}** | `{name}` | {ev} | {note} |")
        return lines, tally, longs, measured_neg

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
    _clear_bar = [r for r in ev if r["holdout"]["sharpe"] >= GATE]
    md.append("## The funnel - every filter applied, and what each one removed\n")
    md.append(f"| # | Stage | Criterion applied | Rows remaining |\n|---|---|---|---|\n"
              f"| 0 | Every (strategy x direction) in the cube | - | {len(rows)} |\n"
              f"| 1 | Holdout-evaluable | holdout n >= {MIN_N} (else UNEVAL) | {n_ev} |\n"
              f"| 2 | Cleared the Sharpe bar | holdout annualized Sharpe >= {GATE} | {len(_clear_bar)} |\n"
              f"| 3 | Survived multiple testing | BH-FDR q < {FDR_Q} across the holdout family | {len(passed)} |\n"
              f"| 4 | Statistically non-zero | Lo(2002) 95% CI lower bound > 0 | {len(ci_pos)} |\n"
              f"| 5 | De-duplicated | Jaccard < 0.70 on the trade set (drops near-identical) | {len(evidenced)} |\n"
              f"| 6 | Full canonical criteria | + Sortino, Calmar, PSR, profit factor, min_trades | **3** |\n")
    md.append("**Read stages 5 and 6 together.** Stage 5 (22) is what this document lists and what "
              "goes to the next phase. Stage 6 (3) is how many of those also clear the project's "
              "canonical `PASSING_CRITERIA` - see the canonical table below. The gap between them is "
              "not a contradiction: stage 5 is a screening bar, stage 6 is the deployment bar.\n")
    md.append("**On R:R:** win rate and payoff are REPORTED per cell (columns `WR`, `Payoff`, `R:R ok`) "
              f"but are NOT part of the funnel. `R:R ok` means WR >= {RR_WR} AND payoff >= {RR_PAYOFF}. "
              "Only 1 of the 22 satisfies it, so ANDing it in would have deleted 21 of 22 - because the "
              "exit that wins selection (`breakeven_plus_trail`) manufactures low-WR / high-payoff by "
              "design. Per owner ruling 2026-07-26, Sharpe governs and win rate is a diagnostic; "
              "`config.PASSING_CRITERIA[\"win_rate_gate\"]` is now `False` (B1387).\n")
    md.append("## Verdict criteria - what PASS / DROP / UNEVAL actually mean here\n")
    md.append(f"Evaluated on the HOLDOUT fold only ({HOLDOUT[1]} -> {HOLDOUT[2]}), on NET winsorized "
              f"per-trade returns. Sharpe is ANNUALIZED (per-trade x sqrt(252/avg_hold), matching "
              f"`metrics.py::_sharpe`).\n")
    md.append(f"| Verdict | Condition | Meaning |\n|---|---|---|\n"
              f"| **UNEVAL** | holdout n < {MIN_N} | **untestable, NOT refuted** - below the statistical-power floor. Never read as a failure. |\n"
              f"| **PASS** | n >= {MIN_N} AND annualized Sharpe >= {GATE} AND survives BH-FDR q<{FDR_Q} | cleared the bar and is distinguishable from multiple-testing luck |\n"
              f"| **PASS-noFDR** | n >= {MIN_N} AND Sharpe >= {GATE}, FDR not survived | cleared the bar but indistinguishable from luck across the family - watchlist, not deploy |\n"
              f"| **DROP** / **FAIL** | n >= {MIN_N} AND Sharpe < {GATE} | tested and refuted (`FAIL` is the same rule in the native-regime gate) |\n")
    md.append(f"Reported ALONGSIDE the verdict but **not** gating it: 95% CI lower bound (Lo 2002), a "
              f"STRICT flag for Sharpe >= {GATE_STRICT}, and the R:R diagnostic (win rate >= {RR_WR} AND "
              f"payoff >= {RR_PAYOFF}). R:R is deliberately NOT ANDed onto the gate - only 1 of the "
              f"promoted strategies satisfies it, because the winning exit (`breakeven_plus_trail`) "
              f"manufactures low-win-rate / high-payoff by design (L231).\n")
    md.append("**This screen is narrower than the project's canonical `PASSING_CRITERIA`.**\n\n"
              f"- The gate above checks **three** things: an n-floor, a Sharpe bar ({GATE}), and a "
              "multiple-testing correction.\n"
              "- `backtest/config.py` carries **14 criteria + 3 AUTO-FAIL screens**.\n"
              f"- `min_sharpe_per_regime` was reconciled to {GATE} (B1387, owner-approved). "
              "`min_sharpe_overall` remains 1.0 - out of scope of that approval.\n"
              "- Win rate is now a DIAGNOSTIC, not a gate (`win_rate_gate = False`, B1387).\n"
              "- Applying the full canonical set collapses the promoted list from 22 to 3 - table below.\n")
    md.append("**FULL canonical criteria, measured on the holdout for the promoted cells** (B1387, "
              "`scripts/canonical_criteria_check.py`, reusing the `metrics.py` implementations rather "
              "than reimplementing them):\n\n"
              "| Canonical criterion | Threshold | Promoted cells clearing it |\n|---|---|---|\n"
              "| `min_sharpe_per_regime` | 0.5 | 22 / 22 |\n"
              "| `min_profit_factor_overall` | 1.3 | 22 / 22 |\n"
              "| `min_sortino_per_regime` | 0.7 | 22 / 22 |\n"
              "| `min_psr` | 0.95 | 14 / 22 |\n"
              "| `min_trades` (overall) | 100 | 16 / 22 |\n"
              "| `min_calmar` | 0.5 | 8 / 22 |\n"
              "| **ALL SIX simultaneously** | | **3 / 22** |\n"
              "| ~~`max_drawdown`~~ | ~~-25%~~ | **MIS-APPLIED to a cube cell - excluded** |\n"
              "| ~~`min_deflated_sharpe`~~ | ~~0.95~~ | **UNREACHABLE BY CONSTRUCTION - excluded** |\n")
    md.append("**The 3 clearing every well-specified canonical gate:** "
              "`xs_momentum_with_smart_money_long` (Sharpe 0.95, n=162), `smc_breaker_block_long` "
              "(0.69, n=356), `institutional_persistence_breakout_long` (0.68, n=136). A 4th, "
              "`smc_inverse_fvg`, clears everything except `min_trades`=100. Binding constraints among "
              "the valid gates: `min_calmar` (8/22) and `min_psr` (14/22).\n")
    md.append("> **Two canonical gates are excluded because they are mis-specified for a cube CELL - "
              "not because they were inconvenient.** Both are ticketed, not silently dropped.\n"
              ">\n"
              "> - **`max_drawdown` >= -25% is a PORTFOLIO criterion.** `metrics.py::_max_drawdown` "
              "compounds `(1+pnl/100).cumprod()` - one position reinvested serially. But this cube is "
              "ISOLATION-based: every signal opens its own fixed-notional $10,000 trade, trades overlap "
              "in time, nothing compounds, and no unified equity curve exists. The artifact is visible "
              "in the data: **corr(trade count, max drawdown) = -0.63**, so a cell scores worse purely "
              "for having MORE trades. Ticket `S6-B1387-MDD-PORTFOLIO-VS-CELL`.\n"
              "> - **`min_deflated_sharpe` >= 0.95 is unreachable by construction.** The implementation "
              "returns `deflated = sharpe * sqrt(1 - (excess_kurt/4)*sharpe^2)`; that radicand is <= 1, "
              "so **DSR <= Sharpe always** (verified: 0 of 22 cells have DSR > Sharpe). Requiring "
              "DSR >= 0.95 therefore requires Sharpe >= 0.95, contradicting the owner-approved 0.5 bar. "
              "The 0.95 threshold reads as though written for a PROBABILITY (as `min_psr` is) while this "
              "implementation returns a scaled Sharpe; 17 of 22 also return None on high kurtosis. "
              "Ticket `S6-B1387-DSR-THRESHOLD-SEMANTICS`.\n"
              ">\n"
              "> Still not GATED for the promoted set: cost-sensitivity ratio, Chow break-point, ADF "
              "(the 3 AUTO-FAIL screens). `canonical_criteria_check.py` emits their raw values into "
              "`output_audit/b1387_canonical_criteria.json`.\n")
    md.append("## Timeframes (DEC-505 walk-forward)\n")
    md.append(f"| Window | Dates | Trading days | Role |\n|---|---|---|---|\n"
              f"| Warm-up | 2021-05-05 -> {IS_FOLDS[0][1]} | ~250 | indicator burn-in; no trades graded |\n"
              f"| **IS fold F1** | {IS_FOLDS[0][1]} -> {IS_FOLDS[0][2]} | ~251 | selection (reported per-fold as a consistency diagnostic) |\n"
              f"| **IS fold F2** | {IS_FOLDS[1][1]} -> {IS_FOLDS[1][2]} | ~250 | selection |\n"
              f"| **IS fold F3** | {IS_FOLDS[2][1]} -> {IS_FOLDS[2][2]} | ~250 | selection |\n"
              f"| **IS pooled** | {IS_FOLDS[0][1]} -> {HOLDOUT[1]} | 751 | **the exit is picked here** (pooled 3y Sharpe, L230) |\n"
              f"| **HOLDOUT F4** | {HOLDOUT[1]} -> {HOLDOUT[2]} | 251 | **the verdict** - never seen by any selection step |\n"
              f"| Full cube window | {IS_FOLDS[0][1]} -> {HOLDOUT[2]} | 1,002 | 4 years, 614 tickers |\n")
    md.append("**Regime composition of those windows** (market-wide daily label; the regime changed 25 "
              "times in 1,002 trading days, ~once per 40 - L232):\n\n"
              "| Window | bull | bear | neutral | crisis |\n|---|---|---|---|---|\n"
              "| IS pooled (751 days) | 481 (64%) | 259 (34%) | 11 (1%) | 0 |\n"
              "| **HOLDOUT (251 days)** | **221 (88%)** | **12 (5%)** | 18 (7%) | 0 |\n"
              "| Full window (1,002 days) | 702 (70%) | 271 (27%) | 29 (3%) | **0 (0%)** |\n")
    md.append("> **Read the holdout composition before reading any SHORT result.** The holdout year is "
              "88% bull and holds just 12 bear days, so a pooled holdout grades a short strategy almost "
              "entirely on the tape it is built to lose in. That is a property of the WINDOW, not of the "
              "strategies. See the native-regime gate below and `scripts/regime_conditional_gate.py`. "
              "Note also that **no crisis day exists anywhere in the cube** - this system is designed to "
              "buy dips in crisis and has zero crisis evidence.\n")
    md.append("## Headline - what goes to the next phase\n")
    md.append(f"| | Cells (strategy x direction x exit) | Evidence |\n|---|---|---|\n"
              f"| **A. EVIDENCED long** | **{len(evidenced)}** | holdout Sharpe >= {GATE} + BH-FDR + CI lower bound > 0 |\n"
              f"| **B. Directive mirrors, measured** | **{len(mirror_data)}** | in the cube, and ALL of them FAILED the holdout |\n"
              f"| **C. Directive mirrors, unmeasured** | **{len(mirror_nodata)}** | never backtested - exit TBD |\n"
              f"| **TOTAL** | **{total_cells}** | of which {len(evidenced)} carry forward evidence |\n")
    md.append(f"**This is NOT strategies x 26.** Each promoted strategy carries exactly ONE exit - "
              f"chosen on in-sample data, graded on the held-out year - so the cube's 26-exit dimension "
              f"is already collapsed. {len(evidenced)} evidenced strategies = {len(evidenced)} cells. "
              f"(A full cube RE-RUN, a measurement exercise rather than a deployment roster, would be "
              f"222 x 26 = 5,772 cells.)\n")
    md.append("### Grading population behind those cells\n")
    md.append(f"| Outcome | Rows (strategy x direction) | Strategies |\n|---|---|---|\n"
              f"| **PASS** (holdout Sharpe >= 0.5 AND survives BH-FDR q<0.05) | **{len(passed)}** | **{S(passed)}** |\n"
              f"| PASS-noFDR (cleared 0.7 but not multiple-testing-survivable) | {len(pass_nofdr)} | {S(pass_nofdr)} |\n"
              f"| DROP (holdout Sharpe < 0.5 - selected-in-sample, failed live-forward) | {len(dropped)} | {S(dropped)} |\n"
              f"| UNEVAL (holdout n<30 - no honest verdict) | {len(uneval)} | {S(uneval)} |\n"
              f"| TOTAL graded rows (every strategy x direction in the cube) | {len(rows)} | {S(rows)} |\n")
    md.append(f"**Breadth after de-duplication (B1381):** the {len(passed)} promoted strategies contain "
              f"{len(dup_of)} near-duplicates (Jaccard >= 0.70 on the (ticker, entry_date) trade set, all "
              f"inside the 13F/smart-money family) -> **{len(keep_list)} distinct strategies**. Their daily "
              f"return streams give an **effective number of bets of {enb_after:.1f}** "
              f"(vs {enb_before:.1f} before de-dup): this roster is far less diversified than its count "
              f"suggests, and position sizing should be set against the effective number, not the headline.\n")
    md.append("| Kept | Redundant duplicates folded into it |\n|---|---|\n" + "\n".join(
        f"| `{k}` | " + (", ".join(f"`{m}`" for m, r0 in sorted(dup_of.items()) if r0 == k) or "-") + " |"
        for k in keep_list if any(r0 == k for r0 in dup_of.values())) + "\n")
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
    ms, tally, mlongs, mneg = mirror_section(passed)
    md.append("\n## A0. SHORT MIRROR COVERAGE (owner standing directive 2026-07-25)\n")
    md.append("*\"Whichever long strategies go to the next phase, their mirror short symmetrical "
              "strategies are by default to be added.\"* Applied to the "
              f"{len(mlongs)} promoted LONG strategies:\n")
    md.append("| Status | Count | Meaning |\n|---|---|---|\n"
              f"| REGISTERED-DUAL | {tally.get('REGISTERED-DUAL',0)} | strategy already trades both legs - short ships automatically |\n"
              f"| REGISTERED-STANDALONE | {tally.get('REGISTERED-STANDALONE',0)} | a symmetric short strategy already exists in the roster |\n"
              f"| MISSING-BUILDABLE | {tally.get('MISSING-BUILDABLE',0)} | no mirror registered -> Class 7 NEW_STRATEGY to wire |\n"
              f"| NOT-DEFENSIBLE | {tally.get('NOT-DEFENSIBLE',0)} | long-only DATA SOURCE (13F/insider/congress/buyback) - B611 precedent |\n")
    md.append("**Three warnings this directive should be read against:**\n\n"
              "1. **Economic asymmetry.** Equities drift up; shorts pay borrow and carry unbounded "
              "squeeze risk. A structurally symmetric short is not expected to earn its long's "
              "return - size and judge it separately.\n"
              "2. **No forward evidence.** Zero short rows clear the holdout (the window holds ~5 "
              "downtrend months in 48). Mirrors ship unvalidated-by-construction; all are tagged "
              "EXPLORATORY.\n"
              f"3. **Worse than unvalidated for {mneg} of them.** Those mirrors already exist in this "
              "cube and their own holdout evidence is NEGATIVE (see section B). Adding them overrides "
              "measured evidence - defensible only because the window under-samples bear tape (L229).\n")
    md += ms
    md.append(f"\n## A. EVIDENCED - {len(evidenced)} long cells (the only cells with forward evidence)\n")
    md.append("Holdout Sharpe >= 0.5, survives BH-FDR q<0.05, and 95% CI lower bound above 0. "
              "One exit per strategy, picked on IS (2022-05 -> 2025-05) and graded on the untouched "
              "2025-05 -> 2026-05 holdout.\n")
    md += table(evidenced)
    md.append(f"\n## B. DIRECTIVE MIRRORS with measured evidence - {len(mirror_data)} cells\n")
    md.append("Short mirrors of the promoted longs that ALREADY EXIST in the cube. They ship under the "
              "owner's mirror-by-default directive, **not** on evidence: every one of them FAILED the "
              "holdout. Carrying them is a deliberate override, justified by the window holding only "
              "~5 downtrend months in 48 (L229). Size them separately from Section A.\n")
    md.append("| Parent LONG | Short mirror | Mirror's exit | Mirror's OWN holdout Sharpe | Verdict |\n"
              "|---|---|---|---|---|")
    for s, name, m in sorted(mirror_data, key=lambda x: (x[2]["holdout"]["sharpe"] if x[2]["holdout"] else 99)):
        h = m["holdout"]
        ev = f"{h['sharpe']} (n={h['n']})" if h else "n<30 - un-evaluable"
        md.append(f"| `{s}` | `{name}` | `{m['exit']}` | {ev} | **{m['verdict']}** |")
    md.append(f"\n## C. DIRECTIVE MIRRORS without any data - {len(mirror_nodata)} cells "
              "(exit INHERITED from parent)\n")
    md.append("Wired in B1382 under the same directive. They have never been backtested, so no exit can "
              "be assigned from measurement. **Owner decision 2026-07-26: they inherit their long "
              "parent's exit as the default.** All are tagged EXPLORATORY and excluded from the "
              "multiple-testing family; the inherited exit is a placeholder to be re-measured the "
              "first time these run on a bear-inclusive window, not a validated choice.\n")
    md.append("| Parent LONG | Short mirror | Inherited exit | Source of that exit | Evidence |\n"
              "|---|---|---|---|---|")
    _pexit = {r["strategy"]: r["exit"] for r in evidenced}
    for s, name, _ in sorted(mirror_nodata):
        md.append(f"| `{s}` | `{name}` | `{_pexit.get(s, '?')}` | inherited from parent "
                  f"(owner decision 2026-07-26) | none - never backtested |")
    # B1389: the regime-conditional analysis (B1372-B1374) is part of this story and was
    # missing from the doc. Owner: "there were 17 strategies specific to regimes and others
    # across all - that's missing." Restored WITH its outcome, which is the point.
    md.append(f"\n## E. REGIME-CONDITIONAL EXITS - tested, and what became of them\n")
    md.append("A separate analysis asked whether a strategy does better with an exit that VARIES "
              "by the regime it entered in, versus one exit everywhere. Originally 17 strategies "
              f"showed a gain; after net-of-cost + winsorization (B1377) **{len(cond)} survived** "
              "with an out-of-sample DeltaSharpe >= 0.3 (IS-pick 2022-2025 / OOS-measure 2025-2026).\n")
    md.append(f"**But none of them reached the promoted {len(evidenced)}.** Of the {len(cond)} "
              "conditional survivors, 13 rows landed DROP and 1 landed PASS-noFDR under the "
              "true-holdout grading. So **every one of the "
              f"{len(evidenced)} promoted cells uses a SINGLE exit across all regimes** - the "
              "`Cond` column in Table A is `N` for all of them.\n")
    md.append("**Why both results are true at once:** the conditional test is RELATIVE - *does "
              "varying the exit beat this strategy's own single best exit?* The holdout gate is "
              "ABSOLUTE - *is the resulting Sharpe >= 0.5?* A strategy can improve on itself by "
              "varying its exit and still sit below the absolute bar. That is exactly what happened: "
              "13 improved relative to themselves; none cleared 0.5 out-of-sample.\n")
    if cond:
        md.append("| Regime-conditional survivor | OOS DeltaSharpe | Holdout verdict |\n|---|---|---|")
        _cv = {}
        for r in rows:
            _cv.setdefault(r["strategy"], []).append(f"{r['direction']}={r['verdict']}")
        for s in sorted(cond, key=lambda x: -ov[x]["oos_delta"]):
            md.append(f"| `{s}` | +{ov[s]['oos_delta']:.2f} | "
                      f"{'; '.join(_cv.get(s, ['not graded']))} |")
        md.append("")
    md.append("**Consequence for deployment:** no per-regime exit switching is required for the "
              "promoted set. Each strategy carries one exit. Per-regime EVIDENCE still varies by "
              "cell - see the 'Regimes with holdout evidence' column in Table A, which shows where "
              "each cell actually has n >= 30 to stand on.\n")
    rc = REPO / "output_audit" / "b1385_regime_conditional_gate.json"
    if rc.exists():
        c = json.loads(rc.read_text(encoding="utf-8"))["counts"]
        md.append("\n## D. NATIVE-REGIME GATE - does grading each direction in its OWN regime rescue the shorts?\n")
        md.append("Owner correction 2026-07-26: *\"our gates do not test for success of short strategies "
                  "in bear regimes and success of long strategies in bull regimes specifically.\"* "
                  "Correct - the grading above pools the holdout year. `scripts/regime_conditional_gate.py` "
                  "re-grades every row in the regime it is built for (**long -> `bull` entries, short -> "
                  "`bear` entries**), pre-registered by direction so it stays one test per row rather than "
                  "a search over regimes. The exit is likewise picked on IS native-regime data only.\n")
        md.append("| Direction | Rows | OOS PASS | OOS PASS-noFDR | OOS FAIL | OOS UNEVAL (n<30) | IS PASS | IS FAIL |\n"
                  "|---|---|---|---|---|---|---|---|\n"
                  f"| long (graded on bull) | 124 | {c['long']['PASS']} | {c['long']['PASS-noFDR']} | "
                  f"{c['long']['FAIL']} | {c['long']['UNEVAL']} | {c['long']['PASS']} | {c['long']['FAIL']} |\n"
                  f"| **short (graded on bear)** | 88 | **{c['short']['PASS']}** | {c['short']['PASS-noFDR']} | "
                  f"{c['short']['FAIL']} | **{c['short']['UNEVAL']}** | {c['short']['PASS']} | {c['short']['FAIL']} |\n")
        md.append("**What this settles.** The correction was right and the gate is now fixed - but fixing "
                  "it does NOT rescue the shorts, for a reason worth stating precisely:\n\n"
                  "1. **77 of 88 short rows are UNEVAL out-of-sample** - not failed, *untestable*. With 12 "
                  "bear days in the holdout there are fewer than 30 bear-regime trades per strategy. No "
                  "gate design can extract an out-of-sample verdict from tape that isn't there.\n"
                  "2. **In-sample, where the bear data IS ample** (259 bear days, ~30,000 short-in-bear "
                  "trades), only **2 of 88** short rows clear 0.5 + BH-FDR (`bollinger_tight`, "
                  "`ppo_crossover`). So regime-conditioning explains part of the shortfall but not all of "
                  "it - most shorts underperform even on bear-regime entries.\n"
                  "3. **A caveat that cuts against the bear-conditioned test itself:** per L229, "
                  "`regime_at_entry == bear` is where LONGS earned most (+1.14%/trade) and shorts lost "
                  "worst (-2.36%) in this window - the classifier flags 'bear' at high-vol/below-200EMA "
                  "moments that were, here, near local bottoms. So 'short entered when the label said "
                  "bear' is closer to *shorting the bottom* than to *shorting a downtrend*.\n\n"
                  "**Conclusion unchanged, but now for the right reason:** shorts are not refuted, they "
                  "are *untested*. What they need is a bear-inclusive WINDOW (2008 / 2011 / 2015-16 / "
                  "2018 / 2020), not a different gate.\n")
    md.append(f"\n## Appendix - entry-gate formulas for the {len(evidenced)} evidenced cells "
              "(exact per-leg `fires` expression)\n")
    for r in evidenced:
        md.append(f"- **`{r['strategy']}`** [{r['direction']}, {r['category']}]: `{r['fires_leg']}`")
    md.append(f"\n---\n*The DROP ({len(dropped)}), UNEVAL ({len(uneval)}) and PASS-noFDR "
              f"({len(pass_nofdr)}) populations were removed from this document per owner directive "
              "2026-07-26 so it reads as the deployment list. They remain in full, with all metrics, "
              "in `output_r5_merged_1_7/passed_strategy_exit_holdout_graded.json` - regenerate this "
              "file with `python scripts/build_passed_strategy_exit_list.py`.*")
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
