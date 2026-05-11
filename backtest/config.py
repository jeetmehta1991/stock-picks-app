"""
config.py  -  Complete system configuration for Stage 2 backtesting engine v2.

Single source of truth for:
  - Universe definitions
  - Market regime windows
  - Entry zone ATR multipliers by strategy type
  - Trailing stop parameters
  - Circuit breaker thresholds
  - Passing criteria (all 10 metrics)
  - Confidence tier definitions
  - Site card parameters
  - Output file names
  - AI model selection
"""

from datetime import date

# -----------------------------------------------------------------------------
# BACKTEST WINDOW (Pass 53 owner directive 2026-05-05; DEC-505)
# Aligned to Polygon Stocks Starter 5y rolling cache (locked 2021-05-05 ->
# 2026-05-05). Owner declined Polygon Developer/Advanced upgrade. Walk-forward
# scheme: 1y warmup (DATA_LOAD_START -> BACKTEST_START) + 4 OOS folds x 1y each.
# Old window 2020-01-01 -> 2026-03-31 had a 16-month gap (2020-01 -> 2021-05) with
# no Polygon data  -  corrected per owner directive: "Remove backtest windows
# for these 16 months."
# -----------------------------------------------------------------------------
BACKTEST_START  = date(2022, 5, 5)   # First tradeable date (post 1y warmup)
BACKTEST_END    = date(2026, 5, 5)   # Polygon cache end
DATA_LOAD_START = date(2021, 5, 5)   # 1y warmup window for 252-day indicators
PHASE_1D_START  = date(2021, 5, 5)   # Pass 53: extended window aligned to cache start (was 2020-01-01)

# Walk-forward folds (DEC-505 supersedes DEC-109):
#   Fold 1 OOS: 2022-05-05 -> 2023-05-05
#   Fold 2 OOS: 2023-05-05 -> 2024-05-05
#   Fold 3 OOS: 2024-05-05 -> 2025-05-05
#   Fold 4 OOS: 2025-05-05 -> 2026-05-05
WALK_FORWARD_FOLDS = [
    (date(2022, 5, 5), date(2023, 5, 5)),
    (date(2023, 5, 5), date(2024, 5, 5)),
    (date(2024, 5, 5), date(2025, 5, 5)),
    (date(2025, 5, 5), date(2026, 5, 5)),
]

# -----------------------------------------------------------------------------
# UNIVERSE  -  Phase 1A (S&P 50 + 17 ETFs = 67 instruments)
# -----------------------------------------------------------------------------
SP50 = [
    # Mega-cap tech
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "ORCL", "AMD",
    # Financials
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "BLK", "SCHW",
    # Healthcare
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "PFE", "TMO", "ABT", "DHR", "ISRG",
    # Energy / Industrials
    "XOM", "CVX", "COP", "NEE", "CAT", "HON", "UPS", "RTX", "GE", "LMT",
    # Consumer / Other
    "WMT", "COST", "HD", "NKE", "SBUX", "MCD", "PG", "KO", "PEP", "DIS",
]

ETFS = [
    # Broad market
    "SPY", "QQQ", "IWM", "DIA", "VTI",
    # Sector
    "XLK", "XLF", "XLE", "XLV", "XLI",
    # Volatility (VXX only  -  no leveraged)
    "VXX",
    # Bonds
    "TLT", "HYG", "LQD",
    # Commodities
    "GLD", "SLV", "GDX",
]

UNIVERSE = SP50 + ETFS   # 67 instruments total

# No leveraged ETFs anywhere in the system  -  TQQQ, SQQQ, SPXL, UVXY, SOXL excluded.
# Reason: volatility decay makes backtested win rates non-transferable to live trading.

# -----------------------------------------------------------------------------
# MARKET REGIMES
# Each strategy is evaluated per-regime independently.
# A strategy passes if it meets criteria within at least one regime (min 30 trades).
# In live trading the screener activates only strategies validated for the current regime.
MIN_REGIME_TRADES = 30   # minimum trades per regime for a statistically valid verdict
# -----------------------------------------------------------------------------
MARKET_REGIMES = {
    "bear_correction_2022": {
        "start": date(2022, 1, 1), "end": date(2022, 12, 31),
        "description": "Bear market  -  S&P -19.4%",
        "bias": "short",
    },
    "rate_rising_2022_2023": {
        "start": date(2022, 3, 1), "end": date(2023, 7, 31),
        "description": "Fed rate cycle 0.25% -> 5.50%",
        "bias": "neutral",
    },
    "strong_bull_2023": {
        "start": date(2023, 1, 1), "end": date(2023, 12, 31),
        "description": "Bull recovery  -  S&P +24.2%",
        "bias": "long",
    },
    "rate_falling_2024": {
        "start": date(2024, 1, 1), "end": date(2024, 12, 31),
        "description": "Fed cutting cycle begins",
        "bias": "long",
    },
    "ai_sector_bull_2024": {
        "start": date(2024, 1, 1), "end": date(2024, 12, 31),
        "description": "AI / tech sector bull",
        "bias": "long",
    },
    "tariff_shock_2025": {
        "start": date(2025, 1, 1), "end": date(2025, 6, 30),
        "description": "Trump tariff uncertainty  -  VIX spikes, policy volatility",
        "bias": "neutral",
    },
    "ai_divergence_2025_2026": {
        "start": date(2025, 7, 1), "end": date(2026, 3, 31),
        "description": "AI sector divergence  -  NVDA +100% vs broad market flat",
        "bias": "long",
    },
    # Phase 1D only
    "covid_crisis_2020": {
        "start": date(2020, 2, 1), "end": date(2020, 6, 30),
        "description": "COVID crash  -  VIX peak 82",
        "bias": "short",
    },
}

# -----------------------------------------------------------------------------
# LIQUIDITY FILTERS  -  applied before all strategy screening
# -----------------------------------------------------------------------------
LIQUIDITY = {
    "min_price":        5.0,      # eliminates penny stocks
    "min_avg_volume":   500_000,  # 20-day average shares/day
    "min_listed_years": 1.0,      # must be listed at least 1 year
    "min_market_cap_m": 100,      # USD millions
}

# -----------------------------------------------------------------------------
# ENTRY ZONE  -  ATR multiplier by strategy category
# Upper bound = next day open + (multiplier x ATR)
# If open exceeds upper bound -> trade skipped, logged as entry_skipped_gap_exceeded
# -----------------------------------------------------------------------------
ENTRY_GAP_ATR_MULT = {
    "breakout":      2.0,   # gap-up confirms the breakout thesis
    "momentum":      2.0,   # momentum entries tolerate larger gaps
    "trend":         1.5,   # moderate gap tolerance
    "confluence":    1.5,   # high conviction  -  worth paying up slightly
    "pivot":         1.0,   # entry level matters  -  large gap invalidates level
    "candle":        1.0,   # pattern entry level matters
    "mean_reversion": 1.0,  # raised from 0.5x  -  backtest needs sufficient trades
}

# -----------------------------------------------------------------------------
# EXIT LOGIC  -  trailing stop system
# -----------------------------------------------------------------------------
TRAILING_STOP = {
    "initial_pct":       0.10,   # 10% below entry price (long) / above (short)
    "trail_pct":         0.10,   # trails at 10% below highest close (long)
    "reset_on":          "close", # trailing stop resets on closing price only
    "primary_exit":      "atr_trail_1x",  # Phase 1A results: atr_trail_1x wins 20/29 strategies
    # Stop only moves in favour of trade  -  never reverses
}

# -----------------------------------------------------------------------------
# CIRCUIT BREAKERS  -  checked before trailing stop, in priority order
# -----------------------------------------------------------------------------
CIRCUIT_BREAKERS = {
    "level_1_gap_pct":         0.12,  # overnight gap > 12% wrong direction -> exit at open
    "level_2_earnings_gap_pct": 0.08, # earnings gap > 8% wrong direction -> exit at open
    "level_3_halt_loss_pct":   0.15,  # intraday halt + down > 15% from entry -> exit on resume
    "level_4_market_halt_pct": 0.07,  # S&P 500 market-wide circuit breaker -> flag all, no new trades
    "level_5_vix_crisis":      40,    # VIX > 40 -> tighten stops to 5%, no new longs
    "level_5_tightened_pct":   0.05,  # tightened trailing stop when VIX > 40
}

# -----------------------------------------------------------------------------
# REGIME FILTER  -  Option B: VIX + SPY based
# Controls which directions are allowed in each regime
# -----------------------------------------------------------------------------
REGIME_FILTER = {
    "bull": {
        "vix_max": 20, "spy_above_200ema": True,
        "long": "full", "short": "reduced",
    },
    "neutral": {
        "vix_range": (20, 30), "spy_above_200ema": None,
        "long": "full", "short": "full",
    },
    "bear": {
        "vix_min": 30, "spy_above_200ema": False,
        "long": "reduced", "short": "full",
    },
    "crisis": {
        "vix_min": 40,
        "long": "reduced",   # 50% size  -  buy dips in crisis, don't block
        "short": "cautious",
    },
    # DEC-316 fix (Pass 51): unknown = no VIX data -> block all new entries.
    # Existing positions continue under their original stop logic; new entries
    # refuse until regime data returns. Fail-closed beats silently trading
    # on missing context.
    "unknown": {
        "long": "none", "short": "none",
        "description": "Missing VIX/regime data  -  block new entries",
    },
}

# Position size multipliers per regime
POSITION_SIZE_MULT = {
    "full":     1.0,   # normal position size
    "reduced":  0.5,   # 50%  -  bear/crisis regime
    "cautious": 0.25,  # 25%  -  cautious regime (crisis shorts)
    "none":     0.0,   # blocked  -  not used for crisis longs (buy-the-dip)
}

# -----------------------------------------------------------------------------
# SHORT-TO-LONG CONVERSION
# Only in bull market (VIX < 20, SPY above 200 EMA)
# Bear market: exit only, no conversion
# -----------------------------------------------------------------------------
CONVERSION = {
    "enabled_regimes": ["bull"],          # only convert in bull market
    "requires_long_signal": True,         # long signal must be firing at conversion point
    "flag_as_conversion_pair": True,      # both trades flagged in trade log
}

# -----------------------------------------------------------------------------
# PASSING CRITERIA  -  all 10 metrics, strategy must pass ALL to advance
# -----------------------------------------------------------------------------
PASSING_CRITERIA = {
    "min_win_rate":            0.55,   # 55%+ win rate
    "min_profit_factor":       1.2,    # total wins / total losses > 1.2
    "min_expected_value":      0.0,    # (win_rate x avg_win) + (loss_rate x avg_loss) > 0
    "min_win_loss_ratio":      1.0,    # avg win / avg loss > 1.0
    "max_drawdown":            20.0,   # max peak-to-trough cumulative loss < 20 pct points
    "min_total_roi":           0.0,    # positive total ROI over backtest period
    "smart_money_lift":        True,   # must show measurable improvement with smart money
    "macro_correlation":       True,   # must show higher win rate in favourable regime
    "min_trades":              100,    # minimum 100 trades for statistical validity
    # Audit flag: anything above these thresholds gets look-ahead bias audit
    # DEC-084 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 39 2026-05-11
    # (owner-approved Path C): lowered audit_win_rate_above 0.75 -> 0.65 per
    # DEC-084 spec (more aggressive flagging of suspicious win rates).
    "audit_win_rate_above":    0.65,
    "audit_profit_factor_above": 1.5,
}

# DEC-083 + DEC-406 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 39
# 2026-05-11 (owner-approved Path C): tiered min-trades enforcement per
# strategy frequency. Daily-freq strategies need 300+ trades for stat
# validity; earnings-event strategies trade ~4x/year so 60+ is sufficient;
# pivot/intraday-style strategies sit between at 150.
TIERED_MIN_TRADES = {
    "daily":          300,   # daily-freq strategies (RSI/MA/momentum/etc.)
    "intraday":       300,   # intraday signals (high freq)
    "pivot":          150,   # daily-pivot strategies
    "swing":          150,   # swing-trade timing
    "earnings_event": 60,    # earnings-event strategies (~4x/year)
    "calendar":       60,    # calendar/seasonal (event-driven)
    "default":        100,   # fallback for uncategorized strategies
}

# Sector-adjusted passing criteria  -  some sectors are inherently more volatile
# High volatility sectors get wider drawdown tolerance and lower win rate requirement
SECTOR_PASSING_CRITERIA = {
    "high_volatility": {
        "sectors": ["Energy", "Information Technology", "Health Care",
                    "Communication Services"],
        "min_win_rate":   0.50,   # lower  -  these sectors have wider swings
        "max_drawdown":   25.0,   # wider  -  drawdowns are larger in volatile sectors
        "min_profit_factor": 1.2,
    },
    "medium_volatility": {
        "sectors": ["Financials", "Industrials", "Consumer Discretionary",
                    "Materials", "Broad Market", "Small Cap"],
        "min_win_rate":   0.55,   # standard
        "max_drawdown":   20.0,   # standard
        "min_profit_factor": 1.3,
    },
    "low_volatility": {
        "sectors": ["Consumer Staples", "Utilities", "Real Estate",
                    "Fixed Income", "Commodities"],
        "min_win_rate":   0.58,   # higher  -  these sectors should be more predictable
        "max_drawdown":   15.0,   # tighter  -  large drawdowns are anomalous here
        "min_profit_factor": 1.4,
    },
}


def get_sector_criteria(sector: str) -> dict:
    """Return passing criteria adjusted for sector volatility profile."""
    for profile, config in SECTOR_PASSING_CRITERIA.items():
        if sector in config["sectors"]:
            criteria = dict(PASSING_CRITERIA)
            criteria["min_win_rate"]      = config["min_win_rate"]
            criteria["max_drawdown"]      = config["max_drawdown"]
            criteria["min_profit_factor"] = config["min_profit_factor"]
            criteria["_label"]            = profile
            return criteria
    result = dict(PASSING_CRITERIA)
    result["_label"] = "medium_volatility"
    return result

# -----------------------------------------------------------------------------
# CONFIDENCE TIERS  -  maps to site card label and position sizing
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# LIVE TRADING OVERRIDES
# These differ from backtest rules  -  applied only in Stage 3+ live trading
# -----------------------------------------------------------------------------

LIVE_TRADING_RULES = {
    "max_positions_per_ticker": 1,      # backtest: unlimited. live: 1 position per ticker max
    "max_open_positions":       10,     # total simultaneous positions
    "drawdown_25pct_threshold": 0.10,   # portfolio drawdown > 10% -> reduce sizes 25%
    "drawdown_50pct_threshold": 0.20,   # portfolio drawdown > 20% -> reduce sizes 50%
    "drawdown_suspend_threshold": 0.30, # portfolio drawdown > 30% -> suspend new entries
    "position_staleness_pct":   0.01,   # cancel if entry price moved >1% since signal
    "broker":                   "IBKR_Canada",  # Interactive Brokers Canada (not Alpaca  -  Canada only)
    "base_currency":            "CAD",  # portfolio denominated in CAD
    "trade_currency":           "USD",  # US equity trades in USD  -  currency risk exists
}

# BUG-95 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 20 2026-05-10
# (owner-approved Option A): portfolio-level simulation requires explicit
# starting capital. Backtest treats portfolio as CAD-denominated per
# LIVE_TRADING_RULES.base_currency; default $100,000 starting capital is
# a placeholder consistent with prior reference_capital_cad used by
# results.metrics.portfolio_return_metrics. Owner can override at
# Backtest(starting_capital=N) call site.
STARTING_CAPITAL = 100_000.0   # CAD; portfolio simulation base

# BUG-95 sub-batch 2: tier -> position-size percent. Mirrors the tier_sizes
# default in results.metrics.portfolio_return_metrics. Engine uses this to
# compute size_pct passed to Portfolio.add_position and Portfolio.can_open.
# AVOID tier maps to 0 (no position; gated upstream); LOW maps to 0 to skip.
TIER_POSITION_SIZE_PCT = {
    "EXCEPTIONAL": 0.05,
    "VERY_HIGH":   0.04,
    "HIGH":        0.03,
    "MEDIUM_HIGH": 0.015,
    "MEDIUM":      0.0075,
    "LOW":         0.0,
    "AVOID":       0.0,
}

# DEC-088 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 51 2026-05-11
# (owner-approved Path C). Portfolio annualized vol target = 15% midpoint
# for medium-high risk profile. Used by Portfolio.vol_target_scale_factor to
# recommend gross-sizing scale (engine consumption deferred to follow-on
# decision; current scope is telemetry + helper, not auto-scaling).
# Joint with DEC-087 (per-position vol-targeted contribution).
PORTFOLIO_VOL_TARGET_ANNUALIZED = 0.15
PORTFOLIO_VOL_LOOKBACK_DAYS = 21
PORTFOLIO_VOL_SCALE_MIN = 0.5
PORTFOLIO_VOL_SCALE_MAX = 1.5

# DEC-087 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 52 2026-05-11
# (owner-approved Path C). Vol-targeted per-position sizing closes DEC-023
# (SUPERSEDED_BY_DEC-087). Higher-vol positions get smaller allocations to
# equalize risk contribution: `size = base_size * (target_vol / position_vol)`,
# bounded by MIN/MAX multipliers to avoid extreme adjustments. Per-position
# target 20% annualized is a midpoint; portfolio-level constraint (DEC-088)
# applies on top. Multiplier bounds [0.25, 2.0] match the wider per-position
# vol distribution vs portfolio-level (DEC-088 [0.5, 1.5]).
VOL_TARGETED_TARGET_PER_POSITION_ANNUALIZED = 0.20
VOL_TARGETED_SIZE_MIN_MULTIPLIER = 0.25
VOL_TARGETED_SIZE_MAX_MULTIPLIER = 2.0

# DEC-021 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
# (owner-approved Path C 10-DEC bundle). 3-tier simplification per Pass 52
# turn 95: 5-tier system collapsed to HIGH (5%) / MEDIUM (3%) / LOW (1.5%)
# for owner-facing reporting + per-strategy verdict tagging. Original
# 5-tier TIER_POSITION_SIZE_PCT preserved for backward-compat (engine
# still consumes it); TIER_3_POSITION_SIZE_PCT is the simplified mapping
# for new reporting/dashboard surfaces. 4-tier 4% mapping -> MEDIUM.
TIER_3_POSITION_SIZE_PCT = {
    "HIGH":   0.05,
    "MEDIUM": 0.03,
    "LOW":    0.015,
}

TIER_5_TO_TIER_3 = {
    "EXCEPTIONAL": "HIGH",
    "VERY_HIGH":   "HIGH",
    "HIGH":        "MEDIUM",
    "MEDIUM_HIGH": "MEDIUM",
    "MEDIUM":      "LOW",
    "LOW":         "LOW",
    "AVOID":       "LOW",
}

# -----------------------------------------------------------------------------
# TWO-STAGE CONFIDENCE TIERING
# Stage 1: Rule-based preliminary tier (before agents run)
# Stage 2: Agent-adjusted final tier (agents can move +/-1 level based on quality)
# This prevents agents being gated by the same data they are evaluating.
# -----------------------------------------------------------------------------

# Agent score thresholds for tier adjustment
AGENT_TIER_UPGRADE_THRESHOLD   = 75   # agent final_score above this -> upgrade one tier
AGENT_TIER_DOWNGRADE_THRESHOLD = 40   # agent final_score below this -> downgrade one tier

CONFIDENCE_TIERS = {
    "EXCEPTIONAL": {
        "tech_strategies_min": 3,
        "smart_money": "congressional+insider_cluster",
        "site_label": "Exceptional",
        "position_pct": 0.05,       # 5% of capital
        "published": True,
        "section": "active_picks",
    },
    "VERY_HIGH": {
        "tech_strategies_min": 2,
        "smart_money": "congressional_or_insider",
        "site_label": "Very High",
        "position_pct": 0.04,       # 4% of capital
        "published": True,
        "section": "active_picks",
    },
    "HIGH": {
        "tech_strategies_min": 3,
        "smart_money": None,
        "site_label": "High",
        "position_pct": 0.03,       # 3% of capital
        "published": True,
        "section": "watchlist",
    },
    "MEDIUM_HIGH": {
        "tech_strategies_min": 2,
        "smart_money": None,
        "site_label": "Medium-High",
        "position_pct": 0.015,      # 1.5% of capital
        "published": True,
        "section": "watchlist",
    },
    "MEDIUM": {
        "tech_strategies_min": 1,
        "smart_money": "any_buy",
        "site_label": "Medium",
        "position_pct": 0.0,
        "published": False,
        "section": None,
    },
    "LOW": {
        "tech_strategies_min": 1,
        "smart_money": None,
        "site_label": "Low",
        "position_pct": 0.0,
        "published": False,
        "section": None,
    },
    "AVOID": {
        "smart_money": "congressional_sell+insider_cluster_sell",
        "site_label": "Avoid",
        "position_pct": 0.0,
        "published": False,
        "section": None,
    },
}

# -----------------------------------------------------------------------------
# SITE OUTPUT
# -----------------------------------------------------------------------------
SITE = {
    "max_active_picks":    10,    # top 10 per day total
    "active_picks_tiers":  ["EXCEPTIONAL", "VERY_HIGH"],
    "watchlist_tiers":     ["HIGH", "MEDIUM_HIGH"],
    "card_format":         "both",   # bullets + paragraph
}

# -----------------------------------------------------------------------------
# AI MODELS
# -----------------------------------------------------------------------------
AI_MODELS = {
    "phase_1a": "claude-haiku-4-5-20251001",
    "phase_1b": "claude-haiku-4-5-20251001",
    "phase_1c": "claude-sonnet-4-6",
    "phase_1d": "claude-sonnet-4-6",
    "live":     "claude-sonnet-4-6",
}

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# -----------------------------------------------------------------------------
# TECHNICAL INDICATOR PARAMETERS
# -----------------------------------------------------------------------------
INDICATORS = {
    "rsi_periods":       [9, 14, 21],
    "macd_params":       [(12, 26, 9), (8, 21, 5)],
    "ema_pairs":         [(9, 21), (20, 50), (50, 200)],
    "sma_pairs":         [(9, 21), (20, 50), (50, 200)],
    "bb_params":         [(20, 2.0), (20, 1.5), (10, 2.0)],
    "atr_period":        14,
    "adx_period":        14,
    "stoch_params":      (14, 3, 3),
    "williams_period":   14,
    "roc_period":        12,
    "mfi_period":        14,
    "cmf_period":        20,
    "hull_period":       20,
    "donchian_periods":  [10, 20],
    "fib_levels":        [0.236, 0.382, 0.500, 0.618, 0.786],
    "pivot_near_pct":    0.003,     # within 0.3% = "near" a pivot level
    "fib_near_pct":      0.005,     # within 0.5% = "near" a Fibonacci level
    "volume_spike_x":    [1.5, 2.0, 3.0],
    "yearly_high_bars":  252,       # ~1 trading year for 52-week high
}

# -----------------------------------------------------------------------------
# OUTPUT FILES
# -----------------------------------------------------------------------------
OUTPUT_DIR = "output"
OUTPUT_FILES = {
    "trade_log":               "trade_log.csv",
    "backtest_results":        "backtest_results.csv",
    "backtest_report":         "backtest_report.html",
    "winning_strategies":      "winning_strategies.json",
    "regime_performance":      "regime_performance.csv",
    "smart_money_combined":    "smart_money_combined.csv",
    "agent_performance":       "agent_performance.csv",
    "congressional_corr":      "congressional_correlation.csv",
    "insider_corr":            "insider_correlation.csv",
    "skipped_trades":          "skipped_trades.csv",
    "circuit_breaker_log":     "circuit_breaker_log.csv",
    "site_picks":              "site_picks_{date}.json",
}

# -----------------------------------------------------------------------------
# CRISIS LONG EXCLUSIONS  -  tickers blocked from long entries in crisis regime
# Data-confirmed: 0-17% win rates in crisis. Short entries still allowed.
# -----------------------------------------------------------------------------
CRISIS_LONG_EXCLUSIONS = {
    "VXX",   # Volatility ETF  -  buying volatility long in crisis is wrong-directional
    "TLT",   # Long-term Treasury ETF  -  falling in rate-hike crisis
    "EEM",   # Emerging Markets ETF  -  first to sell off in crisis
}

# -----------------------------------------------------------------------------
# SHORT BORROW COST  (DEC-295 fix, Pass 50)
# Annual borrow rate as a DECIMAL (0.005 = 0.5% per year), applied
# proportionally to hold period: borrow = SHORT_ANNUAL_BORROW_RATE * (hold_days / 252).
#
# IBKR Canada quotes ~0.25%-1% annual borrow for easy-to-borrow large caps.
# 0.5%/yr is a representative midpoint. Single source of truth  -  used by
# improvements.apply_transaction_costs ONLY. Do NOT also subtract in _pnl().
#
# Previous SHORT_BORROW_COST_PER_DAY (= 0.005 with comment "% per day") was
# ambiguous: same numeric value could mean 1.26%/yr (if percent-units) OR
# 126%/yr (if decimal-units). Renamed and clarified.
# -----------------------------------------------------------------------------
SHORT_ANNUAL_BORROW_RATE = 0.005   # decimal: 0.005 = 0.5% per year
