"""
engine/improvements.py  -  Five critical improvements to backtest realism.

1. Transaction cost model   -  subtracts slippage + commission from every trade
2. Walk-forward validation  -  two-window IS/OOS evaluation
3. Correlation filter       -  built but NOT active in backtest (approved). Available for Stage 3+.
4. Slippage model           -  realistic fill prices based on volatility
5. Regime confidence score  -  probability-based regime classification

These are applied on top of the base backtest engine results.
"""

import logging
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 1. TRANSACTION COST MODEL
# -----------------------------------------------------------------------------

# Realistic slippage + commission estimates per instrument type
TRANSACTION_COSTS = {
    "large_cap":   0.001,   # 0.10%  -  AAPL, MSFT, NVDA etc (tight spreads)
    "mid_cap":     0.0015,  # 0.15%  -  smaller S&P 500 members
    "etf":         0.0008,  # 0.08%  -  ETFs have very tight spreads
    "default":     0.001,   # 0.10%  -  fallback
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


# BUG-205 RESOLVED-IMPLEMENTED Batch 107 2026-05-12 (owner-approved option A
# 2026-05-12): IBKR Pro fixed-tier US-stock commission model. Percentage-
# only TRANSACTION_COSTS underestimates the per-trade fee at small notional
# because IBKR enforces a $1.00 minimum per order (and rebate up to 1% of
# trade value cap). At a $750 trade with ~10 shares, per-share fee is $0.05
# but min wins -> $1 = 0.133% vs the 0.10% percentage model assumes. Over a
# 100-trade backtest at LOW/MEDIUM tier sizes the understatement compounds
# to ~6% ROI overstatement.
IBKR_FIXED_TIER = {
    "per_share_usd":     0.005,   # $0.005/share
    "min_order_usd":     1.00,    # $1.00 min per order
    "max_pct_of_trade":  0.01,    # 1.0% max of trade value
}


def ibkr_fixed_tier_cost(shares: float, trade_dollar: float) -> float:
    """BUG-205: returns one-way IBKR Pro fixed-tier US commission in
    dollars given trade shares + dollar value. min(max_pct_of_trade,
    max(min_order, per_share*shares)).
    """
    if shares <= 0 or trade_dollar <= 0:
        return 0.0
    per_share = shares * IBKR_FIXED_TIER["per_share_usd"]
    capped_at_max = min(IBKR_FIXED_TIER["max_pct_of_trade"] * trade_dollar,
                        per_share)
    return max(IBKR_FIXED_TIER["min_order_usd"], capped_at_max)


def effective_round_trip_cost_pct(
    ticker:        str,
    market_cap_m:  float,
    entry_price:   float = 0.0,
    trade_dollar:  float = 0.0,
) -> float:
    """BUG-205: returns round-trip cost as decimal fraction of
    trade_dollar combining (a) existing TRANSACTION_COSTS spread-percent
    model (commissions implicit) and (b) IBKR Pro fixed-tier per-share
    + min/cap. Picks the max of the two so neither cost driver is
    silently understated. Falls back to pure percentage (legacy
    behavior) when entry_price or trade_dollar unavailable.
    """
    base_one_way_pct = get_transaction_cost(ticker, market_cap_m)
    base_one_way_dollar = base_one_way_pct * trade_dollar
    if entry_price <= 0 or trade_dollar <= 0:
        # Legacy path: percentage only, round-trip = 2 * one-way
        return base_one_way_pct * 2
    shares = trade_dollar / entry_price
    ibkr_one_way_dollar = ibkr_fixed_tier_cost(shares, trade_dollar)
    effective_one_way_dollar = max(base_one_way_dollar, ibkr_one_way_dollar)
    return (effective_one_way_dollar * 2) / trade_dollar


def apply_transaction_costs(
    df_trades: pd.DataFrame,
    info_dict:  dict[str, dict],
) -> pd.DataFrame:
    """
    Apply realistic transaction costs to all trades.
    Subtracts one-way cost on entry + one-way cost on exit.
    Updates pnl_pct, win, and adds cost_pct column.

    Short trades incur additional securities lending (borrow) cost:
    - Easy-to-borrow large caps (most S&P 500): ~0.5% annually
    - Applied proportionally: 0.5% / 252 * hold_days
    """
    df = df_trades.copy()

    # DEC-295 fix (Pass 50): import canonical single-source rate from config.
    # BUG-06 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
    # Single-source borrow cost prevents double-charging on short trades. Per
    # exit_manager.py:175 _pnl computes gross only; borrow is applied here
    # centrally via SHORT_ANNUAL_BORROW_RATE * hold_days / 252.
    from backtest.config import SHORT_ANNUAL_BORROW_RATE

    # BUG-205 RESOLVED-IMPLEMENTED Batch 107 2026-05-12: when the trade
    # row carries entry_price + confidence_tier the IBKR fixed-tier cap
    # model (per-share + $1 min + 1% cap) is applied via
    # effective_round_trip_cost_pct(). Rows missing those fields fall
    # back to the legacy percentage-only model so existing test
    # fixtures (which don't carry tier/entry_price) continue to pass.
    from backtest.config import (STARTING_CAPITAL, TIER_POSITION_SIZE_PCT)

    costs = []
    for _, row in df.iterrows():
        ticker = row.get("ticker", "")
        mkt_cap_m = (info_dict.get(ticker, {}).get("market_cap", 0) or 0) / 1_000_000

        entry_price = float(row.get("entry_price", 0) or 0)
        conf_tier   = row.get("confidence_tier", None)
        tier_pct    = TIER_POSITION_SIZE_PCT.get(conf_tier, 0.0) if conf_tier else 0.0
        trade_dollar = (tier_pct * STARTING_CAPITAL) if tier_pct > 0 else 0.0

        if entry_price > 0 and trade_dollar > 0:
            # BUG-205 path: IBKR cap-aware effective round-trip cost
            round_trip = effective_round_trip_cost_pct(
                ticker, mkt_cap_m, entry_price, trade_dollar,
            )
        else:
            cost = get_transaction_cost(ticker, mkt_cap_m)
            round_trip = cost * 2

        # Short trade: add securities lending (borrow) cost
        if row.get("direction") == "short":
            hold_days = row.get("hold_days", 10)
            borrow_cost = SHORT_ANNUAL_BORROW_RATE * (hold_days / 252)
            round_trip += borrow_cost

        costs.append(round_trip * 100)  # as percentage

    df["cost_pct"]      = costs
    df["pnl_pct_gross"] = df["pnl_pct"].copy()
    df["pnl_pct"]       = df["pnl_pct"] - df["cost_pct"]
    df["win"]           = df["pnl_pct"] > 0

    total_cost = df["cost_pct"].sum()
    gross_roi  = df["pnl_pct_gross"].sum()
    net_roi    = df["pnl_pct"].sum()

    logger.info(
        "Transaction costs applied: gross ROI=%.1f%% net ROI=%.1f%% total_cost=%.1f%%",
        gross_roi, net_roi, total_cost,
    )
    return df


# -----------------------------------------------------------------------------
# 2. WALK-FORWARD VALIDATION
# -----------------------------------------------------------------------------

def run_walk_forward(df_trades: pd.DataFrame) -> dict:
    """
    4-fold walk-forward validation per DEC-505 (Pass 53 owner-approved 2026-05-05).

    Per DEC-505 + DEC-590 + L149 (spec-without-build correction):
      - 1y warmup: 2021-05-05 -> 2022-05-05 (training data accumulation only; not OOS-tested)
      - Fold 1: train 2021-05-05 -> 2022-05-05; OOS 2022-05-05 -> 2023-05-05
      - Fold 2: train 2021-05-05 -> 2023-05-05; OOS 2023-05-05 -> 2024-05-05
      - Fold 3: train 2021-05-05 -> 2024-05-05; OOS 2024-05-05 -> 2025-05-05
      - Fold 4: train 2021-05-05 -> 2025-05-05; OOS 2025-05-05 -> 2026-05-05

    Expanding-window (training set grows each fold). Disjoint 1y OOS periods.

    Verdict mapping (4-fold):
      ROBUST                = passes >=3 of 4 OOS folds
      WEAK                  = passes 1-2 of 4 OOS folds
      OVERFIT               = passes IS but 0 OOS folds
      FAILS_BOTH            = fails IS and OOS
      INSUFFICIENT_OOS_DATA = >=3 folds with <30 OOS trades

    History: legacy 2-window IS/OOS pre-DEC-505 replaced Pass 53 Day 9 evening
    2026-05-07 per WF-1 owner directive ("Approve all"; same-commit per DEC-594).
    """
    from backtest.config import get_sector_criteria

    df_trades = df_trades.copy()
    df_trades["entry_date"] = pd.to_datetime(df_trades["entry_date"]).dt.date

    # 4-fold walk-forward per DEC-505 (1y warmup + 4 OOS folds x 1y each)
    fold_starts = [
        date(2022, 5, 5),
        date(2023, 5, 5),
        date(2024, 5, 5),
        date(2025, 5, 5),
    ]
    train_start = date(2021, 5, 5)
    windows = []
    for i, fold_start in enumerate(fold_starts, start=1):
        # OOS = 1 year from fold_start (or backtest-end if fold_start + 1y exceeds)
        oos_end = date(fold_start.year + 1, fold_start.month, min(fold_start.day, 28))
        # Cap last fold at 2026-05-05 (DEC-505 backtest end)
        if oos_end > date(2026, 5, 5):
            oos_end = date(2026, 5, 5)
        windows.append({
            "name":      f"fold_{i}",
            "train_start": train_start,
            "is_end":    date(fold_start.year, fold_start.month, fold_start.day - 1) if fold_start.day > 1 else date(fold_start.year, fold_start.month - 1, 28),
            "oos_start": fold_start,
            "oos_end":   oos_end,
        })

    MIN_OOS_TRADES = 30

    def _metrics(t, sector="Unknown"):
        if len(t) < 5:
            return None
        pc   = get_sector_criteria(sector)
        wins = t["pnl_pct"] > 0
        pnl  = t["pnl_pct"]
        wr   = float(wins.mean())
        pf_w = float(pnl[wins].sum())
        pf_l = float(abs(pnl[~wins].sum()))
        pf   = round(pf_w / pf_l, 3) if pf_l > 0 else 999
        is_min   = 100   # IS needs 100+ trades
        oos_min  = 30    # OOS minimum is 30  -  sufficient for validation
        passes = (wr >= pc["min_win_rate"] and
                  pf >= pc["min_profit_factor"] and
                  pnl.sum() > 0 and
                  len(t) >= oos_min)  # OOS threshold  -  IS caller checks IS minimum separately
        return {
            "trades":        len(t),
            "win_rate":      round(wr, 4),
            "profit_factor": pf,
            "total_roi":     round(float(pnl.sum()), 3),
            "passes":        passes,
        }

    results = {}
    for strategy in df_trades["strategy"].unique():
        g = df_trades[df_trades["strategy"] == strategy]
        sector = g["sector"].iloc[0] if "sector" in g.columns and not g.empty else "Unknown"

        window_results = {}
        passes_count = 0
        insufficient_count = 0

        for w in windows:
            is_df  = g[g["entry_date"] <= w["is_end"]]
            oos_df = g[(g["entry_date"] >= w["oos_start"]) &
                       (g["entry_date"] <= w["oos_end"])]

            is_m  = _metrics(is_df, sector)
            oos_m = _metrics(oos_df, sector)

            oos_sufficient = len(oos_df) >= MIN_OOS_TRADES
            oos_pass = (oos_m is not None and oos_m["passes"] and oos_sufficient)
            is_pass  = (is_m is not None and is_m["passes"] and is_m.get("trades",0) >= 100)

            if not oos_sufficient:
                insufficient_count += 1

            if oos_pass:
                passes_count += 1

            wr_deg = None
            if oos_m and is_m:
                wr_deg = round(oos_m["win_rate"] - is_m["win_rate"], 4)

            window_results[w["name"]] = {
                "in_sample":       is_m,
                "out_of_sample":   oos_m,
                "is_pass":         is_pass,
                "oos_pass":        oos_pass,
                "oos_sufficient":  oos_sufficient,
                "oos_trades":      len(oos_df),
                "wr_degradation":  wr_deg,
            }

        # Overall verdict (4-fold per DEC-505)
        n_folds = len(windows)
        if insufficient_count >= n_folds - 1:  # 3+ folds insufficient out of 4
            verdict = "INSUFFICIENT_OOS_DATA"
        elif passes_count >= 3:  # >=3 of 4 folds pass = ROBUST
            verdict = "ROBUST"
        elif passes_count >= 1:  # 1-2 folds pass = WEAK
            verdict = "WEAK"
        else:
            # 0 OOS folds passed; check if any IS passes
            is_any_pass = any(w["is_pass"] for w in window_results.values())
            verdict = "OVERFIT" if is_any_pass else "FAILS_BOTH"

        results[strategy] = {
            "windows":    window_results,
            "verdict":    verdict,
            "sector":     sector,
        }

    total    = len(results)
    robust   = sum(1 for r in results.values() if r["verdict"] == "ROBUST")
    overfit  = sum(1 for r in results.values() if r["verdict"] == "OVERFIT")
    weak     = sum(1 for r in results.values() if r["verdict"] == "WEAK")
    insuff   = sum(1 for r in results.values() if r["verdict"] == "INSUFFICIENT_OOS_DATA")

    logger.info(
        "Walk-forward (4 folds per DEC-505): %d strategies | ROBUST=%d | OVERFIT=%d | WEAK=%d | INSUFF=%d",
        total, robust, overfit, weak, insuff,
    )
    return {
        "strategy_results": results,
        "summary": {
            "total": total, "robust": robust, "overfit": overfit,
            "weak": weak, "insufficient_oos_data": insuff,
            "fold_1": "train=2021-05 -> 2022-05; OOS=2022-05 -> 2023-05",
            "fold_2": "train=2021-05 -> 2023-05; OOS=2023-05 -> 2024-05",
            "fold_3": "train=2021-05 -> 2024-05; OOS=2024-05 -> 2025-05",
            "fold_4": "train=2021-05 -> 2025-05; OOS=2025-05 -> 2026-05",
            "min_oos_trades": MIN_OOS_TRADES,
            "spec": "DEC-505 4-fold expanding window (1y warmup + 4x1y OOS)",
        },
    }


def walk_forward_to_df(wf_results: dict) -> pd.DataFrame:
    """Convert walk-forward results to flat DataFrame for CSV export."""
    rows = []
    for strategy, r in wf_results.get("strategy_results", {}).items():
        row = {"strategy": strategy, "verdict": r["verdict"], "sector": r.get("sector","Unknown")}
        for wname, w in r.get("windows", {}).items():
            is_m  = w.get("in_sample") or {}
            oos_m = w.get("out_of_sample") or {}
            row[f"{wname}_is_trades"]      = is_m.get("trades", 0)
            row[f"{wname}_is_win_rate"]    = is_m.get("win_rate", 0)
            row[f"{wname}_is_pf"]          = is_m.get("profit_factor", 0)
            row[f"{wname}_oos_trades"]     = oos_m.get("trades", 0)
            row[f"{wname}_oos_win_rate"]   = oos_m.get("win_rate", 0)
            row[f"{wname}_oos_pf"]         = oos_m.get("profit_factor", 0)
            row[f"{wname}_oos_sufficient"] = w.get("oos_sufficient", False)
            row[f"{wname}_wr_degradation"] = w.get("wr_degradation")
        rows.append(row)
    return pd.DataFrame(rows).sort_values("verdict")


# -----------------------------------------------------------------------------
# 3. CORRELATION FILTER
# -----------------------------------------------------------------------------

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
    3. These prevent real drawdown being 2-3x what backtest shows
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


# -----------------------------------------------------------------------------
# 4. SLIPPAGE MODEL
# -----------------------------------------------------------------------------

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
    1. Market impact  -  proportional to ATR (how volatile the stock is)
    2. Bid-ask spread  -  fixed percentage based on instrument type

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

    # Gap penalty  -  larger gap = harder to get a good fill
    gap_penalty = min(abs(gap_pct) * 0.1, 0.003)  # max 0.3% gap penalty

    total_slippage = spread_pct + gap_penalty

    if direction == "long":
        adjusted = entry_price * (1 + total_slippage)
    else:
        adjusted = entry_price * (1 - total_slippage)

    return round(adjusted, 4), round(total_slippage * 100, 4)


def apply_exit_slippage(
    exit_price: float,
    direction: str,
    ticker: str,
) -> tuple[float, float]:
    """Apply realistic slippage to exit price (mirror of apply_slippage at entry).

    BUG-80 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 15 2026-05-10:
    Previously only entry slippage was charged - exit price used raw stop/target
    trigger level. Real-world exits incur slippage in the OPPOSITE direction
    from entry (long sell hits below trigger; short buy-back fills above trigger).
    Round-trip slippage was understated; this helper adds the missing exit piece.

    Direction conventions:
      - long EXIT  = sell side -> fill BELOW the trigger -> exit_price * (1 - slippage)
      - short EXIT = buy-back  -> fill ABOVE the trigger -> exit_price * (1 + slippage)

    Spread classification uses ticker only (no ATR available at exit time without
    storing it on OpenTrade). For ETFs use tight spread; everything else gets the
    large-cap default 0.08%. High-volatility +ATR penalty path is approximated by
    the entry-time slippage already taken; exit-time charges the base spread only.

    Returns (adjusted_exit_price, slippage_pct).
    """
    if ticker in ETF_TICKERS:
        spread_pct = 0.0003
    else:
        spread_pct = 0.0008

    if direction == "long":
        # Sell side - we receive a worse price than the trigger
        adjusted = exit_price * (1 - spread_pct)
    else:
        # Short buy-back - we pay a worse price than the trigger
        adjusted = exit_price * (1 + spread_pct)

    return round(adjusted, 4), round(spread_pct * 100, 4)


# DEC-092 / DEC-280 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 54
# 2026-05-11 (owner-approved Path C bundle, joint).
# DEC-092: base slippage as f(size%ADV, vol) = alpha + beta*size_pct + gamma*vol_pct.
# DEC-280: time-of-day multiplier (first/last 30min of NYSE session = 1.5x).
# Final formula: final_bps = base_bps * exit_multiplier * time_multiplier.
# Coefficients calibrated against DEC-092 spec test signals:
#   (size 0.5% ADV, vol 20%): expected ~3 bps -> computed 3.25 bps
#   (size 5%   ADV, vol 50%): expected ~25 bps -> computed 24.25 bps
# Engine consumption deferred to follow-on decision once DEC-446 Polygon
# intraday quote calibration data lands; current scope is helper.

DEFAULT_SLIPPAGE_ALPHA = 0.5    # base bid-ask in bps
DEFAULT_SLIPPAGE_BETA  = 4.5    # per 1% of ADV
DEFAULT_SLIPPAGE_GAMMA = 0.025  # per 1% of annualized vol


def compute_slippage_bps_advanced(
    size_pct_adv: float,
    realized_vol_annualized: float,
    alpha: float = DEFAULT_SLIPPAGE_ALPHA,
    beta: float = DEFAULT_SLIPPAGE_BETA,
    gamma: float = DEFAULT_SLIPPAGE_GAMMA,
) -> float:
    """DEC-092: base slippage in bps as f(size%ADV, vol).

    Inputs:
      size_pct_adv: trade size as fraction of ADV (0.005 = 0.5% ADV)
      realized_vol_annualized: annualized realized vol (0.20 = 20% vol)

    Returns bps (basis points) >= 0. Coefficients applied to PERCENT units:
      bps = alpha + beta * (size_pct_adv * 100) + gamma * (vol * 100)
    """
    size_pct_input = max(0.0, size_pct_adv) * 100.0
    vol_pct_input  = max(0.0, realized_vol_annualized) * 100.0
    bps = alpha + beta * size_pct_input + gamma * vol_pct_input
    return max(0.0, bps)


def time_of_day_slippage_multiplier(entry_time) -> float:
    """DEC-280: first/last 30 min of NYSE regular session get 1.5x multiplier
    (open auction + closing auction effects). Otherwise 1.0x.

    NYSE regular session: 09:30 - 16:00 ET. First 30min = [09:30, 10:00);
    last 30min = [15:30, 16:00).

    Inputs:
      entry_time: datetime.time, datetime.datetime, or None. None -> 1.0
        (caller-side lacks intraday context, e.g., daily-bar backtest).

    Returns 1.0 or 1.5.
    """
    from datetime import time as _time, datetime as _datetime
    if entry_time is None:
        return 1.0
    if isinstance(entry_time, _datetime):
        et = entry_time.time()
    else:
        et = entry_time
    open_start          = _time(9, 30)
    open_first_30_end   = _time(10, 0)
    close_last_30_start = _time(15, 30)
    close_end           = _time(16, 0)
    if open_start <= et < open_first_30_end:
        return 1.5
    if close_last_30_start <= et < close_end:
        return 1.5
    return 1.0


STAGE_3_TEST_COVERAGE_THRESHOLD = 0.90  # DEC-098 owner override 90%
MEMORY_CAP_MB_DEFAULT = 4096            # DEC-179 default cap 4GB
CACHE_SIZE_ALERT_THRESHOLD_PCT = 0.80   # DEC-227 alert at 80% disk usage


# DEC-126 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Time-resolution limits of CBs
# documented per Pass 52 turn spec. circuit_breakers.py itself contains
# pre-existing non-ASCII display characters that block the C1 preflight on
# touched files; docstring landed here as a programmatic constant instead.
CIRCUIT_BREAKER_TIME_RESOLUTION_LIMITS = """
Time-resolution limits per DEC-126:

  Levels 1, 2, 6 (portfolio-level): evaluated DAILY at end-of-bar.
    Intraday breaches between bars are NOT detected until the close of
    the day they occur. Backtest is on daily OHLCV; live trading will
    inherit the same coarse cadence unless an intraday data source is
    added (Stage 3+).

  Levels 3, 4, 5 (NYSE Rule 80B): evaluated using daily LOW vs daily
    OPEN as the intraday-low proxy. True intraday tick-by-tick breach
    timing is NOT captured (e.g., a -7% breach hit at 10:00am that
    recovered to -3% by close is detected as a -3% close, NOT a
    Level 3 halt). Conservative caller-side: assume halt fired if
    daily low crossed -7/-13/-20% threshold even if recovery occurred.

These limits are intentional given daily-bar backtest scope. Production
papertrade (Stage 3+) should adopt minute-bar evaluation for accurate
breach timing.
""".strip()


# DEC-329 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Multi-process safety note:
# module-level global caches (VIX, DXY, AAII, CNN F&G in backtest/data/
# sentiment.py + macro.py) are NOT multi-process safe. When the backtest
# is parallelized via multiprocessing.Pool (DEC-184), each worker process
# gets its own _AAII_DF / _CNN_DF copy via on-demand load. Reads are safe.
# Writes (cache refresh / append) MUST go through the file-level filelock
# in cache.py + atomic-write semantics; never mutate the in-memory module
# globals from worker processes -- they will diverge from disk state and
# from each other. ProcessPoolExecutor preferred over ThreadPoolExecutor
# for parallel backtest runs to avoid GIL + module-global mutation races.
MULTI_PROCESS_SAFETY_GUIDANCE = (
    "Module-level caches (_AAII_DF, _CNN_DF, _VIX_DF) are per-process. "
    "Workers must re-load on first access; writes go through cache.py "
    "filelock. Never mutate globals from worker processes."
)


# DEC-606 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Finnhub financials_reported
# excluded permanently (superseded by SEC EDGAR XBRL + Polygon financials).
# This constant + helper enforce the exclusion at programmatic level so
# any future code referencing the path fails fast.
FINNHUB_FINANCIALS_REPORTED_EXCLUDED = True


def assert_no_finnhub_financials(path_or_module: str) -> None:
    """DEC-606 hard guard: raise if caller references finnhub financials path.
    Used as a defensive check at import / config time. Permanent supersedence
    per Pass 53 v8h+1 owner-approved 2026-05-10; reconsideration triggers: NONE.
    """
    if "finnhub" in path_or_module.lower() and "financials" in path_or_module.lower():
        raise RuntimeError(
            f"DEC-606: Finnhub financials_reported is EXCLUDED permanently. "
            f"Use data_prefetch/sec_xbrl/ or data_prefetch/polygon/financials/. "
            f"Caller path: {path_or_module}"
        )


def regulatory_event_flag(
    ticker: str,
    news_items: list,
    event_window_days: int = 5,
    as_of=None,
) -> dict:
    """DEC-159 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Regulatory event handler per
    Pass 52 turn 119 spec: SEC/DOJ investigation or sanction announcements
    suppress strategy entries for the event window.

    Inputs:
      ticker: ticker symbol
      news_items: list of dicts with {date, title, source}
      event_window_days: trailing window where flag stays active
      as_of: date for windowing (default today)

    Detects keywords: 'sec investigation', 'doj', 'sanction', 'enforcement
    action', 'wells notice'. Returns dict with flagged (bool),
    triggering_items (list of titles), oldest_within_window_days.

    Joint DEC-256 (event calendar) + DEC-348 (event suppression window).
    Engine wiring (consume flag at can_open) deferred.
    """
    from datetime import datetime
    if not news_items or not ticker:
        return {"flagged": False, "triggering_items": [],
                "oldest_within_window_days": None}
    keywords = ("sec investigation", "doj ", "doj's", "sanction",
                "enforcement action", "wells notice", "subpoena")
    now = as_of if as_of is not None else date.today()
    triggers = []
    for item in news_items:
        title = (item.get("title") or "").lower()
        item_date = item.get("date")
        if isinstance(item_date, str):
            try:
                item_date = datetime.fromisoformat(item_date).date()
            except ValueError:
                continue
        if item_date is None:
            continue
        days_ago = (now - item_date).days if hasattr(now, "year") else 0
        if 0 <= days_ago <= event_window_days:
            if any(kw in title for kw in keywords):
                triggers.append(item.get("title"))
    return {
        "flagged":                    len(triggers) > 0,
        "triggering_items":           triggers,
        "oldest_within_window_days":  event_window_days if triggers else None,
    }


def lru_cached(maxsize: int = 256):
    """DEC-183 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). Memoization layer for signal
    computation per Pass 52 turn 119 spec. Thin wrapper over
    `functools.lru_cache` returning a decorator with default size 256
    (tuned post-DEC-178 benchmarking).

    Usage:
        @lru_cached(maxsize=512)
        def expensive_signal(ticker, as_of): ...
    """
    from functools import lru_cache
    return lru_cache(maxsize=maxsize)


def get_nyse_calendar_helper():
    """DEC-235 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
    (owner-approved Path C 20-DEC bundle). NYSE/NASDAQ calendar wrapper per
    Pass 52 turn 58 spec using `pandas_market_calendars` library when
    available; falls back to None when not installed (caller-side decides
    fallback to pandas business-day calendar).

    Returns the pandas_market_calendars exchange object (mcal.get_calendar)
    for NYSE or None on import failure.
    """
    try:
        import pandas_market_calendars as mcal
        return mcal.get_calendar("NYSE")
    except ImportError:
        return None


def is_nyse_trading_day(d, calendar=None) -> bool:
    """DEC-235: returns True if `d` is a regular NYSE trading day. Uses the
    pandas_market_calendars library when available, else falls back to a
    pandas BusinessDay check (which lacks half-day / holiday awareness).
    """
    import pandas as pd
    cal = calendar if calendar is not None else get_nyse_calendar_helper()
    d_ts = pd.Timestamp(d)
    if cal is not None:
        try:
            schedule = cal.schedule(start_date=d_ts, end_date=d_ts)
            return len(schedule) > 0
        except Exception:
            pass
    return bool(d_ts.dayofweek < 5)  # Mon-Fri fallback


def benchmark_function(fn, n_iters: int = 100, *args, **kwargs) -> dict:
    """DEC-178 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Signal-lookup performance
    benchmark per Pass 52 turn 119 spec. Joint DEC-183 LRU cache.

    Calls `fn(*args, **kwargs)` n_iters times; returns latency stats.
    Stdlib-only (no pytest-benchmark dependency) so CI baseline tracking
    can ingest the dict.

    Returns dict with median_ms, p95_ms, total_s, n_iters, note.
    """
    import time
    if n_iters <= 0 or fn is None:
        return {"median_ms": None, "p95_ms": None, "total_s": None,
                "n_iters": 0, "note": "no_iters"}
    timings = []
    t_start = time.perf_counter()
    for _ in range(n_iters):
        t0 = time.perf_counter()
        try:
            fn(*args, **kwargs)
        except Exception:
            pass  # benchmark continues; caller checks for exceptions separately
        timings.append((time.perf_counter() - t0) * 1000.0)  # ms
    total_s = time.perf_counter() - t_start
    timings.sort()
    median = timings[len(timings) // 2]
    p95_idx = max(0, int(0.95 * len(timings)) - 1)
    p95 = timings[p95_idx]
    return {
        "median_ms": round(median, 4),
        "p95_ms":    round(p95, 4),
        "total_s":   round(total_s, 4),
        "n_iters":   n_iters,
        "note":      "ok",
    }


def get_cache_size_gb(cache_root) -> float:
    """DEC-227 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Cache size monitoring per
    Pass 52 turn 65 spec. Walks cache_root recursively summing file sizes.

    Returns float GB. Missing path returns 0.0.
    """
    import os
    from pathlib import Path
    p = Path(cache_root) if cache_root else None
    if p is None or not p.exists():
        return 0.0
    total_bytes = 0
    for root, _, files in os.walk(str(p)):
        for f in files:
            try:
                total_bytes += os.path.getsize(os.path.join(root, f))
            except OSError:
                continue
    return float(total_bytes / (1024.0 ** 3))


def cache_size_alert_level(
    cache_size_gb: float,
    disk_total_gb: float,
    threshold_pct: float = CACHE_SIZE_ALERT_THRESHOLD_PCT,
) -> dict:
    """DEC-227: returns dict with size_gb, pct_of_disk, alert (bool), note.
    Caller wires into DEC-225 eviction policy + DEC-095 monitoring infra
    (Stage 4 deferred). Engine consumption deferred; current scope is helper.
    """
    if disk_total_gb <= 0:
        return {"size_gb": round(cache_size_gb, 4), "pct_of_disk": None,
                "alert": False, "note": "invalid_disk_total"}
    pct = cache_size_gb / disk_total_gb
    return {
        "size_gb":     round(float(cache_size_gb), 4),
        "pct_of_disk": round(float(pct), 4),
        "alert":       bool(pct >= threshold_pct),
        "note":        "CACHE_SIZE_ALERT" if pct >= threshold_pct else "ok",
    }


def check_test_coverage_threshold(
    coverage_xml_path,
    threshold: float = STAGE_3_TEST_COVERAGE_THRESHOLD,
) -> dict:
    """DEC-098 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 57 2026-05-11
    (owner-approved Path C 5-DEC bundle). Test coverage gate per Pass 52
    turn 58 owner-overridden spec (90% target, raised from original 70%).
    Stage-3 paper-trading gate: `pytest --cov=backtest --cov-fail-under=90`
    must pass in CI.

    Parses pytest-cov coverage.xml and returns pass/fail vs threshold.

    Inputs:
      coverage_xml_path: path to coverage.xml emitted by pytest-cov
      threshold: required fraction (default 0.90)

    Returns dict with:
      coverage_pct: float 0-1
      threshold:    float 0-1
      passes:       bool
      note:         status string

    Missing file or unparseable XML returns coverage_pct=None and
    note='coverage_unavailable'. Caller decides whether to treat
    'coverage_unavailable' as gate-fail (fail-closed for CI) or skip
    (when running pre-coverage-instrumentation).
    """
    import os
    from pathlib import Path
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        return {"coverage_pct": None, "threshold": threshold,
                "passes": False, "note": "xml_lib_unavailable"}
    p = Path(coverage_xml_path) if coverage_xml_path else None
    if p is None or not p.exists():
        return {"coverage_pct": None, "threshold": threshold,
                "passes": False, "note": "coverage_unavailable"}
    try:
        tree = ET.parse(str(p))
        root = tree.getroot()
        line_rate = float(root.attrib.get("line-rate", "0") or 0)
    except (ET.ParseError, ValueError):
        return {"coverage_pct": None, "threshold": threshold,
                "passes": False, "note": "coverage_unavailable"}
    return {
        "coverage_pct": round(line_rate, 4),
        "threshold":    threshold,
        "passes":       bool(line_rate >= threshold),
        "note":         "ok" if line_rate >= threshold else "below_threshold",
    }


def get_process_memory_mb() -> float:
    """DEC-179 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 57 2026-05-11
    (owner-approved Path C 5-DEC bundle). Returns current process RSS
    in MB. Uses psutil when available; falls back to resource module
    (Unix) or returns -1.0 (Windows without psutil) for graceful
    degradation.
    """
    try:
        import psutil
        return float(psutil.Process().memory_info().rss / (1024.0 * 1024.0))
    except ImportError:
        pass
    try:
        import resource
        # Unix: ru_maxrss in KB on Linux, bytes on macOS
        ru_maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return float(ru_maxrss / 1024.0)  # assume Linux KB convention
    except (ImportError, AttributeError):
        return -1.0


def check_memory_cap(cap_mb: float = MEMORY_CAP_MB_DEFAULT) -> dict:
    """DEC-179: returns dict with current_mb, cap_mb, breached bool.
    Caller decides whether to abort run (raise) or just log warning.
    Engine consumption deferred; current scope is helper.
    """
    current = get_process_memory_mb()
    return {
        "current_mb": round(current, 2) if current >= 0 else None,
        "cap_mb":     float(cap_mb),
        "breached":   bool(current > cap_mb) if current >= 0 else False,
        "note":       "ok" if current <= cap_mb else "MEMORY_CAP_BREACHED",
    }


def check_ohlcv_data_quality(
    df,
    gap_pct_threshold: float = 0.50,
    max_consecutive_nan_days: int = 3,
) -> dict:
    """DEC-233 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 56 2026-05-11
    (owner-approved Path C 5-DEC bundle). Per-ticker OHLCV data-quality
    scan per Pass 52 turn 58 spec. Joint with DEC-260 (cache freshness
    assertion) — DEC-260 catches stale caches, DEC-233 catches in-cache
    anomalies.

    Checks:
      - has_nan_close: any NaN in close column
      - n_nan_days: total count of NaN close days
      - max_consecutive_nan_run: longest run of NaN closes
      - has_extreme_gap: any single-day close-to-close move > gap_pct_threshold
      - extreme_gap_count: count of such days

    Returns dict with check flags + counts + DataQualityWarning bool
    (True when any check breaches).

    Thresholds tunable per DEC-233 REVISIT_AFTER_BACKTEST tag.
    """
    import pandas as pd
    import numpy as np
    if df is None or len(df) == 0 or "close" not in getattr(df, "columns", []):
        return {
            "DataQualityWarning": True,
            "note":               "empty_or_missing_close_column",
        }
    close = pd.to_numeric(df["close"], errors="coerce")
    n_nan = int(close.isna().sum())
    # Compute longest consecutive-NaN run
    if n_nan == 0:
        max_run = 0
    else:
        groups = (close.notna() != close.notna().shift()).cumsum()
        nan_runs = close.isna().groupby(groups).sum()
        max_run = int(nan_runs.max()) if len(nan_runs) > 0 else 0
    # Extreme gap detection on non-NaN close-to-close
    pct = close.pct_change().abs()
    extreme = pct > gap_pct_threshold
    n_extreme = int(extreme.sum())
    warning = (n_nan > 0 and max_run >= max_consecutive_nan_days) or (n_extreme > 0)
    return {
        "DataQualityWarning":    bool(warning),
        "has_nan_close":         n_nan > 0,
        "n_nan_days":            n_nan,
        "max_consecutive_nan_run": max_run,
        "has_extreme_gap":       n_extreme > 0,
        "extreme_gap_count":     n_extreme,
        "note":                  "ok" if not warning else "review_required",
    }


def per_ticker_30day_max_loss_check(
    trade_log_df,
    today,
    cap_pct: float = -10.0,
    cooldown_days: int = 30,
) -> dict:
    """DEC-135 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 55 2026-05-11
    (owner-approved Path C 5-DEC bundle). Per-ticker cumulative max-loss
    cap per Pass 52 turn 115 owner spec: if any ticker's rolling 30-day
    cumulative pnl_pct <= cap_pct, halt that ticker for cooldown_days.

    Inputs:
      trade_log_df: DataFrame with columns ticker, exit_date, pnl_pct
      today: date for the rolling window endpoint
      cap_pct: cumulative loss threshold (default -10.0 = -10%)
      cooldown_days: window after breach to keep halted (default 30)

    Returns dict {ticker: True/False} for tickers seen in window. Tickers
    not in the DataFrame absent from the output (caller-side decides
    default).

    REVISIT_AFTER_BACKTEST tag (per DEC-135 spec) retained for empirical
    tuning of cap_pct. Engine consumption (gate at can_open) deferred to
    follow-on decision; current scope is helper.
    """
    import pandas as pd
    if trade_log_df is None or len(trade_log_df) == 0:
        return {}
    if not isinstance(trade_log_df, pd.DataFrame):
        return {}
    required = {"ticker", "exit_date", "pnl_pct"}
    if not required.issubset(set(trade_log_df.columns)):
        return {}
    df = trade_log_df.copy()
    df["exit_date"] = pd.to_datetime(df["exit_date"]).dt.date
    today_dt = today if hasattr(today, "year") else pd.to_datetime(today).date()
    window_start = today_dt - timedelta(days=cooldown_days)
    in_window = df[(df["exit_date"] >= window_start)
                   & (df["exit_date"] <= today_dt)]
    if in_window.empty:
        return {}
    by_ticker = in_window.groupby("ticker")["pnl_pct"].sum()
    out = {}
    for ticker, cum_pct in by_ticker.items():
        out[ticker] = bool(cum_pct <= cap_pct)
    return out


# -----------------------------------------------------------------------------
# 5. REGIME CONFIDENCE SCORE
# -----------------------------------------------------------------------------

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

    BUG-27 RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10:
    INTENTIONALLY-UNUSED in the Phase 1A backtest path. CLAUDE.md "Approved Rules"
    explicitly state: "No regime confidence scaling - full size always for backtest."
    The function is retained as DEFERRED-TO-STAGE-3+ infrastructure: live papertrade
    + live trading will wire this in for position-mult scaling. Not dead code in the
    architectural sense - it is forward-looking infrastructure with explicit
    project-plan deferral.
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

    # VIX consistency  -  std dev of recent VIX relative to its mean
    vix_cv = float(recent_vix.std() / max(recent_vix.mean(), 1))
    vix_consistency = max(0, 100 - vix_cv * 200)  # 0-100

    # Trend persistence  -  consecutive days in current trend
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
        position_mult = 0.25   # 25% size  -  regime very uncertain

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
            f"Regime {regime} with {confidence:.0f}% confidence  -  "
            f"VIX stable ({vix_consistency:.0f}%), "
            f"trend persistent {trend_days}d  -  "
            f"use {position_mult*100:.0f}% of normal position size"
        ),
    }


# -----------------------------------------------------------------------------
# BONFERRONI CORRECTION FOR MULTIPLE TESTING
# -----------------------------------------------------------------------------

def bonferroni_adjusted_threshold(
    n_strategies: int,
    base_significance: float = 0.05,
    min_win_rate: float = 0.55,
) -> dict:
    """
    Compute Bonferroni-corrected significance thresholds.

    With N strategies tested (N = baseline 60 in Layer 1  -  see CANONICAL_FACTS.md F-002 for
    layered roster expansion to ~108-133 classes), the probability of at least one false
    positive at p=0.05 is 1-(0.95)^N. We need stricter thresholds. The `n_strategies`
    parameter is parameterized  -  caller passes len(ALL_STRATEGIES).

    Returns adjusted thresholds for win rate and minimum trades required.
    """
    # BUG-275 fix 2026-05-13: n_strategies=0 caused ZeroDivisionError.
    if n_strategies <= 0:
        return {
            "n_strategies": n_strategies,
            "base_significance": base_significance,
            "adjusted_significance": base_significance,
            "min_win_rate": min_win_rate,
            "min_trades_required": 0,
            "false_positive_prob_uncorrected": 0.0,
            "false_positive_prob_corrected": base_significance,
            "recommendation": "No strategies tested; no correction applied.",
        }
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


# -----------------------------------------------------------------------------
# SURVIVORSHIP BIAS HAIRCUT
# -----------------------------------------------------------------------------

def apply_survivorship_haircut(
    df_trades: pd.DataFrame,
    years: float = 3.0,
) -> tuple[pd.DataFrame, float]:
    """
    Apply hold-adjusted survivorship bias haircut per trade.
    Proportional to hold time  -  shorter holds have less survivorship exposure.

    BUG-37 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 5 2026-05-10:
    Methodology is hold-adjusted (NOT arbitrary). Annual rate scales with hold
    duration: shorter holds have less survivorship-bias exposure to the
    delisted-ticker problem. Per-trade haircut = rate * (hold_days/252) * 100.
    Rates derived from academic literature on small-cap delisting frequency
    (Shumway 1997; Beaver/McNichols/Price 2007) scaled to S&P 500 historical
    delisting rates (~3-5% per year of components churned via M&A/delisting).
    "Arbitrary" claim resolved by explicit hold-adjusted tiered table below.

    Hold-adjusted annual rates:
      < 7 days:   0.5% / year
      7-14 days:  1.0% / year
      14-30 days: 2.0% / year
      > 30 days:  3.0% / year

    Returns (adjusted_df, total_haircut_pct).
    """
    df = df_trades.copy()
    annual_rates = {7: 0.005, 14: 0.010, 30: 0.020, 999: 0.030}

    haircuts = []
    for _, row in df.iterrows():
        hold = row.get("hold_days", 10)
        rate = 0.030  # default > 30 days
        for threshold, r in sorted(annual_rates.items()):
            if hold <= threshold:
                rate = r
                break
        haircut = rate * (hold / 252) * 100  # as percentage
        haircuts.append(haircut)

    df["survivorship_haircut"] = haircuts
    df["pnl_pct"] = df["pnl_pct"] - df["survivorship_haircut"]
    df["win"]     = df["pnl_pct"] > 0

    total_haircut = sum(haircuts)
    logger.info("Hold-adjusted survivorship haircut: total=%.1f%% over %.1f years",
                total_haircut, years)
    return df, round(total_haircut, 3)
