#!/usr/bin/env python
"""Phase 1 COMPREHENSIVE CORRECTION 2 (owner directive 2026-07-02).

After vol_spike naming fix, owner demanded comprehensive audit against
technical.py. Found 6 additional direction/reference errors:

CATEGORY A — WRONG DIRECTION (STATE -> EVENT framed as LOOSEN):
  A1. institutional_recent_init_momentum_long
      Original rec: macd_12_26_9_bullish (STATE) -> macd_12_26_9_crossover_up (EVENT)
      BUG: STATE fires ~30-50% of bars; EVENT fires ~1-2%. Going STATE->EVENT
      TIGHTENS the gate (fires less), not loosens.

  A2. institutional_buy_momentum_long
      Same STATE->EVENT bug. Was flagged HIGH priority based on wrong direction.

CATEGORY B — WRONG DIRECTION (dropping STATE components from UNION = tighter):
  B1. squeeze_breakout_with_smart_money_long
      Original rec: 'LOOSEN smart_money to EVENT-only (drop STATE 13F)'
      BUG: _has_smart_money_buy(s) is a UNION of 10+ components (5 EVENT + 5 STATE).
      Dropping STATE components makes the union NARROWER = fewer bars pass = TIGHTER.

  B2. xs_momentum_with_smart_money_long: same pattern as B1
  B3. 52w_high_breakout_with_smart_money_long: same pattern as B1

CATEGORY C — REFERENCED SIGNAL DOESN'T EXIST:
  C1. mfi_oversold_with_smart_money_long
      Original rec: '(mfi_oversold OR mfi_14 < 30)'
      BUG: mfi_14 is NOT a signal in technical.py. Producer emits 'mfi' (numeric)
      and 'mfi_oversold' (bool < 20). Correct reference is 'mfi < 30' or
      producer-side widening.

CORRECT FRAMING for STATE->EVENT: this is a SIGNAL-TEMPORALITY CORRECTION per
feedback_signal_temporality (make signal semantics honest), NOT a fire-count
LOOSENING. Only the OR-alternative (drop the AND requirement entirely) is
directionally looser.

CORRECT FRAMING for dropping STATE from smart_money union: this is same class -
signal-temporality correction, TIGHTENS the gate (docstring-alpha honesty).
Fire-count LOOSENING would be OPPOSITE: expand to broader union or drop the
AND requirement.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


CORRECTIONS = {
    "mfi_oversold_with_smart_money_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: 'mfi_14' does NOT exist as a signal in producer. "
            "Producer emits 'mfi' (numeric value) + 'mfi_oversold' (bool, mfi < 20). "
            "CORRECTED LOOSEN: use 's.get(\"mfi\", 50) < 30' (raw numeric comparison) "
            "as OR-alternative to mfi_oversold. Broader (~15% of bars) vs mfi_oversold "
            "(~5% of bars). Retain EMA200 + smart_money as confluence. Expected fire "
            "uplift 2-3x."
        ),
        "notes_suffix": (
            " [CORRECTED 2026-07-02: mfi_14 doesn't exist; use s.get('mfi') numeric.]"
        ),
    },
    "institutional_recent_init_momentum_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: STATE macd_12_26_9_bullish (~30-50% of bars) -> "
            "EVENT macd_12_26_9_crossover_up (~1-2% of bars) is TIGHTENING not "
            "loosening. Original 'LOOSEN' claim was direction-wrong. "
            "CORRECTED LOOSEN: keep macd_12_26_9_bullish AND change AND-with-EMA200 to "
            "OR (any of: MACD bullish OR rsi > 50 OR MACD histogram positive). "
            "Alternatively: drop MACD gate entirely (institutional + trend thesis only) "
            "= true loosening 2-3x. STATE->EVENT is a signal-temporality correction per "
            "feedback_signal_temporality (semantics/honesty), NOT fire-count loosening."
        ),
        "notes_suffix": (
            " [CORRECTED 2026-07-02: STATE->EVENT is TIGHTER not looser; direction "
            "reversed. Prior rec conflated signal-temporality-correction with fire-"
            "loosening.]"
        ),
        "priority": "MED",  # was MED already, keep
    },
    "institutional_buy_momentum_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: Same direction bug as institutional_recent_init_"
            "momentum_long. STATE macd_12_26_9_bullish (~30-50%) -> EVENT crossover_up "
            "(~1-2%) is TIGHTENING not loosening. "
            "CORRECTED LOOSEN options: (a) drop MACD gate entirely - isolates "
            "institutional + trend thesis, expected fire uplift 1.5-2x (80 -> 120-160, "
            "VIABLE); (b) keep MACD STATE but change AND to OR with rsi > 50 - broader "
            "momentum confluence. Priority DOWNGRADED from HIGH to MED since only "
            "drop-MACD alternative is genuinely looser."
        ),
        "notes_suffix": (
            " [CORRECTED 2026-07-02: STATE->EVENT is TIGHTER not looser; priority "
            "downgraded HIGH -> MED. Only 'drop MACD' alternative is true loosening.]"
        ),
        "priority": "MED",  # downgraded from HIGH
    },
    "squeeze_breakout_with_smart_money_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: Dropping STATE 13F components from _has_smart_money_"
            "buy(s) UNION makes union NARROWER (fewer bars pass) = TIGHTENING not "
            "loosening. Original 'LOOSEN to EVENT-only' was direction-wrong. "
            "CORRECTED LOOSEN: drop smart_money AND requirement entirely OR change to "
            "OR with any single component. Signal-temporality correction (drop STATE) "
            "is separate from fire-loosening; do it for docstring honesty per "
            "feedback_signal_temporality, but expect FEWER fires. Expected true "
            "loosening 2-3x by dropping AND requirement."
        ),
        "notes_suffix": (
            " [CORRECTED 2026-07-02: Dropping STATE from union is TIGHTER not looser. "
            "True loosening = drop smart_money AND requirement.]"
        ),
    },
    "xs_momentum_with_smart_money_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: Same UNION-narrowing bug as squeeze_breakout_"
            "with_smart_money. Dropping STATE 13F from _has_smart_money_buy union is "
            "TIGHTER not looser. "
            "CORRECTED LOOSEN: drop smart_money AND requirement (ablate to isolate "
            "pure J-T 12-1 top-decile momentum). Expected true loosening 2-3x. Signal-"
            "temporality separately correct for docstring but not fire-loosening."
        ),
        "notes_suffix": (
            " [CORRECTED 2026-07-02: Dropping STATE from union is TIGHTER not looser.]"
        ),
    },
    "52w_high_breakout_with_smart_money_long": {
        "recommendation": (
            "CORRECTED 2026-07-02: Same UNION-narrowing bug. Dropping STATE 13F from "
            "_has_smart_money_buy is TIGHTER not looser. "
            "CORRECTED LOOSEN: drop smart_money AND requirement (isolate 52w-breakout "
            "pure thesis) OR change smart_money AND to OR-with-secondary-tier. "
            "Expected true loosening 2-3x. B613 F1 docstring reframe about EVENT vs "
            "STATE was about ATTRIBUTION HONESTY, not fire-loosening."
        ),
        "notes_suffix": (
            " [CORRECTED 2026-07-02: Dropping STATE from union is TIGHTER not looser; "
            "B613 F1 was about docstring attribution, not fire-count loosening.]"
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    updated = 0
    priority_changed = 0
    for strat, data in CORRECTIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found")
            continue

        df.loc[mask, "recommendation"] = data["recommendation"]
        current_notes = df.loc[mask, "owner_review_notes"].values[0]
        df.loc[mask, "owner_review_notes"] = current_notes + data["notes_suffix"]

        if "priority" in data:
            old_priority = df.loc[mask, "priority"].values[0]
            df.loc[mask, "priority"] = data["priority"]
            if old_priority != data["priority"]:
                priority_changed += 1
                print(f"  Priority: {strat}: {old_priority} -> {data['priority']}")

        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"\nCorrection 2 applied: {updated} strategies fixed.")
    print(f"Priority changes: {priority_changed}")
    print()
    print("=== VERIFIED PRODUCER SIGNAL FACTS (from technical.py + smc_ict.py) ===")
    print("MFI signals:")
    print("  mfi           = numeric 0-100 value (line 1686)")
    print("  mfi_oversold  = mfi < 20 (line 1687)")
    print("  mfi_overbought = mfi > 80 (line 1688)")
    print("  mfi_14         DOES NOT EXIST")
    print()
    print("RSI signals (per p in [2, 9, 14, 21]):")
    print("  rsi_{p}         = numeric (line 523)")
    print("  rsi_{p}_oversold = <30 / _overbought = >70 (canonical)")
    print("  rsi_{p}_extreme_os = <20 / _extreme_ob = >80")
    print()
    print("MACD signals (per {fast}_{slow}_{sig}):")
    print("  macd_12_26_9_bullish       STATE ~30-50% of bars (macd > signal)")
    print("  macd_12_26_9_crossover_up  EVENT ~1-2% of bars (fresh cross)")
    print("  STATE -> EVENT = TIGHTENING (fewer bars pass)")
    print()
    print("Smart-money union:")
    print("  _has_smart_money_buy = UNION of 10+ components")
    print("  5 EVENT (insider_cluster_active, cfo_buy, large_dollar_buy, ...)")
    print("  5 STATE (institutional_strong_buy, institutional_buy, ...)")
    print("  Dropping STATE = narrower union = TIGHTER (fewer bars pass)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
