"""S6-B1248-SHORT-REGIME-AFFINITY: how SHORT trades did in each entry regime.

The ticket proposed a regime-affinity policy for the standalone shorts that
fire in every regime; the textbook form is 'shorts only in bear (and neutral)
regimes'. Before any policy is designed this measures what the shorts did by
regime, on the R5 merged cube.

METHOD. Every SHORT-direction trade in output_r5_merged_1_7/trade_exit_detail.csv
(pure shorts and the short legs of dual strategies), on the NET basis
(roster_core.net_pnl). Per strategy, ONE exit - the one with the best mean
net pnl in-sample, the funnel's own selector - so 24 exits are not pooled;
then trades, mean net pnl and profit factor per regime_at_entry (the engine's
classification at entry) at that exit, over the IN-SAMPLE window only (entry
before roster_core.HO_START). The holdout is never read: under the owner's
2026-09-30 rulings a holdout read needs the owner's own word, and a regime
policy fitted on it would spend it. DESCRIPTIVE: no gate is graded. The sign
of pnl_pct for shorts is checked on the data each run (it must track entry
minus exit) and the run refuses otherwise.

    python scripts/short_regime_affinity_census.py [--out PATH]
writes output_audit/b3139_short_regime_affinity.json
"""
import json
import sys
from pathlib import Path

import pandas as pd


def _root() -> Path:
    """The repo root, resolved by MARKER (L846): the script's own parent
    tree when installed in scripts/, else the working directory - refused
    unless backtest/signals/screener.py is there."""
    for c in (Path(__file__).resolve().parents[1], Path.cwd()):
        if (c / "backtest" / "signals" / "screener.py").is_file():
            return c
    raise SystemExit("cannot find the repo root (backtest/signals/screener.py) - refusing")


ROOT = _root()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
OUT = ROOT / "output_audit" / "b3139_short_regime_affinity.json"


def pf(x):
    w, loss = float(x[x > 0].sum()), float(-x[x <= 0].sum())
    return None if loss == 0 else round(w / loss, 3)


def census(sh: pd.DataFrame, ho_start) -> tuple:
    """(rows, summary) over the IN-SAMPLE rows of a short-trade frame with
    columns strategy, exit_method, net, entry_date (datetime) and
    regime_at_entry. Rows entered on or after ho_start are dropped FIRST, so
    nothing below can see the holdout - test_b1248_short_regime_census_never_
    reads_the_holdout feeds it holdout rows and asserts they change nothing."""
    sh = sh[sh["entry_date"] < pd.Timestamp(ho_start)]
    rows = []
    for s, gis in sh.groupby("strategy"):
        best = gis.groupby("exit_method")["net"].mean().sort_values(ascending=False).index[0]
        gb = gis[gis["exit_method"] == best]
        reg = {}
        for r, gr in gb.groupby(gb["regime_at_entry"].astype(str)):
            reg[r] = {"n": int(len(gr)), "mean_net": round(float(gr["net"].mean()), 4),
                      "pf": pf(gr["net"])}
        rows.append({"strategy": s, "best_exit_in_sample": best, "trades": int(len(gb)),
                     "mean_net": round(float(gb["net"].mean()), 4), "pf": pf(gb["net"]),
                     "by_regime": reg})
    both = [r for r in rows if "bear" in r["by_regime"] and "bull" in r["by_regime"]]
    big = [r for r in both if r["by_regime"]["bear"]["n"] >= 30
           and r["by_regime"]["bull"]["n"] >= 30]

    def wmean(key):
        n = sum(r["by_regime"][key]["n"] for r in both)
        if not n:
            return 0, None
        m = sum(r["by_regime"][key]["n"] * r["by_regime"][key]["mean_net"] for r in both) / n
        return n, round(m, 3)

    nb, mb = wmean("bear")
    nu, mu = wmean("bull")
    below = lambda rs: sum(r["by_regime"]["bear"]["mean_net"]  # noqa: E731
                           < r["by_regime"]["bull"]["mean_net"] for r in rs)
    summary = {
        "short_strategies_measured": len(rows),
        "with_bear_and_bull_trades": len(both),
        "bear_mean_below_bull_mean": below(both),
        "bear_mean_negative": sum(r["by_regime"]["bear"]["mean_net"] < 0 for r in both),
        "bull_mean_negative": sum(r["by_regime"]["bull"]["mean_net"] < 0 for r in both),
        "with_30_plus_trades_in_each": len(big),
        "of_those_bear_below_bull": below(big),
        "trade_weighted_mean_net_bear": mb, "bear_trades": nb,
        "trade_weighted_mean_net_bull": mu, "bull_trades": nu,
    }
    return rows, summary


def main() -> int:
    global OUT
    if "--out" in sys.argv:
        OUT = Path(sys.argv[sys.argv.index("--out") + 1])
    cols = ["strategy", "direction", "exit_method", "pnl_pct", "entry_date",
            "regime_at_entry", "entry_price", "exit_price"]
    df = pd.read_csv(CUBE, usecols=cols, low_memory=False)
    sh = df[df["direction"].astype(str).str.lower() == "short"].copy()
    chk = sh.dropna(subset=["entry_price", "exit_price", "pnl_pct"]).head(5000)
    signed = (chk["entry_price"] - chk["exit_price"]) / chk["entry_price"] * 100
    sign_corr = float(chk["pnl_pct"].corr(signed))
    if not sign_corr > 0.99:
        raise SystemExit(f"short pnl_pct does not track entry minus exit (corr {sign_corr:.4f}) "
                         f"- the regime census would read the sign backwards; refusing")
    sh["net"] = rc.net_pnl(pd.to_numeric(sh["pnl_pct"], errors="coerce"))
    sh["entry_date"] = pd.to_datetime(sh["entry_date"].astype(str), errors="coerce")
    rows, summary = census(sh, rc.HO_START)
    summary["short_pnl_sign_check_corr"] = round(sign_corr, 4)
    OUT.write_bytes((json.dumps({"generator": "scripts/short_regime_affinity_census.py",
                                 "cube": CUBE.relative_to(ROOT).as_posix(),
                                 "basis": "NET (roster_core.net_pnl)",
                                 "window": f"in-sample, entry before {rc.HO_START}",
                                 "summary": summary, "rows": rows}, indent=1)
                     + "\n").encode("utf-8"))
    for k, v in summary.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
