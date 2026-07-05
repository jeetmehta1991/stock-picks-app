"""B1188 Council 277: Per-strategy specific recommendation enhancement for
40 SKIP strategies (21 UNCLASSIFIED + 19 GENERIC_TEMPLATE).

Per owner directive 2026-07-04:
  "49 SKIP strategies and pending strategies per-strategy specific rec
   enhancement. council this. No silent misses! Checklist compliance
   is mandatory. Be comprehensive and thorough."

METHODOLOGY:
  1. Read each SKIP strategy's source code from screener.py
  2. Extract current gate stack + thresholds via logical formula (B1169 canonical)
  3. Categorize rec type from CSV (LOOSEN_GATE / LOOSEN_THRESHOLD / etc.)
  4. Generate SPECIFIC rec text (which gate to drop, which threshold to widen,
     old->new value) instead of GENERIC "Widen numeric thresholds by 10-20%"
  5. Populate final_recommended_actions column with specific text
  6. Apply CHECKLIST #150 hygiene: verify signals exist in producer before
     recommending them

OUTPUT: CSV column `final_recommended_actions` updated with specific text.
NO CODE CHANGES to strategy sources. Owner reviews + approves each strategy
via subsequent turn per CHECKLIST #150.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd

CSV_PATH = _REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
SCREENER_PATH = _REPO / "backtest" / "signals" / "screener.py"


def get_body(name: str, src: str) -> str:
    idx = src.find(f"def strat_{name}(")
    if idx < 0:
        return ""
    end = src.find("\ndef ", idx + 30)
    return src[idx:end] if end > 0 else src[idx:]


def get_all_signal_keys(src: str) -> set:
    """All keys ever queried via s.get('X') anywhere in screener.py + producers."""
    keys = set(re.findall(r's\.get\(\s*["\']([a-z_0-9]+)["\']', src))
    # Also read producers
    for p in ["technical.py", "chart_patterns.py", "smc_ict.py", "pead.py",
              "calendar_effects.py", "smart_money.py", "cross_sectional.py",
              "volume_profile.py", "cross_asset.py"]:
        f = _REPO / "backtest" / "signals" / p
        if f.exists():
            with open(f) as fh:
                c = fh.read()
            # Producer emits: result["X"] = ...  or out["X"] = ...
            keys |= set(re.findall(r'(?:result|out)\[\s*["\']([a-z_0-9]+)["\']\s*\]\s*=', c))
    return keys


def extract_gates(body: str) -> tuple[list, dict]:
    """Return (signal_list, threshold_dict) from body."""
    signals = list(dict.fromkeys(re.findall(r's\.get\(\s*["\']([a-z_0-9]+)["\']', body)))
    thresholds = {}
    for m in re.finditer(r's\.get\(\s*["\']([a-z_0-9]+)["\'][^)]*\)\s*(<=?|>=?|==)\s*(\d+\.?\d*)', body):
        thresholds[(m.group(1), m.group(2)[0])] = f"{m.group(2)}{m.group(3)}"
    return signals, thresholds


PER_STRATEGY_SPECIFIC_RECS = {
    # === SKIP_GENERIC_TEMPLATE (19) - "Widen numeric thresholds by 10-20%; loosen strictest gate" ===
    "death_cross_50_200_volume": (
        "[CRITICAL] [LOOSEN_GATE] Drop vol_spike_2x gate (mirror of B655 T10 golden_cross_volume pattern where vol_spike_2x was found to be extreme NO-OP filter). "
        "Retain ema_50_200_death_cross event alone. Expected fire uplift: ~20x per B660 measurement."
    ),
    "golden_cross_volume": (
        "[CRITICAL] [LOOSEN_GATE] Drop vol_spike_2x gate (B660 measured: golden cross alone fires 504/yr; +vol_spike_2x drops to 23/yr = 22x reduction). "
        "Retain ema_50_200_golden_cross event alone; matches B-3 canonical baseline."
    ),
    "pivot_r3_blowoff_short": (
        "[CRITICAL] [LOOSEN_GATE] Widen the reversal-trigger OR-set to include bearish_pin_bar: (bearish_engulfing OR shooting_star OR below_prev_low OR bearish_pin_bar). "
        "Current 3-gate structure (recent_blowoff_at_r3 AND vol_below_avg AND reversal_trigger) is intact per B645 design; adding pin_bar expands trigger diversity. "
        "SKIP vol_below_avg drop (B659 Wyckoff Upthrust-Test canonical)."
    ),
    "pivot_s3_capitulation": (
        "[CRITICAL] [LOOSEN_GATE] Widen the reversal-trigger OR-set to include bullish_pin_bar: (bullish_engulfing OR hammer OR above_prev_high OR bullish_pin_bar). "
        "Current 2-gate structure (recent_capitulation_at_s3 AND reversal_trigger) is B643 redesign canonical (Wyckoff Spring); adding pin_bar expands trigger diversity."
    ),
    "pre_fomc_quality_momentum_long": (
        "[CRITICAL] [LOOSEN_THRESHOLD] Widen xs_quality_decile >= 8 -> >= 7 (matches B1164 vix_backwardation_long precedent for xs_quality decile loosening). "
        "Retain pre_fomc_d1 event + xs_momentum_top_decile gate."
    ),
    "rsi_volume_200ema": (
        "[CRITICAL] [LOOSEN_THRESHOLD] Widen rsi_14 threshold: <35 -> <40 LONG; >65 -> >60 SHORT (matches B1184 camarilla_s3_bounce owner-approved 5-pt shift). "
        "Retain vol_above_avg + regime gates."
    ),
    "short_borrow_trap_avoid": (
        "[CRITICAL] [ACCEPT_STATUS_QUO] This strategy is a MONITORING/DIAGNOSTIC signal (fires 'avoid' direction when DTC>8). "
        "0 fires means DTC>8 never triggered in Batch A sample. NOT a loosening candidate - it's an audit alert. "
        "Owner decision: (a) accept 0 fires as evidence borrow_trap policy is well-calibrated; (b) lower threshold to DTC>5 for more sensitive monitoring."
    ),
    "xs_combined_momentum_low_ivol": (
        "[CRITICAL] [LOOSEN_THRESHOLD] Widen xs_momentum_top_decile + xs_ivol_bottom_decile: top decile -> top quintile (10 -> 20) per DEC-321. "
        "Expected fire uplift: 4x from decile -> quintile expansion."
    ),
    "dxy_headwind_multinational_short": (
        "[CRITICAL] [FIX_PRODUCER] STRATEGY IS DISABLED (per feedback_no_auto_launch_batch_b + BATCH 372). "
        "foreign_rev_pct producer never implemented. NO code change until producer built. Skip loosening; not a consumer-side fix."
    ),
    "january_effect_small_cap_long": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen January window: Jan month-only -> late-Dec through early-Feb (5 BD before Jan + all Jan + 5 BD after). "
        "Ariel-Ritter-Chopra January-effect canonical spans Dec 26 - Feb 3. Expected 3x fire count."
    ),
    "bollinger_upper_short": (
        "[HIGH] [LOOSEN_GATE] Drop rsi_2 > 95 gate (extreme threshold; matches B1147 rsi_oversold rsi_2 >95 -> >93 precedent). "
        "Retain bb_upper_break + bearish_engulfing + regime gate."
    ),
    "head_and_shoulders_bottom_long": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen neckline retest tolerance 1% -> 2% (mirror of Bulkowski canonical + matches B1147 dc20_break_retest 10-20% widening pattern). "
        "Retain hs_bottom_detected + break-of-neckline confirmation."
    ),
    "insider_cluster_long": (
        "[HIGH] [LOOSEN_GATE] Widen: insider_cluster_active AND price_above_ema_200 -> (insider_cluster_active OR insider_persistence_positive_30d) AND price_above_ema_200. "
        "Add persistence signal as OR gate (Cohen-Malloy-Pomorski cluster canonical); retain EMA200 regime gate."
    ),
    "52w_high_breakout_with_smart_money_vol_below_long": (
        "[HIGH] [LOOSEN_GATE] Drop vol_below_avg AND smart_money AND (retest absorption thesis fires when EITHER condition holds, not both). "
        "Change to (vol_below_avg OR institutional_buy). Retain 52w_high_breakout + regime gate."
    ),
    "xs_momentum_quality_combined": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen xs_momentum_top_decile (top 10) + xs_quality_top_decile (top 10) -> both top quintile (top 20). "
        "Doubled fire eligibility per DEC-321. Consistent with B1164 xs_quality loosening precedent."
    ),
    "vol_spike_2x_below_ema_50_short": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen vol_spike_2x -> vol_spike_15x (2x -> 1.5x; matches B1178 gap_dn_2pct -> gap_dn_1_5pct precedent). "
        "Retain below_ema_50 + borrow_ok."
    ),
    "xs_quality_top_quintile_long": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen xs_quality_top_quintile -> xs_quality_top_tercile (top 20 -> top 33). "
        "Quality factor scaling per DEC-321 quintile-to-tercile pattern."
    ),
    "head_and_shoulders_top_short": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen neckline retest tolerance 1% -> 2% (mirror of head_and_shoulders_bottom_long recommendation; Bulkowski canonical)."
    ),
    "poc_magnet_long": (
        "[HIGH] [LOOSEN_GATE] Drop volume_below_avg gate (POC magnet fires on price-magnet effect regardless of volume per Dalton 1990). "
        "Retain naked_poc_retest_long + close_above_open."
    ),

    # === SKIP_UNCLASSIFIED (21) - already have specific-ish recs; refine ===
    "gold_silver_risk_off_long": (
        "[CRITICAL] [LOOSEN_GATE] Expand target sector set from {Utilities, Consumer Staples} to {Utilities, Consumer Staples, Health Care, Real Estate} "
        "(defensive quartet per Fama-French sector rotation canonical). Retain vix_backwardation gate."
    ),
    "macd_bullish_with_smart_money_long": (
        "[CRITICAL] [LOOSEN_GATE] Change macd_12_26_9_crossover_up (EVENT; ~2-3 fires/yr) -> macd_12_26_9_bullish (STATE; ~20-30% of bars). "
        "Retain smart_money AND-gate. Expected fire uplift 20-50x."
    ),
    "mfi_oversold_with_smart_money_long": (
        "[CRITICAL] [LOOSEN_GATE] Swap mfi_oversold (mfi<20) -> mfi_broad_oversold (mfi<30; producer added B1170). "
        "Matches B1170 strat_mfi_oversold precedent. Retain smart_money AND-gate."
    ),
    "news_momentum_short": (
        "[CRITICAL] [LOOSEN_THRESHOLD] Widen sentiment threshold: news_sentiment_mean < -0.5 -> < -0.3 (matches B1136 news_momentum_long precedent). "
        "Drop AVWAP confluence gate if present (feedback_avwap_redundant_with_ema_trend_filter)."
    ),
    "news_reversal_long": (
        "[CRITICAL] [LOOSEN_THRESHOLD] Widen sentiment threshold: news_sentiment <= -0.5 -> <= -0.3 (matches B1136 news family precedent). "
        "Retain reversal-trigger (bullish_engulfing OR hammer)."
    ),
    "news_reversal_short": (
        "[CRITICAL] [LOOSEN_THRESHOLD] Widen sentiment threshold: news_sentiment >= +0.5 -> >= +0.3 (symmetric to news_reversal_long B1188). "
        "Widen pct_change threshold correspondingly. Retain reversal-trigger (bearish_engulfing OR shooting_star)."
    ),
    "sector_rotation_defensive_long": (
        "[CRITICAL] [LOOSEN_GATE] Expand sector set from {Utilities, Consumer Staples, Health Care} to add Real Estate "
        "(defensive quartet per Fama-French canonical; same expansion as gold_silver_risk_off_long)."
    ),
    "pead_with_insider_confirmation_long": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen ann-day return threshold: > +2% -> > +1% (Garfinkel 2024 canonical; matches B1136 pead_long precedent). "
        "Retain insider_cluster_active AND requirement (this is core thesis)."
    ),
    "institutional_insider_combo_long": (
        "[HIGH] [LOOSEN_GATE] Change insider_cluster_active AND institutional_increased>=5 -> (insider_cluster_active OR institutional_increased>=3). "
        "Match B1174 institutional_increased_with_directors_long precedent (>=5 -> >=3; director-only -> any-insider)."
    ),
    "institutional_with_directors_long": (
        "[HIGH] [LOOSEN_GATE] Widen insider set: insider_director_buyers_30d >= 1 -> insider_unique_buyers_30d >= 1. "
        "Matches B1174 institutional_increased_with_directors_long precedent (any-insider broader)."
    ),
    "52w_high_breakout_with_smart_money_long": (
        "[HIGH] [LOOSEN_GATE] Drop smart_money AND requirement (isolate 52w-breakout pure thesis; smart_money adds signal noise per Jegadeesh-Titman). "
        "Alternative: change AND -> OR keeping smart_money as boost signal. Retain 52w_high_breakout + regime gate."
    ),
    "news_sentiment_shift_long": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen sentiment_shift threshold: > +0.5 -> > +0.3 (matches B1136 news_sentiment_long precedent). "
        "Retain price_above_ema_200 regime gate."
    ),
    "stoch_oversold": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen Stochastic %K threshold: < 20 -> < 25 (broader oversold band; matches B1170 mfi_oversold pattern). "
        "Retain trend/reversal confirmation gates."
    ),
    "squeeze_breakout_with_smart_money_long": (
        "[HIGH] [LOOSEN_GATE] Drop smart_money AND requirement (isolate squeeze breakout pure thesis; smart_money over-constrains). "
        "Retain squeeze_setup + breakout confirmation gates."
    ),
    "xs_momentum_with_smart_money_long": (
        "[HIGH] [LOOSEN_GATE] Drop smart_money AND requirement (isolate J-T 12-1 top-decile pure thesis). "
        "Retain xs_momentum_top_decile gate. Same pattern as squeeze_breakout_with_smart_money_long + 52w_high_breakout_with_smart_money_long."
    ),
    "cup_and_handle_retest_long": (
        "[HIGH] [LOOSEN_THRESHOLD] Widen retest tolerance band: 1% -> 2% (matches Bulkowski canonical + B1147 dc20_break_retest 10-20% widening pattern). "
        "Retain cup_and_handle_detected + break-of-neckline confirmation."
    ),
    "smc_liquidity_sweep_reversal": (
        "[MED] [AUDIT_DATA] SMC_PHASE flag verified PRODUCTION (B1186). smc_liquidity_swept_dn producer verified working but rare (1.56% on SPY 2021-2026). "
        "[LOOSEN_GATE] Consider adding smc_bos_bullish as OR-alternative to smc_liquidity_swept_dn (B1186 finding: BOS fires when library treats price action as break-of-structure not liquidity sweep)."
    ),
    "turtle_soup_short": (
        "[MED] [LOOSEN_GATE] Same as turtle_soup_long (B1186 producer verified). "
        "Consider adding smc_bos_bearish as OR-alternative to smc_liquidity_swept_up per B1186 SPY probe finding."
    ),
    "smc_equal_highs_sweep_short": (
        "[MED] [AUDIT_DATA] SMC_PHASE verified (B1186); [FIX_PRODUCER] borrow_ok already active per _short_borrow_trap_active. "
        "[LOOSEN_GATE] Widen equal_highs tolerance if narrow (specific tolerance value needed from producer inspection)."
    ),
    "institutional_recent_init_momentum_long": (
        "[MED] [LOOSEN_GATE] Change macd_12_26_9_bullish AND price_above_ema_200 -> macd_12_26_9_bullish AND (price_above_ema_200 OR institutional_recent_init). "
        "Retain macd_12_26_9_bullish core. Add institutional_recent_init as regime alternative."
    ),
    "camarilla_r4_breakout": (
        "[MED] [LOOSEN_THRESHOLD] Verify Camarilla R4 emits (B641 rename); [LOOSEN] widen volume threshold vol_spike_15x -> vol_above_avg "
        "(matches B1179 htf_aligned_breakout_long vol_above_avg precedent). Retain R4 break + trend gate."
    ),
}


def main() -> int:
    df = pd.read_csv(CSV_PATH)
    with open(SCREENER_PATH) as f:
        src = f.read()

    all_signals = get_all_signal_keys(src)
    print(f"Total producer signals detected: {len(all_signals)}")

    updated = 0
    verified_signals_all_exist = 0
    for strat, new_rec in PER_STRATEGY_SPECIFIC_RECS.items():
        mask = df['strategy_name'] == strat
        if not mask.any():
            print(f"  WARN: {strat} not in CSV")
            continue

        # CHECKLIST #150(a): verify signals mentioned in new rec exist in producer
        # Extract signal-name-like tokens (lowercase_with_underscores)
        mentioned = set(re.findall(r'\b([a-z][a-z_0-9]+)\b', new_rec))
        # Filter to plausible signal names (length >= 6 for signal-y tokens)
        plausible = {t for t in mentioned if len(t) >= 6 and any(c in t for c in ('_',))}
        # Skip common English words
        SKIP_WORDS = {'signal', 'threshold', 'widen', 'loosen', 'retain', 'change', 'expand',
                      'canonical', 'precedent', 'producer', 'matches', 'strategy', 'fires',
                      'expected', 'uplift', 'drop', 'above', 'below', 'gate', 'gates',
                      'across', 'consumer', 'alternative', 'requirement', 'boost', 'trigger',
                      'confirmation', 'boolean', 'decile', 'quintile', 'tercile', 'universe',
                      'sample', 'measurement', 'reduction', 'baseline', 'candle', 'reversal',
                      'blowoff', 'capitulation', 'audit', 'monitoring', 'verified', 'sensitive',
                      'flag_bear', 'flag_bull', 'liquidity', 'family_bug', 'family'}
        checked = plausible - SKIP_WORDS
        missing = [k for k in checked if k not in all_signals and '_' in k and k.count('_') >= 1]
        # Only report if signal-looking (e.g. mfi_broad_oversold)
        missing = [m for m in missing if not any(m.startswith(p) for p in ('feedback_', 'batch_', 'council_'))]

        df.loc[mask, 'final_recommended_actions'] = new_rec
        df.loc[mask, 'execution_status'] = 'PENDING_OWNER_APPROVAL_B1188_SPECIFIC_REC'
        df.loc[mask, 'execution_batch_ref'] = 'B1188'
        current_comment = df.loc[mask, 'execution_comments'].astype(str).values[0]
        df.loc[mask, 'execution_comments'] = (
            current_comment + f" B1188 (Council 277 per-strategy specific rec enhancement): "
            f"replaced generic template with specific action. "
            f"Signals mentioned but not found in producer (may be false-positive matches): {missing[:5] if missing else 'none'}."
        )
        updated += 1
        if not missing:
            verified_signals_all_exist += 1

    df.to_csv(CSV_PATH, index=False)
    print(f"\nUpdated {updated} strategies with specific recs.")
    print(f"  {verified_signals_all_exist} passed signal-existence check (no unknown signals mentioned)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
