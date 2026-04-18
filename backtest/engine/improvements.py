"""
engine/improvements.py — Five critical improvements to backtest realism.

1. Transaction cost model  — subtracts slippage + commission from every trade
2. Walk-forward validation — in-sample optimise, out-of-sample evaluate
3. Correlation filter      — prevents over-concentrated correlated positions
4. Slippage model          — realistic fill prices based on volatility
5. Regime confidence score — probability-based regime classification

These are applied on top of the base backtest engine results.
"""

import logging
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# 1. TRANSACTION COST MODEL
# ─────────────────────────────────────────────────────────────────────────────

# Realistic slippage + commission estimates per instrument type
TRANSACTION_COSTS = {
    "large_cap":   0.001,   # 0.10% — AAPL, MSFT, NVDA etc (tight spreads)
    "mid_cap":     0.0015,  # 0.15% — smaller S&P 500 members
    "etf":         0.0008,  # 0.08% — ETFs have very tight spreads
    "default":     0.001,   # 0.10% — fallback
}

# Tickers classified as ETFs for cost purposes
ETF_TICKERS = {
    "SPY","QQQ","IWM","DIA","VTI","XLK","XLF","XLE","XLV","XLI",
    "XLY","XLP","XLU","XLB","XLRE","VXX","TLT","HYG","LQD","IEF",
    "SHY","GLD","SLV","GDX","USO","EEM","EFA",
}


def get_transaction_cost(ticker: str, market_cap_m: float = 0) -> float:
    """Return round-trip transaction cost percentage for a ticker."""
    if ticker in ETF_TICKERS:
        return TRANSACTION_COSTS["etf"]
    if market_cap_m >= 10_000:    # >$10B = large cap
        return TRANSACTION_COSTS["large_cap"]
    if market_cap_m >= 2_000:     # $2-10B = mid cap
        return TRANSACTION_COSTS["mid_cap"]
    return TRANSACTION_COSTS["default"]


def apply_transaction_costs(
    df_trades: pd.DataFrame,
    info_dict:  dict[str, dict],
) -> pd.DataFrame:
    """
    Apply realistic transaction costs to all trades.
    Subtracts one-way cost on entry + one-way cost on exit.
    Updates pnl_pct, win, and adds cost_pct column.

    This is the single most important realism improvement.
    A strategy with 1.21 profit factor before costs may fall below 1.2 after.
    """
    df = df_trades.copy()

    costs = []
    for _, row in df.iterrows():
        ticker = row.get("ticker", "")
        mkt_cap_m = (info_dict.get(ticker, {}).get("market_cap", 0) or 0) / 1_000_000
        cost = get_transaction_cost(ticker, mkt_cap_m)
        # Round trip = entry cost + exit cost
        round_trip = cost * 2
        costs.append(round_trip * 100)  # as percentage

    df["cost_pct"]   = costs
    df["pnl_pct_gross"] = df["pnl_pct"].copy()
    df["pnl_pct"]    = df["pnl_pct"] - df["cost_pct"]
    df["win"]        = df["pnl_pct"] > 0

    total_cost = df["cost_pct"].sum()
    gross_roi  = df["pnl_pct_gross"].sum()
    net_roi    = df["pnl_pct"].sum()

    logger.info(
        "Transaction costs applied: gross ROI=%.1f%% net ROI=%.1f%% total_cost=%.1f%%",
        gross_roi, net_roi, total_cost,
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. WALK-FORWARD VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def run_walk_forward(
    df_trades: pd.DataFrame,
    in_sample_end: date = date(2023, 12, 31),
    out_of_sample_start: date = date(2024, 1, 1),
) -> dict:
    """
    Split trade log into in-sample and out-of-sample periods.
    Evaluates whether strategies that pass in-sample also pass out-of-sample.

    In-sample:       2022-01-01 → 2023-12-31 (optimise on this)
    Out-of-sample:   2024-01-01 → 2024-12-31 (validate on this, untouched)

    A strategy that passes in-sample but fails out-of-sample is overfit.
    A strategy that passes both is robust.
    """
    df_trades = df_trades.copy()
    df_trades["entry_date"] = pd.to_datetime(df_trades["entry_date"]).dt.date

    in_sample  = df_trades[df_trades["entry_date"] <= in_sample_end]
    out_sample = df_trades[df_trades["entry_date"] >= out_of_sample_start]

    results = {}

    for strategy in df_trades["strategy"].unique():
        is_trades  = in_sample[in_sample["strategy"] == strategy]
        oos_trades = out_sample[out_sample["strategy"] == strategy]

        def metrics(t):
            if len(t) < 5:
                return None
            wins = t["pnl_pct"] > 0
            pnl  = t["pnl_pct"]
            wr   = wins.mean()
            pf_w = pnl[wins].sum()
            pf_l = abs(pnl[~wins].sum())
            pf   = round(pf_w / pf_l, 3) if pf_l > 0 else 999
            return {
                "trades":        len(t),
                "win_rate":      round(wr, 4),
                "profit_factor": pf,
                "total_roi":     round(pnl.sum(), 3),
                "avg_pnl":       round(pnl.mean(), 4),
            }

        is_m  = metrics(is_trades)
        oos_m = metrics(oos_trades)

        if is_m is None:
            continue

        is_pass  = (is_m["win_rate"] >= 0.55 and is_m["profit_factor"] >= 1.2
                    and is_m["total_roi"] > 0 and is_m["trades"] >= 50)
        oos_pass = (oos_m is not None and oos_m["win_rate"] >= 0.55
                    and oos_m["profit_factor"] >= 1.2
                    and oos_m["total_roi"] > 0) if oos_m else False

        verdict = (
            "ROBUST"     if is_pass and oos_pass  else
            "OVERFIT"    if is_pass and not oos_pass else
            "WEAK"       if not is_pass and oos_pass else
            "FAILS_BOTH"
        )

        # Degradation — how much did performance drop out-of-sample?
        wr_degradation = None
        if oos_m and is_m:
            wr_degradation = round(oos_m["win_rate"] - is_m["win_rate"], 4)

        results[strategy] = {
            "in_sample":        is_m,
            "out_of_sample":    oos_m,
            "in_sample_pass":   is_pass,
            "oos_pass":         oos_pass,
            "verdict":          verdict,
            "wr_degradation":   wr_degradation,
        }

    # Summary
    total    = len(results)
    robust   = sum(1 for r in results.values() if r["verdict"] == "ROBUST")
    overfit  = sum(1 for r in results.values() if r["verdict"] == "OVERFIT")
    weak     = sum(1 for r in results.values() if r["verdict"] == "WEAK")

    logger.info(
        "Walk-forward: %d strategies | ROBUST=%d | OVERFIT=%d | WEAK=%d",
        total, robust, overfit, weak,
    )
    return {
        "strategy_results": results,
        "summary": {
            "total":   total,
            "robust":  robust,
            "overfit": overfit,
            "weak":    weak,
            "in_sample_period":      f"2022-01-01 → {in_sample_end}",
            "out_of_sample_period":  f"{out_of_sample_start} → 2024-12-31",
        },
    }


def walk_forward_to_df(wf_results: dict) -> pd.DataFrame:
    """Convert walk-forward results dict to a flat DataFrame for CSV export."""
    rows = []
    for strategy, r in wf_results.get("strategy_results", {}).items():
        is_m  = r.get("in_sample") or {}
        oos_m = r.get("out_of_sample") or {}
        rows.append({
            "strategy":             strategy,
            "verdict":              r["verdict"],
            "is_trades":            is_m.get("trades", 0),
            "is_win_rate":          is_m.get("win_rate", 0),
            "is_profit_factor":     is_m.get("profit_factor", 0),
            "is_total_roi":         is_m.get("total_roi", 0),
            "oos_trades":           oos_m.get("trades", 0),
            "oos_win_rate":         oos_m.get("win_rate", 0),
            "oos_profit_factor":    oos_m.get("profit_factor", 0),
            "oos_total_roi":        oos_m.get("total_roi", 0),
            "wr_degradation":       r.get("wr_degradation"),
            "in_sample_pass":       r["in_sample_pass"],
            "oos_pass":             r["oos_pass"],
        })
    return pd.DataFrame(rows).sort_values("verdict")


# ─────────────────────────────────────────────────────────────────────────────
# 3. CORRELATION FILTER
# ─────────────────────────────────────────────────────────────────────────────

def correlation_filter(
    candidate_ticker: str,
    open_positions: list,           # list of OpenTrade objects
    corr_matrix: pd.DataFrame,
    max_correlation: float = 0.70,
    max_same_sector: int = 3,
    sector_map: dict = None,
) -> tuple[bool, str]:
    """
    Check if a new position would create unacceptable correlation with existing positions.

    Returns (allowed: bool, reason: str).

    Rules:
    1. No new position if correlation with any existing position > 0.70
    2. Maximum 3 open positions in the same sector at once
    3. These prevent real drawdown being 2-3× what backtest shows
    """
    if corr_matrix.empty or not open_positions:
        return True, "no_existing_positions"

    open_tickers = [p.ticker for p in open_positions]

    # Rule 1: Correlation check
    if candidate_ticker in corr_matrix.index:
        for existing_ticker in open_tickers:
            if existing_ticker in corr_matrix.columns:
                corr = corr_matrix.loc[candidate_ticker, existing_ticker]
                if abs(corr) > max_correlation:
                    return False, (f"correlation_{corr:.2f}_with_{existing_ticker}_"
                                   f"exceeds_{max_correlation}")

    # Rule 2: Sector concentration
    if sector_map:
        candidate_sector = sector_map.get(candidate_ticker, "Unknown")
        if candidate_sector != "Unknown":
            same_sector = sum(
                1 for t in open_tickers
                if sector_map.get(t) == candidate_sector
            )
            if same_sector >= max_same_sector:
                return False, (f"sector_concentration_{candidate_sector}_"
                               f"already_{same_sector}_positions")

    return True, "passed"


# ─────────────────────────────────────────────────────────────────────────────
# 4. SLIPPAGE MODEL
# ─────────────────────────────────────────────────────────────────────────────

def apply_slippage(
    entry_price: float,
    direction: str,
    atr: float,
    ticker: str,
    gap_pct: float = 0.0,
) -> tuple[float, float]:
    """
    Apply realistic slippage to entry price.

    Two slippage components:
    1. Market impact — proportional to ATR (how volatile the stock is)
    2. Bid-ask spread — fixed percentage based on instrument type

    Returns (adjusted_entry_price, slippage_pct).

    For gap-up opens (breakout strategies), slippage is larger because
    you are competing with other buyers on the gap.
    """
    # Base spread slippage
    if ticker in ETF_TICKERS:
        spread_pct = 0.0003   # 0.03% for ETFs
    elif atr / max(entry_price, 1) > 0.03:
        spread_pct = 0.0015   # 0.15% for high-volatility stocks
    else:
        spread_pct = 0.0008   # 0.08% for normal large-caps

    # Gap penalty — larger gap = harder to get a good fill
    gap_penalty = min(abs(gap_pct) * 0.1, 0.003)  # max 0.3% gap penalty

    total_slippage = spread_pct + gap_penalty

    if direction == "long":
        adjusted = entry_price * (1 + total_slippage)
    else:
        adjusted = entry_price * (1 - total_slippage)

    return round(adjusted, 4), round(total_slippage * 100, 4)


# ─────────────────────────────────────────────────────────────────────────────
# 5. REGIME CONFIDENCE SCORE
# ─────────────────────────────────────────────────────────────────────────────

def regime_confidence(
    vix_values:      pd.Series,     # recent VIX history
    spy_vs_ema200:   pd.Series,     # SPY % above/below 200 EMA history
    lookback_days:   int = 20,
) -> dict:
    """
    Compute regime confidence score (0-100) based on how firmly
    established the current regime is.

    Low confidence = regime is transitioning = reduce position sizes.
    High confidence = regime is established = full position sizes allowed.

    Components:
    - VIX consistency: how stable VIX has been in its current range
    - Trend persistence: how many consecutive days SPY has been above/below 200 EMA
    - Signal agreement: do VIX and trend agree on the regime?
    """
    if vix_values.empty or len(vix_values) < 5:
        return {"regime": "unknown", "confidence": 50, "position_mult": 0.75}

    recent_vix = vix_values.tail(lookback_days)
    current_vix = float(recent_vix.iloc[-1])

    # VIX regime
    if current_vix >= 40:
        vix_regime = "crisis"
    elif current_vix >= 25:
        vix_regime = "bear"
    elif current_vix <= 20:
        vix_regime = "bull"
    else:
        vix_regime = "neutral"

    # VIX consistency — std dev of recent VIX relative to its mean
    vix_cv = float(recent_vix.std() / max(recent_vix.mean(), 1))
    vix_consistency = max(0, 100 - vix_cv * 200)  # 0-100

    # Trend persistence — consecutive days in current trend
    trend_days = 0
    if not spy_vs_ema200.empty:
        current_above = float(spy_vs_ema200.iloc[-1]) > 0
        for val in reversed(spy_vs_ema200.values):
            if (val > 0) == current_above:
                trend_days += 1
            else:
                break
        trend_regime = "bull" if current_above else "bear"
    else:
        trend_regime = "unknown"
        trend_days   = 0

    trend_persistence = min(trend_days / lookback_days * 100, 100)

    # Signal agreement
    agreement = 100 if vix_regime == trend_regime or vix_regime == "neutral" else 40

    # Composite confidence
    confidence = round(
        0.4 * vix_consistency +
        0.35 * trend_persistence +
        0.25 * agreement,
        1,
    )

    # Position multiplier based on confidence
    if confidence >= 75:
        position_mult = 1.0    # full size
    elif confidence >= 50:
        position_mult = 0.75   # 75% size
    elif confidence >= 25:
        position_mult = 0.50   # 50% size
    else:
        position_mult = 0.25   # 25% size — regime very uncertain

    regime = vix_regime if vix_regime != "neutral" else trend_regime

    return {
        "regime":             regime,
        "confidence":         confidence,
        "position_mult":      position_mult,
        "vix_consistency":    round(vix_consistency, 1),
        "trend_persistence":  round(trend_persistence, 1),
        "trend_days":         trend_days,
        "signal_agreement":   agreement,
        "current_vix":        round(current_vix, 2),
        "description": (
            f"Regime {regime} with {confidence:.0f}% confidence — "
            f"VIX stable ({vix_consistency:.0f}%), "
            f"trend persistent {trend_days}d — "
            f"use {position_mult*100:.0f}% of normal position size"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# BONFERRONI CORRECTION FOR MULTIPLE TESTING
# ─────────────────────────────────────────────────────────────────────────────

def bonferroni_adjusted_threshold(
    n_strategies: int,
    base_significance: float = 0.05,
    min_win_rate: float = 0.55,
) -> dict:
    """
    Compute Bonferroni-corrected significance thresholds.

    With 60 strategies tested, the probability of at least one false positive
    at p=0.05 is 1-(0.95)^60 = 95%. We need stricter thresholds.

    Returns adjusted thresholds for win rate and minimum trades required.
    """
    adjusted_p = base_significance / n_strategies

    # For a binomial test, minimum trades needed to achieve adjusted significance
    # at the given win rate threshold
    import math

    def min_trades_for_significance(win_rate, p_value):
        # Approximate using normal distribution (valid for large n)
        z = 2.576  # z-score for p=0.005 (two-tailed)
        # For one-tailed test: H0: wr <= 0.5, H1: wr > 0.5
        # n >= z^2 * p*(1-p) / (wr - 0.5)^2
        if win_rate <= 0.5:
            return float("inf")
        z_adj = abs(stats_z(p_value))
        n = (z_adj**2 * win_rate * (1 - win_rate)) / ((win_rate - 0.5)**2)
        return math.ceil(n)

    def stats_z(p):
        # Approximate z-score for given p-value (one-tailed)
        # Using standard approximation
        import math
        if p >= 0.5:
            return 0
        return math.sqrt(-2 * math.log(p)) * 0.97  # approximation

    min_trades = min_trades_for_significance(min_win_rate, adjusted_p)

    return {
        "n_strategies":          n_strategies,
        "base_significance":     base_significance,
        "adjusted_significance": round(adjusted_p, 6),
        "min_win_rate":          min_win_rate,
        "min_trades_required":   min(min_trades, 500),  # cap at 500
        "false_positive_prob_uncorrected": round(1 - (1 - base_significance)**n_strategies, 3),
        "false_positive_prob_corrected":   round(base_significance, 3),
        "recommendation": (
            f"With {n_strategies} strategies tested, require at least "
            f"{min(min_trades, 500)} trades per strategy for statistical validity "
            f"(Bonferroni-corrected at p={adjusted_p:.4f})"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SURVIVORSHIP BIAS HAIRCUT
# ─────────────────────────────────────────────────────────────────────────────

SURVIVORSHIP_BIAS_HAIRCUT = 0.02   # 2% annual ROI haircut

def apply_survivorship_haircut(
    total_roi: float,
    years: float = 3.0,
) -> tuple[float, float]:
    """
    Apply survivorship bias haircut to total ROI.
    Studies show 1-3% annual inflation from survivorship bias on large-cap backtests.
    We use 2% as conservative middle estimate.

    Returns (adjusted_roi, haircut_applied).
    """
    haircut = SURVIVORSHIP_BIAS_HAIRCUT * years * 100  # as percentage
    adjusted = total_roi - haircut
    return round(adjusted, 3), round(haircut, 3)
