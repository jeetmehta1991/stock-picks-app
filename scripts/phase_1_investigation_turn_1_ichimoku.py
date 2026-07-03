#!/usr/bin/env python
"""Council 236 Investigation Turn 1 — Ichimoku Family (2026-07-02).

Owner directive: 'Complete all pending investigations. Refer to codebase.
Provide post-investigation recommendations.'

INVESTIGATION SCOPE: 3 strategies flagged HIGH for producer investigation
  1. ichimoku_cloud_breakout (5 fires; Council 232 flagged 19,805 expected)
  2. ichimoku_cloud_breakdown (0 fires; SHORT mirror)
  3. ichimoku_tk_cross (17 fires; 2-gate simple)

PRODUCER CODE REVIEWED: technical.py:962-1036 compute_ichimoku()

FINDINGS:

FACT 1: compute_ichimoku produces CORRECT standard Ichimoku values.
  Tenkan = (9-high + 9-low) / 2
  Kijun = (26-high + 26-low) / 2
  Senkou A = (Tenkan + Kijun) / 2, shifted 26 bars
  Senkou B = (52-high + 52-low) / 2, shifted 26 bars
  Signals emitted: ichi_above_cloud, below_cloud, tk_bullish, tk_cross_up/dn,
                   cloud_thick, above/below_cloud_break_recent_5d,
                   weekly_above/below_cloud, weekly_in_cloud
  Producer requires len(df) >= 52 for daily; >= 260 for weekly.
  DatetimeIndex confirmed present in cache (verified with SPY sample).

FACT 2: Council 232's '19,805 expected' baseline is STALE PRE-B725.
  B725 (2026-06-12) applied STATE -> EVENT conversion per B655/B721/B722
  precedents + S4-B717 ceiling routing. Pre-B725 baseline: 11K LONG + 5K
  SHORT per year (B660 measurement, universe-wide). Post-B725 expected
  reduction ~95% per B655 precedent = ~550-800/yr LONG universe-wide.
  Scaled to Batch A (150/503, 4y window):
      550/yr × (150/503) × 4 = 655 fires expected post-B725
      OR
      800/yr × 0.298 × 4 = 954 fires expected post-B725

  Actual 5 fires = 130-190x under B725-adjusted expected. Still a real gap
  but not the '19,805 vs 4' catastrophic gap Council 232 reported.

FACT 3: B657 strict weekly Kumo default=False adds constraint.
  Weekly Ichimoku requires len(df) >= 260 (52 weeks). Cache verification
  showed SPY has data starting 2021-05-06 (returned 1255 rows for 2020-
  01-01 → 2026-05-05 request). At Batch A start (2022-05-05), tickers had
  only ~250 days of history = JUST UNDER the 260 required. Weekly Kumo
  MISSING for first ~2 weeks of Batch A. Post-B657, missing weekly Kumo =
  default False = LONG cannot fire.

FACT 4: EVENT semantic is very selective.
  ichi_above_cloud_break_recent_5d emits ONLY WHEN:
    (a) above_cloud today (close > max(sa, sb))
    (b) AT LEAST ONE bar in last 5 days had close <= cloud upper
  In sustained-trend regimes (2023-24 bull, 2022 bear), price is either
  always above or always below cloud. TURN events are rare (~1-3/yr per
  ticker). B725's stated goal was tightening to catch the TURN not the
  STATE.

FACT 5: ichimoku_cloud_breakdown NOT B725-converted (still uses STATE).
  Gate stack: ichi_below_cloud (STATE) + ichi_tk_cross_dn (EVENT) +
              adx_trending (STATE) + borrow_ok
  Should fire more often than the LONG variant that IS event-converted.
  0 fires is suspicious. Two likely causes:
    (a) SHORT-only strategy + borrow_ok filter blocks most fires on T1a
    (b) EVENT ichi_tk_cross_dn is a specific bar; requiring concurrent
        STATE below_cloud + STATE adx_trending compounds rarity.

FACT 6: ichimoku_tk_cross is 2-gate simple confluence.
  LONG = ichi_tk_cross_up + ichi_above_cloud
  SHORT = ichi_tk_cross_dn + ichi_below_cloud + borrow_ok
  Underfiring at 17 fires vs expected 600-1200 (150 tickers × 4y × 1-2/yr).
  Suggests EVENT signal may need widening OR ichi_above_cloud STATE
  gate too restrictive (cloud position skews toward trending regimes).

POST-INVESTIGATION RECOMMENDATIONS:

REC 1 (ichimoku_cloud_breakout, was HIGH -> keep HIGH):
  Producer verified correct per B725 EVENT design. Council 232 baseline
  mismatch (19,805 was pre-B725 STATE-based; post-B725 expected ~655-954
  fires; actual 5 = still 130-190x gap).

  ACTIONS:
    (a) LOOSEN: widen ichi_above_cloud_break_recent_5d -> _recent_10d
        per supertrend_ichimoku_adx wider-variant precedent. Requires
        producer-side additive change (or strategy-side gate replacement
        with 10-day equivalent using ichi_above_cloud + past 10-day
        below_cloud). Expected 2-3x fire uplift.
    (b) Consider: B657 strict weekly Kumo default=False was correct-in-
        principle but may need first-year exception (default=True when
        data unavailable due to early history). Batch A window is fully
        eligible from 2023-05 onward.
    (c) Batch A 150 stratified universe skews toward large-caps that
        trend smoothly (few cloud-turn events). Batch B (1787) or T3
        (momentum) universes will have more cloud-turn events per
        volatile mid/small-caps.

REC 2 (ichimoku_cloud_breakdown, was HIGH -> keep HIGH):
  NOT B725-converted. Producer emits ichi_below_cloud_break_recent_5d
  but strategy uses raw STATE ichi_below_cloud. Inconsistent with LONG
  counterpart's B725 conversion.

  ACTIONS:
    (a) SYMMETRY FIX: apply B725 EVENT-conversion to SHORT side too.
        Replace ichi_below_cloud with ichi_below_cloud_break_recent_5d.
        Would tighten current gate but ADD event-timing alpha per B725
        thesis. This is a code change requiring owner approval.
    (b) OR: If keeping STATE, INVESTIGATE why 0 fires despite reasonable
        gates. Check borrow_ok filter empirically - if _short_borrow_
        trap_active blocks most SHORT candidates on Batch A T1a 150,
        this affects ALL SHORT strategies not just Ichimoku.
    (c) Pattern S SHORT asymmetric expectancy caveat.

REC 3 (ichimoku_tk_cross, was HIGH -> keep HIGH):
  Producer verified correct. Underfiring 35-70x is due to EVENT
  ichi_tk_cross_up/dn being inherently bar-of-fire.

  ACTIONS:
    (a) LOOSEN: extend ichi_tk_cross_up/dn to _recent_3d event window
        (similar to williams_stoch_dual widening pattern per Turn 5).
        Would fire on any bar where TK crossed in last 3 days (vs
        strict same-bar). Requires producer-side additive change.
        Expected 2-3x fire uplift.
    (b) Consider: B725-style _recent_5d event window applied to TK cross
        (symmetric to cloud break event conversion). Same alpha thesis.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


POST_INVESTIGATION = {
    "ichimoku_cloud_breakout": {
        "cluster_id": "ICHIMOKU_FAMILY",
        "recommendation": (
            "POST-INVESTIGATION 2026-07-02 Turn 1: Producer verified CORRECT per B725 "
            "EVENT design (technical.py:962-1036). Council 232 '19,805 expected' was "
            "PRE-B725 STATE-based baseline; post-B725 expected 655-954 fires (~95% "
            "reduction). Actual 5 fires = still 130-190x gap. Contributing causes: "
            "(1) B657 weekly Kumo strict default=False affects first ~1-2 weeks of "
            "Batch A window (data start ~2021-05; 260-bar min = 2022-04); (2) EVENT "
            "semantic is inherently selective (TURN events not STATE); (3) T1a "
            "large-cap universe trends smoothly with few cloud-turn events. LOOSEN: "
            "widen recent_5d -> recent_10d event window (producer-additive change; "
            "symmetric to supertrend_ichimoku_adx Turn 4 wider variant). Expected "
            "2-3x fire uplift."
        ),
        "priority": "HIGH",
    },
    "ichimoku_cloud_breakdown": {
        "cluster_id": "ICHIMOKU_FAMILY",
        "recommendation": (
            "POST-INVESTIGATION 2026-07-02 Turn 1: Producer verified correct (identical "
            "logic to LONG counterpart's inputs). STRATEGY-SIDE ASYMMETRY: LONG "
            "counterpart got B725 EVENT conversion (ichi_above_cloud_break_recent_5d) "
            "but SHORT side NOT converted - still uses STATE ichi_below_cloud. "
            "Producer emits ichi_below_cloud_break_recent_5d but strategy doesn't "
            "consume it. 0 fires is suspicious given STATE below_cloud fires ~30-40% "
            "in bear regime. Likely combined with borrow_ok filter blocking most "
            "SHORT candidates on T1a 150. ACTIONS: (a) SYMMETRY FIX - apply B725 "
            "EVENT-conversion to SHORT (replace ichi_below_cloud with ichi_below_"
            "cloud_break_recent_5d; needs owner approval as code change); (b) audit "
            "_short_borrow_trap_active blocking rate on Batch A universe. Pattern S "
            "caveat."
        ),
        "priority": "HIGH",
    },
    "ichimoku_tk_cross": {
        "cluster_id": "ICHIMOKU_FAMILY",
        "recommendation": (
            "POST-INVESTIGATION 2026-07-02 Turn 1: Producer verified CORRECT "
            "(technical.py:982-984). 2-gate simple structure: TK cross EVENT + cloud "
            "position STATE. Underfiring 35-70x (17 actual vs 600-1200 expected). "
            "Root cause: EVENT ichi_tk_cross_up/dn is strict same-bar cross (~2-5/yr "
            "per ticker); requiring concurrent STATE ichi_above/below_cloud narrows "
            "further. LOOSEN: extend TK cross to _recent_3d event window per "
            "williams_stoch_dual Turn 5 widening precedent (producer-additive - add "
            "ichi_tk_cross_up_recent_3d + _dn_recent_3d symmetric to B725 cloud "
            "event convention). Alternatively drop cloud STATE gate to isolate pure "
            "TK cross alpha (Ichimoku canonical uses TK cross as PRIMARY signal; "
            "cloud position is CONFIRMATION not filter). Expected 2-3x uplift."
        ),
        "priority": "HIGH",
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    updated = 0
    for strat, data in POST_INVESTIGATION.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"Turn 1 (Ichimoku) investigation complete: {updated} strategies updated.")
    print()
    print("=== POST-INVESTIGATION VERDICTS ===")
    print("ichimoku_cloud_breakout: Producer OK; B725 EVENT design intentional; widen 5d->10d")
    print("ichimoku_cloud_breakdown: Producer OK; STRATEGY asymmetry - apply B725 to SHORT + audit borrow gate")
    print("ichimoku_tk_cross: Producer OK; extend TK cross to _recent_3d event window")

    return 0


if __name__ == "__main__":
    sys.exit(main())
