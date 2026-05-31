"""Batch 504 (2026-05-31) -- Tier C + D + E cube cell metrics.

Source: per CHECKLIST #77 + owner directive 2026-05-31 "resolve
everything else autonomously".
Queue row: EXECUTION_QUEUE.md item #5 cube-cell-metrics-expansion.

Companion to:
  backtest/results/cube_populator.py  (Tier A baseline metrics)
  backtest/results/cube_metrics_tier_b.py (Tier B slice metrics)

Tier C -- new computation (post-hoc on existing trade subset):
  sharpe_ci_95 : bootstrap 95% confidence interval on Sharpe
  oos_sharpe   : Sharpe on out-of-sample subset
  is_oos_decay : IS_Sharpe - OOS_Sharpe (positive -> overfit risk)
  effective_n  : autocorrelation-adjusted effective sample size

Tier D -- composite scores:
  sqn       : System Quality Number (Van Tharp) = mean / std * sqrt(n)
  k_ratio   : trend strength on equity curve (Linda Bradford Raschke)
  mar       : Mean Annual Return / abs(Max Drawdown) [a.k.a. MAR ratio]

Tier E -- risk management:
  kelly_fraction : optimal fractional Kelly bet size
  cvar_5pct      : Conditional VaR at 5% tail
  risk_of_ruin   : probability of equity touching zero given current edge

All functions take a trades DataFrame (with `pnl_pct` + optionally
`entry_date` / `hold_days`) and return a dict of metric values.
Graceful degradation: empty / short input -> values absent or zeroed.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Tier C: new computation
# ---------------------------------------------------------------------------

def compute_sharpe_ci_95(pnls: np.ndarray, n_boot: int = 1000,
                         seed: int = 42) -> dict:
    """Bootstrap 95% CI on Sharpe ratio (per-trade approx).

    For each bootstrap sample (sampling with replacement, same size as
    input), compute Sharpe; return [2.5pct, 97.5pct] quantiles.
    Returns sharpe_ci_low / sharpe_ci_high; empty when n < 30.
    """
    if pnls is None or len(pnls) < 30:
        return {}
    rng = np.random.default_rng(seed)
    sharpes = []
    n = len(pnls)
    for _ in range(n_boot):
        sample = pnls[rng.integers(0, n, size=n)]
        s = sample.std(ddof=1)
        if s > 0:
            sharpes.append(sample.mean() / s * np.sqrt(252))
    if not sharpes:
        return {}
    arr = np.array(sharpes)
    return {
        "sharpe_ci_low":  round(float(np.quantile(arr, 0.025)), 4),
        "sharpe_ci_high": round(float(np.quantile(arr, 0.975)), 4),
    }


def compute_oos_decay(
    trades: pd.DataFrame,
    is_oos_split: float = 0.7,
) -> dict:
    """IS / OOS Sharpe split with a chronological cut.

    Sorts trades by entry_date, takes first `is_oos_split` as IS,
    remainder as OOS, computes Sharpe in each + the decay.
    Empty / short input -> empty dict.
    """
    if trades is None or trades.empty or "entry_date" not in trades.columns:
        return {}
    n = len(trades)
    if n < 60:  # need at least 30 per side
        return {}
    df = trades.copy()
    df["__dt"] = pd.to_datetime(df["entry_date"])
    df = df.sort_values("__dt").reset_index(drop=True)
    cut = int(n * is_oos_split)
    is_pnls = df.iloc[:cut]["pnl_pct"].astype(float).values
    oos_pnls = df.iloc[cut:]["pnl_pct"].astype(float).values
    def _sharpe(arr):
        if len(arr) < 2:
            return 0.0
        s = arr.std(ddof=1)
        return float(arr.mean() / s * np.sqrt(252)) if s > 0 else 0.0
    is_sh  = _sharpe(is_pnls)
    oos_sh = _sharpe(oos_pnls)
    return {
        "is_sharpe":    round(is_sh, 4),
        "oos_sharpe":   round(oos_sh, 4),
        "is_oos_decay": round(is_sh - oos_sh, 4),
    }


def compute_effective_n(pnls: np.ndarray) -> dict:
    """Autocorrelation-adjusted effective sample size.

    n_eff = n * (1 - rho1) / (1 + rho1) where rho1 is lag-1 autocorr.
    When trades are positively autocorrelated (rho1 > 0), effective n
    is smaller than raw n -- a Sharpe of K from rho1=0.3 is less
    reliable than K from rho1=0. Returns dict with autocorr_lag1 and
    effective_n; empty when n < 30.
    """
    if pnls is None or len(pnls) < 30:
        return {}
    n = len(pnls)
    arr = np.asarray(pnls, dtype=float)
    centered = arr - arr.mean()
    denom = (centered ** 2).sum()
    if denom == 0:
        return {"autocorr_lag1": 0.0, "effective_n": int(n)}
    numer = (centered[:-1] * centered[1:]).sum()
    rho1 = float(numer / denom)
    rho1 = max(-0.99, min(0.99, rho1))
    eff_n = n * (1.0 - rho1) / (1.0 + rho1)
    return {
        "autocorr_lag1": round(rho1, 4),
        "effective_n":   int(max(1, round(eff_n))),
    }


# ---------------------------------------------------------------------------
# Tier D: composite scores
# ---------------------------------------------------------------------------

def compute_sqn(pnls: np.ndarray) -> dict:
    """Van Tharp System Quality Number = mean / std * sqrt(n).

    Different from Sharpe in that it does NOT annualize via 252;
    instead uses raw n. Tharp's interpretation:
      < 1.6: poor system
      1.6 - 1.9: below average
      2.0 - 2.4: average
      2.5 - 2.9: good
      3.0 - 5.0: excellent
      > 5.0: holy grail
    """
    if pnls is None or len(pnls) < 2:
        return {}
    arr = np.asarray(pnls, dtype=float)
    s = arr.std(ddof=1)
    if s == 0:
        return {"sqn": 0.0}
    return {"sqn": round(float(arr.mean() / s * np.sqrt(len(arr))), 4)}


def compute_k_ratio(pnls: np.ndarray) -> dict:
    """Linda Bradford Raschke K-ratio: slope of cumulative-pnl regression
    divided by its standard error, scaled by sqrt(n).

    Higher K-ratio = more linear, consistent equity-curve growth.
    Negative K-ratio = downtrending equity.
    """
    if pnls is None or len(pnls) < 3:
        return {}
    cum = np.cumsum(np.asarray(pnls, dtype=float))
    n = len(cum)
    x = np.arange(n)
    # OLS slope: cov(x, y) / var(x)
    x_mean = x.mean()
    y_mean = cum.mean()
    cov = ((x - x_mean) * (cum - y_mean)).sum()
    varx = ((x - x_mean) ** 2).sum()
    if varx == 0:
        return {"k_ratio": 0.0}
    slope = cov / varx
    # Residuals + standard error of slope
    resid = cum - (slope * (x - x_mean) + y_mean)
    if n - 2 <= 0:
        return {"k_ratio": 0.0}
    s_err = float((resid ** 2).sum() / (n - 2))
    if s_err <= 0:
        return {"k_ratio": 0.0}
    se_slope = (s_err / varx) ** 0.5
    if se_slope == 0:
        return {"k_ratio": 0.0}
    k = (slope / se_slope) * (n ** 0.5) / 100.0
    return {"k_ratio": round(float(k), 4)}


def compute_mar_ratio(pnls: np.ndarray, periods_per_year: int = 252) -> dict:
    """MAR ratio = annualized return / abs(max drawdown).

    Annualized return = mean per-trade pnl * trades-per-year.
    Max drawdown computed on cumulative pnl peak-to-trough.
    """
    if pnls is None or len(pnls) < 2:
        return {}
    arr = np.asarray(pnls, dtype=float)
    cum = np.cumsum(arr)
    peak = np.maximum.accumulate(cum)
    dd = peak - cum
    max_dd = float(dd.max())
    if max_dd <= 0:
        return {"mar_ratio": 0.0, "max_dd_value": 0.0}
    # Annualized via simple approximation: mean per trade * (estimated
    # trades per year). When entry-date data isn't available, use raw n
    # as the trade count and 252 as the working-day year.
    ann_ret = arr.mean() * periods_per_year
    return {
        "mar_ratio":    round(float(ann_ret / max_dd), 4),
        "max_dd_value": round(max_dd, 4),
    }


# ---------------------------------------------------------------------------
# Tier E: risk management
# ---------------------------------------------------------------------------

def compute_kelly_fraction(pnls: np.ndarray) -> dict:
    """Optimal Kelly fraction = WR / loss_avg - (1 - WR) / win_avg.

    Bounded to [0, 1]; negative -> 0 (no edge, no bet).
    """
    if pnls is None or len(pnls) < 2:
        return {}
    arr = np.asarray(pnls, dtype=float)
    wins = arr[arr > 0]
    losses = arr[arr <= 0]
    if len(wins) == 0 or len(losses) == 0:
        return {"kelly_fraction": 0.0}
    wr = float(len(wins) / len(arr))
    avg_win = float(wins.mean())
    avg_loss = float(abs(losses.mean()))
    if avg_win == 0 or avg_loss == 0:
        return {"kelly_fraction": 0.0}
    kelly = wr / avg_loss - (1.0 - wr) / avg_win
    # Bound to [0, 1] for sane sizing
    kelly = max(0.0, min(1.0, kelly))
    return {"kelly_fraction": round(kelly, 4)}


def compute_cvar(pnls: np.ndarray, alpha: float = 0.05) -> dict:
    """Conditional Value at Risk: expected loss given loss exceeds the
    VaR threshold. CVaR_5% = E[loss | loss <= 5pct-quantile].

    Returns dict with var_5pct (VaR value) + cvar_5pct.
    """
    if pnls is None or len(pnls) < 20:
        return {}
    arr = np.asarray(pnls, dtype=float)
    var = float(np.quantile(arr, alpha))
    tail = arr[arr <= var]
    if len(tail) == 0:
        return {}
    return {
        f"var_{int(alpha*100)}pct":  round(var, 4),
        f"cvar_{int(alpha*100)}pct": round(float(tail.mean()), 4),
    }


def compute_risk_of_ruin(
    pnls: np.ndarray,
    risk_per_trade: float = 0.02,
    target_drawdown: float = 1.0,
) -> dict:
    """Estimate probability of ruin under repeated bets.

    Uses the standard formula:
      R = ((1 - edge) / (1 + edge)) ** (target_drawdown / risk_per_trade)
    where edge = WR * avg_win - (1 - WR) * avg_loss normalized to a
    bet expressed as a fraction of capital. For per-trade pnl_pct, we
    approximate edge directly as the per-trade mean / abs(avg_loss).
    """
    if pnls is None or len(pnls) < 30:
        return {}
    arr = np.asarray(pnls, dtype=float)
    wins = arr[arr > 0]
    losses = arr[arr <= 0]
    if len(wins) == 0 or len(losses) == 0:
        return {"risk_of_ruin": 0.0}
    avg_loss = float(abs(losses.mean()))
    if avg_loss == 0:
        return {"risk_of_ruin": 0.0}
    edge = float(arr.mean()) / avg_loss
    if edge <= 0:
        # No edge -> guaranteed ruin over infinite play
        return {"risk_of_ruin": 1.0, "edge_estimate": round(edge, 4)}
    if edge >= 1:
        return {"risk_of_ruin": 0.0, "edge_estimate": round(edge, 4)}
    n_bets = target_drawdown / max(risk_per_trade, 1e-9)
    ratio = (1.0 - edge) / (1.0 + edge)
    ror = ratio ** n_bets
    return {
        "risk_of_ruin":  round(float(ror), 6),
        "edge_estimate": round(edge, 4),
    }


# ---------------------------------------------------------------------------
# Top-level aggregator: emit all Tier C/D/E for a per-cell trades subset
# ---------------------------------------------------------------------------

def compute_tier_cde_metrics(trades: pd.DataFrame) -> dict:
    """Run every Tier C/D/E primitive and merge into a single dict.

    Degrades gracefully when input is empty or too short.
    """
    if trades is None or trades.empty:
        return {}
    if "pnl_pct" not in trades.columns:
        return {}
    pnls = trades["pnl_pct"].astype(float).values
    out: dict = {}
    out.update(compute_sharpe_ci_95(pnls))
    out.update(compute_oos_decay(trades))
    out.update(compute_effective_n(pnls))
    out.update(compute_sqn(pnls))
    out.update(compute_k_ratio(pnls))
    out.update(compute_mar_ratio(pnls))
    out.update(compute_kelly_fraction(pnls))
    out.update(compute_cvar(pnls))
    out.update(compute_risk_of_ruin(pnls))
    return out


__all__ = [
    "compute_sharpe_ci_95",
    "compute_oos_decay",
    "compute_effective_n",
    "compute_sqn",
    "compute_k_ratio",
    "compute_mar_ratio",
    "compute_kelly_fraction",
    "compute_cvar",
    "compute_risk_of_ruin",
    "compute_tier_cde_metrics",
]
