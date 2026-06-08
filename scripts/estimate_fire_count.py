"""Batch 619 (2026-06-08) -- Fire-count estimator per CHECKLIST #105 (k).

Pre-cube sanity-check tool for Stage 4 walks: given a strategy's gate
list, estimate fires/year before routing to the cube. If the upper-
bound estimate is already < 30/year, the strategy is fire-starved and
cube cannot produce a statistically valid PASS/FAIL verdict per the
min_trades passing criterion (CLAUDE.md #9).

CAVEAT: this is an UPPER BOUND.
  - The joint computation assumes INDEPENDENCE of gates.
  - Real-world gates are often correlated (e.g. close_above_open and
    close_in_top_40pct_of_range are highly co-occurring).
  - If the upper-bound estimate is already < 30/yr, the actual joint
    fire rate is even lower. Decision: drop a gate, treat as
    exploratory, or split into separate strategies.

USAGE:
  python scripts/estimate_fire_count.py --gates resistance_break_retest \\
      obv_bullish close_above_open vol_below_avg \\
      --tickers 220 --trading-days 252

OR programmatically:
  from scripts.estimate_fire_count import estimate, PRIOR_RATES
  result = estimate(gates=["resistance_break_retest", "obv_bullish",
                            "close_above_open", "vol_below_avg"])
  print(result)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# Prior fire-rates for common producer signals, hand-curated from
# literature defaults + historical signal_fire_rates.json sampling.
# These are PER-NAME-DAY probabilities (P(signal=True for a random
# ticker on a random trading day)). Used as the independence-product
# input when no measured rate is available.
#
# These are NOT measured against the production cache; they are
# CONSERVATIVE upper-bound priors useful for sanity-checking a walk's
# proposed gate set. Per CHECKLIST (k): if the upper bound is already
# < 30/yr fires across the universe, the strategy is fire-starved.
PRIOR_RATES: dict[str, float] = {
    # Bar-of-fire candle gates (B589-family standardization)
    "close_above_open":                  0.50,
    "close_below_open":                  0.50,
    "close_in_top_40pct_of_range":       0.40,
    "close_in_bottom_40pct_of_range":    0.40,

    # Volume gates
    "vol_above_avg":                     0.50,
    "vol_below_avg":                     0.50,
    "vol_spike_12x":                     0.20,  # 1.2x is common
    "vol_spike_15x":                     0.10,
    "vol_spike_17x":                     0.06,
    "vol_spike_2x":                      0.04,

    # Trend / EMA gates (long-run market drift bias)
    "price_above_ema_200":               0.65,
    "price_above_ema_50":                0.55,
    "price_above_ema_20":                0.55,
    "below_ema_200":                     0.35,
    "below_ema_50":                      0.45,
    "below_ema_20":                      0.45,

    # MACD (B609 added bearish; mostly 50/50)
    "macd_12_26_9_bullish":              0.55,
    "macd_12_26_9_bearish":              0.45,

    # OBV (B617 added bearish; 20-bar MA baseline; ~50/50)
    "obv_bullish":                       0.55,
    "obv_bearish":                       0.45,
    "obv_rising":                        0.55,
    "obv_falling":                       0.45,
    "obv_diverge_bull":                  0.05,

    # AVWAP family (B205 + B598 + B612)
    "above_avwap_20low":                 0.50,
    "above_avwap_20high":                0.30,
    "above_avwap_50low":                 0.50,
    "above_avwap_252low":                0.50,
    "below_avwap_20low":                 0.50,
    "below_avwap_20high":                0.70,
    "below_avwap_50low":                 0.50,
    "below_avwap_252low":                0.50,

    # 52-week extremes (rare by construction)
    "near_52w_high":                     0.05,
    "near_52w_high_95pct":               0.08,
    "near_52w_high_98pct":               0.04,
    "near_52w_low":                      0.05,
    "near_52w_low_105pct":               0.08,
    "near_52w_low_102pct":               0.04,

    # Break-retest family (rare multi-bar patterns)
    "resistance_break_retest":           0.03,
    "support_break_retest":              0.03,
    "dc20_resistance_break_retest_strong": 0.015,
    "dc20_support_break_retest_strong":    0.015,
    "year_high_break_retest":            0.01,
    "year_low_break_retest_short":       0.01,
    "flag_bull_break_retest_long":       0.005,
    "flag_bear_break_retest_short":      0.005,
    "flag_bull_broke":                   0.02,
    "flag_bear_broke":                   0.02,
    "flag_bull_detected":                0.05,
    "flag_bear_detected":                0.05,

    # Donchian breakouts
    "dc20_breakout_up":                  0.03,
    "dc20_breakout_dn":                  0.03,
    "dc10_breakout_dn":                  0.05,
    "dc10_breakout_dn_1pct":             0.03,
    "dc10_strong_breakout_dn":           0.02,

    # SMC / ICT signals (event-driven; rare)
    "smc_liquidity_swept_dn":            0.05,
    "smc_liquidity_swept_up":            0.05,
    "above_prev_low":                    0.65,
    "above_prev_high":                   0.45,
    "below_prev_low":                    0.35,
    "below_prev_high":                   0.55,

    # News (cache-dependent, varies by ticker; coarse default)
    "news_sentiment_5d":                 0.50,  # ~50% have ANY sentiment
    "news_volume_zscore_5d":             0.50,
    "news_count_5d":                     0.30,  # 30% have >= 3 articles
    "news_article_count":                0.30,
    "news_sentiment_shift":              0.50,

    # Smart-money (cache-dependent; from signal_fire_rates.json sample)
    "smart_money_score":                 0.20,
    "institutional_buy":                 0.30,  # 13F STATE has high persistence
    "institutional_strong_buy":          0.10,
    "insider_cluster_active":            0.05,
    "cfo_buy":                           0.02,
    "large_dollar_buy":                  0.03,

    # PEAD (event-driven, 60-day window)
    "within_pead_window":                0.20,
    "pead_positive_surprise":            0.15,
    "pead_negative_surprise":            0.15,

    # SI / DTC (positioning)
    "short_interest_pct":                1.00,  # always emitted; threshold check
    "days_to_cover":                     1.00,  # always emitted

    # ===================================================================
    # B635 (2026-06-08 owner directive D) PRIOR_RATES expansion per
    # R5_VALIDATION_MANIFEST M6. 243 INCOMPLETE_PRIORS signals from B621
    # audit get category-based hand-curated defaults so the estimator
    # produces usable upper bounds NOW. Post-R5, each will be refined
    # from signal_fire_rates.json measured frequencies.
    #
    # PRIOR CATEGORIES (rough magnitudes):
    #   Event/cross signals:        ~0.02-0.05 (rare; ~5-13 days/yr)
    #   Threshold extremes:         ~0.05-0.15 (oversold/overbought)
    #   Pattern-detected:           ~0.01-0.03 (rare candle/chart patterns)
    #   Gap signals:                ~0.02-0.05
    #   State signals:              ~0.40-0.60 (bullish/bearish flags)
    #   Calendar/event:             ~0.02-0.10
    #   SMC/ICT:                    ~0.05-0.15
    #   Smart-money/insider:        ~0.02-0.05
    #   Cross-sectional decile:     ~0.10 (top-decile by definition)
    #   Pairs trading:              ~0.05
    #   Volume profile:             ~0.05-0.10
    #   Numerical (no threshold):   ~0.50 (assume coin-flip; threshold
    #                               gates get heuristic multiplier)
    # ===================================================================

    # --- Event / cross signals (rare; ~0.02-0.05) ---
    "ao_cross_up": 0.04, "ao_cross_dn": 0.04,
    "cmf_cross_up": 0.04, "cmf_cross_dn": 0.04,
    "ema_9_21_golden_cross": 0.02, "ema_9_21_death_cross": 0.02,
    "ema_20_50_golden_cross": 0.015, "ema_20_50_death_cross": 0.015,
    "ema_50_200_golden_cross": 0.01, "ema_50_200_death_cross": 0.01,
    "ichi_tk_cross_up": 0.04, "ichi_tk_cross_dn": 0.04,
    "macd_12_26_9_crossover_up": 0.03, "macd_12_26_9_crossover_dn": 0.03,
    "macd_8_21_5_crossover_up": 0.04, "macd_8_21_5_crossover_dn": 0.04,
    "macd_bullish_cross": 0.03,
    "ppo_crossover_up": 0.03, "ppo_crossover_dn": 0.03,
    "psar_flip_up": 0.04, "psar_flip_dn": 0.04,
    "stoch_bullish_cross": 0.05, "stoch_bearish_cross": 0.05,
    "stochrsi_cross_up": 0.05, "stochrsi_cross_dn": 0.05,
    "tema_cross_up": 0.04, "tema_cross_dn": 0.04,
    "force_index_cross_up": 0.05, "force_index_cross_dn": 0.05,
    "adx_cross_up": 0.05,
    "squeeze_fire_up": 0.03, "squeeze_fire_dn": 0.03,
    "squeeze_on_release": 0.03,
    "roc_turning_up": 0.05, "roc_turning_dn": 0.05,

    # --- Threshold extremes ---
    "rsi_14_oversold": 0.05, "rsi_14_rising": 0.50,
    "rsi_9_extreme_os": 0.05, "rsi_9_rising": 0.50,
    "mfi_14_oversold": 0.05, "mfi_oversold": 0.05, "mfi_overbought": 0.05,
    "stoch_oversold": 0.10, "stoch_overbought": 0.10,
    "stochrsi_oversold": 0.10, "stochrsi_overbought": 0.10,
    "williams_r_oversold": 0.10,
    "uo_oversold": 0.06,
    "adx_trending": 0.30, "adx_strong": 0.10,

    # --- Pattern-detected (rare; ~0.01-0.03) ---
    "hammer": 0.04, "pin_bar": 0.04, "doji": 0.10,
    "bullish_engulfing": 0.03, "bearish_engulfing": 0.03,
    "shooting_star": 0.03, "morning_star": 0.01, "evening_star": 0.01,
    "three_white_soldiers": 0.01,
    "inside_bar": 0.05,
    "head_shoulders_bottom_detected": 0.005,
    "double_bottom_detected": 0.01,
    "cup_handle_detected": 0.005,
    "triangle_ascending_detected": 0.02,

    # --- Gap signals ---
    "gap_up_2pct": 0.05, "gap_dn_2pct": 0.05,
    "gap_up_pct": 0.50, "gap_dn_pct": 0.50,  # numerical magnitude

    # --- Near-level / proximity ---
    "near_pivot": 0.20,
    "near_r1": 0.15, "near_r1_wide": 0.25, "near_r2": 0.10, "near_r2_wide": 0.18,
    "near_s1": 0.15, "near_s1_wide": 0.25, "near_s2": 0.10, "near_s2_wide": 0.18,
    "near_s3": 0.05,
    "near_cam_r3": 0.10, "near_cam_s3": 0.10,
    "near_prev_high": 0.20, "near_prev_low": 0.20,
    "near_52w_high_retest_long": 0.02, "near_52w_low_retest_short": 0.02,
    "at_key_fib": 0.10, "at_key_fib_wide": 0.20,
    "above_r1": 0.30, "above_r2": 0.20, "above_cam_r3": 0.15,
    "below_s1": 0.30, "below_s2": 0.20, "below_cam_s3": 0.15,
    "above_cpr": 0.55, "below_cpr": 0.45,
    "cpr_narrow": 0.20, "bb_squeeze": 0.05,

    # --- State signals (continuous; ~0.40-0.60) ---
    "ema_50_200_bullish": 0.55, "ema_50_200_bearish": 0.45,
    "hull_bullish": 0.55,
    "ichi_above_cloud": 0.55, "ichi_below_cloud": 0.30,
    "ichi_weekly_above_cloud": 0.55, "ichi_weekly_below_cloud": 0.30,
    "ichi_tk_bullish": 0.55, "ichi_tk_bearish": 0.45,
    "supertrend_bullish": 0.55,
    "price_above_hull": 0.55,
    "price_above_sma_50": 0.55, "price_above_sma_200": 0.65,
    "price_above_tema": 0.55,
    "above_vwap": 0.50,
    "cmf_positive": 0.55,
    "force_index_breakout": 0.05,

    # --- Bollinger / Keltner touches ---
    "bb_20_15_touch_lower": 0.10, "bb_20_15_touch_upper": 0.10,
    "bb_20_20_touch_lower": 0.10, "bb_20_20_touch_upper": 0.10,
    "kc_touch_lower": 0.08, "kc_touch_upper": 0.08,

    # --- AVWAP percentages ---
    "pct_from_avwap_20high": 0.50, "pct_from_avwap_252low": 0.50,
    "pct_from_avwap_50low": 0.50,

    # --- 52w breaks ---
    "break_52w_high": 0.02, "break_52w_low": 0.02,
    "dc10_breakout_up": 0.05, "dc10_breakout_up_1pct": 0.03,
    "dc10_strong_breakout_up": 0.02,

    # --- Retest signals ---
    "r1_break_retest_long": 0.01, "s1_break_retest_short": 0.01,
    "year_high_break_retest_long": 0.01,

    # --- Smart-money / insider / institutional ---
    "insider_unique_buyers_30d": 0.30, "insider_officer_buyers_30d": 0.10,
    "insider_director_buyers_30d": 0.10,
    "institutional_increased": 0.40, "institutional_negative": 0.20,
    "institutional_new_positions": 0.20,
    "institutional_persistence_growing": 0.15,
    "institutional_persistence_strong": 0.20,
    "persistent_holders_4q": 0.30, "total_active_holders": 1.00,
    "committed_growth_holders": 0.20,
    "sc_13d_filed_within_30d": 0.005,
    "sc_13d_latest_filer_identity": 0.005, "sc_13d_latest_percent_owned": 0.005,

    # --- SMC / ICT ---
    "smc_bos_bullish": 0.10, "smc_bos_bearish": 0.10,
    "smc_bos_retest_long": 0.03, "smc_bos_retest_short": 0.03,
    "smc_breaker_block_bullish": 0.05, "smc_breaker_block_bearish": 0.05,
    "smc_choch_bullish": 0.08, "smc_choch_bearish": 0.08,
    "smc_dealing_range_pct": 0.50,
    "smc_equal_highs_swept": 0.05, "smc_equal_lows_swept": 0.05,
    "smc_fvg_bullish_active": 0.20, "smc_fvg_bearish_active": 0.20,
    "smc_fvg_retest_long_zone": 0.05, "smc_fvg_retest_short_zone": 0.05,
    "smc_in_discount_zone": 0.30, "smc_in_premium_zone": 0.30,
    "smc_inverse_fvg_bullish": 0.05, "smc_inverse_fvg_bearish": 0.05,
    "smc_mitigation_block_long": 0.05, "smc_mitigation_block_short": 0.05,
    "smc_ob_bullish_active": 0.15, "smc_ob_bearish_active": 0.15,
    "smc_ote_long_zone": 0.05, "smc_ote_short_zone": 0.05,
    "smc_retracement_pct": 0.50,
    "po3_bullish": 0.05, "po3_bearish": 0.05,
    "po3_mmbm_setup": 0.02, "po3_mmsm_setup": 0.02,

    # --- Calendar / event signals ---
    "days_until_fomc": 1.00, "pre_fomc_d1": 0.04,
    "is_january": 0.083, "is_pre_holiday": 0.04,
    "is_totm_window": 0.30, "is_halloween_period": 0.50,
    "days_since_8k": 1.00, "recent_8k_filed": 0.05,
    "earnings_announcement_return": 0.04, "earnings_eps_yoy_growth": 0.25,
    "yoy_surprise_high": 0.10, "yoy_surprise_negative": 0.10,
    "yoy_surprise_threshold_long": 0.10, "yoy_surprise_threshold_short": 0.10,
    "classification_changed_recent": 0.02,
    "classification_change_to_tech": 0.005,
    "classification_change_from_tech": 0.005,
    "classification_change_to_defensive": 0.005,
    "days_since_classification_change": 1.00,
    "new_sector": 1.00, "prior_sector": 1.00, "sector": 1.00,

    # --- HTF / weekly bias ---
    "htf_aligned_bull": 0.40, "htf_aligned_bear": 0.30,
    "monthly_bias_bull": 0.55, "monthly_momentum_pos": 0.55,
    "weekly_bias_bull": 0.55, "weekly_bias_bear": 0.45,
    "week_open_gap_up_15pct": 0.03, "week_open_gap_down_15pct": 0.03,

    # --- Sector / regime ---
    "sector_outperforming_spy": 0.50, "sector_underperforming_spy": 0.50,
    "defensive_leadership": 0.30,
    "risk_off_regime_bond_signal": 0.20, "risk_off_regime_gold_signal": 0.20,
    "usd_strengthening": 0.50,
    "vix_band_high": 0.15, "vix_band_low": 0.15,
    "vix_term_backwardation": 0.05,

    # --- Cross-sectional rankings (decile/quintile) ---
    "xs_momentum_top_decile": 0.10, "xs_momentum_bottom_decile": 0.10,
    "xs_low_beta_decile": 0.10, "xs_low_beta_top_quintile": 0.20,
    "xs_quality_decile": 0.10, "xs_quality_top_quintile": 0.20,
    "xs_ivol_decile": 0.10,
    "xs_avoid_high_ivol": 0.10, "xs_avoid_high_max": 0.10,

    # --- Pairs trading ---
    "pair_count_active": 1.00, "pair_counterparty": 1.00,
    "pair_half_life": 1.00, "pair_zscore_signed": 0.50,

    # --- Volume profile ---
    "vp_above_value_area": 0.40, "vp_close_above_poc": 0.50,
    "vp_close_near_poc_pct": 0.50,
    "naked_poc_count": 1.00, "naked_poc_nearest_distance_pct": 0.50,

    # --- News (extension) ---
    "news_sentiment_mean": 0.50,

    # --- Numerical signals (no threshold; assumed coin-flip;
    #     threshold-extracted gates get 0.3x heuristic multiplier per
    #     _gate_rate logic). All "always emitted" magnitudes -> 1.0. ---
    "rsi_14": 1.00, "rsi_2": 1.00, "rsi_9": 1.00, "rsi_21": 1.00,
    "adx": 1.00, "uo": 1.00, "williams_r": 1.00,
    "pct_change_5d": 1.00,
    "foreign_rev_pct": 1.00,
    "cap_band": 1.00, "dow": 1.00,
}


# Default universe size + trading days
DEFAULT_TICKERS = 220        # ~221 active strategies x 220 names = scope
DEFAULT_TRADING_DAYS = 252   # 1 year of trading days


def _parse_threshold_gate(gate: str) -> tuple[str, float | None]:
    """Parse a gate spec like 'short_interest_pct>=0.20' into
    (signal_name, threshold). Returns (signal_name, None) for boolean
    gates."""
    for op in (">=", "<=", ">", "<", "=="):
        if op in gate:
            name, _, val = gate.partition(op)
            try:
                return name.strip(), float(val.strip())
            except ValueError:
                return name.strip(), None
    return gate.strip(), None


def _gate_rate(gate: str) -> tuple[float, str]:
    """Look up the prior rate for a single gate. Returns
    (rate, source_note)."""
    name, threshold = _parse_threshold_gate(gate)
    if name in PRIOR_RATES:
        base_rate = PRIOR_RATES[name]
        # Heuristic: for threshold gates on continuous signals, halve
        # the base if a tight threshold is specified.
        if threshold is not None and base_rate >= 0.5:
            return (base_rate * 0.3, f"{name} @ threshold {threshold} (heuristic 0.3x)")
        return (base_rate, f"{name} (PRIOR_RATES)")
    return (None, f"{name} (NOT IN PRIOR_RATES; estimate skipped)")


def estimate(
    gates: list[str],
    tickers: int = DEFAULT_TICKERS,
    trading_days: int = DEFAULT_TRADING_DAYS,
) -> dict:
    """Estimate annual fires across the universe for a strategy with the
    given gate list.

    Returns dict with:
      - joint_rate: probability of all gates being True on a random
        ticker-day (independence-product upper bound)
      - per_gate_rates: list of (gate, rate, source_note)
      - fires_per_year_upper_bound: joint_rate * tickers * trading_days
      - missing_priors: list of gates not in PRIOR_RATES
      - verdict: "PASS_CUBE" if upper bound >= 30; "WARN_FIRE_STARVED"
        if 5 <= upper bound < 30; "FAIL_FIRE_STARVED" if upper bound < 5
    """
    joint = 1.0
    per_gate = []
    missing = []
    for gate in gates:
        rate, source = _gate_rate(gate)
        per_gate.append((gate, rate, source))
        if rate is None:
            missing.append(gate)
        else:
            joint *= rate

    fires_year = joint * tickers * trading_days

    if missing:
        # If any prior is missing, we can't be confident; flag.
        verdict = "INCOMPLETE_PRIORS"
    elif fires_year >= 30:
        verdict = "PASS_CUBE"
    elif fires_year >= 5:
        verdict = "WARN_FIRE_STARVED"
    else:
        verdict = "FAIL_FIRE_STARVED"

    return {
        "joint_rate": joint,
        "per_gate_rates": per_gate,
        "tickers": tickers,
        "trading_days": trading_days,
        "fires_per_year_upper_bound": round(fires_year, 2),
        "missing_priors": missing,
        "verdict": verdict,
    }


def _format_report(result: dict) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append("FIRE-COUNT ESTIMATOR -- CHECKLIST #105 (k) pre-cube check")
    lines.append("=" * 70)
    lines.append(f"Universe: {result['tickers']} tickers x {result['trading_days']} trading days")
    lines.append(f"Joint rate (independence upper bound): {result['joint_rate']:.6f}")
    lines.append(f"Fires per year (UPPER BOUND): {result['fires_per_year_upper_bound']}")
    lines.append(f"Verdict: {result['verdict']}")
    lines.append("")
    lines.append("Per-gate breakdown:")
    for gate, rate, source in result["per_gate_rates"]:
        if rate is None:
            lines.append(f"  {gate}: MISSING PRIOR -- {source}")
        else:
            lines.append(f"  {gate}: {rate:.4f}  ({source})")
    if result["missing_priors"]:
        lines.append("")
        lines.append("WARNING: missing priors for: " + ", ".join(result["missing_priors"]))
        lines.append("Verdict INCOMPLETE; estimate is partial. Add priors to PRIOR_RATES + re-run.")
    lines.append("")
    lines.append("CAVEATS (per CHECKLIST (k)):")
    lines.append("  - This is an UPPER BOUND assuming independence of gates.")
    lines.append("  - Real-world gates are often positively correlated;")
    lines.append("    actual joint fire rate may be substantially lower.")
    lines.append("  - If upper bound is already < 30/yr (min_trades), the")
    lines.append("    strategy is FIRE-STARVED for cube. Drop a gate, treat")
    lines.append("    as exploratory, or split into separate strategies.")
    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gates", nargs="+", required=True,
        help="List of gate signal names (e.g. resistance_break_retest "
             "obv_bullish close_above_open vol_below_avg)")
    parser.add_argument(
        "--tickers", type=int, default=DEFAULT_TICKERS,
        help=f"Active universe size (default {DEFAULT_TICKERS})")
    parser.add_argument(
        "--trading-days", type=int, default=DEFAULT_TRADING_DAYS,
        help=f"Trading days per year (default {DEFAULT_TRADING_DAYS})")
    parser.add_argument(
        "--json", action="store_true",
        help="Output JSON instead of text report")
    args = parser.parse_args()

    result = estimate(
        gates=args.gates,
        tickers=args.tickers,
        trading_days=args.trading_days,
    )
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(_format_report(result))


if __name__ == "__main__":
    main()
