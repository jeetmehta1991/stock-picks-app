"""
results/metrics.py  -  All 10 passing criteria computed per strategy.

Metrics per strategy (grouped by direction and hold period):
  1.  win_rate                 -  % trades profitable
  2.  profit_factor            -  total wins / total losses (threshold: 1.2)
  3.  expected_value           -  (win_rate x avg_win) + (loss_rate x avg_loss)
  4.  win_loss_ratio           -  avg win pnl / avg loss pnl
  5.  max_drawdown             -  worst peak-to-trough in equity curve
  6.  total_roi                -  sum of all pnl_pct
  7.  smart_money_lift         -  win rate with vs without smart money signal
  8.  macro_correlation        -  win rate in favourable vs unfavourable regime
  9.  trade_count              -  total trades (min 100)
  10. regimes_profitable       -  count of regimes with win rate >= 55%

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
    """Max peak-to-trough drawdown on compounded equity curve.

    BUG-15 RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10:
    Previously used `cumsum` (additive accumulation of % returns), which
    under-states drawdown after sequential losses by failing to account for
    compounding effects on capital. Now uses cumprod equity curve with proper
    drawdown formula: `(equity - peak) / peak * 100`.

    Input: per-trade % returns (e.g. 5.0 for +5% gain).
    Returns: most negative drawdown in %, rounded to 4 decimals
             (e.g. -15.5 means worst 15.5% peak-to-trough).

    For a series like [+10, -5, -10]:
      Old additive:    cumsum = [10, 5, -5];  drawdown = -15 (5 - (-15))? No, [10, 5, -5] - cummax [10,10,10] = [0, -5, -15] -> min = -15
      New compounded:  equity = [1.10, 1.045, 0.9405]; peak [1.10, 1.10, 1.10];
                       drawdown_pct = [0, -5.0, -14.50]; min = -14.50

    The compounded value is mathematically correct for a return series
    (matches industry-standard drawdown definition).
    """
    if pnl_series.empty:
        return 0.0
    equity = (1.0 + pnl_series / 100.0).cumprod()
    peak = equity.cummax()
    drawdown_pct = (equity - peak) / peak * 100.0
    return round(float(drawdown_pct.min()), 4)


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


def _sharpe(pnl_series: pd.Series, hold_days_series: pd.Series = None) -> float:
    """
    Sharpe ratio for per-trade returns  -  annualised by trades/year not sqrt(252).
    sqrt(252) is for daily returns. Per-trade returns use average hold period.
    """
    if pnl_series.std() == 0:
        return 0.0
    avg_hold = float(hold_days_series.mean()) if hold_days_series is not None and len(hold_days_series) > 0 else 10
    trades_per_year = max(1, 252 / avg_hold)
    return round(float(pnl_series.mean() / pnl_series.std() * np.sqrt(trades_per_year)), 3)


def _kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> dict:
    """
    Kelly criterion: theoretically optimal position size.
    Quarter Kelly is industry standard  -  reduces ruin risk.
    """
    if avg_loss == 0 or avg_win == 0:
        return {"full_kelly_pct": 0.0, "quarter_kelly_pct": 0.0, "note": "insufficient_data"}
    wl_ratio     = abs(avg_win / avg_loss)
    full_kelly   = win_rate - ((1 - win_rate) / wl_ratio)
    quarter_kelly = max(0.0, full_kelly / 4)
    if full_kelly < 0:     note = "negative_edge"
    elif quarter_kelly > 0.08: note = "tier_may_be_undersizing"
    elif quarter_kelly < 0.005: note = "tiny_edge"
    else:                  note = "reasonable"
    return {
        "full_kelly_pct":    round(full_kelly * 100, 2),
        "quarter_kelly_pct": round(quarter_kelly * 100, 2),
        "note": note,
    }


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
    hold_s = g["hold_days"] if "hold_days" in g.columns else pd.Series([10]*len(g))
    sharpe = _sharpe(pnl, hold_s)
    calmar = _calmar(pnl, hold_s)
    ci_lo, ci_hi = _confidence_interval_95(win_rate, n)
    statistically_random = ci_lo < 0.50  # lower CI bound below 50% = may be random

    # Sector-adjusted passing criteria  -  computed once, applied per-regime too
    from backtest.config import get_sector_criteria
    sector = g["sector"].iloc[0] if "sector" in g.columns and not g["sector"].empty else "Unknown"
    pc = get_sector_criteria(sector)

    # Per-regime evaluation  -  each regime assessed independently on all criteria
    # A strategy is valid for a regime if it passes all 9 criteria within that regime.
    # Minimum MIN_REGIME_TRADES trades required for a statistically valid verdict.
    from backtest.config import MIN_REGIME_TRADES
    regime_details  = {}
    regime_verdicts = {}   # {regime_name: "PASS"/"FAIL"/"INSUFFICIENT_DATA"}
    best_regimes    = []   # regimes where strategy passes all criteria

    for regime_name in MARKET_REGIMES:
        r_grp = g[g["regime"].str.contains(regime_name, na=False)]
        n_r   = len(r_grp)

        if n_r < MIN_REGIME_TRADES:
            regime_details[regime_name]  = {"trades": n_r, "verdict": "INSUFFICIENT_DATA"}
            regime_verdicts[regime_name] = "INSUFFICIENT_DATA"
            continue

        r_wins  = r_grp[r_grp["win"] == True]
        r_loss  = r_grp[r_grp["win"] == False]
        r_wr    = float(r_grp["win"].mean())
        r_pnl   = r_grp["pnl_pct"]
        r_pf    = _profit_factor(r_pnl)
        r_ev    = (r_wr * float(r_wins["pnl_pct"].mean() if len(r_wins) else 0)) +                   ((1 - r_wr) * float(r_loss["pnl_pct"].mean() if len(r_loss) else 0))
        r_avg_w = float(r_wins["pnl_pct"].mean()) if len(r_wins) else 0
        r_avg_l = float(r_loss["pnl_pct"].mean()) if len(r_loss) else 0
        r_wl_r  = abs(r_avg_w / r_avg_l) if r_avg_l != 0 else float("inf")
        r_mdd   = _max_drawdown(r_pnl)
        r_roi   = round(float(r_pnl.sum()), 4)
        r_hold  = r_grp["hold_days"] if "hold_days" in r_grp.columns else pd.Series([10]*n_r)
        r_ci_lo, _ = _confidence_interval_95(r_wr, n_r)

        # Evaluate all 9 criteria (same sector-adjusted thresholds as overall)
        r_passes = {
            "win_rate":       r_wr >= pc["min_win_rate"],
            "profit_factor":  r_pf >= pc["min_profit_factor"],
            "expected_value": r_ev > pc["min_expected_value"],
            "win_loss_ratio": r_wl_r >= pc["min_win_loss_ratio"],
            "max_drawdown":   r_mdd >= -pc["max_drawdown"],
            "total_roi":      r_roi > pc["min_total_roi"],
            "trade_count":    n_r >= MIN_REGIME_TRADES,
            "smart_money_lift":  True,   # SM lift computed at strategy level, not per-regime
            "macro_correlation": True,   # macro corr computed at strategy level, not per-regime
        }
        # Also require CI lower bound above 40% to avoid purely statistical noise
        if r_ci_lo < 0.40:
            r_passes["win_rate"] = False

        verdict = "PASS" if all(r_passes.values()) else "FAIL"
        if verdict == "PASS":
            best_regimes.append(regime_name)

        regime_verdicts[regime_name] = verdict
        regime_details[regime_name]  = {
            "trades":       n_r,
            "win_rate":     round(r_wr, 4),
            "profit_factor": round(r_pf, 4),
            "avg_pnl":      round(float(r_pnl.mean()), 4),
            "total_roi":    r_roi,
            "max_drawdown": round(r_mdd, 4),
            "verdict":      verdict,
            "passes":       r_passes,
        }

    # Legacy count for backward compatibility (number of PASS regimes)
    regimes_profitable = len(best_regimes)

    # Smart money lift  -  within-strategy comparison (correct method)
    # Isolate SM contribution by holding strategy constant
    has_sm = g[g["smart_money_score"] >= 2]
    no_sm  = g[g["smart_money_score"] < 2]
    sm_lift = None
    if len(has_sm) >= 30 and len(no_sm) >= 30:
        sm_lift = round(float(has_sm["win"].mean()) - float(no_sm["win"].mean()), 4)

    # Macro correlation  -  defined threshold
    fav_macro   = g[g["macro_score"] >= 2]
    unfav_macro = g[g["macro_score"] < 0]
    macro_corr = None
    if len(fav_macro) >= 20 and len(unfav_macro) >= 20:
        macro_corr = round(float(fav_macro["win"].mean()) - float(unfav_macro["win"].mean()), 4)


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
        # regime_verdicts replaces per-regime count  -  see regime_verdicts and best_regimes
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
        "kelly":                 _kelly_criterion(win_rate, avg_win, abs(avg_loss)),
        "avg_hold_days":         round(float(g["hold_days"].mean()), 1) if "hold_days" in g else 0,
        "best_trade_pct":        round(float(pnl.max()), 4),
        "worst_trade_pct":       round(float(pnl.min()), 4),
        "smart_money_lift":      sm_lift,
        "macro_correlation":     macro_corr,
        "regimes_profitable":    regimes_profitable,
        "regime_verdicts":       regime_verdicts,
        "best_regimes":          best_regimes,
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

    # Flatten regime_verdicts into individual columns for easy CSV analysis
    from backtest.config import MARKET_REGIMES
    for regime_name in MARKET_REGIMES:
        col = f"regime_{regime_name}"
        result[col] = result["regime_verdicts"].apply(
            lambda rv: rv.get(regime_name, "INSUFFICIENT_DATA") if isinstance(rv, dict) else "INSUFFICIENT_DATA"
        )

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
    """Win rate and ROI by confidence tier  -  validates tier ordering."""
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


def compute_portfolio_summary(
    df_trades: pd.DataFrame,
    reference_capital: float = 100_000.0,
    tier_sizes: dict = None,
) -> dict:
    """
    Compute portfolio-level metrics applying tier-based position sizing.
    
    All backtest P&L metrics are per-strategy averages. This function
    computes what a real portfolio would have returned if position sizes
    matched confidence tiers.
    
    reference_capital: starting capital in CAD (default $100k)
    tier_sizes: % allocation per tier {EXCEPTIONAL:0.05, VERY_HIGH:0.04, ...}
    """
    if tier_sizes is None:
        tier_sizes = {
            "EXCEPTIONAL": 0.05, "VERY_HIGH": 0.04, "HIGH": 0.03,
            "MEDIUM_HIGH": 0.015, "MEDIUM": 0.0075, "LOW": 0.0,
        }
    if df_trades.empty:
        return {}

    df = df_trades.copy()
    df["position_size_pct"] = df["confidence_tier"].map(
        lambda t: tier_sizes.get(t, 0.01))
    df["position_dollar"]   = df["position_size_pct"] * reference_capital
    df["pnl_dollar_sized"]  = df["pnl_pct"] / 100 * df["position_dollar"]

    total_pnl   = df["pnl_dollar_sized"].sum()
    portfolio_return_pct = total_pnl / reference_capital * 100

    # Portfolio heat: max simultaneous open risk
    # Approximate: sum of position sizes for all trades open on busiest day
    if "entry_date" in df.columns and "exit_date" in df.columns:
        df["entry_date"] = pd.to_datetime(df["entry_date"])
        df["exit_date"]  = pd.to_datetime(df["exit_date"])
        # Count simultaneous open trades per day
        all_dates = pd.date_range(df["entry_date"].min(), df["exit_date"].max(), freq="B")
        max_heat = 0
        for d in all_dates:
            open_on_day = df[(df["entry_date"] <= d) & (df["exit_date"] >= d)]
            heat = open_on_day["position_size_pct"].sum() * 100
            max_heat = max(max_heat, heat)
    else:
        max_heat = 0

    return {
        "reference_capital_cad": reference_capital,
        "total_pnl_dollar":      round(total_pnl, 2),
        "portfolio_return_pct":  round(portfolio_return_pct, 2),
        "max_portfolio_heat_pct": round(max_heat, 1),
        "avg_position_size_pct": round(float(df["position_size_pct"].mean()) * 100, 2),
        "note": "Portfolio return applies tier-based position sizing to all trades",
    }
