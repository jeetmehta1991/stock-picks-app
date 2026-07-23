"""scripts/build_r5_dashboard.py (B1342, Council 369) -- standalone R5 batch
dashboard. Reads output_batches/batch_*/ (committed per-batch outputs) and
emits a self-contained dashboard_r5/index.html: progress vs the 614 full-PIT
T1a target, strategy x exit cube heatmap, per-strategy leaderboard, exit-method
ranking, and silent-strategy tracker. Regenerate after each batch merges.

Cube pooling across ticker-disjoint batches is trade-weighted (approximate,
for VISUALIZATION); the authoritative verdict cube comes from
merge_batch_outputs (exact recompute on pooled trades).

Usage: python scripts/build_r5_dashboard.py [--target 614]
"""
from __future__ import annotations

import argparse
import glob
import html
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "dashboard_r5" / "index.html"


def load_batches():
    batches = []
    for d in sorted(glob.glob(str(REPO / "output_batches" / "batch_*"))):
        p = Path(d)
        sp = p / "summary.json"
        cp = p / "exit_strategy_comparison.csv"
        tp = p / "trade_log.parquet"
        if not cp.exists():
            continue
        rec = {"dir": p.name}
        if sp.exists():
            rec["summary"] = json.loads(sp.read_text(encoding="utf-8"))
        rec["cube"] = pd.read_csv(cp)
        if tp.exists():
            rec["trades"] = pd.read_parquet(tp)
        batches.append(rec)
    return batches


def pool_cube(batches):
    """Trade-weighted pool of per-batch cubes (viz-grade)."""
    frames = [b["cube"].assign(_b=b["dir"]) for b in batches]
    allc = pd.concat(frames, ignore_index=True)
    g = allc.groupby(["strategy", "exit_method"])
    def wavg(x, w):
        wt = allc.loc[x.index, "trades"]
        return (x * wt).sum() / wt.sum() if wt.sum() else 0.0
    out = g.apply(lambda df: pd.Series({
        "trades": int(df["trades"].sum()),
        "win_rate": (df["win_rate"] * df["trades"]).sum() / max(df["trades"].sum(), 1),
        "profit_factor": (df["profit_factor"] * df["trades"]).sum() / max(df["trades"].sum(), 1),
        "avg_pnl_pct": (df["avg_pnl_pct"] * df["trades"]).sum() / max(df["trades"].sum(), 1),
        "total_roi_pct": df["total_roi_pct"].sum(),
        "composite_score": (df["composite_score"] * df["trades"]).sum() / max(df["trades"].sum(), 1),
    })).reset_index()
    return out


def heat_color(v, lo, hi):
    if v is None or pd.isna(v):
        return "#2a2a2a"
    t = max(0.0, min(1.0, (v - lo) / (hi - lo) if hi > lo else 0.5))
    # red -> amber -> green
    if t < 0.5:
        r, g, b = 200, int(80 + 300 * t), 60
    else:
        r, g, b = int(200 - 320 * (t - 0.5)), 190, 70
    return f"rgb({max(0,min(255,r))},{max(0,min(255,g))},{max(0,min(255,b))})"


def build(target: int) -> str:
    batches = load_batches()
    if not batches:
        return "<p>No batches in output_batches/ yet.</p>"

    # KPIs from pooled trades
    all_trades = pd.concat([b["trades"] for b in batches if "trades" in b], ignore_index=True) \
        if any("trades" in b for b in batches) else pd.DataFrame()
    tested = sorted(set().union(*[set(b["summary"]["tickers_requested"])
                                  for b in batches if "summary" in b])) if batches else []
    n_tested = len(tested)
    n_trades = len(all_trades)
    n_strat_traded = all_trades["strategy"].nunique() if len(all_trades) else 0

    from backtest.signals.screener import ALL_STRATEGIES
    n_registered = len(ALL_STRATEGIES)
    n_silent = n_registered - n_strat_traded

    cube = pool_cube(batches)
    # leaderboard: best exit per strategy by composite_score
    best = cube.sort_values("composite_score", ascending=False).drop_duplicates("strategy")
    best = best.sort_values("composite_score", ascending=False)
    # exit-method ranking
    exitrank = cube.groupby("exit_method").agg(
        mean_score=("composite_score", "mean"), cells=("strategy", "count"),
        mean_wr=("win_rate", "mean")).reset_index().sort_values("mean_score", ascending=False)

    pct = 100.0 * n_tested / target
    kpi = f"""
    <div class="kpis">
      <div class="kpi"><div class="v">{len(batches)}</div><div class="l">batches merged</div></div>
      <div class="kpi"><div class="v">{n_tested}<span class="sub">/{target}</span></div><div class="l">tickers tested ({pct:.1f}%)</div></div>
      <div class="kpi"><div class="v">{n_trades:,}</div><div class="l">total trades</div></div>
      <div class="kpi"><div class="v">{n_strat_traded}<span class="sub">/{n_registered}</span></div><div class="l">strategies traded</div></div>
      <div class="kpi"><div class="v">{n_silent}</div><div class="l">still silent</div></div>
    </div>
    <div class="bar"><div class="fill" style="width:{pct:.1f}%"></div></div>
    """

    # leaderboard table (top 40)
    lb_rows = ""
    for _, r in best.head(40).iterrows():
        lb_rows += (f"<tr><td class='s'>{html.escape(str(r['strategy']))}</td>"
                    f"<td>{html.escape(str(r['exit_method']))}</td>"
                    f"<td>{int(r['trades'])}</td>"
                    f"<td>{r['win_rate']*100:.1f}%</td>"
                    f"<td>{r['profit_factor']:.2f}</td>"
                    f"<td>{r['avg_pnl_pct']:.2f}</td>"
                    f"<td class='sc'>{r['composite_score']:.1f}</td></tr>")

    # exit ranking
    ex_rows = ""
    for _, r in exitrank.iterrows():
        ex_rows += (f"<tr><td>{html.escape(str(r['exit_method']))}</td>"
                    f"<td>{r['mean_score']:.1f}</td><td>{r['mean_wr']*100:.1f}%</td>"
                    f"<td>{int(r['cells'])}</td></tr>")

    # cube heatmap: top 30 strategies x all exits, colored by composite_score
    top_strats = best.head(30)["strategy"].tolist()
    exits = list(cube["exit_method"].unique())
    piv = cube.pivot_table(index="strategy", columns="exit_method",
                           values="composite_score", aggfunc="mean")
    lo, hi = float(cube["composite_score"].quantile(0.1)), float(cube["composite_score"].quantile(0.9))
    hh = "<tr><th class='rowh'>strategy \\ exit</th>" + "".join(
        f"<th class='exh'>{html.escape(e[:10])}</th>" for e in exits) + "</tr>"
    hrows = ""
    for s in top_strats:
        cells = ""
        for e in exits:
            v = piv.loc[s, e] if (s in piv.index and e in piv.columns) else None
            col = heat_color(v, lo, hi)
            txt = "" if (v is None or pd.isna(v)) else f"{v:.0f}"
            cells += f"<td class='hc' style='background:{col}' title='{html.escape(s)} / {html.escape(e)}: {txt}'>{txt}</td>"
        hrows += f"<tr><td class='rowh'>{html.escape(s)}</td>{cells}</tr>"

    ladder = [(1, 10), (2, 20), (3, 50), (4, 100), (5, 200), (6, target - 380)]
    ladder_rows = ""
    cum = 0
    for bi, sz in ladder:
        cum += sz
        done = "done" if bi <= len(batches) else ("run" if bi == len(batches) + 1 else "")
        mark = "&#9989;" if bi <= len(batches) else ("&#9203;" if bi == len(batches) + 1 else "")
        ladder_rows += f"<tr class='{done}'><td>{mark} Batch {bi}</td><td>{sz}</td><td>{cum}</td></tr>"

    return f"""
    <h1>R5 cube  -  batch progress</h1>
    <p class="meta">Full-PIT T1a target {target} tickers  &middot;  escalating disjoint batches  &middot;  cube = strategy  &times;  exit (trade-weighted pooled; authoritative verdict via merge_batch_outputs)</p>
    {kpi}
    <div class="grid2">
      <section><h2>Batch ladder</h2><table class="mini"><tr><th>batch</th><th>size</th><th>cumulative</th></tr>{ladder_rows}</table></section>
      <section><h2>Exit-method ranking</h2><table class="mini"><tr><th>exit</th><th>mean score</th><th>mean WR</th><th>cells</th></tr>{ex_rows}</table></section>
    </div>
    <h2>Cube heatmap  -  top 30 strategies  &times;  exits (composite score)</h2>
    <div class="scroll"><table class="heat">{hh}{hrows}</table></div>
    <h2>Strategy leaderboard  -  best exit per strategy (top 40)</h2>
    <div class="scroll"><table class="lb"><tr><th>strategy</th><th>best exit</th><th>trades</th><th>win rate</th><th>PF</th><th>avg pnl%</th><th>score</th></tr>{lb_rows}</table></div>
    """


CSS = """
:root{--bg:#0f1115;--card:#171a21;--fg:#e6e6e6;--mut:#9aa0aa;--line:#262a33;--acc:#4a9eff}
@media(prefers-color-scheme:light){:root{--bg:#f6f7f9;--card:#fff;--fg:#1a1d23;--mut:#5a616b;--line:#e2e5ea;--acc:#2266dd}}
:root[data-theme=dark]{--bg:#0f1115;--card:#171a21;--fg:#e6e6e6;--mut:#9aa0aa;--line:#262a33}
:root[data-theme=light]{--bg:#f6f7f9;--card:#fff;--fg:#1a1d23;--mut:#5a616b;--line:#e2e5ea}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;padding:24px;max-width:1400px;margin:0 auto}
h1{font-size:24px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 10px;color:var(--fg)}
.meta{color:var(--mut);margin:0 0 20px;font-size:12.5px}
.kpis{display:flex;gap:14px;flex-wrap:wrap}.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px;flex:1;min-width:130px}
.kpi .v{font-size:28px;font-weight:700}.kpi .sub{font-size:15px;color:var(--mut);font-weight:400}.kpi .l{color:var(--mut);font-size:12px;margin-top:2px}
.bar{height:10px;background:var(--card);border:1px solid var(--line);border-radius:6px;margin:16px 0;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,var(--acc),#39d98a)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:800px){.grid2{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;font-size:12.5px}th,td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--line)}
th{color:var(--mut);font-weight:600;text-align:right}td.s,td.rowh,th.rowh{text-align:left;font-family:ui-monospace,monospace;font-size:11.5px}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
.heat td.hc{text-align:center;color:#000;font-size:10px;min-width:34px;padding:3px}.heat th.exh{font-size:9.5px;writing-mode:vertical-rl;transform:rotate(180deg);padding:6px 2px}
.heat td.rowh{position:sticky;left:0;background:var(--card)}
td.sc,td.sc{font-weight:700;color:var(--acc)}
.mini td,.mini th{font-size:12px}
tr.done td:first-child{color:#39d98a}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=614)
    args = ap.parse_args()
    body = build(args.target)
    OUT.parent.mkdir(exist_ok=True)
    page = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>R5 cube dashboard</title><style>{CSS}</style></head>"
            f"<body>{body}<p class='meta' style='margin-top:30px'>Generated by "
            f"scripts/build_r5_dashboard.py  -  regenerate after each batch.</p></body></html>")
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
