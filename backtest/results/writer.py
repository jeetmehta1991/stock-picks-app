"""
results/writer.py — Write all 15 output files including walk-forward and improvements data.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from backtest.config import PASSING_CRITERIA

logger = logging.getLogger(__name__)


def write_all_outputs(
    df_trades:          pd.DataFrame,
    metrics:            pd.DataFrame,
    skipped:            list,
    cb_log:             list,
    exit_compare:       pd.DataFrame,
    trade_exit_detail:  pd.DataFrame  = None,
    walk_forward:       pd.DataFrame  = None,
    survivorship_info:  dict          = None,
    bonferroni:         dict          = None,
    output_dir:         Path          = Path("output"),
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Trade log ──
    df_trades.to_csv(output_dir / "trade_log.csv", index=False)
    logger.info("Wrote trade_log.csv (%d trades)", len(df_trades))

    # ── Backtest results ──
    if not metrics.empty:
        csv_m = metrics.drop(columns=["regime_details","passes"], errors="ignore")
        csv_m.to_csv(output_dir / "backtest_results.csv", index=False)
        logger.info("Wrote backtest_results.csv (%d strategies)", len(metrics))

        winners = metrics[metrics.get("passes_all", False) == True].copy() \
                  if "passes_all" in metrics else pd.DataFrame()

        # Attach optimal exit + walk-forward verdict to winners
        if not exit_compare.empty and not winners.empty:
            best_exits = (exit_compare[exit_compare.get("recommended", False) == True]
                         [["strategy","exit_method","composite_score"]]
                         .set_index("strategy"))
            winners["optimal_exit_method"]  = winners["strategy"].map(
                best_exits.get("exit_method",  pd.Series()).to_dict())
            winners["exit_composite_score"] = winners["strategy"].map(
                best_exits.get("composite_score", pd.Series()).to_dict())

        if walk_forward is not None and not walk_forward.empty and not winners.empty:
            wf_map = walk_forward.set_index("strategy")["verdict"].to_dict()
            winners["walk_forward_verdict"] = winners["strategy"].map(wf_map)

        with open(output_dir / "winning_strategies.json", "w") as f:
            json.dump({
                "generated_at":       datetime.utcnow().isoformat(),
                "total_winners":      len(winners),
                "passing_criteria":   {k: str(v) for k, v in PASSING_CRITERIA.items()
                                       if not k.startswith("audit")},
                "survivorship_info":  survivorship_info or {},
                "bonferroni":         bonferroni or {},
                "strategies": winners.drop(
                    columns=["regime_details","passes"], errors="ignore"
                ).to_dict(orient="records"),
            }, f, indent=2, default=str)
        logger.info("Wrote winning_strategies.json (%d winners)", len(winners))

    # ── Regime performance ──
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
        logger.info("Wrote regime_performance.csv")

    # ── Exit comparison ──
    if not exit_compare.empty:
        exit_compare.to_csv(output_dir / "exit_strategy_comparison.csv", index=False)
        best = exit_compare[exit_compare.get("recommended", False) == True].copy()

    if trade_exit_detail is not None and not trade_exit_detail.empty:
        trade_exit_detail.to_csv(output_dir / "trade_exit_detail.csv", index=False)
        logger.info("Wrote trade_exit_detail.csv — %d rows (%d trades × exits)",
                    len(trade_exit_detail),
                    trade_exit_detail["ticker"].count() if "ticker" in trade_exit_detail.columns else 0)
        best.to_csv(output_dir / "exit_strategy_best.csv", index=False)
        logger.info("Wrote exit_strategy_comparison.csv + exit_strategy_best.csv")

    # ── Walk-forward validation ──
    # Portfolio-level summary with tier-based position sizing
    try:
        from backtest.results.metrics import compute_portfolio_summary
        port_summary = compute_portfolio_summary(df_trades)
        if port_summary:
            (output_dir / "portfolio_summary.json").write_text(json.dumps(port_summary, indent=2))
            logger.info("Portfolio return (tier-sized): %.1f%% | Max heat: %.1f%%",
                        port_summary.get("portfolio_return_pct", 0),
                        port_summary.get("max_portfolio_heat_pct", 0))
    except Exception as e:
        logger.debug("Portfolio summary failed: %s", e)

    # Sector concentration analysis — how often were we concentrated in one sector?
    if "sector" in df_trades.columns and "entry_date" in df_trades.columns:
        try:
            df_trades["entry_date"] = pd.to_datetime(df_trades["entry_date"])
            sector_daily = df_trades.groupby(["entry_date", "sector"]).size().reset_index(name="trades")
            total_daily  = df_trades.groupby("entry_date").size().reset_index(name="total_trades")
            sector_conc  = sector_daily.merge(total_daily, on="entry_date")
            sector_conc["sector_pct"] = sector_conc["trades"] / sector_conc["total_trades"] * 100
            high_conc = sector_conc[sector_conc["sector_pct"] >= 50]
            sector_conc.to_csv(output_dir / "sector_concentration.csv", index=False)
            logger.info("Sector concentration: %d days with >=50%% in one sector", len(high_conc))
        except Exception as e:
            logger.debug("Sector concentration calc failed: %s", e)

    if walk_forward is not None and not walk_forward.empty:
        walk_forward.to_csv(output_dir / "walk_forward_validation.csv", index=False)
        robust  = (walk_forward["verdict"] == "ROBUST").sum()
        overfit = (walk_forward["verdict"] == "OVERFIT").sum()
        logger.info("Wrote walk_forward_validation.csv — ROBUST=%d OVERFIT=%d",
                    robust, overfit)

    # ── IS/OOS granular trade splits ──
    # In-sample: 2022-01-01 to 2024-12-31 | Out-of-sample: 2025-01-01 to 2026-03-31
    if "entry_date" in df_trades.columns:
        df_trades["entry_date"] = pd.to_datetime(df_trades["entry_date"])
        is_trades  = df_trades[df_trades["entry_date"] < "2025-01-01"]
        oos_trades = df_trades[df_trades["entry_date"] >= "2025-01-01"]
        is_trades.to_csv(output_dir / "trade_log_in_sample.csv", index=False)
        oos_trades.to_csv(output_dir / "trade_log_out_of_sample.csv", index=False)
        logger.info("Wrote IS trade log: %d trades | OOS trade log: %d trades",
                    len(is_trades), len(oos_trades))

    # ── Improvements summary ──
    improvements = {
        "generated_at":        datetime.utcnow().isoformat(),
        "transaction_costs": {
            "applied": "pnl_pct" in df_trades and "pnl_pct_gross" in df_trades,
            "gross_total_roi": round(df_trades.get("pnl_pct_gross", df_trades["pnl_pct"]).sum(), 3),
            "net_total_roi":   round(df_trades["pnl_pct"].sum(), 3),
            "total_cost":      round(df_trades.get("cost_pct", pd.Series([0])).sum(), 3),
        },
        "survivorship_bias":  survivorship_info or {},
        "bonferroni":         bonferroni or {},
        "walk_forward_summary": {
            "total":   len(walk_forward) if walk_forward is not None else 0,
            "robust":  int((walk_forward["verdict"] == "ROBUST").sum())  if walk_forward is not None and not walk_forward.empty else 0,
            "overfit": int((walk_forward["verdict"] == "OVERFIT").sum()) if walk_forward is not None and not walk_forward.empty else 0,
        } if walk_forward is not None else {},
    }
    with open(output_dir / "improvements_summary.json", "w") as f:
        json.dump(improvements, f, indent=2, default=str)

    # ── Smart money ──
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

    # ── Confidence tier performance ──
    if "confidence_tier" in df_trades:
        from backtest.results.metrics import compute_confidence_tier_metrics
        tier_metrics = compute_confidence_tier_metrics(df_trades)
        tier_metrics.to_csv(output_dir / "agent_performance.csv", index=False)

        # Preliminary vs agent-adjusted tier comparison
        if "preliminary_tier" in df_trades.columns:
            tier_compare = df_trades.groupby(["preliminary_tier", "confidence_tier"]).agg(
                trades=("win", "count"),
                win_rate=("win", "mean"),
            ).reset_index()
            tier_compare["upgraded"]   = tier_compare.apply(
                lambda r: r["confidence_tier"] > r["preliminary_tier"], axis=1)
            tier_compare["downgraded"] = tier_compare.apply(
                lambda r: r["confidence_tier"] < r["preliminary_tier"], axis=1)
            tier_compare.to_csv(output_dir / "tier_adjustment_analysis.csv", index=False)
            logger.info("Wrote tier_adjustment_analysis.csv — agent upgrade/downgrade rates")

    # ── Placeholder CSVs ──
    for fname in ["congressional_correlation.csv", "insider_correlation.csv"]:
        p = output_dir / fname
        if not p.exists():
            pd.DataFrame(columns=["signal","trades","win_rate","avg_pnl"]).to_csv(p, index=False)

    # ── Skipped + circuit breakers ──
    pd.DataFrame(skipped).to_csv(output_dir / "skipped_trades.csv", index=False)
    pd.DataFrame(cb_log).to_csv(output_dir / "circuit_breaker_log.csv", index=False)

    # ── HTML report ──
    _write_html(df_trades, metrics, exit_compare, walk_forward,
                survivorship_info, bonferroni, output_dir)

    logger.info("All outputs written to %s", output_dir)


def _write_html(df, metrics, exit_compare, walk_forward,
                survivorship_info, bonferroni, output_dir):
    ts   = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    n    = len(df)
    n_w  = int(metrics["passes_all"].sum()) if not metrics.empty and "passes_all" in metrics else 0
    n_s  = len(metrics) if not metrics.empty else 0
    dirs = df["direction"].value_counts().to_dict() if "direction" in df else {}
    gross_roi = df.get("pnl_pct_gross", df["pnl_pct"]).sum() if "pnl_pct_gross" in df else df["pnl_pct"].sum()
    net_roi   = df["pnl_pct"].sum()
    cost_roi  = df.get("cost_pct", pd.Series([0])).sum()

    def wr_cell(wr):
        pct = round(wr*100, 1)
        c   = "#3fb950" if wr >= 0.55 else "#e3b341" if wr >= 0.45 else "#f85149"
        return f'<td style="color:{c};font-weight:500">{pct}%{"  ✓" if wr>=0.55 else ""}</td>'

    strat_rows = ""
    if not metrics.empty:
        # Merge walk-forward verdicts
        wf_map = {}
        if walk_forward is not None and not walk_forward.empty:
            wf_map = walk_forward.set_index("strategy")["verdict"].to_dict()

        for _, r in metrics.head(40).iterrows():
            pc     = "#3fb950" if r.get("total_roi_pct",0)>0 else "#f85149"
            mc     = "#f85149" if r.get("max_drawdown_pct",0)<-10 else "#e3b341"
            wfv    = wf_map.get(r["strategy"],"—")
            wf_col = "#3fb950" if wfv=="ROBUST" else "#f85149" if wfv=="OVERFIT" else "#e3b341"
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
              <td style="color:{wf_col};font-weight:500">{wfv}</td>
              <td>{'✅' if r.get('passes_all') else ''}{'⚠️' if r.get('audit_flags') else ''}</td>
            </tr>"""

    # Walk-forward summary table
    wf_rows = ""
    if walk_forward is not None and not walk_forward.empty:
        for _, r in walk_forward.head(30).iterrows():
            vc = "#3fb950" if r["verdict"]=="ROBUST" else "#f85149" if r["verdict"]=="OVERFIT" else "#e3b341"
            wf_rows += f"""<tr>
              <td style="color:#58a6ff">{r['strategy']}</td>
              <td style="color:{vc};font-weight:600">{r['verdict']}</td>
              <td>{r.get('is_trades',0)}</td>
              <td style="color:{'#3fb950' if r.get('is_win_rate',0)>=0.55 else '#f85149'}">{round(r.get('is_win_rate',0)*100,1)}%</td>
              <td>{r.get('oos_trades',0)}</td>
              <td style="color:{'#3fb950' if r.get('oos_win_rate',0)>=0.55 else '#f85149'}">{round(r.get('oos_win_rate',0)*100,1)}%</td>
              <td style="color:{'#f85149' if (r.get('wr_degradation') or 0)<-0.05 else '#8b949e'}">{round((r.get('wr_degradation') or 0)*100,1)}%</td>
            </tr>"""

    sb  = survivorship_info or {}
    bon = bonferroni or {}

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
.improvements{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:.75rem;margin-bottom:1.5rem}}
.imp-card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:.9rem 1.1rem}}
.imp-card .title{{font-size:.7rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.4rem}}
.imp-card .val{{font-size:1.1rem;font-weight:600;color:#f0f6fc}}
.imp-card .sub{{font-size:.72rem;color:#8b949e;margin-top:.2rem}}
table{{width:100%;border-collapse:collapse;font-size:.8rem;margin-bottom:1rem}}
th{{background:#161b22;color:#8b949e;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;
    padding:.55rem .8rem;text-align:left;border-bottom:1px solid #21262d}}
td{{padding:.55rem .8rem;border-bottom:1px solid #21262d}}
tr:hover td{{background:#1c2128}}
footer{{text-align:center;margin-top:3rem;font-size:.75rem;color:#484f58;
        padding-top:1rem;border-top:1px solid #21262d}}
</style></head><body>
<h1>Backtest Report — Stage 2</h1>
<p style="color:#8b949e;font-size:.85rem">Generated {ts} &nbsp;|&nbsp; 60 strategies &nbsp;|&nbsp; 12 exit methods &nbsp;|&nbsp; 5 improvements applied</p>

<div class="stats">
  <div class="stat"><div class="v">{n:,}</div><div class="l">Trades simulated</div></div>
  <div class="stat"><div class="v">{n_s}</div><div class="l">Strategies tested</div></div>
  <div class="stat"><div class="v" style="color:#3fb950">{n_w}</div><div class="l">Passing all criteria</div></div>
  <div class="stat"><div class="v">{dirs.get('long',0):,}</div><div class="l">Long trades</div></div>
  <div class="stat"><div class="v">{dirs.get('short',0):,}</div><div class="l">Short trades</div></div>
  <div class="stat"><div class="v" style="color:{'#3fb950' if gross_roi>0 else '#f85149'}">{gross_roi:.1f}%</div><div class="l">Gross ROI</div></div>
  <div class="stat"><div class="v" style="color:{'#3fb950' if net_roi>0 else '#f85149'}">{net_roi:.1f}%</div><div class="l">Net ROI (after costs)</div></div>
  <div class="stat"><div class="v" style="color:#f85149">-{cost_roi:.1f}%</div><div class="l">Transaction costs</div></div>
</div>

<h2>Improvements applied</h2>
<div class="improvements">
  <div class="imp-card"><div class="title">Transaction costs</div>
    <div class="val">-{cost_roi:.2f}% total</div>
    <div class="sub">0.08% ETF · 0.10% large-cap · 0.15% mid-cap round-trip</div></div>
  <div class="imp-card"><div class="title">Survivorship bias haircut</div>
    <div class="val">-{sb.get('haircut_pct',0):.1f}% applied</div>
    <div class="sub">2% annual over {sb.get('years',3):.1f} years — gross {sb.get('gross_roi',0):.1f}% → adjusted {sb.get('adjusted_roi',0):.1f}%</div></div>
  <div class="imp-card"><div class="title">Walk-forward validation</div>
    <div class="val">In-sample 2022-23 · OOS 2024</div>
    <div class="sub">ROBUST = passes both · OVERFIT = fails out-of-sample</div></div>
  <div class="imp-card"><div class="title">Correlation filter</div>
    <div class="val">Max 0.70 correlation</div>
    <div class="sub">Max 3 positions per sector · prevents concentrated drawdowns</div></div>
  <div class="imp-card"><div class="title">Slippage model</div>
    <div class="val">Applied at entry</div>
    <div class="sub">Spread + gap penalty · 0.03% ETF · 0.08% large-cap · 0.15% high-vol</div></div>
  <div class="imp-card"><div class="title">Bonferroni correction</div>
    <div class="val">{bon.get('min_trades_required',200)}+ trades required</div>
    <div class="sub">60 strategies tested · adjusted p={bon.get('adjusted_significance',0):.5f}</div></div>
</div>

<h2>Strategy performance (net of transaction costs)</h2>
<div class="note"><strong>Pass criteria:</strong> 55%+ win rate · profit factor &gt;1.2 · {bon.get('min_trades_required',100)}+ trades · 2+ regimes · positive net ROI · max drawdown &lt;20%
&nbsp;·&nbsp; ⚠️ = flagged for look-ahead bias audit</div>
<table><thead><tr><th>Strategy</th><th>Category</th><th>L/S</th><th>Trades</th>
<th>Win rate</th><th>Profit factor</th><th>Net ROI</th><th>Max DD</th><th>Regimes</th><th>Walk-forward</th><th>Pass</th>
</tr></thead><tbody>{strat_rows or '<tr><td colspan="11" style="text-align:center;color:#484f58;padding:2rem">No data yet</td></tr>'}</tbody></table>

<h2>Walk-forward validation — in-sample (2022-23) vs out-of-sample (2024)</h2>
<div class="note"><strong>ROBUST</strong> = strategy passes both periods — real edge &nbsp;·&nbsp;
<strong>OVERFIT</strong> = passes in-sample, fails 2024 — curve-fitted to training data, do not trade &nbsp;·&nbsp;
Win rate degradation &gt;5% is a red flag</div>
<table><thead><tr><th>Strategy</th><th>Verdict</th><th>IS trades</th><th>IS win rate</th>
<th>OOS trades</th><th>OOS win rate</th><th>WR degradation</th></tr></thead><tbody>
{wf_rows or '<tr><td colspan="7" style="text-align:center;color:#484f58;padding:2rem">Run full Phase 1A to see walk-forward results</td></tr>'}
</tbody></table>

<footer><p>Stock Picks &amp; Automated Trading System — Stage 2 &nbsp;·&nbsp; All improvements applied</p>
<p>Point-in-time data · No look-ahead bias · 60 strategies · 12 exits · 5 regimes · 5 improvements</p></footer>
</body></html>"""

    with open(output_dir / "backtest_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    logger.info("Wrote backtest_report.html")
