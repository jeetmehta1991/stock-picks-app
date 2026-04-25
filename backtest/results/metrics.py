"""
results/metrics.py — All 10 passing criteria computed per strategy.

Metrics per strategy (grouped by direction and hold period):
  1.  win_rate                — % trades profitable
  2.  profit_factor           — total wins / total losses (threshold: 1.2)
  3.  expected_value          — (win_rate × avg_win) + (loss_rate × avg_loss)
  4.  win_loss_ratio          — avg win pnl / avg loss pnl
  5.  max_drawdown            — worst peak-to-trough in equity curve
  6.  total_roi               — sum of all pnl_pct
  7.  smart_money_lift        — win rate with vs without smart money signal
  8.  macro_correlation       — win rate in favourable vs unfavourable regime
  9.  trade_count             — total trades (min 100)
  10. regimes_profitable      — count of regimes with win rate >= 55%

Also computes:
  - Sharpe ratio approximation
  - Average hold days
  - Best / worst single trade
  - Regime breakdown table
"""

import logging
from datetime import date

import numpy as np
import pandas as pd

from backtest.config import PASSING_CRITERIA, MARKET_REGIMES

logger = logging.getLogger(__name__)


def _profit_factor(pnl_series: pd.Series) -> float:
    wins   = pnl_series[pnl_series > 0].sum()
    losses = abs(pnl_series[pnl_series < 0].sum())
    return round(wins / losses, 4) if losses > 0 else float("inf")


def _max_drawdown(pnl_series: pd.Series) -> float:
    """Max peak-to-trough drawdown on cumulative PnL curve."""
    cumulative = pnl_series.cumsum()
    peak       = cumulative.cummax()
    drawdown   = (cumulative - peak)
    return round(float(drawdown.min()), 4)


def _calmar(pnl_series: pd.Series, hold_days_series: pd.Series) -> float:
    """Calmar ratio: annualised return / max drawdown magnitude."""
    mdd = abs(_max_drawdown(pnl_series))
    if mdd == 0:
        return 0.0
    # Annualise: assume average 252 trading days/year
    avg_hold = float(hold_days_series.mean()) if len(hold_days_series) > 0 else 10
    n_trades_per_year = 252 / max(avg_hold, 1)
    annual_return = float(pnl_series.mean()) * n_trades_per_year
    return round(annual_return / mdd, 3)


def _confidence_interval_95(win_rate: float, n: int) -> tuple:
    """95% Wilson confidence interval for win rate."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.96
    p = win_rate
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2*n)) / denom
    margin = (z * (p*(1-p)/n + z**2/(4*n**2))**0.5) / denom
    lo = max(0.0, round(centre - margin, 4))
    hi = min(1.0, round(centre + margin, 4))
    return (lo, hi)


def _sharpe(pnl_series: pd.Series) -> float:
    if pnl_series.std() == 0:
        return 0.0
    return round(float(pnl_series.mean() / pnl_series.std() * np.sqrt(252)), 3)


def compute_strategy_metrics(df: pd.DataFrame, strategy: str) -> dict:
    """Compute all metrics for a single strategy across all trades."""
    g = df[df["strategy"] == strategy]
    if g.empty:
        return {}

    pnl  = g["pnl_pct"]
    wins = g[g["win"] == True]
    loss = g[g["win"] == False]

    n        = len(g)
    win_rate = len(wins) / n if n > 0 else 0
    avg_win  = float(wins["pnl_pct"].mean()) if len(wins) > 0 else 0
    avg_loss = float(loss["pnl_pct"].mean()) if len(loss) > 0 else 0

    pf    = _profit_factor(pnl)
    ev    = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    wl_r  = abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")
    mdd   = _max_drawdown(pnl)
    roi   = round(float(pnl.sum()), 4)
    sharpe = _sharpe(pnl)
    calmar = _calmar(pnl, g["hold_days"] if "hold_days" in g else pd.Series([10]))
    ci_lo, ci_hi = _confidence_interval_95(win_rate, n)
    statistically_random = ci_lo < 0.50  # lower CI bound below 50% = may be random

    # Regime breakdown — count profitable regimes
    regimes_profitable = 0
    regime_details     = {}
    for regime_name in MARKET_REGIMES:
        r_grp = g[g["regime"].str.contains(regime_name, na=False)]
        if len(r_grp) >= 5:
            r_wr = r_grp["win"].mean()
            regime_details[regime_name] = {
                "trades": len(r_grp), "win_rate": round(r_wr, 4),
                "avg_pnl": round(float(r_grp["pnl_pct"].mean()), 4),
                "profitable": r_wr >= PASSING_CRITERIA["min_win_rate"],
            }
            if r_wr >= PASSING_CRITERIA["min_win_rate"]:
                regimes_profitable += 1

    # Smart money lift — within-strategy comparison (correct method)
    # Isolate SM contribution by holding strategy constant
    has_sm = g[g["smart_money_score"] >= 2]
    no_sm  = g[g["smart_money_score"] < 2]
    sm_lift = None
    if len(has_sm) >= 30 and len(no_sm) >= 30:
        sm_lift = round(float(has_sm["win"].mean()) - float(no_sm["win"].mean()), 4)

    # Macro correlation — defined threshold
    fav_macro   = g[g["macro_score"] >= 2]
    unfav_macro = g[g["macro_score"] < 0]
    macro_corr = None
    if len(fav_macro) >= 20 and len(unfav_macro) >= 20:
        macro_corr = round(float(fav_macro["win"].mean()) - float(unfav_macro["win"].mean()), 4)

    # Sector-adjusted passing criteria
    from backtest.config import get_sector_criteria
    sector = g["sector"].iloc[0] if "sector" in g.columns and not g["sector"].empty else "Unknown"
    pc = get_sector_criteria(sector)
    # Direction split
    long_df  = g[g["direction"] == "long"]
    short_df = g[g["direction"] == "short"]

    SM_LIFT_THRESHOLD    = 0.03   # >= 3pp win rate improvement required
    MACRO_CORR_THRESHOLD = 0.05   # >= 5pp win rate diff required
    passes = {
        "win_rate":           win_rate >= pc["min_win_rate"],
        "profit_factor":      pf >= pc["min_profit_factor"],
        "expected_value":     ev > pc["min_expected_value"],
        "win_loss_ratio":     wl_r >= pc["min_win_loss_ratio"],
        "max_drawdown":       mdd >= -pc["max_drawdown"],
        "total_roi":          roi > pc["min_total_roi"],
        "smart_money_lift":   (sm_lift is None) or (sm_lift >= SM_LIFT_THRESHOLD),
        "macro_correlation":  (macro_corr is None) or (macro_corr >= MACRO_CORR_THRESHOLD),
        "trade_count":        n >= pc["min_trades"],
        "regimes_profitable": regimes_profitable >= pc["min_regimes_profitable"],
    }
    passes_all = all(passes.values())

    # Audit flags
    audit_flags = []
    if win_rate > pc["audit_win_rate_above"]:
        audit_flags.append(f"win_rate_{win_rate*100:.1f}pct_exceeds_audit_threshold")
    if pf > pc["audit_profit_factor_above"]:
        audit_flags.append(f"profit_factor_{pf:.2f}_exceeds_audit_threshold")
    if statistically_random:
        audit_flags.append(f"ci_lower_{ci_lo*100:.1f}pct_may_be_random")

    return {
        "strategy":              strategy,
        "sector":                sector,
        "sector_criteria":       pc.get("_label", "medium_volatility"),
        "direction_mix":         f"{len(long_df)}L/{len(short_df)}S",
        "total_trades":          n,
        "win_rate":              round(win_rate, 4),
        "win_rate_ci_low":       ci_lo,
        "win_rate_ci_high":      ci_hi,
        "statistically_random":  statistically_random,
        "profit_factor":         round(pf, 4),
        "expected_value":        round(ev, 4),
        "win_loss_ratio":        round(wl_r, 4) if wl_r != float("inf") else 999,
        "avg_win_pct":           round(avg_win, 4),
        "avg_loss_pct":          round(avg_loss, 4),
        "max_drawdown_pct":      round(mdd, 4),
        "total_roi_pct":         round(roi, 4),
        "sharpe_ratio":          sharpe,
        "calmar_ratio":          calmar,
        "avg_hold_days":         round(float(g["hold_days"].mean()), 1) if "hold_days" in g else 0,
        "best_trade_pct":        round(float(pnl.max()), 4),
        "worst_trade_pct":       round(float(pnl.min()), 4),
        "smart_money_lift":      sm_lift,
        "macro_correlation":     macro_corr,
        "regimes_profitable":    regimes_profitable,
        "regime_details":        regime_details,
        "passes":                passes,
        "passes_all":            passes_all,
        "audit_flags":           audit_flags,
        "category":              g["category"].iloc[0] if "category" in g else "",
    }


def compute_all_metrics(df: pd.DataFrame, spy_total_return: float = None) -> pd.DataFrame:
    """Compute metrics for all strategies. Returns sorted DataFrame.
    
    spy_total_return: SPY buy-and-hold total return over same period (for benchmark comparison).
    If None, benchmark comparison columns are omitted.
    """
    if df.empty:
        return pd.DataFrame()
    strategies = df["strategy"].unique()
    rows = []
    for s in strategies:
        m = compute_strategy_metrics(df, s)
        if m:
            if spy_total_return is not None:
                m["spy_benchmark_return"] = round(spy_total_return, 4)
                m["vs_benchmark"]         = round(m["total_roi_pct"] - spy_total_return, 4)
                m["beats_benchmark"]      = m["total_roi_pct"] > spy_total_return
            rows.append(m)

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    result = result.sort_values(
        ["passes_all", "win_rate", "profit_factor"],
        ascending=False,
    ).reset_index(drop=True)

    logger.info("Metrics computed: %d strategies, %d pass all criteria",
                len(result), result["passes_all"].sum())
    if spy_total_return is not None:
        beats = result["beats_benchmark"].sum() if "beats_benchmark" in result else 0
        logger.info("Strategies beating SPY benchmark: %d/%d", beats, len(result))
    return result


def compute_confidence_tier_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Win rate and ROI by confidence tier — validates tier ordering."""
    if df.empty or "confidence_tier" not in df:
        return pd.DataFrame()
    rows = []
    for tier in ["EXCEPTIONAL","VERY_HIGH","HIGH","MEDIUM_HIGH","MEDIUM","LOW"]:
        g = df[df["confidence_tier"] == tier]
        if g.empty:
            continue
        rows.append({
            "tier":         tier,
            "trades":       len(g),
            "win_rate":     round(g["win"].mean(), 4),
            "avg_pnl":      round(g["pnl_pct"].mean(), 4),
            "profit_factor": round(_profit_factor(g["pnl_pct"]), 4),
            "total_roi":    round(g["pnl_pct"].sum(), 4),
        })
    return pd.DataFrame(rows)
