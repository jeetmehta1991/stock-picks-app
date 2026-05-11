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


def _adf_test(equity_curve: pd.Series, alpha: float = 0.05) -> dict:
    """DEC-414 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 41 2026-05-11
    (owner-approved Path B Step B - statsmodels dependency).

    Augmented Dickey-Fuller stationarity test on a per-strategy equity curve.
    H0: series has unit root (non-stationary). H1: series is stationary.
    Reject H0 (p < alpha) -> stationary -> strategy edge is consistent.
    Fail to reject H0 -> non-stationary -> edge erosion / drift over time.

    Inputs:
      equity_curve: pd.Series of cumulative pnl (compounded equity)
      alpha: significance level (default 0.05)

    Returns dict with adf_statistic, p_value, is_stationary (bool), critical
    values, note (insufficient_sample if n<20, ok if test ran).
    """
    if equity_curve.empty or len(equity_curve) < 20:
        return {
            "adf_statistic": None, "adf_p_value": None,
            "is_stationary": None, "note": "insufficient_sample",
        }
    try:
        from statsmodels.tsa.stattools import adfuller
        # autolag=AIC to choose lag order; series dropped NaN
        series = equity_curve.dropna()
        if len(series) < 20:
            return {
                "adf_statistic": None, "adf_p_value": None,
                "is_stationary": None, "note": "insufficient_sample",
            }
        result = adfuller(series, autolag="AIC")
        adf_stat = float(result[0])
        p_value = float(result[1])
        is_stat = p_value < alpha
        return {
            "adf_statistic": round(adf_stat, 4),
            "adf_p_value":   round(p_value, 4),
            "is_stationary": is_stat,
            "note": "ok" if is_stat else "non_stationary_edge_may_erode",
        }
    except Exception as exc:
        return {
            "adf_statistic": None, "adf_p_value": None,
            "is_stationary": None, "note": f"adf_failed_{type(exc).__name__}",
        }


def _chow_test(equity_curve: pd.Series, split_idx: int = None, alpha: float = 0.05) -> dict:
    """DEC-416 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 41 2026-05-11
    (owner-approved Path B Step B).

    Chow split-sample structural break test on equity curve. Linear models
    fit before and after split_idx; F-test rejects "same slope/intercept".
    Reject -> structural break (regime-change in strategy behavior).

    Inputs:
      equity_curve: pd.Series of equity values
      split_idx: index to split sample (default = len/2)
      alpha: significance level (default 0.05)

    Returns dict with chow_f, chow_p, has_structural_break (bool), note.
    Requires n>=20 with at least 5 obs on each side of split.
    """
    if equity_curve.empty or len(equity_curve) < 20:
        return {
            "chow_f_statistic": None, "chow_p_value": None,
            "has_structural_break": None, "note": "insufficient_sample",
        }
    if split_idx is None:
        split_idx = len(equity_curve) // 2
    if split_idx < 5 or (len(equity_curve) - split_idx) < 5:
        return {
            "chow_f_statistic": None, "chow_p_value": None,
            "has_structural_break": None, "note": "insufficient_split_subsets",
        }
    try:
        import statsmodels.api as sm
        from scipy.stats import f as f_dist
        series = equity_curve.dropna().reset_index(drop=True)
        if len(series) < 20:
            return {
                "chow_f_statistic": None, "chow_p_value": None,
                "has_structural_break": None, "note": "insufficient_sample",
            }
        n = len(series)
        x_all = sm.add_constant(np.arange(n).astype(float))
        x1 = sm.add_constant(np.arange(split_idx).astype(float))
        x2 = sm.add_constant(np.arange(n - split_idx).astype(float))
        y_all = series.values
        y1 = series.values[:split_idx]
        y2 = series.values[split_idx:]
        # Pooled vs separate residual sum of squares
        rss_all = float(sm.OLS(y_all, x_all).fit().ssr)
        rss1 = float(sm.OLS(y1, x1).fit().ssr)
        rss2 = float(sm.OLS(y2, x2).fit().ssr)
        k = 2  # parameters: intercept + slope
        # Chow F-statistic: ((RSS_pooled - (RSS1 + RSS2)) / k) / ((RSS1 + RSS2) / (n - 2*k))
        rss_split = rss1 + rss2
        denom_df = n - 2 * k
        if denom_df <= 0 or rss_split <= 0:
            return {
                "chow_f_statistic": None, "chow_p_value": None,
                "has_structural_break": None, "note": "denom_invalid",
            }
        f_stat = ((rss_all - rss_split) / k) / (rss_split / denom_df)
        # p-value from F-distribution with (k, n-2k) df
        p_value = 1.0 - float(f_dist.cdf(f_stat, k, denom_df))
        has_break = (p_value < alpha) and (f_stat > 0)
        return {
            "chow_f_statistic": round(f_stat, 4),
            "chow_p_value":     round(p_value, 4),
            "has_structural_break": has_break,
            "note": "structural_break_detected" if has_break else "no_structural_break",
        }
    except Exception as exc:
        return {
            "chow_f_statistic": None, "chow_p_value": None,
            "has_structural_break": None, "note": f"chow_failed_{type(exc).__name__}",
        }


def _time_in_market_metrics(df_trades: pd.DataFrame,
                            start_date=None, end_date=None) -> dict:
    """DEC-241 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 40 2026-05-11
    (owner-approved Path C). Time-in-market metric: % of trading days with
    at least 1 position open / % long / % short / % cash.

    Inputs:
      df_trades: DataFrame with entry_date, exit_date, direction columns
      start_date: optional override (default: min entry_date in df)
      end_date: optional override (default: max exit_date in df)

    Returns dict with time_in_market_pct, pct_days_long, pct_days_short,
    pct_days_cash. All percent values 0-100.
    """
    if df_trades.empty:
        return {
            "time_in_market_pct": 0.0,
            "pct_days_long":      0.0,
            "pct_days_short":     0.0,
            "pct_days_cash":      100.0,
            "total_trading_days": 0,
        }
    df = df_trades.copy()
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df["exit_date"] = pd.to_datetime(df["exit_date"])
    if start_date is None:
        start_date = df["entry_date"].min()
    if end_date is None:
        end_date = df["exit_date"].max()
    all_days = pd.date_range(start_date, end_date, freq="B")  # business days
    if len(all_days) == 0:
        return {
            "time_in_market_pct": 0.0, "pct_days_long": 0.0,
            "pct_days_short": 0.0, "pct_days_cash": 100.0,
            "total_trading_days": 0,
        }

    open_days = set()
    long_days = set()
    short_days = set()
    for _, t in df.iterrows():
        days = pd.date_range(t["entry_date"], t["exit_date"], freq="B")
        days_dt = set(d.normalize() for d in days)
        open_days |= days_dt
        if t.get("direction") == "long":
            long_days |= days_dt
        elif t.get("direction") == "short":
            short_days |= days_dt
    all_days_normalized = set(d.normalize() for d in all_days)
    in_market = len(open_days & all_days_normalized)
    in_long = len(long_days & all_days_normalized)
    in_short = len(short_days & all_days_normalized)
    total = len(all_days_normalized)
    return {
        "time_in_market_pct": round(in_market / total * 100, 2) if total > 0 else 0.0,
        "pct_days_long":      round(in_long / total * 100, 2) if total > 0 else 0.0,
        "pct_days_short":     round(in_short / total * 100, 2) if total > 0 else 0.0,
        "pct_days_cash":      round((total - in_market) / total * 100, 2) if total > 0 else 100.0,
        "total_trading_days": total,
    }


def _event_window_breakdown(df_trades: pd.DataFrame, window_days: int = 3) -> dict:
    """DEC-409 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 40 2026-05-11
    (owner-approved Path C). Event-window breakdown: % trades entered near
    FOMC / CPI / NFP. Uses backtest.data.macro.is_near_high_impact_event.

    Inputs:
      df_trades: DataFrame with entry_date column
      window_days: event proximity window (default 3 days on each side)

    Returns dict with pct_trades_near_event + per-event-type breakdown.
    Caller-side wins/losses split via _event_conditional_win_rate (DEC-408).
    """
    if df_trades.empty:
        return {
            "pct_trades_near_event": 0.0,
            "pct_trades_near_fomc":  0.0,
            "pct_trades_near_cpi":   0.0,
            "pct_trades_near_nfp":   0.0,
            "n_trades_near_event":   0,
        }
    try:
        from backtest.data.macro import is_near_high_impact_event
    except ImportError:
        return {
            "pct_trades_near_event": None,
            "pct_trades_near_fomc":  None,
            "pct_trades_near_cpi":   None,
            "pct_trades_near_nfp":   None,
            "n_trades_near_event":   None,
        }
    n = len(df_trades)
    near_event = 0
    near_fomc = 0
    near_cpi = 0
    near_nfp = 0
    for _, trade in df_trades.iterrows():
        try:
            ed = pd.to_datetime(trade["entry_date"]).date()
            event = is_near_high_impact_event(ed, window_days=window_days)
            if event.get("blocked"):
                near_event += 1
                et = event.get("nearest_event_type")
                if et == "FOMC":
                    near_fomc += 1
                elif et == "CPI":
                    near_cpi += 1
                elif et == "NFP":
                    near_nfp += 1
        except Exception:
            continue
    return {
        "pct_trades_near_event": round(near_event / n * 100, 2),
        "pct_trades_near_fomc":  round(near_fomc / n * 100, 2),
        "pct_trades_near_cpi":   round(near_cpi / n * 100, 2),
        "pct_trades_near_nfp":   round(near_nfp / n * 100, 2),
        "n_trades_near_event":   near_event,
    }


def _event_conditional_win_rate(df_trades: pd.DataFrame, window_days: int = 3) -> dict:
    """DEC-408 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 40 2026-05-11
    (owner-approved Path C). Comprehensive macro correlation: per-strategy
    win rates on event-adjacent vs non-event-adjacent days.

    For each trade, classify by event proximity (FOMC/CPI/NFP within
    window_days). Compute win rate for each bucket. Returns delta which
    surfaces edge presence/absence near events.

    Returns dict with win_rate_near_event, win_rate_far_from_event,
    win_rate_delta (near - far). Positive delta = strategy outperforms
    near events; negative = strategy underperforms near events.
    """
    if df_trades.empty or len(df_trades) < 6:
        return {
            "win_rate_near_event":     None,
            "win_rate_far_from_event": None,
            "win_rate_event_delta":    None,
            "n_trades_near_event":     0,
            "n_trades_far_from_event": 0,
            "note": "insufficient_sample",
        }
    try:
        from backtest.data.macro import is_near_high_impact_event
    except ImportError:
        return {
            "win_rate_near_event":     None,
            "win_rate_far_from_event": None,
            "win_rate_event_delta":    None,
            "n_trades_near_event":     0,
            "n_trades_far_from_event": 0,
            "note": "macro_module_unavailable",
        }
    near_wins, near_total, far_wins, far_total = 0, 0, 0, 0
    for _, trade in df_trades.iterrows():
        try:
            ed = pd.to_datetime(trade["entry_date"]).date()
            event = is_near_high_impact_event(ed, window_days=window_days)
            won = bool(trade.get("win", False))
            if event.get("blocked"):
                near_total += 1
                if won:
                    near_wins += 1
            else:
                far_total += 1
                if won:
                    far_wins += 1
        except Exception:
            continue
    wr_near = (near_wins / near_total) if near_total > 0 else None
    wr_far = (far_wins / far_total) if far_total > 0 else None
    delta = None
    if wr_near is not None and wr_far is not None:
        delta = wr_near - wr_far
    note = "ok"
    if near_total < 5 or far_total < 5:
        note = "small_subgroup"
    return {
        "win_rate_near_event":     round(wr_near, 4) if wr_near is not None else None,
        "win_rate_far_from_event": round(wr_far, 4) if wr_far is not None else None,
        "win_rate_event_delta":    round(delta, 4) if delta is not None else None,
        "n_trades_near_event":     near_total,
        "n_trades_far_from_event": far_total,
        "note": note,
    }


def _sharpe_daily(pnl_series: pd.Series, entry_date_series: pd.Series,
                  exit_date_series: pd.Series) -> float:
    """Daily-returns-based Sharpe ratio (DEC-081 Phase A canonicalization).

    DEC-402 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 39 2026-05-11
    (owner-approved Path C). Distinct from _sharpe (per-trade form).

    Methodology: distribute each trade's pnl evenly across its hold-day
    range, sum per-day pnl across overlapping trades, compute daily-return
    series, then annualize Sharpe via sqrt(252).

    Note: this is a simplified daily-Sharpe approximation; full daily-mark-to-
    market Sharpe would require per-day price data (handled by Portfolio
    class equity_curve in BUG-95 + the compute_portfolio_metrics_from_curves
    output - this helper is a strategy-level proxy).

    Inputs:
      pnl_series: per-trade pnl_pct
      entry_date_series: per-trade entry_date
      exit_date_series: per-trade exit_date

    Returns: round to 3 decimals. 0.0 on insufficient data.
    """
    if pnl_series.empty or len(pnl_series) < 2:
        return 0.0
    try:
        # Build daily aggregation
        entry_dates = pd.to_datetime(entry_date_series)
        exit_dates = pd.to_datetime(exit_date_series)
        if entry_dates.isna().any() or exit_dates.isna().any():
            return 0.0
        # For each trade, distribute pnl evenly across hold days
        daily_pnl = {}
        for i in range(len(pnl_series)):
            ed = entry_dates.iloc[i]
            xd = exit_dates.iloc[i]
            p = float(pnl_series.iloc[i])
            n_days = max(1, (xd - ed).days + 1)
            per_day = p / n_days
            for offset in range(n_days):
                d = ed + pd.Timedelta(days=offset)
                daily_pnl[d] = daily_pnl.get(d, 0.0) + per_day
        if len(daily_pnl) < 2:
            return 0.0
        daily_returns = pd.Series(list(daily_pnl.values()))
        if daily_returns.std(ddof=1) == 0:
            return 0.0
        sharpe = float(daily_returns.mean() / daily_returns.std(ddof=1) * np.sqrt(252))
        if np.isnan(sharpe) or np.isinf(sharpe):
            return 0.0
        return round(min(sharpe, 999.0), 3)
    except Exception:
        return 0.0


def _sortino_ratio(pnl_series: pd.Series, hold_days_series: pd.Series = None) -> float:
    """Sortino ratio: like Sharpe but uses downside deviation only.

    DEC-403 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 38 2026-05-11
    (owner-approved Path C: Statistical Methodology implementation).

    Annualised by trades/year (same convention as _sharpe).
    Formula: Sortino = mean(returns) / downside_std * sqrt(trades_per_year)
    where downside_std = std of returns < 0 (negative returns only).

    Returns: round to 3 decimals. 0.0 if no downside (all wins) or no trades.
    Inf returns capped at 999 for serialization safety.
    """
    if pnl_series.empty:
        return 0.0
    downside = pnl_series[pnl_series < 0]
    if downside.empty:
        return 999.0  # capped inf - no losses means infinite Sortino
    downside_std = float(downside.std(ddof=1)) if len(downside) > 1 else float(abs(downside.iloc[0]))
    if downside_std == 0:
        return 999.0
    avg_hold = float(hold_days_series.mean()) if hold_days_series is not None and len(hold_days_series) > 0 else 10
    trades_per_year = max(1, 252 / avg_hold)
    ratio = float(pnl_series.mean() / downside_std * np.sqrt(trades_per_year))
    if np.isnan(ratio) or np.isinf(ratio):
        return 0.0
    return round(min(ratio, 999.0), 3)


def _deflated_sharpe(sharpe: float, n_trades: int, skew: float, kurtosis: float) -> dict:
    """Deflated Sharpe ratio + Probabilistic Sharpe Ratio (PSR).

    DEC-110 + DEC-413 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 38
    2026-05-11 (owner-approved Path C). Bailey & Lopez de Prado (2014).

    PSR(SR*) = Pr(SR > SR*) given finite sample size, non-normal distribution.
    Formula: PSR = Phi((SR - SR*) * sqrt(n-1) / sqrt(1 - skew*SR + (kurtosis-1)/4 * SR^2))

    Inputs:
      sharpe: realised per-trade Sharpe ratio (annualised)
      n_trades: trade count (sample size)
      skew: skewness of trade pnl distribution
      kurtosis: excess kurtosis of trade pnl distribution

    SR_star (the benchmark Sharpe we test against) = 0 (testing "is Sharpe > 0?").

    Returns dict with psr (probability), deflated_sharpe (SR after adjustment),
    and note flagging low-confidence cases.
    """
    if n_trades < 30 or sharpe == 0:
        return {"psr": None, "deflated_sharpe": None, "note": "insufficient_sample"}
    # Skew and kurtosis NaN-safe defaults
    if pd.isna(skew) or pd.isna(kurtosis):
        skew = 0.0
        kurtosis = 3.0  # normal kurtosis baseline
    excess_kurt = kurtosis - 3.0 if kurtosis >= 3.0 else 0.0
    try:
        from scipy.stats import norm
        denominator_sq = 1.0 - skew * sharpe + (excess_kurt / 4.0) * sharpe**2
        if denominator_sq <= 0:
            return {"psr": None, "deflated_sharpe": None, "note": "denominator_invalid"}
        denom = (denominator_sq / (n_trades - 1)) ** 0.5
        z = sharpe / denom if denom > 0 else 0
        psr = float(norm.cdf(z))
        deflated = sharpe * (1.0 - (excess_kurt / 4.0) * sharpe**2) ** 0.5
        if np.isnan(deflated) or np.isinf(deflated):
            deflated = None
        return {
            "psr": round(psr, 4),
            "deflated_sharpe": round(deflated, 4) if deflated is not None else None,
            "note": "ok" if psr >= 0.95 else ("low_confidence" if psr < 0.80 else "moderate"),
        }
    except ImportError:
        # scipy not available - compute psr via numpy normal CDF approximation
        # Erfc-based normal CDF: 0.5 * (1 + erf(x / sqrt(2)))
        from math import erf, sqrt
        denominator_sq = 1.0 - skew * sharpe + (excess_kurt / 4.0) * sharpe**2
        if denominator_sq <= 0:
            return {"psr": None, "deflated_sharpe": None, "note": "denominator_invalid"}
        denom = (denominator_sq / (n_trades - 1)) ** 0.5
        z = sharpe / denom if denom > 0 else 0
        psr = 0.5 * (1.0 + erf(z / sqrt(2.0)))
        deflated = sharpe * (1.0 - (excess_kurt / 4.0) * sharpe**2) ** 0.5 if denominator_sq > 0 else None
        return {
            "psr": round(psr, 4),
            "deflated_sharpe": round(deflated, 4) if deflated is not None else None,
            "note": "ok" if psr >= 0.95 else ("low_confidence" if psr < 0.80 else "moderate"),
        }


def _cost_sensitivity_sharpe(pnl_series: pd.Series, hold_days_series: pd.Series = None,
                              cost_levels_bps: list = None) -> dict:
    """Compute Sharpe at multiple transaction cost levels.

    DEC-404 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 38 2026-05-11
    (owner-approved Path C: DEC-081 Phase C transaction cost sensitivity).

    Defaults to 4 cost levels: 0, 5, 10, 20 bps per round-trip trade.
    For each level, deduct cost_bps/100 (in pct) from each trade's pnl and
    recompute Sharpe. Helps owner see how performance degrades with realistic
    transaction costs (per Anthropic Q3 owner directive for honest reporting).

    Returns dict with keys sharpe_at_0bps, sharpe_at_5bps, sharpe_at_10bps,
    sharpe_at_20bps.
    """
    if cost_levels_bps is None:
        cost_levels_bps = [0, 5, 10, 20]
    out = {}
    for bps in cost_levels_bps:
        cost_pct = bps / 100.0   # 5 bps = 0.05% per trade
        adjusted = pnl_series - cost_pct
        out[f"sharpe_at_{bps}bps"] = _sharpe(adjusted, hold_days_series)
    return out


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


def detect_strategy_decay(
    sharpe_baseline: float,
    sharpe_recent: float,
    drop_threshold: float = 0.5,
) -> dict:
    """DEC-249 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 55 2026-05-11
    (owner-approved Path C 5-DEC bundle). Strategy decay metric per Pass 52
    turn 117 owner spec: flag STRATEGY_DECAY_WARNING when rolling 6-month
    Sharpe drops > drop_threshold fraction from baseline (default 50%).

    Inputs:
      sharpe_baseline: full-period or pre-decay-window Sharpe
      sharpe_recent: rolling 6mo (or whatever recent window) Sharpe
      drop_threshold: fractional drop to flag (default 0.5 = 50%)

    Returns dict with is_decayed (bool), drop_pct (float -- can exceed 1.0
    when sharpe flips sign), note (str). Handles edge cases: baseline <= 0
    -> note 'no_baseline_to_compare'; recent improves on baseline ->
    is_decayed=False with negative drop_pct.

    Joint with DEC-214 (quarterly re-validation) — decay flag triggers
    full A/B re-validation when consumed downstream.
    """
    if sharpe_baseline is None or sharpe_recent is None:
        return {"is_decayed": False, "drop_pct": None, "note": "missing_input"}
    if sharpe_baseline <= 0:
        return {"is_decayed": False, "drop_pct": None,
                "note": "no_baseline_to_compare"}
    drop_pct = (sharpe_baseline - sharpe_recent) / sharpe_baseline
    is_decayed = drop_pct > drop_threshold
    return {
        "is_decayed": bool(is_decayed),
        "drop_pct":   round(float(drop_pct), 4),
        "note":       "STRATEGY_DECAY_WARNING" if is_decayed else "ok",
    }


def decompose_trade_pnl(
    actual_pnl_dollar: float,
    timing_delta_dollar: float = 0.0,
    exit_delta_dollar: float = 0.0,
    sizing_delta_dollar: float = 0.0,
    agent_delta_dollar: float = 0.0,
) -> dict:
    """DEC-279 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 54 2026-05-11
    (owner-approved Path C bundle; sandbox-prototype scope per spec).

    5-component decomposition of a single trade's realized P&L:
      (1) signal     - residual P&L if no overlays applied
      (2) timing     - delta vs idealized entry (actual entry late/early)
      (3) exit       - delta vs idealized exit (over-/under-stayed)
      (4) sizing     - delta vs equal-weight baseline sizing
      (5) agent      - delta from agent overlay vs rules-only baseline

    The function takes the 4 derived-delta inputs and SOLVES for signal as:
      signal = actual_pnl - (timing + exit + sizing + agent)
    so the 5 components sum to actual_pnl by construction (test-signal
    invariant per DEC-279 spec).

    Inputs are signed dollar deltas. Positive = additive to P&L; negative =
    drag. Idealized baselines (signal-driven entry, perfect exit, equal-
    weight sizing, rules-only baseline) are caller-supplied as deltas;
    sandbox prototype intentionally avoids prescribing the idealization
    methodology pending Phase 1B-alpha validation.

    Returns dict with 5 contributions + actual_total_check (round-trip
    sum validator).
    """
    derived = (timing_delta_dollar + exit_delta_dollar
               + sizing_delta_dollar + agent_delta_dollar)
    signal = actual_pnl_dollar - derived
    return {
        "signal_contribution":  round(signal, 4),
        "timing_contribution":  round(timing_delta_dollar, 4),
        "exit_contribution":    round(exit_delta_dollar, 4),
        "sizing_contribution":  round(sizing_delta_dollar, 4),
        "agent_contribution":   round(agent_delta_dollar, 4),
        "actual_total_check":   round(signal + derived, 4),
    }


def _aep_pct_metric(df_trades: pd.DataFrame) -> dict:
    """DEC-435 / DEC-075 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 49
    2026-05-11 (owner-approved Path C). Adverse Exit Pct (AEP): per-trade
    exit-distance-from-peak. Lower = exit near peak (better); higher = more
    giveback. Formula per DEC-435: `(mfe - exit_pnl) / mfe` for winning trades
    only (pnl > 0; mfe >= pnl > 0 so AEP is bounded [0, 1)). Losing trades
    skipped (would yield AEP > 1, distorting mean). POOR_EXIT_TIMING flag
    raised when mean_aep_pct > 0.5 (mean exit gives back >50% of peak).

    Inputs:
      df_trades: DataFrame with pnl_pct + max_favourable_excursion columns

    Returns dict with avg_aep_pct (mean across winners), n_aep_eligible
    (count of winners with mfe > 0), poor_exit_timing (bool), aep_note.
    """
    if df_trades.empty or "max_favourable_excursion" not in df_trades.columns:
        return {
            "avg_aep_pct": None, "n_aep_eligible": 0,
            "poor_exit_timing": False, "aep_note": "no_mfe_column",
        }
    mfe = pd.to_numeric(df_trades["max_favourable_excursion"], errors="coerce")
    pnl = pd.to_numeric(df_trades["pnl_pct"], errors="coerce")
    eligible = (pnl > 0) & (mfe > 0) & mfe.notna() & pnl.notna()
    n_eligible = int(eligible.sum())
    if n_eligible == 0:
        return {
            "avg_aep_pct": None, "n_aep_eligible": 0,
            "poor_exit_timing": False, "aep_note": "no_winning_trades_with_mfe",
        }
    aep = (mfe[eligible] - pnl[eligible]) / mfe[eligible]
    mean_aep = round(float(aep.mean()), 4)
    return {
        "avg_aep_pct":      mean_aep,
        "n_aep_eligible":   n_eligible,
        "poor_exit_timing": bool(mean_aep > 0.5),
        "aep_note":         "ok",
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
    # DEC-403 + DEC-110/413 + DEC-404 RESOLVED-IMPLEMENTED Pass 53 v8h+1
    # Phase 3 Batch 38 2026-05-11 (owner-approved Path C statistical
    # methodology). Sortino (downside-deviation-only), Deflated Sharpe (PSR
    # per Bailey 2014), and cost-sensitivity Sharpe at 0/5/10/20 bps.
    sortino = _sortino_ratio(pnl, hold_s)
    # DEC-081 Phase A / DEC-402 Sharpe canonicalization: daily-Sharpe alongside
    # per-trade Sharpe. Sharpe (above) uses per-trade form; sharpe_daily uses
    # daily-distributed pnl annualized via sqrt(252).
    if "entry_date" in g.columns and "exit_date" in g.columns:
        sharpe_daily = _sharpe_daily(pnl, g["entry_date"], g["exit_date"])
    else:
        sharpe_daily = None
    # DEC-409 event-window breakdown (% trades near FOMC/CPI/NFP)
    event_bd = _event_window_breakdown(g)
    # DEC-408 event-conditional win rates (delta near vs far from event)
    event_wr = _event_conditional_win_rate(g)
    # DEC-414 ADF stationarity test + DEC-416 Chow structural break test
    # on the per-strategy compounded equity curve (DEC-111 children).
    equity_curve = (1.0 + pnl / 100.0).cumprod()
    adf_result = _adf_test(equity_curve)
    chow_result = _chow_test(equity_curve)
    try:
        skew_val = float(pnl.skew()) if len(pnl) >= 3 else 0.0
        kurt_val = float(pnl.kurt()) if len(pnl) >= 4 else 3.0
    except Exception:
        skew_val, kurt_val = 0.0, 3.0
    psr_dict = _deflated_sharpe(sharpe, n, skew_val, kurt_val)
    cost_sensitivity = _cost_sensitivity_sharpe(pnl, hold_s)
    # DEC-435 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 49 2026-05-11.
    # Adverse Exit Pct (mean giveback from MFE) for exit-quality assessment.
    aep_dict = _aep_pct_metric(g)

    # DEC-083 + DEC-406 tiered min-trades enforcement. Map strategy category
    # to tiered threshold; passes_all uses the tiered threshold instead of
    # generic pc["min_trades"].
    from backtest.config import TIERED_MIN_TRADES
    category = g["category"].iloc[0] if "category" in g.columns and not g["category"].empty else ""
    cat_lower = category.lower()
    if "intraday" in cat_lower:
        tiered_min = TIERED_MIN_TRADES["intraday"]
    elif "pivot" in cat_lower:
        tiered_min = TIERED_MIN_TRADES["pivot"]
    elif "swing" in cat_lower:
        tiered_min = TIERED_MIN_TRADES["swing"]
    elif "earnings" in cat_lower or "event" in cat_lower:
        tiered_min = TIERED_MIN_TRADES["earnings_event"]
    elif "calendar" in cat_lower or "seasonal" in cat_lower:
        tiered_min = TIERED_MIN_TRADES["calendar"]
    elif cat_lower in ("trend", "momentum", "mean_reversion", "breakout", "confluence", "candle", "daily"):
        tiered_min = TIERED_MIN_TRADES["daily"]
    else:
        tiered_min = TIERED_MIN_TRADES["default"]
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
        "sharpe_daily":          sharpe_daily,
        "sortino_ratio":         sortino,
        "deflated_sharpe":       psr_dict.get("deflated_sharpe"),
        "psr":                   psr_dict.get("psr"),
        "psr_note":              psr_dict.get("note"),
        "tiered_min_trades":     tiered_min,
        "meets_tiered_min":      n >= tiered_min,
        # DEC-409 event-window breakdown
        "pct_trades_near_event": event_bd.get("pct_trades_near_event"),
        "pct_trades_near_fomc":  event_bd.get("pct_trades_near_fomc"),
        "pct_trades_near_cpi":   event_bd.get("pct_trades_near_cpi"),
        "pct_trades_near_nfp":   event_bd.get("pct_trades_near_nfp"),
        # DEC-408 event-conditional win rates
        "win_rate_near_event":     event_wr.get("win_rate_near_event"),
        "win_rate_far_from_event": event_wr.get("win_rate_far_from_event"),
        "win_rate_event_delta":    event_wr.get("win_rate_event_delta"),
        "event_wr_note":           event_wr.get("note"),
        # DEC-414 ADF stationarity
        "adf_statistic":         adf_result.get("adf_statistic"),
        "adf_p_value":           adf_result.get("adf_p_value"),
        "is_stationary":         adf_result.get("is_stationary"),
        "adf_note":              adf_result.get("note"),
        # DEC-416 Chow structural break
        "chow_f_statistic":      chow_result.get("chow_f_statistic"),
        "chow_p_value":          chow_result.get("chow_p_value"),
        "has_structural_break":  chow_result.get("has_structural_break"),
        "chow_note":             chow_result.get("note"),
        "sharpe_at_0bps":        cost_sensitivity.get("sharpe_at_0bps"),
        "sharpe_at_5bps":        cost_sensitivity.get("sharpe_at_5bps"),
        "sharpe_at_10bps":       cost_sensitivity.get("sharpe_at_10bps"),
        "sharpe_at_20bps":       cost_sensitivity.get("sharpe_at_20bps"),
        # DEC-435 / DEC-075 Adverse Exit Pct (exit-quality telemetry + flag)
        "avg_aep_pct":           aep_dict.get("avg_aep_pct"),
        "n_aep_eligible":        aep_dict.get("n_aep_eligible"),
        "poor_exit_timing":      aep_dict.get("poor_exit_timing"),
        "aep_note":              aep_dict.get("aep_note"),
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


# ============================================================================
# BUG-95 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 20 Sub-batch 3/5
# 2026-05-10 (owner-approved Option A): true portfolio metrics computed from
# the Portfolio.equity_curve + Portfolio.benchmark_curve (NOT from per-trade
# pnl_pct summation). This is the canonical portfolio-level Sharpe / alpha
# / beta / IR / tracking-error implementation.
#
# Inputs (typically from engine.portfolio):
#   equity_curve:    list[(date, equity_dollar)]   -- self.portfolio.equity_curve
#   benchmark_curve: list[(date, benchmark_close)] -- self.portfolio.benchmark_curve
#   starting_capital: float (CAD) -- self.portfolio.starting_capital
#
# Output dict keys:
#   portfolio_total_return_pct   -- final/starting - 1 (%)
#   portfolio_sharpe             -- annualized Sharpe of daily portfolio returns
#                                   (assumes 252 trading days, risk-free = 0;
#                                    matches industry baseline)
#   portfolio_max_drawdown_pct   -- worst peak-to-trough on equity_curve
#   benchmark_total_return_pct   -- SPY total return over same window
#   alpha_annualized_pct         -- portfolio_ann_return - beta * benchmark_ann_return
#   beta_to_benchmark            -- cov(port, bench) / var(bench)
#   tracking_error_pct           -- std(port_daily - bench_daily) * sqrt(252) * 100
#   information_ratio            -- excess_return / tracking_error
# ============================================================================

def _daily_returns_from_curve(curve: list) -> "pd.Series":
    """Convert [(date, value), ...] list to a Series of daily simple returns."""
    if not curve or len(curve) < 2:
        return pd.Series(dtype=float)
    dates = [pt[0] for pt in curve]
    values = [float(pt[1]) for pt in curve]
    s = pd.Series(values, index=pd.DatetimeIndex(dates))
    # Drop duplicates if any (engine may double-mark a day on partial data)
    s = s[~s.index.duplicated(keep="last")]
    rets = s.pct_change().dropna()
    return rets


def compute_portfolio_metrics_from_curves(
    equity_curve: list,
    benchmark_curve: list,
    starting_capital: float,
) -> dict:
    """Compute portfolio-level Sharpe / drawdown / alpha / beta / IR / tracking
    error from the equity curve produced by Portfolio.mark_to_market.

    Returns a dict suitable for inclusion in backtest_report.html and the
    site_picks JSON. All percent values are in %, NOT decimal. NaN/inf-safe.
    """
    out: dict = {
        "starting_capital":             round(float(starting_capital), 2),
        "n_equity_points":              len(equity_curve) if equity_curve else 0,
        "portfolio_total_return_pct":   0.0,
        "portfolio_sharpe":             None,
        "portfolio_max_drawdown_pct":   0.0,
        "benchmark_total_return_pct":   None,
        "alpha_annualized_pct":         None,
        "beta_to_benchmark":            None,
        "tracking_error_pct":           None,
        "information_ratio":            None,
        "note": "BUG-95: portfolio metrics from Portfolio.equity_curve",
    }
    if not equity_curve or len(equity_curve) < 2:
        return out

    port_rets = _daily_returns_from_curve(equity_curve)
    if port_rets.empty:
        return out

    # Total return: (final / starting) - 1
    final_equity = float(equity_curve[-1][1])
    if starting_capital > 0:
        total_ret = (final_equity / starting_capital - 1.0) * 100.0
        out["portfolio_total_return_pct"] = round(total_ret, 4)

    # Portfolio max drawdown (peak-to-trough on equity_curve)
    eq_values = pd.Series([float(p[1]) for p in equity_curve])
    peak = eq_values.cummax()
    dd_series = (eq_values - peak) / peak * 100.0
    out["portfolio_max_drawdown_pct"] = round(float(dd_series.min()), 4)

    # Annualized Sharpe (252 trading days; rf=0)
    if port_rets.std(ddof=1) > 0:
        sharpe = (port_rets.mean() / port_rets.std(ddof=1)) * (252 ** 0.5)
        if not (np.isnan(sharpe) or np.isinf(sharpe)):
            out["portfolio_sharpe"] = round(float(sharpe), 4)

    # Benchmark metrics
    if benchmark_curve and len(benchmark_curve) >= 2:
        bench_rets = _daily_returns_from_curve(benchmark_curve)
        if not bench_rets.empty:
            # Benchmark total return
            bench_first = float(benchmark_curve[0][1])
            bench_last = float(benchmark_curve[-1][1])
            if bench_first > 0:
                bench_total = (bench_last / bench_first - 1.0) * 100.0
                out["benchmark_total_return_pct"] = round(bench_total, 4)

            # Align port and bench daily returns on common dates
            aligned = pd.concat([port_rets, bench_rets], axis=1,
                                join="inner").dropna()
            aligned.columns = ["port", "bench"]
            if len(aligned) >= 2 and aligned["bench"].var(ddof=1) > 0:
                # Beta = cov(port, bench) / var(bench)
                beta = (aligned["port"].cov(aligned["bench"]) /
                        aligned["bench"].var(ddof=1))
                if not (np.isnan(beta) or np.isinf(beta)):
                    out["beta_to_benchmark"] = round(float(beta), 4)

                # Alpha (annualized): port_ann - beta * bench_ann
                port_ann = aligned["port"].mean() * 252
                bench_ann = aligned["bench"].mean() * 252
                if out["beta_to_benchmark"] is not None:
                    alpha = (port_ann - beta * bench_ann) * 100.0
                    if not (np.isnan(alpha) or np.isinf(alpha)):
                        out["alpha_annualized_pct"] = round(float(alpha), 4)

                # Tracking error (annualized std of return diff, %)
                excess = aligned["port"] - aligned["bench"]
                te = excess.std(ddof=1) * (252 ** 0.5) * 100.0
                if not (np.isnan(te) or np.isinf(te)):
                    out["tracking_error_pct"] = round(float(te), 4)

                # Information ratio (excess return / tracking error)
                excess_ann = excess.mean() * 252 * 100.0
                if te > 0 and not (np.isnan(excess_ann) or np.isinf(excess_ann)):
                    ir = excess_ann / te
                    out["information_ratio"] = round(float(ir), 4)

    return out
