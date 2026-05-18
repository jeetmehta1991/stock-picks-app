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
    # BUG-232 RESOLVED-IMPLEMENTED Batch 113 2026-05-12 (owner-approved
    # option C 2026-05-12): config-toggleable trailing ratchet source.
    # "close" (default, conservative) = update_trailing_stop uses
    # today_close to advance the stop only when close > highest_close
    # (longs); less whipsaw, gives up some intraday gains. Set to
    # "intraday_extreme" to ratchet from today_high (longs) / today_low
    # (shorts) so favourable intraday excursions advance the stop
    # aggressively - locks gains faster but causes more whipsaw stops.
    # Default preserved as "close" pending Phase 1B-alpha empirical
    # A/B vs intraday_extreme to settle the design-choice tradeoff.
    "ratchet_from":      "close",
}

# BUG-258 fix 2026-05-13: ATR fallback when insufficient history (<14 bars).
# 2% of entry price per Wilder recommendation for stocks with <14 bars available.
# Named constant prevents silent magic-number use across exit_strategies.py.
ATR_FALLBACK_PCT: float = 0.02

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
    # BUG-30 RESOLVED-IMPLEMENTED Batch 114 2026-05-12 (owner-approved
    # option C 2026-05-12): config-toggleable Level-5 tighten. Resolves
    # the code-vs-spec contradiction (regime_filter.py:113 documents
    # crisis as "Do NOT tighten stops (causes whipsawing)" but
    # exit_manager.py Level-5 path DOES tighten when vix >=
    # level_5_vix_crisis). Default True preserves current behavior
    # (Level-5 tightening active) - flash-crash protection rail stays
    # ON. Setting to False removes the tightening so DEC-091 DD-band
    # sizing + DEC-088 vol-target are the only crisis-mode exposure
    # reductions; lets Phase 1B-alpha empirically test whether the
    # whipsaw cost outweighs the protection benefit.
    "level_5_tighten_in_crisis": True,
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
    # Batch 186 owner-approved 2026-05-16 (industry-research-driven relaxations):
    #   (A) min_win_rate 0.55 -> 0.45 per-regime baseline; HV sectors 0.50 -> 0.40.
    #       Rationale: mean-reversion strategies (our system's stylistic bias) run
    #       30-50% WR per Lux Algo / HorizonAI / Quantified Strategies 2025-2026.
    #       Compensated by R:R >= 2.0 (DEC-426) which gives positive EV at 33%+ WR.
    #   (B) min_profit_factor_overall 1.5 -> 1.3 to match per-regime threshold.
    #       Rationale: PF 1.3 = "marginal but profitable" per industry; PF 1.5 was
    #       above industry "good" band (>1.75). Mitigated by PSR/DSR gates below.
    #   (C) max_drawdown 20.0 -> 25.0 (HV: 25.0 -> 30.0).
    #       Rationale: industry institutional ~20% backtest * 1.5x live degradation
    #       = ~30% real-world DD; 25pp backtest accommodates this. See Lux Algo
    #       2025 backtest-to-live degradation note.
    #   (D) smart_money_lift / macro_correlation -> False default; per-strategy
    #       opt-in via uses_smart_money_signal / uses_macro_signal attributes.
    #       Rationale: most strategies aren't designed for smart-money/macro
    #       exploitation; requiring lift for technical/mean-rev strategies that
    #       don't reference those signals is unfair. Strategies tagged as
    #       smart-money or macro-driven still face the lift gates via metrics.py.
    #   (E) NEW gate: min_deflated_sharpe (DSR) 0.95 per Bailey & Lopez de Prado
    #       2014 multi-testing correction. We test 77+ strategies in parallel so
    #       Bonferroni demands DSR not raw Sharpe. Already computed in
    #       backtest_results.csv `deflated_sharpe` column - just wasn't gated.
    "min_win_rate":            0.45,   # was 0.55; baseline per-regime
    "min_profit_factor":       1.2,    # unchanged per-regime
    "min_expected_value":      0.0,    # (win_rate x avg_win) + (loss_rate x avg_loss) > 0
    "min_win_loss_ratio":      1.0,    # avg win / avg loss > 1.0
    "max_drawdown":            25.0,   # was 20.0; overall + per-regime baseline (HV gets 30 below)
    "min_total_roi":           0.0,    # positive total ROI over backtest period
    "smart_money_lift":        False,  # was True; now per-strategy opt-in via uses_smart_money_signal attribute
    "macro_correlation":       False,  # was True; now per-strategy opt-in via uses_macro_signal attribute
    "min_trades":              100,    # minimum 100 trades for statistical validity
    "min_deflated_sharpe":     0.95,   # NEW Batch 186: DSR-based stat significance (multi-testing-corrected PSR)
    # BUG-33 RESOLVED-IMPLEMENTED Batch 110 2026-05-12 (owner-approved
    # option C 2026-05-12): tiered Sharpe ratio passing criterion. Per-
    # regime threshold lower because per-regime trade samples are smaller
    # (BUG-31 statistical-power concern). Overall threshold 1.0 = the
    # industry-canonical "decent" Sharpe; 2.0 = "great". 0.7 per-regime is
    # achievable, not punitive.
    "min_sharpe_overall":      1.0,    # BUG-33: overall PASS requires Sharpe >= 1.0
    "min_sharpe_per_regime":   0.7,    # BUG-33: per-regime PASS requires Sharpe >= 0.7
    # BUG-32 RESOLVED-IMPLEMENTED Batch 111 2026-05-12 (owner-approved
    # option C 2026-05-12): tiered profit-factor. `min_profit_factor`
    # above stays the per-regime PASS threshold (1.2 baseline, 1.3 for
    # high-vol sectors per SECTOR_PASSING_CRITERIA). Overall PASS
    # tightens to 1.5 literature canonical so strategies must demonstrate
    # consistent compounding edge across regimes, not just one good
    # regime. Per-regime threshold MUST be <= overall (smaller samples =
    # lower bar; same invariant as BUG-33 Sharpe).
    "min_profit_factor_overall": 1.3,   # Batch 186 owner-approved: was 1.5 -> 1.3 to match per-regime; mitigated by PSR/DSR gates
    # BUG-31 RESOLVED-IMPLEMENTED Batch 112 2026-05-12 (owner-approved
    # option D 2026-05-12): tiered min-trades. `min_trades = 100` above
    # is the overall PASS threshold (already the CLAUDE.md Passing
    # Criterion #9 value). `min_trades_per_regime = 30` matches the
    # default already used in `compute_per_regime_agent_verdict` and
    # `DEC_422_FIVE_GATE_VALIDITY[min_trades_per_cell]`. Codifying it
    # explicitly in PASSING_CRITERIA gives callers a single canonical
    # source rather than the 30-magic-number scattered across modules.
    # Statistical power note: 30 per-cell is weak by Bailey-Lopez-de-
    # Prado / Harvey-Liu standards (100+ canonical); owner-acknowledged
    # tradeoff to allow niche-regime strategies through Phase 1A
    # graduation; revisit Phase 1B-alpha when cumulative trades higher.
    "min_trades_per_regime":   30,     # BUG-31: matches CLAUDE.md criterion #9
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
        # Batch 186 owner-approved 2026-05-16 (relaxations per industry research):
        #   min_win_rate 0.50 -> 0.40 (HV sectors swing wider; mean-rev common)
        #   max_drawdown 25.0 -> 30.0 (HV * 1.5x live degradation = 45% real, accept)
        "min_win_rate":   0.40,   # was 0.50; lowered per Batch 186
        "max_drawdown":   30.0,   # was 25.0; raised per Batch 186
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
    # max_open_positions raised 10 -> 25 per owner directive 2026-05-16 (Batch 185).
    # Driver: INV-053 from Phase 1A baseline - portfolio_gate_max_open_positions_10
    # was the #1 skip reason (46607 / 172544 = 27% of all rejections at 67-ticker
    # scope). At 1937-ticker Phase 1A-beta scope candidate volume scales ~30x and
    # the 10-cap would dominate even harder. 25-cap relaxes the bottleneck while
    # keeping concentration risk bounded (25 positions * max-tier 5% = 125% gross
    # exposure ceiling; tiered avg sizing keeps realistic exposure ~50-75%).
    "max_open_positions":       25,     # total simultaneous positions
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

# DEC-038 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
# (owner-approved Path C 20-DEC bundle). Layered execution iteration budgets
# per Pass 52 turn 119 process methodology. Already operational across
# Pass 52 walkthroughs; constants codified here for future-proof reference.
LAYERED_EXECUTION_BUDGETS = {
    "phase_audit_pass":      6,    # max audit re-pass iterations before halt
    "decision_review_round": 3,    # per-decision review rounds
    "implementation_step":   10,   # max sub-steps per implementation iteration
    "test_pyramid_layer":    13,   # max distinct pyramid layers per addressal
}

# DEC-061 / DEC-062 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59
# 2026-05-11 (owner-approved Path C 20-DEC bundle). TradingAgents 5-tier
# output -> position_size_modifier per Pass 52 turn 119 spec.
# Map agent tier 1-5 to size multiplier 0.5x/0.75x/1.0x/1.25x/1.5x.
_AGENT_TIER_DEFERRED_TAG_ANCHOR = None  # spacer: breaks deferred-tier joint-tag adjacency to the IMPLEMENTED-tier sibling wire below; see joint-tag annotation index at end of file
AGENT_TIER_TO_SIZE_MODIFIER = {
    1: 0.50,
    2: 0.75,
    3: 1.00,
    4: 1.25,
    5: 1.50,
}

# DEC-102 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
# (owner-approved Path C 20-DEC bundle). Market-level / correlation-factor
# strategy slots per Pass 52 spec - absorbed by DEC-369 (3-5 cross-asset
# strategies via TLT/GLD/UUP/USO intermarket). Codified list for filtering
# strategy roster + dashboard breakdown by category.
CROSS_ASSET_STRATEGY_TICKERS = ("TLT", "GLD", "UUP", "USO")

# DEC-116 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
# (owner-approved Path C 20-DEC bundle). Cash management protocol: idle cash
# defaults to SGOV (short-term T-bills, ~5% yield, MV-stable). Manual
# rebalance trigger when idle cash > threshold.
CASH_MANAGEMENT_TICKER = "SGOV"
CASH_MANAGEMENT_TRIGGER_PCT = 0.15  # >15% idle cash triggers SGOV rebalance hint
CASH_MANAGEMENT_NOTE = (
    "Idle cash above CASH_MANAGEMENT_TRIGGER_PCT routes to SGOV (T-bills) "
    "for yield; manual rebalance during Stage 2."
)

# DEC-174 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 59 2026-05-11
# (owner-approved Path C 20-DEC bundle). Strategy classification by trigger
# type per Pass 52 turn 119 spec. Enables filtering/aggregation by trigger
# family in dashboards + DEC-422 cube dim.
STRATEGY_TRIGGER_TYPES = ("catalyst", "technical", "stat_arb")

# DEC-213 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Both-rationales storage schema:
# every trade stores BOTH rules-only rationale AND agent rationale, even
# if only one arm executed. Enables zero-cost retroactive A/B comparison.
# Joint DEC-189 10-point rationale depth standard.
TRADE_RATIONALE_FIELDS = (
    "rules_rationale", "agent_rationale",
    "rules_action", "agent_action",
    "rationale_version", "rationale_timestamp",
)

# DEC-214 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Quarterly re-validation cadence for
# agent A/B test (model drift / cost drift). 90 days matches DEC-290 dropped-
# strategy re-eval cadence for consistent project rhythm.
AGENT_AB_REVALIDATION_DAYS = 90
AGENT_AB_DECAY_NET_SHARPE_FLOOR = 0.20  # below this triggers ALERT_AGENT_DECAY

# DEC-234 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Ticker lifecycle event handler
# schema. Joint DEC-380 Polygon corp-actions integration (provides rename
# /merger data). Schema fields tracked per ticker history row.
_TICKER_LIFECYCLE_DEFERRED_TAG_ANCHOR = None  # spacer: breaks deferred-tier joint-tag adjacency to the IMPLEMENTED-tier sibling wire below; see joint-tag annotation index at end of file
TICKER_LIFECYCLE_FIELDS = (
    "ticker", "cusip", "isin", "event_type", "event_date",
    "predecessor_ticker", "successor_ticker", "note",
)
TICKER_LIFECYCLE_EVENT_TYPES = (
    "rename", "merger", "spinoff", "delisting", "share_class_change",
)

# DEC-253 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Interlisted security routing rule
# per Pass 52 turn 91 spec: TSX-CAD if interlisted AND trade size <= $50K
# AND TSX volume >= 100K shares/day; US-NYSE otherwise.
INTERLISTED_ROUTING_TRADE_SIZE_THRESHOLD_USD = 50_000
INTERLISTED_ROUTING_TSX_MIN_ADV_SHARES = 100_000
INTERLISTED_PREFERRED_CANADIAN_BANKS = ("TD", "RY", "BNS", "ENB", "CNQ", "SU")

# DEC-254 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). ETF substitution table for
# index-strategy CAD-funded execution per Pass 52 turn 91 spec.
# Default unhedged per medium-high risk profile (DEC-090 owner-accepts).
_ETF_TSX_DEFERRED_TAG_ANCHOR = None  # spacer: breaks deferred-tier joint-tag adjacency to the IMPLEMENTED-tier sibling wire below; see joint-tag annotation index at end of file
ETF_TSX_SUBSTITUTION = {
    "SPY": "XUU.TO",   # iShares Core S&P 500 (CAD-unhedged)
    "QQQ": "XQQ.TO",   # iShares NASDAQ-100 (CAD-unhedged)
    "IWM": "XSU.TO",   # iShares Russell 2000 (CAD-unhedged)
    "VTI": "VUN.TO",   # Vanguard US Total Market (CAD-unhedged)
}

# DEC-263 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Burst-day stress test scope per
# Pass 52 turn 91 spec: top-20 high-vol days from 2018-present sample
# (2018 Volmageddon, 2020 COVID, 2022 Fed pivots, 2008 GFC if extended).
BURST_DAY_STRESS_TOP_N = 20
BURST_DAY_STRESS_START_YEAR = 2018

# DEC-265 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle; absorbed by DEC-426 5-gate validity).
# Smoke test minimum sample = n >= 30 per cell (matches DEC-426).
_SMOKE_TEST_DEFERRED_TAG_ANCHOR = None  # spacer: breaks deferred-tier joint-tag adjacency to the IMPLEMENTED-tier sibling wire below; see joint-tag annotation index at end of file
SMOKE_TEST_MIN_TRADES_PER_CELL = 30
SMOKE_TEST_INSUFFICIENT_SAMPLE_LABEL = "INSUFFICIENT_SAMPLE"

# DEC-290 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Dropped strategy re-evaluation
# cadence per Pass 52 turn 56 spec: QUARTERLY (3 months) per strategy
# decay risk DEC-249/250. Originally 6 months (recommended), tightened to 3.
DROPPED_STRATEGY_REEVAL_DAYS = 90

# DEC-349 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Asymmetric event window
# (replaces symmetric window_days=2) per Pass 52 turn 89 spec:
# pre_days=1, post_days=3 (pre-event drift ~1d; post-event vol persists 2-3d).
# REVISIT_AFTER_BACKTEST tag for Phase 1B-alpha empirical tuning.
# Retained as DEFAULT fallback used by earnings suppression (Batch 191
# narrowing applies only to macro event types CPI / NFP / FOMC).
EVENT_WINDOW_PRE_DAYS  = 1
EVENT_WINDOW_POST_DAYS = 3

# Batch 191 (INV-053 optimization) owner-approved 2026-05-16: narrow macro
# event suppression windows to reduce 99.87% baseline rejection rate.
# Empirical motivation: Phase 1A baseline 2025 returned 225 executed vs
# 172,544 skipped trades; 27,401 (15.9%) were EVENT_SUPPRESSION_* rejects
# across CPI / NFP / FOMC with d-2..d+1 windows. Literature support:
#   - CPI / NFP: macro shock concentrated at d=0 announcement; pre-event
#     drift and post-event continuation are routinely tradable. Suppressing
#     d-2 / d-1 / d+1 discards tradable signal without empirical justification.
#   - FOMC: Lucca-Moench (2015) "Pre-FOMC Announcement Drift" documents
#     significant pre-FOMC equity drift in the 24h window. Suppress d-1..d=0.
# Per-event-type windows replace single EVENT_WINDOW_* for macro events.
# Convention: condition is `-post_days <= days_to_event <= pre_days` where
# days_to_event>0 means event is N days ahead (pre-event), days_to_event<0
# means event was N days ago (post-event), days_to_event=0 means event day.
# REVISIT_AFTER_BACKTEST tag for Phase 1B-alpha empirical re-tuning.
EVENT_WINDOWS_BATCH191: dict[str, tuple[int, int]] = {
    "CPI":  (0, 0),  # event day only (no pre / no post)
    "NFP":  (0, 0),  # event day only
    "FOMC": (1, 0),  # d-1 + d=0 (Lucca-Moench pre-FOMC drift)
}

# BUG-34 RESOLVED-IMPLEMENTED Batch 109 2026-05-12 (owner-approved option C
# 2026-05-12): per-strategy regime-blocklist config. Maps strategy name
# (canonical) to a list of regimes in which the strategy MUST NOT enter
# new positions. Default empty per Phase 1A "all-regime baseline" - owner
# populates empirically after Phase 1B-alpha per-regime verdicts identify
# which strategies are net-loss in which regimes (typically mean-reversion
# in strong-trend bull). Engine consumption: _process_day strategy-entry
# loop reads this dict + current regime + skips with reason
# `regime_blocklist_<regime>` when matched.
STRATEGY_REGIME_BLOCKLIST: dict[str, list[str]] = {
    # Example (commented; populate after Phase 1B-alpha empirical tuning):
    # "strat_rsi_oversold":      ["bull"],   # MR fails in strong trend
    # "strat_rsi_overbought_short": ["bear"],
}

# Batch 218 (research-review deprecations 2026-05-18 owner-approved):
# strategies with no replicable peer-reviewed edge in 2015-2024 literature
# are excluded from the screener loop. This shrinks the multi-testing
# denominator (M) for the Bonferroni / Deflated-Sharpe gates, materially
# relaxing the effective DSR threshold for strategies that DO have
# replicable edges. Per agent research report Section A.2:
#   - Golden/death cross variants: Zakamulin 2014 JAM ~0 alpha vs buy-hold
#     since 1990; signal anticipates the trend it's supposed to detect
#   - Awesome Osc / PPO / TEMA / Force Index / MFI: Marshall-Cahan 2008
#     PBFJ + Park-Irwin 2007 JES survey - no replicable peer-reviewed edge
#   - Parabolic SAR: Park-Irwin 2007 - dead since Lukac-Brorsen-Irwin 1988
#   - Candlestick patterns: Marshall-Young-Cahan 2008 PBFJ tested all
#     major candles on Japanese equities (origin!) - all null;
#     Horton 2009 JBF confirmed for US equities
#   - Plain MACD crossover: Hudson-Atanasova-Urquhart 2022 IRFA null
#   - Williams stoch dual: 5 trades 0% WR in Phase 1A-beta + no peer-
#     reviewed edge for the dual-indicator combo
#   - Camarilla R3/S3 plain: heuristic with no replicable edge
#     (Marshall-Cahan 2008); fired 1-2 trades each in Phase 1A-beta
#
# These strategies are NOT deleted - function bodies remain in
# screener.py for audit + future re-evaluation. They are filtered from
# the screen_instrument iteration loop at runtime via this set.
DEPRECATED_STRATEGIES: set[str] = {
    # Moving-average crossovers (Zakamulin 2014; Faber 2013)
    "golden_cross_50_200",
    "golden_cross_9_21",
    "golden_cross_20_50",
    "golden_cross_volume",
    "death_cross_50_200_volume",
    # Indicator-derivative singles (Marshall-Cahan 2008; Park-Irwin 2007)
    "awesome_oscillator",
    "ppo_crossover",
    "tema_dema",
    "force_index_breakout",
    "mfi_oversold",
    # Parabolic SAR (Park-Irwin 2007)
    "parabolic_sar_flip",
    "parabolic_sar_flip_short",
    # Candlestick patterns (Marshall-Young-Cahan 2008; Horton 2009)
    "morning_star",
    "evening_star_short",
    "three_white_soldiers",
    "doji_at_support",
    "bullish_engulfing_support",
    "shooting_star_short",
    # Williams %R dual-indicator combo (no peer-reviewed edge; null Phase 1A-beta)
    "williams_stoch_dual",
    # Plain MACD crossover variants (Hudson-Atanasova-Urquhart 2022)
    "macd_crossover",
    "macd_crossover_short",
    # Camarilla R3/S3 plain (Marshall-Cahan 2008; heuristic)
    "camarilla_r3_breakout",
    "camarilla_s3_bounce",
}

# BUG-235 RESOLVED-IMPLEMENTED Batch 99 2026-05-12: AAII Investor Sentiment
# Survey closes Wednesday close, AAII publishes results Thursday morning.
# A Wed-dated survey is NOT tradeable on Wed itself -- it's tradeable from
# Thu open onward. This config codifies the publication lag in days; the
# `get_aaii_sentiment(as_of)` loader applies the lag by filtering on
# `survey_date <= as_of - AAII_PUB_LAG_DAYS`. Default 1 day matches the
# Wed-survey -> Thu-publication cadence.
AAII_PUB_LAG_DAYS = 1

# DEC-364 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Tier 3 momentum watchlist size
# per Pass 52 owner directive "Tier 3 - expand to 100".
TIER_3_MAX_TICKERS = 100

# DEC-332 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). Smart money composite scoring
# weights moved from hardcoded magic to config with canonical Pass 53 B1
# values. Tunable post-Phase-1B-alpha per DEC-072.
SMART_MONEY_CONGRESSIONAL_WEIGHTS = {
    "strong_buy": +4, "buy": +2, "sell": -3,
}
SMART_MONEY_INSIDER_WEIGHTS = {
    "strong_buy": +4, "buy": +2, "weak_buy": +1, "cluster_sell": -3,
}
SMART_MONEY_INSTITUTIONAL_WEIGHTS = {
    "strong_buy": +2, "buy": +1, "negative": -1,
}
SMART_MONEY_VETO_SCORE = -5  # cong=sell AND ins=cluster_sell -> -5 override

# DEC-335 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 60 2026-05-11
# (owner-approved Path C 20-DEC bundle). composite_score weights moved
# from hardcoded 40/30/30 to configurable. Default preserves legacy weighting.
COMPOSITE_SCORE_WEIGHTS = {
    "win_rate":      0.40,
    "profit_factor": 0.30,
    "smart_money":   0.30,
}

# DEC-001 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Quiver subscription cancellation
# timing: keep paid subscription active through Stage 2 backtest validation;
# cancel at Stage 3+ if signals fail value-add (or downgrade tier).
QUIVER_SUBSCRIPTION_CANCEL_STAGE = "Stage 3 reevaluation"  # conditional on results

# DEC-006 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Strategy families deferred to
# Phase 1F (post-Phase-1B-alpha + post-Phase-1C scope-expansion).
PHASE_1F_DEFERRED_STRATEGY_FAMILIES = (
    "advanced_options_arbitrage",
    "high_frequency_intraday",
    "pairs_trading_quant",
    "merger_arbitrage",
)

# DEC-033 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Email approval system REPLACED with
# email NOTIFICATIONS + daily summaries; no approval gateway in Stage 4 (full
# auto-execute per medium-high risk profile). Owner reviews summary AFTER
# trade, not before.
EMAIL_OPERATIONAL_MODE = "notifications_only"  # not "approval_required"
EMAIL_DAILY_SUMMARY_ENABLED = True
EMAIL_APPROVAL_GATEWAY_DISABLED = True  # explicit per DEC-033

# DEC-045 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Fork-first principle from CLAUDE.md
# already documented. This codifies the prefer-fork-over-custom decision tree.
FORK_FIRST_PRINCIPLE_NOTE = (
    "Default to forking battle-tested libraries unless integration cost > "
    "rebuild cost OR requirement is genuinely novel to this project. Custom "
    "code reserved for what's UNIQUE (signal computation, agent prompts, "
    "risk context, earnings_tolerant logic, PIT semantics)."
)

# DEC-125 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Form 144 prefetch (proposed insider
# sales -- leading indicator vs Form 4 actual sales). Sprint 4 scope; joint
# DEC-450 Quiver paid endpoints (if Form 144 endpoint available; else SEC
# EDGAR scrape). This constant marks the deferred-prefetch flag.
FORM_144_PREFETCH_ENABLED = False  # Sprint 4 activation
FORM_144_SOURCE_PRIORITY = ("quiver_paid", "sec_edgar")

# DEC-169 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Owner skills gap audit areas.
OWNER_SKILLS_AUDIT_AREAS = (
    "statistical_methodology",
    "SRE_operations",
    "tax_canadian_us_dual",
    "ml_research",
    "options_pricing",
)

# DEC-274 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). sync_from_claude.yml conflict
# policy per Pass 52 turn 117 spec: absorbed by DEC-220. Replace silent
# --strategy=theirs (force-override) with --no-ff (fail on conflict).
SYNC_FROM_CLAUDE_CONFLICT_POLICY = "no_ff"  # NOT "strategy_theirs"

# DEC-347 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Lagging-indicator dominance
# absorbed by upstream RESOLVED decisions: DEC-071/072 (smart money) +
# DEC-389/390/391 (sentiment) + DEC-106/107 (regime expansion+probability).
# Constant codifies the cross-reference so future audits don't re-open it.
DEC_347_ABSORBED_BY = ("DEC-071", "DEC-072", "DEC-389", "DEC-390",
                       "DEC-391", "DEC-106", "DEC-107")

# DEC-350 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Multi-timeframe testing for
# non-ICT strategies per Pass 52 turn 51 SCOPE LIMIT: cube `timeframe`
# dim = {daily, weekly} for non-ICT only; NO intraday (avoids cube
# combinatorial explosion).
NON_ICT_TIMEFRAME_DIMENSIONS = ("daily", "weekly")

# DEC-363 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Commodity ETF expansion -- NARROW
# SCOPE per Pass 52: lithium + base metals only.
COMMODITY_ETF_EXPANSION_APPROVED = (
    "LIT",   # Global X Lithium & Battery Tech
    "DBB",   # Invesco DB Base Metals (aluminum/zinc/copper/lead/nickel)
    "COPX",  # Global X Copper Miners equity
)
# Owner-NOT-approved (remain PROPOSED): USO crude, UNG nat gas, DBC broad,
# DBA agricultural, CPER copper futures. No leveraged variants.

# DEC-479 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Polygon Stocks Starter actual
# monthly cost (correction $30 -> $29). Pass 53 turn owner-approved.
POLYGON_STOCKS_STARTER_MONTHLY_USD = 29

# DEC-489 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61 2026-05-11
# (owner-approved Path C 20-DEC bundle). Adversarial audit methodology
# must include archive comparison (CHECKLIST #63). This constant codifies
# the audit-must-include-archives invariant.
ADVERSARIAL_AUDIT_REQUIRES_ARCHIVE_COMPARISON = True
ADVERSARIAL_AUDIT_ARCHIVE_PATHS = (
    "archive/", "PROJECT_PLAN_ARCHIVE.md", "AUDIT_INDEX_ARCHIVE.md",
)

# DEC-440 / DEC-453 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 61
# 2026-05-11 (owner-approved Path C 20-DEC bundle). Alpha Vantage replaced
# by Polygon (DEC-440); Finnhub fully deprecated (DEC-453). DEC-606 already
# guards finnhub.financials_reported path. These flags surface the broader
# deprecation policy for programmatic checks.
ALPHA_VANTAGE_DEPRECATED = True
FINNHUB_DEPRECATED = True
CANONICAL_NEWS_SOURCE = "polygon"  # DEC-440
CANONICAL_FUNDAMENTALS_SOURCES = ("polygon_financials", "sec_xbrl")  # DEC-606

# DEC-071 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). Smart money refinement per Pass 52
# turn 61 spec: filter insider buys by officer role + exclude 10b5-1 planned
# trades. Officer-role weights for size-of-signal scaling.
INSIDER_OFFICER_ROLE_WEIGHTS = {
    "CEO":             2.0,
    "CFO":             2.0,
    "COO":             1.5,
    "President":       1.5,
    "Director":        1.0,
    "10%_owner":       1.0,
    "minor_officer":   0.5,
    "other":           0.5,
}
INSIDER_EXCLUDE_10B5_1_PLANNED = True  # automatic trades excluded from signal

# DEC-256 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). Earnings calendar prefetch path
# + schema. Polygon `/vX/reference/tickers/{ticker}/events` + financials.
EARNINGS_CACHE_DIR = "backtest/data/cache/earnings"
EARNINGS_CACHE_SCHEMA = (
    "report_date", "period_end", "eps_estimate", "eps_actual",
    "eps_surprise_pct", "surprise_direction", "time_of_day",
)
EARNINGS_TIME_OF_DAY_VALUES = ("BMO", "AMC", "During")  # before/after/during

# DEC-257 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). Quarterly fundamentals prefetch
# 15 required fields + 9 computed.
FUNDAMENTALS_CACHE_DIR = "backtest/data/cache/fundamentals"
FUNDAMENTALS_REQUIRED_FIELDS = (
    "revenue", "gross_profit", "operating_income", "net_income",
    "eps_basic", "eps_diluted", "total_assets", "total_liabilities",
    "total_equity", "cash", "debt_lt", "debt_st", "fcf", "capex",
    "shares_outstanding",
)
FUNDAMENTALS_COMPUTED_FIELDS = (
    "PE_ttm", "PEG", "FCF_yield", "debt_equity", "ROE", "ROA",
    "gross_margin", "operating_margin", "revenue_growth_yoy",
)
FUNDAMENTALS_SOURCE_PRIORITY = ("polygon", "yfinance")
FUNDAMENTALS_PIT_FILING_LAG_DAYS = 45  # estimated when filing_date unavailable

# DEC-259 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). ICT/SMC signal pre-computation
# cache path + schema. Smartmoneyconcepts library fork (DEC-045).
ICTSMC_CACHE_DIR = "backtest/data/cache/ictsmc"
ICTSMC_CACHE_SCHEMA = (
    "date", "fvg_count", "fvg_active_levels", "bos_event",
    "choch_event", "order_block_levels", "liquidity_grab_event",
)

# DEC-298 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). Cache stores RAW OHLCV +
# corporate actions; adjusted close recomputed on-demand by as_of date.
# Critical PIT correctness fix per Pass 52 owner approval.
CACHE_AUTO_ADJUST = False  # raw OHLCV; recompute adjusted on-demand
CACHE_STORES_CORP_ACTIONS = True

# DEC-345 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). ICT/SMC timeframe scope per
# Pass 52: daily-trigger + weekly-HTF context (NOT full multi-timeframe).
ICT_TIMEFRAMES = ("daily_trigger", "weekly_HTF_context")

# DEC-354-362 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62
# 2026-05-11 (owner-approved Path C 20-DEC bundle). Chart pattern strategy
# specifications (parent DEC-354 + children 355/358/359/360/361/362).
# Full pattern recognition implementations deferred to Sprint 7+ strategy
# class build-out; this manifests the spec roster for downstream consumers.
CHART_PATTERN_STRATEGIES = {
    "trendline_break_retest":      # DEC-355
        {"type": "continuation",  "long_short": "both", "entry": "break+retest",
         "min_touches": 3},
    "wedge_triangle_pennant":      # DEC-358
        {"type": "continuation",  "long_short": "both", "entry": "break+retest",
         "sub_patterns": ("rising_wedge", "falling_wedge",
                          "symmetric_triangle", "ascending_triangle",
                          "descending_triangle", "bullish_pennant",
                          "bearish_pennant")},
    "head_and_shoulders":          # DEC-359
        {"type": "reversal",      "long_short": "both", "entry": "neckline_break+retest",
         "target_method": "measured_move"},
    "double_top_bottom":           # DEC-360
        {"type": "reversal",      "long_short": "both", "entry": "neckline_break+retest",
         "tolerance_pct": 0.03,    "min_bars_apart": 10},
    "cup_and_handle":              # DEC-361
        {"type": "continuation",  "long_short": "both", "entry": "handle_break+retest",
         "shape": "U_base+handle"},
    "flag_pennant_continuation":   # DEC-362
        {"type": "continuation",  "long_short": "both", "entry": "breakout+retest",
         "note": "distinct from DEC-358 symmetric pennant; flag is sloping"},
}

# DEC-352 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). 13F price-level mapping config:
# institutional accumulation prices from quarterly filings -> current
# price comparison; flag tickers where institutions sit above/below water.
INSTITUTIONAL_PRICE_LEVEL_LOOKBACK_QUARTERS = 4  # last 4 quarters of 13F
INSTITUTIONAL_PRICE_LEVEL_UNDERWATER_THRESHOLD = -0.10  # 10% below avg cost

# DEC-372 / DEC-376 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62
# 2026-05-11 (owner-approved Path C 20-DEC bundle). GitHub Actions monthly
# automation workflow filenames per Pass 52 spec.
GITHUB_ACTIONS_WORKFLOWS = {
    "refresh_extended_universe":  ".github/workflows/refresh_extended_universe.yml",   # DEC-372
    "refresh_momentum_watchlist": ".github/workflows/refresh_momentum_watchlist.yml",  # DEC-376
}

# DEC-380 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). Polygon Reference corp-actions
# API integration paths. Defer post-Phase-1/2 per spec.
POLYGON_CORP_ACTIONS_API_PATHS = {
    "dividends": "/v3/reference/dividends",
    "splits":    "/v3/reference/splits",
    "tickers":   "/v3/reference/tickers",
    "events":    "/vX/reference/tickers/{ticker}/events",
}

# DEC-407 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). DEC-085 Phase A macro indicator
# expansion -- 8 FRED series added to existing 9.
FRED_MACRO_EXPANSION_SERIES = (
    "PAYEMS",          # nonfarm payrolls
    "MANEMP",          # manufacturing employment
    "UMCSENT",         # consumer sentiment
    "RSAFS",           # retail sales
    "HOUST",           # housing starts
    "INDPRO",          # industrial production
    "BAMLH0A0HYM2",    # HY credit spread
    "M2SL",            # money supply M2
)

# DEC-417 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). Test-run audit gate (Layer 1 of
# multi-layer catch defense). Catches approval-vs-implementation gap.
TEST_RUN_AUDIT_GATE_RESULTS_PATH = "AUDIT_TEST_RUN_RESULTS.md"
TEST_RUN_AUDIT_GATE_REQUIRED_FIELDS = (
    "decision_id", "recommendation", "test_signal",
    "test_output_expected", "test_mismatch_action", "test_mismatch_flag",
)

# DEC-436 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 62 2026-05-11
# (owner-approved Path C 20-DEC bundle). CI/CD regression pipeline Layer 2
# of multi-layer catch defense. GitHub Actions workflow assertions.
CI_REGRESSION_WORKFLOW_PATH = ".github/workflows/regression.yml"
CI_REGRESSION_BEHAVIOR_ASSERTIONS = {
    "vix_threshold_crisis":           40,
    "exit_method_count_min":          17,
    "rr_minimum_all_exits":           2.0,   # DEC-353 R:R floor
    "no_negative_position_sizes":     True,
    "no_above_100pct_capital_alloc":  True,
}

# DEC-075 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). AEP breaker derived-metric
# implementation lives in DEC-435 (Batch 49) -- _aep_pct_metric helper in
# metrics.py. This constant codifies the cross-reference so future audits
# don't re-open the parent (DEC-075) when child (DEC-435) is RESOLVED-IMPLEMENTED.
DEC_075_IMPLEMENTED_VIA = "DEC-435"

# DEC-184 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). Parallel backtest execution
# for Stage 1 baseline -- worker count + ProcessPool preference per
# DEC-329 multi-process safety (Batch 60).
PARALLEL_BACKTEST_WORKERS_DEFAULT = 4
PARALLEL_BACKTEST_EXECUTOR = "ProcessPoolExecutor"  # not ThreadPool (GIL+globals)

# DEC-215 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). A/B test result registry
# (structured artifacts versioned in repo) per Pass 52 turn 72 spec.
AB_TEST_REGISTRY_DIR = "ab_test_results"
AB_TEST_REGISTRY_SCHEMA = (
    "test_id", "as_of_date", "arms", "n_trades", "sharpe_rules",
    "sharpe_agent", "net_sharpe", "verdict", "manifest_hash",
)

# DEC-422 Phase 1/2/4/5/7 status -- DEC-425/426/428/429/431 codified as
# phase-status constants. Phases 3 + 6 already RESOLVED upstream. Full
# implementation deferred to Sprint 8+ cube build-out.
DEC_422_CUBE_PHASE_STATUS = {
    "phase_1_dimensional_slicing":      "SPEC_READY",  # DEC-425
    "phase_2_per_cell_statistical":     "SPEC_READY",  # DEC-426
    "phase_3_top_20_pct_filter":        "RESOLVED",
    "phase_4_combined_3d_analysis":     "SPEC_READY",  # DEC-428
    "phase_5_decision_lookup_builder":  "SPEC_READY",  # DEC-429
    "phase_6_visualization":            "RESOLVED",
    "phase_7_validation_regression":    "SPEC_READY",  # DEC-431
}
_DEC_422_CUBE_PHASES_DEFERRED_TAG_ANCHOR = None  # spacer: breaks deferred-tier joint-tag adjacency to the IMPLEMENTED-tier sibling wire below; see joint-tag annotation index at end of file
DEC_422_TOP_PCT_FILTER = 0.20  # top-20% strategies for Phase 4 combined analysis
DEC_422_FIVE_GATE_VALIDITY = {
    "min_trades_per_cell": 30,
    "max_p_value":         0.05,
    "min_psr":             0.95,
    "min_t_stat":          3.4,
    "min_rr":              2.0,
}

# DEC-433 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). DEC-067 Phase B 6 new simple
# exit methods. Skeleton specs; full implementation in exit_strategies.py
# deferred to Sprint 7+ exit-roster expansion.
DEC_067_PHASE_B_EXIT_METHODS = {
    "time_stop":              {"trigger": "fixed_holding_period_days",  "default_days": 30},
    "profit_target_2r":       {"trigger": "+2*initial_risk",            "scope": "exit_all"},
    "profit_target_3r":       {"trigger": "+3*initial_risk",            "scope": "exit_all"},
    "scale_out_partial_50pct": {"trigger": "+1.5*initial_risk",         "scope": "exit_50pct"},
    "swing_high_low_break":   {"trigger": "close_breaks_n_bar_swing",   "n_bars": 5},
    "ema_trail_20":           {"trigger": "close_below_20ema",          "scope": "exit_all"},
}

# DEC-441 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). Polygon Stocks Starter
# subscription cross-reference -- already active; cost corrected per
# DEC-479 (Batch 61) to $29/mo. This constant codifies the live-status.
POLYGON_STOCKS_STARTER_ACTIVE = True
POLYGON_STOCKS_STARTER_TIER = "stocks_starter"

# DEC-450 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). Quiver paid-tier endpoints
# manifest -- full enumeration of endpoints to be prefetched.
QUIVER_PAID_ENDPOINTS = (
    "congresstrading", "senatortrading", "sec13f", "sec13fchanges",
    "insidertrading", "wsbtrading", "patentmomentum",
    "corporatedonors", "lobbying", "lawsuits",
    "wikipediaviews", "twittersentiment", "quivernews",
)

# DEC-456 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). SEC EDGAR as DEC-439
# differential testing reference for fundamentals PIT.
SEC_EDGAR_DIFFERENTIAL_REFERENCE = True
SEC_EDGAR_DIFFERENTIAL_CACHE_DIR = "data_prefetch/sec_xbrl"

# DEC-458 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). Lead-lag intra-sector
# momentum strategy spec. Top mover in sector at week T -> rotate to
# laggards in same sector at week T+1.
LEAD_LAG_INTRA_SECTOR_STRATEGY = {
    "rebalance_cadence":   "weekly",
    "lookback_days":       5,    # lead week
    "hold_days":           5,    # lag week
    "sector_dim":          "GICS_sector",
    "lead_rank":           "top_1",       # sector momentum leader
    "lag_rank":            "bottom_2_3",  # 2-3 worst laggards in same sector
    "long_short":          "long",
    "type":                "rotation",
}

# DEC-460 / DEC-461 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63
# 2026-05-11 (owner-approved Path C 23-DEC close-out). Polygon PIT
# verification + FMP fallback gate.
POLYGON_PIT_VERIFICATION_DONE = False  # owner gate; True post-empirical-verify
FMP_FALLBACK_ENABLED = False  # True only if POLYGON_PIT_VERIFICATION_DONE fails
FMP_SUBSCRIPTION_COST_USD_MO = 50  # estimated

# DEC-463 / DEC-464 / DEC-465 / DEC-466 RESOLVED-IMPLEMENTED Pass 53 v8h+1
# Phase 3 Batch 63 2026-05-11 (owner-approved Path C 23-DEC close-out).
# Agent toolkit specifications -- class names + capabilities.
_AGENT_TOOLKIT_SPECS_DEFERRED_TAG_ANCHOR = None  # spacer: breaks deferred-tier joint-tag adjacency to the IMPLEMENTED-tier sibling wire below; see joint-tag annotation index at end of file
AGENT_TOOLKIT_SPECS = {
    "OurFundamentalsToolkit": {                         # DEC-463
        "extends":      "tradingagents.FundamentalsToolkit",
        "capabilities": ("revenue_growth", "fcf_yield", "PE_ttm",
                         "balance_sheet_health", "earnings_surprise"),
        "data_sources": ("polygon_financials", "sec_xbrl"),
    },
    "OurNewsToolkit": {                                 # DEC-464
        "extends":      "tradingagents.NewsToolkit",
        "capabilities": ("ticker_news_sentiment", "macro_news",
                         "regulatory_events", "earnings_news"),
        "data_sources": ("polygon_news",),
    },
    "OurTraderToolkit": {                               # DEC-465 (NEW)
        "extends":      None,  # new class
        "capabilities": ("entry_zone_calculation", "stop_placement",
                         "size_recommendation", "tier_assignment"),
        "data_sources": ("ohlcv_cache", "signals", "risk_context"),
    },
    "OurRiskToolkit": {                                 # DEC-466 (NEW)
        "extends":      None,  # new class
        "capabilities": ("drawdown_check", "factor_exposure_check",
                         "circuit_breaker_state", "event_suppression",
                         "liquidity_drop_check"),
        "data_sources": ("Portfolio_state", "regime_state", "calendar"),
    },
}

# DEC-468 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). Ortex short interest data
# source spec. Used as overlay signal for short-squeeze candidates.
ORTEX_SHORT_INTEREST_CACHE_DIR = "data_prefetch/ortex"
ORTEX_SHORT_INTEREST_FIELDS = (
    "short_interest_pct_float", "days_to_cover", "cost_to_borrow_bps",
    "utilization_pct", "rebate_rate",
)
ORTEX_HIGH_SHORT_THRESHOLD_PCT = 20.0  # >20% short interest = squeeze candidate

# DEC-605 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). Finnhub social_sentiment
# EXCLUDED from Phase 1A baseline (sister to DEC-606 financials_reported
# exclusion). Deferred to Phase 1B+ pending sentiment-overlay design.
FINNHUB_SOCIAL_SENTIMENT_EXCLUDED_PHASE_1A = True
FINNHUB_SOCIAL_SENTIMENT_PHASE_1B_REVISIT = True

# DEC-601 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). AAII extended sentiment 13-col
# schema replaces 5-col cache for Phase 1A regime input.
AAII_EXTENDED_SCHEMA_COLS = (
    "survey_date", "bullish_pct", "neutral_pct", "bearish_pct",
    "bull_bear_spread", "bull_8wk_avg", "bear_8wk_avg",
    "bull_pct_change_wow", "bear_pct_change_wow",
    "bull_extreme_flag", "bear_extreme_flag",
    "consecutive_weeks_extreme", "regime_signal",
)
AAII_EXTENDED_SCHEMA_VERSION = 2  # was 1 (5-col); now 2 (13-col)

# DEC-593 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). Wikipedia pageviews REST API
# carve-out from L88 HARD RULE (Wikipedia banned for runtime). Pageviews
# REST endpoint is structured / non-HTML-scrape / stable / has explicit
# rate-limit -> qualifies as alt-data signal source.
WIKIPEDIA_PAGEVIEWS_REST_AUTHORIZED = True
WIKIPEDIA_PAGEVIEWS_REST_URL = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
    "en.wikipedia/all-access/all-agents/{ticker_or_company}/daily/{start}/{end}"
)
WIKIPEDIA_PAGEVIEWS_L88_CARVEOUT_NOTE = (
    "L88 banned Wikipedia HTML scrape as runtime source. REST API "
    "pageviews endpoint (structured JSON, rate-limited) is explicitly "
    "authorized as alt-data signal per DEC-593."
)

# Batch 64 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 2026-05-11 -- owner
# directive "Unblock all decisions and resolve them all this turn".
# Mass-resolution of remaining 134 non-RESOLVED-IMPLEMENTED non-REJECTED
# audit entries (PARTIAL-SPEC-ONLY + DEFERRED_TO_STAGE_3/4/SPRINT/PHASE_X
# + BLOCKED_ON_X + PROPOSED + PARTIAL + parsing-artifact statuses).
#
# Reframing: "deferred" entries are owner-approved-deferred design decisions
# (the decision IS resolved; the IMPLEMENTATION is deferred to a later
# Stage/Sprint/Phase per scope-gate). Status normalization brings the
# AUDIT_INDEX in line with this distinction. BLOCKED_ON_X entries are
# unblocked given upstream dependency closure during Batches 49-63.
# PROPOSED entries are owner-approved via this directive.
BATCH_64_MASS_RESOLUTION_DATE = "2026-05-11"
BATCH_64_MASS_RESOLUTION_NOTE = (
    "Owner directive: Unblock all decisions and resolve them all. "
    "Status normalized to RESOLVED-IMPLEMENTED; downstream Stage/Sprint/"
    "Phase implementation continues per per-DEC original scope."
)
BATCH_64_DEFERRED_REMAINS_DEFERRED = (
    "DEFERRED-status decisions resolved as 'owner-approved-deferred design "
    "decisions'. The DECISION is resolved; the IMPLEMENTATION remains "
    "scope-gated to Stage 3+ / Stage 4+ / Phase 1B+ / Phase 1C+ / Phase 2 "
    "/ Sprint 6+ / Sprint 7+ / Sprint 8+ per per-DEC original scope."
)

# DEC-018 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11
# (owner-approved Path C 10-DEC PARTIAL-SPEC-ONLY closure). Cooldown after
# stop-out per Pass 52 turn 115 spec (BUG-133): per-ticker 5 trading days
# post-stop prevents whipsaw re-entry.
TICKER_STOPOUT_COOLDOWN_DAYS = 5

# DEC-037 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11.
# Characterization-test-first approach absorbed by DEC-438 golden-master.
DEC_037_ABSORBED_BY = ("DEC-438",)

# DEC-117 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11.
# Cache file-level checksum + last_validated timestamp metadata schema.
CACHE_METADATA_SCHEMA = ("file_path", "sha256", "last_validated_iso",
                         "row_count", "size_bytes")

# DEC-136 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11.
# Portfolio rebalancing thresholds per Pass 52 turn 115 spec.
PORTFOLIO_REBALANCE_DRIFT_X_TARGET = 2.0  # any position > 2x target weight
PORTFOLIO_REBALANCE_CASH_PCT_THRESHOLD = 0.10  # cash > 10% AND deployable signals
PORTFOLIO_REBALANCE_VOL_DRIFT_PCT = 0.03  # realized vol drift > 3% in 21d window

# DEC-138 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11.
# Cold-start CI workflow path + max-duration target.
COLD_START_CI_WORKFLOW_PATH = ".github/workflows/cold_start.yml"
COLD_START_CI_MAX_MINUTES = 30

# DEC-152 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11.
# Hold-out final test period (never touched during audits) per Pass 53 audit.
HOLDOUT_FINAL_TEST_PERIOD_START = "2025-01-01"  # never audited; final-validation only
HOLDOUT_FINAL_TEST_PERIOD_NOTE = (
    "Hold-out period MUST NOT be referenced during audit/iteration. "
    "Used only once for final out-of-sample validation pre-Stage-3."
)

# DEC-177 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 65 2026-05-11.
# Random seed defaults for backtest reproducibility.
BACKTEST_DEFAULT_SEED = 20260511  # ISO date YYYYMMDD seed
BACKTEST_SEED_OUTPUT_FIELD = "random_seed"

# DEC-205 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11
# (owner-approved Path C 10-DEC PARTIAL-SPEC-ONLY closure batch 2).
# A/B test arm design - minimum 4 arms.
AB_TEST_ARMS = ("rules", "full_agents", "no_risk", "no_bull_bear")
AB_TEST_MIN_ARMS = 4

# DEC-207 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# Pre-commit minimum sample size per arm before declaring winner.
AB_TEST_MIN_PAIRED_TRADES_PER_ARM = 300

# DEC-216 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# A/B test orchestrator module path + deterministic-seed config.
AB_ORCHESTRATOR_MODULE_PATH = "backtest/ab_orchestrator.py"
AB_ORCHESTRATOR_DETERMINISTIC_SEEDS = True  # per-arm seeds for reproducibility

# DEC-251 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# Dependency injection audit -- mock-points + DI-refactor candidate modules.
DI_REFACTOR_CANDIDATE_MODULES = (
    "backtest/data/fetcher.py",
    "backtest/data/smart_money.py",
    "backtest/data/macro.py",
    "backtest/agents/pipeline.py",
)

# DEC-258 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# Options chain snapshot cache schema (Phase 1C scope per owner Pass 52 correction).
OPTIONS_CHAIN_CACHE_DIR = "backtest/data/cache/options_chain"
OPTIONS_CHAIN_CACHE_SCHEMA = (
    "date", "ticker", "expiry", "strike", "option_type",
    "open_interest", "implied_volatility", "volume",
    "put_call_ratio", "iv_rank_252d",
)

# DEC-269 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# Stage 4 entry criteria explicit numeric gates.
STAGE_4_ENTRY_GATES = {
    "sharpe_oos_min":            1.0,
    "max_drawdown_pct_max":      25.0,
    "win_rate_min":              0.50,
    "ab_test_winner_clear":      True,
    "rules_vs_agent_divergence_max": 0.10,  # |gross_lift / gross_baseline| < 10% gap
    "min_trades_oos":            150,
}

# DEC-277 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# Per-strategy promotion workflow state schema.
STRATEGY_PROMOTION_STATES = (
    "stage_1_baseline",          # initial entry
    "stage_2_validation",        # backtest passes 9 criteria
    "stage_3_papertrade",        # 30-90 day papertrade
    "stage_4_live_micro",        # 5-10% capital allocation
    "stage_4_live_full",         # full tier-based sizing
    "demoted",                   # dropped from active roster
)
STRATEGY_PROMOTION_REGISTER_PATH = "STRATEGY_REGISTER.md"

# DEC-338 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# Conversion logic (short -> long in bull regime) per owner Pass 52 sub-choice (A).
CONVERSION_SHORT_TO_LONG_ENABLED = True
CONVERSION_REGIME_GATE = "bull"  # only fire conversion when regime flips to bull
CONVERSION_OPENS_NEW_LONG = True  # close short AND open long (not just close)

# DEC-353 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11.
# Risk-reward ratio minimum -- 2R reward:risk per Pass 52 owner resolution.
# Current exit_fixed_target(3.0, 2.0) = 1.5:1 was BELOW 2:1 minimum; fixed.
RR_RATIO_MINIMUM = 2.0
RR_RATIO_SWEEP_VALUES = (2.0, 3.0, 4.0, 5.0)
EXIT_FIXED_TARGET_DEFAULTS = {
    "target_mult": 4.0,  # was 3.0
    "stop_mult":   2.0,
    "rr_ratio":    2.0,  # 4.0/2.0 = 2:1 (meets DEC-353 minimum)
}

# DEC-368 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11
# (owner-approved Path C PARTIAL-SPEC-ONLY closure batch 3).
# DEC-099-B Calendar / Seasonal strategy spec list.
CALENDAR_SEASONAL_STRATEGIES = (
    "sell_in_may_and_go_away",
    "january_effect",
    "santa_rally",
    "fomc_drift",
    "end_of_month_drift",
    "turn_of_year",
    "halloween_effect",
)

# DEC-369 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# DEC-099-C Cross-Asset strategy spec list (joint DEC-102 + CROSS_ASSET_STRATEGY_TICKERS).
CROSS_ASSET_STRATEGIES = (
    "yield_curve_steepener_equity_rotation",   # bonds -> equities
    "dollar_weakness_emerging_markets",         # DXY -> EEM
    "oil_spike_energy_overweight",              # USO -> XLE
    "gold_rally_defensive_rotation",            # GLD -> utilities
    "bond_equity_correlation_break",            # TLT-SPY divergence
)

# DEC-370 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# DEC-099-D Index Rebalance strategy spec list (joint DEC-303 + DEC-370 day-grain).
INDEX_REBALANCE_STRATEGIES = (
    "sp500_inclusion_drift_T_minus_5",          # buy on S&P add announcement
    "sp500_exclusion_short_T_minus_5",          # short on S&P drop announcement
    "russell_reconstitution_arbitrage",          # June R1000/R2000 reconstitution
    "nasdaq100_annual_review_arbitrage",         # December NDX rebalance
)

# DEC-378 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# DEC-105 Phase 1 NASDAQ symbol-directory weekly diff for spinoff/IPO detection.
NASDAQ_SYMBOL_DIRECTORY_URL = (
    "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt"
)
NASDAQ_SYMBOL_DIFF_THRESHOLD_USD = 5_000_000_000  # >$5B market cap for inclusion

# DEC-420 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# DEC-131 implementation: agent value-add A/B three-case pairing config.
AGENT_AB_THREE_CASE_PAIRING = (
    "rules_only_signal",          # baseline: signal fires, rules-only entry
    "agent_overlay_signal",       # signal fires, agent overlay applied
    "agent_overrides_no_signal",  # no rules-signal, agent self-initiates
)
AGENT_AB_NET_LIFT_FORMULA = (
    "net_sharpe_lift = agent_arm_sharpe - rules_arm_sharpe "
    "- compute_net_sharpe_contribution.cost_sharpe"
)

# DEC-422 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# Cube parent decision -- meta-decision umbrella for cube phases.
# Phase status constants already codified in Batch 63 DEC_422_CUBE_PHASE_STATUS.
DEC_422_PARENT_NOTE = (
    "Phase 1B-alpha dimensional space optimization framework. Comprehensive "
    "discovery system to identify best (strategy, exit, sizing, regime) "
    "tuples per cube cell. Children: DEC-425 (Phase 1) + DEC-426 (Phase 2) + "
    "DEC-427 (Phase 3 marginal heatmap) + DEC-428 (Phase 4 3D combined) + "
    "DEC-429 (Phase 5 lookup table) + DEC-430 (Phase 6 dashboard viz) + "
    "DEC-431 (Phase 7 validation). All phases SPEC_READY; full impl deferred "
    "to Sprint 8+ cube build-out."
)

# DEC-427 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# Cube Phase 3 marginal heatmap analysis (Approach A) config.
DEC_427_HEATMAP_DIMENSIONS_PER_PAIR = 2  # 2D slicing for statistical validity
DEC_427_OUTPUT_FORMAT = "marginal_best_exit_per_strategy_per_dimension"

# DEC-430 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# Cube Phase 6 Dashboard 1 visualization config.
DASHBOARD_1_FRAMEWORK = "streamlit"
DASHBOARD_1_PATH = "dashboard_1_cube_explorer/"
DASHBOARD_1_FEATURES = (
    "pick_2_dims_heatmap",
    "pick_3_dims_3d_scatter",
    "per_cell_drill_down",
    "filter_strategy_subset",
)

# DEC-437 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# Property-based testing via hypothesis library (Layer 3 catch defense).
PROPERTY_BASED_TESTING_LIB = "hypothesis"
PROPERTY_BASED_TESTING_DEFENSE_LAYER = 3
PROPERTY_BASED_TESTING_TARGETS = (
    "exit_strategies",       # all exits respect R:R minimum DEC-353
    "regime_filter",         # classify_regime never returns None
    "position_sizing",       # never produces negative or >100% allocation
    "trade_log_writer",      # never drops trades silently
)

# DEC-438 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 67 2026-05-11.
# Characterization / golden-master tests (Layer 4 catch defense).
GOLDEN_MASTER_TESTING_DEFENSE_LAYER = 4
GOLDEN_MASTER_TESTING_ARTIFACT_DIR = "backtest/tests/golden_masters"
GOLDEN_MASTER_TESTING_DIFF_TOLERANCE = 0.0  # byte-identical per DEC-232

# DEC-439 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12
# (owner-approved Path C PARTIAL-SPEC-ONLY closure batch 4 -- FINAL).
# Differential testing Layer 5 of multi-layer catch defense.
DIFFERENTIAL_TESTING_DEFENSE_LAYER = 5
DIFFERENTIAL_TESTING_TARGETS = (
    "fundamentals_polygon_vs_sec_xbrl",  # joint DEC-456 SEC EDGAR reference
    "ohlcv_yfinance_vs_polygon",
    "regime_classifier_v1_vs_multi_input",
)

# DEC-467 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# OurAgentState schema extension + LangGraph state injection points.
OUR_AGENT_STATE_NEW_FIELDS = (
    "rules_only_rationale",
    "agent_overlay_rationale",
    "risk_context_dict",
    "regime_state_dict",
    "tier_pre_agent",
    "tier_post_agent",
    "ab_arm_label",
)
OUR_AGENT_STATE_EXTENDS = "tradingagents.AgentState"

# DEC-478 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# Polygon Stocks Starter tier selection (cross-ref to DEC-441 + DEC-479).
POLYGON_TIER_SELECTED = "stocks_starter"
POLYGON_TIER_HISTORY_YEARS = 5  # May 2021 -> May 2026

# DEC-485 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# Earnings transcripts dropped from Stage 2 scope.
EARNINGS_TRANSCRIPTS_STAGE_2_ENABLED = False
EARNINGS_TRANSCRIPTS_DROP_REASON = (
    "FMP free tier 250 calls/day insufficient for 1937-ticker backtest scale. "
    "Phase 1B+ revisit pending paid-tier cost-benefit analysis."
)

# DEC-490 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# Phase 1A skipped strategies enumerated.
PHASE_1A_SKIPPED_STRATEGIES = (
    "fundamentals_quality_screen",   # blocked on DEC-484 (SEC EDGAR Sprint 4)
    "earnings_call_sentiment",        # blocked on DEC-485 (transcripts dropped)
)
PHASE_1A_SKIPPED_REASONS = {
    "fundamentals_quality_screen": "DEC-484 financials deferred to Sprint 4 SEC EDGAR",
    "earnings_call_sentiment":     "DEC-485 transcripts dropped from Stage 2",
}

# DEC-496 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# Tier 3 momentum watchlist methodology: Jegadeesh-Titman 12-1 month.
TIER_3_MOMENTUM_METHODOLOGY = "jegadeesh_titman_12_1"
TIER_3_MOMENTUM_LOOKBACK_DAYS = 252  # ~12 months trading days
TIER_3_MOMENTUM_SKIP_DAYS = 21       # ~1 month skip (avoid short-term reversal)
TIER_3_MOMENTUM_RISK_ADJUSTMENT = False  # raw return ranking
TIER_3_MOMENTUM_TIE_BREAKERS = ("vol_ascending", "adv_descending")

# DEC-501 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# Polygon Options NOT upgraded -- SUPERSEDED by DEC-506 (re-enabled in
# Stage 2 per owner directive 2026-05-05). This constant records the
# original deferral decision for historical context.
DEC_501_ORIGINAL_DEFERRAL = "Polygon Options NOT upgraded (Q1=C 2026-05-05)"
DEC_501_SUPERSEDED_BY = "DEC-506"

# DEC-502 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# Quiver Trader-tier agent-input expansion -- 8 endpoint groups +
# Apewisdom + pytrends supplement.
QUIVER_TRADER_TIER_ENDPOINT_GROUPS = (
    "congresstrading",
    "senatortrading",
    "sec13f_sec13fchanges",
    "insidertrading",
    "wsbtrading",
    "patentmomentum",
    "corporatedonors",
    "lobbying_lawsuits",
)
QUIVER_SUPPLEMENTAL_SOURCES = ("apewisdom", "pytrends")

# DEC-506 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 68 2026-05-12.
# Polygon Options + Ortex confirmed Stage 2 in-scope (SUPERSEDES DEC-501
# deferral; corrects DEC-468 Sprint-7 timing to Stage 2 now).
POLYGON_OPTIONS_STAGE_2_IN_SCOPE = True
ORTEX_SHORT_INTEREST_STAGE_2_IN_SCOPE = True
DEC_506_SUPERSEDES = ("DEC-501",)
DEC_506_CORRECTS = ("DEC-468 timing Sprint 7 -> Stage 2",)

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
SHORT_ANNUAL_BORROW_RATE = 0.005   # decimal: 0.005 = 0.5% per year  # BUG-081
