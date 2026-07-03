#!/usr/bin/env python
"""Council 236 Investigation Turn 2 (2026-07-03) — BB_SQUEEZE + SEASONAL.

SCOPE: 4 strategies
  1. bb_squeeze_volume (0 fires, MED)
  2. bollinger_tight (7 fires, HIGH)
  3. squeeze_breakout (39 fires, MED)
  4. halloween_seasonal_long (1 fire, HIGH) — CRITICAL: 300x underfire

PRODUCER FILES REVIEWED:
  - technical.py:1307-1378 compute_bollinger (bb_reclaim signals)
  - technical.py:1488-1520 compute_squeeze (squeeze_fire_up/dn)
  - calendar_effects.py:136-197 compute_calendar_signals (halloween_first_day)

FINDINGS:

bb_squeeze_volume:
  Producer verified correct. squeeze_fire_up EVENT semantics per B390 fix
  (2026-05-26 owner directive). Gate stack: squeeze_fire_up + vol_spike_2x
  + above_vwap = 3-way AND with EVENT + 2 STATE. Universe-agnostic setup
  but structurally rare joint.

bollinger_tight:
  Producer verified. Post-B801 EVENT-converted (bb_20_15_reclaim_from_lower
  _recent_3d OR bb_20_20_reclaim_from_lower_recent_3d). B660 baseline
  6,725/yr STATE -> ~673/yr EVENT (10x reduction). Batch A scaled expected
  ~803 fires. Actual 7 = 115x underfire.

  SUSPICIOUS: bollinger_lower fires 29 (Batch A). bollinger_tight uses same
  reclaim EVENT signals OR'd across 1.5+2.0 sigma bands (should fire MORE)
  yet fires LESS (7 vs 29). Delta 4x in wrong direction.

  Possible cause: bollinger_tight's VIX-conditional RSI thresholds (normal
  VIX = 45/55) may be TIGHTER than bollinger_lower's (~35-40). Combined
  with the OR-of-two-BB-widths logic vs single-width in bollinger_lower.

squeeze_breakout:
  Producer verified. Single-gate: squeeze_fire_up. No consumer-side gate
  stack. 39 fires = actual squeeze release events across 150 tickers x 4y.
  Rate ~0.065/ticker/year = reasonable for canonical LazyBear TTM squeeze.

halloween_seasonal_long — CRITICAL FINDING:
  Producer VERIFIED correct via calendar_effects.py:196:
    out["is_halloween_period_first_day"] = bool(as_of.month == 11 and tdm == 1)
  Test coverage: test_batch723_calendar_state_to_event.py passes.

  Expected for Batch A window (2022-05-05 -> 2026-05-05):
    - 4 halloween-first-days: 2022-11-01, 2023-11-01, 2024-11-01, 2025-11-03
    - x 150 tickers = 600 potential signal-events
    - x ~50% price_above_ema_200 pass rate = 300 expected fires
  Actual: 1 fire = 300x underfire.

  totm_long (same B723 EVENT pattern) shows similar underfire: 12 actual
  vs ~4300 expected (360x). COMMON THREAD: both use calendar_effects.py
  B723 EVENT signals.

  ROOT CAUSE HYPOTHESES (ordered by likelihood):
    (a) @lru_cache on _cached_calendar_signals(str(as_of)) may return
        stale/wrong values for certain dates (screener.py:6500). Cache
        invalidation issue?
    (b) tdm (trading day of month) calculation edge case around US
        holidays or DST transitions
    (c) calendar_signals silently dropped for tickers where per-day
        as_of date is different from expected trading day boundary
    (d) Signal fires correctly but cube fan-out drops these trades
        (similar to prior cube bug fixed in Batch 1095)

  RECOMMENDED PROBE: on Batch A output, cross-check trade_log.csv for
  trades on entry_date 2022-11-01, 2023-11-01, 2024-11-01, 2025-11-03
  from ANY strategy that uses calendar signals. If NO calendar strategies
  fired on those dates, the plumbing itself is broken. If some strategies
  fired but not halloween_seasonal_long, the strategy-specific gate is
  the issue.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_2_INVESTIGATIONS = {
    "bb_squeeze_volume": {
        "post_investigation_verdict": "PRODUCER_OK",
        "post_investigation_recommendation": (
            "Producer VERIFIED CORRECT (technical.py:1488-1520 compute_squeeze). "
            "squeeze_fire_up EVENT semantics per B390 fix (2026-05-26). Gate stack "
            "squeeze_fire_up + vol_spike_2x + above_vwap is 3-way AND (EVENT + 2 STATE). "
            "0 fires reflects rare joint probability. ACTIONS: (a) LOOSEN vol_spike_2x "
            "-> vol_above_avg per feedback (Bollinger 1992 canonical uses 'expansion + "
            "rising volume', no 2x mandate); (b) consider dropping above_vwap "
            "redundancy (squeeze release direction itself confirms momentum). Expected "
            "3-5x uplift."
        ),
    },
    "bollinger_tight": {
        "post_investigation_verdict": "PRODUCER_OK + THRESHOLD_INTERACTION_SUSPECT",
        "post_investigation_recommendation": (
            "Producer VERIFIED CORRECT (technical.py:1370-1371 bb_reclaim_from_lower/"
            "upper_recent_3d). Post-B801 EVENT-converted. Baseline scaled expected "
            "~803 fires; actual 7 = 115x underfire. INVESTIGATE FURTHER: bollinger_lower "
            "fires 29 (4x more) despite bollinger_tight using OR-of-two-BB-widths "
            "which should fire MORE. Likely bollinger_tight's VIX-conditional RSI "
            "thresholds (normal VIX = 45/55; low VIX = 40/60; high VIX = 50/50) "
            "combined with rsi_2<10 OR rsi_14<thr tighten more than bollinger_lower's "
            "(35/65 canonical). ACTIONS: (a) audit RSI threshold configuration - "
            "bollinger_tight may need widen to match Connors canonical (rsi_14 < 40 "
            "for LONG); (b) verify bb_20_15_reclaim_from_lower_recent_3d producer "
            "fires proportionally to bb_20_20 variant."
        ),
    },
    "squeeze_breakout": {
        "post_investigation_verdict": "PRODUCER_OK + STRUCTURAL_LOW_FIRE",
        "post_investigation_recommendation": (
            "Producer VERIFIED CORRECT (technical.py:1488-1520). Single-gate: "
            "squeeze_fire_up. 39 fires = 0.065/ticker/year = reasonable for canonical "
            "LazyBear TTM squeeze release rate. No consumer-side gate stack to loosen. "
            "ACCEPT AS STRUCTURAL. Universe expansion (Batch B / T3) primary lever. "
            "Alternatively add secondary tier boost/scoring on top of squeeze_fire_up."
        ),
    },
    "halloween_seasonal_long": {
        "post_investigation_verdict": "PRODUCER_LIKELY_BUG_OR_PLUMBING",
        "post_investigation_recommendation": (
            "Producer code VERIFIED CORRECT (calendar_effects.py:196). Test coverage "
            "verified via test_batch723_calendar_state_to_event.py. BUT actual behavior "
            "SEVERELY INCONSISTENT WITH DESIGN: expected ~300 fires (4 halloween-"
            "first-days x 150 tickers x ~50% EMA200 pass), actual 1 = 300x underfire. "
            "Same 300-400x underfire pattern on totm_long (12 vs ~4300 expected) which "
            "uses same B723 calendar EVENT signals. COMMON THREAD: calendar_effects.py "
            "B723 signals. LIKELY ROOT CAUSES: (a) @lru_cache on _cached_calendar_"
            "signals returning stale values; (b) tdm calculation edge case; (c) "
            "signals silently dropped per-ticker; (d) cube fan-out drops trades. "
            "ACTIONS: (1) URGENT runtime probe - check trade_log.csv for ANY strategy "
            "fires on 2022-11-01/2023-11-01/2024-11-01/2025-11-03. If ZERO calendar "
            "strategies fired, plumbing is broken (BLOCKS Batch B). If some fired, "
            "strategy-specific issue. (2) family-wide audit of all B723-converted "
            "strategies: totm_long, halloween_seasonal_long, is_pre_holiday consumers."
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
    for strat, data in TURN_2_INVESTIGATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"Turn 2 investigation complete: {updated} strategies updated.")
    print()
    print("=== TURN 2 VERDICTS ===")
    print("bb_squeeze_volume:        PRODUCER_OK - loosen vol_2x -> vol_above_avg")
    print("bollinger_tight:          PRODUCER_OK - RSI/VIX threshold config suspect")
    print("squeeze_breakout:         PRODUCER_OK - structural low-fire, accept")
    print("halloween_seasonal_long:  URGENT - producer/plumbing likely bug (300x underfire)")
    print("                          Same pattern on totm_long (family-wide B723 issue)")
    print("                          BLOCKS Batch B until root cause identified")

    return 0


if __name__ == "__main__":
    sys.exit(main())
