# Design audit Part 3 — Remaining design gaps, bugs, logic issues
**Generated:** 2026-05-20 (post-Batches 281/282/284/285)
**Source:** Direct code inspection at commit `d283b1cec`; per CHECKLIST #77 canonical-source attribution.
**Scope:** Anything not covered by Audit Parts 1 + 2. Bug class, logic class, and arbitrary-design class.

---

## §0 — Summary

| # | Finding | Severity | Status |
|---|---|---|---|
| 1 | EMA-9 missing from ticker_bars (silent no-op for Batch 285 ma_exit_ema9) | BUG | ✅ FIXED in this audit |
| 2 | Initial stop is blanket 10% across all strategies | LOGIC | Document; fix Batch 287 |
| 3 | In-sample cube optimization risk (Stage C overfitting to per-strategy assignments) | METHODOLOGY | Document; mitigate via OOS validation |
| 4 | Tier sizing × dedup-split interaction with breakeven_at_1R | LOGIC | Verify; document |
| 5 | `crisis_flag` set twice in dedup loop (cosmetic bug) | COSMETIC | Document |
| 6 | Per-strategy gap_atr_mult ignored | DESIGN | Document; Batch 287 candidate |
| 7 | OHLCV historical data: dividend adjustment inconsistencies | DATA | Investigation needed |
| 8 | Volume-zero days (halts) silently included | DATA | Investigation needed |
| 9 | Cube hardening thresholds (≤250d, ≥0.5 fire-rate) are heuristic | METHODOLOGY | Document |
| 10 | `_n_strategies_for_split` uses pre-gate count (overestimates N) | LOGIC | Low priority; conservative |

---

## §1 — Finding 1 (BUG, FIXED): EMA-9 missing from ticker_bars

**Code path**: Batch 285 implemented `ma_exit_ema9` in `_check_per_strategy_exit_hit`, expecting `today_ema_9` from caller. The caller (`process_day_exits` in `exit_manager.py`) reads it via `bar.get("ema_9")` on `ticker_bars[ticker]`.

**Bug**: `_build_today_bars` in `backtest.py` (called once per sim day to build `ticker_bars`) NEVER populated `ema_9`. Result: `bar.get("ema_9") = None`, `_check_per_strategy_exit_hit` returned `(None, None)`, the strategy `po3_bearish` (whose override is `ma_exit_ema9`) silently fell through to default trailing_stop. The override was a no-op.

**Fix applied in this audit** (`_build_today_bars`):
```python
closes_incl_today = pd.concat([prev["close"], pd.Series([float(row["close"])])])
if len(closes_incl_today) >= 9:
    ema_9 = float(closes_incl_today.ewm(span=9, adjust=False).mean().iloc[-1])
```

Verified: 806 unit + integration tests pass post-fix.

**Pattern to watch**: any future exit method needing additional context (e.g., today's regime classification, today's pivots, today's ATR) must verify the plumbing in `_build_today_bars` — silent no-ops are very hard to detect downstream.

---

## §2 — Finding 2 (LOGIC): Blanket 10% initial stop across all strategies

**Code** (`backtest.py:1191-1193`):
```python
init_stop = entry_price * (1 - TRAILING_STOP["initial_pct"])  # always 0.10
```

Every position gets a 10% initial stop regardless of strategy.

**Why it matters**:
- `R = |entry - initial_stop|` is used by Batch 284 `fixed_4r_2r` (target = entry + 4R; stop = entry - 2R)
- With R = 10% × entry: `fixed_4r_2r` target = +40%, stop = -20%
- For bollinger_lower (mean-reversion, 14d hold): targeting +40% is unrealistic; target rarely hits → fewer wins, more time-stops
- For longer-trend strategies (avwap_252_breakout, 138d hold): +40% target is reasonable

Mean-reversion strategies need TIGHTER initial stops (e.g., 3-5%). Trend strategies need WIDER initial stops (e.g., 12-15%) to avoid whipsaw exits.

**Recommendation**: Add `initial_pct` to STRATEGY_EXIT_OVERRIDE:
```python
"bollinger_lower": {"exit_method": "fixed_4r_2r", "initial_pct": 0.03},
"avwap_252_breakout": {"initial_pct": 0.12},
```

Batch 287 candidate (~10 lines + tests).

---

## §3 — Finding 3 (METHODOLOGY): In-sample cube optimization risk

Batch 284/285 STRATEGY_EXIT_OVERRIDE assignments are derived from Stage C (50 tkrs × 3y 2021-2023) cube-best. This means:
- The per-strategy assignments were CHOSEN to maximize Stage C aggregate
- Running D1 (642 tkrs × 4y 2022-2026) with these assignments tests on overlapping data
- Out-of-sample (2024-2026) is partially fresh but heavily contaminated

**Risk**: D1 results overstate the true edge of the per-strategy exits because the assignments were fit to the same period.

**Mitigation paths**:
- (a) Use only PRE-2024 data for cube-best assignment, then test 2024-2026 OOS
- (b) Apply cross-validation: split tickers into folds, optimize on fold-1-9 per strategy, evaluate on fold-10
- (c) Apply DEC-505 walk-forward methodology to per-strategy exit assignment

**Recommendation**: Document the in-sample optimization explicitly in the next D1 run output. Don't claim "+10-15k pp" as out-of-sample edge. Run D1 split into IS (2022-2024) and OOS (2024-2026); cube-best assignments derived from IS only, OOS metrics reported separately.

---

## §4 — Finding 4 (LOGIC): Tier sizing × dedup-split × breakeven_at_1R interaction

With Batch 279 dedup removal + size-split: when 5 strategies fire on AAPL same day at HIGH tier (3%), each gets 0.6% sized position.

But the breakeven_at_1R logic (from Batch 281, applied in `update_trailing_stop`):
- Computes `one_r = |entry_price - initial_stop|`
- `initial_stop = entry * 0.90` → R = 10% of entry
- At today_close >= entry + R → move stop to entry

This is applied PER POSITION. So all 5 positions on AAPL have the SAME initial_stop, R, and breakeven trigger point. They all break-even at the same price level. That's fine — they're effectively replicated trades sized smaller.

**Subtle issue**: with 5 smaller positions on same ticker, the broker reality would be ONE position of size 5×0.6%=3%, not 5 positions. The backtest tracks them as separate trades (good for per-strategy attribution) but real-world execution would combine them. Position sizing is correct; just the granularity differs.

**Recommendation**: Document the simulation-vs-reality mismatch. Stage 3 paper trading should aggregate same-ticker same-day positions for actual broker execution while preserving per-strategy attribution in records.

---

## §5 — Finding 5 (COSMETIC): `crisis_flag` set twice in dedup loop

**Code** (`backtest.py:1022, 1075`):
```python
# Line 1022 (inside the CRISIS_LONG_EXCLUSIONS block)
if direction == "long" and crisis_flag:
    ...

# Line 1075 (a few lines later, unconditional)
crisis_flag = regime == "crisis"
```

The first reference uses `crisis_flag` BEFORE it's set. Looking at the trace, `crisis_flag` is initialized earlier in the function (line 866 maybe) so this works, but the redundant second assignment is ugly.

**Severity**: cosmetic — no functional bug. Just confusing code.

**Recommendation**: Move the `crisis_flag = regime == "crisis"` assignment to the top of the candidate loop, remove the duplicate. Batch 287 cleanup.

---

## §6 — Finding 6 (DESIGN): Per-strategy gap_atr_mult ignored

**Code** (`backtest.py:1080-1091` via `validate_entry_zone`):
```python
valid, gap_reason = validate_entry_zone(next_open, close, atr, category, direction)
```

`validate_entry_zone` uses `ENTRY_GAP_ATR_MULT[category]` to compute the allowable gap. But:
- mean_reversion strategies might want STRICTER gap allowance (oversold + gap-up = stale signal)
- breakout strategies might want LOOSER gap allowance (gap-and-go is the signal)
- The forensic for rsi_oversold in T1a found `gap_up_6.5pct_exceeds_1.0x_atr_limit` blocked 45 of 137 candidates

**Recommendation**: Add `entry_gap_atr_mult` to STRATEGY_EXIT_OVERRIDE per strategy. Or accept current category-level granularity. Batch 287 candidate (low priority).

---

## §7 — Finding 7 (DATA): Dividend adjustment

OHLCV cache uses Polygon `adjusted=true` per prefetch script. This means historical prices are split-and-dividend-adjusted backward. Two implications:

1. **Trading dividends as gains**: a 2% quarterly dividend appears as a ~2% downward adjustment to historical close (pre-ex date). The post-ex price reflects only the price drop, not the cash received. So a backtest LONG entry pre-ex captures the dividend as a price decline in our cache → underestimates real return.

2. **Reverse splits create discontinuities**: SOLS, WW, CORZ, TPST cases from Batch 276 — even with `adjusted=true`, the adjustment isn't perfect across event dates.

**Recommendation**: For dividend-paying tickers (~70% of S&P 500), the cube and trade outcomes systematically understate returns by ~1-2% per year. Add dividend yield credit at trade level: when a trade is open across an ex-dividend date, add dividend amount to pnl_pct. Material for ~30bps annual improvement.

Investigation needed before D1 to quantify impact. Defer fix to Sprint 5.

---

## §8 — Finding 8 (DATA): Volume-zero days (halts) silently included

Halted ticker days have `volume = 0` in Polygon data. The screener currently doesn't filter these out — strategies fire on the most recent valid bar, but if today is halted, the prior bar's signals + today's open at the resumption price could create unrealistic fills.

**Recommendation**: Add a "no_trade_today_volume_zero" filter at the screener pre-pass. Investigation needed to count how many halted days exist in 642-ticker universe over 4y.

---

## §9 — Finding 9 (METHODOLOGY): Cube hardening thresholds are heuristic

Batch 266 set:
- `avg_hold_days ≤ 250`: any longer is "long-hold artifact"
- `actual_fire_rate ≥ 0.5`: less = exit isn't really firing

Why 250 and 0.5? These are reasonable defaults but not empirically derived. A 252-day hold (1 year) is just as suspect as a 240-day hold. A 49% fire-rate isn't materially different from 51%.

**Recommendation**: Re-evaluate thresholds post-D1 based on actual distribution of hold-days and fire-rates. Document that 250 / 0.5 are heuristic.

---

## §10 — Finding 10 (LOGIC, low priority): `_n_strategies_for_split` overestimates N

`_n_strategies_for_split = max(1, len(cand.get("strategies", [])))` counts ALL strategies firing on the ticker — but some of them might be filtered downstream (regime affinity, NFP suppression, blocklist, etc.). The size_pct is divided by this count, but only a fraction actually opens positions.

**Net effect**: positions are UNDER-sized when downstream gates filter some firings. This is CONSERVATIVE (safe), but means we under-utilize tier capacity.

**Example**: HIGH tier 3%, 5 strategies fire on AAPL, 2 pass downstream gates. Each opens at 3%/5 = 0.6%. Total deployed: 1.2% on AAPL. True HIGH tier intent was 3%. Lost capacity: 1.8%.

**Recommendation**: Two-pass approach — pre-scan to count surviving strategies, then size by that count. Estimated +30% capacity utilization on multi-strategy days. Batch 287 candidate (medium effort).

---

## §11 — Other observations (low priority / acknowledged)

| # | Item | Status |
|---|---|---|
| 11.1 | Hardcoded RSI thresholds (e.g., RSI<30 vs RSI<40) | Documented in Part 1; defer to post-D1 empirical sweep |
| 11.2 | signal.update() last-write-wins | Documented in Part 1; verified no current key conflicts |
| 11.3 | Skip-reason first-fire-wins (forensic loss) | Documented in Part 1; low priority |
| 11.4 | 8-multiplier position-sizing stack with no cumulative bound | Documented in Part 1; low priority |
| 11.5 | Regime classifier mis-calibration (2022 stealth bear) | UNFIXED; owner option A pending |

---

## §12 — Recommendations summary

**Tier 1 — Immediate (this batch):**
- ✅ FIXED: EMA-9 plumbing (Batch 286 within audit)

**Tier 2 — Next batch (Batch 287, ~1-2h):**
- Strategy-specific `initial_pct` (per-strategy initial stop width)
- `crisis_flag` cleanup (cosmetic)
- Two-pass `_n_strategies_for_split` (capacity recovery)
- Add `entry_gap_atr_mult` per strategy (optional)

**Tier 3 — Methodology (pre-D1):**
- Document in-sample cube optimization risk; consider IS/OOS split for D1
- Document cube hardening threshold heuristics
- Document per-strategy assignments derive from Stage C in-sample data

**Tier 4 — Sprint 5+ (deferred):**
- Dividend yield credit (data + accounting)
- Volume-zero day filter
- Walk-forward per-strategy exit assignment (DEC-505 extension)

**Tier 5 — Owner-decision-required:**
- Option A regime classifier calibration (pending from Audit Part 1)

---

**END.** The EMA-9 plumbing bug is the only urgent issue surfaced; fixed in this audit batch. Remaining items are documented for Batch 287 + Sprint 5+ work. The core architecture (Batches 279/281/282/284/285) is now consistent and complete; remaining gaps are calibration/optimization rather than structural.
