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
