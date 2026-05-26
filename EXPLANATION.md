# Plain-English Guide to the Trading System
## Everything you need to understand, with examples — up to end of Phase 1C

**Last updated:** 2026-05-15 (Pass 53 Day 9+ Batch 178 — Phase 1A launch day).
**Live dashboards (3):** https://jeetmehta1991.github.io/stock-picks-app/ — landing + Sprint 0A API coverage + Stage 2 registry + **NEW** Phase 1A trade analysis (12 tabs, Batch 177).
**Backtest health:** 1882 tests passing / 0 failed. Matrix stable 731. 109 API endpoints CACHED across 20 APIs.
**Pass 53 update:** Phase 1A architecture restored across canonical docs. Pass 53 also added: comprehensive signal universe documentation (TRADING_RULES §2A — 6 categories, ~265-275 fields); smart money composite formula with weights matrix (TRADING_RULES §10.8 — was missing pre-Pass-53); API endpoint inventory (TRADING_RULES §13.12 — 16 sources); 5-bucket universe model with B++ schema (T1a/T1b/T1c sub-tiers + Tier 1 ETFs + T2 + T3); universe CSVs moved to top-level `Backtesting universe/` folder; CLAUDE.md HARD RULE for CSV-first data architecture. EXPLANATION.md content below describes the original Phase 1A/1B/1C/1D taxonomy (preserved as primary mental model). The Pass 52 → 53 evolution: original Phase 1A → 1B → 1C → 1D got compressed during Pass 52 turn 119 (DEC-014 absorbed by DEC-422+426); Pass 53 restored Phase 1A as 3 distinct sub-phases (1A baseline → 1A-α rules-only cube → 1A-β scale validation) preceding Phase 1B agent overlay. For canonical taxonomy see PROJECT_PLAN.md §3.6-3.10. EXPLANATION.md retains plain-English flavor of original phasing for reader continuity.

---

## What is this system trying to do?

Imagine you could watch 500 stocks every day, spot the ones about to move, and place trades automatically while you sleep. That is exactly what this system does.

It is a **swing trading** system — meaning it holds positions for days to weeks, not seconds. It is not high-frequency trading. It is closer to how a careful, disciplined investor would trade if they had unlimited time and perfect memory.

**The philosophy is "buy the dip, sell the rip."**
- When a stock falls too far, too fast — buy it expecting a bounce back up (long trade)
- When a stock rises too high, too fast — short it expecting a drop back down (short trade)
- When signals are mixed — do nothing

---

## The Five Stages (big picture — canonical per CLAUDE.md)

| Stage | What happens | Cost per month |
|---|---|---|
| 1 | Proof of concept — webpage with daily picks | ~$0 (COMPLETE; retired) |
| 2 | Strategy validation — backtest all signals across historical regimes | ~$29/mo Polygon + ~$300 one-time Phase 1B-α API budget |
| 3 | Paper trading — validate live with fake money | ~$200 CAD |
| 4 | Live trading small — $500-1000 CAD with email approval | ~$300 CAD |
| 5 | Full automation — autonomous trading | ~$350 CAD |

We are currently in **Stage 2 — Strategy Validation** (Pass 53; Sprint 0A pending Polygon prefetch). Phase 1A baseline is the next gate before agent overlay (Phase 1B).

---

## What is a backtest?

A backtest is asking: "If I had run this strategy on historical data, would it have made money?"

**Example:**
- Strategy: "Buy AAPL when RSI-14 falls below 35 AND price is above the 200-day moving average"
- Test period: January 2022 to January 2023
- Result: This strategy triggered 12 times. It won 7 of them (+42% avg), lost 5 (-8% avg). Win rate = 58%.

A backtest does NOT guarantee future results. But if a strategy fails the backtest completely, it almost certainly fails in live trading too.

---

## What are strategies? (we have ~119)

(Pass 53 update: ~119 strategy classes was the historical snapshot; live `len(ALL_STRATEGIES)`=186 Pass 53 Batch 316a (DEPRECATED_STRATEGIES emptied per owner directive 2026-05-25 — empirical-validation-over-literature-pruning). 2 strategies still skipped at runtime per DEC-490 due to missing-data: `buyback_announcements` needs SEC EDGAR fundamentals Sprint 4; `guidance_driven_momentum` needs earnings transcripts dropped per DEC-485.)

A strategy is a specific set of rules that says "enter a trade when conditions X, Y, and Z are all true at the same time."

**Simple example — Golden Cross:**
- Condition 1: The 50-day moving average crosses ABOVE the 200-day moving average
- Condition 2: Volume today is 2× the 20-day average volume
- Direction: LONG (buy)

When all conditions are true → open a long trade. When the trailing stop triggers → close it.

**The system now evaluates every strategy in THREE states:**
1. **LONG** — conditions say buy
2. **SHORT** — conditions say sell (the exact opposite signals)
3. **AVOID** — long and short signals both firing at the same time = conflicting = do nothing

**Example of three-state in practice:**
- Golden Cross fires LONG when: 50-day crosses above 200-day
- Golden Cross fires SHORT when: 50-day crosses BELOW 200-day (death cross)
- If somehow both crossed on the same day: AVOID

---

## The 7 strategy categories

### 1. Pivot (9 strategies)
Pivot points are mathematical price levels calculated from the previous day's high, low, and close. Professional traders watch these levels obsessively.

**Example — `cpr_narrow_bullish`:**
- The Central Pivot Range (CPR) is very narrow today (tight range yesterday)
- Price opened ABOVE the CPR
- RSI is above 50
- All three true → this is a directional day, bullish bias → BUY

**Short version:** If all three reverse (price below CPR, RSI<50) → SHORT

### 2. Momentum (9 strategies)
Momentum strategies catch stocks that are starting to move in a direction after being stalled.

**Example — `macd_crossover`:**
- MACD line crosses ABOVE the signal line → momentum turning bullish → BUY
- MACD line crosses BELOW the signal line → momentum turning bearish → SHORT

Think of MACD as a speedometer for price movement. Crossing zero means the car changed direction.

### 3. Trend (9 strategies)
Trend strategies enter after a trend is already confirmed. They sacrifice early entry for higher confidence.

**Example — `supertrend_macd`:**
- Supertrend indicator is showing green (bullish) — confirmed uptrend
- MACD histogram is positive — momentum agreeing
- ADX above 20 — the trend has actual strength, not a sideways drift
- All three → BUY

Short version: All three flip bearish → SHORT

### 4. Mean Reversion (11 strategies)
Mean reversion strategies say "this stock went too far from normal — it will come back."

**Example — `bollinger_lower`:**
- Price touches the lower Bollinger Band (statistically 2 standard deviations below the 20-day average)
- RSI-14 is below 40 (oversold)
- ADX below 30 (no strong downtrend — just a dip, not a collapse)
- All three → BUY (expecting bounce back to the middle band)

Short version: Price at upper band, RSI>60, ADX<30 → SHORT (expecting drop back to middle)

### 5. Breakout (6 strategies)
Breakout strategies enter when price breaks through a significant level with strong volume.

**Example — `donchian_10_breakout`:**
- Price breaks above the 10-day highest high (new 10-day high)
- Volume is 1.5× average (institutions are buying)
- MACD is positive
- All three → BUY (momentum expected to continue)

Short version: Price breaks below 10-day lowest low with volume → SHORT

### 6. Candle Patterns (6 strategies)
Candlestick patterns are specific visual formations in price bars that have well-documented predictive value.

**Example — `morning_star`:**
- Day 1: Big red candle (sellers dominated)
- Day 2: Small candle (indecision — buyers and sellers equal)
- Day 3: Big green candle (buyers took over)
- RSI below 45, above 50/200 EMA
- Pattern + context → BUY

Short version: Evening star (reverse pattern — buyers giving up to sellers) + RSI>55 + below 50/200 EMA → SHORT

### 7. Confluence (9 strategies)
Confluence strategies require multiple independent systems to agree simultaneously. Fewer signals but highest conviction.

**Example — `camarilla_rsi_obv` (highest conviction long):**
- Price near Camarilla S3 level (strongest institutional support)
- RSI below 35 (oversold)
- OBV rising (institutions accumulating)
- CMF positive (money flow positive)
- Four independent systems all pointing to "buy" → BUY at maximum confidence tier

Short version: Near Camarilla R3 + RSI>65 + OBV falling + CMF negative → SHORT at maximum conviction

---

## New dedicated short strategies (12 added)

Beyond the three-state logic on existing strategies, we added 12 strategies that are SHORT-ONLY by design:

**Trend-following shorts (4):**
- `death_cross_50_200_volume` — 50-day crosses below 200-day with 2× volume (death cross confirmed by institutions)
- `supertrend_macd_short` — Supertrend bearish + MACD bearish + ADX>20 (three systems agree it's falling)
- `ichimoku_cloud_breakdown` — Price breaks below cloud + Tenkan below Kijun + ADX strong
- `parabolic_sar_flip_short` — SAR flips above price (trend reversed down) + ADX trending

**Momentum shorts (3):**
- `macd_crossover_short` — MACD crosses below signal line (momentum turned negative)
- `hull_rsi_short` — Hull MA falling + price below Hull + RSI-9<50
- `stochrsi_overbought_short` — StochRSI above 80 + K crosses below D

**Breakdown shorts (3 — no long equivalent):**
- `donchian_breakdown_short` — Price breaks 10-day low with volume + MACD bearish
- `52w_low_breakdown` — Price breaks 52-week low with 2× volume (serious capitulation)
- `prev_day_low_breakdown` — Breaks below previous day's low with volume, below VWAP

**Confluence shorts (2):**
- `camarilla_rsi_obv_short` — All four systems agreeing bearish at R3 resistance
- `cpr_narrow_momentum_short` — Narrow CPR + below CPR + RSI<50 + MACD bearish

---

## What are signals?

Signals are individual measurements of what a stock is doing right now. Strategies combine multiple signals.

**Examples of signals:**
- `rsi_14 = 28.4` → RSI-14 is 28.4 (below 35 = oversold)
- `macd_12_26_9_crossover_up = True` → MACD just crossed above zero today
- `vol_spike_2x = True` → Today's volume is 2× the 20-day average
- `ichi_above_cloud = False` → Price is NOT above the Ichimoku cloud
- `break_52w_low = True` → Price just broke its 52-week low (new added signal)

The system computes ~220 signals per ticker per day from OHLCV data (Open, High, Low, Close, Volume).

---

## What is a confidence tier?

Not all signals are equal. A confidence tier is the system's assessment of how strong a trade setup is.

| Tier | What it means | Position size |
|---|---|---|
| EXCEPTIONAL | Extremely rare — multiple systems + smart money all aligned | 5% of portfolio |
| VERY_HIGH | 4+ signals + smart money confirming | 4% |
| HIGH | 3+ signals firing | 3% |
| MEDIUM_HIGH | 2 signals firing | 1.5% |
| MEDIUM | 1 signal + smart money buy | 0.75% |
| LOW | 1 signal only | 0% (watch only) |
| AVOID | Strong bearish smart money signals | Evaluate as short |

**Example:**
- AAPL triggers `hull_rsi` (1 strategy) AND `cpr_narrow_bullish` (1 strategy) on the same day → 2 strategies → MEDIUM_HIGH tier → open position at 1.5% of portfolio

---

## What are agents? (the AI layer)

Eleven active AI agents (Claude Haiku model in Phase 1B; Sonnet in Phase 1C+) analyse each trade candidate before it opens. They adjust the confidence tier up or down based on broader context. Architecture per [DETAILED_PROJECT_PLAN.md §2.6](DETAILED_PROJECT_PLAN.md) (TradingAgents Pattern 2 integration; DEC-057). Plus 1 Reflection node post-decision (12 total LLM nodes per propagate(), per [LEARNINGS.md L94](LEARNINGS.md)).

**The 11 active agents:**

| # | Agent | What it checks |
|---|---|---|
| 1 | Market Analyst | Technical indicators, ATR, volume, momentum — false signal or genuine? |
| 2 | Fundamentals Analyst | Earnings, balance sheet, insider/congressional buying, contracts |
| 3 | News Analyst | News sentiment, headline-flow, event-driven catalysts |
| 4 | Bull Researcher | Argues the long side — strongest case for entry |
| 5 | Bear Researcher | Argues the short / no-trade side — strongest case against |
| 6 | Research Manager | Adjudicates Bull vs Bear debate → research conclusion |
| 7 | Trader | Position sizing + entry/exit timing recommendation |
| 8 | Aggressive Risk Debater | Argues for taking risk — opportunity cost framing |
| 9 | Conservative Risk Debater | Argues for limiting risk — capital preservation framing |
| 10 | Neutral Risk Debater | Balanced risk perspective — base-rate framing |
| 11 | Portfolio Manager | Final synthesis → score 0-100 → adjusts tier |
| (+1) | Reflection (post-decision) | Stores trade rationale for continuous learning |

**Example — NVDA on Jan 10, 2022:**
- Preliminary tier: HIGH (3 strategies fired)
- Technical agent: score 4/10 — "oversold but tech sector under heavy selling"
- Risk agent: score 2/10 — "VIX crisis regime, CPI in 2 days"
- Bull/Bear: Bear wins — "no catalyst to reverse the trend"
- Decision: final score 22/100 → below 35 threshold → downgrade to MEDIUM_HIGH
- Result: trade opened at 1.5% instead of 3%

**What we learned from Phase 1B agents:**
- Risk Agent scored exactly 2/10 on ALL 34,727 trades — it was locked to a floor because VIX was in crisis. Zero variance = zero value.
- Agents never recommended ENTER (0% of trades). They said SKIP (87%) or AVOID (11%). But trades opened anyway because the engine only used the score, not the label.
- **Fix for Phase 1C:** SKIP and AVOID will actually block long entries AND trigger short evaluation. Agents will finally have teeth.

---

## What is a regime?

A regime is the current market environment. The system classifies every day into one of these:

| Regime | What it means | Example period |
|---|---|---|
| `bull` | Market trending up, low fear | 2023 |
| `neutral` | Sideways market | Most of 2021 |
| `bear` | Market trending down | Late 2022 |
| `crisis_CRISIS_FLAG` | Extreme fear, VIX very high | Jan–Sep 2022 |

**Why regimes matter:**
- In `bull` regime: long strategies work well, short strategies mostly fail
- In `crisis` regime: most long strategies lose, but specific ones (energy in March 2022) work well AND short strategies have strong edge
- The system adjusts which strategies to emphasise based on regime

**From Phase 1B data:**
- July 2022 was `crisis` regime but had 56.7% win rate — the bear market rally. The system correctly profited in a month that felt like a crisis.
- September 2022: 8.5% win rate. Worst month. No long strategy should have been active.

---

## What is smart money?

Smart money is what insiders, institutional investors, and well-connected people are doing with their own money. The system tracks four types:

**1. Congressional trades** — US senators and congress members must report their stock trades. Research shows they significantly outperform the market. If a congressman bought $500K of stock in a company last week, that is a signal.

**2. Insider buying** — When a company's own CEO or CFO buys shares with their own money (not stock options), they almost certainly believe the stock is undervalued.

**3. 13F institutional filings** — Large funds report their holdings quarterly. New large positions = institutional conviction.

**4. Government contracts** — A company just won a $200M government contract that is not yet widely known = fundamental catalyst.

**Example:**
- FANG (energy company) — congressional member bought $300K the week before earnings + company has new government contracts for oil leases → smart money alignment → confidence tier stays HIGH despite crisis regime

---

## What is the exit system?

Every trade has a trailing stop. There are no fixed profit targets — winners are held until the trailing stop triggers.

**How trailing stop works:**
- Buy AAPL at $150. Initial stop set at $135 (10% below).
- AAPL rises to $180. Stop rises to $162 (10% below $180).
- AAPL falls to $162 → stop triggered → sell → profit locked in.
- AAPL never rises to $180. Falls to $135 immediately → original stop triggered → small loss.

**Stop distance by strategy category:**

| Category | Stop distance | Why |
|---|---|---|
| Pivot strategies | 1.0× ATR | Tight — pivot levels are precise |
| Mean reversion | 1.5× ATR | Wider — needs room to bounce |
| Trend following | 2.0× ATR | Wide — trends have pullbacks |
| Breakout | 1.5× ATR | Medium — breakouts can retest |

ATR = Average True Range = how much the stock normally moves per day. A 1.0× ATR stop means: stop at one day's normal movement below entry.

---

## What is the agent pipeline in Phase 1B vs Phase 1C?

**Phase 1B (current — NO agents, $0 cost):**
- All Layer 1 baseline 60 + Layer 2/2D/3/4 strategies screen every ticker every day (full layered roster ~108-133 classes; 100+ unique testable strategies projected — see [CANONICAL_FACTS.md F-002](CANONICAL_FACTS.md))
- Three-state evaluation: long / short / avoid
- Preliminary tier assigned by rule (how many strategies fired)
- Trade opens at preliminary tier size
- No AI involved — pure rules

**Phase 1C (next — Sonnet agents, ~$15-20 cost):**
- Only strategies that PASSED Phase 1B criteria get agents
- Agents use Claude Sonnet (more capable than Haiku)
- SKIP/AVOID actions will actually block entries
- SKIP on a long → evaluate if a short strategy is firing → open short
- AVOID on a long → stronger bearish conviction → open short at higher size if short signal present
- Decision agent receives a computed base score (not free-form) → adjusts ±15 points max
- Risk agent scores RELATIVE to crisis baseline (not absolute) → variance restored

---

## What is Phase 1B trying to prove?

Phase 1B runs the full layered strategy roster (Layer 1 baseline 60 + Layer 2 Phase 0.D ICT/Earnings/Calendar + Layer 2D form-derived ICT + Layer 3 Pass 52 RESOLVED chart-pattern/categories + Layer 4 PENDING ≈ ~108-133 classes; 100+ unique testable strategies projected — see [CANONICAL_FACTS.md F-002](CANONICAL_FACTS.md)) on the full 5-bucket universe (~1,937 unique tickers per [F-005](CANONICAL_FACTS.md)) across the walk-forward window (1y warmup + 4 OOS folds × 1y per [DEC-505](AUDIT_INDEX.md)). The goal is to answer: **"Which strategies have statistically valid edge?"**

A strategy passes Phase 1B if it meets ALL 10 criteria across enough trades:
1. Win rate ≥ 55% (more than half the trades win)
2. Profit factor ≥ 1.3 (winners outweigh losers by 30%)
3. Expected value > 0 (on average, each trade makes money)
4. Win/loss ratio ≥ 1.0 (average win ≥ average loss)
5. Max drawdown ≤ 20% (never lost more than 20% in a straight run)
6. Total ROI > 0 (made money overall)
7. Smart money lift ≥ 3% (win rate higher when smart money agrees)
8. Macro correlation ≥ 5% (win rate higher in favourable macro regime)
9. Minimum 500 trades (enough data to be statistically meaningful)
10. Agent agreement (in Phase 1C — agents agree with the direction)

**What happened in our partial Phase 1B run:**
- Covered Jan 2022 – Jan 2023 only (1 year of 4+ planned)
- 34,727 trades, 442 tickers, long-only (shorts not yet implemented)
- Overall win rate: 29.7% — expected in a sustained bear/crisis market for long-only strategies
- July 2022 win rate: 56.7% — buy-the-dip works in bear market rallies
- No strategy passed all 10 criteria yet — not enough data, not enough regimes

---

## What does the full run need to look like?

**Phase 1B full run plan:**
- Full layered strategy roster (~108-133 classes per [F-002](CANONICAL_FACTS.md); long + short + avoid variants)
- 5-bucket universe ~1,937 unique tickers per [F-005](CANONICAL_FACTS.md) (T1a/T1c/T1ETF/T2/T3 with DEC-504 multi-tier precedence)
- Walk-forward window: 1y warmup + 4 OOS folds × 1y per [DEC-505](AUDIT_INDEX.md) (Polygon Stocks Starter 5y rolling cap)
- NO agents ($0 cost)
- 5 parallel batches on laptop
- Estimated time: 15-20 hours
- Estimated cost: $0 (no API calls)

**Data already committed:**
- 34,727 trades from partial run (Jan 2022 – Jan 2023) — stored separately, valid for reference
- Agent cache with 12,000+ cached responses — reusable if agents are re-enabled later

---

## Why did we spend $150 and what did we learn?

The $150 went to Claude Haiku API calls for agents during the Phase 1B partial run. It was expensive and the agents added near-zero differentiation because:

1. The entire run was in crisis regime — Risk Agent locked to floor on every trade
2. Agents scored every trade similarly (crisis = uniformly bad)
3. Agent action labels (SKIP/AVOID) were not wired to actually block trades
4. The upgrade threshold (75) was never reachable given the score distribution

**What we gained:**
- Proof that the pipeline works end-to-end
- Understanding of exactly how agents behave in crisis regime
- Data showing which sectors, strategies, and months have edge
- Design fixes for Phase 1C agents that will make them actually useful

**The $150 was an expensive lesson, not wasted money.** Without running it, we would have gone into Phase 1C with broken agents and spent far more fixing them on live Sonnet calls.

---

## Key numbers to remember

| Metric | Value | What it means |
|---|---|---|
| Strategies | 72 | 60 original + 12 new dedicated shorts |
| Tickers | 509 | Full S&P 500 + key ETFs |
| Backtest period | Jan 2022 – Mar 2026 | 4+ years, all regimes |
| Phase 1B cost | $0 | No agents = no API cost |
| Phase 1C cost est. | ~$15-20 USD | Sonnet on passing strategies only |
| Min trades to pass | 500 | Statistical validity threshold |
| Position sizing | 0.75% – 5% | Scales with confidence tier |
| Max drawdown threshold | 20% | Strategy must not lose >20% in a streak |
| Target win rate | ≥ 55% | More than half the trades must win |
| Short selling broker | IBKR Canada (Stage 4) | Wealthsimple does not support shorts |

---

## Glossary of terms used in this project

| Term | Plain English |
|---|---|
| ATR | Average True Range — how much a stock normally moves per day |
| Backtest | Testing a strategy on historical data |
| Circuit breaker | An emergency rule that closes a trade if it falls too fast |
| CMF | Chaikin Money Flow — measures whether money is flowing in or out of a stock |
| Confidence tier | How strong a trade setup is (LOW → EXCEPTIONAL) |
| CPR | Central Pivot Range — a daily price zone professional traders watch |
| Death cross | 50-day MA crosses below 200-day MA (bearish) |
| Donchian channel | The highest high and lowest low over N days |
| EMA | Exponential Moving Average — a moving average that weights recent prices more |
| Force Index | Price change × volume — measures the power behind a move |
| Golden cross | 50-day MA crosses above 200-day MA (bullish) |
| Haiku | Claude Haiku — fast, cheap AI model used in Phase 1B agents |
| Hull MA | Hull Moving Average — a faster, smoother moving average |
| Ichimoku | A Japanese technical system with 5 components showing trend, support, resistance |
| MACD | Moving Average Convergence/Divergence — momentum indicator |
| MFI | Money Flow Index — volume-weighted RSI |
| OBV | On-Balance Volume — running total of volume based on price direction |
| Parquet | A compressed file format used to store price data efficiently |
| Pivot | Mathematical price levels calculated from previous day's price action |
| Preliminary tier | Confidence tier assigned by rules before agents run |
| Profit factor | Total winnings ÷ total losses (>1.3 = strategy makes more than it loses) |
| Regime | The current market environment (bull / bear / crisis) |
| RSI | Relative Strength Index — measures how overbought or oversold a stock is (0-100) |
| Sonnet | Claude Sonnet — more capable AI model used in Phase 1C agents |
| SMA | Simple Moving Average — average price over N days, equal weighting |
| Smart money | Insiders, institutions, and congress members whose trades are publicly reported |
| Squeeze | When Bollinger Bands compress inside Keltner Channels — energy building for a move |
| Supertrend | A trend indicator that flips bullish or bearish at key price levels |
| Swing trading | Holding positions for days to weeks (not intraday) |
| Trailing stop | A stop-loss that moves up as the price rises, locking in profit |
| VIX | Volatility Index — the "fear index" of the market (>30 = elevated fear) |
| VWAP | Volume-Weighted Average Price — the average price weighted by volume |
| Walk-forward | Validating a strategy on data it was NOT trained on (out-of-sample testing) |
| Win rate | Percentage of trades that make money |
