"""scripts/measure_roster_breadth_and_alpha.py (B1462) -- S6-B1461a + the corrected breadth scope.

TWO CORRECTIONS AND ONE NEW MEASUREMENT.

CORRECTION 1 -- BREADTH WAS MEASURED ON THE WRONG BOOK (owner-surfaced 2026-08-05).
B1461 reported N_eff = 2.5 over 13 cells. But 13 is the count of GRADED LONG cells; the DEPLOYABLE
book is 22 legs -- 13 long + 4 separately-registered mirror shorts + 5 dual short legs. The nine
short legs were silently excluded. Since shorts are typically negatively correlated with longs,
excluding them BIASES BREADTH DOWNWARD, so 2.5 understated the deployable book. Both scopes are
reported here so the difference is visible rather than asserted.

CORRECTION 2 -- the short legs carry no graded exit (they were never holdout-graded; they are
retained by the owner's symmetry directive). Each short leg is therefore evaluated at ITS LONG
PARENT'S chosen exit, which is the natural deployment pairing. This is a modelling choice, not a
measurement: it is stated here and in the output JSON so no reader mistakes it for evidence.

NEW MEASUREMENT (S6-B1461a) -- BETA RESIDUALISATION.
The 9-cell cluster B1461 found spans families that look unrelated by name. The hypothesis is that
they are nine ways to be long market beta in an 88%-bull holdout. Test: regress each leg's daily
P&L on SPY's daily return,

    r_cell(t) = alpha + beta * r_spy(t) + eps(t)

and re-rank on ALPHA (the intercept, annualised) plus the correlation of the RESIDUALS. If the
cluster is beta, residual correlations collapse and residual N_eff rises toward the leg count. If
the cluster survives residualisation, these are genuinely the same bet and the roster must be cut.

This is a MEASUREMENT. No gate, threshold, config or roster is modified.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

HO_START, HO_END = date(2025, 5, 5), date(2026, 5, 5)
WINSORIZE, COST_BPS, CLUSTER_RHO = 300.0, 20.0, 0.50


def breadth(panel: pd.DataFrame, label: str) -> dict:
    panel = panel.dropna(axis=1, how="all")
    C = panel.corr()
    n = C.shape[0]
    if n < 2:
        return {"label": label, "n": n, "rho_bar": None, "n_eff": float(n)}
    iu = np.triu_indices(n, k=1)
    rho = C.values[iu]
    rho_bar = float(np.nanmean(rho))
    n_eff = n / (1.0 + (n - 1) * rho_bar) if rho_bar > -1.0 / (n - 1) else float(n)
    parent = {c: c for c in C.columns}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if C.values[i, j] >= CLUSTER_RHO:
                a, b = find(C.columns[i]), find(C.columns[j])
                if a != b:
                    parent[a] = b
    groups = {}
    for c in C.columns:
        groups.setdefault(find(c), []).append(c)
    clusters = sorted((sorted(v) for v in groups.values()), key=len, reverse=True)
    print(f"  {label:<34} n={n:<3} rho_bar={rho_bar:>6.3f}  N_eff={n_eff:>5.1f}  "
          f"clusters={len(clusters):<3} largest={len(clusters[0])}")
    return {"label": label, "n": n, "rho_bar": rho_bar, "n_eff": n_eff,
            "clusters": clusters, "corr": C.round(3).to_dict()}


def main() -> int:
    rj = json.loads((REPO / "output_audit" / "b1453_phase_1b_roster.json").read_text("utf-8"))
    roster = rj["roster"]

    # ---- assemble the 22 deployable legs -----------------------------------
    legs = []                                   # (label, strategy, direction, exit)
    for r in roster:
        legs.append((f"{r['strategy']}|L", r["strategy"], "long", r["exit"]))
    for r in roster:
        if r["mirror_status"] == "DUAL-SELF":
            legs.append((f"{r['strategy']}|S", r["strategy"], "short", r["exit"]))
        elif r["mirror_status"] == "REGISTERED" and r["mirror"]:
            legs.append((f"{r['mirror']}|S", r["mirror"], "short", r["exit"]))
    print("=" * 100)
    print("ROSTER BREADTH + BETA RESIDUALISATION (B1462 / S6-B1461a) -- measurement only")
    print("=" * 100)
    print(f"  deployable legs assembled: {len(legs)}  "
          f"(13 graded long + 5 dual short + 4 mirror short)")
    print("  short legs evaluated at their LONG PARENT'S exit -- a modelling choice, not evidence\n")

    df = pd.read_csv(REPO / "output_r5_merged_1_7" / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date", "pnl_pct"],
                     low_memory=False,
                     dtype={"strategy": "category", "direction": "category",
                            "exit_method": "category", "pnl_pct": "float32"})
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df = df[(df.entry_date >= pd.Timestamp(HO_START)) & (df.entry_date < pd.Timestamp(HO_END))]
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0

    series, missing = {}, []
    for label, s, d, e in legs:
        g = df[(df.strategy == s) & (df.direction == d) & (df.exit_method == e)]
        if g.empty:
            missing.append(label)
            continue
        # MEAN per trade, not SUM (L300): a summed daily series is trade VOLUME, not
        # return, and regressing it on SPY percent returns produced betas of 6.2 -- a
        # specification failure, not a finding. Mean is dimensionally consistent.
        series[label] = g.groupby("entry_date")["pnl_pct"].mean()
    if missing:
        print(f"  [WARN] {len(missing)} leg(s) have NO holdout trades at the parent exit "
              f"-> excluded, cannot be measured: {', '.join(missing)}\n")

    panel = pd.DataFrame(series).sort_index()   # NaN = no trade that day, not a zero return
    long_cols = [c for c in panel.columns if c.endswith("|L")]

    print("  RAW P&L breadth")
    res = {"long_only": breadth(panel[long_cols], "LONG ONLY (what B1461 measured)"),
           "deployable": breadth(panel, "DEPLOYABLE BOOK (all legs)")}

    # ---- SPY benchmark ------------------------------------------------------
    spy_p = REPO / "backtest" / "data" / "cache" / "ohlcv" / "SPY.parquet"
    if not spy_p.exists():
        print(f"\n  [HALT] SPY cache absent at {spy_p} - cannot residualise. "
              f"Breadth results above stand; S6-B1461a NOT completed.")
        (REPO / "output_audit" / "b1462_breadth_alpha.json").write_text(
            json.dumps({"MEASUREMENT_ONLY": True, "breadth": res,
                        "residualisation": "BLOCKED - SPY cache absent"},
                       indent=2, default=str), encoding="utf-8")
        return 0
    spy = pd.read_parquet(spy_p)
    dcol = "date" if "date" in spy.columns else spy.columns[0]
    ccol = "close" if "close" in spy.columns else "Close"
    spy[dcol] = pd.to_datetime(spy[dcol])
    spy = spy.set_index(dcol)[ccol].sort_index()
    mkt = (spy.pct_change() * 100.0).reindex(panel.index)

    print(f"\n  BETA RESIDUALISATION vs SPY  ({len(mkt)} aligned days)")
    print(f"  {'leg':<46}{'alpha/day':>11}{'beta':>8}{'R2':>7}")
    resid, rows = {}, []
    for c in panel.columns:
        both = pd.concat([panel[c], mkt], axis=1).dropna()
        if len(both) < 30:
            continue
        y = both.iloc[:, 0].values
        X = np.column_stack([np.ones(len(both)), both.iloc[:, 1].values])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        e = y - X @ coef
        ss_t = float(((y - y.mean()) ** 2).sum())
        r2 = 1.0 - float((e ** 2).sum()) / ss_t if ss_t > 0 else 0.0
        resid[c] = pd.Series(e, index=both.index)
        rows.append({"leg": c, "alpha": float(coef[0]), "beta": float(coef[1]), "r2": r2})
    for r in sorted(rows, key=lambda x: -x["alpha"])[:24]:
        print(f"  {r['leg']:<46}{r['alpha']:>11.4f}{r['beta']:>8.3f}{r['r2']:>7.3f}")

    rp = pd.DataFrame(resid)
    print("\n  RESIDUAL breadth (beta removed) -- the S6-B1461a verdict")
    res["long_resid"] = breadth(rp[long_cols], "LONG ONLY, residual")
    res["deployable_resid"] = breadth(rp, "DEPLOYABLE BOOK, residual")

    out = REPO / "output_audit" / "b1462_breadth_alpha.json"
    out.write_text(json.dumps({"MEASUREMENT_ONLY": True,
                               "legs": [l[0] for l in legs], "missing_legs": missing,
                               "breadth": res, "regression": rows},
                              indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
