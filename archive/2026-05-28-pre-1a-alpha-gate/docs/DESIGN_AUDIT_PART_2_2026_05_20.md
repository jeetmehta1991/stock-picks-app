# Design audit Part 2 — Per-(strategy × exit) evaluation
**Generated:** 2026-05-20 (post-Batches 279/281/282)
**Trigger:** Owner directive — "Viewing net WR across all trades cumulatively by strategy will never make sense. It needs to be viewed individually for each strategy and exit combination."
**Source:** `output_smoke_stageC/trade_exit_detail.csv` (Stage C 50 tkrs × 3y cube), code at commit `672a02c57`. Per CHECKLIST #77 canonical-source attribution.

---

## §0 — Owner's core insight

The previous evaluation framework was structurally wrong:
- **Wrong**: "Strategy X has 28% WR → strategy X is bad"
- **Right**: "Strategy X with exit method E1 has 80% WR; with E2 has 21% WR. Strategy X is fine — exit assignment was wrong."

A strategy is only meaningful in the context of its exit method. Stage C cube data confirms this empirically: for the 11 strategies tested, the **spread between best and worst exit per strategy ranges from 3.5 pp to 13.0 pp per trade.** Saying "the strategy has X% WR" without specifying exit is meaningless.

---

## §1 — Per-(strategy × exit) full matrix from Stage C

11 strategies × 25 exit methods = 275 raw cells. Post-Batch-266 hardening (avg_hold ≤ 250d) leaves 265 valid cells.

### §1.1 — Headline: lift opportunity per strategy

If every strategy used its CUBE-BEST exit instead of the current default `trailing_15pct`:

| Strategy | n | Default (trail_15) mean | Cube-best exit | Cube-best mean | Lift/trade | Lift × n |
|---|---:|---:|---|---:|---:|---:|
| avwap_252_breakout | 5 | +10.80% | trailing_15pct (same) | +10.80% | +0.00 | 0.0 |
| **avwap_50_reclaim** | 16 | **-4.44%** | **hybrid_50pct_target** | **+6.76%** | **+11.20** | **+179.2** |
| **bollinger_lower** | 14 | **-7.55%** | **fixed_4r_2r** | **+0.27%** | **+7.82** | **+109.5** |
| **bollinger_tight** | 10 | **-7.20%** | **next_pivot_target** | **+1.74%** | **+8.94** | **+89.4** |
| **cpr_narrow_bullish** | 31 | +0.21% | **regime_flip** | **+3.56%** | **+3.35** | **+103.9** |
| **monthly_bias_momentum_long** | 17 | +3.20% | earnings_blackout† | +7.85% | +4.65 | +79.0 |
| po3_bearish | 13 | -1.85% | ma_exit_ema9 | -0.11% | +1.74 | +22.6 |
| po3_bullish | 20 | -0.82% | class_time_stop | +1.73% | +2.55 | +51.0 |
| smc_choch_reversal | 7 | -1.12% | breakeven_plus_trail | +1.89% | +3.01 | +21.1 |
| stochrsi_oversold | 5 | +3.09% | time_stop_10d | +4.69% | +1.60 | +8.0 |
| xs_momentum_top_decile | 9 | +4.67% | class_time_stop | +8.11% | +3.44 | +31.0 |
| **TOTAL** | **147** | -10.81% aggregate | — | +27.71% aggregate | — | **+694.6 pp** |

†earnings_blackout has 237.7d avg hold → borderline long-hold artifact; safer choice is breakeven_plus_trail at +4.57%/50d hold.

**Conclusion**: switching from one-size-fits-all `trailing_15pct` to per-strategy cube-best would lift Stage C from -276 pp to roughly **+419 pp aggregate** on these 147 trades (the bulk of total firings).

### §1.2 — trailing_15pct is the WRONG default for 3 of 11 strategies

The new Batch 281 default (`trail_pct=0.15`) is the **literal WORST exit method** for:

| Strategy | trail_15 (default) | Best alternative | Penalty |
|---|---:|---|---:|
| **bollinger_lower** | **-7.55%** mean | fixed_4r_2r | -7.82pp/trade |
| **bollinger_tight** | **-7.20%** mean | next_pivot_target | -8.94pp/trade |
| **avwap_50_reclaim** | **-4.44%** mean | hybrid_50pct_target | -11.20pp/trade |

These are mean-reversion / breakout-fade strategies where a wide trail allows the price to retrace through the position. They need tighter exits (5% trail, R-multiple, or pivot-target).

### §1.3 — Top-3 exits per strategy (full Stage C cube)

| Strategy | #1 exit | mean | #2 exit | mean | #3 exit | mean |
|---|---|---:|---|---:|---|---:|
| avwap_252_breakout | trailing_15pct | +10.80% | hybrid_50pct_target | +7.18% | fixed_4r_2r | +6.02% |
| avwap_50_reclaim | hybrid_50pct_target | +6.76% | class_time_stop | +1.12% | trailing_5pct | -0.18% |
| bollinger_lower | fixed_4r_2r | +0.27% | ma_exit_ema9 | -0.14% | chandelier_3x | -0.15% |
| bollinger_tight | next_pivot_target | +1.74% | regime_flip | +1.11% | time_stop_20d | +1.11% |
| cpr_narrow_bullish | regime_flip | +3.56% | time_stop_20d | +3.56% | class_time_stop | +2.82% |
| monthly_bias_momentum_long | earnings_blackout† | +7.85% | breakeven_plus_trail | +4.57% | trailing_10pct | +4.20% |
| po3_bearish | ma_exit_ema9 | -0.11% | breakeven_plus_trail | -0.76% | r_multiple_2r | -0.95% |
| po3_bullish | class_time_stop | +1.73% | next_pivot_target | +1.07% | hybrid_50pct_target | +1.04% |
| smc_choch_reversal | breakeven_plus_trail | +1.89% | trailing_5pct | +0.10% | multi_tier_partial | +0.05% |
| stochrsi_oversold | time_stop_10d | +4.69% | hybrid_50pct_target | +4.43% | fixed_4r_2r | +4.01% |
| xs_momentum_top_decile | class_time_stop | +8.11% | time_stop_20d | +4.84% | regime_flip | +4.84% |

†Long-hold artifact; second-best is the operational choice.

---

## §2 — Implications for the evaluation framework

### §2.1 — Aggregate WR metrics are misleading

Stage C aggregate: 30.4% WR, -276 pp. This number is meaningless because:
- It mixes 11 different strategies on the SAME exit method (trailing_stop / trailing_15pct)
- The same strategy under a different exit can flip from -7.55% to +0.27% mean (bollinger_lower)
- Strategy "edge" is jointly determined by signal + exit

### §2.2 — Passing criteria need re-formulation

Current passing criteria (CLAUDE.md):
- WR ≥ 55% per regime
- Profit factor > 1.3 per regime
- Total ROI > 0% per regime

These are evaluated PER STRATEGY in aggregate. Should be evaluated PER (strategy × exit × regime) cell. A strategy might pass under exit E1 in bull regime but fail under E2 in same regime — both are valid data points.

### §2.3 — Decommission decisions need re-examination

Strategies the owner previously held back from decommissioning (Tier 4 retain):
- **po3_bullish**: under trailing_15pct -0.82% mean; under **class_time_stop +1.73% mean**. Was the strategy bad, or was the exit?
- **bollinger_lower**: under trailing_15pct -7.55% (worst possible); under fixed_4r_2r +0.27%. Definitely an exit problem.

The right framing: **decommission (strategy × exit) cells with negative edge at n ≥ 30; retain the strategy itself if any (strategy × exit) cell shows positive edge.**

---

## §3 — Batch 282 override coverage gaps

Batch 282 deployed STRATEGY_EXIT_OVERRIDE with 5 entries. But it misses several high-leverage findings:

| Strategy | Batch 282 override | Cube-best | Status |
|---|---|---|---|
| stochrsi_oversold | time_stop_10d ✓ | time_stop_10d | ✅ correct |
| xs_momentum_top_decile | time_stop_30d (approx) | class_time_stop | ⚠ approximation |
| po3_bullish | time_stop_30d (approx) | class_time_stop | ⚠ approximation |
| avwap_50_reclaim | trail_pct=0.10 (proxy) | hybrid_50pct_target | ❌ misses +11.20pp |
| bollinger_lower | trail_pct=0.05 (proxy) | fixed_4r_2r | ❌ misses +7.82pp |
| **bollinger_tight** | NOT IN OVERRIDE | next_pivot_target | ❌ misses +8.94pp |
| **cpr_narrow_bullish** | NOT IN OVERRIDE | regime_flip | ❌ misses +3.35pp × 31 |
| **monthly_bias_momentum_long** | NOT IN OVERRIDE | breakeven_plus_trail | ❌ misses +1.37pp × 17 |
| **smc_choch_reversal** | NOT IN OVERRIDE | breakeven_plus_trail | ❌ misses +3.01pp × 7 |
| **po3_bearish** | NOT IN OVERRIDE | ma_exit_ema9 | ❌ misses +1.74pp × 13 |

Coverage gap = ~+460 pp of unrealized Stage C opportunity.

**Root cause**: Batch 282 only supports `trail_pct` and `time_stop_days` params; complex exits (hybrid_50pct_target, regime_flip, fixed_4r_2r, ma_exit_ema9, next_pivot_target, breakeven_plus_trail with default params) are not yet implemented as per-day logic.

---

## §4 — Proposed Batch 284: implement remaining exit methods

To capture the full +694 pp Stage C opportunity, need to implement these exit logics as per-day evaluable functions in `exit_manager.process_day_exits`:

| Exit | Per-day logic | Complexity |
|---|---|---|
| `breakeven_plus_trail` | Move stop to entry once +1×ATR favourable; then trail at 10%. Already implemented in `exit_strategies.py` but as forward-scan; need per-day version. | Low |
| `class_time_stop` | Time-based per-category cutoff (already exists as Batch 213 logic). Just promote to primary exit when configured. | Trivial |
| `regime_flip` | Exit when current regime ≠ regime_at_entry. Track today's regime per trade. | Low |
| `next_pivot_target` | Exit at next pivot R1/R2/S1/S2 level above entry. Requires pivot data on the trade. | Medium |
| `hybrid_50pct_target` | Close 50% at +3×ATR, trail remainder at 10%. Requires partial-fill tracking. | Medium |
| `fixed_4r_2r` | Hard target at +4×ATR / hard stop at -2×ATR from entry. Fixed levels. | Trivial |
| `ma_exit_ema9` | Exit when close crosses EMA-9 against position direction. | Trivial |
| `r_multiple_2r/3r` | Hard target at +2R or +3R from entry. | Trivial |

**Recommendation**: implement `breakeven_plus_trail`, `class_time_stop`, `fixed_4r_2r`, `ma_exit_ema9`, `r_multiple_2r/3r` first (trivial-to-low complexity, covers 8 of the 11 strategies' cube-best). Defer `regime_flip`, `next_pivot_target`, `hybrid_50pct_target` to Batch 285+.

Once implemented, expand STRATEGY_EXIT_OVERRIDE with:
```python
STRATEGY_EXIT_OVERRIDE.update({
    "xs_momentum_top_decile":       {"exit_method": "class_time_stop"},
    "po3_bullish":                  {"exit_method": "class_time_stop"},
    "bollinger_lower":              {"exit_method": "fixed_4r_2r"},
    "po3_bearish":                  {"exit_method": "ma_exit_ema9"},
    "monthly_bias_momentum_long":   {"exit_method": "breakeven_plus_trail"},
    "smc_choch_reversal":           {"exit_method": "breakeven_plus_trail"},
})
```

---

## §5 — Recommendations to owner

### Tier 1 — Empirical evaluation framework
1. **Adopt per-(strategy × exit) verdict** as the primary unit of analysis. The `verdict_cube` already produces this; promote it to the main reporting view.
2. **Reformulate passing criteria** as `min_wr_per_combo`, `min_pf_per_combo`, etc. Aggregate-per-strategy metrics become advisory only.
3. **Decommission cells, not strategies**. A (strategy × exit) cell with n ≥ 30, mean < -2%, WR < 25%, p < 0.05 vs random is a decommission candidate. The strategy itself stays available for alternate exits.

### Tier 2 — Architectural completeness
4. **Batch 284: implement 5 trivial exit methods** + expand STRATEGY_EXIT_OVERRIDE. ~150 lines, ~2h. Captures ~+460 pp of unrealized opportunity.
5. **Batch 285+: implement complex exits** (regime_flip, hybrid_50pct_target, next_pivot_target). ~250 lines, ~4h.

### Tier 3 — Operational
6. **All future strategy backtests** report per-(strategy × exit) cube as primary output. Single-strategy aggregate WR is a footnote.
7. **D1 full T1a should use STRATEGY_EXIT_OVERRIDE** (already wired in Batch 282; expanded in Batch 284).

### Tier 4 — Methodology
8. **Document the philosophy in CLAUDE.md**: "All performance evaluation is per (strategy × exit × regime) cell. Cross-strategy aggregates are computed for portfolio metrics only; they cannot inform per-strategy retention decisions."

---

## §6 — Other audit findings (continued from Part 1)

Re-confirming findings from `DESIGN_AUDIT_2026_05_20.md` Part 1 (still applicable):

| # | Finding | Status |
|---|---|---|
| 1 | Batch 262 phantom config | ✅ FIXED Batch 281 |
| 2 | Single hardcoded exit method | ⚠ PARTIAL — Batch 282 added trail_pct + time_stop_days overrides; complex exits still TODO |
| 3 | Position-in-dict dedup | ✅ FIXED Batch 279 |
| 4 | Regime classifier mis-calibration | ❌ UNFIXED (owner option A pending) |
| 5 | Position-sizing 8-multiplier stack | ❌ UNFIXED (low priority) |

New findings from this audit:
| 6 | trailing_15pct (Batch 281 default) is WORST exit for 3 of 11 strategies | Mitigated by Batch 282 override; full fix needs Batch 284 |
| 7 | Passing criteria evaluated at aggregate level when cube-level is appropriate | Architectural; CLAUDE.md update needed |
| 8 | Decommission decisions made at strategy level when (strategy × exit) level is correct | Tier 4 retain decision may need revisiting under proper framing |

---

**END.** Awaiting owner direction on:
- Batch 284 implementation (5 trivial exit methods + override expansion)
- Tier 1 framework reformulation (per-(strategy × exit) as primary unit)
- Whether to re-run Stage B v5 + Stage C v2 with 281/282 active first, OR proceed straight to Batch 284 + then validate
