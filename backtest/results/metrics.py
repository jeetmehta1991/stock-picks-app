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
    # Batch 197 (Phase 1A-beta batch_2 crash fix 2026-05-17): the deflated
    # Sharpe formula uses (1 - (kurt/4) * sharpe^2)**0.5 whose radicand can be
    # NEGATIVE when (excess_kurt/4) * sharpe^2 > 1.0 (high excess kurtosis +
    # nontrivial Sharpe), producing a complex number that crashes round().
    # The pre-batch denominator_sq guard does NOT cover this -- denominator_sq
    # uses + skew * sharpe terms whereas the deflated formula uses
    # - excess_kurt term, so the radicands are orthogonal. Both branches
    # (scipy + scipy-less) now guard the deflated radicand independently.
    deflated_radicand = 1.0 - (excess_kurt / 4.0) * sharpe**2
    try:
        from scipy.stats import norm
        denominator_sq = 1.0 - skew * sharpe + (excess_kurt / 4.0) * sharpe**2
        if denominator_sq <= 0:
            return {"psr": None, "deflated_sharpe": None, "note": "denominator_invalid"}
        denom = (denominator_sq / (n_trades - 1)) ** 0.5
        z = sharpe / denom if denom > 0 else 0
        psr = float(norm.cdf(z))
        if deflated_radicand <= 0:
            deflated = None
        else:
            deflated = sharpe * deflated_radicand ** 0.5
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
        if deflated_radicand <= 0:
            deflated = None
        else:
            deflated = sharpe * deflated_radicand ** 0.5
            if np.isnan(deflated) or np.isinf(deflated):
                deflated = None
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


CANONICAL_BREAKDOWN_VARIABLES = (
    "regime", "sector", "market_cap_band", "vol_band", "momentum_band",
    "liquidity_band", "confidence_tier", "category", "direction",
    "exit_method", "tier", "smart_money_score_band", "macro_score_band",
    "sentiment_band", "earnings_window", "gap_band", "weekday",
)


def compute_per_bucket_metrics(df_trades, breakdown_var: str) -> dict:
    """DEC-100 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 56 2026-05-11
    (owner-approved Path C 5-DEC bundle). 17+ categorical breakdown
    variables per Pass 52 turn 119 spec; the breakdown list is the
    canonical input dimension set for DEC-422 cube aggregation.

    For a given breakdown_var (must be a column in df_trades), groups
    trades and returns dict {bucket_value: stats_dict}. stats_dict has
    n / win_rate / avg_pnl_pct / total_roi_pct / profit_factor.

    Returns empty dict on empty df, unknown column, or breakdown_var
    not in CANONICAL_BREAKDOWN_VARIABLES (defensive against typos).
    """
    import pandas as pd
    if df_trades is None or len(df_trades) == 0:
        return {}
    if breakdown_var not in CANONICAL_BREAKDOWN_VARIABLES:
        return {}
    if breakdown_var not in df_trades.columns:
        return {}
    out = {}
    for bucket, g in df_trades.groupby(breakdown_var):
        n = len(g)
        if n == 0:
            continue
        wins = g[g["win"] == True] if "win" in g.columns else g[g["pnl_pct"] > 0]
        win_rate = len(wins) / n
        avg_pnl = float(g["pnl_pct"].mean())
        total_roi = float(g["pnl_pct"].sum())
        pf = _profit_factor(g["pnl_pct"])
        out[str(bucket)] = {
            "n":              n,
            "win_rate":       round(win_rate, 4),
            "avg_pnl_pct":    round(avg_pnl, 4),
            "total_roi_pct":  round(total_roi, 4),
            "profit_factor":  round(pf, 4) if pf != float("inf") else None,
        }
    return out


def evaluates_pass(value: float, threshold: float, kind: str = "pass_ge") -> bool:
    """DEC-284 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 56 2026-05-11
    (owner-approved Path C 5-DEC bundle). Canonical pass/fail comparison
    operator per Pass 52 turn 56 spec: STRICT-LESS-THAN for fail
    thresholds, STRICT-GREATER-THAN-OR-EQUAL for pass thresholds.
    Equality goes pass-side.

    Examples:
      Sharpe >= 0.5 -> evaluates_pass(value, 0.5, 'pass_ge')
      Sharpe < 0.5  -> evaluates_pass(value, 0.5, 'fail_lt')  # invert if used as fail
      trades >= 300 -> evaluates_pass(value, 300, 'pass_ge')

    Inputs:
      value: observed value
      threshold: the threshold
      kind: 'pass_ge' (default, returns value >= threshold)
            or 'pass_le' for max-bound criteria (e.g., max_drawdown <= 20)

    Returns bool. None inputs evaluate False (fail-closed).
    """
    if value is None or threshold is None:
        return False
    if kind == "pass_ge":
        return float(value) >= float(threshold)
    if kind == "pass_le":
        return float(value) <= float(threshold)
    return False


def compute_per_regime_agent_verdict(
    df_rules_only,
    df_agent_overlay,
    regimes=("bull", "neutral", "bear", "crisis"),
    min_trades_per_regime: int = 30,
) -> dict:
    """DEC-209 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 56 2026-05-11
    (owner-approved Path C 5-DEC bundle). Per-regime agent A/B verdict:
    agents pass/fail SEPARATELY in each regime (Pass 45 spec).

    For each regime, compares win_rate (rules-only) vs win_rate
    (agent-overlay) on trades labeled with that regime. Verdict per
    regime:
      'AGENT_ADDS'    if agent_wr - rules_wr >= 0.03 (3pp lift)
      'AGENT_HURTS'   if rules_wr - agent_wr >= 0.03
      'NEUTRAL'       otherwise
      'INSUFFICIENT_DATA' if either subset has < min_trades_per_regime

    Returns dict {regime: {verdict, rules_wr, agent_wr, delta_pp,
    n_rules, n_agent}}.
    """
    import pandas as pd
    out = {}
    if (df_rules_only is None or df_agent_overlay is None
            or len(df_rules_only) == 0 or len(df_agent_overlay) == 0):
        return {r: {"verdict": "INSUFFICIENT_DATA"} for r in regimes}
    for r in regimes:
        rules_r = df_rules_only[df_rules_only.get("regime", pd.Series([], dtype=str)).str.contains(r, na=False)]
        agent_r = df_agent_overlay[df_agent_overlay.get("regime", pd.Series([], dtype=str)).str.contains(r, na=False)]
        n_rules = len(rules_r)
        n_agent = len(agent_r)
        if n_rules < min_trades_per_regime or n_agent < min_trades_per_regime:
            out[r] = {
                "verdict":  "INSUFFICIENT_DATA",
                "n_rules":  n_rules,
                "n_agent":  n_agent,
            }
            continue
        rules_wr = float(rules_r["win"].mean()) if "win" in rules_r.columns else None
        agent_wr = float(agent_r["win"].mean()) if "win" in agent_r.columns else None
        if rules_wr is None or agent_wr is None:
            out[r] = {"verdict": "INSUFFICIENT_DATA",
                      "n_rules": n_rules, "n_agent": n_agent}
            continue
        delta = agent_wr - rules_wr
        if delta >= 0.03:    verdict = "AGENT_ADDS"
        elif delta <= -0.03: verdict = "AGENT_HURTS"
        else:                verdict = "NEUTRAL"
        out[r] = {
            "verdict":   verdict,
            "rules_wr":  round(rules_wr, 4),
            "agent_wr":  round(agent_wr, 4),
            "delta_pp":  round(delta * 100, 2),
            "n_rules":   n_rules,
            "n_agent":   n_agent,
        }
    return out


class CacheStaleError(Exception):
    """DEC-260 raised when cache file's max(date) < requested as_of."""

    def __init__(self, ticker, cache_type, cached_end, requested_date):
        self.ticker = ticker
        self.cache_type = cache_type
        self.cached_end = cached_end
        self.requested_date = requested_date
        super().__init__(
            f"CacheStaleError: ticker={ticker} cache_type={cache_type} "
            f"cached_end={cached_end} requested_date={requested_date}"
        )


def assert_cache_fresh(
    ticker: str,
    cache_type: str,
    cached_end_date,
    requested_date,
) -> None:
    """DEC-260 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). Cache freshness
    assertion per Pass 52 spec: if requested_date > cached_end_date,
    raise CacheStaleError to force prefetch refresh.

    Inputs:
      ticker: ticker symbol
      cache_type: 'ohlcv' / 'earnings' / 'fundamentals' / etc
      cached_end_date: last date present in cache (date or pd.Timestamp)
      requested_date: target as_of date

    Raises CacheStaleError if requested > cached_end. No-op otherwise.
    Joint DEC-117 checksum + DEC-330 schema versioning.
    """
    if cached_end_date is None or requested_date is None:
        return  # caller-side fail-soft
    if requested_date > cached_end_date:
        raise CacheStaleError(ticker, cache_type, cached_end_date, requested_date)


def maybe_convert_short_to_long(
    open_short_position: dict,
    current_regime: str,
    prior_regime: str = None,
) -> dict:
    """DEC-338 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). Conversion logic
    short -> long when regime flips to bull per Pass 52 turn 50 owner
    sub-choice (A): actually OPEN new long position, not just close short.

    Inputs:
      open_short_position: dict with at least {ticker, shares, entry_price}
      current_regime: today's regime label
      prior_regime: yesterday's regime (None on first day)

    Returns dict with:
      action: 'no_conversion' / 'close_short_and_open_long'
      ticker, close_short_shares, open_long_shares, note
    """
    from backtest.config import (CONVERSION_SHORT_TO_LONG_ENABLED,
                                   CONVERSION_REGIME_GATE,
                                   CONVERSION_OPENS_NEW_LONG)
    if not CONVERSION_SHORT_TO_LONG_ENABLED:
        return {"action": "no_conversion", "note": "feature_disabled"}
    if not open_short_position or open_short_position.get("shares", 0) >= 0:
        return {"action": "no_conversion", "note": "not_a_short"}
    if current_regime != CONVERSION_REGIME_GATE:
        return {"action": "no_conversion", "note": "regime_not_bull"}
    # Only fire on FLIP (regime changed today to bull, was something else)
    if prior_regime is not None and prior_regime == CONVERSION_REGIME_GATE:
        return {"action": "no_conversion", "note": "not_flip_day"}
    abs_shares = abs(open_short_position.get("shares", 0))
    return {
        "action":              "close_short_and_open_long",
        "ticker":              open_short_position.get("ticker"),
        "close_short_shares":  abs_shares,
        "open_long_shares":    abs_shares if CONVERSION_OPENS_NEW_LONG else 0,
        "note":                "REGIME_FLIP_BULL_CONVERSION",
    }


def is_ticker_in_stopout_cooldown(
    ticker: str,
    trade_log_df,
    as_of,
    cooldown_days: int = None,
) -> dict:
    """DEC-018 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). Cooldown after
    stop-out per Pass 52 turn 115 spec (BUG-133): per-ticker 5 trading days
    post-stop prevents whipsaw re-entry.

    Inputs:
      ticker: ticker symbol
      trade_log_df: DataFrame with ticker, exit_date, exit_reason columns
      as_of: today's date
      cooldown_days: override default (TICKER_STOPOUT_COOLDOWN_DAYS=5)

    Returns dict with in_cooldown (bool), days_since_stop, last_stop_date,
    note. Joint DEC-135 per-ticker max-loss cap (Batch 55).
    """
    import pandas as pd
    from backtest.config import TICKER_STOPOUT_COOLDOWN_DAYS
    cd = cooldown_days if cooldown_days is not None else TICKER_STOPOUT_COOLDOWN_DAYS
    if trade_log_df is None or len(trade_log_df) == 0:
        return {"in_cooldown": False, "days_since_stop": None,
                "last_stop_date": None, "note": "no_trade_log"}
    required = {"ticker", "exit_date", "exit_reason"}
    if not required.issubset(set(trade_log_df.columns)):
        return {"in_cooldown": False, "days_since_stop": None,
                "last_stop_date": None, "note": "missing_cols"}
    rows = trade_log_df[
        (trade_log_df["ticker"] == ticker)
        & (trade_log_df["exit_reason"].astype(str).str.lower().str.contains("stop"))
    ]
    if rows.empty:
        return {"in_cooldown": False, "days_since_stop": None,
                "last_stop_date": None, "note": "no_stop_history"}
    last_exit = pd.to_datetime(rows["exit_date"]).max()
    as_of_ts = pd.to_datetime(as_of)
    days = (as_of_ts - last_exit).days
    return {
        "in_cooldown":      bool(days < cd),
        "days_since_stop":  int(days),
        "last_stop_date":   str(last_exit.date()),
        "note":             "STOPOUT_COOLDOWN" if days < cd else "ok",
    }


def regime_probability_phase_a(regime_score) -> dict:
    """DEC-107 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). Phase A regime
    probability emission per Pass 52 turn 61 phased-rollout spec.

    Inputs:
      regime_score: 0-100 score from multi_input_regime_score / multi_asset_regime_score

    Returns dict with regime_label (existing 4-class) AND regime_probabilities
    (vector over bull/neutral/bear/crisis using soft-bin assignment). Backwards
    compatible: callers can ignore probabilities and use only the label.
    Phase B (strategies migrate to probability gating) deferred per spec.
    """
    if regime_score is None:
        return {"regime_label": "unknown",
                "regime_probabilities": {"bull": 0.0, "neutral": 0.0,
                                          "bear": 0.0, "crisis": 0.0}}
    s = float(regime_score)
    # Soft-bin assignment based on score distance from band centers
    centers = {"bull": 80, "neutral": 50, "bear": 30, "crisis": 10}
    sigma = 15.0  # bandwidth
    import math
    weights = {k: math.exp(-((s - c) ** 2) / (2 * sigma * sigma))
               for k, c in centers.items()}
    total = sum(weights.values())
    probs = {k: round(v / total, 4) for k, v in weights.items()}
    label = max(probs.items(), key=lambda kv: kv[1])[0]
    return {"regime_label": label, "regime_probabilities": probs}


def compute_cache_checksum(file_path) -> dict:
    """DEC-117 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). File-level checksum
    + last_validated timestamp per Pass 52 turn 119 spec.

    Returns dict per CACHE_METADATA_SCHEMA: file_path / sha256 / last_validated_iso /
    row_count (None for non-parquet) / size_bytes. Joint DEC-260 cache freshness +
    DEC-330 schema versioning.
    """
    import hashlib
    from pathlib import Path
    from datetime import datetime
    p = Path(file_path) if file_path else None
    if p is None or not p.exists():
        return {"file_path": str(file_path), "sha256": None,
                "last_validated_iso": None, "row_count": None,
                "size_bytes": None, "note": "missing_file"}
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return {
        "file_path":           str(p),
        "sha256":              h.hexdigest(),
        "last_validated_iso":  datetime.utcnow().isoformat(),
        "row_count":           None,
        "size_bytes":          p.stat().st_size,
        "note":                "ok",
    }


def should_rebalance_portfolio(
    position_weights: dict,
    target_weights: dict,
    cash_pct: float = 0.0,
    deployable_signals_available: bool = False,
    drift_x_target: float = None,
    cash_threshold: float = None,
) -> dict:
    """DEC-136 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). Portfolio rebalancing
    trigger per Pass 52 turn 115 spec: any position > 2x target weight
    (drift) OR cash > 10% AND deployable signals.

    Returns dict with should_rebalance (bool), reason (str), worst_drift_ticker.
    """
    from backtest.config import (PORTFOLIO_REBALANCE_DRIFT_X_TARGET,
                                   PORTFOLIO_REBALANCE_CASH_PCT_THRESHOLD)
    drift = drift_x_target if drift_x_target is not None else PORTFOLIO_REBALANCE_DRIFT_X_TARGET
    cash_th = cash_threshold if cash_threshold is not None else PORTFOLIO_REBALANCE_CASH_PCT_THRESHOLD
    worst_ticker = None
    worst_ratio = 0.0
    for ticker, cur_weight in (position_weights or {}).items():
        target = (target_weights or {}).get(ticker, 0.0)
        if target <= 0:
            continue
        ratio = cur_weight / target
        if ratio > worst_ratio:
            worst_ratio = ratio
            worst_ticker = ticker
    drift_breach = worst_ratio > drift
    cash_breach = (cash_pct > cash_th) and deployable_signals_available
    if drift_breach:
        reason = f"DRIFT_BREACH_{worst_ticker}_{round(worst_ratio,2)}x"
    elif cash_breach:
        reason = f"CASH_DEPLOYABLE_{round(cash_pct,4)}"
    else:
        reason = "ok"
    return {
        "should_rebalance":     bool(drift_breach or cash_breach),
        "reason":               reason,
        "worst_drift_ticker":   worst_ticker,
        "worst_drift_ratio":    round(worst_ratio, 4),
    }


def momentum_delta_band(stock_20d_return: float, sector_20d_return: float) -> dict:
    """DEC-144 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). Stock-vs-sector
    momentum delta breakdown variable per Pass 52 turn 85 spec.

    momentum_delta = stock_20d_return - sector_20d_return.

    Bands:
      high_outperform: delta >= +0.10
      outperform:      0.05 <= delta < 0.10
      neutral:         -0.05 < delta < 0.05
      underperform:    -0.10 < delta <= -0.05
      high_underperform: delta <= -0.10

    Returns dict with delta, band, note.
    """
    if stock_20d_return is None or sector_20d_return is None:
        return {"delta": None, "band": "unknown", "note": "missing_input"}
    delta = stock_20d_return - sector_20d_return
    if delta >= 0.10:      band = "high_outperform"
    elif delta >= 0.05:    band = "outperform"
    elif delta > -0.05:    band = "neutral"
    elif delta > -0.10:    band = "underperform"
    else:                  band = "high_underperform"
    return {"delta": round(delta, 4), "band": band, "note": "ok"}


def signal_persistence_weight(
    consecutive_days: int,
    base_weight: float = 1.0,
    growth_per_day: float = 0.25,
    max_weight: float = 2.5,
) -> float:
    """DEC-175 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11
    (owner-approved Path C PARTIAL-SPEC-ONLY closure). Signal persistence
    weighting per Pass 52 turn 119 spec: consecutive-day signals weighted
    higher (3-day breakout > 1-day breakout). Joint DEC-148 + DEC-108.

    Inputs:
      consecutive_days: number of consecutive days the signal has fired
      base_weight: weight at 1 day (default 1.0)
      growth_per_day: linear weight increment per additional day (default 0.25)
      max_weight: cap (default 2.5)

    Returns float weight. 1-day -> 1.0, 3-day -> 1.5, 7+ day -> capped at 2.5.
    """
    if consecutive_days is None or consecutive_days <= 0:
        return 0.0
    n = max(1, int(consecutive_days))
    raw = base_weight + (n - 1) * growth_per_day
    return min(float(max_weight), raw)


def detect_chart_pattern_skeleton(
    pattern_name: str,
    ohlcv_df=None,
) -> dict:
    """DEC-354/355/358/359/360/361/362 RESOLVED-IMPLEMENTED Pass 53 v8h+1
    Phase 3 Batch 62 2026-05-11 (owner-approved Path C 20-DEC bundle).

    Chart-pattern detection SKELETON. Returns the strategy spec from
    CHART_PATTERN_STRATEGIES + a `detected` boolean. Full pattern-
    recognition implementations (trendline-fit, peak/trough detection,
    measured-move target arithmetic) deferred to Sprint 7+ strategy
    class build-out. This helper provides the parent-spec lookup so
    downstream consumers can iterate the roster.

    Inputs:
      pattern_name: key from CHART_PATTERN_STRATEGIES
      ohlcv_df: optional OHLCV DataFrame (placeholder; not used by skeleton)

    Returns dict with pattern_name, spec (full sub-dict), detected (False
    in skeleton), note='SKELETON_PENDING_FULL_IMPL'.
    """
    from backtest.config import CHART_PATTERN_STRATEGIES
    spec = CHART_PATTERN_STRATEGIES.get(pattern_name)
    if spec is None:
        return {"pattern_name": pattern_name, "spec": None, "detected": False,
                "note": "unknown_pattern"}
    return {
        "pattern_name": pattern_name,
        "spec":         spec,
        "detected":     False,
        "note":         "SKELETON_PENDING_FULL_IMPL",
    }


def institutional_price_level_mapping(
    quarterly_avg_cost_basis: float,
    current_price: float,
    underwater_threshold: float = None,
) -> dict:
    """DEC-352 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
    (owner-approved Path C 20-DEC bundle). 13F price-level mapping per
    Pass 52 spec: compare current price to institutional average cost
    basis (derived from quarterly 13F filings); flag tickers where
    institutions sit underwater (potential supply overhang / selling
    pressure).

    Inputs:
      quarterly_avg_cost_basis: VWAP or simple average of last-4-quarter
        institutional accumulation prices
      current_price: today's close
      underwater_threshold: fractional drop to flag (default
        INSTITUTIONAL_PRICE_LEVEL_UNDERWATER_THRESHOLD = -0.10 i.e. -10%)

    Returns dict with cost_basis_delta_pct, position ('above'/'at'/'below'),
    underwater (bool when delta below threshold), note.
    """
    from backtest.config import INSTITUTIONAL_PRICE_LEVEL_UNDERWATER_THRESHOLD
    if (quarterly_avg_cost_basis is None or quarterly_avg_cost_basis <= 0
            or current_price is None or current_price <= 0):
        return {"cost_basis_delta_pct": None, "position": None,
                "underwater": False, "note": "invalid_input"}
    threshold = (underwater_threshold
                 if underwater_threshold is not None
                 else INSTITUTIONAL_PRICE_LEVEL_UNDERWATER_THRESHOLD)
    delta = (current_price - quarterly_avg_cost_basis) / quarterly_avg_cost_basis
    if delta > 0.02:        position = "above"
    elif delta < -0.02:     position = "below"
    else:                   position = "at"
    underwater = delta <= threshold
    return {
        "cost_basis_delta_pct": round(float(delta), 4),
        "position":             position,
        "underwater":           bool(underwater),
        "note":                 "INSTITUTIONS_UNDERWATER" if underwater else "ok",
    }


def event_calendar_suppression_check(
    as_of_date,
    ticker_earnings_date=None,
    fomc_dates=None,
    cpi_release_dates=None,
    nfp_release_dates=None,
    pre_days: int = None,
    post_days: int = None,
) -> dict:
    """DEC-348 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
    (owner-approved Path C 20-DEC bundle). Event-calendar suppression per
    Pass 52 turn 89 spec: suppress strategy entries on date of FOMC /
    earnings / CPI within DEC-349 asymmetric window (pre=1, post=3).

    Joint DEC-256 (earnings calendar) + DEC-407/448 (FRED FOMC/CPI dates)
    + DEC-349 (asymmetric window).

    Inputs:
      as_of_date: entry candidate date
      ticker_earnings_date: optional earnings date for the ticker
      fomc_dates / cpi_release_dates / nfp_release_dates: lists of events
      pre_days / post_days: override DEC-349 defaults

    Returns dict with suppressed (bool), reasons (list of event-type tags),
    note.
    """
    from datetime import datetime, date
    from backtest.config import EVENT_WINDOW_PRE_DAYS, EVENT_WINDOW_POST_DAYS
    if as_of_date is None:
        return {"suppressed": False, "reasons": [], "note": "no_as_of"}
    if isinstance(as_of_date, str):
        as_of_date = datetime.fromisoformat(as_of_date).date()
    pre = pre_days if pre_days is not None else EVENT_WINDOW_PRE_DAYS
    post = post_days if post_days is not None else EVENT_WINDOW_POST_DAYS

    def _within_window(event_d):
        if event_d is None:
            return False
        if isinstance(event_d, str):
            try:
                event_d = datetime.fromisoformat(event_d).date()
            except ValueError:
                return False
        days_to_event = (event_d - as_of_date).days
        return -post <= days_to_event <= pre

    reasons = []
    if ticker_earnings_date is not None and _within_window(ticker_earnings_date):
        reasons.append("EVENT_SUPPRESSION_EARNINGS")
    for fomc_d in (fomc_dates or []):
        if _within_window(fomc_d):
            reasons.append("EVENT_SUPPRESSION_FOMC")
            break
    for cpi_d in (cpi_release_dates or []):
        if _within_window(cpi_d):
            reasons.append("EVENT_SUPPRESSION_CPI")
            break
    for nfp_d in (nfp_release_dates or []):
        if _within_window(nfp_d):
            reasons.append("EVENT_SUPPRESSION_NFP")
            break
    return {
        "suppressed": len(reasons) > 0,
        "reasons":    reasons,
        "note":       "REJECT_REASON_EVENT_SUPPRESSION" if reasons else "ok",
    }


def bonferroni_dynamic_n(
    p_values,
    n_strategies_tested=None,
) -> dict:
    """DEC-400 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
    (owner-approved Path C 20-DEC bundle). DEC-080 Phase A: replace
    hardcoded Bonferroni N=60 with dynamic `len(STRATEGIES_TESTED)` count.

    Inputs:
      p_values: list of raw p-values (one per strategy)
      n_strategies_tested: override count (default: len(p_values))

    Returns dict with adjusted_p_values (list), n_tested, alpha_bonferroni
    at conventional 0.05 (= 0.05 / n_tested), per_strategy_pass (bool list
    where adjusted_p < 0.05).

    REVISIT_AFTER_BACKTEST tag per Pass 52 turn 37; tune post-Phase-1B-alpha.
    """
    if not p_values:
        return {"adjusted_p_values": [], "n_tested": 0,
                "alpha_bonferroni": None, "per_strategy_pass": [],
                "note": "no_p_values"}
    n = n_strategies_tested if n_strategies_tested is not None else len(p_values)
    if n <= 0:
        return {"adjusted_p_values": [], "n_tested": 0,
                "alpha_bonferroni": None, "per_strategy_pass": [],
                "note": "invalid_n"}
    adjusted = [min(float(p) * n, 1.0) for p in p_values]
    alpha = 0.05 / n
    passes = [float(p) < alpha for p in p_values]
    return {
        "adjusted_p_values": [round(a, 6) for a in adjusted],
        "n_tested":          n,
        "alpha_bonferroni":  round(float(alpha), 8),
        "per_strategy_pass": passes,
        "note":              "ok",
    }


def is_earnings_tolerant_strategy(strategy_attributes: dict) -> bool:
    """DEC-013 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
    (owner-approved Path C 20-DEC bundle). Helper that resolves a strategy's
    `earnings_tolerant` flag from its attribute dict. REVISED Pass 24
    semantics: True means the strategy can hold through earnings; False
    means strategy must close before earnings within DEC-348 window.

    Default: False (conservative; close before earnings unless explicitly
    flagged tolerant).

    Inputs: dict of strategy attributes (from STRATEGY_REGISTER or class
    attribute).
    Returns bool.
    """
    if not strategy_attributes:
        return False
    return bool(strategy_attributes.get("earnings_tolerant", False))


def liquidity_drop_warning(
    entry_adv_shares: float,
    current_adv_shares: float,
    drop_threshold_pct: float = 50.0,
) -> dict:
    """DEC-019 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
    (owner-approved Path C 20-DEC bundle). Liquidity-drop re-validation per
    Pass 52 turn 115 spec (BUG-135 closure): liquidity applied at entry;
    re-validate at exit only if ADV drops > 50% from entry-day ADV. Joint
    DEC-321 fail-closed + DEC-366 tier-specific floors.

    Returns dict with warning (bool), drop_pct, note.
    """
    if entry_adv_shares is None or entry_adv_shares <= 0:
        return {"warning": False, "drop_pct": None, "note": "no_entry_adv"}
    if current_adv_shares is None:
        return {"warning": False, "drop_pct": None, "note": "no_current_adv"}
    drop_pct = (entry_adv_shares - current_adv_shares) / entry_adv_shares * 100.0
    warning = bool(drop_pct > drop_threshold_pct)
    return {
        "warning":  warning,
        "drop_pct": round(float(drop_pct), 2),
        "note":     "LIQUIDITY_DROP_WARNING" if warning else "ok",
    }


def detect_stop_cluster_pattern(
    stop_dates,
    window_days: int = 10,
    threshold: int = 5,
) -> dict:
    """DEC-078A RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
    (owner-approved Path C 20-DEC bundle). Stop-out cluster diagnostic per
    Pass 52 spec: rolling-window stop density. If >= threshold stop_loss
    exit_reasons within window_days, flag STOP_CLUSTER_PATTERN
    (informational only; no action taken).

    Inputs:
      stop_dates: iterable of stop-out exit dates (date or pd.Timestamp)
      window_days: rolling window (default 10 trading days)
      threshold: minimum stops within window to fire (default 5)

    Returns dict with cluster_detected (bool), max_density, note.
    """
    import pandas as pd
    if not stop_dates or len(stop_dates) < threshold:
        return {"cluster_detected": False, "max_density": 0,
                "note": "insufficient_stops"}
    dates = sorted(pd.to_datetime(list(stop_dates)).tolist())
    max_density = 0
    for i in range(len(dates)):
        window_end = dates[i] + pd.Timedelta(days=window_days)
        density = sum(1 for d in dates[i:] if d <= window_end)
        if density > max_density:
            max_density = density
    return {
        "cluster_detected": max_density >= threshold,
        "max_density":      int(max_density),
        "note":             "STOP_CLUSTER_PATTERN" if max_density >= threshold else "ok",
    }


def route_interlisted_trade(
    ticker: str,
    trade_size_usd: float,
    tsx_adv_shares: float,
    is_interlisted: bool,
) -> dict:
    """DEC-253 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
    (owner-approved Path C 20-DEC bundle). Interlisted security routing per
    Pass 52 turn 91 spec: TSX-CAD if interlisted AND trade_size <= $50K AND
    TSX ADV >= 100K; otherwise US-NYSE.

    Returns dict with venue ('TSX' / 'US-NYSE'), routed_ticker, reason.
    """
    from backtest.config import (INTERLISTED_ROUTING_TRADE_SIZE_THRESHOLD_USD,
                                  INTERLISTED_ROUTING_TSX_MIN_ADV_SHARES)
    if not is_interlisted:
        return {"venue": "US-NYSE", "routed_ticker": ticker,
                "reason": "not_interlisted"}
    if trade_size_usd > INTERLISTED_ROUTING_TRADE_SIZE_THRESHOLD_USD:
        return {"venue": "US-NYSE", "routed_ticker": ticker,
                "reason": "trade_size_above_threshold"}
    if tsx_adv_shares < INTERLISTED_ROUTING_TSX_MIN_ADV_SHARES:
        return {"venue": "US-NYSE", "routed_ticker": ticker,
                "reason": "tsx_liquidity_below_floor"}
    return {
        "venue":          "TSX",
        "routed_ticker":  f"{ticker}.TO",
        "reason":         "interlisted_size_and_liquidity_ok",
    }


def composite_score(
    win_rate: float,
    profit_factor: float,
    smart_money_score: float,
    weights: dict = None,
    use_roi_proxy: bool = False,
    total_roi_pct: float = None,
) -> float:
    """DEC-334 + DEC-335 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60
    2026-05-11 (owner-approved Path C 20-DEC bundle). Configurable composite
    score replacing prior hardcoded 40/30/30 weighting (DEC-335) and adding
    optional ROI substitution for win_rate proxy (DEC-334).

    Inputs:
      win_rate: 0-1
      profit_factor: typically 0.5-3.0
      smart_money_score: configurable scale (e.g. -5..+6)
      weights: dict overriding COMPOSITE_SCORE_WEIGHTS defaults
      use_roi_proxy: when True, substitute total_roi_pct (normalized) for
        win_rate per DEC-334 spec (replace win_rate as ROI proxy with actual ROI)
      total_roi_pct: required when use_roi_proxy=True
    """
    from backtest.config import COMPOSITE_SCORE_WEIGHTS
    w = weights if weights is not None else COMPOSITE_SCORE_WEIGHTS
    if use_roi_proxy:
        if total_roi_pct is None:
            roi_component = 0.0
        else:
            roi_component = float(total_roi_pct) / 100.0  # normalize to 0-1 scale
        return (w.get("win_rate", 0.40) * roi_component
                + w.get("profit_factor", 0.30) * float(profit_factor)
                + w.get("smart_money", 0.30) * float(smart_money_score))
    return (w.get("win_rate", 0.40) * float(win_rate)
            + w.get("profit_factor", 0.30) * float(profit_factor)
            + w.get("smart_money", 0.30) * float(smart_money_score))


def smart_money_composite_score(
    congressional_signal: str = None,
    insider_signal: str = None,
    institutional_signal: str = None,
    weights: dict = None,
) -> dict:
    """DEC-332 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
    (owner-approved Path C 20-DEC bundle). Smart money composite scoring
    using canonical Pass 53 B1 weights from config (moved from hardcoded
    magic in `backtest/data/smart_money.py:470-529`).

    Veto case: cong=sell AND insider=cluster_sell -> score = -5 override.
    Score labels by threshold (>=6/>=4/>=2/>=1/0/<0/<=-4).
    """
    from backtest.config import (SMART_MONEY_CONGRESSIONAL_WEIGHTS,
                                  SMART_MONEY_INSIDER_WEIGHTS,
                                  SMART_MONEY_INSTITUTIONAL_WEIGHTS,
                                  SMART_MONEY_VETO_SCORE)
    if (congressional_signal == "sell"
            and insider_signal == "cluster_sell"):
        return {"score": SMART_MONEY_VETO_SCORE,
                "label": "congressional_sell+insider_cluster_sell"}
    score = 0
    score += SMART_MONEY_CONGRESSIONAL_WEIGHTS.get(congressional_signal, 0)
    score += SMART_MONEY_INSIDER_WEIGHTS.get(insider_signal, 0)
    score += SMART_MONEY_INSTITUTIONAL_WEIGHTS.get(institutional_signal, 0)
    if score >= 6:    label = "congressional+insider_cluster"
    elif score >= 4:  label = "congressional_or_insider"
    elif score >= 2:  label = "any_buy"
    elif score >= 1:  label = "weak_buy"
    elif score == 0:  label = "none"
    elif score >= -3: label = "negative"
    else:             label = "congressional_sell+insider_cluster_sell"
    return {"score": int(score), "label": label}


def compute_strategy_correlation_matrix(
    daily_returns_by_strategy,
    window: int = 90,
):
    """DEC-015 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). 90-day rolling Pearson correlation
    matrix per Pass 52 turn 67 spec. Consumed by DEC-089 (max correlation
    cap 0.7 between simultaneous holdings) for portfolio diversification.

    Inputs:
      daily_returns_by_strategy: DataFrame indexed by date, columns = strategies
      window: rolling window days (default 90)

    Returns DataFrame correlation matrix using the last `window` rows. Returns
    empty DataFrame on insufficient data.
    """
    import pandas as pd
    if daily_returns_by_strategy is None or len(daily_returns_by_strategy) < window:
        return pd.DataFrame()
    recent = daily_returns_by_strategy.iloc[-window:]
    return recent.corr(method="pearson")


def top_n_losing_trades_per_strategy(
    df_trades, n: int = 10,
):
    """DEC-120 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Top-N losing trades per strategy
    for loss attribution report per Pass 52 turn 119 spec. Joint DEC-119
    explainability + DEC-201 Dashboard 3.

    Returns dict {strategy_name: list of dicts with ticker, pnl_pct,
    entry_date, exit_date, regime}.
    """
    import pandas as pd
    if df_trades is None or len(df_trades) == 0 or "strategy" not in df_trades.columns:
        return {}
    out = {}
    for strat, g in df_trades.groupby("strategy"):
        losers = g[g["pnl_pct"] < 0].sort_values("pnl_pct").head(n)
        out[str(strat)] = losers[
            [c for c in ("ticker", "pnl_pct", "entry_date", "exit_date", "regime")
             if c in losers.columns]
        ].to_dict(orient="records")
    return out


def exponential_decay_weights(
    days_ago_list, half_life_days: int = 90,
) -> list:
    """DEC-123 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Exponential decay smart-money
    signal weights per Pass 52 turn 119 spec: half-life 90 days default
    REVISIT_AFTER_BACKTEST.

    weight = 0.5 ** (days_ago / half_life)

    Inputs: list of days-ago integers (e.g. [0, 30, 90, 180]).
    Returns list of weights normalized to sum=1.0 (so weight 0.0 on all
    means returned as zeros, not NaN).
    """
    if not days_ago_list:
        return []
    raw = [0.5 ** (d / half_life_days) for d in days_ago_list]
    total = sum(raw)
    if total <= 0:
        return [0.0] * len(raw)
    return [w / total for w in raw]


def cross_source_smart_money_cluster(
    insider_signal: str = None,
    congressional_signal: str = None,
    institutional_signal: str = None,
) -> dict:
    """DEC-124 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Cross-source confluence per
    Pass 52 turn 119 spec: 3+ sources align same direction = high-confidence.

    Inputs: 3 signal strings ('buy' / 'strong_buy' / 'sell' / 'none' / etc).
    Returns dict with sources_aligned (count), direction, confluence_score
    (0/1/2/3), cluster_label.
    """
    bull_sources = sum(1 for s in (insider_signal, congressional_signal,
                                   institutional_signal)
                       if s in ("buy", "strong_buy"))
    bear_sources = sum(1 for s in (insider_signal, congressional_signal,
                                   institutional_signal)
                       if s in ("sell", "strong_sell"))
    if bull_sources >= bear_sources:
        direction = "bull"
        n_aligned = bull_sources
    else:
        direction = "bear"
        n_aligned = bear_sources
    if n_aligned >= 3:    label = "HIGH_CONFLUENCE"
    elif n_aligned == 2:  label = "PARTIAL_CONFLUENCE"
    elif n_aligned == 1:  label = "ISOLATED_SIGNAL"
    else:                 label = "NO_SIGNAL"
    return {
        "sources_aligned":  n_aligned,
        "direction":        direction if n_aligned > 0 else "none",
        "confluence_score": n_aligned,
        "cluster_label":    label,
    }


def agent_value_add_two_gate_check(
    agent_sharpe: float,
    rules_sharpe: float,
    absolute_threshold: float = 0.2,
    relative_threshold: float = 0.15,
) -> dict:
    """DEC-131 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Two-gate logic per Pass 52 turn 13
    refinement: primary `agent - rules >= 0.2`; secondary
    `(agent - rules) / max(rules, 0.1) >= 0.15`; PASS if EITHER clears.
    Catches both low-baseline trap and high-baseline trap per CAV-060.

    Returns dict with passes (bool), absolute_diff, relative_diff,
    gate_reason ('absolute' / 'relative' / 'none').
    """
    if agent_sharpe is None or rules_sharpe is None:
        return {"passes": False, "absolute_diff": None, "relative_diff": None,
                "gate_reason": "missing_input"}
    abs_diff = agent_sharpe - rules_sharpe
    rel_diff = abs_diff / max(rules_sharpe, 0.1)
    abs_pass = abs_diff >= absolute_threshold - 1e-9
    rel_pass = rel_diff >= relative_threshold - 1e-9
    if abs_pass and rel_pass:    reason = "both"
    elif abs_pass:               reason = "absolute"
    elif rel_pass:               reason = "relative"
    else:                        reason = "none"
    return {
        "passes":        bool(abs_pass or rel_pass),
        "absolute_diff": round(abs_diff, 4),
        "relative_diff": round(rel_diff, 4),
        "gate_reason":   reason,
    }


def compute_fx_exposure_pct(
    usd_portfolio_value_cad: float,
    total_portfolio_value_cad: float,
) -> dict:
    """DEC-134 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). USD/CAD exposure tracking per
    Pass 52 turn 115 spec (FX hedge impl deferred to Stage 4).

    Returns dict with fx_exposure_pct, total_cad, usd_in_cad, note.
    Tracking only; hedge construction deferred to DEC-255 Norbert Gambit.
    """
    if total_portfolio_value_cad is None or total_portfolio_value_cad <= 0:
        return {"fx_exposure_pct": None, "total_cad": None, "usd_in_cad": None,
                "note": "invalid_portfolio_total"}
    pct = (usd_portfolio_value_cad or 0.0) / total_portfolio_value_cad * 100.0
    return {
        "fx_exposure_pct": round(float(pct), 2),
        "total_cad":       round(float(total_portfolio_value_cad), 2),
        "usd_in_cad":      round(float(usd_portfolio_value_cad or 0.0), 2),
        "note":            "ok",
    }


def build_sector_neutral_hedge(
    long_ticker: str,
    long_dollar_value: float,
    long_sector_etf: str,
    hedge_ratio: float = 1.0,
) -> dict:
    """DEC-141 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Sector-neutral hedge plan: long
    position + short sector ETF per Pass 52 turn 85 spec (implementation-
    deferred; this helper provides plan-shape for downstream consumers).

    Returns dict with hedge_ticker, hedge_direction='short', hedge_dollar.
    Caller decides whether to execute. Owner risk philosophy notes
    sector-neutral is OPPOSITE direction from medium-high risk profile;
    use only when strategy explicitly opts in.
    """
    if long_dollar_value <= 0 or not long_sector_etf:
        return {"hedge_ticker": None, "hedge_direction": None,
                "hedge_dollar": 0.0, "note": "invalid_input"}
    return {
        "long_ticker":     long_ticker,
        "hedge_ticker":    long_sector_etf,
        "hedge_direction": "short",
        "hedge_dollar":    round(long_dollar_value * hedge_ratio, 2),
        "note":            "plan_only_execution_deferred",
    }


def build_market_neutral_hedge(
    long_ticker: str,
    long_dollar_value: float,
    beta: float,
    spy_ticker: str = "SPY",
) -> dict:
    """DEC-142 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Market-neutral construction:
    long stock + short SPY at beta-weight per Pass 52 turn 85 spec
    (implementation-deferred; this helper provides plan-shape).

    Returns dict with spy_short_dollar = long_dollar * beta.
    """
    if long_dollar_value <= 0 or beta is None:
        return {"hedge_ticker": None, "hedge_direction": None,
                "hedge_dollar": 0.0, "note": "invalid_input"}
    return {
        "long_ticker":     long_ticker,
        "hedge_ticker":    spy_ticker,
        "hedge_direction": "short",
        "hedge_dollar":    round(long_dollar_value * float(beta), 2),
        "beta_used":       round(float(beta), 4),
        "note":            "plan_only_execution_deferred",
    }


def iv_pre_earnings_anomaly(
    current_iv: float,
    historical_iv_pre_earnings,
    sigma_threshold: float = 2.0,
) -> dict:
    """DEC-145 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). IV delta vs historical pre-earnings
    pattern per Pass 52 turn 85 spec (depends on DEC-258 options chain cache;
    this helper accepts caller-supplied historical IV list).

    Inputs:
      current_iv: today's pre-earnings IV
      historical_iv_pre_earnings: list of past 8 (or N) pre-earnings IVs
      sigma_threshold: stdev multiplier to flag anomaly (default 2.0)

    Returns dict with z_score, anomaly (bool), direction.
    """
    import statistics
    if (current_iv is None or historical_iv_pre_earnings is None
            or len(historical_iv_pre_earnings) < 3):
        return {"z_score": None, "anomaly": False, "direction": None,
                "note": "insufficient_history"}
    mean = statistics.mean(historical_iv_pre_earnings)
    std = statistics.stdev(historical_iv_pre_earnings)
    if std <= 0:
        return {"z_score": 0.0, "anomaly": False, "direction": None,
                "note": "zero_std"}
    z = (current_iv - mean) / std
    direction = "elevated" if z > 0 else "depressed"
    return {
        "z_score":   round(float(z), 4),
        "anomaly":   bool(abs(z) >= sigma_threshold),
        "direction": direction,
        "note":      "ok",
    }


def evaluate_paired_ab_arms(trade_id, per_arm_outcomes: dict) -> dict:
    """DEC-206 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Paired A/B design per Pass 45
    spec: every trade evaluated by every arm in parallel (same data, same
    signal, different overlay).

    Inputs:
      trade_id: identifier for the trade
      per_arm_outcomes: dict {arm_name: pnl_pct}

    Returns dict with trade_id, n_arms, best_arm, worst_arm, spread.
    """
    if not per_arm_outcomes:
        return {"trade_id": trade_id, "n_arms": 0, "best_arm": None,
                "worst_arm": None, "spread": None}
    items = list(per_arm_outcomes.items())
    best = max(items, key=lambda kv: kv[1] if kv[1] is not None else float("-inf"))
    worst = min(items, key=lambda kv: kv[1] if kv[1] is not None else float("inf"))
    spread = (best[1] - worst[1]) if (best[1] is not None and worst[1] is not None) else None
    return {
        "trade_id":  trade_id,
        "n_arms":    len(per_arm_outcomes),
        "best_arm":  best[0],
        "worst_arm": worst[0],
        "spread":    round(float(spread), 4) if spread is not None else None,
    }


def tag_agent_disagreement(
    bull_signal: str = None,
    bear_signal: str = None,
    risk_signal: str = None,
) -> dict:
    """DEC-212 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Agent-disagreement decomposition
    per Pass 52 turn 72 spec. Tags trades where Bull vs Bear disagree, or
    Risk overrides consensus.

    Inputs: 3 signal strings ('BUY' / 'HOLD' / 'SELL' / 'APPROVE' / 'VETO').

    Returns dict with disagreement_type ('bull_bear_disagree' /
    'risk_override' / 'consensus' / 'partial'), tags (list).
    """
    tags = []
    bb_disagree = (bull_signal == "BUY" and bear_signal == "HOLD") or \
                  (bull_signal == "HOLD" and bear_signal == "BUY")
    risk_override = risk_signal in ("VETO", "OVERRIDE")
    if bb_disagree:
        tags.append("AGENT_DISAGREEMENT_BULL_BEAR")
    if risk_override:
        tags.append("AGENT_DISAGREEMENT_RISK_OVERRIDE")
    if bb_disagree and risk_override:
        d_type = "partial"
    elif bb_disagree:
        d_type = "bull_bear_disagree"
    elif risk_override:
        d_type = "risk_override"
    else:
        d_type = "consensus"
    return {
        "disagreement_type": d_type,
        "tags":              tags,
        "n_tags":            len(tags),
    }


def vol_adjusted_momentum_lookback(
    realized_vol_annualized: float,
    base_lookback: int = 21,
    low_vol_lookback: int = 60,
    high_vol_lookback: int = 10,
    low_vol_threshold: float = 0.15,
    high_vol_threshold: float = 0.40,
) -> int:
    """DEC-148 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Stock-specific adaptive
    momentum lookback per Pass 52 turn 119 spec: per-ticker lookback
    scales INVERSELY with realized vol (high-vol stocks shorter lookback
    ~10d; low-vol stocks longer ~60d).

    Inputs:
      realized_vol_annualized: per-ticker annualized vol (0.20 = 20%)
      base_lookback: midpoint (default 21 trading days)
      low_vol_lookback / high_vol_lookback: extremes
      low_vol_threshold / high_vol_threshold: vol boundaries

    Returns int days. Linear interpolation between thresholds.
    """
    if realized_vol_annualized is None:
        return base_lookback
    v = float(realized_vol_annualized)
    if v <= low_vol_threshold:
        return low_vol_lookback
    if v >= high_vol_threshold:
        return high_vol_lookback
    frac = (v - low_vol_threshold) / (high_vol_threshold - low_vol_threshold)
    days = low_vol_lookback - frac * (low_vol_lookback - high_vol_lookback)
    return int(round(days))


def compute_vs_spy_metrics(strategy_returns, spy_returns) -> dict:
    """DEC-155 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). vs-SPY benchmark comparison
    per Pass 52 turn 119 spec: alpha + beta + information_ratio +
    tracking_error.

    Inputs:
      strategy_returns: pd.Series of strategy daily returns (decimal)
      spy_returns: pd.Series of SPY daily returns (decimal), same index

    Returns dict with alpha_annualized, beta, information_ratio,
    tracking_error_annualized, n_obs, note. Alpha annualized via *252;
    tracking error via std(excess) * sqrt(252).
    """
    import pandas as pd
    import numpy as np
    if strategy_returns is None or spy_returns is None:
        return {"alpha_annualized": None, "beta": None,
                "information_ratio": None, "tracking_error_annualized": None,
                "n_obs": 0, "note": "missing_input"}
    s = pd.Series(strategy_returns).dropna()
    b = pd.Series(spy_returns).dropna()
    common = s.index.intersection(b.index) if hasattr(s, "index") else None
    if common is not None and len(common) > 0:
        s = s.loc[common]
        b = b.loc[common]
    n = min(len(s), len(b))
    if n < 30:
        return {"alpha_annualized": None, "beta": None,
                "information_ratio": None, "tracking_error_annualized": None,
                "n_obs": n, "note": "insufficient_obs"}
    excess = s.values - b.values
    var_b = float(np.var(b.values, ddof=1))
    if var_b <= 0:
        beta = 0.0
    else:
        cov = float(np.cov(s.values, b.values, ddof=1)[0, 1])
        beta = cov / var_b
    alpha_daily = float(s.mean()) - beta * float(b.mean())
    alpha_ann = alpha_daily * 252.0
    te_daily = float(np.std(excess, ddof=1))
    te_ann = te_daily * (252.0 ** 0.5)
    ir = (float(np.mean(excess)) / te_daily) * (252.0 ** 0.5) if te_daily > 0 else 0.0
    return {
        "alpha_annualized":          round(alpha_ann, 4),
        "beta":                      round(beta, 4),
        "information_ratio":         round(ir, 4),
        "tracking_error_annualized": round(te_ann, 4),
        "n_obs":                     n,
        "note":                      "ok",
    }


def compute_multi_metric_ab_comparison(
    df_arm_a, df_arm_b, label_a: str = "rules", label_b: str = "agent",
) -> dict:
    """DEC-208 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Multi-metric A/B comparison
    per Pass 45 spec: Sharpe + Sortino + DD + win_rate + PF + CVaR + cost.

    Inputs:
      df_arm_a, df_arm_b: trade-log DataFrames with pnl_pct + win + hold_days
      label_a, label_b: arm labels for output dict keys

    Returns dict with per-arm metrics + delta dict (b - a).
    """
    import pandas as pd
    def _arm_metrics(df):
        if df is None or len(df) == 0:
            return {"sharpe": None, "sortino": None, "max_dd": None,
                    "win_rate": None, "profit_factor": None, "cvar_5pct": None,
                    "n_trades": 0}
        # BUG-075 fix 2026-05-13: sort by exit_date so equity curve is chronological.
        if "exit_date" in df.columns:
            df = df.sort_values("exit_date")
        pnl = df["pnl_pct"] if "pnl_pct" in df.columns else pd.Series([])
        hold = df["hold_days"] if "hold_days" in df.columns else pd.Series([10] * len(df))
        wins = df[df["win"] == True] if "win" in df.columns else df[pnl > 0]
        n = len(df)
        sharpe = _sharpe(pnl, hold)
        sortino = _sortino_ratio(pnl, hold)
        mdd = _max_drawdown(pnl)
        wr = len(wins) / n if n > 0 else 0
        pf = _profit_factor(pnl)
        # CVaR at 5% (mean of worst 5% pnl)
        if n >= 20:
            cutoff = pnl.quantile(0.05)
            cvar = float(pnl[pnl <= cutoff].mean())
        else:
            cvar = None
        return {
            "sharpe":        sharpe,
            "sortino":       sortino,
            "max_dd":        mdd,
            "win_rate":      round(wr, 4),
            "profit_factor": round(pf, 4) if pf != float("inf") else None,
            "cvar_5pct":     round(cvar, 4) if cvar is not None else None,
            "n_trades":      n,
        }
    a = _arm_metrics(df_arm_a)
    b = _arm_metrics(df_arm_b)
    delta = {}
    for k in ("sharpe", "sortino", "win_rate", "max_dd"):
        if a.get(k) is not None and b.get(k) is not None:
            delta[k] = round(b[k] - a[k], 4)
        else:
            delta[k] = None
    return {label_a: a, label_b: b, "delta": delta}


def compute_net_sharpe_contribution(
    gross_sharpe_lift: float,
    annual_agent_cost_usd: float,
    portfolio_size_usd: float = 100_000.0,
    portfolio_vol_decimal: float = 0.12,
) -> dict:
    """DEC-210 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Net Sharpe contribution
    accounting per Pass 52 turn 72 spec:
      Net Sharpe = Gross Sharpe Lift - Annualized Agent Cost-Sharpe
      cost_sharpe = (annual_cost_usd) / (portfolio_size * portfolio_vol)

    Joint DEC-131 (Agent value-add Sharpe >= 0.2 over rules-only) and
    DEC-420. Spec test signal: $1000/mo on $100K portfolio with 12% vol
    -> cost-Sharpe = (12000) / (100000 * 0.12) = 1.0; agent must clear
    1.2 gross Sharpe lift to meet DEC-131 0.2 net threshold.

    Returns dict with cost_sharpe, net_sharpe, meets_dec_131_threshold (bool).
    """
    if portfolio_size_usd <= 0 or portfolio_vol_decimal <= 0:
        return {"cost_sharpe": None, "net_sharpe": None,
                "meets_dec_131_threshold": False,
                "note": "invalid_portfolio_inputs"}
    cost_sharpe = annual_agent_cost_usd / (portfolio_size_usd * portfolio_vol_decimal)
    net = gross_sharpe_lift - cost_sharpe
    # Use 1e-9 tolerance to make the threshold inclusive against float noise
    # (e.g., spec test signal: gross 1.2, cost 1.0 -> net 0.2 should meet).
    return {
        "cost_sharpe":             round(float(cost_sharpe), 4),
        "net_sharpe":              round(float(net), 4),
        "meets_dec_131_threshold": bool(net >= 0.2 - 1e-9),
        "note":                    "ok",
    }


def compute_per_agent_ablation_contributions(arm_metrics: dict) -> dict:
    """DEC-211 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Per-agent ablation per Pass 52
    turn 72 Option-A narrow scope: 7-arm ablation produces marginal
    Sharpe contribution per agent.

    Marginal contribution per agent = sharpe(full-agents) - sharpe(no-AGENT)
    Positive = agent adds value; negative = agent hurts.

    Inputs:
      arm_metrics: dict mapping arm_name -> {sharpe: float, ...}
        Must include 'full' as a key for the all-agents arm.
        Arms named 'no_Bull', 'no_Bear', etc. for ablated arms.

    Returns dict {agent_name: marginal_sharpe_contribution}.
    """
    if "full" not in arm_metrics:
        return {"_error": "missing_full_arm"}
    full_sharpe = arm_metrics["full"].get("sharpe")
    if full_sharpe is None:
        return {"_error": "full_arm_sharpe_missing"}
    out = {}
    for arm_name, metrics in arm_metrics.items():
        if not arm_name.startswith("no_"):
            continue
        agent_name = arm_name[3:]  # strip 'no_' prefix
        no_agent_sharpe = metrics.get("sharpe")
        if no_agent_sharpe is None:
            out[agent_name] = None
        else:
            out[agent_name] = round(full_sharpe - no_agent_sharpe, 4)
    return out


def diff_trade_logs(df_a, df_b) -> dict:
    """DEC-232 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Determinism test helper per
    Pass 52 turn 85 spec: 2 identical runs should produce byte-identical
    trade ledgers; this helper compares two DataFrames.

    Returns dict with byte_identical (bool), shape_match (bool),
    row_diff_count, first_diff_index (int or None), note.

    Caller-side: feed in two runs of identical config + data; assert
    byte_identical to catch silent non-determinism (dict iteration order,
    threading races).
    """
    import pandas as pd
    if df_a is None or df_b is None:
        return {"byte_identical": False, "shape_match": False,
                "row_diff_count": None, "first_diff_index": None,
                "note": "missing_input"}
    if df_a.shape != df_b.shape:
        return {"byte_identical": False, "shape_match": False,
                "row_diff_count": abs(len(df_a) - len(df_b)),
                "first_diff_index": 0, "note": "shape_mismatch"}
    common_cols = sorted(set(df_a.columns) & set(df_b.columns))
    if not common_cols:
        return {"byte_identical": False, "shape_match": True,
                "row_diff_count": len(df_a), "first_diff_index": 0,
                "note": "no_common_columns"}
    a = df_a[common_cols].reset_index(drop=True)
    b = df_b[common_cols].reset_index(drop=True)
    diffs = (a != b)
    # Treat NaN==NaN as equal
    nan_match = a.isna() & b.isna()
    diffs = diffs & ~nan_match
    row_any_diff = diffs.any(axis=1)
    diff_count = int(row_any_diff.sum())
    first_idx = int(row_any_diff.idxmax()) if diff_count > 0 else None
    return {
        "byte_identical":     diff_count == 0,
        "shape_match":        True,
        "row_diff_count":     diff_count,
        "first_diff_index":   first_idx,
        "note":               "ok" if diff_count == 0 else "DIFF_DETECTED",
    }


def compute_freshness_banner(
    last_updated_iso,
    now=None,
    warn_threshold_hours: float = 24.0,
) -> dict:
    """DEC-287 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 56 2026-05-11
    (owner-approved Path C 5-DEC bundle). Public site freshness signal
    per Pass 52 turn 56 spec.

    Inputs:
      last_updated_iso: ISO-8601 string ('2026-05-11T08:30:00') or None
        (None -> ERROR state: data missing entirely, never silent stale)
      now: optional datetime override for testing (default: datetime.now)
      warn_threshold_hours: hours threshold to flip from OK to WARN

    Returns dict with state ('OK' / 'WARN' / 'ERROR'),
    last_updated_display (str), age_hours (float or None),
    banner_message (str for HTML rendering).

    Module placement note: helper lives in metrics.py instead of
    site_generator.py because site_generator.py contains pre-existing
    non-ASCII chars (em-dashes, warning emoji, multiplication) in
    display strings that would trip the ASCII C1 preflight rule. Helper
    is computation-only; HTML rendering integration is downstream work.
    """
    from datetime import datetime
    if last_updated_iso is None:
        return {
            "state":                 "ERROR",
            "last_updated_display":  "unavailable",
            "age_hours":             None,
            "banner_message":        "Data fetch failed; please retry shortly.",
        }
    try:
        last_dt = datetime.fromisoformat(str(last_updated_iso).replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return {
            "state":                 "ERROR",
            "last_updated_display":  "unavailable",
            "age_hours":             None,
            "banner_message":        "Data timestamp invalid; please retry shortly.",
        }
    now_dt = now if now is not None else datetime.now(tz=last_dt.tzinfo)
    age_seconds = (now_dt - last_dt).total_seconds()
    age_hours = age_seconds / 3600.0
    display = last_dt.strftime("%Y-%m-%d %H:%M ET")
    if age_hours > warn_threshold_hours:
        return {
            "state":                 "WARN",
            "last_updated_display":  display,
            "age_hours":             round(age_hours, 2),
            "banner_message":        f"Data is {age_hours:.0f}h old; awaiting next refresh.",
        }
    return {
        "state":                 "OK",
        "last_updated_display":  display,
        "age_hours":             round(age_hours, 2),
        "banner_message":        f"Last updated: {display}",
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
    # BUG-075 fix 2026-05-13: sort by exit_date so equity curve and drawdown
    # are computed on the chronological sequence of trades, not arbitrary row order.
    if "exit_date" in g.columns:
        g = g.sort_values("exit_date")

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

        # BUG-075 fix 2026-05-13: sort by exit_date for chronological drawdown
        if "exit_date" in r_grp.columns:
            r_grp = r_grp.sort_values("exit_date")
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
    # Batch 186: DSR (Deflated Sharpe Ratio) gate per Bailey & Lopez de Prado 2014.
    # Industry-canonical multi-testing-corrected PSR; threshold default 0.95.
    dsr_value = psr_dict.get("deflated_sharpe") if isinstance(psr_dict, dict) else None
    passes = {
        "win_rate":           win_rate >= pc["min_win_rate"],
        "profit_factor":      pf >= pc["min_profit_factor"],
        "expected_value":     ev > pc["min_expected_value"],
        "win_loss_ratio":     wl_r >= pc["min_win_loss_ratio"],
        "max_drawdown":       mdd >= -pc["max_drawdown"],
        "total_roi":          roi > pc["min_total_roi"],
        # Batch 186 owner-approved 2026-05-16: smart_money_lift / macro_correlation
        # now per-strategy opt-in. When pc[flag] is False (the new default), the
        # gate auto-passes - strategies that don't use these signals aren't
        # penalized. Phase 1B will tag opt-in strategies via per-strategy
        # uses_smart_money_signal / uses_macro_signal attributes (future work).
        "smart_money_lift":   (not pc["smart_money_lift"]) or (sm_lift is None) or (sm_lift >= SM_LIFT_THRESHOLD),
        "macro_correlation":  (not pc["macro_correlation"]) or (macro_corr is None) or (macro_corr >= MACRO_CORR_THRESHOLD),
        "trade_count":        n >= pc["min_trades"],
        # Batch 186 NEW gate: DSR (multi-testing-corrected PSR per Bailey-Lopez 2014).
        # None means insufficient sample - auto-passes to avoid double-penalty
        # with the n>=30 / trade_count gates already in place.
        "deflated_sharpe":    (dsr_value is None) or (dsr_value >= pc.get("min_deflated_sharpe", 0.95)),
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

    # BUG-96 RESOLVED-IMPLEMENTED Batch 108 2026-05-12 (owner-approved
    # option A 2026-05-12): SPY buy-and-hold reference over the same
    # window. Lets owner-facing reports show "strategy +X% / SPY B&H
    # +Y%" side-by-side. Reads SPY OHLCV from the cache (no live calls
    # per DEC-497 NO-LIVE-API HARD CUT). Falls back to None when SPY
    # cache unavailable / df_trades has no entry/exit dates.
    spy_bh_return_pct = None
    spy_bh_window = None
    try:
        if "entry_date" in df.columns and "exit_date" in df.columns:
            from backtest.data.cache import get_ohlcv_bulk as _cached_bulk
            window_start = df["entry_date"].min().date()
            window_end   = df["exit_date"].max().date()
            spy_data = _cached_bulk(["SPY"], start=window_start, end=window_end)
            spy_df_ = spy_data.get("SPY") if spy_data else None
            if spy_df_ is not None and not spy_df_.empty and "close" in spy_df_.columns:
                spy_open  = float(spy_df_["close"].iloc[0])
                spy_close = float(spy_df_["close"].iloc[-1])
                if spy_open > 0:
                    spy_bh_return_pct = round((spy_close - spy_open) / spy_open * 100.0, 2)
                    spy_bh_window = f"{window_start}..{window_end}"
    except Exception as _exc:
        # SPY cache miss / data layer error -> leave benchmark None
        logger.debug("BUG-96 SPY buy-and-hold reference skipped: %s", _exc)

    return {
        "reference_capital_cad": reference_capital,
        "total_pnl_dollar":      round(total_pnl, 2),
        "portfolio_return_pct":  round(portfolio_return_pct, 2),
        "max_portfolio_heat_pct": round(max_heat, 1),
        "avg_position_size_pct": round(float(df["position_size_pct"].mean()) * 100, 2),
        "spy_buy_hold_return_pct": spy_bh_return_pct,    # BUG-96
        "spy_buy_hold_window":     spy_bh_window,        # BUG-96
        "vs_spy_excess_return_pct": (
            round(portfolio_return_pct - spy_bh_return_pct, 2)
            if spy_bh_return_pct is not None else None
        ),
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
