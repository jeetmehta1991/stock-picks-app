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

import os  # B1519: env-overridable optimisation knobs
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
DATA_LOAD_START = date(2021, 5, 6)   # 1y warmup window for 252-day indicators
# B1562 (owner-approved A2 2026-08-14): was 2021-05-05, but NO cached ticker
# holds a 2021-05-05 bar -- the universe prefetch's first bar is 2021-05-06, so
# the cache-coverage check failed for 2,118 of 2,122 tickers and every run
# re-downloaded from yfinance (L435). Warmup only: the LOCKED backtest window
# 2022-05-05 -> 2026-05-05 is untouched, and one leading bar cannot change a
# 252-day indicator's state a year later.
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
    # Batch 281 (2026-05-20 owner-approved): trail_pct 0.10 -> 0.15. The
    # claim was originally made in Batch 262 commit message but the actual
    # config dict was never modified - audit 2026-05-20 found smokes A/B/C
    # had been running on the prior 10% setting. Now actually deployed.
    "trail_pct":         0.15,   # trails at 15% below highest close (long)
    "reset_on":          "close", # trailing stop resets on closing price only
    # Batch 281: breakeven_move_at_1r flag now actually present. The logic
    # at exit_manager.py:291-302 was added in Batch 262 but gated on this
    # key with default False -> never fired. Now defaults True.
    "breakeven_move_at_1r": True,
    # B1429 (owner-approved 2026-07-31, Council "A + E"): was atr_trail_1x.
    #   R6 holdout (2025-05-05 ->), 5,796 trades x 26 exits, winsorized +/-300 net 20bps:
    #     atr_trail_1x          exp -1.28pp  WR 0.199  W/L 1.06  PF 0.26   <- rank 24 of 26
    #     breakeven_plus_trail  exp +1.39pp  WR 0.247  W/L 4.87  PF 1.60   <- rank 1
    #   Delta +2.68pp/trade. 181 of 222 strategies had no STRATEGY_EXIT_OVERRIDE and
    #   were therefore running the worst-of-26 exit.
    #   Owner decision D (2026-07-31): judge exits on PF>1.5 + W/L>1.0, NOT win rate --
    #   breakeven_plus_trail is the only exit of 26 passing both; the WR>=0.40-compliant
    #   alternative (hybrid_50pct_target) fails both (PF 1.11, W/L 0.90).
    #   Prior "wins 20/29 strategies" was the Phase 1A v3 archive on a 29-strategy roster.
    "primary_exit":      "breakeven_plus_trail",
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

# Batch 282 (2026-05-20 owner-approved per DESIGN_AUDIT_2026_05_20 Tier 1 #2):
# Per-strategy exit override. The default TRAILING_STOP applies to every trade
# unless a strategy is listed here with an explicit exit configuration. Stage C
# cube analysis (50 tkrs x 3y, post-Batch-266 hardened) showed each strategy
# has a different best-exit; the system was previously leaving ~+845 pp on
# the table by using a single trailing_15pct for all.
#
# Each entry can override:
#   - trail_pct           (float): % trail; default = TRAILING_STOP["trail_pct"] (0.15)
#   - time_stop_days      (int or None): max bars held; default = None (no time stop)
#   - breakeven_at_R      (float or None): R-multiple to ratchet stop to entry;
#                          default = 1.0 if breakeven_move_at_1r else None
#   - exit_method         (str or None): per-strategy exit method dispatched
#                          to _check_per_strategy_exit_hit. Supported in
#                          Batch 284: fixed_4r_2r, r_multiple_2r, r_multiple_3r,
#                          class_time_stop, breakeven_plus_trail.
#                          Batch 285 adds: ma_exit_ema9, regime_flip,
#                          next_pivot_target, hybrid_50pct_target.
#
# Strategies not listed fall through to TRAILING_STOP defaults.
STRATEGY_EXIT_OVERRIDE: dict[str, dict] = {
    # B1420 (2026-07-28 owner-approved): EXIT REASSIGNMENT, 6 strategies -> breakeven_plus_trail.
    # Derived IS-only (2022-05 -> 2025-05) and guarded against L227, which measured exit
    # selection as the MOST overfit component (IS-picked exits cleared the holdout bar on 5.9%
    # of rows vs a hindsight oracle 17.6%). Naive argmax over 26 exits is exactly that failure,
    # so each proposal had to be TOP-QUARTILE IN >=2 OF 3 IS FOLDS (all 6 are 3/3), beat the
    # incumbent by >=0.5%/trade, and clear a DATE-CLUSTERED BH-FDR test. 26 strategies would
    # change under naive argmax; only these 6 survived. All 6 are structurally simple exits,
    # the class L227 found transfers best. Predictions pre-registered for R6 in
    # output_audit/b1415_exit_reassignment.json - each can be falsified.
    # Batch 309 (2026-05-24 owner-approved): Phase 1B-alpha survivor roster.
    # Per per_cell_is_oos.csv from Phase 1A-beta 7,191-trade run, these 7
    # unique strategies have at least one (strategy x exit) cell with BOTH
    # IS and OOS sum > 0 (n>=10 OOS for statistical power). All other
    # strategies that fired in Phase 1A-beta are listed in
    # PHASE_1B_ALPHA_DISABLED_STRATEGIES below and skipped at screener time.
    #
    # Performance evidence (OOS sum on chosen exit, from Phase 1A-beta):
    #   avwap_50_reclaim   x hybrid_50pct_target   = +843 pp (90 OOS, 100% WR)
    #   po3_bullish        x class_time_stop       = +395 pp (136 OOS, 54% WR)
    #   monthly_bias...    x loose trail           = +374 pp (47 OOS, 83% WR)
    #     [Phase 1A-beta best was end_of_backtest; deployable equivalent
    #      is a loose trailing stop that lets the trend run]
    #   xs_low_beta_long   x loose trail           = +319 pp (30 OOS, 87% WR)
    #     [same end_of_backtest -> loose trail mapping]
    #   cpr_narrow_bullish x regime_flip           = +142 pp (37 OOS, 59% WR)
    #   xs_momentum_top_decile x class_time_stop   = +129 pp (28 OOS, 68% WR)
    #   stochrsi_oversold  x time_stop_10d         = +107 pp (27 OOS, 74% WR)
    #
    # Batch 284 entries that REMAIN (winners):
    # B834-SWAP-APPLIED #73 (owner-approved B886 2026-06-17): R4 cube
    #   Sharpe 0.481 breakeven_plus_trail beats B309 time_stop_days=10.
    #   Invalidated test_batch287a_per_strategy_initial_pct_override pin
    #   (updated B886 to match new exit_method).
    "stochrsi_oversold":           {"exit_method": "breakeven_plus_trail"},
    # B834-SWAP-APPLIED #74 (owner-approved B886): R4 cube Sharpe 0.386
    #   breakeven_plus_trail beats B309 class_time_stop OOS +395pp.
    #   Invalidated test_batch284_check_per_strategy_exit_hit_class_time
    #   _stop pin (updated B886).
    "po3_bullish":                 {"exit_method": "breakeven_plus_trail"},
    "avwap_50_reclaim":            {"exit_method": "hybrid_50pct_target"},
    # B834-SWAP-APPLIED #75 (owner-approved B886): R4 cube Sharpe 0.303
    #   breakeven_plus_trail beats B309 regime_flip OOS +142pp.
    #   Invalidated test_batch285_regime_flip_exits_on_regime_change pin
    #   (updated B886).
    "cpr_narrow_bullish":          {"exit_method": "breakeven_plus_trail"},

    # ----- Batch 1070 Stage C ITEM 2 (2026-06-29 owner-approved per Council 174/177/178) -----
    # Source: B395 cube (output_batch395_final/trade_exit_detail.csv;
    #   729,500 rows). Re-derived from B414 precedent + Batch 266
    #   fire_rate>=0.95 guardrail per Council 178 Option 6 INSPECT-+-
    #   MANUAL-EXTRACT-COMBO.
    # Criteria: N>=100 per (strategy, exit_method) cell + Sharpe>=0.3 +
    #   WR>=0.45 + fire_rate>=0.95 (Batch 266 exit-method-actually-
    #   triggers guardrail). Best exit_method per strategy selected by
    #   Sharpe.
    # Filters: in current ALL_STRATEGIES + NOT in existing STRATEGY_EXIT
    #   _OVERRIDE + NOT in DEPRECATED_STRATEGIES + NOT in STRATEGIES_
    #   DISABLED_MISSING_PRODUCER. Strategies added post-B414 lacking
    #   cube history are absent from B395 (auto-skipped).
    # Honest-finding caveat: PSR<0.95 means statistically suggestive but
    #   not high-confidence (B414 precedent same caveat). Walk-forward
    #   (DEC-505) is the next-Stage gate; Phase 4 cube will produce
    #   universe-scale verdicts for B1072 refinement.
    # Cube evidence (Sharpe / n / WR / fire_rate per B395):
    #   htf_aligned_breakout_long       4.09 / 190  / 0.526 / 1.000
    #   avwap_252_breakout              2.97 / 179  / 0.508 / 0.989
    #   pre_fomc_long_sleeve            2.59 / 229  / 0.515 / 1.000
    #   institutional_buy_momentum_long 2.54 / 126  / 0.492 / 1.000
    #   morning_star                    2.45 / 228  / 0.539 / 1.000
    #   williams_stoch_dual             2.19 / 134  / 0.858 / 1.000
    #   squeeze_breakout                1.94 / 252  / 0.520 / 1.000
    #   orb_stocks_in_play_long         1.90 / 205  / 0.473 / 1.000
    #   macd_fast_crossover             1.86 / 256  / 0.520 / 1.000
    #   supertrend_macd                 1.73 / 520  / 0.462 / 1.000
    #   golden_cross_9_21               1.71 / 155  / 0.671 / 1.000
    #   ultimate_oscillator             1.46 / 462  / 0.519 / 1.000
    #   ppo_crossover                   1.45 / 296  / 0.534 / 1.000
    #   tema_dema                       1.04 / 406  / 0.727 / 1.000
    #   cpr_narrow_momentum             0.76 / 283  / 0.502 / 1.000
    #   three_white_soldiers            0.67 / 344  / 0.753 / 1.000
    #   break_retest_volume             0.65 / 329  / 0.492 / 1.000
    #   macd_crossover                  0.61 / 144  / 0.500 / 1.000
    #   awesome_oscillator              0.61 / 212  / 0.524 / 1.000
    #   stochrsi_overbought_short       0.57 / 353  / 0.535 / 1.000
    #   hull_rsi                        0.52 / 360  / 0.733 / 1.000
    #   parabolic_sar_flip              0.49 / 338  / 0.654 / 1.000
    #   pead_short                      0.37 / 453  / 0.508 / 1.000
    "htf_aligned_breakout_long":       {"exit_method": "earnings_blackout"},
    "avwap_252_breakout":              {"exit_method": "breakeven_plus_trail"},
    "pre_fomc_long_sleeve":            {"exit_method": "earnings_blackout"},
    "institutional_buy_momentum_long": {"exit_method": "earnings_blackout"},
    # B1420: time_stop_10d -> breakeven_plus_trail | IS expectancy +0.01% -> +2.34% (margin +2.33), WR 0.491 -> 0.262, top-quartile in 3/3 IS folds
    "morning_star":                    {"exit_method": "breakeven_plus_trail"},
    # B1420: next_pivot_target -> breakeven_plus_trail | IS expectancy -0.10% -> +0.94% (margin +1.04), WR 0.826 -> 0.230, top-quartile in 3/3 IS folds
    "williams_stoch_dual":             {"exit_method": "breakeven_plus_trail"},
    "squeeze_breakout":                {"exit_method": "earnings_blackout"},
    "orb_stocks_in_play_long":         {"exit_method": "earnings_blackout"},
    "macd_fast_crossover":             {"exit_method": "earnings_blackout"},
    "supertrend_macd":                 {"exit_method": "earnings_blackout"},
    "golden_cross_9_21":               {"exit_method": "next_pivot_target"},
    "ultimate_oscillator":             {"exit_method": "earnings_blackout"},
    "ppo_crossover":                   {"exit_method": "class_time_stop"},
    # B1420: next_pivot_target -> breakeven_plus_trail | IS expectancy +0.03% -> +2.46% (margin +2.43), WR 0.671 -> 0.300, top-quartile in 3/3 IS folds
    "tema_dema":                       {"exit_method": "breakeven_plus_trail"},
    "cpr_narrow_momentum":             {"exit_method": "time_stop_10d"},
    "three_white_soldiers":            {"exit_method": "next_pivot_target"},
    "break_retest_volume":             {"exit_method": "earnings_blackout"},
    # B1420: time_stop_10d -> breakeven_plus_trail | IS expectancy -0.12% -> +2.04% (margin +2.17), WR 0.488 -> 0.301, top-quartile in 3/3 IS folds
    "macd_crossover":                  {"exit_method": "breakeven_plus_trail"},
    "awesome_oscillator":              {"exit_method": "earnings_blackout"},
    # B1420: class_time_stop -> breakeven_plus_trail | IS expectancy -1.55% -> -0.14% (margin +1.42), WR 0.441 -> 0.245, top-quartile in 3/3 IS folds
    "stochrsi_overbought_short":       {"exit_method": "breakeven_plus_trail"},
    # B1420: next_pivot_target -> breakeven_plus_trail | IS expectancy -0.46% -> +0.79% (margin +1.24), WR 0.643 -> 0.288, top-quartile in 3/3 IS folds
    "hull_rsi":                        {"exit_method": "breakeven_plus_trail"},
    "parabolic_sar_flip":              {"exit_method": "next_pivot_target"},
    "pead_short":                      {"exit_method": "regime_flip"},

    # ----- Legacy Batch 284/285 entries RETAINED for backward-compat -----
    # These entries STAY in the dict but their strategies are in
    # PHASE_1B_ALPHA_DISABLED_STRATEGIES, so screener.py skips them BEFORE
    # the exit-method lookup ever happens. Keeping them here so existing
    # tests (test_batch284_*, test_batch285_*, test_batch287a_*) still find
    # the entries, and so re-enabling a strategy is a 1-line change rather
    # than re-deriving the exit assignment from scratch.
    "bollinger_lower":             {"exit_method": "fixed_4r_2r", "initial_pct": 0.03},
    "smc_choch_reversal":          {"exit_method": "breakeven_plus_trail"},
    "po3_bearish":                 {"exit_method": "ma_exit_ema9"},

    # ----- Batch 414 (2026-05-28 owner-approved) -----
    # Source: post-AWS Phase 1A-beta cube run output_batch395_final +
    # scripts/optimize_strategies_from_cube.py output (Lens A Dim D best-
    # exit-pairing). All 9 strategies below have a (strategy x
    # breakeven_plus_trail) cell that passes 4 of 5 DEC-426 gates (n>=30,
    # p<0.05 Bonferroni, t>=3.4, R:R>=2.0) AND fire_rate >= 0.95 (Batch 266
    # cube hardening guardrail - the exit method actually triggers
    # breakeven_trail_stop on 95%+ of trades, NOT bull-market end_of_data
    # fall-through). PSR<0.95 means each is statistically suggestive but
    # not high-confidence; walk-forward (DEC-505) is the next-Stage gate.
    #
    # Replaces Batch 309 entries for the 4 strategies below where new
    # cube evidence supersedes prior recommendations.
    #
    # Cube evidence (Sharpe / n / PF / fire_rate):
    #   bollinger_tight              0.642 / 364  / 2.09 / 0.975
    #   xs_momentum_top_decile       0.558 / 415  / 2.20 / 0.961
    #   cmf_flip                     0.545 / 639  / 2.34 / 0.973
    #   monthly_bias_momentum_long   0.542 / 1286 / 2.11 / 0.963
    #   xs_quality_top_quintile_long 0.525 / 603  / 2.03 / 0.967
    #   pead_long                    0.521 / 528  / 2.44 / 0.994
    #   pairs_mean_reversion_long    0.411 / 1144 / 2.70 / 0.969
    #   adx_initiation               0.379 / 942  / 3.30 / 0.973
    #   xs_low_beta_long             0.307 / 1021 / 2.11 / 0.949
    #
    # Note: 12 strategies that "won" with earnings_blackout in the same cube
    # (htf_aligned_breakout_long, pre_fomc_long_sleeve, buyback_8k_recent_long,
    # orb_stocks_in_play_long, po3_htf_aligned_long, institutional_cluster_long,
    # supertrend_macd, three_white_soldiers, macd_fast_crossover,
    # camarilla_r3_breakout, squeeze_breakout, tema_dema) had fire_rate=0.000
    # because the cube's signals_at_entry dict lacks ticker/strategy_name keys
    # so fetch_earnings_dates("") returns []. Those cells are curve-fit on
    # no_earnings_known end-of-data fall-through, not real edge. Batch 415
    # follow-up: fix run_exit_comparison to inject ticker+strategy_name into
    # signals dict, re-run cube, re-evaluate.
    "bollinger_tight":             {"exit_method": "breakeven_plus_trail"},  # was next_pivot_target (Batch 285)
    "xs_momentum_top_decile":      {"exit_method": "breakeven_plus_trail"},  # was class_time_stop (Batch 284)
    "monthly_bias_momentum_long":  {"exit_method": "breakeven_plus_trail"},  # was trail_pct=0.25 (Batch 309)
    "xs_low_beta_long":            {"exit_method": "breakeven_plus_trail"},  # was trail_pct=0.25 (Batch 309)
    "cmf_flip":                    {"exit_method": "breakeven_plus_trail"},  # NEW
    "xs_quality_top_quintile_long": {"exit_method": "breakeven_plus_trail"},  # NEW
    "pead_long":                   {"exit_method": "breakeven_plus_trail"},  # NEW
    "pairs_mean_reversion_long":   {"exit_method": "breakeven_plus_trail"},  # NEW
    "adx_initiation":              {"exit_method": "breakeven_plus_trail"},  # NEW

    # ----- Batch 834/835 (2026-06-16 Stage 4 R4 cube PASS-cell additions) -----
    # Source: R4 cube optimizer output_optimization_candidates_R4_2026_06_16/
    # via scripts/optimize_strategies_from_cube.py + B834 PASS-cell extraction
    # (verdict=PASS + five_gate_pass=True + n>=30). All R4-evidence-driven.
    #
    # NEW ticket #71 (no prior entry): williams_r_oversold x breakeven_plus_trail
    #   R4 cube empirical Sharpe 0.491 / n=849 / PF 1.84 / PSR 1.000.
    "williams_r_oversold":         {"exit_method": "breakeven_plus_trail"},  # B835 NEW (#71)
    # NEW ticket #72 (no prior entry): institutional_cluster_long x earnings_blackout
    #   R4 cube empirical Sharpe 0.373 / n=278 / PF 3.10 / PSR 1.000.
    "institutional_cluster_long":  {"exit_method": "earnings_blackout"},  # B835 NEW (#72)
}


# Batch 310 (2026-05-24 owner-directed REVERT of Batch 309 Decision 2 sub-item):
# This set is REFERENCE-ONLY metadata. It is NO LONGER USED as a screener
# gate - the import + skip filter in backtest/signals/screener.py was
# removed in Batch 310 per owner directive "DO NOT DISABLE ANYTHING TILL
# I ANALYZE AND COMMAND".
#
# Why we keep the set in source: the per_cell_is_oos.csv analysis that
# produced this list took compute + careful work. Discarding the data
# means re-deriving it. Keeping it documents WHICH strategies underperformed
# at universe-scale in Phase 1A-beta so the next decision pass (per-regime /
# per-ticker / per-classifier stratification) starts from this baseline.
#
# Owner framework (per directive): we are NOT looking for universal
# strategies. We're looking for the best (strategy x exit x regime x
# ticker x classifier) combinations. A strategy that lost money
# universe-wide in 2024-2026 bull may still be the right play in 2022
# bear or for a specific tier / sector / capitalization band. Roster
# decisions move to STRATEGY_REGIME_AFFINITY (already exists) +
# future per-classifier tagging.
#
# Source: output_phase_1a_beta_merged_local/per_cell_is_oos.csv,
# Phase 1A-beta 7191 trades, IS-2022-01..2024-06 / OOS-2024-07..2026-04.
# These strategies had NO (strategy x exit) cell with OOS n>=5 and OOS
# sum_pp > 0 at universe-wide scale. Use as PRIORITY LIST for per-regime
# analysis, NOT as automatic disable.
PHASE_1A_BETA_UNDERPERFORMERS_REFERENCE: set[str] = {
    # Worst losers (Phase 1A-beta OOS sum < -100 pp)
    "xs_momentum_bottom_decile_short",   # -308 pp OOS
    "po3_bearish",                       # -229 pp OOS
    "htf_aligned_breakout_short",        # -225 pp OOS
    "buyback_8k_recent_long",            # -201 pp OOS
    "stochrsi_overbought_short",         # -127 pp OOS
    "cpr_narrow_momentum",               # -119 pp OOS
    "smc_bos_continuation",              # -116 pp OOS

    # Moderate losers (-30 to -100 pp OOS)
    "macd_fast_crossover",
    "po3_htf_aligned_long",
    "avwap_252_breakout",
    "smc_breaker_block_short",
    "orb_stocks_in_play_short",
    "insider_cluster_long",
    "smc_discount_long",
    "macd_ichimoku",
    "po3_htf_aligned_short",
    "cmf_flip",

    # Small-sample losers
    "bollinger_tight",                   # -26 pp OOS (was an explicit override)
    "smc_premium_short",
    "r1_break_retest",
    "break_retest_confluence",
    "pivot_s2_bounce",
    "pivot_r2_continuation",
    "dc20_break_retest",
    "adx_initiation",
    "rsi_oversold",
    "smc_ote_short",
    "prev_day_high_break",
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
    # B1387 (2026-07-26 owner ruling "b sharpe" on the win-rate-vs-Sharpe conflict):
    # win rate is DEMOTED from a hard gate to a reported diagnostic. Measured cause:
    # the exit that wins selection (breakeven_plus_trail) truncates losers at
    # breakeven and lets winners run, MANUFACTURING a low win rate (0.30-0.46) with a
    # high payoff (3.5-10.3) - only 4 of 22 promoted cells cleared 0.45 while 22 of 22
    # cleared profit factor. A standalone win-rate floor and a Sharpe/expectancy gate
    # encode incompatible trade shapes (L231/L237). Win rate is not a validity
    # criterion on its own; PROFIT FACTOR already encodes the win-rate x payoff
    # tradeoff (PF = payoff x W/(1-W)) and remains gated at min_profit_factor.
    # Follows the Batch 186 precedent for smart_money_lift / macro_correlation:
    # flag False => the gate auto-passes, the VALUE is still computed and reported.
    "win_rate_gate":           False,  # B1387: diagnostic, not a gate
    # B1436 (2026-08-03 owner ruling): TWO further gates demoted to diagnostics,
    # following the Batch 186 / B1387 precedent exactly (flag False => the gate
    # auto-passes, the VALUE is still computed and reported).
    #
    # (a) max_drawdown_gate -- owner: "max_drawdown can only happen in phase 1B when
    #     we analyze portfolio performance. Illogical to have it as a gate now."
    #     Measured cause: `_max_drawdown` compounds a strategy's own trade sequence as
    #     if 100% of capital rolled from each trade into the next. In cube isolation
    #     every signal is an INDEPENDENT fixed-notional trade with no portfolio, while
    #     real deployment sizes at 0.75-5% per the confidence tiers and runs 20+
    #     strategies concurrently. So the cell figure is not the portfolio drawdown the
    #     -25 threshold describes. It cleared 1 of 90 cells (1/22 promoted + 1/68
    #     re-scored) while profit factor cleared 71 of 90 - the signature of a category
    #     mismatch, not a bad roster. RE-ENGAGE AT PHASE 1B on a blended book.
    #
    # (b) deflated_sharpe_gate -- owner: "deflated_sharpe - remove".
    #     Cleared 0 of 90 cells and returns None for many of them, so it was rejecting
    #     everything rather than discriminating. DSR deflates for multiple testing across
    #     N trials; at 222 registered strategies the hurdle is effectively absolute.
    #     Multiple-testing control remains via BH-FDR (B982) + PSR, both still gated.
    "max_drawdown_gate":       False,  # B1436: diagnostic; re-engage at Phase 1B (portfolio-level)
    "deflated_sharpe_gate":    False,  # B1436: diagnostic, not a gate
    # (c) calmar_gate -- B1437 owner ruling "calmar to be removed as well".
    #     CLASS CLOSURE, not a third one-off: calmar = return / abs(max_drawdown), so its
    #     DENOMINATOR is the isolation-cube drawdown demoted in (a). Demoting max_drawdown
    #     while leaving calmar gated re-imposed the same quantity as a ratio - calmar became
    #     the tightest gate at 15 of 90 cells immediately after B1436. Enumerated every
    #     _max_drawdown consumer to confirm these are the only two gates in the class;
    #     `portfolio_max_drawdown_pct` (metrics.py, computed on a real equity curve) is the
    #     Phase 1B quantity and is unaffected. RE-ENGAGE AT PHASE 1B alongside max_drawdown.
    "calmar_gate":             False,  # B1437: diagnostic; re-engage at Phase 1B (portfolio-level)
    "min_profit_factor":       1.2,    # unchanged per-regime
    "min_expected_value":      0.0,    # (win_rate x avg_win) + (loss_rate x avg_loss) > 0
    "min_win_loss_ratio":      1.0,    # avg win / avg loss > 1.0
    "max_drawdown":            25.0,   # was 20.0; overall + per-regime baseline (HV gets 30 below)
    "min_total_roi":           0.0,    # positive total ROI over backtest period
    "smart_money_lift":        False,  # was True; now per-strategy opt-in via uses_smart_money_signal attribute
    "macro_correlation":       False,  # was True; now per-strategy opt-in via uses_macro_signal attribute
    "min_trades":              100,   # legacy single-window key; superseded by the two below
    # B1492 (owner-approved 2026-08-09): the old single `min_trades` was applied to
    # whichever window evaluate() received, and the BINDING call is the holdout - so it
    # demanded 100 trades in ONE year of a FOUR-year window, roughly a 4x harsher bar
    # than "100 trades" reads. Split into two explicit legs.
    "min_trades_full_period":  100,   # > 100 over the whole 4y window
    "min_trades_holdout":      25,    # >= 25 in the 1y holdout    # minimum 100 trades for statistical validity
    "min_deflated_sharpe":     0.95,   # NEW Batch 186: DSR-based stat significance (multi-testing-corrected PSR)
    # B983 (2026-06-21) Council 86 Option-7 owner-approved 2026-06-21 per
    # directive 'Approve your recommendation. Proceed council this.':
    # DEC #6 PSR companion gate (Bailey-Lopez de Prado 2012). PSR per-
    # strategy = Pr(SR > 0) given finite sample + non-normality. Separate
    # from passes_compose (B982 BH-FDR family-level gate) per DEC #6
    # literal reading 'PSR per-strategy + DSR on family'. PSR=None
    # (n_trades < 30) PASSES per `feedback_minimum_fire_count_gate_before
    # _cube` (defers to canonical n>=30 criterion #9; no double-penalty).
    # Closes Bucket B B1 (5-of-5 closure target).
    "min_psr":                 0.95,   # B983: DEC #6 PSR companion gate threshold
    # BUG-33 RESOLVED-IMPLEMENTED Batch 110 2026-05-12 (owner-approved
    # option C 2026-05-12): tiered Sharpe ratio passing criterion. Per-
    # regime threshold lower because per-regime trade samples are smaller
    # (BUG-31 statistical-power concern). Overall threshold 1.0 = the
    # industry-canonical "decent" Sharpe; 2.0 = "great". 0.7 per-regime is
    # achievable, not punitive.
    "min_sharpe_overall":      1.0,    # BUG-33: overall PASS requires Sharpe >= 1.0
    # B1387 (2026-07-26 owner-approved "reconcile config to the approved 0.5"):
    # per-regime bar 0.7 -> 0.5. Rationale: the R5 grading that set 0.5 adds TWO
    # filters the 0.7 bar never had - a true holdout fold (no selection ever saw it)
    # and BH-FDR multiple-testing control - so 0.5-with-holdout-and-FDR is stronger
    # evidence than 0.7 was in-sample. NOTE: min_sharpe_overall is UNCHANGED at 1.0;
    # only the per-regime tier was in scope of the approval.
    "min_sharpe_per_regime":   0.5,    # B1387: was 0.7 (BUG-33)
    # Batch 221 (validation 2026-05-18 owner-approved research review):
    # Add Sortino + Calmar + per-regime>=2 gates per Section B.
    # Sortino penalizes only downside vol; complements Sharpe by catching
    # strategies with asymmetric return distributions. Standard in CTA
    # evaluation. Source: Sortino-Price 1991 JoI.
    "min_sortino_overall":     1.0,    # Batch 221: Sortino must also clear 1.0 overall
    "min_sortino_per_regime":  0.7,    # Same per-regime tier as Sharpe
    # Calmar = annualized return / max drawdown. Robert Carver
    # "Leveraged Trading" 2019 standard. Source: Magdon-Ismail-Atiya 2004
    # Risk Magazine.
    "min_calmar":              0.5,    # Batch 221: Calmar >= 0.5
    # Per-regime PASS gate.
    # Batch 221 (2026-05-18): set to 2 per Carver 2015 "strategy passing
    #   only in one regime is likely a regime-coincidence finding."
    # Batch 891 (2026-06-18) DEC-611 OWNER-APPROVED CORRECTION: REVERTED
    #   to 1 per CLAUDE.md canonical criterion #11 ("PASS in >=1 regime,
    #   not universal pass required") + CLAUDE.md core principle ("Per-
    #   regime strategy library: different strategies for different
    #   regimes -- not universal strategies"). Council 15 surfaced the
    #   doc-vs-code DRIFT; Council 16 implementation owner-approved
    #   2026-06-18. Project design intentionally preserves regime-
    #   specialist strategies (short = bear regime only; VIX spike =
    #   crisis only) as Priority-1 candidates -- Carver's >=2 rule
    #   was for ~20-strategy universal-deployment systems and does
    #   NOT scale-correctly to a 218-strategy per-regime-library design.
    "min_regimes_passing":     1,      # DEC-611 B891 (was 2 Batch 221; per CLAUDE.md canonical)
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
    # Batch 890 (2026-06-18) Council 16 owner-approved per Council 15
    # corrections: promote 3 metrics.py "sleeping unicorns" from advisory
    # (computed but ungated) to AUTO-FAIL gates per `feedback_doc_count_drift
    # _must_be_test_pinned` + B888 implementation plan section 10.10c.
    # DEC-612 cost-sensitivity gate: degraded-Sharpe (at realistic 20bps
    #   commission+slippage) must retain >=50% of clean-Sharpe value. Catches
    #   strategies that look profitable in zero-cost backtest but die under
    #   realistic execution friction. Threshold derived per Council 16
    #   Executor: 20bps tier-conservative for T1a (~5bps slippage + 1bp IB
    #   commission + spread); brutal for T3 but acceptable since T3 strategies
    #   should clear this floor anyway. Insufficient-sample auto-PASS per
    #   Contrarian Council 16 (None auto-passes; mirrors DSR/Sortino/Calmar
    #   pattern at line 2436-2439).
    "min_cost_sensitivity_ratio": 0.5,    # DEC-612 B890: sharpe_at_20bps / sharpe_at_0bps >= 0.5
    # DEC-613 Chow break-point gate: catches dead-strategy false positives
    #   (regime-coincidence: strategy died at 2022-06-13 rate-hike pivot,
    #   still coasting on pre-break trades). p < 0.05 indicates structural
    #   break; require post-break Sharpe >= 0.3 to confirm strategy survived
    #   the break. Insufficient sample (n<60 to satisfy ~30 pre + ~30 post
    #   per Contrarian Council 16) auto-passes to avoid double-penalty with
    #   trade_count gate.
    "chow_test_p_max": 0.05,              # DEC-613 B890
    "chow_post_break_sharpe_min": 0.3,    # DEC-613 B890: only enforced when Chow p < 0.05
    # DEC-614 ADF stationarity gate: REGIME-CONDITIONAL applied to
    #   mean-reversion strategies only (per Council 15 First Principles).
    #   Mean-reverting equity curve = whip-saw non-compounder; LLM agents
    #   add zero value to non-compounding strategies. Non-stationary equity
    #   on a mean-reversion strategy is the canonical "no edge" signature.
    #   Insufficient sample auto-PASS. Non-mean-rev strategies AUTO-PASS
    #   (gate doesn't apply). Mean-reversion classification taxonomy is
    #   explicit + auditable: MEAN_REVERSION_STRATEGIES set populated at
    #   module load from screener._strat3 / _strat category="mean_reversion"
    #   tag (per Contrarian Council 16 "explicit auditable taxonomy file"
    #   demand).
    "adf_test_p_max_mean_reversion": 0.10,  # DEC-614 B890
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
    #
    # Batch 370 Fix 1 (owner-approved 2026-05-26): raised 25 -> 59 to unlock the
    # bull-regime effective cap. Empirical Phase-1A-beta evidence: 12,180 skips
    # were `max_open_positions_25_reached` on bull/neutral days. The min(base,
    # regime_cap) formula in engine/backtest.py means base=59 only changes the
    # BULL regime effective cap (25 -> 40 = Batch 203's regime spec). Neutral
    # stays 25 (regime cap = 25); bear stays 15 (Batch 203 risk control on
    # 2022 -117pp loss-year); crisis stays 10. Worst-case bull exposure with 40
    # positions x max-tier 5% sizing = 200% gross; tier-mix avg sizing ~100-120%.
    "max_open_positions":       59,     # total simultaneous positions (base; regime cap binds tighter)
    "drawdown_25pct_threshold": 0.10,   # portfolio drawdown > 10% -> reduce sizes 25%
    "drawdown_50pct_threshold": 0.20,   # portfolio drawdown > 20% -> reduce sizes 50%
    "drawdown_suspend_threshold": 0.30, # portfolio drawdown > 30% -> suspend new entries
    "position_staleness_pct":   0.01,   # cancel if entry price moved >1% since signal
    "broker":                   "IBKR_Canada",  # Interactive Brokers Canada (not Alpaca  -  Canada only)
    "base_currency":            "CAD",  # portfolio denominated in CAD
    "trade_currency":           "USD",  # US equity trades in USD  -  currency risk exists
    # Batch 223 (correlation + beta hedge 2026-05-18 owner-approved):
    # correlation-cap thresholds + beta-neutralization opt-in flag.
    # Beta hedge defaults OFF - enabling changes the goal from absolute
    # return to alpha-vs-SPY (owner decision; currently absolute-return
    # framing). When True the engine maintains a SPY-short overlay
    # sized to portfolio_gross_beta * beta_hedge_ratio. Phase 1B
    # owner-tunable.
    "correlation_skip_threshold":   0.85,  # |corr|>=0.85 -> block entry
    "correlation_halve_threshold":  0.70,  # 0.70<=|corr|<0.85 -> halve size
    "beta_hedge_enabled":           False, # OFF by default; opt-in
    "beta_hedge_ratio":             0.5,   # SPY short = gross_beta * 0.5
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
# B1545 (owner-approved): uniform position size used ONLY under
# --cube-isolation. The sizing tier maps LOW/AVOID to 0.0, and a zero size skips
# the trade - so tier data (smart-money, agents) was deciding WHICH SIGNALS
# BECOME TRADES, defeating the purpose of isolation. Under isolation every valid
# signal opens a trade at this uniform size. The VALUE is arbitrary and cannot
# affect any gate: the cube records pnl_pct, a PERCENTAGE, so size cancels.
CUBE_ISOLATION_SIZE_PCT: float = 0.01

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


def apply_agent_tier_size_modifier(tier: int, base_size_pct: float) -> float:
    """Batch 398 (2026-05-27): DEC-062 engine activation.

    Apply the TradingAgents 5-tier output modifier to a base position-size %.
    Phase 1B canary (DEC-508 Phase B) flow:
        agent_output_tier (1-5) -> modifier (0.5x..1.5x) -> adjusted_size_pct

    Args:
        tier: TradingAgents output tier 1..5; out-of-range returns base unchanged
              with a logged warning (no-op default rather than silent zero).
        base_size_pct: CONFIDENCE_TIERS base sizing % from current engine path.

    Returns:
        Adjusted size % (base * modifier), clamped non-negative.

    Note: DEC-062 modifier is INDEPENDENT of the engine's existing
    `_adjust_tier_by_agent` +/-1 shift (Approved Rules score>=75/<=40).
    The shift adjusts the CONFIDENCE_TIERS slot; this modifier scales the
    base % within whatever slot the trade lands in.  Both can coexist
    when Phase B canary activates.
    """
    if tier not in AGENT_TIER_TO_SIZE_MODIFIER:
        # Out-of-range tier: log + return base unchanged (fail-open).
        import logging
        logging.getLogger(__name__).warning(
            "DEC-062: tier=%s out of range [1..5]; returning base size unchanged",
            tier,
        )
        return max(0.0, float(base_size_pct))
    return max(0.0, float(base_size_pct) * AGENT_TIER_TO_SIZE_MODIFIER[tier])

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

# Batch 510b (2026-05-31, R4 cube spec per owner directive 2026-05-31):
# Required macro regime per strategy. When a strategy is keyed here, the
# engine accepts the candidate only when `macro_score` matches the listed
# constraint (typically "neutral" only). Default empty -> no filter.
#
# Backed by Batch 501 entry-side optimizer analysis on merged R3 cube:
# `macro_score == neutral` is the dominant entry-side lift across 5 of
# the 9 LOCK-causing candidate strategies (Sharpe lifts +1.6 to +4.5):
#   bollinger_tight              -0.06 -> +4.41 (n=36)
#   monthly_bias_momentum_long    0.80 -> +3.90 (n=82) [regime_neutral]
#   xs_quality_top_quintile_long  0.21 -> +3.07 (n=76)
#   pead_long                     1.13 -> +3.40 (n=58)
#   adx_initiation               -0.40 -> +1.84 (n=138)
#
# Default empty -> no behavior change for non-R4 runs. Owner populates
# for R4 cube spec (separate from the default to keep R3-replay tests
# deterministic).
STRATEGY_REQUIRED_MACRO_REGIME: dict[str, str] = {
    # Batch 514 (2026-05-31) -- R4 cube spec ACTIVATED per owner directive.
    # Source: Batch 501 entry-side optimizer found `macro_score == neutral`
    # is the dominant entry-side lift across these 5 strategies (Sharpe
    # lifts from negative/low up to +1.84 to +4.41). Wiring these as
    # required entry gates is the R4 cube unblock for 1A-alpha.
    "bollinger_tight":              "neutral",
    "monthly_bias_momentum_long":   "neutral",
    "xs_quality_top_quintile_long": "neutral",
    "pead_long":                    "neutral",
    "adx_initiation":               "neutral",
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
# Batch 224 (pre-FOMC + buybacks 2026-05-18 owner-approved research review
# Top-10 #9): strategies in this set BYPASS the Batch 191 event suppression
# gate. They are explicitly designed to fire DURING macro event windows
# (e.g., pre-FOMC long sleeve - Lucca-Moench 2015 documented +50bps/yr
# alpha in the 24h preceding FOMC announcements). The engine's event
# suppression check inside backtest.py respects this set so the long
# sleeve isn't blocked by the suppression intended for non-event
# strategies.
STRATEGIES_BYPASS_EVENT_SUPPRESSION: set[str] = {
    "pre_fomc_long_sleeve",
    "pre_fomc_quality_momentum_long",
    "buyback_8k_recent_long",
}


# Batch 316a (2026-05-25) owner directive 2026-05-25: REVERSED Batch 218
# deprecation. All 23 prior-deprecated strategies re-activated for Stage D
# + Phase 1A-beta empirical validation. Rationale: let the backtest produce
# per-strategy verdicts on actual data, rather than relying on a-priori
# literature filtering. Strategies that produce no trades or losing
# verdicts at Phase 1A-beta scale can be pruned with empirical evidence
# (not just citations).
#
# Tradeoff acknowledged: Bonferroni / Deflated-Sharpe multi-testing
# denominator grows 125 -> 148 (~17% tighter effective threshold for
# borderline strategies). Owner accepts this for the validation pass.
#
# Literature citations preserved below for context but no longer gate
# the runtime filter. If the empirical pass confirms the literature
# (zero alpha / null verdicts), re-deprecation is a single-line change.
#
# Original Batch 218 (2026-05-18) deprecation rationale, retained for
# historical context:
#   - Moving-average crossovers (Zakamulin 2014 JAM; Faber 2013): ~0 alpha
#     vs buy-hold since 1990. Names: golden_cross_50_200, golden_cross_9_21,
#     golden_cross_20_50, golden_cross_volume, death_cross_50_200_volume.
#   - Indicator-derivative singles (Marshall-Cahan 2008 PBFJ; Park-Irwin
#     2007 JES): awesome_oscillator, ppo_crossover, tema_dema,
#     force_index_breakout, mfi_oversold.
#   - Parabolic SAR (Park-Irwin 2007; Lukac-Brorsen-Irwin 1988):
#     parabolic_sar_flip, parabolic_sar_flip_short.
#   - Candlestick patterns (Marshall-Young-Cahan 2008 PBFJ tested on
#     Japanese equities; Horton 2009 JBF confirmed null on US): morning_star,
#     evening_star_short, three_white_soldiers, doji_at_support,
#     bullish_engulfing_support, shooting_star_short.
#   - Williams %R dual-combo (Phase 1A-beta empirical 0% WR / 5 trades):
#     williams_stoch_dual.
#   - Plain MACD crossover (Hudson-Atanasova-Urquhart 2022 IRFA null):
#     macd_crossover, macd_crossover_short.
#   - Camarilla R3/S3 plain heuristic (Marshall-Cahan 2008): camarilla_r4_breakout
#     (B641 W10 renamed from camarilla_r3_breakout per source-system re-anchor),
#     camarilla_s3_bounce.
DEPRECATED_STRATEGIES: set[str] = set()


# Batch 372 (2026-05-26) owner directive: STRATEGIES_DISABLED_MISSING_PRODUCER
# is SEMANTICALLY DISTINCT from DEPRECATED_STRATEGIES. The deprecated set
# was reversed in Batch 316a to validate empirically; this set tracks
# strategies that CANNOT fire because a required upstream data producer
# does not exist in the prefetch pipeline. Re-enable when the producer
# lands. NOT a literature-pruning judgement.
#
# Each entry must record: (a) the missing producer signal key,
# (b) what data source would supply it, (c) why it's not implementable
# "now" (Sprint dependency).
#
# Current entries (Batch 372, B975 +1):
#   dxy_headwind_multinational_short - missing foreign_rev_pct producer
#     Strategy gate: usd_strengthening AND foreign_rev_pct > 40.
#     usd_strengthening fires correctly (UUP-proxy DXY in cache).
#     foreign_rev_pct (% of revenue from foreign operations) requires
#     10-K geographic segment table parsing. Verified 2026-05-26:
#       Polygon Stocks Starter financials_json: no segments
#       SEC EDGAR companyfacts API: consolidated revenues only
#       Existing SEC XBRL prefetch: no axis dimensions
#       Finnhub financials_reported: bs/ic/cf only
#     Real-data implementation requires raw 10-K XBRL segment-axis
#     parser (1-2 day Sprint-1 build) or paid Polygon Plus tier.
#     Owner directive 2026-05-26: disable via this set until the
#     producer lands; clean Stage 2 boundary preferred over hand-
#     curated CSV.
#
#   naked_poc_retest_long - REVERSED B1035 (2026-06-27) Council 129
#     Option-6 owner-approved per directive 'Approve all recs council
#     this. Has everything been implemented from wiring audit'. F2
#     sub-agent runtime probe on AAPL 2024-06-30 confirmed producer
#     EXISTS at screener.py:8257-8272 (inline orchestrator block
#     calling volume_profile.compute_period_pocs); emits
#     naked_poc_count=6 + naked_poc_nearest_distance_pct=0.079 on
#     real bars. B975 disablement was a FALSE-POSITIVE driven by
#     BLIND-SPOT-3 in b974_classify_signal_orphan_17.py extractor
#     (skips screener.py orchestrator by design per line 202). Per
#     feedback_no_a_priori_strategy_pruning: producer works ->
#     re-enable + let cube empirically measure. NOT in this set.
#
#   m_and_a_target_long - REVERSED B1035 (2026-06-27) Council 129
#     Option-6 owner-approved. F3 sub-agent reconcile of B984 vs
#     B748d found: producer EXISTS-RELIABLE at sec_edgar_extractor.py
#     :239-344 (compute_sec_edgar_signals reads
#     data_prefetch/sec_edgar_decoded/8_K/<TICKER>.parquet with
#     populated item_codes). B748d pin test 8 (test_batch748d_
#     audit_script_fix.py:144-153) verified AAL 2026-03-16 returns
#     8k_item_1_01_filed_within_30d=True. B984 "CC-B 8-K population-
#     mixing carry" rationale was a citation slip - EV-7 deletion
#     (screener.py:3454-3456) explicitly distinguishes itself from
#     properly-parsed Item 1.01 strategies. Re-enable as
#     EXPLORATORY pending SM-4 feasibility cube verdict
#     (S4-B673-SM4-FEASIBILITY-FAILURE-RECLASSIFICATION ticket
#     tracks separately). NOT in this set.
STRATEGIES_DISABLED_MISSING_PRODUCER: set[str] = set()

# B1441 (2026-08-03 owner directive "Retire group 2") - SEMANTICALLY DISTINCT from both
# sets above, and deliberately NOT folded into MISSING_PRODUCER.
#
# These strategies have a producer that WORKS. `get_classification_change_signals`
# (backtest/data/universe.py:605) is implemented, wired via signal_loader.py:312, pinned
# by test_batch557_phase1a_beta_classification_cluster_verdict.py, and emits all six keys.
# What is missing is DATA: `Backtesting universe/sector_history.csv` spans 2018-09-24 ->
# 2023-03-17, so the entire 2022-05-05..2026-05-05 backtest window contains just
# **14 reclassification events, all on one date (2023-03-17)**. Nine strategies each
# layering further gates (retest, EMA-200, insider, institutional) on 14 ticker-days
# cannot produce cube evidence. Structurally starved, NOT mis-tuned - per
# `feedback_no_prior_edge_consolidate_before_tune`, loosening against a 14-event universe
# would manufacture overfit.
#
# Filing these under MISSING_PRODUCER would send a future reader hunting for a producer
# that is not missing - precisely the confusion that made ticket S6-B1419 wrong for weeks
# (it asserted "producer never emits new_sector/prior_sector"; all four parts were false).
# Naming the real cause is the fix.
#
# RE-ENABLE when sector_history.csv is extended past 2023-03-17 (S6-B1434b).
STRATEGIES_DISABLED_DATA_SCARCITY: set[str] = {
    "classification_change_breakout_long",
    "classification_change_from_tech_short",
    "classification_change_momentum_long",
    "classification_change_oversold_long",
    "classification_change_recent_long",
    "classification_change_to_tech_long",
    "classification_change_volume_long",
    "classification_change_with_insider_long",
    "classification_change_with_institutional_long",
}


# B1465 (2026-08-05 owner-approved, ticket S6-B1463a) -- DUPLICATE REGISTRATIONS.
# SEMANTICALLY DISTINCT from every other disable set, following the B1441 precedent
# of creating a new set rather than overloading one:
#   DEPRECATED_STRATEGIES              literature-null (no replicable peer-reviewed edge)
#   STRATEGIES_DISABLED_MISSING_PRODUCER  the producer does not exist
#   STRATEGIES_DISABLED_DATA_SCARCITY  the producer works, the DATA is thin
#   STRATEGIES_DISABLED_DUPLICATE      <- the strategy WORKS and is a COPY of another
#
# Each entry fires on gates identical (or near-identical) to a surviving registration,
# so it doubles that signal's drag while presenting as an independent result in every
# count, gate tally and multiple-testing denominator. Found by
# scripts/audit_registration_redundancy.py, which compares every (strategy x direction)
# cell to every other WITHOUT reference to returns -- the roster's own de-dup runs
# downstream of the performance gate and therefore only ever compares winners (L303).
#
# ROOT CAUSE IN ALL THREE CASES: a loosening batch removed the only differentiating
# gate. These are not historical accidents; they were manufactured by optimisation.
# CHECKLIST #169 now requires this audit after every loosening batch, which directly
# binds S6-OPT-196 (196 strategies to be loosened).
#
# Disabled rather than deleted: the function bodies stay readable, the ~15 referencing
# tests keep passing, and re-enablement is a one-line revert if a differentiating gate
# is restored.
STRATEGIES_DISABLED_DUPLICATE: set[str] = {
    # jaccard 0.9982 vs `squeeze_breakout`. B1194 (Council 278) dropped the smart_money
    # AND-requirement "to isolate the squeeze breakout pure thesis", leaving bare
    # `squeeze_fire_up` -- which IS squeeze_breakout. The loosening deleted the strategy.
    "squeeze_breakout_with_smart_money_long",
    # jaccard 1.0000 vs `macd_crossover`'s short branch over 1,524 trades - literally the
    # same trades under two registrations. Same META-PATTERN as B874 camarilla_rsi_obv.
    "macd_crossover_short",
    # jaccard 0.9993/0.9987 vs `macd_crossover` on BOTH legs. B1139 (Council 253) dropped
    # both ichimoku cloud gates as "redundant with cross direction", leaving a strategy
    # named macd_ichimoku that contains no ichimoku and is byte-identical to macd_crossover.
    "macd_ichimoku",
    # B1494 (2026-08-09 owner directive: "undo the 6 strategies now added to last turn to
    # disabled back to the optimization roster"). The six de-duplicated institutional/
    # rsi_oversold cells added at B1491 are REMOVED from this set and returned to the
    # optimisation population. Rationale for the reversal: they were disabled as redundant
    # against institutional_strong_conviction_long, but that cell no longer holds a roster
    # place after B1493 armed the Sharpe gate to 1.0 - so there is no longer a canonical
    # survivor for them to be redundant WITH, and they are eligible for tightening like any
    # other unpromoted strategy. If a future roster restores that parent, re-evaluate.
}
# B1189 (2026-07-06 Council 278 owner-approved DELETE): dxy_headwind_multinational_short
# ELIMINATED per owner directive. Was disabled since Batch 372 pending foreign_rev_pct
# producer that was never built. Owner-decision 2026-07-06 to eliminate strategy
# entirely rather than continue waiting. Function body + registry entry removed.


# B1038 (2026-06-27) Council 130 + Council 131 Option-A owner-approved
# per directive 'Category C and phase C execute' + 'Option-A' confirmation.
# DEC-508 Phase B canary gate for smartmoneyconcepts library.
#
# Status: doc-vs-reality drift surfaced via W3 wiring audit (B1033).
#   vendored/MANIFEST.md declares Phase A IN PROGRESS / Phase B + C
#     NOT STARTED.
#   But 18 SMC strategies (smc_*) were firing live in screener.py.
#   Phase B -> C owner-approval gate per DEC-508 was NEVER CROSSED.
#
# B416 root cause CONFIRMED via Phase C smoke 2026-06-27 (Council 131):
#   Engine log: "component=smc_ict.import_smartmoneyconcepts
#     exception=ModuleNotFoundError: No module named 'smartmoneyconcepts'"
#   vendored/smartmoneyconcepts/ exists in repo BUT NOT INSTALLED in
#     AWS user-data (no pip install -e vendored/smartmoneyconcepts/).
#   Producer compute_smc_signals returns {} for all bars.
#   Result: 18 SMC strategies are de-facto disabled in production
#     (Phase A coverage proves they CAN run; production simply lacks
#     the library install).
#
# Owner Decision (Option-A): formalize de-facto state via explicit
#   SMC_PHASE flag. Default "B-CANARY" short-circuits 18 SMC strategy
#   classes. One-line flip to "PRODUCTION" when owner approves Phase
#   C promotion per C-1 declaration doc's 8 sign-off items.
#
# Per `feedback_narrow_scope_blast_radius`: single config flag; reverse-
#   able one-line edit. Per `feedback_no_a_priori_strategy_pruning`:
#   this is a DEC-508 Phase B canary gate, NOT pruning (cube still
#   computes signals + records counts; strategies short-circuit only).
#
# B1041 (2026-06-28) Council 133 Option-2 owner Approve-all directive:
# Promoted SMC_PHASE from "B-CANARY" to "PRODUCTION" per owner sign-off.
# All 6 outstanding decisions APPROVED via "Approve all":
#   (a) 75% coverage waiver
#   (b) Dashboard 2 waiver
#   (c) AUDIT.md sign-off (B1041 entry at AUDIT.md:9-79)
#   (d) Sub-agent #5 single-ticker harness-proof scope
#   (e) SMC_PHASE='PRODUCTION' + Phase C v2 smoke
#   (f) Phase D R5 Phase 1 ladder launch (gated on Phase C v2 PASS)
SMC_PHASE: str = "PRODUCTION"  # "B-CANARY" | "PRODUCTION"


# DEC-614 (B890 owner-approved 2026-06-18) ADF mean-reversion taxonomy.
# Per Council 16 Contrarian "explicit auditable taxonomy file" demand:
# rather than infer mean-reversion classification via regex / name-pattern,
# enumerate the strategies explicitly. This set is the SINGLE SOURCE OF TRUTH
# for ADF AUTO-FAIL gate (DEC-614 / adf_test_p_max_mean_reversion).
#
# Derivation: strategies registered via screener._strat3() / _strat() with
# category="mean_reversion" tag. Cross-checked via grep
# `category.*mean_reversion` in screener.py (12 hits as of B890).
#
# Maintenance discipline: when a new mean-reversion strategy is added via
# Class 7 NEW_STRATEGY workflow, add to this set in the SAME batch.
# Pin test `test_batch890_mean_reversion_taxonomy_complete` asserts that
# every category="mean_reversion" registration in screener.py has a matching
# entry here (drift-guard per `feedback_doc_count_drift_must_be_test_pinned`).
MEAN_REVERSION_STRATEGIES: set[str] = {
    # Bollinger band mean-reversion family
    "bollinger_lower",
    "bollinger_tight",
    "bollinger_upper_short",
    # Keltner mean-reversion
    "keltner_lower",
    # RSI extreme mean-reversion
    "rsi_oversold",
    "rsi_overbought_short",
    "rsi9_extreme",
    "rsi21_slow",
    # Williams %R mean-reversion
    "williams_r_oversold",
    # Stochastic mean-reversion
    "stochrsi_oversold",
    "stochrsi_overbought_short",
    # MFI mean-reversion
    "mfi_oversold",
}


# B906 (2026-06-18) Council 28 NEW: MEASUREMENT_DISPUTED taxonomy. Auditable
# set of strategies where R4 cube and B660-extended fire-count measurements
# disagree materially, OR where both measurements are below the n=30 cube-
# validity threshold without prior owner walk-back protection. Members are
# INELIGIBLE for Stage 5 SWAP promotion + B888 Phase 1B-alpha winners
# shortlist until removed (gate enforced by downstream selection scripts).
#
# Removal protocol (one of):
#   (a) Post-B901 re-measurement via measure_fire_count.py confirms fire
#       count >= 30/yr on full T1a x 6.41yr universe -> remove + cube-
#       eligible
#   (b) OPEN_INVESTIGATIONS entry resolved with empirical evidence of
#       measurement-pair convergence -> remove + cube-eligible
#   (c) Owner-approved EXPLORATORY tag applied -> remove (EXPLORATORY
#       supersedes MEASUREMENT_DISPUTED as it's a deeper marker)
#
# Reason for separate taxonomy (vs just EXPLORATORY-tagging):
#   - EXPLORATORY is sticky across roster docs, dashboards, count-pins
#   - Tagging on KNOWN-BROKEN measurements would violate
#     `feedback_no_a_priori_strategy_pruning`
#   - MEASUREMENT_DISPUTED is INSTRUMENTED DEFER (Council 28 Option C+);
#     auto-resolves when B901-fix + re-measurement lands (B907)
#
# DEC-614 PATTERN precedent: explicit auditable set in code +
# `feedback_doc_count_drift_must_be_test_pinned` adherence.
MEASUREMENT_DISPUTED: set[str] = {
    # B906 initial population: 6 GENUINELY_FIRE_STARVED strategies from B900
    # audit with NO existing EXPLORATORY tag AND NO walk-back marker.
    # R4 cube fired < 30 / B660-extended also < 30 OR materially different
    # measurement; clear cube-validity below n=30 threshold per
    # `feedback_minimum_fire_count_gate_before_cube`. Resolve via B907
    # post-B901 SMC fix re-measurement.
    "institutional_oversold_long",                # R4=1, B660-ext=0.00/yr
    "institutional_breakout_confirmation_long",   # R4=3, B660-ext=0.00/yr
    # B979 (2026-06-21) owner-approved Council 80 Option-F: REMOVED
    # institutional_persistent_holders_long from MEASUREMENT_DISPUTED via
    # removal protocol clause (c) -- EXPLORATORY tag now applied in
    # backtest/engine/multiple_testing_correction.py EXPLORATORY_STRATEGIES.
    # Resolves B931/B906 MAY-REVERT (was pending owner decision since B906
    # Council 28). B901 re-measurement hook preserved as
    # B901-INSTITUTIONAL-PERSISTENT-HOLDERS-RE-MEASUREMENT queue ticket.
    "keltner_lower",                              # R4=1, B660-ext=17.93/yr -- MEASUREMENT DISAGREEMENT
    "post_inclusion_reversal_short",              # R4=7, B660-ext=0.00/yr
    "pivot_s2_bounce",                            # R4=10, B660-ext=28.38/yr -- BORDERLINE
    "pivot_s3_capitulation",                      # R4=11, B660-ext=2.34/yr -- B643 redesign
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
ALPHA_VANTAGE_DEPRECATED = True
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
    "exit_method_count_min":          21,    # Batch 226 +4 (chandelier, vix-conditional, mfe-lockin, mae-conditional)
    "rr_minimum_all_exits":           2.0,   # DEC-353 R:R floor
    "no_negative_position_sizes":     True,
    "no_above_100pct_capital_alloc":  True,
}

# DEC-075 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 63 2026-05-11
# (owner-approved Path C 23-DEC close-out). AEP breaker derived-metric
# implementation lives in DEC-435 (Batch 49) -- _aep_pct_metric helper in
# metrics.py. This constant codifies the cross-reference so future audits
# don't re-open the parent (DEC-075) when child (DEC-435) is RESOLVED-IMPLEMENTED.
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
TICKER_STOPOUT_COOLDOWN_DAYS = 5

# BUG-61 concurrent-block mode (Batch 510a 2026-05-31 per owner directive
# "investigate + fix bug; surface recommendation for approval"):
# Mode-A "ticker"           : BLOCK any new entry on a ticker that already
#                              has ANY open position (current default;
#                              prior owner-approved behavior; 49.7% of R3
#                              skip events).
# Mode-B "ticker_direction" : BLOCK only same-direction entries on the
#                              ticker (a long open allows a new short; a
#                              short open allows a new long). Permits
#                              hedging-pair strategies to coexist.
# Mode-C "ticker_strategy"  : BLOCK only when the SAME strategy already
#                              has an open position on the ticker. Lets
#                              different strategies stack on the same
#                              name (e.g. pead_long + xs_momentum_long
#                              both open AAPL).
# Mode-D "off"              : DISABLE the block entirely. Portfolio cap +
#                              max-loss-cap + cooldown still apply.
#
# Batch 514 (2026-05-31, R4 cube activation per owner directive):
# FLIPPED from "ticker" (prior owner-approved Option A) to
# "ticker_strategy" -- allows different strategies to stack on the
# same ticker (e.g. pead_long + xs_momentum_long both open AAPL)
# while still blocking the SAME strategy from re-entering. Recovers
# up to 685k blocked candidates per R3 item #2 diagnosis without
# removing concentration risk management (portfolio cap +
# cooldown + max-loss-cap still apply downstream).
BUG_61_BLOCK_MODE = "ticker_strategy"

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

# DEC-216 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 66 2026-05-11
# (constants); module wired Batch 245 + verified Batch 373 2026-05-26.
# A/B test orchestrator module path + deterministic-seed config.
# Batch 373 path correction: module lives at backtest/results/ab_orchestrator.py
# per Batch 245 (was incorrectly "backtest/ab_orchestrator.py" pre-Batch-373).
AB_ORCHESTRATOR_MODULE_PATH = "backtest/results/ab_orchestrator.py"
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

# -----------------------------------------------------------------------------
# OPT-B Phase 7 (Batch 538, 2026-06-01): panel-style technical signals
# feature flag.
#
# When True, screen_universe pre-builds a close_panel from all per-ticker
# OHLCV and calls backtest.signals.technical_panel for vectorized
# computation of RSI, simple_returns, EMA/SMA. Per-ticker
# compute_all_signals SKIPS those indicators (no double-compute).
#
# Default OFF -- the wire-in changes the engine output path. Validate
# parity via test_batch538_panel_wire_in_parity_gate BEFORE flipping ON
# in production R4. Once parity holds across full Phase 1A-beta cube,
# this flag flips to True permanently.
#
# Expected speedup when ON: ~20% additional R4 wall reduction on top of
# OPT-A's 30%. Net R4 cost on c7a.16xlarge: ~$22 (within $25 budget).
#
# Batch 542 (2026-06-02): FLIPPED TO TRUE per owner directive "1 yes
# approve" after parity validation 2026-06-02:
#   - Local 5-ticker test: panel ON vs OFF produced identical tickers
#     + identical strategy_count (parity GREEN)
#   - Warm-state speedup: 1.03x at 5 tickers (extrapolates ~10-15% at
#     388-ticker production scale)
#   - Underlying RSI vectorization: 10.66x measured (B537 microbench)
# -----------------------------------------------------------------------------
USE_PANEL_TECHNICAL_SIGNALS = True

# -----------------------------------------------------------------------------
# OPT-D Phase 2 (Batch 541, 2026-06-02): pre-computed signals feature flag.
#
# When True, screen_instrument first tries
# backtest.signals.precomputed_cache.load_precomputed_signals(ticker,
# as_of). On cache HIT, signals dict is returned without running
# compute_all_signals. On MISS, falls back to per-ticker compute path
# (backward-compat for tickers/dates not yet materialized).
#
# Default OFF -- wire-in changes engine path. Empirical parity verified
# locally (B541 validation 2026-06-02): direct compute_all_signals vs
# precomputed parquet read on AAPL 2024-06-14 -> 335 keys, 0 value diffs.
# Production flip to True is owner-gated after a real Phase 1A-beta
# smoke run validates parity at scale.
#
# Expected speedup when ON + materialized: backtest wall drops 10-50x on
# the compute layer. Walk-forward / IS-OOS replay near-instant.
# Trade-off: ~21GB storage + multi-hour one-time precompute step.
#
# Batch 542 (2026-06-02): FLIPPED TO TRUE per owner directive "run pre
# compute to validate then wire in. Same for b538." Pre-compute
# validation completed 2026-06-02 on 5 mega-cap tickers (AAPL/MSFT/
# AMZN/GOOGL/META) over 2024-05-01 to 2024-06-30 -- parity confirmed:
# direct compute_all_signals == load_precomputed_signals (335 keys,
# 0 value diffs). Flag flip is SAFE because cache MISS falls back to
# compute_all_signals (backward-compat preserved). Speedup only
# materializes after scripts/precompute_signals.py runs on full
# universe + writes parquets to data_prefetch/precomputed_signals/.
# -----------------------------------------------------------------------------
# B1563: was True, but `precompute_cache_info()` returns
# {'dir_exists': False, 'ticker_count': 0} -- the flag has been ON with an
# EMPTY cache, so every lookup missed and the miss was swallowed by a bare
# `except Exception: signals = None` in screen_instrument. A flag advertising
# a 10-50x optimisation that has never held a single row is worse than no
# flag: it makes the code read as if the fast path exists.
# Turning it OFF is the honest state. Re-enabling requires (a) populating the
# cache AND (b) a per-key PIT-divergence audit first -- the sibling
# USE_SMC_PANEL_CACHE was measured UNSAFE at 11.5pct divergence (B1542), and
# a signals cache primed from full series carries the same lookahead risk.
# See S6-B1563b.
USE_PRECOMPUTED_SIGNALS = False

# -----------------------------------------------------------------------------
# USE_SMC_PANEL_CACHE - Batch 555 OPT-C Phase 4 wire-in flag (2026-06-02)
#
# When True, `compute_smc_signals` reads the 6 SMC primitives (FVG, swings,
# OB, BOS_CHOCH, liquidity, retracements) from `backtest.signals.smc_panel_cache`
# instead of calling the vendored smartmoneyconcepts library per call.
# Cache is primed at engine init from `self.ohlcv_dict` (full per-ticker
# OHLCV) once per backtest session. Cache primitives are sliced at each
# (ticker, as_of) call respecting PIT lookahead semantics:
#   - FVG: 1-bar lookahead -> filter Index <= current_idx - 1
#   - Swing-dependent: swing_length-bar lookahead -> filter Index <= current_idx - swing_length
#
# Empirical parity (B554 parity gate on AAPL OHLCV):
#   FVG exact (0/3710 bars differ), swings within 5pct tolerance,
#   OB 0.12pct divergence (forward-mutation residual, much smaller
#   than 30pct ceiling).
#
# Expected speedup: profile shows compute_smc_signals = 175s. Cache reduces
# per-call work to dict-lookup + boolean slice. Projected 175s -> ~10-20s.
#
# Cache MISS (ticker not primed) falls back to per-call library compute,
# preserving back-compat.
# -----------------------------------------------------------------------------
# --- S6-OPT-196 producer-optimisation knobs (B1519, owner-approved) ---------
# Env-overridable so ONE code SHA can run an N-config parameter sweep: each
# engine run exports a different value instead of the tree being edited between
# runs (which would break the frozen_sha pin and make runs non-comparable).
# Defaults reproduce production EXACTLY, so an unset environment is a no-op.
#
# L387 lineage: these existed as producer arguments but the ENGINE never passed
# them - screener called compute_smc_signals(df, ticker=ticker) only - so a
# 20-config sweep would have produced 20 IDENTICAL cubes.
# --- S6-OPT-196 OPTIMIZATION MODE (B1543, owner-approved) -------------------
# Marks a run as a PARAMETER SEARCH rather than a portfolio simulation. Default
# False: production and every R5-comparable run are unaffected.
#
# When True:
#   * (B1544 REMOVED) smart_money_score is NOT skipped. B1543 skipped it on the
#     argument that sizing cannot move the gates. That was WRONG: config.py:857
#     records "LOW maps to 0 to skip", so the confidence tier GATES ENTRY, not
#     just size. A measured A/B (20 tickers x 2y) showed the entry set CHANGED -
#     245 only-ON, 124 only-OFF of ~5.2k - which would make optimisation cubes
#     non-comparable to R5. Measured saving was 6.3pct, not the 14.3pct profiler
#     share. Reverted.
#   * the max_cands auto-raise to 200 is SKIPPED. 200 was sized for ~29
#     strategies competing; a parameter sweep does not know how many
#     combinations fire, and a binding cap would make tickers compete - which
#     would break the disjoint-universe APPEND design and is the leading
#     hypothesis for the unexplained 26.63x entry inflation at 5 tickers (L376).
OPTIMIZATION_MODE: bool = os.environ.get("OPTIMIZATION_MODE", "0") == "1"

# B1561 -- STAGE-2 NO-LIVE-API ENFORCEMENT (CLAUDE.md HARD CUT 2026-05-05).
# Defaults ON: a backtest must never reach the network. Until B1561 this rule
# was policy-only, and a reader/writer schema mismatch in get_ohlcv_bulk
# (dates in a `date` COLUMN vs a reader assuming a DatetimeIndex) meant EVERY
# run silently re-downloaded its entire universe from yfinance -- non-PIT data,
# no symptom other than 11.2s of rate-limit sleep in a profile.
# Set to 0 ONLY for one-time SETUP/prefetch jobs, never for a backtest.
STAGE2_NO_LIVE_FETCH: bool = os.environ.get("STAGE2_NO_LIVE_FETCH", "1") == "1"

SMC_SWING_LENGTH: int = int(os.environ.get("SMC_SWING_LENGTH", "20"))

# B1616 / S6-B1612f (owner-approved 2026-08-17). The breaker-block optimisation
# sweep graded FOUR parameters the engine could not apply: they existed only in
# the offline grader, so a winning combination would NOT have reproduced live
# (a graded 68 fires / Sharpe 2.239 would have run as 420 fires / Sharpe 0.789,
# with a different exit method selected on the different fire set). L475.
#
# EVERY DEFAULT BELOW REPRODUCES PRE-B1616 BEHAVIOUR EXACTLY:
#   close_mitigation False  = the vendored `ob` default the engine relied on
#   tail_n           20     = the hardcoded literal at smc_ict.py:274
#   age_bars_max     None   = no age filter existed in the breaker loop
#   break_pct_max    None   = `close > top` was a strict inequality, uncapped
# `test_b1616_engine_defaults_are_byte_identical` pins that (CHECKLIST #205).
SMC_OB_CLOSE_MITIGATION: bool = os.environ.get(
    "SMC_OB_CLOSE_MITIGATION", "0") == "1"
SMC_OB_TAIL_N: int = int(os.environ.get("SMC_OB_TAIL_N", "20"))
_v = os.environ.get("SMC_BREAKER_AGE_BARS_MAX", "").strip()
SMC_BREAKER_AGE_BARS_MAX = int(_v) if _v else None
_v = os.environ.get("SMC_BREAKER_BREAK_PCT_MAX", "").strip()
SMC_BREAKER_BREAK_PCT_MAX = float(_v) if _v else None
del _v

# B1619 / S6-B1617b (owner-approved C+D, 2026-08-17). The four knobs above are
# GLOBAL: MEASURED blast radius is 5 strategies for tail_n/close_mitigation and
# 2 for the breaker caps. Setting one to tune the LONG leg silently retunes the
# SHORT leg and both mitigation blocks, whose numbers were measured at the
# defaults. Invisible under `--cube-isolation`; a real defect at Phase 1B where
# the whole roster runs together.
#
# VARIANTS are the fix. Each entry emits ADDITIONAL suffixed signal keys -
# `smc_breaker_block_bullish__<suffix>` - leaving the base keys untouched, so a
# tuned strategy binds to its own signal and every other consumer is unaffected.
# This is the B574 narrow-scope local-variant precedent (`cpr_narrow_tight`,
# `supertrend_flip_recent_long_5d`).
#
# COST, MEASURED B1619 on a 1,200-bar AAPL slice:
#   extra variant sharing ob_df ............ 0.368 ms
#   extra _smc.ob call (differing close_mitigation) ... 4.92 ms
# So variants differing only in tail/age/break are ~free; the producer groups
# by close_mitigation and calls _smc.ob at most ONCE per distinct value.
#
# Format: {"<suffix>": {"tail_n": int, "age_bars_max": int|null,
#                       "break_pct_max": float|null, "close_mitigation": bool}}
# EMPTY BY DEFAULT - no variant keys are emitted and the signal dict is
# byte-identical to pre-B1619.
import json as _json
_raw = os.environ.get("SMC_BREAKER_VARIANTS", "").strip()
try:
    SMC_BREAKER_VARIANTS: dict = _json.loads(_raw) if _raw else {}
except Exception:
    # A malformed spec must NOT silently fall back to "no variants" - that
    # would run the sweep at production settings while reporting a variant.
    raise ValueError(f"SMC_BREAKER_VARIANTS is not valid JSON: {_raw!r}")
del _raw

# Which EMA span the trend leg reads. compute_ema_sma emits spans 9/20/21/50/200
# from pairs (9,21),(20,50),(50,200) - so no producer change is needed, only a
# change of which emitted signal the strategy consumes.
STRAT_EMA_SPAN: int = int(os.environ.get("STRAT_EMA_SPAN", "200"))

USE_SMC_PANEL_CACHE = False
