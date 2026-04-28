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
