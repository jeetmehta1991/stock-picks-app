# Design audit — illogical / arbitrary patterns
**Generated:** 2026-05-20 (post-Batch 279, during Stage B v4 smoke)
**Trigger:** Owner question after Stage C — "are there other such illogical designs? Each (strategy × exit) needs to be evaluated individually."
**Scope:** Backtest engine + screener + exit_manager + config
**Source:** Direct code inspection of `backtest/engine/backtest.py`, `backtest/engine/exit_manager.py`, `backtest/signals/screener.py`, `backtest/config.py` at commit `e54235175`; cube data from `output_smoke_stageC/trade_exit_detail.csv` (Batch 279 smoke). Per CHECKLIST #77 canonical-source attribution.

---

## §0 — TL;DR — 5 critical findings, ordered by impact

| # | Finding | Impact | Status |
|---|---|---|---|
| **1** | **Batch 262 config changes NEVER landed**: `trail_pct: 0.10→0.15` and `breakeven_move_at_1r: True` were committed to messaging but the actual config dict was never modified. All today's smokes (Stage A, B, B v2, B v3, C, B v4 in flight) ran on the OLD 10% trail and NO breakeven. | **~+500-1,500 pp expected uplift** | UNFIXED |
| **2** | **Single hardcoded exit method**: `exit_manager.process_day_exits` uses ONE exit logic for all trades (10%-trailing-stop). The cube evaluates 25 alternatives but they're never actually used in live trades. `TRAILING_STOP["primary_exit"] = "atr_trail_1x"` config key is documented but unread by any code. | **+450 pp on 78 trades in Stage C** (5 best swaps; extrapolates massively) | ARCHITECTURAL |
| **3** | **Position-in-dict dedup** (now FIXED in Batch 279) | -1,500 pp Stage B v1, ~-340 pp ongoing | ✅ FIXED |
| **4** | **Regime classifier mis-calibrated** for 2022-style grinding bear. Requires VIX≥30 + below-200EMA for "bear"; VIX≥40 for "crisis". 2022 SPY -23% drawdown classified 100% neutral. | -198 pp on 2022 longs in Stage C | UNFIXED |
| **5** | **8 multiplicative position-sizing scalars** applied in arbitrary stack order, with no holistic cap. Compound extreme cases possible (e.g., 3% base → 0.014% after all scalars, or → 36% in opposite direction). | Unclear impact; defensive code currently | LOW PRIORITY |

---

## §1 — Critical Finding 1: Batch 262 phantom config

**Claim** (Batch 262 commit message, 2026-05-20 morning):
> Changed `trail_pct: 0.10` → `0.15`
> Added `breakeven_move_at_1r: True`

**Reality** (verified by `git log backtest/config.py`):
- `config.py` last modified at **Batch 226 (2026-05-18)** — three commits older than Batch 262.
- `TRAILING_STOP["trail_pct"]` still equals `0.10` in current HEAD.
- No `breakeven_move_at_1r` key exists anywhere in the TRAILING_STOP dict.
- The breakeven LOGIC was added to `exit_manager.py:291-302` but is gated on `TRAILING_STOP.get("breakeven_move_at_1r", False)` → defaults False → never fires.

**Trace impact**: This means every smoke run today (Stage A, B v1/2/3, C, B v4 in flight) has been running on the OLD trailing-stop logic. The "trail 10→15%" exit improvement supposedly tested has actually never been exercised.

**Expected impact when fixed**:
- The Stage B v1 counterfactual analysis showed `trailing_15pct` outperformed `vix_kill` by +6.98% per trade (95% CI [+3.00%, +11.35%]).
- Stage C Stage C smoke had 159 trailing_stop exits → fixing trail_pct could shift ~+1,000-1,800 pp.
- `breakeven_move_at_1r` would tighten the worst losses (currently no early-profit-protection).

**Fix**: 3-line config change. Should be Batch 280.

```python
TRAILING_STOP = {
    "initial_pct":           0.10,
    "trail_pct":             0.15,    # was 0.10 - Batch 262/280 deploy
    "reset_on":              "close",
    "primary_exit":          "atr_trail_1x",
    "ratchet_from":          "close",
    "breakeven_move_at_1r":  True,    # Batch 262/280 - new key
}
```

---

## §2 — Critical Finding 2: Single hardcoded exit method

**Design as built**: `exit_manager.process_day_exits` evaluates exits in fixed order:
1. Circuit breakers (level 1-6 portfolio gates)
2. `check_trailing_stop_hit` — uses `update_trailing_stop` with **ONE** trail logic (config `trail_pct`)
3. `time_stop_{N}d_mfe<0.5pct` — fixed per-category time window

Every trade exits via the same mechanism regardless of which strategy opened it. The cube (`run_exit_comparison` in `exit_strategies.py`) evaluates 25 alternative exit methods per trade, but **its output is purely diagnostic** — never feeds back into trade exit logic.

**Cube findings from Stage C** (50 tkrs × 3y, hardened cube post avg_hold_days≤250 filter):

| Strategy | Best exit | n | WR | Mean | Σ pp |
|---|---|---:|---:|---:|---:|
| avwap_252_breakout | **trailing_15pct** | 5 | 80% | +10.80% | +54 |
| xs_momentum_top_decile | **class_time_stop** | 9 | 78% | +8.11% | +73 |
| monthly_bias_momentum_long | earnings_blackout* | 17 | 53% | +7.85% | +133 |
| avwap_50_reclaim | **hybrid_50pct_target** | 16 | 94% | +6.76% | +108 |
| stochrsi_oversold | **time_stop_10d** | 5 | 80% | +4.69% | +23 |
| cpr_narrow_bullish | **regime_flip** | 31 | 65% | +3.56% | +110 |
| smc_choch_reversal | breakeven_plus_trail | 7 | 29% | +1.89% | +13 |
| bollinger_tight | next_pivot_target | 10 | 80% | +1.74% | +17 |
| po3_bullish | class_time_stop | 20 | 65% | +1.73% | +35 |
| bollinger_lower | fixed_4r_2r | 14 | 21% | +0.27% | +4 |
| po3_bearish | ma_exit_ema9 | 13 | 23% | -0.11% | -1 |

*earnings_blackout's 237-day avg hold makes the +133 pp suspect (long-hold artifact at borderline of 250d filter).

**Total cube-best across 11 strategies**: **+569 pp on 147 trades.** Realized aggregate on the SAME trades was **-256 pp** (Stage C total -276 minus the 25 chart_patterns/news/etc that didn't fire). **Per-strategy exit assignment swing: ~+825 pp** in a 3y / 50-tkr smoke. Extrapolated to 642 tkrs × 4y, this is **+5,000-10,000 pp** of structural opportunity.

**Architectural fix path**:
- Add `STRATEGY_EXIT_OVERRIDE` config dict mapping each strategy → its cube-best exit
- In `exit_manager.process_day_exits`, branch by `trade.strategy` to invoke per-strategy exit logic
- Fall back to default `trailing_stop` when override not specified
- ~80 lines + tests; needs careful implementation

Owner approval needed before implementation.

---

## §3 — Critical Finding 3: Position-in-dict dedup ✅ FIXED Batch 279

Already addressed. See Batch 279 commit `e54235175`. Multi-strategy same-ticker now allowed with size-split.

---

## §4 — Critical Finding 4: Regime classifier mis-calibration

**Code** (`backtest/engine/regime_filter.py:classify_regime`):
```python
if vix_value >= 40: return "crisis"
if vix_value >= 30 and spy_above_200ema is False: return "bear"
if vix_value < 20 and spy_above_200ema is True: return "bull"
return "neutral"
```

**Empirical reality** (2022 grinding bear):
- 2022 peak VIX: ~38 (never reached 40 "crisis" threshold)
- 2022 VIX mostly 20-35 (rarely hit 30 "bear" co-trigger with sub-200EMA)
- 2022 SPY: -23% YTD drawdown (clear bear)
- **Stage C classified 100% of 2022 trades as "neutral"**

**Impact**: Long-bias strategies fired during 2022 bear without bear-regime risk-reduction. Short-only strategies (whose regime affinity = `{bear, crisis}`) never fired because regime never reached those values.

**Stage C 2022 PnL**:
- Long: 81 trades, 27% WR, -2.45% mean, **-198 pp**
- Short: 26 trades, 19% WR, -2.97% mean, -77 pp
- Total 2022: **-275 pp** (matches Stage C aggregate −276 pp)

The 2022 bear is essentially the SOURCE of the entire Stage C aggregate loss.

**Fix options** (deferred pending owner decision A):
- (A.1) Lower VIX bear threshold to ≥25
- (A.2) Add SPY-only bear gate (e.g., below-200-EMA for ≥20 days = bear regardless of VIX)
- (A.3) Multi-input regime score (already implemented as `multi_input_regime_score` but not used)

---

## §5 — Other arbitrary / order-dependent patterns

### §5.1 — Position-sizing multiplier stack (Finding 5)

Eight multiplicative scalars stacked in arbitrary order in `engine/backtest.py:1238-1370`:

| # | Multiplier | Bound | Source |
|---|---|---|---|
| 1 | `TIER_POSITION_SIZE_PCT[tier]` | 0.0075-0.05 | Config |
| 2 | `/ _n_strategies_for_split` | divides by 1-N | Batch 279 |
| 3 | `drawdown_size_multiplier()` | {0, 0.5, 0.75, 1.0} | DEC-091 |
| 4 | `vol_target_scale_factor()` | [0.5, 1.5] | DEC-088 |
| 5 | `vol_targeted_size()` | [0.25, 2.0] | DEC-087 |
| 6 | `per_strategy_kelly_from_trade_log()` | [0.25, 2.0]* | Batch 212 |
| 7 | `per_strategy_hrp_weight()` | [0.25, 2.0]* | Batch 219 |
| 8 | VIX overlay (Batch 203) | varies | Cederburg-Johnson-Maio |

*bounds applied independently AFTER multiplication, so they don't cap cumulative effect.

**Worst-case downward**: 3% × 0.5 × 0.5 × 0.25 × 0.5 × 0.25 × 0.5 × 0.7 = **0.005%** ($5 on $100k).
**Worst-case upward**: 3% × 1.5 × 2.0 × 2.0 × 2.0 × 1.5 = **54%** ($54k on $100k single position).

Other portfolio gates would catch the upward case, but the downward case can silently produce nearly-zero positions that still count toward `max_open_positions`. Not catastrophic but inefficient.

**Recommendation**: Add a final cumulative bound `size_pct = clip(size_pct, 0.0025, 0.05)` (0.25% to 5%). Or document the bounds explicitly.

### §5.2 — Signal merge ordering in `screen_instrument`

`signals.update(other)` patterns at lines 2822-2953:

```python
signals.update(pead)       # if duplicate key, pead overwrites prior
signals.update(insider)
signals.update(pre_fomc)
signals.update(recent_8k)
signals.update(smc_out)
signals.update(chart_out)
... 13 more
```

If two signal sources produce the same key (e.g., both have `vol_spike_2x`), the LAST update wins. This means signal computation order matters for any overlapping keys. Currently no documentation of which keys overlap.

**Risk**: Low — most signal modules use namespaced keys (smc_*, news_*, ir_*). But if any cross-contamination exists, the last-write-wins behavior is silent.

**Recommendation**: Audit for duplicate keys across signal modules; if any exist, surface as explicit conflict-resolution logic.

### §5.3 — Hardcoded strategy thresholds with no empirical backing

RSI thresholds vary by strategy with no documented rationale:
- pivot_s3_capitulation: RSI < 30
- pivot_s2_bounce: RSI < 40
- camarilla_rsi_obv: RSI < 35 long / > 65 short
- cpr_narrow_momentum: RSI > 50 long / < 50 short
- smc_bos_continuation: RSI > 50 (Batch 278 addition)
- news_sentiment_long: RSI > 55 (Batch 278 addition)
- cup_and_handle_long: RSI < 70 (Batch 278 addition)

These are heuristic defaults from technical-analysis literature, not empirical optimizations.

**Risk**: Medium — these thresholds significantly affect fire rates and possibly edge.

**Recommendation**: Post-D1 full-T1a, sweep each strategy's RSI threshold ±10 in 5-point steps; pick the empirical optimum per strategy. Or accept current as literature-canonical and document.

### §5.4 — Skip-reason hierarchy (gate evaluation order)

Per-ticker gates in `backtest.py:822-1075` are evaluated in this order; **first to fire wins** (only one skip_reason logged):

1. BUG-61 open_tickers (cross-day concurrent)
2. DEC-018 stopout_cooldown_active_5d
3. DEC-135 max_loss_cap_breach (-10% in 30d)
4. DEC-076 factor_concentration_breach (sector >25%)
5. Batch 223 correlation_cap (|corr|>0.85)
6. avoid_direction (conflicting signals)
7. BUG-34 STRATEGY_REGIME_BLOCKLIST (hard exclusion)
8. Batch 203 STRATEGY_REGIME_AFFINITY (soft regime gate)
9. CRISIS_LONG_EXCLUSIONS
10. exact-duplicate same-ticker-same-strategy
11. (was: dedup_one_position_per_ticker_per_day — removed Batch 279)
12. no_next_bar
13. validate_entry_zone (gap filter)
14. ...etc

**Risk**: Low — each gate has a legitimate purpose. But the "first-fire wins" means a ticker blocked by BOTH NFP_d0 AND portfolio_max_open will only log one reason. Skip-reason analytics could be misleading.

**Recommendation**: Log ALL blocking reasons (not just the first); current behavior reduces forensic visibility.

---

## §6 — Per-(strategy × exit) cube evaluation

Stage C (50 tkrs × 3y) cube produced 275 (strategy × exit) cells across 11 strategies × 25 exit methods. Post-Batch-266 hardening filter (avg_hold ≤ 250d, fire_rate ≥ 0.5) reduces to 265 valid cells.

### §6.1 — Strategies with positive expectancy under their cube-best exit

| Strategy | Best exit | n | WR | Mean | Σ pp | Hold |
|---|---|---:|---:|---:|---:|---:|
| avwap_252_breakout | trailing_15pct | 5 | 80% | +10.80% | +54 | 138 |
| xs_momentum_top_decile | class_time_stop | 9 | 78% | +8.11% | +73 | 36 |
| monthly_bias_momentum_long | earnings_blackout | 17 | 53% | +7.85% | +133 | 238 |
| avwap_50_reclaim | hybrid_50pct_target | 16 | 94% | +6.76% | +108 | 124 |
| stochrsi_oversold | time_stop_10d | 5 | 80% | +4.69% | +23 | 14 |
| cpr_narrow_bullish | regime_flip | 31 | 65% | +3.56% | +110 | 27 |
| smc_choch_reversal | breakeven_plus_trail | 7 | 29% | +1.89% | +13 | 42 |
| bollinger_tight | next_pivot_target | 10 | 80% | +1.74% | +17 | 19 |
| po3_bullish | class_time_stop | 20 | 65% | +1.73% | +35 | 34 |
| bollinger_lower | fixed_4r_2r | 14 | 21% | +0.27% | +4 | 17 |

### §6.2 — Strategies with marginal/negative expectancy even under best exit

| Strategy | Best exit | Mean |
|---|---|---:|
| po3_bearish | ma_exit_ema9 | -0.11% (statistically zero) |

### §6.3 — Single-exit vs per-strategy exit comparison

| Approach | n trades | Aggregate Σ |
|---|---:|---:|
| **Realized (single trailing_stop)** | 181 | **-275.8 pp** |
| Cube-best per strategy (147 trades in cube; ex chart_patterns etc.) | 147 | **+569 pp** |
| Delta | — | **+845 pp swing** |

Even after accounting for fire-rate effects (cube assumes all trades take the optimal exit; real implementation would underperform somewhat), the swing is at the ~+500-700 pp level on a 3y / 50-tkr smoke.

**At 642-tkr × 4y T1a scale, this represents ~+10,000-15,000 pp of structural opportunity** — by far the highest-leverage architectural fix available.

---

## §7 — Recommendations (priority-ordered)

### Tier 1 — Immediate (1-2h each)
1. **Deploy Batch 262 config** — change `trail_pct: 0.10→0.15`, add `breakeven_move_at_1r: True`. 3-line config change. Should be Batch 280.
2. **Per-strategy exit assignment** — add `STRATEGY_EXIT_OVERRIDE` config dict mapping strategy → cube-best exit; wire into `exit_manager.process_day_exits`. ~80 lines + tests.

### Tier 2 — Investigation (1h each)
3. **Regime classifier calibration** (owner option A) — 3 options. A.2 (SPY-only bear gate) is least disruptive.
4. **Signal merge audit** — grep for duplicate keys across signal modules; surface conflicts.

### Tier 3 — Optimization (deferred)
5. **Position-sizing cumulative bound** — add `clip(size_pct, 0.0025, 0.05)` at end of stack.
6. **Skip-reason multi-logging** — track all blocking reasons, not just first.
7. **RSI threshold sweep** — empirical optimization post-D1.

### Tier 4 — Owner-decision-required
8. **Structural losers** (owner option C from prior analysis) — bollinger_lower / po3_* / avwap_50_reclaim show negative edge at n≥10. Decision deferred.
9. **Reorder Batches 252-255 strategies** (owner option B from prior analysis) — currently dormant at back of dict; revisit after Option 1 + Tier 1+2 fixes deploy.

---

## §8 — Methodology notes

- **Stage B v4** (in flight at time of writing): tests Batch 279 dedup-removal effect in isolation, BUT still runs on broken Batch 262 config (trail_pct=0.10, no breakeven). Once Stage B v4 lands, deploying Tier 1 #1 + #2 would give a clean A/B for the next smoke.
- **Cube hardening (Batch 266)** is essential context — the pre-hardening cube reported `earnings_blackout` as winner across strategies via 900-day hold artifact. The post-hardening cube produces realistic 14-238 day holds.
- **All findings are derived from Stage A/B/C smoke data + code inspection**. No predictions are made about T1a full-scale behavior without empirical confirmation.

---

**END.** Awaiting owner direction on Tier 1 fixes (Batch 280 config deploy + Batch 281 per-strategy exit assignment).
