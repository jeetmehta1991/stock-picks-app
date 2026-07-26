"""scripts/regime_conditional_gate.py (B1385) -- grade each strategy in the regime it is
BUILT FOR, not on a pooled window.

Owner correction 2026-07-26: "our gates do not test for success of short strategies in bear
regimes and success of long strategies in bull regimes specifically."

Why this matters, measured: the R5 holdout year (2025-05 -> 2026-05) is **88% bull days /
5% bear days** (12 of 251), while the IS window is 34% bear. A pooled holdout therefore
grades a SHORT strategy almost entirely on the tape it is designed to lose in - which is
exactly what produced "zero shorts pass" in B1378-B1381. That was a property of the gate,
not necessarily of the strategies.

The gate here is PRE-REGISTERED BY DIRECTION, so it stays one test per row rather than a
search over regimes (which would need its own multiple-testing correction):
    long  -> graded on `regime_at_entry == bull`
    short -> graded on `regime_at_entry == bear`
The exit is likewise picked on IS *native-regime* data only.

Two verdicts are reported per row, and they are NOT interchangeable:
  OOS_*  native-regime HOLDOUT test - genuine out-of-sample, but bear-starved so most
         shorts land UNEVAL (n < 30).
  IS_*   native-regime IN-SAMPLE test - statistically powered (30k+ short-in-bear trades)
         but in-sample; it answers "does a bear-regime edge exist at all", NOT "will it
         persist". Never present IS_PASS as validation.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from walk_forward_r5_cells import _sharpe, bh_fdr  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
CUBE = REPO / "output_r5_merged_1_7"
IS = (date(2022, 5, 5), date(2025, 5, 5))
HO = (date(2025, 5, 5), date(2026, 5, 5))
MIN_N = 30
GATE = 0.5
WINSORIZE, COST_BPS = 300.0, 20.0
NATIVE = {"long": "bull", "short": "bear"}


def main() -> int:
    df = pd.read_csv(CUBE / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date",
                              "regime_at_entry", "pnl_pct", "hold_days"], low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
    print(f"[INFO] {len(df):,} trades | winsorize +/-{WINSORIZE} cost {COST_BPS}bps")

    rows = []
    for (s, d), sd in df.groupby(["strategy", "direction"]):
        nat = NATIVE.get(str(d).lower())
        if nat is None:
            continue
        sd = sd[sd.regime_at_entry == nat]
        if sd.empty:
            continue
        best = None
        for ex, g in sd.groupby("exit_method"):
            gi = g[(g.entry_date >= IS[0]) & (g.entry_date < IS[1])]
            m = _sharpe(gi.pnl_pct.values, gi.hold_days.values)
            if m and (best is None or m["sharpe"] > best[1]["sharpe"]):
                gh = g[(g.entry_date >= HO[0]) & (g.entry_date < HO[1])]
                best = (ex, m, _sharpe(gh.pnl_pct.values, gh.hold_days.values))
        if best is None:
            continue
        ex, ism, hom = best
        rows.append({"strategy": s, "direction": d, "native_regime": nat, "exit": ex,
                     "is_native": ism, "ho_native": hom})

    ev = [r for r in rows if r["ho_native"]]
    rej, _ = bh_fdr([r["ho_native"]["p"] for r in ev], q=0.05)
    for r, ok in zip(ev, rej):
        r["bh_oos"] = bool(ok)
    rej2, _ = bh_fdr([r["is_native"]["p"] for r in rows], q=0.05)
    for r, ok in zip(rows, rej2):
        r["bh_is"] = bool(ok)
    for r in rows:
        h, i = r["ho_native"], r["is_native"]
        r.setdefault("bh_oos", False)
        r["oos"] = ("UNEVAL" if not h else
                    "PASS" if (h["sharpe"] >= GATE and r["bh_oos"]) else
                    "PASS-noFDR" if h["sharpe"] >= GATE else "FAIL")
        r["is_verdict"] = "PASS" if (i["sharpe"] >= GATE and r["bh_is"]) else \
                          "PASS-noFDR" if i["sharpe"] >= GATE else "FAIL"

    def tab(dirn):
        rs = [r for r in rows if r["direction"] == dirn]
        c = lambda k, v: sum(1 for r in rs if r[k] == v)  # noqa: E731
        return rs, c

    print("\n" + "=" * 92)
    print("NATIVE-REGIME GATE  (long graded on BULL entries, short graded on BEAR entries)")
    print("=" * 92)
    print(f"  {'direction':<10}{'rows':>6}{'OOS PASS':>10}{'OOS noFDR':>11}{'OOS FAIL':>10}"
          f"{'OOS UNEVAL':>12}{'IS PASS':>9}{'IS noFDR':>10}{'IS FAIL':>9}")
    for d in ("long", "short"):
        rs, c = tab(d)
        print(f"  {d:<10}{len(rs):>6}{c('oos','PASS'):>10}{c('oos','PASS-noFDR'):>11}"
              f"{c('oos','FAIL'):>10}{c('oos','UNEVAL'):>12}"
              f"{c('is_verdict','PASS'):>9}{c('is_verdict','PASS-noFDR'):>10}{c('is_verdict','FAIL'):>9}")

    for d in ("short", "long"):
        rs = [r for r in rows if r["direction"] == d and r["is_verdict"] == "PASS"]
        rs.sort(key=lambda r: -r["is_native"]["sharpe"])
        print(f"\n=== {d.upper()}: top native-regime IS passers (IN-SAMPLE - powered, NOT validation) ===")
        print(f"  {'strategy':<44}{'exit':<22}{'IS sharpe':>10}{'n':>7}{'OOS':>12}")
        for r in rs[:15]:
            i, h = r["is_native"], r["ho_native"]
            print(f"  {r['strategy']:<44}{r['exit']:<22}{i['sharpe']:>10}{i['n']:>7}"
                  f"{(str(h['sharpe']) + ' n=' + str(h['n'])) if h else 'n<30':>12}")
        print(f"  ({len(rs)} total {d} rows clear the native-regime IS gate + BH-FDR)")

    out = REPO / "output_audit" / "b1385_regime_conditional_gate.json"
    out.write_text(json.dumps({
        "gate": GATE, "min_n": MIN_N, "native_map": NATIVE,
        "holdout_regime_days": {"bear": 12, "bull": 221, "neutral": 18, "total": 251},
        "counts": {d: {k: sum(1 for r in rows if r["direction"] == d and r[f] == k)
                       for f, ks in (("oos", ("PASS", "PASS-noFDR", "FAIL", "UNEVAL")),
                                     ("is_verdict", ("PASS", "PASS-noFDR", "FAIL")))
                       for k in ks}
                   for d in ("long", "short")},
        "rows": rows}, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
