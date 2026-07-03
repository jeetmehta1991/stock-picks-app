#!/usr/bin/env python
"""Council 236 Investigation Turn 6 FINAL (2026-07-03).

SCOPE: 15 strategies across 4 clusters (INDEX_REBALANCE + AVWAP + DONCHIAN + MISC)

PRODUCER VERIFICATIONS (via live tests):
  Donchian:     WORKS. SPY currently has dc10/dc20 breakout_up + new_high
  ADX:          WORKS. AAPL adx=15.8, SPY adx=22.7; adx_di_bull emits
  MACD cross:   WORKS (0 fires today = no fresh cross events, expected)
  52w signals:  WORKS. NVDA + SPY emit near_52w_high, break_52w_high, year_high
  Golden cross: technical.py:757 emits f'ema_{fast}_{slow}_golden_cross'
  Pivots:       compute_pivots in technical.py; near_s1/r1/cam_r4 signals

CRITICAL FINDING #1 - INDEX REBALANCE DATA FILE MISSING:
  Producer: backtest/signals/index_rebalance.py (Batch 251 / DEC-370)
  Expected data: data_prefetch/derived/index_rebalance_events.parquet
  Actual: FILE DOES NOT EXIST
  Producer gracefully no-ops (returns empty dict per docstring).
  Impact: 4 strategies get NO SIGNAL DATA:
    - post_inclusion_drift_long
    - post_inclusion_reversal_short
    - post_deletion_drift_short
    - pre_rebalance_long
  Blocked pending Sprint 5 DEC-380 corp actions prefetch implementation.

CRITICAL FINDING #2 - TRIANGLE DETECTOR LIKELY BROKEN (from Turn 5):
  0 fires across 20 major tickers over 6 years vs Bulkowski 5-15/yr.
  Impacts 3 triangle strategies.

CRITICAL FINDING #3 - B832 SPOF SENTINELS TRIPPED (from Turn 4):
  All 3 news_sentiment SPOF thresholds tripped during Batch A.
  Impacts 5+ news_* strategies.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_6_INVESTIGATIONS = {
    # INDEX_REBALANCE cluster (1)
    "post_deletion_drift_short": {
        "post_investigation_verdict": "DATA_FILE_MISSING - PRODUCER_NO_OP",
        "post_investigation_recommendation": (
            "PRODUCER CODE EXISTS (backtest/signals/index_rebalance.py Batch 251/DEC-"
            "370). EXPECTED DATA FILE MISSING: data_prefetch/derived/index_rebalance_"
            "events.parquet DOES NOT EXIST. Producer gracefully no-ops (returns empty "
            "dict per docstring; 'Graceful no-op when prefetch missing (strategies fire "
            "0 trades until Sprint 5 data lands)'). Impact: this strategy + "
            "post_inclusion_drift_long + post_inclusion_reversal_short + pre_rebalance_"
            "long all get NO SIGNAL DATA (0 fires until data lands). ACTION: BLOCKED "
            "pending Sprint 5 DEC-380 corp actions prefetch implementation. Owner "
            "decision: (a) implement index_rebalance data prefetch pre-Batch-B (owner "
            "was doing this via Polygon /v3/reference feed); (b) accept as DISABLED-"
            "PENDING-DATA and skip cube-run for these 4 strategies until Sprint 5."
        ),
    },
    # AVWAP cluster (1)
    "avwap_252_breakout": {
        "post_investigation_verdict": "PRODUCER_OK + STRUCTURAL_RARE_EVENT",
        "post_investigation_recommendation": (
            "AVWAP signals emit from technical.py (avwap_20high/low, avwap_50high/low, "
            "avwap_252high/low families). Producer works. Consumer gate: 252-day AVWAP "
            "reclaim/loss + volume confirmation + RSI not extreme. 32 fires reflects "
            "252-day event window rarity (yearly institutional level shifts happen ~5-"
            "10/yr per ticker). ACTIONS: (1) LOOSEN vol threshold from vol_spike_15x "
            "(actually 1.5x per corrected memory) to vol_above_avg per canonical "
            "Shannon 2022; (2) drop extreme-overbought RSI filter (Shannon canonical "
            "doesn't require). Expected 1.5-2x uplift."
        ),
    },
    # DONCHIAN cluster (1)
    "donchian_breakdown_retest_short": {
        "post_investigation_verdict": "PRODUCER_OK + RETEST_STRUCTURAL_RARE",
        "post_investigation_recommendation": (
            "Donchian producer VERIFIED (technical.py compute_donchian emits dc10/20 "
            "breakout/breakdown + retest variants). SPY test shows dc10_breakout_up + "
            "dc20_breakout_up firing. Consumer gate: DC10 breakdown_retest_short + "
            "close_below_open + close_in_bottom_40pct + vol_below_avg + borrow_ok. "
            "6 fires reflects retest event compound. ACTIONS: (1) STATUS QUO on B682 "
            "vol_below_avg (Bulkowski canonical - empirically justified); (2) universe "
            "expansion primary lever; (3) Pattern S SHORT asymmetric caveat."
        ),
    },
    # MISC cluster (12)
    "squeeze_setup_long": {
        "post_investigation_verdict": "PRODUCER_OK + L1_STATE_+_L2_EVENT_ARCH",
        "post_investigation_recommendation": (
            "L1 (STATE eligibility): short_interest_pct + days_to_cover + institutional_"
            "buy (FINRA bi-monthly + 13F quarterly). L2 (EVENT trigger): news_sentiment_"
            "shift OR PEAD (B748d confirmed news producer works). Producer WORKS but "
            "L1 STATE + L2 EVENT compound extremely rare. Universe mismatch: high-"
            "short-interest names typically NOT in T1a S&P 500 majors. Also affected "
            "by B832 news SPOF (Turn 4 finding). ACTIONS: (1) URGENT audit FINRA short_"
            "interest prefetch coverage across Batch A tickers; (2) universe expansion "
            "(Batch B / T3 non-T1a with more high-SI names). Expected 5-10x uplift on "
            "wider universe."
        ),
    },
    "break_retest_confluence": {
        "post_investigation_verdict": "PRODUCER_OK + MULTI_SIGNAL_COMPOUND",
        "post_investigation_recommendation": (
            "Multi-signal break-retest with OBV vs 20-bar MA flow confirmation + "
            "Bulkowski dry-up volume. Producer VERIFIED (uses standard technical.py "
            "signals + Bulkowski retest variant). 28 fires reflects post-B617 empirically-"
            "justified structure. STATUS QUO. Retest strategies structurally lower fire "
            "than base breakout. Universe expansion primary lever."
        ),
    },
    "cpr_narrow_momentum": {
        "post_investigation_verdict": "PRODUCER_OK + B718_EMPIRICALLY_TIGHTENED",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py cpr_narrow_tight per B718). B718 switched "
            "cpr_narrow -> cpr_narrow_tight (0.05 threshold vs prior 0.15) per B710 "
            "reviewer fire-count-ceiling finding (B660 measured 13,906/yr SHORT = state-"
            "flag at 0.15). Post-B718 = MARGINAL territory. 25 fires reflects deliberate "
            "tightening. ACTION: STATUS QUO on B718 (empirically justified per S4-B717 "
            "ceiling). Universe expansion primary lever."
        ),
    },
    "52w_low_breakdown_pullback_short": {
        "post_investigation_verdict": "PRODUCER_OK + STRUCTURAL_RARE",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py emits near_52w_low_retest_short). Single-"
            "gate strategy + borrow_ok. 17 fires reflects retest event rarity. ACTIONS: "
            "(1) universe expansion primary lever (Batch B distressed-name coverage); "
            "(2) Pattern S SHORT asymmetric caveat."
        ),
    },
    "xs_low_beta_long": {
        "post_investigation_verdict": "PRODUCER_OK + UNIVERSE_MISMATCH",
        "post_investigation_recommendation": (
            "Producer VERIFIED (cross_sectional.py emits xs_low_beta_bottom_2_decile). "
            "B358 removed price_above_ema_200 regime gate per cell audit. 13 fires "
            "on T1a 503 = low-beta bottom-decile is INHERENTLY narrow universe (S&P "
            "500 majors are typically 1.0+ beta). ACTION: UNIVERSE EXPANSION is the "
            "ONLY meaningful lever - Batch B / T3 mid-cap universe will 5-10x fires "
            "(Utilities/Staples/RE ETFs naturally low-beta)."
        ),
    },
    "macd_crossover_short": {
        "post_investigation_verdict": "PRODUCER_OK + BORROW_FILTER_SUSPECT",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py compute_macd emits crossover_dn events). "
            "Single-gate + borrow_ok. 11 fires unusually low for a MACD-cross-based "
            "strategy (expected ~2-5/yr per ticker x 150 x 4y = 1,200-3,000). SUSPECT: "
            "_short_borrow_trap_active gate blocking most SHORT candidates on T1a. "
            "ACTION: audit borrow_ok filter blocking rate across ALL SHORT strategies "
            "(same finding surfaced in Turn 1 ichimoku_cloud_breakdown investigation). "
            "Pattern S SHORT asymmetric caveat."
        ),
    },
    "52w_high_breakout": {
        "post_investigation_verdict": "PRODUCER_OK + B697_APPLIED",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py emits break_52w_high, near_52w_high, "
            "year_high; NVDA test emits year_high=216.83, SPY near_52w_high=True). "
            "B697 walk applied 2 changes: (1) dropped sector_outperforming_spy per "
            "REJECT_REDUNDANT sweep verdict; (2) loosened same-bar 4-way AND. Post-"
            "B697 gate stack ~4 gates. 9 fires reflects intrinsic 52w-high breakout "
            "rarity + strong-close/volume confluence. ACTION: universe expansion "
            "primary lever."
        ),
    },
    "52w_high_breakout_pullback_long": {
        "post_investigation_verdict": "PRODUCER_OK + PRODUCER_RARE_EVENT",
        "post_investigation_recommendation": (
            "Producer VERIFIED emits near_52w_high_retest_long. Single-gate. 8 fires "
            "reflects producer 4-condition compound (52w high broken in last 10 days + "
            "close within 1% + low volume + bullish bar). ACTION: producer-side widen "
            "1% proximity band to 2%; extend 10-day recency to 20-day. Expected 2-3x."
        ),
    },
    "golden_cross_50_200": {
        "post_investigation_verdict": "PRODUCER_OK + STRUCTURAL_LOW_FIRE",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py:757 emits f'ema_{fast}_{slow}_golden_"
            "cross'; ema_50_200_golden_cross valid signal). Single-gate dual (LONG "
            "= golden_cross; SHORT = death_cross + borrow). 8 fires close to B660 "
            "baseline post-B725 scaled expectation. 50/200 EMA crosses fire ~1-2/yr "
            "per ticker structurally. ACTIONS: universe expansion; verify borrow_ok "
            "blocking on SHORT side."
        ),
    },
    "golden_cross_20_50": {
        "post_investigation_verdict": "PRODUCER_OK + REDUNDANT_200EMA_GATE",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py:757 f'ema_20_50_golden_cross'). Dual "
            "gate + 200-EMA regime gate. 6 fires suggests 200-EMA gate blocks most "
            "cross events. ACTION: LOOSEN - drop 200-EMA regime gate (EMA 20/50 cross "
            "IS trend-direction signal per feedback_avwap_redundant precedent). "
            "Expected 3-5x uplift."
        ),
    },
    "adx_initiation": {
        "post_investigation_verdict": "PRODUCER_OK + EVENT_STRUCTURAL_RARE",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py:894 emits adx_cross_up = adx>25 AND "
            "padx<=25). Live test AAPL adx=15.8 (not trending), SPY adx=22.7 (near "
            "threshold; not yet crossed). adx_di_bull/bear also emit. 2 fires reflects "
            "ADX cross-25 event rarity (~2-5/yr per ticker) + DI direction filter. "
            "ACTIONS: (1) LOOSEN threshold adx>25 to adx>20 - broader trend initiation; "
            "(2) universe expansion. Expected 3-5x uplift."
        ),
    },
    "camarilla_r4_breakout": {
        "post_investigation_verdict": "PRODUCER_OK + POST_B641_REFRAMED",
        "post_investigation_recommendation": (
            "Producer VERIFIED (technical.py compute_pivots emits cam_r4 signals). "
            "B641 W10 renamed strat_camarilla_r3_breakout -> strat_camarilla_r4_"
            "breakout per Camarilla source-system re-anchor (R3=fade per Slim Khan/"
            "Nick Scott; R4=breakout level). REFRAMED POST-B879 as daily-momentum-"
            "context. 30 fires at MARGINAL boundary. ACTIONS: (1) verify Camarilla "
            "R4/S4 producer post-B641 rename fires correctly; (2) LOOSEN volume "
            "threshold if present. Expected 1.5-2x uplift."
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    for col in ("post_investigation_verdict", "post_investigation_recommendation"):
        if col not in df.columns:
            df[col] = ""

    updated = 0
    for strat, data in TURN_6_INVESTIGATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    total_investigated = (df["post_investigation_verdict"].fillna("").str.len() > 0).sum()
    print(f"Turn 6 FINAL complete: {updated} strategies updated.")
    print(f"Total investigations: {total_investigated} of 46.")
    print()
    print("=== TURN 6 CRITICAL FINDINGS ===")
    print("1. INDEX REBALANCE DATA MISSING: data_prefetch/derived/")
    print("   index_rebalance_events.parquet does NOT exist.")
    print("   4 strategies get 0 signals (post_inclusion/deletion/pre_rebalance).")
    print("   ACTION: implement Sprint 5 DEC-380 prefetch OR mark as DISABLED-DATA")
    print()
    print("2. BORROW_OK FILTER SUSPECT: macd_crossover_short (11f) has ~10x")
    print("   underfire suggesting borrow filter blocks SHORT candidates.")
    print("   Same finding surfaced in Turn 1 ichimoku_cloud_breakdown.")
    print()
    print("3. GOLDEN_CROSS_20_50 EMA200 gate redundant - LOOSEN 3-5x uplift.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
