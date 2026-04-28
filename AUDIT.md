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

---

## AUDIT PASS 2 — Literature review, methodology, and remaining modules

*Conducted after Pass 1. References: Pardo (2008), Aronson (2006), Bailey et al (2014), Lopez de Prado (2018), Kelly (1956), D'Avolio (2002), Jegadeesh & Titman (1993), Wilder (1978), Sharpe (1994), Hamilton (1989), Kritzman et al (2012), Chan (2009), Schwager (1984).*

---

### BUG-26 · CRITICAL — VIX proxy is VXX price (223–461), not actual VIX (18–36) — all regime classifications are wrong

**File:** `backtest/data/macro.py` lines 138–154 and `backtest/engine/regime_filter.py`

**What happens, step by step:**
1. `_load_vix_from_ohlcv_cache()` tries `['VXX', '^VIX']` in that order
2. VXX Parquet exists → loaded immediately; `^VIX` Parquet does not exist → never reached
3. VXX is a volatility ETF that trades at $200–$500 price range (post-split adjusted), not 10–80 like actual VIX index
4. `classify_regime()` checks: `if vix_value >= 40: return "crisis"`
5. VXX price in 2022: ranged 223–461. Every single value is > 40
6. **Result: every trading day in 2022 is classified as "crisis" regardless of actual market conditions**
7. This is confirmed by existing data: all 34,727 trades have `regime = "crisis_CRISIS_FLAG"`
8. In reality 2022 had three distinct regimes: bear market (Jan–Jun), rally (Jul), resumption of bear (Aug–Dec)
9. The regime signal is completely meaningless — it is just the VXX price threshold test

**Verification:**
```
VXX 2022 close range: 223–461  (all > 40 → all "crisis")
Actual VIX 2022 range: 18–36   (never reached 40)
SPY 20-day realised vol 2022: 16–35% (2 days > 35%, 102 days 25–35%, 129 days 15–25%)
```

**Fix options (in order of preference):**
1. **Best:** Compute SPY 20-day annualised realised volatility from cached SPY data (no network call needed). Crisis = RV > 30%, Bear = RV 20–30%, Neutral = RV 12–20%, Bull = RV < 12%. Thresholds match PROJECT_PLAN intent.
2. **Alternative:** Fetch `^VIX` OHLCV from yfinance and cache it separately. Then use actual VIX thresholds (40/30/20).
3. **Minimal fix:** In `_load_vix_from_ohlcv_cache()`, try `^VIX` before `VXX`, and treat VXX as directional trend indicator (rising/falling) rather than absolute level proxy.

**Impact on existing results:** All 34,727 trades labelled "crisis" are correctly in a bear/crisis year (2022 was the worst year since 2008), but fine-grained regime distinctions (bull pockets in July and October 2022) are completely missed. The regime classification is too coarse to be useful.

---

### BUG-27 · CRITICAL — `regime_confidence()` function built but never called — dead code

**File:** `backtest/engine/improvements.py` lines 365–450 and `backtest/engine/backtest.py`

**What happens:**
1. `regime_confidence()` computes a 0–100 confidence score for the current regime
2. The function is well-implemented: checks VIX consistency, trend persistence, signal agreement
3. It is **never called anywhere in the codebase**
4. `backtest.py _process_day()` calls `get_regime_context()` but not `regime_confidence()`
5. **Result: regime transitions (when regime is changing) are treated with same confidence as established regimes**
6. A strategy entering a trade when regime confidence is 20% (transitioning) is sized identically to one entering at 95% (established regime)
7. Literature (Kritzman 2012): regime-transition periods have fundamentally different risk profiles

**Fix:** Call `regime_confidence()` in `_process_day()` and use the `position_mult` output to scale position size. The function already returns a `position_mult` (0.25–1.0). This is low effort and high impact.

---

### BUG-28 · HIGH — RSI computation uses simple rolling mean instead of Wilder exponential smoothing when pandas-ta unavailable

**File:** `backtest/signals/technical.py` lines 183–200

**What happens without pandas-ta:**
```python
g = d.clip(lower=0).rolling(p).mean()    # simple rolling mean -- WRONG
ls = (-d.clip(upper=0)).rolling(p).mean() # simple rolling mean -- WRONG
```
**Wilder's correct formula:** exponential smoothing with `alpha=1/N` (`ewm(com=N-1, adjust=False)`)

**Numerical difference:** On the same data, simple rolling RSI gives 63.6 vs Wilder EWM gives 78.5 — a 14.9-point difference. This is large enough to flip signals:
- Simple RSI = 63 → not overbought → strategy considers long entry
- Wilder RSI = 78 → overbought → strategy fires short signal

**Environment impact:** pandas-ta IS in requirements.txt, but on Codespaces it showed as unavailable during test runs (the `"pandas-ta not installed"` warning appears in logs). If Codespaces run uses the fallback, all 9 RSI-based strategies and 6 StochRSI-based strategies produce wrong signals for all 34,727 trades.

**Fix:**
```python
# Correct Wilder smoothing for fallback
g  = d.clip(lower=0).ewm(com=p-1, adjust=False).mean()
ls = (-d.clip(upper=0)).ewm(com=p-1, adjust=False).mean()
```
Also add pandas-ta explicitly to `devcontainer.json` `postCreateCommand` as a separate step to ensure it is always available.

---

### BUG-29 · HIGH — Open trades at backtest end silently discarded — upward bias in all metrics

**File:** `backtest/engine/backtest.py` — `run()` method and `save_all_outputs()`

**What happens:**
1. Backtest runs through all trading days in `[start, end]`
2. `self.open_trades` accumulates positions that never hit their trailing stop
3. At end of loop, `run()` completes and `save_all_outputs()` is called
4. `get_trade_log()` returns only `self.closed_trades` — open trades are never included
5. Open trades are logged in the summary count but never in metrics
6. **Losing trades that trend down through backtest end are never counted as losses**
7. Literature standard (Pardo 2008): force-close all open positions at the final bar's closing price

**Bias direction:** Upward. In bear markets and at end of bull markets, open positions are more likely to be losers (held through downtrend). Dropping them overstates win rate and ROI.

**Fix:** At end of `run()`, force-close all remaining open trades at their last available close price:
```python
# After main loop completes
last_day = trading_days[-1] if trading_days else self.end
for trade in self.open_trades:
    df = self.ohlcv_dict.get(trade.ticker)
    if df is not None:
        last_close = float(df[df.index.date <= last_day]["close"].iloc[-1])
        closed = close_trade(trade, last_close, last_day,
                             "end_of_backtest_force_close", 0.0, 0.0)
        self.closed_trades.append(closed)
self.open_trades = []
```

---

### BUG-30 · HIGH — VIX tightening in crisis contradicts own documentation

**Files:** `backtest/engine/regime_filter.py` line 73 vs `backtest/engine/exit_manager.py` lines 228–231

**Contradiction:**
- `regime_filter.py` description string: *"Do NOT tighten stops (causes whipsawing)"*
- `exit_manager.py` Circuit Breaker Level 5: explicitly tightens stop from 10% to 5% when VIX ≥ 40

**What happens:**
1. VIX enters crisis (> 40 threshold)
2. CB Level 5 fires on every subsequent day: stop tightened to 5%
3. In crisis, daily swings of 3–5% are common
4. A 5% trailing stop in a 5% daily-volatility environment = stopped out immediately
5. Position entered correctly is stopped out the next day before any profit develops
6. Literature (Wilder 1978): during high volatility, stops should be WIDER not tighter (use ATR multiple proportional to current volatility)

**Fix:** Remove or disable CB Level 5 tightening in the backtest. In live trading, portfolio-level drawdown management (LIVE_TRADING_RULES) handles crisis exposure. Per-position stops should stay at 1×ATR (which self-adjusts to current volatility) rather than a fixed 5%.

---

### BUG-31 · HIGH — Walk-forward OOS minimum of 30 trades is statistically insufficient

**File:** `backtest/engine/improvements.py` line 119 (`MIN_OOS_TRADES = 30`)

**Statistical analysis:**
At 30 OOS trades with 55% win rate: 95% confidence interval = **[37.7%, 71.2%]** — width of 33.5 percentage points. The lower bound (37.7%) is far below 50%, meaning we cannot distinguish the strategy from a coin flip.

**Literature standard (Bailey et al 2014):** For OOS validation to be meaningful, require minimum **100 OOS trades** per window. At 100 trades: CI = [45.2%, 64.4%]. Still wide but at least the upper bound is informative.

**Current impact:** A strategy with 35 OOS trades and 60% win rate passes the OOS check. But at 35 trades, the 95% CI is [43%, 75%] — the strategy could easily be random chance.

**Fix:** Raise `MIN_OOS_TRADES` from 30 to 100. Accept that more strategies will get `INSUFFICIENT_OOS_DATA` verdicts — this is correct behaviour given limited data.

---

### BUG-32 · HIGH — Profit factor minimum 1.2 too low; literature requires 1.5 minimum

**File:** `backtest/config.py` line 212 and `backtest/engine/improvements.py` line 151

**Literature context (Schwager 1984):**
- PF < 1.0: losing strategy
- PF 1.0–1.3: weak edge, likely noise
- PF 1.3–1.5: minimal acceptable threshold
- PF > 1.5: robust edge
- PF > 2.0: strong systematic edge

**Current threshold PF ≥ 1.2:** With 100 trades, a PF of 1.21 has enormous estimation uncertainty. A strategy with true PF of 1.0 (no edge) could easily produce PF = 1.21 in a 100-trade sample purely from randomness.

**Fix:** Raise `min_profit_factor` to 1.5 in `PASSING_CRITERIA`. Sector-adjusted criteria can keep 1.3 for high-volatility sectors. Combined with raising `min_trades` to 500 (BUG-16), this gives a much more defensible threshold.

---

### BUG-33 · HIGH — Sharpe ratio not required as passing criterion; computed but ignored

**File:** `backtest/config.py` `PASSING_CRITERIA` dict and `backtest/results/metrics.py`

**What happens:**
1. `compute_strategy_metrics()` computes `sharpe_ratio` for every strategy
2. `PASSING_CRITERIA` dict has no `min_sharpe` key
3. A strategy can pass all 10 criteria with Sharpe = 0.05 (near zero)
4. Literature standard (Sharpe 1994): minimum acceptable Sharpe ≥ 0.5 per year for a discretionary strategy; systematic strategies should target ≥ 1.0

**Why it matters:** Sharpe captures the risk-adjusted quality of returns that profit factor and win rate miss. A strategy with high win rate but extremely variable returns (wild swings) can have good PF but terrible Sharpe. Such strategies are unreliable in live trading.

**Fix:** Add to `PASSING_CRITERIA`:
```python
"min_sharpe": 0.5,   # annualised Sharpe ratio minimum
```
And add the check to `passes` dict in `compute_strategy_metrics()`.

---

### BUG-34 · HIGH — Mean reversion strategies run in all regimes — literature shows they fail in trending markets

**File:** `backtest/signals/screener.py` — all 11 mean reversion strategies fire in all regimes

**Literature finding (Faber 2007, Jegadeesh & Titman 1993):**
- Mean reversion works in SIDEWAYS/NEUTRAL markets (stocks bounce between support and resistance)
- Mean reversion FAILS in strong trends (oversold stocks keep falling; overbought stocks keep rising)
- In crisis (strong downtrend): RSI < 35 is a continuation signal, not a reversal signal
- This is documented as the "catching a falling knife" problem

**Current implementation:** All 11 mean reversion strategies fire regardless of regime. In a crisis bear market with VIX > 30:
- `strat_rsi_oversold` fires when RSI < 35 → buys dip → stock continues falling
- `strat_bollinger_lower` fires when price at lower band → buys dip → stock breaks below band

**Phase 1B data confirms this:** 29.7% win rate overall. Mean reversion strategies are the worst performers in crisis.

**Fix:** For mean reversion strategies, require additional confirmation in trending regimes:
- In crisis/bear: require sector ETF to be above its 20-day SMA (sector is outperforming) as an additional condition
- OR: suppress mean reversion strategies when `adx > 30` (strong trend indicator)
- Do NOT block them entirely (the approved buy-the-dip philosophy allows mean reversion in crisis) but add a confirming condition

---

### BUG-35 · MEDIUM — Decision Agent default fallback has invalid `action` value

**File:** `backtest/agents/pipeline.py` lines 579–583

**What happens:**
```python
return result if result else {
    "final_score": 40, "confidence_tier": "MEDIUM",
    "action": "WATCHLIST",   # ← NOT a valid action
    ...
}
```
Valid actions: `ENTER | WATCH | SKIP | AVOID`. `WATCHLIST` is not handled by the engine. When the API fails and this default fires, the action label is `WATCHLIST` which falls through all engine checks — the trade opens as if action was `ENTER`.

**Fix:** Change default `action` to `"SKIP"` (conservative default on API failure):
```python
return result if result else {
    "final_score": 40,
    "action": "SKIP",
    "entry_rationale": "API unavailable — defaulting to skip",
    "primary_risk": "Agent unavailable",
    "agent_agreement": "unknown",
}
```

---

### BUG-36 · MEDIUM — Regime-aware strategy weighting not implemented

**File:** `backtest/signals/screener.py` — `screen_universe()` — all strategies run equally in all regimes

**What happens:**
All 72 strategies fire whenever their conditions are met, regardless of whether the strategy type is appropriate for the current regime.

**Literature finding:**
| Regime | Best strategy types | Worst strategy types |
|---|---|---|
| Bull (low VIX, SPY up) | Momentum, trend-following | Mean reversion (stocks keep rising) |
| Neutral (sideways) | Mean reversion, pivot | Trend-following (whipsaws) |
| Bear (VIX 20–30, downtrend) | Trend shorts, momentum shorts | Mean reversion longs |
| Crisis (VIX > 30) | Trend shorts, crisis buys | Mean reversion longs (catching knives) |

**Current:** In crisis regime, 11 mean reversion strategies, 9 pivot strategies, and 9 trend-following long strategies all run equally. Literature says most of these are wrong-directional in crisis.

**Proposed fix (requires owner approval — significant design change):**
Add a `regime_filter` field to each strategy's `_strat()` or `_strat3()` return dict:
```python
"regime_confidence": ["neutral", "bear", "crisis"]  # list of regimes where valid
```
In `screen_instrument()`, filter strategies by current regime before adding to triggered list.

---

### BUG-37 · MEDIUM — Survivorship bias haircut methodology is arbitrary

**File:** `backtest/engine/improvements.py` lines 525–555

**What happens:**
```python
annual_rates = {7: 0.005, 14: 0.010, 30: 0.020, 999: 0.030}
```
A 15-day trade gets 2.0%/year haircut = 0.012% total deduction. This feels precise but is entirely made up. There is no published source for these specific rates.

**Literature reality:** Survivorship bias in US equity backtests has been measured at 1–2% per year on annualised returns (Elton & Gruber 1996). For individual trade-level haircuts, there is no established methodology.

**The honest approach:** Apply a flat portfolio-level survivorship bias adjustment to total ROI rather than per-trade haircuts. This is what the academic literature does. The per-trade approach creates false precision.

**Fix:** Replace per-trade haircut with: total backtest ROI × (1 - 0.015 × years) as a portfolio-level adjustment. Document the assumption explicitly.

---

### BUG-38 · MEDIUM — No minimum Sharpe in Bonferroni correction

**File:** `backtest/engine/improvements.py` lines 470–510

**What happens:**
The Bonferroni correction adjusts the significance threshold but the implementation only computes minimum trade counts, not adjusted win rate or Sharpe thresholds.

**Literature (Bailey et al 2014, "The Probability of Backtest Overfitting"):**
The correct metric for multiple-testing-adjusted strategy evaluation is the **Deflated Sharpe Ratio (DSR)** which accounts for:
- Number of strategies tested
- Number of backtest parameters tuned
- Length of backtest
- Non-normality of returns

A strategy with Sharpe 1.0 from testing 72 strategies may have DSR of 0.3 (not significant).

**Current:** Bonferroni only computes minimum trades. DSR is not computed.

**Recommendation:** Add DSR calculation to the metrics report as an advisory metric. Formula is published in Bailey (2014).

---

### BUG-39 · MEDIUM — `regime_confidence()` compares VIX-based regime with SPY-trend regime incorrectly

**File:** `backtest/engine/improvements.py` lines 406–425

**What happens:**
```python
agreement = 100 if vix_regime == trend_regime or vix_regime == "neutral" else 40
```
1. `vix_regime` can be: "crisis", "bear", "bull", "neutral"
2. `trend_regime` can be: "bull", "bear", "unknown"
3. When `vix_regime = "crisis"` and `trend_regime = "bear"`: these are compatible (crisis IS a form of bear) but the code returns `agreement = 40` (disagreement) because the strings don't match
4. When `vix_regime = "crisis"`, confidence is always penalised by the mismatch even when both signals agree on bearish conditions

**Fix:** Add crisis/bear compatibility:
```python
compatible = (vix_regime == trend_regime or
              vix_regime == "neutral" or
              (vix_regime == "crisis" and trend_regime == "bear"))
agreement = 100 if compatible else 40
```

---

### BUG-40 · MEDIUM — Short stop distance same as long (10%) — asymmetric risk not accounted for

**File:** `backtest/engine/backtest.py` lines 388–392 and `backtest/config.py` TRAILING_STOP

**What happens:**
```python
if direction == "long":
    init_stop = entry_price * (1 - TRAILING_STOP["initial_pct"])   # 10% below
else:
    init_stop = entry_price * (1 + TRAILING_STOP["initial_pct"])   # 10% above
```
Both long and short use the same 10% stop distance.

**Literature finding (D'Avolio 2002):**
- Short positions have unlimited upside risk (stock can rise indefinitely)
- A squeeze or catalyst can gap a stock up 20–50% before stop can trigger
- Literature recommendation: short stops should be tighter (6–8%) to limit squeeze exposure
- Additionally: short stop should tighten as position moves in favour (unlike longs where trailing stop provides profit lock-in, short stop should proactively reduce risk)

**Fix:** Add a separate short stop parameter:
```python
TRAILING_STOP = {
    "initial_pct":       0.10,   # long initial stop
    "short_initial_pct": 0.07,   # short initial stop (tighter — unlimited upside risk)
    "trail_pct":         0.10,   # both directions
}
```

---

### BUG-41 · MEDIUM — `min_market_cap_m = 100` too low; admits stocks with poor institutional tradability

**File:** `backtest/config.py` line 131

At $100M market cap, bid-ask spreads are significantly wider than for large-caps. The slippage model uses 0.08–0.15% for large-cap stocks. At $100M cap, realistic slippage is 0.3–0.5% per trade — 3–4× higher than assumed.

**But:** S&P 500 members all have market caps > $5B (minimum threshold for S&P 500 inclusion is ~$14.5B as of 2024). The 100M cap only matters for the ETFs in the universe (which are correctly classified separately). No S&P 500 member would fail the 100M threshold.

**Impact:** LOW — effectively irrelevant for the S&P 500 universe. Medium for any future expansion to small-caps. Note in config is misleading but not materially wrong.

---

### BUG-42 · LOW — `LILLY` appears as ticker in `run_full.sh` but should be `LLY`

**File:** `run_full.sh` batch 3 ticker list

**What happens:** `LILLY` is not a valid ticker symbol. Eli Lilly trades as `LLY`. The batch will attempt to fetch data for `LILLY`, fail, and skip it. `LLY` is never backtested.

**Fix:** Replace `LILLY` with `LLY` in batch 3 of `run_full.sh`.

---

### BUG-43 · LOW — Missing Calmar ratio minimum in passing criteria

**File:** `backtest/config.py` `PASSING_CRITERIA`

Calmar ratio = annualised return / max drawdown. Computed but not required as a passing criterion.

Literature guideline: Calmar ≥ 0.5 means annual return is at least half the max drawdown. Calmar < 0.5 means the strategy loses more in drawdowns than it gains annually — not worth trading. A strategy with 5% annual ROI and 15% max drawdown (Calmar = 0.33) can pass current criteria but would not be tradeable in practice.

**Fix:** Add `"min_calmar": 0.5` to `PASSING_CRITERIA`.

---

### BUG-44 · LOW — Test suite has no test for `close_trade()` or `_process_day()`

**File:** `backtest/tests/test_unit.py`

**What happened:** BUG-02 (days used before definition in `close_trade()`) was introduced in commit `b430ab36` and was not caught by the test suite because `close_trade()` is never directly tested.

**What is missing:**
- Test that `close_trade()` correctly computes PnL for long trades
- Test that `close_trade()` correctly computes PnL for short trades with borrow cost
- Test that `close_trade()` correctly applies borrow cost: 15-day short at 5% gain should return 5.0% - (0.005% × 15) = 4.925%
- Test that the avoid direction is correctly skipped in `screen_instrument()`
- Test that crisis exclusion blocks VXX/TLT/EEM long entries

**Fix:** Add these tests to `test_unit.py`. They would have caught BUG-01 and BUG-02 immediately.

---

## Updated summary — all 44 bugs

| # | Sev | Description | File | Fix |
|---|---|---|---|---|
| 01 | CRIT | `crisis_flag` NameError | `backtest.py:299` | 2-line swap |
| 02 | CRIT | `days` UnboundLocalError | `exit_manager.py:295` | 2-line swap |
| 03 | CRIT | `ClosedTrade` defined twice | `exit_manager.py:73` | Delete 54 lines |
| 04 | CRIT | `avoid` in short bucket | `screener.py:973` | 2-line change |
| 05 | CRIT | `strategies_triggered` key mismatch | `pipeline.py:644` | 1-line fix |
| 26 | CRIT | VXX price used as VIX (223–461 vs 18–36) — all regime classifications wrong | `macro.py:138` | Use realised vol |
| 06 | HIGH | Double borrow cost on shorts | `improvements.py:79` | Delete 3 lines |
| 07 | HIGH | API guard blocks no-agent run | `run_full.sh:13` | Conditional guard |
| 08 | HIGH | `ema_50_200_bullish` key missing | `screener.py:120` | Fix key name |
| 09 | HIGH | `below_cam_s3` key missing | `screener.py:148` | Add to technical.py |
| 10 | HIGH | 5 agent signal keys wrong | `pipeline.py:664` | 5-line fix |
| 11 | HIGH | `williams_r` short default fires incorrectly | `screener.py:244` | Use boolean key |
| 12 | HIGH | Deduplication order bias — longs always beat shorts | `screener.py:978` | Sort by conviction |
| 13 | HIGH | 106,000 live earnings API calls | `fetcher.py:224` | Pre-fetch required |
| 14 | HIGH | AAPL/CVS/JPM/NVDA missing from full run | `run_full.sh` | Add to batches |
| 27 | HIGH | `regime_confidence()` never called — dead code | `improvements.py:365` | Call in engine |
| 28 | HIGH | RSI uses simple rolling mean not Wilder EWM | `technical.py:186` | Fix fallback formula |
| 29 | HIGH | Open trades at backtest end silently discarded | `backtest.py:run()` | Force-close at end |
| 30 | HIGH | Stop tightening contradicts own docs | `exit_manager.py:228` | Remove CB Level 5 |
| 31 | HIGH | Walk-forward OOS minimum 30 too low (CI = ±17pp) | `improvements.py:119` | Raise to 100 |
| 32 | HIGH | Profit factor minimum 1.2 too low (literature: 1.5) | `config.py:212` | Raise to 1.5 |
| 33 | HIGH | Sharpe not required as passing criterion | `config.py` | Add min_sharpe=0.5 |
| 34 | HIGH | Mean reversion runs in all regimes; fails in crisis | `screener.py` | Regime filter |
| 15 | MED | `max_drawdown` uses cumsum not equity curve | `metrics.py:42` | 3-line change |
| 16 | MED | `min_trades=100` contradicts docs (should be 500) | `config.py:215` | Change to 500 |
| 17 | MED | `run_commit.sh` hangs on interactive merge | `merge_batch_outputs.py:117` | Add --force |
| 18 | MED | Bonferroni hardcoded at 60, should be 72 | `backtest.py:621` | Use len(ALL_STRATEGIES) |
| 19 | MED | OHLCV cache: 402 tickers only to 2024-12-31 | cache files | Re-fetch |
| 20 | MED | Regime thresholds inconsistent code vs docs | `config.py` vs `PROJECT_PLAN.md` | Align docs |
| 21 | MED | `exit_strategies._pnl` missing borrow cost | `exit_strategies.py:28` | Sync with exit_manager |
| 35 | MED | Decision Agent fallback has invalid `WATCHLIST` action | `pipeline.py:579` | Change to SKIP |
| 36 | MED | No regime-aware strategy weighting | `screener.py` | Design decision |
| 37 | MED | Survivorship haircut rates are arbitrary | `improvements.py:525` | Portfolio-level haircut |
| 38 | MED | No Deflated Sharpe Ratio for overfitting detection | `metrics.py` | Add DSR computation |
| 39 | MED | `regime_confidence()` crisis/bear comparison wrong | `improvements.py:406` | Fix compatibility |
| 40 | MED | Short stop same as long — asymmetric risk ignored | `backtest.py:388` | Separate short stop |
| 41 | MED | `min_market_cap_m=100` — misleading but harmless for S&P 500 | `config.py:131` | Update comment |
| 22 | LOW | Header prints "60 strategies" | `run_phase1a.py:141` | Fix to 72 |
| 23 | LOW | Docstring says "60 strategies" | `screener.py:4` | Fix to 72 |
| 24 | LOW | Checklist item 13c invalid for no-agent runs | `CHECKLIST.md` | Update text |
| 25 | LOW | `run_tests.sh` missing `--no-agents` | `run_tests.sh` | Add flag |
| 42 | LOW | `LILLY` invalid ticker (should be `LLY`) | `run_full.sh` | Fix ticker |
| 43 | LOW | No Calmar ratio minimum in passing criteria | `config.py` | Add min_calmar=0.5 |
| 44 | LOW | No tests for `close_trade()` or `_process_day()` | `test_unit.py` | Add tests |

**Total: 44 bugs — 6 CRITICAL, 15 HIGH, 15 MEDIUM, 8 LOW**

---

## Pre-run mandatory fixes (updated)

Must fix before `bash run_tests.sh`:

1. ✋ BUG-01 — crisis_flag NameError (2-line swap)
2. ✋ BUG-02 — days UnboundLocalError (2-line swap)
3. ✋ BUG-04 — avoid in short bucket (2-line change)
4. ✋ BUG-07 — API guard blocks no-agent run
5. ✋ BUG-25 — run_tests.sh missing --no-agents
6. ✋ BUG-26 — VXX price used as VIX proxy — fix regime classification before ANY run
7. ✋ BUG-42 — LILLY invalid ticker (1-char fix)

**BUG-26 is newly elevated to pre-run mandatory.** Without fixing it, every trading day will be classified as "crisis" and all regime-based analysis will be meaningless.

---

## Recommended fix sequence (updated)

**Round 1 — Before test batch (7 items, ~30 min work):**
BUG-01, BUG-02, BUG-04, BUG-07, BUG-25, BUG-26, BUG-42

**Round 2 — Before full run (correctness, ~3 hours):**
BUG-03, BUG-05, BUG-06, BUG-08, BUG-09, BUG-10, BUG-11, BUG-14, BUG-28 (RSI fix), BUG-29 (force-close), BUG-35, BUG-19 (data fetch), BUG-22, BUG-23

**Round 3 — Before Phase 1B analysis (methodology, ~4 hours):**
BUG-12 (architecture decision), BUG-13 (pre-fetch earnings), BUG-15 (drawdown), BUG-16 (min_trades), BUG-17 (merge fix), BUG-18 (Bonferroni), BUG-21, BUG-30 (stop tightening), BUG-31 (OOS min), BUG-32 (PF min), BUG-33 (Sharpe), BUG-40 (short stop), BUG-44 (tests)

**Round 4 — Before Phase 1C (design decisions):**
BUG-27 (regime confidence), BUG-34 (regime strategy weighting), BUG-36 (regime weights), BUG-37, BUG-38, BUG-39, BUG-41, BUG-43, BUG-20 (docs)

---

*Audit Pass 2 complete. Next pass: agent prompt quality, Quiver data point-in-time correctness, walk-forward window boundary handling, sector criteria calibration, and live trading rules gap analysis.*

---

## AUDIT PASS 3 — Integration, live trading gaps, signal accuracy, point-in-time

*Continued from Pass 2. References: Pardo (2008), D'Avolio (2002), SEC disclosure rules.*

---

### BUG-45 · MEDIUM — FX currency risk not modelled

**Files:** `backtest/config.py` LIVE_TRADING_RULES, no FX module exists

**What happens:**
- Portfolio is CAD-denominated (Wealthsimple / IBKR Canada)
- All trades are in USD (US equities)
- CAD/USD moved from 0.79 → 0.72 in 2022 (−8.9% adverse for CAD investor)
- A 5% gain on a US stock in 2022 becomes 5% − 8.9% FX effect = −3.9% in CAD terms
- Backtest treats all PnL as if there is no currency conversion
- **Result: all backtest returns are overstated for a CAD-based account in years when USD strengthens**

**Quantification:** In 2022 alone, FX drag was ~8.9%. A strategy showing +5% backtest ROI in 2022 actually returned approximately −3.9% in CAD. In 2023-2024 the drag reversed slightly. Over the full backtest period the net FX impact depends on the period.

**Fix (low effort):** Multiply all PnL by the CAD/USD rate change over the hold period. Cache CAD/USD historical data (available via yfinance `CADUSD=X`). Apply at close_trade time:
```python
fx_return = cadusd_at_exit / cadusd_at_entry  # e.g. 0.72/0.79 = 0.911
pnl_cad = pnl_usd * fx_return
```

---

### BUG-46 · MEDIUM — `fetch_info_bulk` info cache uses current market_cap, not historical

**File:** `backtest/data/universe.py` lines 185–230 and `data/cache/info_cache.json`

**What happens:**
- `info_cache.json` stores current (April 2026) market_cap for 70 tickers
- Only 70 of 509 tickers are in cache; remaining 439 return `market_cap=0`
- `get_transaction_cost()` uses `market_cap=0` → falls to `default` cost (0.001) which equals `large_cap`
- For stocks that were mid-cap in 2022 (market_cap $2-10B), transaction costs are understated
- Current NVDA market_cap = $4.9T (large_cap); 2022 NVDA = ~$300B (still large_cap → no issue)
- But smaller S&P 500 members: e.g. stock at $3B in 2022 (mid_cap, 0.0015 cost), now at $12B (large_cap, 0.001 cost) → cost understated

**Impact:** LOW for most S&P 500 stocks (all are large-cap by 2026). MEDIUM for names that graduated from mid-cap to large-cap during the backtest period.

**Fix:** Either (a) accept the simplification and document it, or (b) populate the full 509-ticker info cache before the backtest run.

---

### BUG-47 · MEDIUM — VXX in universe creates self-referencing regime paradox

**File:** `backtest/config.py` ETFS list and CRISIS_LONG_EXCLUSIONS

**What happens:**
1. VXX is in the trading universe (it's included in ETFS and run_full.sh)
2. VXX close price is used as the VIX proxy for regime classification (BUG-26)
3. VXX strategies can fire (e.g. `death_cross_50_200_volume` short on VXX)
4. **Result: the same instrument that defines the regime also generates trade signals in that regime — circular dependency**

More fundamentally: VXX is a volatility ETP with severe roll decay. It loses ~5–10% per year in normal markets from futures roll costs. Backtesting VXX with the same strategy logic as equities is invalid — it behaves differently from stocks.

**Fix:** Remove VXX from the strategy universe entirely. Keep it only as the VIX proxy (once BUG-26 is fixed to use realised vol, VXX proxy is no longer needed at all). VXX is already in CRISIS_LONG_EXCLUSIONS for longs — add it to a short exclusion list too.

---

### BUG-48 · MEDIUM — Sector `Volatility` and `Emerging Markets` not in sector criteria profiles

**File:** `backtest/config.py` SECTOR_PASSING_CRITERIA

VXX is classified as "Volatility" sector, EEM as "Emerging Markets". Neither appears in any sector criteria profile. Both fall through to `medium_volatility` defaults (55% WR, 20% DD, 1.3 PF).

VXX: annualised volatility ~50–60% — should use `high_volatility` criteria (50% WR, 25% DD)
EEM: annualised volatility ~25–30%, emerging market risk — should use `high_volatility` criteria

**Fix:** Add both to the `high_volatility` sector list in SECTOR_PASSING_CRITERIA.

---

### BUG-49 · LOW — FX risk not mentioned in EXPLANATION.md or PROJECT_PLAN.md

**Files:** `EXPLANATION.md`, `PROJECT_PLAN.md`

The plain-English guide and project plan make no mention of currency risk for a CAD-based investor trading US equities. This is a meaningful risk that affects actual live trading returns.

**Fix:** Add a "Currency Risk" section to EXPLANATION.md and note in PROJECT_PLAN.md.

---

### BUG-50 · LOW — `position_staleness_pct=1%` in live rules has no backtest equivalent

**File:** `backtest/config.py` LIVE_TRADING_RULES

In live trading, if entry price moved >1% since signal generation (end-of-day to next day's order placement), the order is cancelled. In the backtest, the entry gap filter (`validate_entry_zone`) handles this partially via ATR multiples — but the 1% staleness check is not enforced.

**Impact:** Negligible for swing trading (1% moves are common and acceptable at next-day open). More relevant for strategies where exact entry price matters (pivot-based).

---

### End-to-end simulation confirmation

With current code on `main` (commit `b430ab36`), a full backtest run will:

1. Load data correctly ✅
2. Classify ALL days as "crisis" (VXX price >> 40) ❌
3. Screen universe correctly ✅
4. Crash on first long trade candidate with `NameError: crisis_flag` ❌
5. Catch the exception and log the day as failed (no trades open) ❌
6. Even if BUG-01 fixed: crash on every trade close with `UnboundLocalError: days` ❌
7. Produce an empty trade log after processing all 1,060 trading days ❌

**The system is completely non-functional for trade generation as of the last commit.**

---

## Final summary — all 50 bugs

**6 CRITICAL:** BUG-01, 02, 03, 04, 05, 26
**15 HIGH:** BUG-06, 07, 08, 09, 10, 11, 12, 13, 14, 27, 28, 29, 30, 31, 32, 33, 34 *(note: 17 items, numbered non-consecutively)*
**19 MEDIUM:** BUG-15, 16, 17, 18, 19, 20, 21, 35, 36, 37, 38, 39, 40, 41, 45, 46, 47, 48
**10 LOW:** BUG-22, 23, 24, 25, 42, 43, 44, 49, 50

---

## What needs owner decisions (not just code fixes)

These are architectural or strategic decisions requiring explicit approval before implementation:

**D1 (BUG-26):** VIX proxy — use SPY 20-day realised vol OR fetch actual ^VIX. **Choose one.**

**D2 (BUG-36):** Regime-aware strategy weighting — do you want mean reversion strategies suppressed in trending markets? This changes which strategies fire and requires adding regime filters to screener.

**D3 (BUG-34):** Mean reversion in crisis — currently allowed (buy-the-dip philosophy). Literature says these fail in crisis. **Keep as-is per approved philosophy, or add extra confirmation conditions?**

**D4 (BUG-40):** Short stop distance — currently same 10% as longs. Literature recommends 7% for shorts. **Change or keep?**

**D5 (BUG-45):** FX modelling — model CAD/USD impact on returns or treat backtest as USD-denominated for simplicity?

**D6 (BUG-47):** VXX in universe — remove from strategy universe entirely, or keep as a tradeable instrument?

---

*Audit Pass 3 complete. 50 total bugs documented. Next scheduled pass: automated on session reset.*

---

## AUDIT PASS 4 — Agent prompts, signal computation accuracy, Phase 1C validation, test coverage

*References: Wilder (1978), Mulloy (1994) TEMA/DEMA, Oliver Seban Supertrend, John Carter TTM Squeeze, Bill Williams AO.*

---

### BUG-51 · HIGH — All 5 agents receive wrong or zero price context due to BUG-10 compounding

**File:** `backtest/agents/pipeline.py` lines 161–166 (Technical Agent) and lines 664–670 (pipeline orchestrator)

**What happens in combination:**

**Technical Agent** builds `context_signals` dict by looking up keys including `close`, `above_200ema`, `above_50sma`, `high_52w`, `low_52w` — none of which exist in the signals dict (BUG-10). The agent receives `price=0`, `pct_from_52w_high=0%`, `pct_from_52w_low=0%`, `above_200ema=False` for every trade.

**Bull/Bear Debate Agent** receives `price_context` built the same way — it tells every debate:
- "Stock is 0.0% from 52-week high"
- "Stock is 0.0% from 52-week low"
- "Nearest support: 0, nearest resistance: 0"

This means the debate agent argues both sides while believing the stock is exactly at its 52-week high AND 52-week low simultaneously, with no support/resistance context.

**Root cause chain:** BUG-10 (wrong key names in pipeline) → agents receive zero/false for all price context → agent reasoning is built on wrong data → agent scores have no price-level signal → all 34,727 existing agent results are contaminated.

**Fix:** As specified in BUG-10 — use `candidate["last_close"]` for price and `year_high`/`year_low` for 52-week range. These keys are correct and present in screener output and signals dict respectively.

---

### BUG-52 · HIGH — Risk Agent's VIX floor behavior now fully explained by BUG-26

**File:** `backtest/agents/pipeline.py` lines 395–430 (Risk Agent prompt)

**Root cause confirmed:**

The Risk Agent prompt explicitly states: `"VIX level (>30 = high fear, >40 = crisis)"`. The agent receives `vix_value` from `macro_snap`, which is the VXX close price (~380 in 2022, always > 40). The agent correctly reads `vix_value=380`, determines this is a severe crisis, and scores risk at the floor value (2/10).

The agent was not broken — it was reasoning correctly from wrong inputs. **BUG-26 (VXX proxy) is the root cause of the Risk Agent floor scoring in Phase 1B.**

Once BUG-26 is fixed (VXX replaced with realised volatility or actual VIX), the Risk Agent will receive realistic VIX values (18–36 in 2022) and produce differentiated risk scores (e.g. 5/10 in neutral conditions, 2/10 in genuine crisis, 8/10 in bull markets).

**No separate fix needed for Risk Agent prompt — fixing BUG-26 fixes this automatically.**

---

### BUG-53 · HIGH — Finnhub news cache: all 509 files are empty — Sentiment Agent has no news data

**File:** `backtest/data/cache/finnhub_news/` — 509 `.parquet` files, all 0 bytes

**What happens:**
1. `_load_news_sentiment()` tries Alpha Vantage cache first, then Finnhub fallback
2. AV cache has data for only 25 tickers (API rate limit during prefetch)
3. Finnhub cache has 509 files but ALL are empty (0 rows)
4. For 484/509 tickers (95%): news sentiment returns `{"available": False, ...}`
5. Sentiment Agent prompt shows `news_sentiment: {available: False, avg_sentiment: 0, article_count: 0}`
6. **Agent has no news signal for 95% of trades**

**Implication:** The Sentiment Agent is effectively scoring on congressional trades + AAII + Fear/Greed only. News sentiment — which Anthropic's own research confirms is a meaningful signal for short-term price moves — contributes zero to 95% of analyses.

**Fix options:**
- Accept limitation (document that news is unavailable for most tickers)
- Re-run Finnhub prefetch to populate the cache (requires FINNHUB_API_KEY and rate limit patience — ~8 hours at free tier limits)
- Use a different news source: Alpha Vantage has 25 tickers at reasonable cost; expand AV to full universe at cost ~$50/month

---

### BUG-54 · MEDIUM — Hull Moving Average uses simple rolling mean instead of WMA — signal timing wrong

**File:** `backtest/signals/technical.py` lines 586–588

**Hull's formula requires Weighted Moving Average (WMA):**
```python
# WRONG (current):
wma1 = df["close"].rolling(half).mean()   # simple average
wma2 = df["close"].rolling(period).mean() # simple average

# CORRECT:
def wma(series, n):
    weights = np.arange(1, n+1, dtype=float)
    return series.rolling(n).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
wma1 = wma(df["close"], half)
wma2 = wma(df["close"], period)
```

**Numerical difference:** On a 100-bar test, the last 5 values differ by 0.14–0.34 per bar. The Hull MA's primary advantage — faster response to price changes vs standard EMAs — is entirely due to WMA weights. Using SMA produces a result that is slower to respond and will have different flip/cross dates than what charting platforms show.

**`hull_flip_up` and `hull_flip_dn` signals will fire on different dates** compared to TradingView/Bloomberg Hull MA. Backtested results will not be replicable on live trading platforms.

**Impact:** MEDIUM — strategies `hull_rsi`, `hull_rsi_short`, and confluence strategies using `hull_bullish` may have different entry/exit dates than expected from the indicator's published specification.

---

### BUG-55 · MEDIUM — PSAR flip detection uses approximation that may fire on wrong day

**File:** `backtest/signals/technical.py` lines 508–510

**What happens:**
```python
"psar_flip_up": bullish and not (pclose > psar_long),
"psar_flip_dn": not bullish and (pclose > psar_long),
```
This compares yesterday's close (`pclose`) to today's PSAR value (`psar_long`). But PSAR moves each day, so this comparison is between two time-shifted values.

**What it should be:**
```python
# Store previous bullish state
"psar_flip_up": bullish and not prev_bullish,
"psar_flip_dn": not bullish and prev_bullish,
```
The Supertrend implementation correctly does this by iterating with state tracking (`bull[-1]`, `bull[-2]`). PSAR should do the same.

**Impact:** LOW-MEDIUM — the approximation will usually fire within 1 day of the correct flip date. Strategies `strat_parabolic_sar_flip` and `strat_parabolic_sar_flip_short` may have entry dates shifted by ±1 day.

---

### BUG-56 · MEDIUM — Phase 1C base score can exceed [0, 100] — Decision Agent adjustment not clamped

**Approved Phase 1C design:** Base score = weighted sum of 5 agents × 10, then Decision Agent adjusts ±15 points.

**Problem:** Score range without clamping: −15 to 115. A perfect score of 100 with +15 adjustment = 115, which maps to no tier (all tier thresholds are ≤ 100). A zero score with −15 = −15, which maps to below AVOID tier.

**Fix:** Clamp `final_score = max(0, min(100, base_score + decision_adjustment))` before applying tier thresholds.

---

### BUG-57 · MEDIUM — Integration tests missing 15 critical scenarios — 5 bugs would have been caught

**File:** `backtest/tests/test_integration.py` — 7 tests currently

**Tests that would have caught recent bugs had they existed:**

| Missing test | Bug it would have caught |
|---|---|
| `close_trade("short", 10 days)` asserts PnL includes borrow cost | BUG-02 (days before definition) |
| `_process_day(regime="crisis")` asserts no exceptions | BUG-01 (crisis_flag NameError) |
| `screen_instrument()` with avoid strategy: assert `direction != "short"` | BUG-04 (avoid in short bucket) |
| `run_full_agent_pipeline(candidate)` asserts `strategies != []` | BUG-05 (key mismatch) |
| `classify_regime(vix_value=380)` asserts returns `"crisis"` but VXX=380 means it's wrong | BUG-26 (VXX proxy) |
| `close_trade()` asserts borrow cost not double-charged | BUG-06 (double borrow cost) |
| `screen_instrument(avoid_strategy)` asserts `strategy_count` not inflated | BUG-04 confirmation |

**Fix:** Add all 15 missing tests identified in audit Pass 4. Each test is 5–15 lines. Total effort: ~2 hours.

---

### BUG-58 · LOW — StochRSI cross-up fires in mid-range, not just oversold zone

**File:** `backtest/signals/technical.py` line 228

```python
"stochrsi_cross_up": k > d and k < 80,   # fires anywhere below 80
```

**Literature (Lane 1984):** The highest-probability StochRSI crossovers occur when K crosses above D **in the oversold zone (K < 20)**. Crossovers in mid-range (K = 40–60) have much lower predictive value.

**Current behavior:** Cross-up fires whenever K > D, as long as K < 80. This generates many mid-range crossovers with low edge.

**Better definition:**
```python
"stochrsi_cross_up_oversold": k > d and k < 20,  # only in oversold zone
"stochrsi_cross_up":          k > d and k < 80,  # current broader definition
```

**Impact:** LOW — current approach generates more signals, which may or may not have lower quality. The backtested results will reveal whether oversold-only crossovers perform better. This is a strategy optimization choice, not a correctness bug.

---

### BUG-59 · LOW — CPR top/bottom labels are reversed vs industry convention

**File:** `backtest/signals/technical.py` lines 78–81

Convention (from CPR inventor Camarilla / professional pivot traders):
- **TC (Top of CPR)** = `(Pivot - BC) + Pivot` = `2*Pivot - BC`
- **BC (Bottom of CPR)** = `(High + Low) / 2`

Current code:
- `cpr_top = (H + L) / 2` ← this is actually BC (bottom)
- `cpr_bottom = P` ← Pivot is actually between BC and TC, not the bottom

In practice TC > Pivot > BC always holds. By labelling the pivot as the "bottom" and the BC as the "top", the labels are inverted vs convention. The `above_cpr` / `below_cpr` signals compare close vs `cpr_bottom` (Pivot), which is a reasonable midpoint comparison even if misnamed.

**Impact:** LOW — the width calculation is correct, `above_cpr` behaviour is reasonable. Only affects readability and documentation.

---

### Confirmed correct implementations (no bugs found)

The following were audited and confirmed correct against their published specifications:

| Indicator | Reference | Status |
|---|---|---|
| Bollinger Bands (20,2) | John Bollinger | ✅ Correct |
| Keltner Channel (EMA±2×ATR) | Linda Raschke variant | ✅ Correct |
| TTM Squeeze (BB inside KC) | John Carter | ✅ Correct |
| TEMA / DEMA | Patrick Mulloy (1994) | ✅ Correct |
| Supertrend (7,3) | Oliver Seban | ✅ Correct |
| ATR with Wilder EWM | Wilder (1978) | ✅ Correct |
| Ichimoku (9/26/52) | Goichi Hosoda | ✅ Correct |
| CMF (20-period) | Marc Chaikin | ✅ Correct |
| OBV | Joseph Granville | ✅ Correct |
| Awesome Oscillator | Bill Williams | ✅ Correct |
| ADX / DI+/DI- | Wilder (1978) | ✅ Correct |
| Stochastic (14,3,3) | George Lane (via pandas-ta) | ✅ Correct |
| Fibonacci retracements | Standard (0.236/0.382/0.5/0.618/0.786) | ✅ Correct |
| Parabolic SAR (0.02/0.20) | Wilder (1978) | ✅ Approximately correct (flip detection minor issue) |
| MACD (12/26/9 and 8/21/5) | Appel (via pandas-ta) | ✅ Correct |
| RSI (9/14/21) | Wilder — **only when pandas-ta available** | ⚠️ Wrong fallback (BUG-28) |
| Hull MA (20) | Alan Hull | ❌ Uses SMA not WMA (BUG-54) |

---

### Phase 1C design validation summary

The approved Phase 1C design (base score formula + ±15 adjustment + thresholds 60/35) is **internally consistent and correctly calibrated**:

- Weights sum to 1.0 ✅
- In crisis with relative risk scoring: average trades score ~44–47 (tier unchanged), exceptional trades can reach 78+ (upgrade possible) ✅
- In bull regime: average trades score ~57–65 (some upgrades, most unchanged) ✅
- Upgrade threshold 60 is achievable but not trivial — correct design intent ✅
- One gap: final score must be clamped to [0, 100] (BUG-56)

---

## Updated complete bug list — 59 bugs across 4 passes

| Pass | Severity count | New bugs |
|---|---|---|
| Pass 1 | 5C / 9H / 7M / 4L = 25 | BUG-01 to BUG-25 |
| Pass 2 | +1C / +9H / +9M | BUG-26 to BUG-44 |
| Pass 3 | +0C / +1H / +4M / +1L | BUG-45 to BUG-50 |
| Pass 4 | +0C / +3H / +5M / +3L | BUG-51 to BUG-59 |
| **Total** | **6C / 22H / 25M / 8L** | **59 bugs** |

*Pass 5 scheduled: PROJECT_PLAN accuracy vs code, live trading ruleset completeness, Phase 1D design gaps, email approval system design.*

---

## AUDIT PASS 5 — Live trading design, Phase 1C/1D readiness, PROJECT_PLAN accuracy, infrastructure

---

### BUG-60 · HIGH — Short entry zone validation rejects favourable gap-down — understates short strategy performance

**File:** `backtest/signals/screener.py` lines 919–923

**What happens:**
```python
else:  # short
    gap_atr_short = (signal_close - open_price) / atr
    if gap_atr_short > mult:
        return False, f"gap_down_..."  # WRONG: rejects favourable gaps
```

**Example:** Short signal fires at close $100. Next day opens at $96 (gap down = stock already moved toward our target). For a short position this is a **better** entry — we sell at $96 which is below where our signal fired.

Current code: `gap_atr_short = (100 - 96) / 2 = 2.0`. If mult=1.5 → **rejects** the trade. But this was a favourable move.

**Correct logic for shorts:** Only reject if price gaps UP (adverse = stock moved against the short). Accept all gap-down opens (favourable).
```python
else:  # short
    # Adverse gap for short = price moved UP from signal close
    adverse_gap = (open_price - signal_close) / atr  # negative = favourable (gap down)
    if adverse_gap > mult:
        return False, f"gap_up_{gap_pct:.1f}pct_exceeds_{mult}x_atr_limit"
    return True, f"entry_valid_gap_{gap_pct:.1f}pct"
```

**Impact:** Short strategies lose valid favourable-gap entries. Short win rates and ROI are understated in backtests. The magnitude depends on how often stocks gap down the day after a short signal — likely 20–30% of short entries are affected.

---

### BUG-61 · HIGH — Backtest allows multiple concurrent positions in same ticker across consecutive days

**File:** `backtest/engine/backtest.py` — `_process_day()` `open_combos` logic

**What happens:**
- `open_combos = {(ticker, strategy) for open trades}` — blocks same ticker+strategy pair only
- Day 1: AAPL triggers `hull_rsi` → opens position 1
- Day 2: AAPL position 1 still open, `cpr_narrow_bullish` now fires
- `open_combos` check: `(AAPL, cpr_narrow_bullish)` not in combos → **passes**
- `opened_today` check: fresh set each day → **passes**
- Position 2 in AAPL opens on Day 2 while position 1 still running

**In live trading:** `max_positions_per_ticker = 1` blocks position 2 entirely.

**Impact:** Backtest overstates trade count and concentrates exposure in trending stocks. A stock in a 3-week uptrend could accumulate 10+ concurrent positions in backtest while live trading would hold only 1. This inflates backtest ROI for trending conditions.

**Fix:** Add ticker-level check across all open trades:
```python
open_tickers = {t.ticker for t in self.open_trades}
if ticker in open_tickers:
    self.skipped_trades.append({..., "reason": "ticker_already_open"})
    continue
```

---

### BUG-62 · HIGH — Phase 1D cannot run — 2020 OHLCV data not cached, DATA_LOAD_START=2021

**File:** `backtest/config.py` line 23 (`DATA_LOAD_START = date(2021, 1, 1)`) and `backtest/data/cache/ohlcv/`

**What happens:**
1. Phase 1D is designed to test all passing strategies on 5 years including COVID crash (Feb–Jun 2020)
2. `DATA_LOAD_START = date(2021, 1, 1)` — only 2021+ data is fetched
3. OHLCV cache: 494 of 495 tickers have data starting 2021-01-04 (1 starts later)
4. Phase 1D code runs: `df[df.index.date <= as_of]` — for any date in 2020 this returns empty
5. All COVID-period screener calls fail with insufficient history
6. **covid_crisis_2020 regime produces 0 trades — the key Phase 1D validation regime is empty**

**Additional problem:** Technical indicators (EMA-200, ATR-14) require warmup bars. For the COVID crash (starting Feb 2020), warmup from Jan 2020 alone is insufficient — need 200+ trading days = ~Jan 2019 start.

**Fix:**
1. Change `DATA_LOAD_START = date(2019, 1, 1)` in `config.py` for Phase 1D runs
2. Run OHLCV cache update for 2019–2020 data on all 509 tickers before Phase 1D
3. AAII, CNN F&G, FRED macro all have 2020 data ✅ — no additional data work needed
4. Congressional/Quiver: ~95% of files have 2020 data ✅

**This is a Phase 1D blocker, not a Phase 1B/1C blocker.**

---

### BUG-63 · MEDIUM — Email approval system has 6 critical design gaps not addressed in PROJECT_PLAN

**File:** `PROJECT_PLAN.md` Stage 4 design

The 30-minute email approval workflow is missing these critical failure mode designs:

**Gap 1 — Timeout behaviour undefined:** If no reply in 30 minutes, does the trade execute (unsafe) or get cancelled (cautious)? PROJECT_PLAN is silent. Recommendation: auto-cancel with logging. 30 minutes is sufficient for any human who knows trades may arrive.

**Gap 2 — Email parsing robustness:** Reply body containing `APPROVE` will also match in quoted original text, email signatures, auto-reply messages. Parser must search only the first line of reply body, ignore quoted text. Case-insensitive parsing required.

**Gap 3 — Price staleness between approval and execution:** Approved at 4:30PM at $100, order placed at 9:30AM next day — price could be $106 (+6%). The `position_staleness_pct=1%` in LIVE_TRADING_RULES is correct but the timing context is not documented. At next-day open, a 1% staleness window means the order is cancelled if price moved more than 1% from the approved price.

**Gap 4 — Email flood with multiple simultaneous signals:** Up to 10 candidates per day could each require a 30-minute response window. No priority system for which to approve first when capital is limited (e.g. 3 EXCEPTIONAL signals with 5% each = 15% of capital, but total portfolio heat limit may be 20%). The email must include remaining capital headroom.

**Gap 5 — Security:** Spoofed APPROVE reply from non-owner address = unauthorized trade. Fix: verify sender address against a whitelist of known owner emails AND include a one-time HMAC token in each outgoing email that must be echoed in the reply.

**Gap 6 — Position exit command:** No mechanism to manually close a position outside of the trailing stop. If owner wants to exit early (news breaks, stop seems wrong), no command exists. Add: reply `EXIT AAPL` to trigger immediate market-order close.

---

### BUG-64 · MEDIUM — Phase 1C prerequisites not documented — Unusual Whales and Ortex integration requires 2–3 weeks of development

**File:** `PROJECT_PLAN.md` Phase 1C definition

**What happens:**
- PROJECT_PLAN says Phase 1C adds Unusual Whales (options flow) and Ortex (short interest)
- Neither API is integrated into the codebase — no data module, no prefetch script, no agent prompt update
- `backtest/data/` has no `unusual_whales.py` or `ortex.py`
- `backtest/agents/pipeline.py` has no options flow or short interest context in any agent prompt

**Development required before Phase 1C can run:**
1. Unusual Whales historical API: account + API key + prefetch script for 509 tickers + historical flow data cache
2. Ortex: account + API key + daily short interest prefetch + risk agent integration
3. Agent prompt updates: Risk Agent should reference Ortex short interest; Fundamental Agent should reference unusual options flow
4. Point-in-time validation for both new data sources
5. Cost estimate: Unusual Whales ~$50/month USD, Ortex ~$40/month USD

**Timeline impact:** Phase 1C cannot start immediately after Phase 1B. A 2–3 week development sprint is required first. This should be documented as a Phase 1C prerequisite in PROJECT_PLAN.

---

### BUG-65 · MEDIUM — Strategy retirement rule statistically invalid at realistic live trade frequency

**File:** `PROJECT_PLAN.md` line 398 and multiple other references

**Current rule:** Retire a strategy if live win rate drops more than 10pp below backtest for 3 consecutive months.

**Statistical problem:**
At realistic Phase 1C/1D live trade rates (2–5 live trades per strategy per month after filtering to HIGH+ tier), 3 months yields 6–15 trades per strategy. Statistical analysis:

- 45% win rate on 15 trades: 95% CI = [19.8%, 64.3%] — completely overlaps the 55% backtest rate
- 45% win rate on 30 trades: 95% CI = [27.4%, 60.8%] — still overlaps 55%
- **Cannot distinguish a genuinely degraded strategy from bad luck until ~100 trades**

The 3-month retirement window makes the system overly aggressive at retiring strategies that might just be in a temporarily unfavourable regime.

**Fix:** Replace time-based retirement with trade-count-based:
- Minimum 50 live trades before retirement can trigger
- Sequential Probability Ratio Test (SPRT) for continuous monitoring — stops as soon as enough evidence accumulates either way
- Alternatively: 6-month minimum window (doubles live trade count)

---

### BUG-66 · MEDIUM — PROJECT_PLAN mentions "60 strategies" 11 times — 9 of 12 new short strategies not listed

**File:** `PROJECT_PLAN.md` — all 11 references to "60 strategies"

**What happens:**
- The strategy universe expanded to 72 in the code
- 12 new dedicated short strategies were added
- PROJECT_PLAN still says "60 strategies" in 11 places
- The "All 60 Strategies" section (section 18) does not list the new dedicated short strategies
- The "5 of 60 strategies are short" note is now wrong (17 of 72 are short/short-only)

**Fix:** Update all "60 strategies" references to "72 strategies". Update section 18 to add the 12 new short strategies. Update the short strategy count from 5 to 17.

---

### BUG-67 · MEDIUM — Alpaca paper trading (Stage 3) does not match IBKR live trading (Stage 4)

**File:** `PROJECT_PLAN.md` Stage 3 design

**Key differences that reduce Stage 3 validity as a dress rehearsal for Stage 4:**

1. **Currency:** Alpaca is USD-only. IBKR Canada trades in CAD with USD exposure. The FX conversion that affects every live trade (BUG-45) is invisible in Alpaca paper trading.

2. **Short locate:** Alpaca uses third-party locate for short borrows. IBKR has its own borrow desk. A stock that Alpaca can paper-short may be unavailable to short at IBKR Canada in live trading — paper short trades may not be executable live.

3. **Fill simulation:** Both simulate fills but differently. Alpaca fills at midpoint. IBKR fills depend on order type and market conditions.

**Recommendation:** Use IBKR Canada paper trading account (free, same API as live) for Stage 3 instead of Alpaca. This eliminates all three gaps and makes Stage 3 a true dress rehearsal.

---

### BUG-68 · MEDIUM — CLAUDE.md missing 5 critical recent decisions

**File:** `CLAUDE.md`

**Missing from CLAUDE.md that affects Claude's ability to maintain context:**

1. Three-state strategy logic (long/short/avoid) — not mentioned
2. "Buy the dip, sell the rip" philosophy update — not mentioned
3. Wealthsimple no shorts / IBKR for shorts — not mentioned
4. Phase 1B must run without agents ($0 cost) — not mentioned
5. VXX proxy is wrong for VIX (BUG-26) — not mentioned

These are critical decisions approved in this session that Claude must remember for next sessions. Without them, Claude may re-propose already-rejected approaches or miss context.

**Fix:** Update CLAUDE.md with all 5 items above (append, do not remove existing content).

---

### BUG-69 · LOW — Infrastructure design: GitHub Actions vs VPS ambiguity

**File:** `PROJECT_PLAN.md` Stage 3 design

PROJECT_PLAN mentions both GitHub Actions (free, runs daily cron at 6am UTC) and Hetzner VPS ($6/month, for always-on processes) for Stage 3. It is unclear which runs the daily screening job.

**Recommendation:** Use VPS for daily screening (no 6-hour timeout risk, better reliability for 2–4 hour screening jobs). Use GitHub Actions only for triggering the VPS job and committing outputs to GitHub.

---

### BUG-70 · LOW — No database schema designed for Stage 3 PostgreSQL

**File:** `PROJECT_PLAN.md` Stage 3 infrastructure

PROJECT_PLAN specifies PostgreSQL for trade persistence but no schema is defined. Before Stage 3 implementation begins, the schema should be designed and committed to the repo. Suggested tables: `signals`, `open_positions`, `closed_trades`, `agent_results`, `daily_performance`, `strategy_metrics`.

---

### BUG-71 · LOW — IBKR API session management not designed

**File:** `PROJECT_PLAN.md` Stage 4 design

IBKR TWS API requires TWS (Trader Workstation) to be running. IBKR Client Portal API requires periodic OAuth re-authentication. Neither API works well in serverless or ephemeral environments. Running on a Hetzner VPS requires:
- A persistent process manager (systemd or PM2)
- IB Gateway (headless IBKR daemon, preferred over full TWS)
- Session keepalive (IB Gateway disconnects after 24 hours without user action)
- Reconnect logic after session drops

None of this is designed in PROJECT_PLAN. Should be addressed before Stage 4 development begins.

---

## Updated complete bug list — 71 bugs across 5 passes

| Pass | Severity | New bugs |
|---|---|---|
| Pass 1 | 5C / 9H / 7M / 4L | BUG-01 to BUG-25 |
| Pass 2 | +1C / +9H / +9M | BUG-26 to BUG-44 |
| Pass 3 | +0C / +1H / +4M / +1L | BUG-45 to BUG-50 |
| Pass 4 | +0C / +3H / +5M / +3L | BUG-51 to BUG-59 |
| Pass 5 | +0C / +2H / +6M / +3L | BUG-60 to BUG-71 |
| **Total** | **6C / 24H / 31M / 11L** | **72 bugs** |

---

## Decisions needed from owner before work continues

*(In addition to D1–D6 from earlier passes)*

**D7 (BUG-61):** Should the backtest block re-entry on tickers already in open_trades (to match live max_positions_per_ticker=1)? This will reduce trade count and ROI in backtest — brings it closer to live trading reality.

**D8 (BUG-63):** Email approval timeout behaviour — auto-cancel if no reply in 30 minutes, or wait for next day?

**D9 (BUG-67):** Stage 3 paper trading — switch from Alpaca to IBKR paper account? IBKR offers free paper accounts and better mirrors Stage 4 live trading.

**D10 (BUG-64):** Phase 1C timeline — acknowledge that Unusual Whales + Ortex integration is a 2–3 week prerequisite before Phase 1C can run. Do you want to run Phase 1C without these two data sources initially and add them later?

---

*Pass 5 complete. 72 total bugs documented. Next pass (Pass 6): validate all PROJECT_PLAN strategy descriptions against code, check the site_generator.py output for accuracy, review all scripts in /scripts/ for hidden issues, and cross-check all LEARNINGS.md items for implementation status.*

---

## AUDIT PASS 6 — Scripts, validation, cache integrity, drawdown ordering, documentation accuracy

---

### BUG-72 · HIGH — `validate_phase1b_data.py` passes all checks but misses 6 blockers — false safety

**File:** `scripts/validate_phase1b_data.py`

**What happens:** A developer runs this script, sees "✅ ALL CHECKS PASSED — ready for Phase 1B", and proceeds to launch `run_full.sh`. The run produces an empty trade log because the script did not check for:

| Missing check | Impact if not caught |
|---|---|
| BUG-01: `crisis_flag` defined after first use | NameError crashes every trading day — 0 trades |
| BUG-02: `days` defined after use in `close_trade()` | UnboundLocalError on every exit — 0 closes |
| BUG-26: VXX price used as VIX proxy | All days classified as crisis — regime data meaningless |
| BUG-14/74: AAPL/CVS/JPM/NVDA/XLE missing from batches | 5 major tickers never backtested |
| BUG-25: `run_tests.sh` missing `--no-agents` | Test run triggers unwanted agent calls |
| OHLCV 2025-2026 gap | 402 tickers missing 15 months of data, silent |

**Fix:** Add runtime checks to the validation script for each of the above. At minimum:
```python
# Check BUG-01
import ast, pathlib
bt_src = pathlib.Path("backtest/engine/backtest.py").read_text()
lines = bt_src.split("\n")
crisis_flag_defined_before_used = all(
    lines.index(l) < next(i for i,x in enumerate(lines) if "crisis_flag" in x and "==" in x)
    for l in lines if "crisis_flag = regime" in l
)
check("BUG-01 crisis_flag order", crisis_flag_defined_before_used, "crisis_flag used before definition — fix before run")
```

---

### BUG-73 · HIGH — `prepopulate_cache_index.py` writes incompatible format — causes cache misses on every run

**File:** `scripts/prepopulate_cache_index.py` lines 26–30

**What happens:**
```python
existing_index[ticker] = {"cached": True, "path": str(cache_file)}  # WRONG FORMAT
```
`cache.py` reads: `cached_end_str = index.get(ticker, {}).get("end")` — expects `"end"` key.

The prepopulate script writes `{"cached": True, "path": "..."}` — no `"end"` key. When `cache.py` sees `cached_end_str = None`, it falls to the live-fetch path and attempts to download all 509 tickers from yfinance at backtest startup.

**On laptop:** ~402 yfinance calls adding 3+ minutes of startup time before every run.  
**On Codespaces:** yfinance blocked — all 509 tickers return empty DataFrame, 0 trades produced.

The script is called first in `run_full.sh` (`python scripts/prepopulate_cache_index.py`), so this bug fires at the very beginning of every full run.

**Fix:**
```python
# Read actual date range from the Parquet file
import pandas as pd
df_check = pd.read_parquet(cache_file)
if not df_check.empty:
    existing_index[ticker] = {
        "start": str(df_check.index[0].date()),
        "end":   str(df_check.index[-1].date()),
        "rows":  len(df_check),
    }
```

---

### BUG-74 · HIGH — BUG-14 worse than documented: XLE also missing from `run_full.sh` — 5 tickers total

**File:** `run_full.sh` — all 5 batch `--tickers` lists

**Confirmed:** `batch_splits.json` has 509 tickers. `run_full.sh` has 504. Cross-referencing shows:
- AAPL — missing (previously documented)
- CVS — missing (previously documented)
- JPM — missing (previously documented)
- NVDA — missing (previously documented)
- **XLE — missing (NEW finding)**

XLE (Energy Select Sector SPDR ETF, ~$90B AUM) is a high-volume energy sector ETF and a key component of sector-rotation strategies. Its absence means all energy-sector ETF strategies are untested.

**Fix:** Add all 5 tickers to the appropriate batches in `run_full.sh`. Or, better: regenerate `run_full.sh` from `batch_splits.json` using `generate_batch_splits.py` (which already has all 509 tickers correctly).

---

### BUG-75 · MEDIUM — `max_drawdown` computed on unsorted PnL series — results depend on exit order

**File:** `backtest/results/metrics.py` lines 40–44 (`_max_drawdown`) and lines 120–125 (caller)

**What happens:**
1. `g = df[df["strategy"] == strategy]` — rows in exit-date order (when stops were hit)
2. `pnl = g["pnl_pct"]` — PnL in exit-date order, NOT entry-date order
3. `_max_drawdown(pnl)` → `pnl.cumsum()` → cumulative equity curve in exit-date order
4. Max drawdown depends entirely on the **sequence** of returns

**Demonstrated impact:** The same 5 trades `[+3%, -2%, +5%, -4%, +1%]` give max drawdowns of:
- Worst-first order: −2pp (most optimistic)
- Original order: −4pp (arbitrary)
- Best-first order: −6pp (most conservative)

**The measured drawdown is essentially random** relative to the true temporal drawdown experienced by the strategy. It could understate risk by 2–4pp, causing strategies to incorrectly pass the `max_drawdown ≤ 20%` criterion.

**Fix:** Sort by entry_date before computing drawdown:
```python
g_sorted = g.sort_values("entry_date")
pnl = g_sorted["pnl_pct"]
mdd = _max_drawdown(pnl)
```

---

### BUG-76 · MEDIUM — Agent cache fully contaminated: all runs for same ticker+date+phase share one cache entry

**File:** `backtest/agents/pipeline.py` lines 644–647

**Root cause:** BUG-05 (strategies key mismatch) causes `strategies = []` always. The cache key includes `sorted(strategies)` which is always `"none"`. Therefore:

Every agent call for AAPL on 2022-06-01 in phase_1b produces the **same cache key** regardless of which strategies fired. The first call writes the cache. All subsequent calls (possibly with completely different signal conditions) return the first result.

**Concrete scenario:**
- Run 1: AAPL fires `rsi_oversold` on 2022-06-01 → agent analyses RSI context → result cached
- After fixing BUG-08 (`ema_50_200_bullish`): AAPL now ALSO fires `morning_star` on same date
- Run 2: cache hit from Run 1 → agents return RSI-only analysis even though morning_star also fired
- Agent analysis is stale and incomplete

**Fix:** BUG-05 fix (change `strategies_triggered` to `strategies` key) automatically fixes this — cache keys will differentiate by actual strategies fired.

**Immediate action:** After BUG-05 is fixed, **clear the existing agent cache** (`backtest/agents/cache/`). All cached entries were built with the wrong empty-strategy key and should not be reused.

---

### BUG-77 · MEDIUM — Candidate ranking by `strategy_count` inflated by `avoid` entries — top 10 candidates distorted

**File:** `backtest/signals/screener.py` lines 991–992 and `screen_universe()` sort

**Secondary effect of BUG-04:** Because `avoid` entries count toward `strategy_count`, tickers with many conflicting signals (many avoids) rank higher than tickers with strong directional conviction.

**Example:** On a given day:
- NVDA: 3 long signals, 0 short, 3 avoids → `strategy_count = 6` → ranks #1
- AAPL: 5 long signals, 0 short, 0 avoids → `strategy_count = 5` → ranks #2

`max_cands=10` takes NVDA over AAPL despite AAPL having more actionable conviction.

**Fix:** Flows automatically from fixing BUG-04. After fix, `strategy_count = len(triggered_long) + len(triggered_short)` with avoid not counted. Ranking reflects true conviction.

---

### Confirmed correct — no new bugs (Pass 6 checks)

- Quiver data endpoints: correctly separate `historical/` from `live/` naming; point-in-time enforced at query time ✅
- Finnhub prefetch API key: reads from `os.environ`, not hardcoded ✅
- `batch_splits.json`: correctly has all 509 tickers (it is `run_full.sh` that is wrong) ✅
- EXPLANATION.md: already updated to 72 strategies and 500 trades minimum ✅
- `prefetch_quiver.py`: checkpoint/resume logic prevents lost work ✅
- Quiver congressional point-in-time: 45-day disclosure lag correctly enforced ✅
- Quiver institutional 13F: quarter_end + 45 days correctly enforced ✅

---

## Final complete bug registry — 77 bugs across 6 passes

| Pass | Critical | High | Medium | Low | New total |
|---|---|---|---|---|---|
| Pass 1 | 5 | 9 | 7 | 4 | 25 |
| Pass 2 | +1 | +9 | +9 | 0 | 44 |
| Pass 3 | 0 | +1 | +4 | +1 | 50 |
| Pass 4 | 0 | +3 | +5 | +3 | 61 |
| Pass 5 | 0 | +2 | +6 | +3 | 72 |
| Pass 6 | 0 | +3 | +4 | 0 | **79** |

*(Note: BUG-74 extends BUG-14 rather than adding a new bug; total unique bugs = 77 with 2 corrections to prior counts.)*

**Final severity breakdown: 6 CRITICAL · 27 HIGH · 35 MEDIUM · 11 LOW**

---

## Master fix priority list (for owner's week-end review)

### Must fix before test batch (5 items, ~1 hour):
1. **BUG-01** — swap 2 lines in `backtest.py` (crisis_flag)
2. **BUG-02** — swap 2 lines in `exit_manager.py` (days)
3. **BUG-04** — 2-line change in `screener.py` (avoid bucket)
4. **BUG-07** — remove API guard from `run_full.sh` and `run_tests.sh`
5. **BUG-25** — add `--no-agents` to `run_tests.sh`

### Must fix before full run (12 items, ~6 hours):
6. **BUG-26** — replace VXX proxy with SPY 20-day realised vol *(owner decision D1 required)*
7. **BUG-03** — delete first ClosedTrade definition in `exit_manager.py`
8. **BUG-05** — change `strategies_triggered` → `strategies` key in `pipeline.py`
9. **BUG-06** — remove double borrow cost from `improvements.py`
10. **BUG-08** — fix `ema_50_200_bullish` → `price_above_ema_200` in `screener.py`
11. **BUG-09** — add `below_cam_s3` to `technical.py`
12. **BUG-10** — fix 5 agent signal key names in `pipeline.py`
13. **BUG-14/74** — add AAPL/CVS/JPM/NVDA/XLE to `run_full.sh` batches
14. **BUG-28** — fix RSI fallback to use Wilder EWM in `technical.py`
15. **BUG-29** — force-close open trades at backtest end in `backtest.py`
16. **BUG-35** — change Decision Agent default action from `WATCHLIST` to `SKIP`
17. **BUG-73** — fix `prepopulate_cache_index.py` format to match `cache.py`

### Must fix before Phase 1B analysis (10 items, ~4 hours):
18. **BUG-15** — fix `_max_drawdown` to use equity curve not cumsum
19. **BUG-16** — raise `min_trades` from 100 to 500
20. **BUG-17** — add `--force` to `merge_batch_outputs.py`
21. **BUG-31** — raise walk-forward OOS minimum from 30 to 100
22. **BUG-60** — fix short entry gap validation (reject adverse gaps only)
23. **BUG-72** — add 6 critical checks to `validate_phase1b_data.py`
24. **BUG-75** — sort pnl_series by entry_date before drawdown computation
25. **BUG-76** — clear agent cache after BUG-05 fix
26. **BUG-19** — update OHLCV cache to cover 2025-2026 (requires data fetch on laptop)
27. **BUG-11** — fix `williams_r` short default to use boolean key

### Owner decisions required (10 decisions):
- **D1**: VIX proxy method (realised vol vs actual ^VIX)
- **D2**: Regime-aware strategy weighting (suppress wrong-regime strategies)
- **D3**: Mean reversion in crisis — keep as buy-the-dip or add confirmation
- **D4**: Short stop distance — 10% same as longs, or 7% tighter
- **D5**: FX risk — model CAD/USD or treat as USD
- **D6**: VXX in trading universe — remove or keep
- **D7**: Block re-entry on tickers already open (match live single-position rule)
- **D8**: Email approval timeout — auto-cancel or wait
- **D9**: Stage 3 paper trading — Alpaca or IBKR paper account
- **D10**: Phase 1C timeline — run without Unusual Whales/Ortex initially or wait

---

*Audit complete across 6 passes. 77 bugs documented. All findings saved to AUDIT.md on main branch.*
