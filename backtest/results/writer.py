"""
results/writer.py — Write all 13 output files including exit strategy comparison.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from backtest.config import PASSING_CRITERIA

logger = logging.getLogger(__name__)


def write_all_outputs(
    df_trades:    pd.DataFrame,
    metrics:      pd.DataFrame,
    skipped:      list,
    cb_log:       list,
    exit_compare: pd.DataFrame,
    output_dir:   Path,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df_trades.to_csv(output_dir / "trade_log.csv", index=False)
    logger.info("Wrote trade_log.csv (%d trades)", len(df_trades))

    if not metrics.empty:
        csv_m = metrics.drop(columns=["regime_details","passes"], errors="ignore")
        csv_m.to_csv(output_dir / "backtest_results.csv", index=False)

        winners = metrics[metrics.get("passes_all", False) == True].copy()
        if not exit_compare.empty and not winners.empty:
            best_exits = (exit_compare[exit_compare.get("recommended", False) == True]
                         [["strategy","exit_method","composite_score"]]
                         .set_index("strategy"))
            winners["optimal_exit_method"]  = winners["strategy"].map(
                best_exits.get("exit_method", pd.Series()).to_dict())
            winners["exit_composite_score"] = winners["strategy"].map(
                best_exits.get("composite_score", pd.Series()).to_dict())

        with open(output_dir / "winning_strategies.json", "w") as f:
            json.dump({
                "generated_at":   datetime.utcnow().isoformat(),
                "total_winners":  len(winners),
                "passing_criteria": {k: str(v) for k, v in PASSING_CRITERIA.items()
                                     if not k.startswith("audit")},
                "strategies": winners.drop(
                    columns=["regime_details","passes"], errors="ignore"
                ).to_dict(orient="records"),
            }, f, indent=2, default=str)
        logger.info("Wrote winning_strategies.json (%d winners)", len(winners))

    # Regime performance
    if "regime" in df_trades and "strategy" in df_trades:
        rows = []
        for strat, grp in df_trades.groupby("strategy"):
            for regime_str, r_grp in grp.groupby("regime"):
                if len(r_grp) < 3:
                    continue
                rows.append({
                    "strategy":  strat, "regime": regime_str,
                    "trades":    len(r_grp),
                    "win_rate":  round(r_grp["win"].mean(), 4),
                    "avg_pnl":   round(r_grp["pnl_pct"].mean(), 4),
                    "total_roi": round(r_grp["pnl_pct"].sum(), 4),
                })
        pd.DataFrame(rows).to_csv(output_dir / "regime_performance.csv", index=False)

    # Exit comparison
    if not exit_compare.empty:
        exit_compare.to_csv(output_dir / "exit_strategy_comparison.csv", index=False)
        best = exit_compare[exit_compare.get("recommended", False) == True].copy()
        best.to_csv(output_dir / "exit_strategy_best.csv", index=False)
        logger.info("Wrote exit_strategy_comparison.csv + exit_strategy_best.csv")

    # Smart money
    if "smart_money_score" in df_trades:
        rows = []
        for tier in range(0, 11, 2):
            g = df_trades[df_trades["smart_money_score"] >= tier]
            if len(g) < 5:
                continue
            rows.append({"min_sm_score": tier, "trades": len(g),
                         "win_rate": round(g["win"].mean(), 4),
                         "avg_pnl":  round(g["pnl_pct"].mean(), 4)})
        pd.DataFrame(rows).to_csv(output_dir / "smart_money_combined.csv", index=False)

    if "confidence_tier" in df_trades:
        from backtest.results.metrics import compute_confidence_tier_metrics
        compute_confidence_tier_metrics(df_trades).to_csv(
            output_dir / "agent_performance.csv", index=False)

    for fname in ["congressional_correlation.csv", "insider_correlation.csv"]:
        p = output_dir / fname
        if not p.exists():
            pd.DataFrame(columns=["signal","trades","win_rate","avg_pnl"]).to_csv(p, index=False)

    pd.DataFrame(skipped).to_csv(output_dir / "skipped_trades.csv", index=False)
    pd.DataFrame(cb_log).to_csv(output_dir / "circuit_breaker_log.csv", index=False)
    _write_html(df_trades, metrics, exit_compare, output_dir)
    logger.info("All outputs written to %s", output_dir)


def _write_html(df, metrics, exit_compare, output_dir):
    ts  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    n   = len(df)
    n_w = int(metrics["passes_all"].sum()) if not metrics.empty and "passes_all" in metrics else 0
    n_s = len(metrics) if not metrics.empty else 0
    dirs = df["direction"].value_counts().to_dict() if "direction" in df else {}

    def wr_cell(wr):
        pct = round(wr*100, 1)
        c   = "#3fb950" if wr >= 0.55 else "#e3b341" if wr >= 0.45 else "#f85149"
        return f'<td style="color:{c};font-weight:500">{pct}%{"  ✓" if wr>=0.55 else ""}</td>'

    strat_rows = ""
    if not metrics.empty:
        for _, r in metrics.head(40).iterrows():
            pc = "#3fb950" if r.get("total_roi_pct",0)>0 else "#f85149"
            mc = "#f85149" if r.get("max_drawdown_pct",0)<-10 else "#e3b341"
            strat_rows += f"""<tr>
              <td style="color:#58a6ff;font-weight:600">{r['strategy']}</td>
              <td style="color:#8b949e">{r.get('category','')}</td>
              <td>{r.get('direction_mix','')}</td>
              <td>{int(r.get('total_trades',0)):,}</td>
              {wr_cell(r.get('win_rate',0))}
              <td>{r.get('profit_factor',0):.2f}</td>
              <td style="color:{pc}">{r.get('total_roi_pct',0):.1f}%</td>
              <td style="color:{mc}">{r.get('max_drawdown_pct',0):.1f}%</td>
              <td>{int(r.get('regimes_profitable',0))}</td>
              <td>{'✅' if r.get('passes_all') else ''}{'⚠️' if r.get('audit_flags') else ''}</td>
            </tr>"""

    exit_rows = ""
    if not exit_compare.empty:
        best = exit_compare[exit_compare.get("recommended", False) == True]
        for _, r in best.iterrows():
            cs_c = "#3fb950" if r.get("composite_score",0)>=60 else "#e3b341"
            exit_rows += f"""<tr>
              <td style="color:#58a6ff;font-weight:600">{r['strategy']}</td>
              <td style="color:#c9d1d9;font-weight:500">{r['exit_method']}</td>
              <td>{int(r.get('trades',0)):,}</td>
              {wr_cell(r.get('win_rate',0))}
              <td>{r.get('profit_factor',0):.2f}</td>
              <td style="color:{'#3fb950' if r.get('total_roi_pct',0)>0 else '#f85149'}">{r.get('total_roi_pct',0):.1f}%</td>
              <td style="color:#f85149">{r.get('max_drawdown_pct',0):.1f}%</td>
              <td>{r.get('avg_hold_days',0):.1f}d</td>
              <td style="color:{cs_c};font-weight:600">{r.get('composite_score',0):.1f}</td>
            </tr>"""

    html = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Backtest Report — {ts}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0d1117;color:#c9d1d9;padding:2rem 1rem}}
h1{{font-size:1.7rem;color:#f0f6fc;margin-bottom:.4rem}}
h2{{font-size:1rem;color:#58a6ff;margin:2.5rem 0 .75rem;border-bottom:1px solid #21262d;padding-bottom:.4rem}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:1.5rem 0}}
.stat{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem 1.2rem}}
.stat .v{{font-size:2rem;font-weight:700;color:#f0f6fc}} .stat .l{{font-size:.75rem;color:#8b949e;margin-top:3px}}
.note{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:.9rem 1.2rem;
       font-size:.82rem;color:#8b949e;margin-bottom:1.5rem}}
.note strong{{color:#c9d1d9}}
table{{width:100%;border-collapse:collapse;font-size:.82rem;margin-bottom:1rem}}
th{{background:#161b22;color:#8b949e;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;
    padding:.55rem .8rem;text-align:left;border-bottom:1px solid #21262d}}
td{{padding:.55rem .8rem;border-bottom:1px solid #21262d}}
tr:hover td{{background:#1c2128}}
footer{{text-align:center;margin-top:3rem;font-size:.75rem;color:#484f58;
        padding-top:1rem;border-top:1px solid #21262d}}
</style></head><body>
<h1>Backtest Report — Stage 2</h1>
<p style="color:#8b949e;font-size:.85rem">Generated {ts} &nbsp;|&nbsp; 60 strategies &nbsp;|&nbsp; 12 exit methods</p>
<div class="stats">
  <div class="stat"><div class="v">{n:,}</div><div class="l">Trades simulated</div></div>
  <div class="stat"><div class="v">{n_s}</div><div class="l">Strategies tested</div></div>
  <div class="stat"><div class="v" style="color:#3fb950">{n_w}</div><div class="l">Passing all criteria</div></div>
  <div class="stat"><div class="v">{dirs.get('long',0):,}</div><div class="l">Long trades</div></div>
  <div class="stat"><div class="v">{dirs.get('short',0):,}</div><div class="l">Short trades</div></div>
</div>
<h2>Strategy performance</h2>
<div class="note"><strong>Pass criteria:</strong> 55%+ win rate · profit factor &gt;1.2 · 100+ trades · 2+ regimes · positive ROI · max drawdown &lt;20%</div>
<table><thead><tr><th>Strategy</th><th>Category</th><th>L/S</th><th>Trades</th>
<th>Win rate</th><th>Profit factor</th><th>Total ROI</th><th>Max DD</th><th>Regimes</th><th>Pass</th>
</tr></thead><tbody>{strat_rows or '<tr><td colspan="10" style="text-align:center;color:#484f58;padding:2rem">No data yet</td></tr>'}</tbody></table>
<h2>Exit strategy comparison — best exit per strategy</h2>
<div class="note"><strong>Composite score</strong> = 40% ROI + 30% profit factor + 30% lowest drawdown &nbsp;·&nbsp;
Score &gt;60 = recommended &nbsp;·&nbsp; Optimal exit shown on site card per strategy</div>
<table><thead><tr><th>Strategy</th><th>Best exit</th><th>Trades</th>
<th>Win rate</th><th>Profit factor</th><th>Total ROI</th><th>Max DD</th><th>Avg hold</th><th>Score</th>
</tr></thead><tbody>{exit_rows or '<tr><td colspan="9" style="text-align:center;color:#484f58;padding:2rem">No exit comparison data yet</td></tr>'}</tbody></table>
<footer><p>Stock Picks &amp; Automated Trading System — Stage 2</p>
<p>Point-in-time data enforced · No look-ahead bias · 60 strategies · 12 exit methods · 5 regimes</p></footer>
</body></html>"""

    with open(output_dir / "backtest_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    logger.info("Wrote backtest_report.html")
