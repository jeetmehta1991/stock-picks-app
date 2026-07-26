"""scripts/r5_gate_ladder_analysis.py (B1379) - the measurement behind the B1379 council.

PART 1  gate A/B test: does an R:R>=1.5 + WR>=50pct acceptance gate select rows that
        survive a TRUE HOLDOUT better than the Sharpe>=0.7 gate? Each gate is applied
        IS (2022-05->2025-05) to PICK the exit, then graded on the untouched holdout
        year (2025-05->2026-05), and compared to the base rate of rows it REJECTED --
        because any looser bar mechanically passes more rows; only lift is evidence.

PART 2  short-side diagnosis (broken vs window-starved) + a THRESHOLD LADDER showing
        how far the bar must drop to reach a 40-50 strategy roster.

Run: python scripts/r5_gate_ladder_analysis.py   (reads output_r5_merged_1_7/trade_exit_detail.csv)
"""
import sys, json
from pathlib import Path
from datetime import date
from collections import Counter
sys.path.insert(0, "scripts")
import numpy as np
import pandas as pd
from walk_forward_r5_cells import _sharpe, bh_fdr

C = Path("output_r5_merged_1_7")
IS = (date(2022, 5, 5), date(2025, 5, 5))
HO = (date(2025, 5, 5), date(2026, 5, 5))
MIN_N = 30

df = pd.read_csv(C / "trade_exit_detail.csv",
                 usecols=["strategy", "direction", "exit_method", "entry_date", "pnl_pct", "hold_days"],
                 low_memory=False)
df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
df["pnl_pct"] = df["pnl_pct"].clip(-300, 300) - 0.20
print(f"[INFO] {len(df):,} trades | exits available: {sorted(df.exit_method.unique())}\n")


def stats(a, hold):
    n = len(a)
    if n < MIN_N:
        return None
    s = _sharpe(a, hold)
    wins, losses = a[a > 0], a[a <= 0]
    payoff = float(wins.mean() / abs(losses.mean())) if len(losses) and losses.mean() != 0 else float("inf")
    return {"n": n, "sharpe": s["sharpe"], "wr": s["wr"], "payoff": round(payoff, 3),
            "p": s["p"], "ci_lo": s["ci_lo"], "exp": round(float(a.mean()), 4)}


def g_sharpe(m):  return m and m["sharpe"] >= 0.7
def g_rr(m):      return m and m["wr"] >= 0.50 and m["payoff"] >= 1.5
def g_rr55(m):    return m and m["wr"] >= 0.55 and m["payoff"] >= 1.5


rows = []
for (s, d), sd in df.groupby(["strategy", "direction"]):
    cands = []
    for ex, g in sd.groupby("exit_method"):
        i = g[(g.entry_date >= IS[0]) & (g.entry_date < IS[1])]
        h = g[(g.entry_date >= HO[0]) & (g.entry_date < HO[1])]
        mi = stats(i.pnl_pct.values, i.hold_days.values)
        mh = stats(h.pnl_pct.values, h.hold_days.values)
        if mi is None:
            continue
        cands.append({"exit": ex, "is": mi, "ho": mh})
    if not cands:
        continue
    row = {"strategy": s, "direction": d, "cands": cands}
    # pick per gate, on IS only
    for gname, gf in [("sharpe", g_sharpe), ("rr", g_rr), ("rr55", g_rr55)]:
        elig = [c for c in cands if gf(c["is"])]
        # among IS-eligible, take the highest IS expectancy; if none eligible, row fails this gate IS-side
        row[f"pick_{gname}"] = max(elig, key=lambda c: c["is"]["exp"]) if elig else None
    rows.append(row)

print(f"[INFO] {len(rows)} (strategy x direction) rows with an evaluable IS window\n")
print("=" * 100)
print("Q: does an R:R>=1.5 + WR>=50% gate produce MORE deployable strategies than Sharpe>=0.7?")
print("   (gate applied IS to PICK the exit, then graded on the untouched holdout year)")
print("=" * 100)

summary = {}
for gname, gf, label in [("sharpe", g_sharpe, "Sharpe >= 0.7 (current)"),
                         ("rr", g_rr, "WR>=50% AND payoff>=1.5 (owner proposal)"),
                         ("rr55", g_rr55, "WR>=55% AND payoff>=1.5 (repo criterion 1)")]:
    picked = [r for r in rows if r[f"pick_{gname}"]]
    ev = [r for r in picked if r[f"pick_{gname}"]["ho"]]
    held = [r for r in ev if gf(r[f"pick_{gname}"]["ho"])]        # gate holds in holdout
    rej = [r for r in rows if not r[f"pick_{gname}"] ]
    # base rate: rows the gate REJECTED on IS -- how often would they have held in holdout anyway?
    rej_ev, rej_hit = 0, 0
    for r in rej:
        best = max(r["cands"], key=lambda c: c["is"]["exp"])
        if best["ho"]:
            rej_ev += 1
            if gf(best["ho"]):
                rej_hit += 1
    ps = [r[f"pick_{gname}"]["ho"]["p"] for r in held]
    bh, thr = bh_fdr(ps, q=0.05)
    fdr_ok = [r for r, ok in zip(held, bh) if ok]
    dl = Counter(r["direction"] for r in held)
    dlf = Counter(r["direction"] for r in fdr_ok)
    hit = len(held) / len(ev) if ev else 0
    base = rej_hit / rej_ev if rej_ev else 0
    summary[gname] = {"label": label, "is_selected_rows": len(picked), "holdout_evaluable": len(ev),
                      "held_rows": len(held), "held_strategies": len({r["strategy"] for r in held}),
                      "held_long": dl.get("long", 0), "held_short": dl.get("short", 0),
                      "fdr_rows": len(fdr_ok), "fdr_strategies": len({r["strategy"] for r in fdr_ok}),
                      "fdr_long": dlf.get("long", 0), "fdr_short": dlf.get("short", 0),
                      "holdout_hit_rate": round(hit, 4), "rejected_base_rate": round(base, 4),
                      "lift": round(hit / base, 2) if base else None}
    print(f"\n--- {label} ---")
    print(f"  IS-selected rows           : {len(picked)}")
    print(f"  ...holdout-evaluable       : {len(ev)}")
    print(f"  ...GATE HELD in holdout    : {len(held)} rows / {len({r['strategy'] for r in held})} strategies"
          f"   [long {dl.get('long',0)} / short {dl.get('short',0)}]")
    print(f"  ...AND survives BH-FDR     : {len(fdr_ok)} rows / {len({r['strategy'] for r in fdr_ok})} strategies"
          f"   [long {dlf.get('long',0)} / short {dlf.get('short',0)}]")
    print(f"  PREDICTIVE POWER: gate-selected hold {hit:.1%} vs rejected-rows {base:.1%}"
          f"  -> lift {summary[gname]['lift']}x")

print("\n" + "=" * 100)
print("SHORT-SIDE DIAGNOSIS: why do 0 shorts survive?")
print("=" * 100)
for d in ["long", "short"]:
    sub = [r for r in rows if r["direction"] == d]
    hos = [c["ho"] for r in sub for c in r["cands"] if c["ho"]]
    if not hos:
        continue
    sh = np.array([m["sharpe"] for m in hos]); wr = np.array([m["wr"] for m in hos])
    po = np.array([m["payoff"] for m in hos if np.isfinite(m["payoff"])])
    ex = np.array([m["exp"] for m in hos])
    print(f"  {d:>5}: rows={len(sub):>4} cells={len(hos):>5} | holdout median Sharpe={np.median(sh):+.3f} "
          f"medWR={np.median(wr):.3f} medPayoff={np.median(po):.2f} medExpectancy={np.median(ex):+.3f}% "
          f"| frac Sharpe>=0.7={np.mean(sh>=0.7):.1%} | frac WR>=.5&payoff>=1.5={np.mean([(m['wr']>=.5 and m['payoff']>=1.5) for m in hos]):.1%}")
    # IS side for contrast
    iss = [c["is"] for r in sub for c in r["cands"]]
    sh2 = np.array([m["sharpe"] for m in iss])
    print(f"         IS(2022-25) median Sharpe={np.median(sh2):+.3f} | frac IS Sharpe>=0.7={np.mean(sh2>=0.7):.1%}")

print("\n" + "=" * 100)
print("WHICH EXIT maximises passing rows under each gate (holdout)?")
print("=" * 100)
for gname, gf in [("sharpe", g_sharpe), ("rr", g_rr)]:
    cnt = Counter()
    for r in rows:
        for c in r["cands"]:
            if c["ho"] and gf(c["ho"]):
                cnt[c["exit"]] += 1
    print(f"  gate={gname}: " + ", ".join(f"{k}={v}" for k, v in cnt.most_common(8)))

Path("output_audit").mkdir(exist_ok=True)
json.dump(summary, open("output_audit/b1379_gate_ab_test.json", "w"), indent=2)
print("\n[OK] wrote output_audit/b1379_gate_ab_test.json")

# ============================== PART 2 ==============================
import sys
from pathlib import Path
from datetime import date
import numpy as np
import pandas as pd
sys.path.insert(0, "scripts")
from walk_forward_r5_cells import _sharpe, bh_fdr

C = Path("output_r5_merged_1_7")
FOLDS = [("F1 22-23 BEARish", date(2022, 5, 5), date(2023, 5, 5)),
         ("F2 23-24", date(2023, 5, 5), date(2024, 5, 5)),
         ("F3 24-25", date(2024, 5, 5), date(2025, 5, 5)),
         ("F4 25-26 HOLDOUT", date(2025, 5, 5), date(2026, 5, 5))]
IS = (date(2022, 5, 5), date(2025, 5, 5)); HO = (date(2025, 5, 5), date(2026, 5, 5))

df = pd.read_csv(C / "trade_exit_detail.csv",
                 usecols=["strategy", "direction", "exit_method", "entry_date", "pnl_pct", "hold_days"],
                 low_memory=False)
df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
df["pnl_pct"] = df["pnl_pct"].clip(-300, 300) - 0.20

print("=" * 96)
print("1a. LONG vs SHORT aggregate by fold  (if shorts lose in the BEAR fold too -> suspect mechanics)")
print("=" * 96)
for nm, lo, hi in FOLDS:
    f = df[(df.entry_date >= lo) & (df.entry_date < hi)]
    out = []
    for d in ["long", "short"]:
        g = f[f.direction == d]
        if not len(g):
            continue
        out.append(f"{d}: n={len(g):>7,} meanPnl={g.pnl_pct.mean():+.3f}% WR={(g.pnl_pct>0).mean():.3f} "
                   f"medPnl={g.pnl_pct.median():+.3f}%")
    print(f"  {nm:<18} " + " | ".join(out))

print("\n" + "=" * 96)
print("1b. SHORT expectancy by EXIT METHOD (uniform failure across all 26 -> entry-side or systemic;")
print("    failure concentrated in trailing/stop exits -> exit-side mechanics)")
print("=" * 96)
sh = df[df.direction == "short"]
rowsx = []
for ex, g in sh.groupby("exit_method"):
    rowsx.append((ex, len(g), g.pnl_pct.mean(), (g.pnl_pct > 0).mean(), g.pnl_pct.median()))
for ex, n, m, w, md in sorted(rowsx, key=lambda r: -r[2]):
    print(f"  {ex:<26} n={n:>7,}  meanPnl={m:+.3f}%  WR={w:.3f}  medPnl={md:+.3f}%")
lg = df[df.direction == "long"]
print(f"  {'--- LONG (reference) ---':<26} n={len(lg):>7,}  meanPnl={lg.pnl_pct.mean():+.3f}%  "
      f"WR={(lg.pnl_pct>0).mean():.3f}  medPnl={lg.pnl_pct.median():+.3f}%")

print("\n" + "=" * 96)
print("1c. BEST short cells that exist at all (IS 2022-25, n>=30) - is there ANY short edge?")
print("=" * 96)
best = []
for (s, ex), g in sh.groupby(["strategy", "exit_method"]):
    i = g[(g.entry_date >= IS[0]) & (g.entry_date < IS[1])]
    if len(i) < 30:
        continue
    st = _sharpe(i.pnl_pct.values, i.hold_days.values)
    if st:
        best.append((st["sharpe"], s, ex, st["n"], st["wr"]))
best.sort(reverse=True)
print(f"  {len(best)} short cells evaluable IS; top 8 by IS Sharpe:")
for sh_, s, ex, n, w in best[:8]:
    print(f"    IS Sharpe={sh_:>6}  {s:<40} {ex:<22} n={n:>5} wr={w}")
print(f"  short cells with IS Sharpe > 0 : {sum(1 for b in best if b[0] > 0)}/{len(best)}")

print("\n" + "=" * 96)
print("2. THRESHOLD LADDER on the true holdout (exit picked on IS by mean IS Sharpe)")
print("   how far must the bar drop to reach 40-50 strategies?")
print("=" * 96)
rows = []
for (s, d), sd in df.groupby(["strategy", "direction"]):
    bestc = None
    for ex, g in sd.groupby("exit_method"):
        i = g[(g.entry_date >= IS[0]) & (g.entry_date < IS[1])]
        mi = _sharpe(i.pnl_pct.values, i.hold_days.values)
        if not mi:
            continue
        if bestc is None or mi["sharpe"] > bestc[0]:
            h = g[(g.entry_date >= HO[0]) & (g.entry_date < HO[1])]
            bestc = (mi["sharpe"], ex, _sharpe(h.pnl_pct.values, h.hold_days.values))
    if bestc and bestc[2]:
        rows.append({"strategy": s, "direction": d, "exit": bestc[1], "ho": bestc[2]})
print(f"  {len(rows)} rows with BOTH an evaluable IS pick and an evaluable holdout\n")
print(f"  {'bar':<34}{'rows':>6}{'strats':>8}{'long':>6}{'short':>7}{'+FDR rows':>11}{'FDR strats':>12}")
for label, f in [("holdout Sharpe >= 0.7 (current)", lambda m: m["sharpe"] >= 0.7),
                 ("holdout Sharpe >= 0.5", lambda m: m["sharpe"] >= 0.5),
                 ("holdout Sharpe >= 0.3", lambda m: m["sharpe"] >= 0.3),
                 ("holdout Sharpe >= 0.0", lambda m: m["sharpe"] >= 0.0),
                 ("expectancy > 0 (any Sharpe)", lambda m: m["sharpe"] > 0)]:
    k = [r for r in rows if f(r["ho"])]
    ps = [r["ho"]["p"] for r in k]
    bh, _ = bh_fdr(ps, q=0.05)
    fk = [r for r, ok in zip(k, bh) if ok]
    nl = sum(1 for r in k if r["direction"] == "long"); ns = sum(1 for r in k if r["direction"] == "short")
    print(f"  {label:<34}{len(k):>6}{len({r['strategy'] for r in k}):>8}{nl:>6}{ns:>7}"
          f"{len(fk):>11}{len({r['strategy'] for r in fk}):>12}")
print("\n  (FDR = Benjamini-Hochberg q<0.05 within that bar's passing set)")