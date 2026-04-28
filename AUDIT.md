# Comprehensive Audit — Stock Picks & Automated Trading System
**Audit date:** April 2026  
**Audited by:** Claude (iterative, no code changes made)  
**Scope:** Full codebase — engine, signals, agents, data, config, scripts, docs  
**Status:** READ-ONLY audit. No fixes applied. All items require owner decisions.

---

## How to read this document

Each finding has:
- **Severity** — CRITICAL (crashes or wrong results) / HIGH (silent wrong results) / MEDIUM (methodology gap) / LOW (minor)
- **File and line** — exact location
- **What happens** — the actual failure mode, simulated step by step
- **Fix required** — exact change needed

Findings are ordered: CRITICAL first, then HIGH, MEDIUM, LOW.

---

## CRITICAL BUGS — system cannot run correctly with these present

---

### BUG-01 · `crisis_flag` used before definition → NameError crash

**File:** `backtest/engine/backtest.py` lines 299 and 325  
**Introduced by:** Commit `b430ab36` (our crisis exclusions change)

**What happens, step by step:**
1. Engine enters `_process_day()` for any day in crisis regime (Jan–Sep 2022)
2. Outer loop: `for cand in candidates[:10]`
3. Inner loop: `for strat_entry in cand.get("strategies", [])`
4. First strategy entry with `direction = "long"` reaches line 299:
   ```python
   if direction == "long" and crisis_flag:   # Line 299 — crisis_flag NOT YET DEFINED
   ```
5. Python raises `NameError: name 'crisis_flag' is not defined`
6. The exception is caught by the outer `try/except Exception` at the day level
7. The entire day is logged as failed, zero trades open
8. **Result: NO trades are ever opened in crisis regime. The most important regime in the backtest produces zero results.**

**Fix:** Move `crisis_flag = regime == "crisis"` (line 325) to BEFORE the inner strategy loop, immediately after `crisis_flag` is logically needed. Swap lines 299 and 325.

```python
# CORRECT ORDER:
crisis_flag = regime == "crisis"   # define FIRST

for strat_entry in cand.get("strategies", []):
    direction = strat_entry["direction"]
    ...
    if direction == "long" and crisis_flag:   # use AFTER
        ...
```

---

### BUG-02 · `days` variable used before definition → UnboundLocalError on every trade close

**File:** `backtest/engine/exit_manager.py` lines 295 and 297  
**Introduced by:** Commit `b430ab36` (our borrow cost change)

**What happens:**
1. Any trade reaches its exit condition (trailing stop hit, circuit breaker, etc.)
2. `close_trade()` is called
3. Line 295: `pnl = _pnl(trade.entry_price, exit_price, trade.direction, days)`
4. `days` is a local variable assigned at line 297 — Python treats it as local throughout the function
5. Referencing it at line 295 before assignment → `UnboundLocalError: local variable 'days' referenced before assignment`
6. **Result: No trade can ever be closed. All positions accumulate indefinitely. Trade log is always empty.**

**Before our change:** `pnl = _pnl(entry, exit_p, direction)` then `days = ...` — no `days` parameter, order didn't matter.  
**After our change:** We added `days` as a parameter to `_pnl()` but forgot to reorder the lines.

**Fix:** Swap the two lines:
```python
days = (exit_date - trade.entry_date).days   # define FIRST
pnl  = _pnl(trade.entry_price, exit_price, trade.direction, days)  # use AFTER
win  = pnl > 0
```

---

### BUG-03 · `ClosedTrade` dataclass defined twice — dead code, maintenance risk

**File:** `backtest/engine/exit_manager.py` lines 73 and 128

**What happens:**
1. Python reads file top-to-bottom; the second `@dataclass class ClosedTrade:` overwrites the first
2. Python uses the second definition (which has `sector`, `preliminary_tier`, `agent_reasoning`) — functionally correct
3. The first definition (lines 73–126) is dead code that will never be used
4. Risk: anyone reading the file sees two conflicting definitions and may edit the wrong one
5. Risk: if a circular import occurs during partial module load, the incomplete first definition could be used

**Fix:** Delete the first `ClosedTrade` definition (lines 73–126). Keep only the second (correct) one.

---

### BUG-04 · `avoid` direction falls into `triggered_short` bucket — inflates confidence tier

**File:** `backtest/signals/screener.py` lines 971–974

**What happens:**
```python
if direction == "long":
    triggered_long.append(entry)
else:
    triggered_short.append(entry)   # 'avoid' lands here
```
1. Three-state strategies that return `direction="avoid"` are appended to `triggered_short`
2. `strategy_count = len(triggered_long) + len(triggered_short)` — includes avoid entries
3. `confidence_tier` is assigned based on `strategy_count`
4. A ticker with 2 long strategies + 3 avoid strategies gets `strategy_count = 5` → `EXCEPTIONAL` tier
5. Engine then catches the avoid direction and logs it as skipped — but the tier was already wrong
6. **Result: Confidence tiers for all tickers with conflicting signals are systematically inflated**

**Fix:** Add explicit handling for `avoid`:
```python
if direction == "long":
    triggered_long.append(entry)
elif direction == "short":
    triggered_short.append(entry)
# avoid: do not append to either bucket — just discard
```

---

### BUG-05 · `strategies_triggered` key mismatch — agent cache is always wrong

**File:** `backtest/agents/pipeline.py` line 644 vs `backtest/signals/screener.py` line 988

**What happens:**
1. `screen_instrument()` returns: `{"strategies": all_triggered, ...}` — key is `"strategies"`
2. `run_full_agent_pipeline()` reads: `candidate.get("strategies_triggered", [])` — key is `"strategies_triggered"`
3. `.get("strategies_triggered", [])` always returns `[]` (empty list) — key does not exist
4. Agent cache key is built from `strategies=[]` for every ticker on every date
5. **All trades for the same ticker on the same date share ONE cache key regardless of which strategies fired**
6. First call writes cache with `strategies=[]`. All subsequent calls on same ticker+date return that cached result, even with completely different signals
7. **Result: Agent pipeline runs are not cached per strategy set — cache collisions corrupt agent analysis**

**Fix:** In `pipeline.py` line 644:
```python
strategies = candidate.get("strategies", [])   # matches screener output key
```

---

## HIGH SEVERITY — silent wrong results, no crash

---

### BUG-06 · Double borrow cost on short trades

**Files:** `backtest/engine/exit_manager.py` (`_pnl()`) and `backtest/engine/improvements.py` (`apply_transaction_costs()`)

**What happens:**
1. `_pnl()` now deducts `SHORT_BORROW_COST_PER_DAY * hold_days` from short PnL (added in b430ab36)
2. `apply_transaction_costs()` also deducts `ANNUAL_BORROW_RATE * (hold_days / 252)` for short trades
3. Both use rate ≈ 0.005%/day (0.5%/year annualised)
4. A 15-day short trade pays borrow cost **twice**: once in `_pnl()` and once in `apply_transaction_costs()`
5. **Result: Short trades are penalised ~2× on borrow cost. Short strategy win rates and ROI are artificially depressed. Short strategies are less likely to pass Phase 1B criteria.**

**Fix:** Remove the borrow cost deduction from `apply_transaction_costs()`. It is now correctly handled in `_pnl()`.  
In `improvements.py` around line 79: delete the block:
```python
# SHORT TRADE: add securities lending (borrow) cost  ← DELETE THIS BLOCK
if row.get("direction") == "short":
    hold_days = row.get("hold_days", 10)
    borrow_cost = ANNUAL_BORROW_RATE * (hold_days / 252)
    round_trip += borrow_cost
```

---

### BUG-07 · API key guard blocks no-agent Phase 1B run

**Files:** `run_full.sh` lines 13–19, `run_tests.sh` lines 13–19

**What happens:**
1. Both scripts check: `if [ -z "$ANTHROPIC_API_KEY" ]; then exit 1; fi`
2. Both scripts also pass `--no-agents` to every batch command
3. With `--no-agents`, the API key is never used — agents are disabled
4. **Result: Both scripts refuse to run if the API key is not set, even though the key is not needed**
5. User must set a fake API key or the scripts will not run at all

**Fix:** Make the guard conditional on whether agents are enabled:
```bash
if [ -z "$ANTHROPIC_API_KEY" ] && echo "$@" | grep -qv "\-\-no-agents"; then
    echo "ERROR: ANTHROPIC_API_KEY required for agent runs"
    exit 1
fi
```
Or simpler: remove the guard entirely from both scripts since Phase 1B is always `--no-agents`.

---

### BUG-08 · `ema_50_200_bullish` signal key does not exist

**File:** `backtest/signals/screener.py` lines 120–121 (`strat_pivot_r2_continuation`) and 515–516 (`strat_morning_star`)

**What happens:**
1. Both strategies call `s.get("ema_50_200_bullish")`
2. `technical.py` generates `ema_50_200_golden_cross` and `ema_50_200_death_cross` — never `ema_50_200_bullish`
3. `s.get("ema_50_200_bullish")` always returns `None` which is falsy
4. `strat_pivot_r2_continuation` long: `s.get("ema_50_200_bullish")` is always `None` → long condition never fully satisfied  
   `strat_pivot_r2_continuation` short: `not s.get("ema_50_200_bullish")` is always `True` → short fires whenever `below_s2` and `adx_trending` are True, even in bull markets
5. `strat_morning_star` long: same problem — misses valid long setups  
   `strat_morning_star` short: fires incorrectly in bullish regimes
6. **Result: Both strategies fire shorts in wrong conditions and miss valid longs**

**Fix:** Replace `ema_50_200_bullish` with the correct signal: `price_above_ema_200` (which does exist and means price is above the long-term trend):
```python
# strat_pivot_r2_continuation
fl = (s.get("above_r2") and s.get("adx_trending") and s.get("price_above_ema_200"))
fs = (s.get("below_s2") and s.get("adx_trending") and not s.get("price_above_ema_200"))

# strat_morning_star
fl = (s.get("morning_star") and s.get("rsi_14", 50) < 45 and s.get("price_above_ema_200"))
fs = (s.get("evening_star") and s.get("rsi_14", 50) > 55 and not s.get("price_above_ema_200"))
```

---

### BUG-09 · `below_cam_s3` signal key does not exist

**File:** `backtest/signals/screener.py` line 148 (`strat_camarilla_r3_breakout` short condition)

**What happens:**
1. Short condition: `fs = (s.get("below_cam_s3") and s.get("vol_spike_2x"))`
2. `technical.py` generates `near_cam_s3` — not `below_cam_s3`
3. `s.get("below_cam_s3")` always returns `None` → short version of Camarilla R3 breakout **never fires**
4. **Result: One of the highest-volume short breakdown signals is permanently disabled**

**Fix:** Add `below_cam_s3` to `technical.py` in the `compute_pivots()` function:
```python
result["below_cam_s3"] = today < cs3
```
Or use the raw price comparison directly in the screener:
```python
fs = (s.get("cam_s3", 0) > 0 and close < s.get("cam_s3", 0) and s.get("vol_spike_2x"))
```

---

### BUG-10 · Agent signal keys wrong — agents always see `False` for key price context

**File:** `backtest/agents/pipeline.py` lines 664–670

**What happens:**
```python
price = signals.get("close", 0)          # 'close' not in signals dict → always 0
high_52w = signals.get("high_52w", price) # 'high_52w' not in signals dict → always 0 (= price)
low_52w  = signals.get("low_52w", price)  # 'low_52w' not in signals dict → always 0
...
"above_200ema": signals.get("above_200ema", False)  # should be 'price_above_ema_200' → always False
"above_50sma":  signals.get("above_50sma", False)   # should be 'price_above_sma_50' → always False
```
1. `signals` dict is the output of `compute_all_signals()` from `technical.py`
2. `close` is not in this dict (it's input data, not a computed signal)
3. `high_52w` / `low_52w` not in dict — correct keys are `year_high` / `year_low`
4. `above_200ema` not in dict — correct key is `price_above_ema_200`
5. `above_50sma` not in dict — correct key is `price_above_sma_50`
6. **Result: Every agent receives zero as the current price, 0% from 52-week high/low, and False for all MA position context. Agent reasoning about price level and trend context is built on wrong data.**

**Fix:**
```python
price    = candidate.get("last_close", 0)                # use screener output, not signals
high_52w = signals.get("year_high", price)               # correct key
low_52w  = signals.get("year_low", price)                # correct key
...
"above_200ema": signals.get("price_above_ema_200", False) # correct key
"above_50sma":  signals.get("price_above_sma_50", False)  # correct key
```

---

### BUG-11 · `williams_r` short default fires incorrectly

**File:** `backtest/signals/screener.py` line 244 (`strat_williams_r_oversold`)

**What happens:**
```python
fs = (s.get("williams_r", 0) > -20 and ...)
```
1. Williams %R range is -100 to 0 (negative always)
2. If `williams_r` is not in signals dict, `.get("williams_r", 0)` returns `0`
3. `0 > -20` is `True`
4. Short fires incorrectly whenever Williams %R computation failed or produced missing data
5. **Result: Generates false short signals on data quality failures**

**Fix:** Use the pre-computed boolean signal instead:
```python
fs = (s.get("williams_r_overbought", False) and ...)
```

---

### BUG-12 · Deduplication order bias — shorts never fire when long strategy fires first

**File:** `backtest/signals/screener.py` lines 978, 971–974 and `backtest/engine/backtest.py` deduplication logic

**What happens:**
1. `all_triggered = triggered_long + triggered_short` — longs always appear first
2. In the engine, `opened_today` deduplication fires on the **first** strategy entry that passes all checks
3. For any ticker with both bullish and bearish signals: the first long strategy in the list opens a trade
4. All subsequent strategies for that ticker (including any short strategies) hit the `opened_today` check and are skipped
5. **Result: Short strategies can never open a position if ANY long strategy fires first on the same ticker. This means a ticker showing both RSI oversold (long) and death cross (short) will always take the long — even when the death cross is the stronger signal.**

**Fix:** Before deduplication, sort `all_triggered` by a conviction score (e.g. number of signals used) and pick the direction with the highest conviction. Alternatively: allow one long and one short position per ticker per day if they come from different strategy categories.

---

### BUG-13 · `days_to_next_earnings` makes ~106,000 live yfinance calls during backtest

**File:** `backtest/data/fetcher.py` lines 224–240  
**Called from:** `backtest/engine/backtest.py` inside the trade opening loop

**What happens:**
1. `days_to_next_earnings(ticker, as_of)` calls `yf.Ticker(ticker).earnings_dates` — live network call
2. Called for every trade candidate that passes the gap filter, every trading day
3. Estimated: 100 candidates/day × 1,060 trading days = 106,000 yfinance calls
4. **On laptop:** adds ~53 minutes of network time (0.3s per call) spread across the run
5. **On Codespaces:** yfinance blocked (403 error) → returns `None` for all → circuit breaker 2 never fires → all earnings gap losses are missed

**Fix:** Pre-fetch earnings dates to a Parquet cache (similar to Quiver prefetch), keyed by ticker. Load from cache during backtest. One-time cost, reusable across all runs.

---

### BUG-14 · AAPL, CVS, JPM, NVDA missing from `run_full.sh` batch ticker lists

**File:** `run_full.sh` — all 5 batch `--tickers` lists

**What happens:**
1. These 4 tickers were used as test tickers in `run_tests.sh`
2. When the full batch lists were assembled, they were accidentally excluded
3. AAPL is the 2nd largest S&P 500 constituent (~7% weight); NVDA was top performer 2023–2024; JPM is largest US bank
4. **Result: Full Phase 1B run will produce results for 500 tickers but miss 4 of the most important ones**

**Fix:** Add AAPL, CVS, JPM, NVDA to the appropriate batch (batch 1 has capacity based on letter ordering — AAPL should be in batch 1, CVS batch 1, JPM batch 3, NVDA batch 4).

---

## MEDIUM SEVERITY — methodology gaps affecting result quality

---

### BUG-15 · `max_drawdown` uses `cumsum()` instead of compounded equity curve

**File:** `backtest/results/metrics.py` lines 41–44

**What happens:**
```python
cumulative = pnl_series.cumsum()   # additive, not multiplicative
peak       = cumulative.cummax()
drawdown   = (cumulative - peak)
```
1. A strategy with returns `[+5%, -3%, +8%, -10%]` produces cumsum `[5, 2, 10, 0]`
2. Correct compound equity: `[(1.05)(0.97)(1.08)(0.90)] = 0.989` → drawdown from peak `1.134` = `-12.8%`
3. cumsum gives `10 → 0` = `-10pp drawdown` — different result, different threshold behaviour
4. **Result: Drawdown criterion may pass or fail incorrectly. Strategies near the 20% drawdown threshold may be misclassified.**

**Fix:**
```python
equity     = (1 + pnl_series / 100).cumprod()
peak       = equity.cummax()
drawdown   = (equity / peak - 1) * 100
```

---

### BUG-16 · `PASSING_CRITERIA min_trades = 100` contradicts all documentation

**File:** `backtest/config.py` line 215 vs `PROJECT_PLAN.md` line 175, `EXPLANATION.md` line 337

**What happens:**
1. Code runs with minimum 100 trades for strategy to be evaluated
2. At 100 trades with 55% win rate: 95% confidence interval = [45.2%, 64.4%] — lower bound below 50%
3. Cannot statistically distinguish 55% win rate from random chance (50%) at 100 trades
4. At 500 trades: CI = [50.6%, 59.3%] — barely defensible
5. **Result: Strategies with 100–499 trades could pass all 10 criteria but be statistically indistinguishable from noise**

**Fix:** Change `config.py` to `"min_trades": 500`. This aligns code with documentation and with sound statistical practice.

---

### BUG-17 · `run_commit.sh` full mode hangs on interactive `input()` in merge script

**Files:** `run_commit.sh` line 57, `scripts/merge_batch_outputs.py` line 117

**What happens:**
1. `run_commit.sh full` calls `python scripts/merge_batch_outputs.py` non-interactively
2. If any batch produced no trades (all strategies failed), `merge_batch_outputs.py` asks: `"Continue merge with partial batches? (yes/no): "`
3. In non-interactive mode (script), `input()` blocks indefinitely waiting for stdin
4. **Result: `run_commit.sh full` hangs forever if any batch is empty or partial. No merge completes, no final results.**

**Fix:** Add `--force` flag to `merge_batch_outputs.py`:
```python
parser.add_argument("--force", action="store_true", help="Skip interactive confirmation")
...
if empty_dirs and not args.force:
    response = input(...)
```
And update `run_commit.sh` to pass `--force`.

---

### BUG-18 · Bonferroni correction hardcoded to 60 strategies, should be 72

**File:** `backtest/engine/backtest.py` line 621

```python
bonferroni = bonferroni_adjusted_threshold(60)   # wrong — 72 strategies now
```

**Impact:** Understates the multiple-testing problem.  
With 60 strategies: P(at least one false positive) = 1 - (0.95)^60 = 95.4%  
With 72 strategies: P(at least one false positive) = 1 - (0.95)^72 = 97.6%  
The Bonferroni-adjusted p-value threshold should be tighter (0.05/72 = 0.00069 vs 0.05/60 = 0.00083).

**Fix:** Change line 621 to use `len(ALL_STRATEGIES)`:
```python
from backtest.signals.screener import ALL_STRATEGIES
bonferroni = bonferroni_adjusted_threshold(len(ALL_STRATEGIES))
```

---

### BUG-19 · OHLCV cache incomplete — 402 of 495 tickers only cover to 2024-12-31

**Files:** `backtest/data/cache/ohlcv/` (Parquet files), `backtest/data/cache/index.json`

**What happens:**
1. Backtest covers Jan 2022 – Mar 2026
2. 402 tickers (81%) have OHLCV data only to Dec 31, 2024
3. 88 tickers have data to Mar 2026; 5 tickers stop at 2022
4. On laptop: cache.py detects the gap and attempts to fetch Jan 2025 – Mar 2026 from yfinance (402 network calls on startup, ~3 minutes)
5. On Codespaces: yfinance blocked → all 402 tickers silently have no data for 2025–2026
6. **Result: tariff_shock_2025 and ai_divergence_2025_2026 regimes cannot be evaluated for 402 tickers. Bull regime 2024 is also truncated. The Codespaces run would produce results for only 2022–2024.**

**Recommendation:** Run `python scripts/update_ohlcv_cache.py` (or equivalent) on the laptop before the full run to fetch all missing data and commit updated Parquet files. Confirm all tickers cover to BACKTEST_END before running.

---

### BUG-20 · Regime thresholds inconsistent between PROJECT_PLAN and config.py

**Files:** `backtest/config.py` lines 162–172 vs `PROJECT_PLAN.md` lines 630–634

**What happens:**
- `PROJECT_PLAN.md` states: VIX proxy > 35% = crisis, > 25% = bear
- `config.py REGIME_FILTER` uses: `vix_min=40` for crisis, `vix_min=30` for bear
- These are different thresholds producing different regime classifications
- `PROJECT_PLAN.md` also states "20-day realised volatility as VIX proxy"
- Code uses VXX (a volatility ETF) as proxy, not realised volatility

**Impact:** Medium — the code thresholds (40/30) are used in production. Documentation describes a different system. Creates confusion about which is intentional.

**Fix:** Update PROJECT_PLAN.md to match the code (VIX proxy = VXX ETF, thresholds = 40/30) or vice versa. Make one document the source of truth.

---

### BUG-21 · `exit_strategies.py` own `_pnl` has no borrow cost — short comparison optimistic

**File:** `backtest/engine/exit_strategies.py` lines 28–32

**What happens:**
1. `exit_manager._pnl()` deducts borrow cost from short PnL (0.005%/day)
2. `exit_strategies._pnl()` does not — it uses raw price difference only
3. The exit strategy comparison (which ranks exit methods) uses the version without borrow cost
4. **Result: Short trades in exit strategy comparison appear slightly more profitable than they would be in the live system. The ranking of exit strategies for short positions may be biased.**

**Fix:** Sync `exit_strategies._pnl()` to accept `hold_days` parameter and apply borrow cost for shorts:
```python
def _pnl(entry: float, exit_p: float, direction: str, hold_days: int = 0) -> float:
    if direction == "long":
        return (exit_p - entry) / entry * 100
    from backtest.config import SHORT_BORROW_COST_PER_DAY
    return (entry - exit_p) / entry * 100 - SHORT_BORROW_COST_PER_DAY * max(hold_days, 1)
```

---

## LOW SEVERITY — documentation, minor issues

---

### BUG-22 · `run_phase1a.py` header prints "60 strategies"

**File:** `backtest/run_phase1a.py` line 141

```python
print("60 strategies | Trailing stop exits | Circuit breakers | Long + Short")
```
Should say 72. Minor but printed to logs on every run.

---

### BUG-23 · `screener.py` docstring says "60 strategies across 7 categories"

**File:** `backtest/signals/screener.py` lines 4–25

Should say "72 strategies across 8 categories" with the dedicated shorts category listed.

---

### BUG-24 · CHECKLIST item 13c says "review ALL agent outputs" — not applicable for no-agent runs

**File:** `CHECKLIST.md` item 13c

The mandatory batch test sequence says: *"Manually review ALL agent outputs for those 5 tickers"*  
Phase 1B runs without agents. Checklist should specify: for no-agent runs, review strategy firing rates, deduplication counts, and skip reasons instead of agent outputs.

---

### BUG-25 · `run_tests.sh` does not pass `--no-agents` flag

**File:** `run_tests.sh` — all 5 batch commands

`run_full.sh` was updated to include `--no-agents` but `run_tests.sh` was not.  
Test runs will attempt to use agents (and fail with API key guard unless key is set).  
The test run should be no-agents too — it is purely for validating strategy signals and engine logic.

**Fix:** Add `--no-agents \` to each batch command in `run_tests.sh`.

---

## Summary table

| # | Severity | Bug | File | Fix complexity |
|---|---|---|---|---|
| 01 | CRITICAL | `crisis_flag` used before definition | `backtest.py:299` | 2 lines swap |
| 02 | CRITICAL | `days` used before definition | `exit_manager.py:295` | 2 lines swap |
| 03 | CRITICAL | `ClosedTrade` defined twice | `exit_manager.py:73` | Delete 54 lines |
| 04 | CRITICAL | `avoid` goes into `triggered_short` bucket | `screener.py:973` | 2 lines change |
| 05 | CRITICAL | `strategies_triggered` key mismatch | `pipeline.py:644` | 1 line fix |
| 06 | HIGH | Double borrow cost on shorts | `improvements.py:79` | Delete 3 lines |
| 07 | HIGH | API key guard blocks no-agent run | `run_full.sh:13`, `run_tests.sh:13` | 5 lines each |
| 08 | HIGH | `ema_50_200_bullish` key missing | `screener.py:120,515` | 2 lines change |
| 09 | HIGH | `below_cam_s3` key missing | `screener.py:148` & `technical.py` | Add 1 line to technical.py |
| 10 | HIGH | Agent signal keys wrong (5 keys) | `pipeline.py:664` | 5 lines fix |
| 11 | HIGH | `williams_r` short default fires incorrectly | `screener.py:244` | 1 line fix |
| 12 | HIGH | Deduplication order bias (shorts never fire first) | `screener.py:978` | Architecture decision required |
| 13 | HIGH | 106,000 live earnings API calls during backtest | `fetcher.py:224` | Pre-fetch required |
| 14 | HIGH | AAPL/CVS/JPM/NVDA missing from full run | `run_full.sh` | Add to batch lists |
| 15 | MEDIUM | `max_drawdown` uses cumsum not equity curve | `metrics.py:42` | 3 lines change |
| 16 | MEDIUM | `min_trades=100` contradicts docs (should be 500) | `config.py:215` | 1 line change |
| 17 | MEDIUM | `run_commit.sh` hangs on interactive merge | `merge_batch_outputs.py:117` | Add `--force` flag |
| 18 | MEDIUM | Bonferroni hardcoded to 60, should be 72 | `backtest.py:621` | 1 line fix |
| 19 | MEDIUM | OHLCV cache only covers 402 tickers to 2024 | cache files | Re-fetch required |
| 20 | MEDIUM | Regime thresholds inconsistent (code vs docs) | `config.py` vs `PROJECT_PLAN.md` | Documentation alignment |
| 21 | MEDIUM | `exit_strategies._pnl` missing borrow cost | `exit_strategies.py:28` | 4 lines add |
| 22 | LOW | Header prints "60 strategies" | `run_phase1a.py:141` | 1 line |
| 23 | LOW | Docstring says "60 strategies" | `screener.py:4` | 3 lines |
| 24 | LOW | Checklist item 13c not valid for no-agent runs | `CHECKLIST.md:13c` | Update text |
| 25 | LOW | `run_tests.sh` missing `--no-agents` | `run_tests.sh` | Add flag to 5 commands |

---

## Pre-run checklist (must fix before ANY test batch)

These MUST be fixed before `bash run_tests.sh`:

1. ✋ **BUG-01** — crisis_flag NameError. Current code produces zero trades in crisis regime.
2. ✋ **BUG-02** — days UnboundLocalError. Current code cannot close any trade.
3. ✋ **BUG-04** — avoid in short bucket. Inflates tiers before engine can catch it.
4. ✋ **BUG-07** — API key guard. Will block the test run.
5. ✋ **BUG-25** — run_tests.sh missing --no-agents. Will trigger agent calls.

After these 5 are fixed, the test batch can run and produce results. The remaining bugs can be fixed between test batch and full run.

---

## Recommended fix sequence

**Round 1 (before test batch — 5 critical fixes):**
BUG-01, BUG-02, BUG-04, BUG-07, BUG-25

**Round 2 (before full run — correctness fixes):**
BUG-03, BUG-05, BUG-06, BUG-08, BUG-09, BUG-10, BUG-11, BUG-14, BUG-19 (data), BUG-22, BUG-23

**Round 3 (before Phase 1B analysis — methodology):**
BUG-12 (architecture decision), BUG-13 (pre-fetch), BUG-15, BUG-16, BUG-17, BUG-18, BUG-21

**Round 4 (before Phase 1C):**
BUG-20 (documentation), BUG-24

---

## Data readiness check (run on laptop before full run)

```bash
# 1. Update OHLCV cache to cover 2025-2026
python scripts/update_ohlcv_cache.py --end 2026-03-31

# 2. Verify all tickers covered
python scripts/validate_phase1b_data.py

# 3. Confirm macro/sentiment data covers full period (already OK):
# AAII: 2020-01-02 to 2026-03-26 ✅
# CNN Fear/Greed: 2020-01-01 to 2026-03-31 ✅
# Macro combined: 2020-01-01 to 2026-03-31 ✅
# Quiver: all 7 types, 509 tickers ✅
```

---

*Audit complete. Next audit pass scheduled when session limit resets. Will check: agent pipeline prompts, exit strategy ranking logic, walk-forward implementation, and live trading rules.*
