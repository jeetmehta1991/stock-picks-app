# Stock Picks & Automated Trading System
## Project Plan — Complete Reference
**Last updated:** April 2026 | **Repo:** github.com/jeetmehta1991/stock-picks-app

---

## What This Project Is

This project builds an automated swing trading system for US equities from scratch. It starts as a simple stock picks webpage and evolves into a fully automated trading engine. Every stage is proven before money is risked, and every strategy is mathematically validated before being deployed live.

**Swing trading** means holding positions for days to weeks — not intraday. We buy when a stock shows multiple signals of strength and sell when the trailing stop triggers or the setup breaks down. We are not day traders.

**The core philosophy:** Buy the dip, sell the rip — profit from both oversold bounces and overbought reversals across all market regimes. Find edges that have worked consistently across multiple market conditions. Validate them rigorously. Deploy them with strict risk management. Accept that drawdowns will happen and manage them, rather than trying to avoid them entirely.

**Long and short:** Every strategy evaluates three states — long (buy), short (sell), or avoid (conflicting signals). In a crisis, when everything is falling, the system looks for short opportunities. In a rally, it looks for longs. When signals conflict, it does nothing. This is how professional traders operate across all market conditions.

**Broker note:** Short selling requires a broker that supports it. Wealthsimple Canada does not support short selling as of 2026. Backtesting includes shorts. For live trading of short strategies, switch to IBKR Canada (planned for Stage 4). Wealthsimple remains viable for long-only live trading.

---

## Current Status

| Stage | Status | What it means |
|---|---|---|
| Stage 1 — Daily stock picks | ✅ Complete | Live website showing top US and Canadian gainers |
| Stage 2 Phase 1A — Proof of concept | ✅ Complete | Tested 67 instruments across 4 years. Pipeline works. |
| Stage 2 Phase 1B — Full validation | 🔄 Batch test complete, full run pending | 5-ticker batch test done (577 trades). Full 509-ticker run ready to start on laptop. |
| Stage 2 Phase 1C — Sonnet refinement | ⏳ Pending | Deeper AI analysis on strategies that passed 1B |
| Stage 2 Phase 1D — 5-year test | ⏳ Pending | Extended validation including COVID 2020 |
| Stage 3 — Paper trading | ⏳ Pending | Automated paper trading for 3-6 months |
| Stage 4 — Live small | ⏳ Pending | Real money, small size, email approval every trade |
| Stage 5 — Full automation | ⏳ Pending | Larger size, fully automated |

---

## The Five Stages — What Happens in Each

### Stage 1: Proof of Concept (Complete)

The project started as a simple webpage that shows the top gaining stocks each day in the US and Canadian markets. This is updated automatically every morning at 6am via GitHub Actions and hosted on GitHub Pages at zero cost.

**What it produces:** A dark-themed webpage with today's top movers. No trading decisions — just information.

**Why we built this first:** To establish the GitHub infrastructure (automated workflows, Pages hosting, Python pipeline) before building anything complex.

**APIs used:** Alpha Vantage (free tier) for stock quotes. GitHub Actions for automation.

---

### Stage 2: Strategy Validation (Current Stage)

This is the most important stage and the one we are in now. No money is at risk. The entire purpose is to find out which trading strategies actually work, under which conditions, and with what level of confidence.

**The fundamental question we're answering:** If we had followed a particular trading rule for the last 4 years, would we have made money consistently — not just in bull markets, but across bear markets, rising rates, crises, and sector-specific events?

**What we're testing:** 60 different trading strategies across 509 US stocks and ETFs, covering January 2022 through March 2026. This period includes a significant bear market (2022), a strong bull recovery (2023-2024), AI sector divergence, and Trump tariff uncertainty (2025) — giving us 7 distinct market regimes to validate against.

**How validation works (the IS/OOS split explained simply):**

Think of it like preparing for an exam. You study from old past papers (this is the In-Sample period). Then you sit a real exam with questions you've never seen before (this is the Out-of-Sample period). If you only memorised the past papers without understanding the concepts, you'll fail the real exam.

In our system:
- **In-Sample (IS):** January 2022 – December 2024. We use this 3-year period to see which strategies produce good results.
- **Out-of-Sample (OOS):** January 2025 – March 2026. This is 15 months of data the strategies never influenced. We test the IS winners here.
- **Why two windows?** We do this test twice with different splits to make sure we're not getting lucky. A strategy must pass BOTH tests to be called "Robust." Passing one could be a coincidence.
  - Window 1: Study 2022-2023, test on 2024
  - Window 2: Study 2022-2024, test on 2025-March 2026
- **What "Robust" means:** The strategy passed both unseen test periods. It didn't just memorise the study material.
- **What "Overfit" means:** It passed the study period but failed both real tests. It memorised patterns that don't generalise.
- **INSUFFICIENT_OOS_DATA:** Fewer than 30 trades in the OOS period. We can't make a verdict with so few data points.

**The 4 validation phases:**

**Phase 1A (Complete):** We ran all 60 strategies on a small universe of 67 instruments to make sure the pipeline works correctly. We found that `atr_trail_1x` (a volatility-adjusted trailing stop) outperforms all other exit methods, winning 20 out of 29 strategy comparisons. No strategies passed all criteria yet — expected, because 67 instruments isn't enough to generate 500+ trades per strategy.

**Phase 1B (Running now):** Full 509-instrument run. Every strategy gets enough trades to be statistically meaningful. AI agents (Claude Haiku) analyse each trade candidate and adjust confidence tiers. Cost: approximately $116 CAD in AI API calls.

**Phase 1C (After 1B):** All strategies that pass Phase 1B criteria are re-run with Claude Sonnet (a more capable model) for deeper analysis. Unusual Whales (options flow) and Ortex (short interest) data are added — validating their contribution before using them in live trading.

**Phase 1D (After 1C):** All strategies passing Phase 1C are tested on 5 years of data including COVID 2020 — the most extreme market event in recent history. This is the final validation before paper trading.

#### What the 60 Strategies Are

The strategies fall into 7 categories, each with a different logic:

**Pivot-based (10 strategies):** Stocks have daily support and resistance levels called "pivots" calculated from the previous day's trading range. These strategies buy near support levels (expecting bounces) or buy when resistance levels break (expecting continuation). Example: `pivot_s1_bounce` buys when a stock is near its S1 support level AND shows a bullish candlestick pattern AND volume is rising.

**Momentum (9 strategies):** When a stock's momentum turns positive after being negative, it often continues higher. These strategies use indicators like MACD, RSI, and Rate of Change to catch the early stages of momentum shifts.

**Trend following (9 strategies):** Strong trends tend to persist. These strategies enter when a trend is clearly established — for example, when a shorter moving average crosses above a longer one (golden cross), confirming buyers are in control.

**Mean reversion (11 strategies):** Stocks that fall too far, too fast, tend to snap back. These strategies buy extreme oversold conditions (RSI below 35, at Bollinger Band lower boundary) expecting a bounce. Also includes short strategies for extreme overbought conditions.

**Breakout (6 strategies):** When a stock breaks above a significant level with strong volume, institutional buying is often behind it. These strategies catch breakouts from consolidation patterns, 52-week highs, and volume squeezes.

**Candle patterns (6 strategies):** Specific Japanese candlestick patterns (morning star, bullish engulfing, shooting star) at key price levels have well-documented predictive value. These strategies require the pattern to appear at a significant support or resistance level.

**Confluence (9 strategies):** These require multiple independent signals to fire simultaneously. For example, `camarilla_rsi_obv` requires: near Camarilla S3 support AND RSI below 35 AND rising OBV AND positive money flow — four completely different systems all pointing the same direction. Rarer but higher conviction.

#### How AI Agents Evaluate Each Trade

When a candidate stock passes the screener (one or more strategies fired), six AI agents evaluate it in sequence:

1. **Technical Agent:** Examines the specific signals that triggered the strategy, the stock's position relative to its 52-week range, support/resistance levels, and whether the sector ETF is a tailwind or headwind today.

2. **Fundamental Agent:** Looks at insider buying and selling (from Form 4 filings), institutional 13F positioning changes, government contracts won or lost, lobbying activity trends, and WallStreetBets/Wikipedia interest as retail sentiment proxies.

3. **Sentiment Agent:** Examines the three most recent congressional trades in this stock (with representative names, amounts, and parties), AAII investor sentiment survey readings, CNN Fear & Greed index, and news sentiment from Alpha Vantage.

4. **Risk Agent:** Assesses the macro environment — yield curve shape, VIX level, DXY trend, corporate credit spreads, proximity to major economic events (CPI, NFP, FOMC meetings), and earnings proximity.

5. **Bull/Bear Debate:** One agent argues the bull case for the trade, another argues the bear case. They each know where price is relative to support and resistance. The debate result captures whether the overall signal picture is convincing.

6. **Decision Agent:** Synthesises all five agent outputs and the current portfolio state (how many positions are open, sector concentration, whether we already hold this stock) into a final conviction score from 0 to 100. This score is independent — the agent doesn't know the tier thresholds, so it can't game them.

#### Two-Stage Confidence Tiering

The confidence tier system has two stages:

**Stage 1 (Rule-based, before agents):** The preliminary tier is assigned based on raw signal counts and smart money signals. Three strategies firing plus both congressional and insider cluster buys = EXCEPTIONAL. Two strategies plus one smart money signal = VERY HIGH. And so on down to LOW.

**Stage 2 (Agent-adjusted):** The agent's final_score (0-100) can move the tier up or down by one level. Score ≥ 75 upgrades the tier. Score ≤ 40 downgrades it. AVOID tier never upgrades regardless of agent score.

This separation is critical: agents evaluate signal quality independently, without knowing the tier rules. The tier assignment then uses their score as evidence, not as the output.

| Tier | Conditions | Position Size | Notes |
|---|---|---|---|
| EXCEPTIONAL | 3+ strategies + congressional buy + insider cluster buy | 5% of capital | Rarest — both SM signals required |
| VERY HIGH | 2+ strategies + congressional OR insider buy | 4% of capital | Strong SM confirmation |
| HIGH | 3+ strategies, no smart money | 3% of capital | Technical confluence only |
| MEDIUM-HIGH | 2 strategies, no smart money | 1.5% of capital | Moderate conviction |
| MEDIUM | 1 strategy + any smart money buy | 0.75% of capital | Small — SM present |
| LOW | 1 strategy only | 0% — watch only | Insufficient evidence |
| AVOID | Congressional sell + insider cluster sell | 0% long | Evaluate as short setup |

**AVOID as a short opportunity:** When both congressional members AND corporate insiders are selling a stock simultaneously, this is the highest-conviction "informed selling" signal available. Rather than just blocking a long trade, the system evaluates whether a short strategy is also firing — if so, this becomes an EXCEPTIONAL conviction short entry.

#### The Smart Money Data

Smart money signals come from three sources:

**Congressional trading:** US members of Congress are legally required to disclose stock trades within 45 days (STOCK Act). Research shows these trades outperform the market significantly, likely due to policy insight. We apply a 45-day disclosure lag to ensure we're using information that was actually public at the time. Trades are also age-weighted: trades disclosed within 30 days get full weight, 30-60 days get 50% weight, older than 60 days are excluded.

**Insider trading (Form 4):** Corporate insiders (CEOs, CFOs, board members) must file Form 4 within 2 business days of trading. We filter out non-discretionary transactions (option exercises, automated 10b5-1 plans, gifts) and focus on open-market purchases. A CEO buying stock with their own money is a strong signal. We specifically look for cluster buys (3+ insiders buying simultaneously) and CEO purchases.

**Institutional 13F:** Investment funds managing over $100M must disclose their holdings quarterly. A 45-day lag is applied after quarter-end. This captures systematic accumulation or distribution by major funds.

#### Exit System

All exits use ATR-based trailing stops — the stop is set at 1× ATR (Average True Range) below the highest closing price. ATR normalises the stop to each stock's volatility: a volatile stock like NVDA gets a wider stop than a stable stock like KO. This was confirmed as the best exit method in Phase 1A (winning 20/29 strategy comparisons).

The trailing stop is checked against the daily intraday low (not just the closing price), because real stop orders trigger whenever price trades through the stop level — not just at the end of the day.

Five circuit breakers override the trailing stop in extreme conditions:
1. Overnight gap > 12% in wrong direction → exit at open
2. Earnings gap > 8% in wrong direction → exit at open
3. Intraday halt + > 15% loss from entry → exit on resume
4. Market-wide circuit breaker halt → pause all new trades
5. VIX > 40 → reduce new position sizes to 50%, require VERY HIGH minimum tier. Do NOT tighten existing stops (this causes whipsawing and forced exits at the worst time). VIX > 50 → suspend new entries entirely.

**On crisis markets:** When VIX is above 40 (like March 2020 or October 2022), conventional wisdom says stop trading. Our philosophy is the opposite — these are exactly when the best entry prices appear. We reduce position sizes but do not stop trading longs. The trailing stop manages the downside.

#### The 10 Passing Criteria

For a strategy to advance to Phase 1C, it must pass all 10 of these simultaneously. Thresholds are sector-adjusted (energy and tech get wider drawdown tolerance than utilities and consumer staples):

1. **Win rate ≥ 55%** (high volatility sectors: ≥ 50%)
2. **Profit factor > 1.3** — total winning dollars / total losing dollars (high vol: > 1.2)
3. **Expected value > 0** — (win rate × avg win) + (loss rate × avg loss) > 0
4. **Win/loss ratio > 1.0** — average winner larger than average loser
5. **Maximum drawdown < 20%** (high vol: < 25%, low vol: < 15%)
6. **Total ROI > 0%** — overall profit across the full backtest period
7. **Smart money lift ≥ 3pp** — win rate is at least 3 percentage points higher when SM signals are present vs absent (min 30 trades in each bucket)
8. **Macro correlation ≥ 5pp** — win rate is at least 5pp higher in favourable macro regimes vs unfavourable (min 20 trades per regime)
9. **Minimum 500 trades** — statistical validity threshold
10. **Per-regime verdict** — each strategy evaluated independently within each regime. A strategy passes for a specific regime if it meets all 9 other criteria within that regime (minimum 30 trades required). The output is a strategy-regime matrix, not a universal pass/fail. A strategy may be excellent in crisis and irrelevant in bull — both are valid outcomes. In live trading the screener activates only strategies validated for the current regime.

**Output:** `strategy_regime_matrix.json` — maps each strategy to its passing regimes. Format: `{strategy: {best_regimes: [...], regime_verdicts: {regime: PASS/FAIL/INSUFFICIENT_DATA}, overall_win_rate, total_trades}}`. This is the primary artifact used by the Stage 3 live screener to activate only regime-appropriate strategies.

Statistical validity note: All win rates are reported with 95% confidence intervals. If the lower confidence bound falls below 50%, the strategy is flagged as potentially indistinguishable from random chance, regardless of the point estimate.

#### Sector-Adjusted Passing Criteria

Different sectors have inherently different volatility profiles. The same 22% drawdown means very different things in Energy vs Consumer Staples.

| Sector type | Examples | Win rate | Max drawdown | Min profit factor |
|---|---|---|---|---|
| High volatility | Energy, Tech, Healthcare | ≥ 50% | < 25% | > 1.2 |
| Medium volatility | Financials, Industrials | ≥ 55% | < 20% | > 1.3 |
| Low volatility | Staples, Utilities, REITs | ≥ 58% | < 15% | > 1.4 |

#### Data Pre-Fetching Architecture

All external data is downloaded to local Parquet files before the backtest runs. During the backtest, the engine reads from disk only — no network calls. This is critical for three reasons: (1) network failures can't interrupt a 24-hour run, (2) the same data is used deterministically on every run, (3) speed — reading from Parquet is ~50× faster than API calls.

Data currently downloading:
- **OHLCV prices:** 509 tickers, January 2020 – March 2026 (✅ complete)
- **Congressional trades:** 509 tickers, all history (✅ complete)
- **Insider trades (Form 4):** 509 tickers, all history (✅ complete)
- **Institutional 13F:** Quiver API outage — retry when recovered
- **Government contracts:** Quiver API outage — retry when recovered
- **Lobbying filings:** Quiver API outage — retry when recovered
- **Wikipedia page views:** Quiver API outage — retry when recovered
- **WallStreetBets mentions:** Quiver API outage — retry when recovered
- **Alpha Vantage news sentiment:** 4 GitHub Actions batches running overnight
- **FRED macro data:** ✅ Complete to March 2026
- **AAII sentiment survey:** ✅ 325 weekly readings
- **CNN Fear & Greed:** ✅ 1,630 daily readings

---

### Stage 3: Paper Trading (After Phase 1D)

**Duration:** 3-6 months minimum  
**Capital at risk:** Zero — Alpaca paper trading account (free)  
**Execution:** Fully automated — no email approval needed  

Once strategies are validated through Phase 1D, the system runs daily:
1. At 6am UTC, a GitHub Actions workflow screens all 509 instruments
2. Candidates passing the AI agent pipeline at VERY HIGH or EXCEPTIONAL tier are automatically paper-traded via the Alpaca API
3. Exit monitoring runs daily — trailing stops are managed automatically
4. Results are written to the website for review

This is a full dress rehearsal for live trading. The system must run reliably for 3+ months with live win rates within 10pp of backtest win rates before advancing.

**Why fully automated (no approval)?** Stage 3 is testing the automation, not the strategy. If approval is required, we're testing human decision-making, not the system. Stage 4 is where human approval is introduced deliberately as a risk control.

**Success criteria to advance to Stage 4:**
- Minimum 50 paper trades completed
- Live win rate ≥ 50% (absolute floor)
- Live profit factor ≥ 1.0
- Live win rate within 10pp of backtest
- Zero unplanned system outages in final 30 days
- All tiers tracked internally (not just published picks)

**Monthly cost:** ~$150-175 CAD (Quiver + Unusual Whales + Anthropic API)

---

### Stage 4: Live Trading — Small Scale

**Starting capital:** $10,000 CAD (minimum viable for position sizing math to work)  
**Broker:** Interactive Brokers Canada (lowest commissions for active Canadian traders)  
**Approval:** Email approval required for every single trade  
**Commission:** $0.005/share USD, $1 minimum  

The email approval workflow: the system generates a trade signal → sends an email with full context (ticker, tier, entry price, position size, stop level, agent reasoning) → owner replies APPROVE or REJECT within 30 minutes → if approved, the order is placed via IBKR API.

**Why email approval in Stage 4 when Stage 3 was fully automated?** Because real money changes the equation. The approval step forces conscious acknowledgment of every trade. It also gives 30 minutes to check news or other context the system may not have. Stage 4 is about building confidence that the live system matches the backtest — not about speed.

**Risk management rules for Stage 4:**
- Maximum 10 open positions simultaneously
- Maximum 1 position per ticker (multiple strategies on same ticker → one combined position)
- Portfolio drawdown > 10% → reduce all new position sizes by 25%
- Portfolio drawdown > 20% → reduce all new position sizes by 50%
- Portfolio drawdown > 30% → suspend new entries, manage existing exits only
- Reduce to 50% position size after 3 consecutive losses
- All 5 circuit breakers active at all times
- Daily loss limit: calibrated from Stage 3 paper trading data

**Currency note:** All trades are in USD. Portfolio is measured in CAD. USD/CAD fluctuations affect actual CAD returns. This is a known and accepted exposure at Stage 4 scale.

**Tax note:** Swing trading of US equities by a Canadian investor should qualify for capital gains treatment (50% inclusion rate) rather than business income (100%). Confirm with a tax professional before Stage 4.

**Success criteria to advance to Stage 5:**
- 6+ months live trading, minimum 50 real trades
- Live win rate within 10pp of paper trading win rate
- No single trade loss exceeding its defined position size
- System stable — zero unplanned outages in final 60 days
- Profit factor > 1.0 on real trades (breaking even is acceptable — validating the system)

**Monthly cost:** ~$190 CAD

---

### Stage 5: Full Automation

**Gate condition:** Stage 4 profitable for 6+ months, all systems proven reliable  
**Change from Stage 4:** Remove email approval, increase position sizes, add Ortex for short interest  
**Monthly cost:** ~$300-360 CAD  

At Stage 5, the system executes fully automatically within defined risk parameters. Position sizes are larger. Alert emails are sent for unusual events (large position, circuit breaker trigger) but no approval is required for normal trades.

---

## The Website

### What It Shows at Each Stage

**Stage 1 (now):** Daily top gainers for US and Canadian markets. Simple, informational.

**Stage 2:** Analysis dashboards for the development team only. Not public.

**Stage 3:** Live screening candidates with confidence tiers, agent analysis, and paper trade tracking. The public website shows VERY HIGH and EXCEPTIONAL tier candidates with full reasoning. ALL tiers are tracked internally for performance analysis — the public view is a subset.

**Stage 4-5:** Full trade management — active positions, trailing stop levels, closed trade history, performance vs benchmark.

### Stage 3 Website Design

The website is a static HTML/JavaScript site, updated daily by GitHub Actions. No server required — everything is written to JSON files that the website reads.

Each candidate card shows: ticker and company name, sector, current price, confidence tier, which strategies fired (in plain English), suggested entry price and position size, stop level, days to next earnings (flagged if < 14 days), current CNN Fear & Greed score, the bull agent's case for the trade, the bear agent's case against it, and the Decision Agent's final recommendation.

The paper trading tracker shows: open paper positions with current unrealised P&L, trailing stop levels, the date and price each position was entered, and closed trades with their outcome.

---

## How the APIs Work Together

Every data source serves a specific purpose in the decision chain. Here is how they flow together:

**yfinance** provides the raw price and volume history (OHLCV) for all 509 instruments, going back to 2020 for signal warmup. This is the foundation of every technical signal. Also provides VIX data for regime classification.

**FRED** provides macro-economic time series: the yield curve (T10Y2Y), Federal Funds rate, unemployment rate, CPI inflation, 10-year Treasury yield, and corporate credit spreads. These feed the Risk Agent to assess whether the macro environment is favourable for new positions.

**Quiver Quantitative** (Trader plan, $75/month) provides: congressional trade disclosures, insider Form 4 filings, institutional 13F holdings, government contracts, lobbying filings, Wikipedia page views, and WallStreetBets mentions. This is the smart money layer that separates our system from purely technical approaches.

**Alpha Vantage** (existing free key) provides AI-powered news sentiment scores for all 509 tickers, with full historical coverage back to 2022. This feeds the Sentiment Agent with context about recent news direction.

**AAII Investor Sentiment Survey** is loaded from a committed CSV file. It provides weekly readings of how bullish or bearish individual investors are — a contrarian indicator (extreme bearishness is often a buy signal).

**CNN Fear & Greed Index** is loaded from a committed CSV file. A composite daily score from 0 (extreme fear) to 100 (extreme greed). Used as a contrarian indicator and as context for the Sentiment Agent.

**Anthropic Claude** (Haiku for Phase 1B, Sonnet for 1C/1D and live) runs the six-agent pipeline for each trade candidate. The six agents are not separate models — they are separate API calls to the same model with different prompts and context.

**Unusual Whales** (Phase 1C onwards, ~$50/month) provides options flow data — large unusual options activity often precedes significant price moves. Added in Phase 1C to validate its contribution to confidence tiers before using it in live trading.

**Ortex** (Stage 3 onwards, ~$40/month) provides short interest data — stocks with very high short interest and rising borrowing costs are candidates for short squeezes. Used by the Risk Agent.

**IBKR Canada** (Stage 4 onwards) executes real trades. $0.005/share, $1 minimum commission. The only Canadian-accessible broker with a proper API for automated trading at reasonable commissions.

---

## Risk Management Philosophy

### The Core Approach

We accept that drawdowns will happen. Our job is not to eliminate them but to ensure they are recoverable and that the long-term edge compensates for them. A strategy with a 65% win rate will still have losing streaks of 5-7 trades. This is mathematically inevitable, not a system failure.

### What We Control

**Entry discipline:** Only enter when multiple independent signals agree. The minimum is 1 strategy, but EXCEPTIONAL tier requires 3+ strategies plus congressional and insider buying. Higher tier = higher conviction = larger position.

**Exit discipline:** Every trade has a trailing stop from day one. No exceptions. The stop moves in our favour as the price rises but never moves against us. The only question is when the stop gets hit, not whether we'll exit.

**Position sizing:** Based on confidence tier. An EXCEPTIONAL trade gets 5% of capital. A MEDIUM-HIGH trade gets 1.5%. This automatically sizes our bets to our conviction level.

**Drawdown scaling:** At 10% portfolio drawdown, reduce new position sizes by 25%. At 20%, reduce by 50%. At 30%, stop opening new positions entirely. This prevents a bad streak from becoming catastrophic.

**Kelly Criterion sanity check:** After Phase 1B, we calculate the optimal position size for each strategy using the Kelly Criterion. This validates that our tier-based sizes are not over- or under-leveraged relative to the strategy's actual edge.

### What We Accept

- VIX > 40 environments (market crises) are not stopped — position sizes are reduced but longs are still taken. These are often the best entry points.
- Currency risk: US equities, Canadian account. USD/CAD moves affect returns. Accepted at current scale.
- Survivorship bias: the S&P 500 constituents we're testing are survivors by definition. We apply a hold-adjusted haircut (0.5-3% annually) to account for this.
- Stop simulation optimism: our daily bar data means trailing stops are checked against the closing price. Real stops trigger intraday. We use the intraday low for stop trigger checks to partially correct this.

---

## Data Integrity Principles

**Point-in-time enforcement:** The backtest never uses data that wasn't available on the signal date. Congressional trades use the disclosure date (not transaction date) plus a 45-day lag. 13F data uses a 45-day lag after quarter-end. Insider trades use a 2-business-day lag. FRED data uses the actual release date. This is non-negotiable — using future data in backtests is the most common source of falsely optimistic results.

**Congressional age weighting:** Trades disclosed within 30 days receive full weight. 30-60 days receive 50% weight. Over 60 days are excluded. A 60-day-old congressional buy signal has far less predictive value than a week-old one.

**Pre-fetch architecture:** All data is downloaded to Parquet files before the backtest runs. No live API calls during backtest execution. This ensures reproducibility and prevents network failures from affecting results.

**Agent determinism:** All agent API calls use temperature=0 (fully deterministic). The same inputs always produce the same outputs. This makes Phase 1B results reproducible if the run needs to be restarted.

**Agent cache versioning:** Agent results are cached with a version key (currently v2.0). When agent prompts change materially, the version is incremented and all old cached results are automatically ignored. This prevents stale analyses from polluting new runs.

---

## Technical Infrastructure

**Development environment:** GitHub Codespaces for computation. Personal laptop with VS Code and Claude Code for browsing and interaction. GitHub Actions for automated data downloads.

**Storage:** All data in Parquet files committed to the GitHub repository. No separate database needed for Stage 2.

**Testing:** Three layers of automated tests run before every Phase 1B run:
- Integration tests: verify data flows correctly between modules
- Unit tests: verify individual functions produce correct results for known inputs
- End-to-end smoke test: verify the full pipeline produces trades with correct fields

**Pre-run validation:** `python scripts/validate_phase1b_data.py` checks all data completeness before any backtest starts.

**Stage 3 infrastructure:** Hetzner VPS ($6 USD/month) for always-on process runner. PostgreSQL for trade persistence. GitHub Actions for daily screening job.

---

## Strategy Decay and Long-Term Maintenance

A strategy validated on 2022-2026 data may stop working in 2028. Market microstructure changes, institutional behaviour evolves, retail participation shifts.

**How we handle this:**

After Phase 1D, validated strategies are deployed in Stage 3 paper trading. Monthly performance reviews compare live results against backtest expectations. If a strategy's live win rate drops more than 10 percentage points below its backtest win rate for three consecutive months, it is retired and replaced.

Annual re-backtesting runs Phase 1B through 1D again on extended data including new years. New strategies can be added. Failing strategies are removed.

**Re-validation triggers:**
- VIX sustained above 30 for 30+ days (regime shift)
- Any strategy underperforms backtest by > 15pp for 2+ months
- Major market structure change (new regulation, circuit breaker rule, new instrument class)

The Risk Agent explicitly flags when the current macro regime differs significantly from the validation period — surfacing potential strategy decay before it shows in P&L.

---

## Outstanding Items and Future Roadmap

### Before Phase 1B Full Run (Checklist)
1. Sync laptop: `git pull --rebase origin main`
2. Disable laptop sleep (Settings → Power → Sleep → Never while plugged in)
3. Set 3 API keys in each terminal (ANTHROPIC_API_KEY, QUIVER_API_KEY, FRED_API_KEY)
4. Run quarterly S&P 500 refresh: `python scripts/refresh_sp500_universe.py --write` (CHECKLIST item 19)
5. Run: `python scripts/prepopulate_cache_index.py`
6. Run 1-ticker-per-batch test (5 terminals, Jan 2022 only) — see `scripts/generate_batch_splits.py`
7. Owner reviews test outputs and approves before scaling
8. Scale to full 509 tickers across 5 parallel batches (~$116 CAD, ~15 hours)

**News decision:** Proceeding Phase 1B WITHOUT news sentiment. Alpha Vantage free tier returns `not_available` for all tickers — the A/B comparison would be identical. News will be revisited in Phase 1C with Unusual Whales options flow data, which is far richer.

### Phase 1C Additions
Unusual Whales options flow and Ortex short interest data are added in Phase 1C. Additionally, two correlation-factor additions are planned (see Market-Level and Correlation-Factor Strategies section for full detail):
- Relative strength precondition added to all 6 existing breakout strategies (requires stock to outperform its sector ETF over prior 20 days)
- One new strategy (strategy 61): sector ETF crosses above 50-day EMA + stock shows momentum signal
- Intermarket signals (TLT, GLD, DXY trends) added as Risk Agent context with tier adjustment logic

Total strategies in Phase 1C: approximately 62. All additions are backtested against the same 10 passing criteria as Phase 1B strategies.

### Stage 3 Design (When Phase 1D Completes)
- IBKR Canada paper trading account setup (Alpaca for US users; IBKR for Canadian)
- Daily screening cron job implementation
- Position persistence mechanism (PostgreSQL)
- Website with live paper trade tracking
- Hybrid regime classifier: daily vol for speed (crisis detection) + weekly BMSB confirmation for structural shifts
- Live market breadth dashboard (PCT_ABOVE_50EMA, PCT_ABOVE_200EMA, new high/low ratio)
- IWM/SPY ratio filter as live small-cap conviction modifier
- Approximate factor bucket classification (value/growth/quality/momentum) using current fundamentals
- Rate-cycle rotation strategy using TLT vs SPY as entry trigger (intermarket signal as live strategy)
- Post-earnings drift as priority paper trading candidate (validate before committing to Phase 1D results)

See Market-Level and Correlation-Factor Strategies section for full detail on each item.

### Stage 4 Design (When Stage 3 Proves Profitable)
- Email approval workflow implementation
- IBKR live account setup
- Position reconciliation mechanism (cancel if price moved > 1% since signal)
- Tax reporting integration

### Post-Phase 1B Analysis Items
- Kelly Criterion validation of tier position sizes
- Senate vs House distinction in congressional signal weighting
- Agent score calibration check (distribution should be roughly normal, centred 50-60)
- Per-agent predictive accuracy (which agents correlate most with actual trade outcomes)
- Strategy return correlation matrix (identify redundant strategies)
- VIX threshold empirical validation (let data determine optimal regime thresholds)

---

## Market-Level and Correlation-Factor Strategies — A Critical Gap

### Why this gap exists and why it matters

Every one of the 60 strategies in Phase 1B evaluates a single stock in isolation. The only market-level input currently in any strategy is the sector ETF return for the day passed as context to the Technical Agent. This means the screener can simultaneously be buying NVDA on a technical signal while the semiconductor sector is breaking down, IWM (small caps) is signalling risk-off, TLT is surging (flight to safety), and market breadth is deteriorating. The agent partially compensates through narrative context, but no entry strategy is structured to use these correlation factors as triggers or blockers.

This is a known architectural limitation. It does not invalidate Phase 1B — the agent pipeline partially compensates and the the per-regime verdict matrix identifies which strategies work in which environments. But it represents a systematic blind spot that must be addressed in later phases to build a truly robust system.

The eight missing strategy categories are documented below with a specific implementation plan for each stage. No changes are made to Phase 1B. Categories are sequenced by implementation complexity and data availability.

---

### Category 1 — Sector Rotation (Phase 1C)

**The concept:** Capital rotates between sectors based on the economic cycle. Early recovery favours Financials and Consumer Discretionary. Mid-cycle favours Industrials and Materials. Late cycle favours Energy and Staples. Recession favours Healthcare and Utilities. Identifying which sector is receiving institutional inflows — and buying the leading stocks within that sector — is a well-documented edge.

**What's missing today:** All 60 strategies apply identically regardless of whether a stock's sector ETF is in an uptrend or downtrend. A stock can trigger `rsi_volume_200ema` while XLF is in a 3-month downtrend and the system won't care.

**Proposed implementation — Phase 1C:**
Two additions. First, a relative strength precondition added to all 6 existing breakout strategies: require that the stock has outperformed its sector ETF over the prior 20 trading days (stock return minus sector ETF return > 0). This is not a new strategy — it is a filter on existing ones. Implementation is approximately 15 lines of code and requires no new data sources. Second, one new strategy (strategy 61): sector ETF crosses above its 50-day EMA AND has outperformed SPY by >2% over 20 days AND individual stock in that sector shows any momentum signal → enter with MEDIUM-HIGH minimum tier. This is sector rotation implemented directly as a strategy.

**Data required:** Already cached. All sector ETFs (XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLU, XLB, XLRE) are in the OHLCV cache.

**Statistical validity concern:** Each sector ETF crossing its 50-day EMA is a rare event — roughly 8-15 times per year per sector. Over 4 years across 11 sectors, this generates perhaps 400-600 sector-rotation entry opportunities, which when filtered to individual stock signals may yield 150-250 trades. Borderline for the 500-trade minimum. Sector rotation strategy may need Phase 1D's 5-year window to reach statistical validity.

---

### Category 2 — Relative Strength vs Sector and Market (Phase 1C)

**The concept:** Mansfield Relative Strength measures how a stock performs relative to its sector ETF over 52 weeks. A stock with RS > 1.0 is outperforming. The highest-conviction setups occur when a stock with RS > 1.0 is in a sector with RS > 1.0 vs SPY. A breakout on a sector leader in a leading sector is categorically different in quality from the same breakout on a laggard.

**What's missing today:** `52w_high_breakout` fires on any stock hitting a 52-week high regardless of whether that stock is leading or lagging its sector. This produces many low-quality signals.

**Proposed implementation — Phase 1C:**
Add a Mansfield RS score (stock 52-week return / sector ETF 52-week return) as a computed signal available to all strategies. Require RS > 1.0 as a precondition for all breakout strategies. Additionally add RS as a context input to the Technical Agent — the agent already receives sector ETF return for the day but has no visibility into the stock's relative performance over prior months.

**Data required:** Already cached. OHLCV for all stocks and sector ETFs.

**Expected impact:** Reduces false signals on breakout strategies by an estimated 20-30%. The relative strength filter is one of the most consistently validated edges in the academic literature on technical analysis.

---

### Category 3 — Intermarket Signals: Bonds, Gold, Dollar (Phase 1C, enhanced in Stage 3)

**The concept:** Asset classes are interconnected. When TLT (20-year bonds) rises sharply, falling rate expectations historically benefit growth stocks and hurt banks. When GLD outperforms SPY over 20 days, it signals institutional risk-off positioning — cyclical stocks underperform. When DXY falls >2% over 20 days, multinationals and commodity exporters benefit. These cross-asset relationships are systematic and have multi-decade academic backing (John Murphy's "Intermarket Analysis" is the canonical reference).

**What's missing today:** DXY trend is computed in `macro.py` and passed to the Risk Agent as a text string ("rising" / "falling" / "flat"). TLT and GLD are in the OHLCV cache as part of the ETF universe (TLT, GLD are included). But no strategy uses these as entry triggers or hard filters.

**Proposed implementation — Phase 1C:**
Three intermarket signals added as context to the Risk Agent with specific threshold logic:

- **Bond signal:** TLT 20-day return vs SPY 20-day return. If TLT is outperforming SPY by >3% (risk-off bond rally), downgrade all new long entries in cyclical sectors (XLY, XLF, XLI, XLE) by one tier. If TLT is underperforming by >3% (risk-on bond selloff), upgrade momentum long entries in growth sectors (XLK, XLV) by one tier.

- **Gold signal:** GLD 20-day return vs SPY. If GLD outperforms by >5%, apply a 0.5x size multiplier to all new long entries (systemic risk-off signal). If GLD underperforms (risk appetite high), no adjustment.

- **Dollar signal:** Already computed. DXY rising >2% in 20 days → reduce conviction on multinationals and commodity names. DXY falling >2% → increase conviction on same names. Requires mapping each ticker to its USD sensitivity bucket (multinationals, domestic, commodity-linked) — this can be estimated from sector membership.

**Data required:** TLT and GLD already in OHLCV cache. USD sensitivity mapping requires a one-time lookup table.

**Phase 1C scope:** Intermarket signals as Risk Agent context upgrades/downgrades only — not standalone strategies. The agent already handles the final decision.

**Stage 3 enhancement:** Dedicated intermarket strategy: TLT crosses below 50-day EMA (rates rising, bond bears confirmed) AND financial sector stock shows any momentum signal → VERY HIGH minimum tier for the Financials entry. This is the rate-cycle rotation trade implemented explicitly. Requires live daily data from the OHLCV feed — already available.

---

### Category 4 — Market Breadth (Phase 1D, live in Stage 3)

**The concept:** Breadth measures participation. When SPY rises but only 30% of S&P 500 stocks are above their 50-day EMAs, the rally is being driven by a handful of mega-caps (typically the "Magnificent 7" in 2023-2024) and is fragile. When >70% of stocks are above their 50-day EMAs, the rally is broad and institutions are buying across the board — this is the highest-conviction environment for swing long entries. The Advance-Decline Line, McClellan Oscillator, and "percentage of S&P 500 above 200 EMA" are the three most widely watched breadth indicators.

**What's missing today:** The system has no concept of breadth. A narrow rally driven by 5 mega-caps and a broad rally with 400 participating stocks look identical to the screener and agents.

**Why not Phase 1C:** Computing breadth requires daily calculation across all 500+ stocks in the universe — a non-trivial infrastructure addition. Phase 1C is focused on strategy quality improvements, not new infrastructure.

**Proposed implementation — Phase 1D:**
Compute three breadth metrics daily across the full 509-ticker universe as a post-processing step during the backtest:
- **PCT_ABOVE_50EMA:** percentage of S&P 500 stocks above their 50-day EMA (bullish when >60%, bearish when <40%)
- **PCT_ABOVE_200EMA:** percentage above 200-day EMA (structural bull/bear indicator)
- **NEW_HIGH_NEW_LOW_RATIO:** daily new 52-week highs divided by (highs + lows). Readings above 70% are strongly bullish.

These metrics are stored as daily time series and used as filters: new long entries are blocked when PCT_ABOVE_50EMA < 35% (narrow deteriorating market). New short entries are blocked when PCT_ABOVE_50EMA > 65% (healthy bull market — shorts have poor odds). These are portfolio-level filters applied before any individual stock evaluation.

**Stage 3 implementation:** The same breadth metrics are computed daily in the live screening job using the prior day's closes. Cost: zero (computed from already-available OHLCV data). A breadth dashboard is added to the website showing the daily readings and their historical percentile.

**Stage 4/5 enhancement:** Breadth divergence alert — when SPY makes a new high but PCT_ABOVE_200EMA is declining, this is a classic distribution warning. Email alert is sent automatically. No position changes are made automatically, but the email draws attention to the regime risk.

---

### Category 5 — Large-Cap vs Small-Cap Rotation (Phase 1D)

**The concept:** The ratio of IWM (Russell 2000) to SPY measures risk appetite at the institutional level. When small caps outperform, institutional money is reaching for higher-beta names — a risk-on signal. When large caps outperform, institutions are defensively hiding in mega-caps — a risk-off signal. This ratio is a powerful conditioning variable: small-cap individual stock picks dramatically underperform when IWM is losing ground to SPY regardless of individual technical signals.

**What's missing today:** IWM is in the OHLCV cache and universe but its relative performance vs SPY is never computed or used as a filter.

**Proposed implementation — Phase 1D:**
Compute a daily IWM/SPY ratio trend (20-day rolling). When IWM underperforms SPY by >5% over 20 days (risk-off rotation), apply a 0.75x position size multiplier to all small and mid-cap stock entries (market cap < $10B). When IWM outperforms SPY by >5% (risk-on), apply a 1.1x multiplier to the same names (capped so total size stays within tier limits).

Additionally, a new strategy (strategy 62): IWM crosses above its 50-day EMA AND has outperformed SPY by >3% over 20 days AND individual small/mid-cap stock shows any momentum or breakout signal → enter with a one-tier upgrade from the preliminary tier. This is the small-cap rotation trade.

**Data required:** Already cached. IWM, SPY OHLCV available.

---

### Category 6 — Post-Earnings Drift (Phase 1D)

**The concept:** Post-earnings announcement drift (PEAD) is one of the most replicated anomalies in academic finance (documented since Ball & Brown 1968). When a company reports earnings that significantly beat expectations, the stock tends to continue drifting higher for 3-20 trading days — not all in one session. This occurs because institutional investors take multiple sessions to fully build positions following a surprise. The same drift occurs in the negative direction after a miss.

**What's missing today:** The system treats earnings proximity purely as a risk factor (a circuit breaker and a Risk Agent warning). It never explicitly enters a trade to capture post-earnings drift.

**Proposed implementation — Phase 1D:**
New strategy (strategy 63): Stock reports earnings with >5% gap-up on earnings day AND closes in the top 20% of its daily range (not a reversal day) AND volume is >2× the 20-day average → enter the next morning at open, target the post-earnings drift for 5-15 days, trail with 1.5× ATR (wider than standard — post-earnings volatility is elevated).

This requires knowing historical earnings dates with point-in-time accuracy. Currently earnings dates come from yfinance and are not always historically accurate. A dedicated earnings calendar source may be required for this strategy. Flag as needing data validation before implementation.

**Stage 3 enhancement:** Post-earnings drift is one of the few strategies that works better in live trading than backtesting (because real fills at next-day open capture the actual drift, whereas backtests use close-to-close). Priority candidate for Stage 3 paper trading validation.

---

### Category 7 — Sector-Level Mean Reversion (Phase 1D)

**The concept:** When an entire sector is deeply oversold (XLE down 20% in 60 days, XLF down 15%), the best stocks in that sector become the highest-conviction recovery plays. Sector-level capitulation followed by the first signs of sector stabilisation (sector ETF closes above prior day high for 3 consecutive days after a sustained decline) is a distinct entry trigger. This is different from buying any oversold individual stock — it is specifically timing the sector recovery.

**What's missing today:** Mean reversion strategies (`rsi_oversold`, `bollinger_lower`, etc.) fire on any oversold stock regardless of sector context. A stock can be oversold while its sector continues falling — the worst type of falling knife.

**Proposed implementation — Phase 1D:**
Two additions. First, a sector oversold context added to existing mean reversion strategies: if the stock's sector ETF is in a confirmed downtrend (below 50-day EMA and declining), require a higher tier minimum (VERY HIGH instead of HIGH) for mean reversion entries. This filters out the "falling knife" problem. Second, new strategy (strategy 64): sector ETF has declined >15% from its 60-day high AND closes above prior session high for 3 consecutive days (stabilisation signal) AND individual stock in sector is above its own 50-day EMA (a relative strength leader in the beaten sector) → enter with HIGH minimum tier. This is sector capitulation recovery.

**Data required:** Already cached. Sector ETF OHLCV.

---

### Category 8 — Factor Rotation: Value, Growth, Momentum, Quality (Stage 3)

**The concept:** Factor exposures rotate in and out of favour based on macro conditions. Rising rates environments favour value (low P/E, high dividends) over growth (high P/E, no dividends). Falling rates favour growth. High inflation favours commodities and real assets. Post-crisis recovery favours high-beta momentum names. Quality (low debt, stable earnings, high ROE) outperforms in uncertain environments. In 2022, value and dividends dominated. In 2023-2024, momentum and growth dominated. In 2025 tariff uncertainty, quality dominated.

**What's missing today:** The system applies identical logic to a pure growth stock trading at 40× sales and a deep value stock trading at 8× earnings. Factor context is absent from both the screener and agent prompts.

**Why this is a Stage 3 addition, not Phase 1C/1D:** Factor data (P/E ratios, debt/equity, ROE, dividend yield) requires a separate data source from what is currently cached. Fundamental data for all 509 tickers is available through yfinance's `info` endpoint, but point-in-time historical fundamental data is not available through free sources. Using today's fundamentals for trades made in 2022 introduces look-ahead bias — a stock trading at 40× sales today may have been trading at 80× sales in 2022. Valid historical factor data requires Compustat or a similar institutional source, which is cost-prohibitive until Stage 5.

**Stage 3 approach (approximate, no look-ahead):** Use current factor buckets as a static classification. At Stage 3, the backtest period is only 3-6 months prior to live trading — the look-ahead bias from using current fundamentals is minimal for a 6-month window. Classify each stock as value/growth/quality/momentum based on current fundamentals and apply factor-aware position sizing: reduce size on growth stocks when the macro regime suggests rates are rising, increase size on quality stocks when CNN Fear & Greed is below 30 (uncertainty regime).

**Stage 5 approach (full implementation):** Subscribe to a historical fundamental data source. Add factor rotation as a conditioning variable on all confidence tier assignments. This is the most powerful long-term enhancement but requires the most infrastructure.

---

### Category 9 — Regime Change as a Strategy (Phase 1D)

**The concept:** When `classify_regime()` transitions from bear → neutral or neutral → bull after 10+ consecutive days in the prior regime, the stocks that held up best during the downturn (relative strength leaders) tend to be the first and strongest movers in the recovery. This is a distinct edge: the entry trigger is the regime transition itself, not an individual stock's technical signal. It is the market-level analogue of buying a stock's first higher high after a downtrend.

**Why this matters:** Every one of the current 60 strategies can fire during any regime. None of them explicitly time regime transitions as the primary entry trigger. This means the system misses the highest-conviction window — the first few days after a regime improvement — when the risk/reward is most favourable.

**What makes this valid:** From the chart, the 2022 bear → neutral transition (October 2022) produced one of the strongest rallies in recent history. The late 2023 neutral → bull transition preceded the 2024 bull run. These are not random — they reflect genuine shifts in institutional positioning.

**Why Phase 1D, not Phase 1C:** With 8-10 regime transitions over 4 years (as seen in the regime chart), this strategy generates approximately 40-80 candidate entries across the full universe. This is well below the 500-trade minimum for Phase 1B/1C validation. The 5-year Phase 1D window (adding 2020-2021 with COVID recovery as a major regime transition) provides 2-3 additional transitions and pushes the trade count closer to statistical validity.

**Proposed implementation — Phase 1D:**
New strategy (strategy 65): `classify_regime()` returns a regime that differs from the prior 10 consecutive days' regime AND the new regime is less restrictive (bear → neutral, neutral → bull, crisis → bear) AND individual stock has 20-day relative strength > 1.0 vs its sector ETF → enter with HIGH minimum tier, targeting the regime recovery drift.

**Confirmation buffer requirement:** Same 3-day confirmation buffer proposed for live trading applies here — regime change is only flagged as confirmed after the new regime persists for 3 consecutive trading days. This prevents whipsawing during choppy regime transitions.

---

### Hybrid Regime Classifier: Daily + Weekly Confirmation (Stage 3)

**The problem with the current classifier:** Our 20-day realised vol + SPY vs 200 EMA approach detects regime changes faster than Bull Market Support Band (BMSB uses 20-week SMA + 21-week EMA on weekly closes). But faster also means noisier — a single volatile week can temporarily flip our daily vol calculation into bear territory during an otherwise healthy bull market, producing a false regime change that adjusts position sizing unnecessarily.

**The hybrid approach:** Use our daily classifier for speed — specifically for crisis detection (where waiting 5 months for BMSB to confirm is unacceptable) and for the alert layer. Use BMSB for sustained regime confirmation before changing the structural bias. The logic is:

**For crisis (VIX proxy > 35%):** Our daily classifier triggers immediately. No weekly confirmation required. Crisis requires speed — the March 2020 crash moved from normal to crisis in 5 trading days. Waiting for a weekly close confirmation would have meant entering crisis regime after the worst moves were already done.

**For bear regime (VIX proxy > 25%, SPY below 200 EMA):** Our daily classifier raises an alert. BMSB confirmation (SPY closes below both 20-week SMA and 21-week EMA on a weekly close) is required before structural bias shifts. Until BMSB confirms, the system applies a 0.75x size multiplier to new longs as a precaution but does not change the regime label.

**For bull regime (VIX proxy < 15%, SPY above 200 EMA):** Our daily classifier raises a recovery alert. Require 3 consecutive daily bull readings before calling the regime bull. BMSB (SPY above both 20-week SMA and 21-week EMA) provides additional confirmation that can upgrade the confidence on regime-change strategy entries.

**What this solves:** False positives during healthy bull markets where one volatile week temporarily pushes daily vol above 15%. False negatives during crashes where waiting for weekly confirmation is too slow. The hybrid gets the best of both: daily speed for crisis, weekly confirmation for structural shifts.

**Implementation stage:** Stage 3 — live trading requires a real-time regime classifier, and this is the appropriate time to build the two-layer system. Phase 1B/1C/1D use the existing daily classifier. The hybrid is built and tested during Stage 3 paper trading against the daily classifier to measure false positive reduction before committing to it in Stage 4.

---

### Implementation Roadmap Summary

| Category | Phase 1B | Phase 1C | Phase 1D | Stage 3 | Stage 4/5 |
|---|---|---|---|---|---|
| 1 — Sector rotation | ❌ No change | ✅ RS filter on breakouts + 1 new strategy | ✅ Validate with 5yr data | ✅ Live sector momentum signal | ✅ Enhanced with institutional flow |
| 2 — Relative strength vs sector | ❌ No change | ✅ RS precondition on all breakouts | ✅ Validate | ✅ RS in live screener | ✅ Full Mansfield RS scoring |
| 3 — Intermarket (bonds/gold/dollar) | ❌ No change | ✅ As Risk Agent context upgrades | ✅ Validate | ✅ As dedicated strategy (rate-cycle rotation) | ✅ Full cross-asset correlation scoring |
| 4 — Market breadth | ❌ No change | ❌ No change | ✅ As portfolio-level entry filter | ✅ Daily breadth dashboard + live filter | ✅ Breadth divergence alert system |
| 5 — Large/small cap rotation | ❌ No change | ❌ No change | ✅ IWM/SPY ratio as size modifier + 1 new strategy | ✅ Live IWM/SPY filter | ✅ Full factor rotation |
| 6 — Post-earnings drift | ❌ No change | ❌ No change | ✅ 1 new strategy (data validation required) | ✅ Priority paper trading candidate | ✅ With accurate earnings calendar |
| 7 — Sector mean reversion | ❌ No change | ❌ No change | ✅ Sector oversold filter + 1 new strategy | ✅ Live sector ETF context | ✅ Enhanced |
| 8 — Factor rotation | ❌ No change | ❌ No change | ❌ Look-ahead bias risk | ✅ Approximate static factor buckets | ✅ Historical fundamental data source |
| 9 — Regime change strategy | ❌ No change | ❌ No change | ✅ 1 new strategy (needs 5yr for trade count) | ✅ With live regime detection | ✅ Full implementation |
| Hybrid regime classifier | ❌ No change | ❌ No change | ❌ No change | ✅ Build and validate vs daily classifier | ✅ Deploy if Stage 3 validates it |

**Phase 1C adds:** 2 new strategies (sector rotation, RS filter on breakouts), intermarket signals as agent context. Total strategies: ~62.

**Phase 1D adds:** 4 new strategies (IWM rotation, post-earnings drift, sector mean reversion, regime change). Breadth and IWM/SPY as portfolio filters. Total strategies: ~66.

**Stage 3 adds:** Hybrid regime classifier, live breadth dashboard, factor bucket classification, real-time intermarket signals. No new strategy count — these are live infrastructure.

**Stage 4/5 adds:** Full factor rotation with historical fundamental data. Enhanced cross-asset correlation scoring. Breadth divergence alerts.

### Known limitations of this gap (updated)

The original Known Limitations section listed "Sector contagion effects not explicitly modelled." This section replaces and expands that item. The complete list of correlation-factor limitations in Phase 1B is:

- No sector rotation signal — strategy fires regardless of sector ETF trend direction
- No relative strength filter — a sector laggard and a sector leader trigger identically
- No intermarket conditioning — bond rally, gold surge, DXY spike do not block individual stock entries
- No market breadth filter — narrow 5-stock rally and broad 400-stock rally look identical
- No large/small cap rotation signal — IWM underperformance does not reduce small-cap conviction
- No post-earnings drift strategy — earnings proximity is only a risk flag, never an entry trigger
- No sector-level mean reversion — sector capitulation and recovery not used as entry filter
- No factor awareness — value, growth, quality, momentum exposures ignored
- No regime change strategy — regime transitions not used as primary entry triggers
- Regime classifier is daily-only — no weekly confirmation layer (proposed hybrid not yet built)

These limitations are accepted for Phase 1B and will be addressed in later phases per the roadmap above.

---

---

## Universe Architecture — Three Tiers

### Why a single static list is insufficient

A static S&P 500 CSV committed once and never updated is a time bomb. The index changes 10-20 times per year. Major spinoffs (SNDK, GEV) go undiscovered for months. High-momentum non-S&P stocks (VST, SMCI) are never screened. The SanDisk case study is the definitive example: spun off February 2025, S&P 500 addition November 2025 — 9 months invisible to a static-universe system. The stock returned 1,200%+ in that period.

The fix is architecture: three tiers with defined refresh frequencies, refresh scripts, and CHECKLIST items attached to each.

### Tier 1 — S&P 500 Core

**File:** `backtest/data/sp500_tickers.csv` (~484-505 tickers)
**Refresh frequency:** Quarterly (January, April, July, October) — CHECKLIST item 19
**Refresh method:** `python scripts/refresh_sp500_universe.py --write` on laptop
**Source:** slickcharts.com — free, stable, updated same day as S&P announcements. NEVER Wikipedia (blocked in Codespaces, not point-in-time, fragile — L88).
**Used by:** Phase 1B/1C/1D backtesting and Stage 3+ live screening
**Covers:** All S&P 500 constituents after passing a liquidity filter (price >$5, avg volume >300K)

### Tier 2 — Extended Universe (spinoffs, large non-S&P)

**File:** `backtest/data/extended_universe.csv` (~50-100 tickers)
**Refresh frequency:** Monthly for live trading (Stage 3+). Run immediately on any major spinoff above $5B market cap — do not wait for the monthly cycle.
**Refresh method:** `python scripts/refresh_extended_universe.py --write` on laptop
**Used by:** Stage 3+ live screening only. NOT used in Phase 1B/1C/1D backtesting.
**Covers:**
- Recent spinoffs (within 12 months of listing, above $5B market cap)
- Nasdaq 100 non-S&P members above $10B market cap
- Any name manually curated as strategically important

**Why monthly not quarterly:** SNDK would still have been missed for 3-6 months with quarterly Tier 2 refresh. Monthly catches spinoffs within 0-4 weeks. Immediate-add capability (`--add TICKER --reason spinoff`) handles urgent cases within hours.

### Tier 3 — Momentum Watchlist

**File:** `backtest/data/momentum_watchlist.csv` (~50 tickers)
**Refresh frequency:**
- **Live trading (Stage 3+):** Monthly — recomputed at start of each month, fixed for the entire month. Out-of-cycle addition for any stock with >50% single-month move via `--out-of-cycle` flag.
- **Backtesting:** Static — computed once at the start of the backtest run, never changes during the run. Prevents look-ahead bias from using future momentum data.
**Refresh method:** `python scripts/build_momentum_watchlist.py --write` on laptop
**Used by:** Stage 3+ live screening only. NOT used in Phase 1B/1C/1D backtesting.
**Covers:** Top 50 non-S&P stocks by 3-month momentum passing liquidity filter (price >$10, avg volume >500K, market cap >$2B)

**Why monthly not weekly:** Weekly is too noisy — high turnover causes excessive churn in the screening universe. Monthly aligns with institutional rebalancing cycles. A genuinely breakout stock that appears mid-month can be added via the out-of-cycle flag.

### Live universe construction (Stage 3+)

```python
from backtest.data.universe import get_full_live_universe
universe = get_full_live_universe()
# Returns Tier 1 + Tier 2 + Tier 3 + ETFs, deduplicated
# Typical size: 600-650 tickers
```

### Universe history and look-ahead bias (Phase 1D)

For Phase 1D (5-year backtest including 2020-2021), using today's S&P 500 membership for 2020 trades is a subtle form of look-ahead bias — stocks that joined in 2022-2024 are screened for 2020 signals they wouldn't have generated at the time. A `universe_history.csv` file tracking entry/exit dates for each ticker is planned for Phase 1D to address this. Not in scope for Phase 1B/1C.

### Known gaps accepted for Phase 1B

The current Phase 1B backtest uses the static CSV. These stocks are missing and their returns are not captured: SNDK, GEV, SMCI, VST, GDDY, ERIE. The stale removals (HSIC, WBA — confirmed removed from S&P 500) are still in the CSV and will generate minor noise. These are accepted limitations for Phase 1B and addressed from Phase 1C onwards.

---

### Known Limitations

**Data and infrastructure limitations:**
- Daily bar data only — intraday stop precision limited
- Gap-down exits slightly optimistic (estimated 0.1-0.3% on affected trades)
- Earnings dates from yfinance not always point-in-time historical
- 2020 Phase 1D data lacks smart money context (Quiver history may not extend to 2020)

**Correlation and market-level limitations (see dedicated section above for full detail and remediation roadmap):**
- No sector rotation signal, no relative strength filter, no intermarket conditioning
- No market breadth filter, no large/small cap rotation signal
- No post-earnings drift strategy, no sector-level mean reversion
- No factor awareness (value/growth/quality/momentum), no regime change strategy
- Regime classifier is daily-only with no weekly confirmation layer

---

## Cost Summary

| Item | One-time | Monthly | Notes |
|---|---|---|---|
| Phase 1B (Haiku agents) | ~$116 CAD | — | One-time run |
| Phase 1C (Sonnet) | ~$102 CAD | — | One-time run |
| Phase 1D (Sonnet) | ~$38 CAD | — | One-time run |
| Quiver Trader | — | $75 USD | Cancel after 1B, re-subscribe Stage 3 |
| Unusual Whales | — | ~$50 USD | Phase 1C onwards |
| Ortex | — | ~$40 USD | Stage 3 onwards |
| Anthropic (live) | — | ~$25 CAD | Daily screening |
| IBKR commissions | — | Variable | Stage 4 — $0.005/share |
| Hetzner VPS | — | ~$8 CAD | Stage 3 onwards |
| **Total Stage 4** | | ~$250 CAD/mo | All APIs + VPS |

---

## Regime Classification

### Two systems — different purposes

The system uses two separate regime frameworks that serve different purposes and must not be confused.

**System 1 — Real-time regime detection (engine, runs every trading day)**

Classifies the current market environment into one of 4 regimes using only data available at the time of signal evaluation:

- **Bull:** 20-day realised vol < 15% AND SPY above 200-day EMA. Full size, long favoured.
- **Neutral:** Neither bull nor bear conditions met. Full size, both directions.
- **Bear:** 20-day realised vol > 25% AND SPY below 200-day EMA. Full size, short favoured.
- **Crisis:** 20-day realised vol > 35%. Long size reduced to 50%, VERY HIGH tier required for longs.

Note: 20-day realised volatility is used as a VIX proxy because ^VIX is blocked in the Codespace environment. In live trading this will be replaced by actual VIX. Crisis regime deliberately allows long entries at 50% size — this is the buy-the-dip thesis for high-conviction setups during dislocations.

**System 2 — Historical backtest regimes (IS/OOS labelling only)**

Eight named historical periods used to label the backtest study window and define walk-forward validation splits. These are hardcoded date ranges, not computed dynamically. They exist only for analysis labelling, not for trade decisions.

The eight regimes are: bear_correction_2022, rate_rising_2022_2023, strong_bull_2023, rate_falling_2024, ai_sector_bull_2024, tariff_shock_2025, ai_divergence_2025_2026, covid_crisis_2020.

### How regime affects trades (System 1 only)

Every signal evaluation calls classify_regime() before candidate assessment. The result affects: (1) whether a direction is allowed, (2) minimum confidence tier in crisis (VERY HIGH for longs), (3) long position size in crisis (0.5x). Regime does not block entries outright except shorts require VERY HIGH tier in bull regime.

### Regime distribution 2022-2026

Based on 20-day realised vol and SPY vs 200 EMA across the full backtest period: Bull 58%, Neutral 32%, Bear 10%, Crisis 2%. The 2022 bear/crisis period is the primary stress test — realised vol peaked at 54% in June 2022.

### Live trading regime change detection (Stage 3 — not yet built)

Two detection layers are planned: a confirmation layer (3-day persistence before regime change is applied, preventing whipsawing) and an alert layer (fast signals: VXX single-day spike >15%, SPY first close below 200 EMA, CNN Fear & Greed below 25 — two simultaneous alerts trigger immediate position size reduction). Crisis detection bypasses the 3-day buffer — a single-day VXX threshold breach triggers crisis immediately.

### Known limitations

The regime classifier itself is not backtested for accuracy in Phase 1B — thresholds are literature-based. Per-regime metrics (win rate, profit factor per regime) are computed in Phase 1B results to validate whether regime filtering is working. Portfolio heat is computed per batch in parallel runs, not across all simultaneous positions — documented as known limitation in CHECKLIST item 18.
---

## Glossary of Technical Terms

**ATR (Average True Range):** A measure of a stock's daily price volatility. Calculated as the average of (high minus low) over the past 14 days, accounting for overnight gaps. A stock with ATR of $5 typically moves $5 in a normal day. Used to set stop-loss distances proportional to each stock's volatility.

**Bollinger Bands:** Price envelope plotted 2 standard deviations above and below a 20-day moving average. When price touches the lower band it is statistically "oversold" relative to recent history. Used in mean-reversion strategies.

**Camarilla Pivots:** Intraday support and resistance levels calculated from the prior day's high, low, and close using fixed mathematical ratios. S3 and S4 are strong support levels; R3 and R4 are strong resistance levels. The Camarilla system produces tighter, more precise levels than standard pivots.

**EMA (Exponential Moving Average):** A moving average that weights recent prices more heavily than older prices. The 200-day EMA is the most widely-watched long-term trend indicator used by institutional traders.

**MACD (Moving Average Convergence Divergence):** A momentum indicator calculated as the difference between a 12-day and 26-day EMA, with a 9-day signal line. A MACD line crossing above its signal line suggests momentum is turning positive.

**OBV (On-Balance Volume):** A running cumulative sum of volume — volume is added on up-days and subtracted on down-days. Rising OBV alongside price confirms that buyers are genuinely driving the move.

**Pivot Points:** Daily support and resistance levels calculated from the prior day's high, low, and close. S1 (support 1) is the first support below the pivot; R1 (resistance 1) is the first resistance above. Used as reference points by professional traders.

**Profit Factor:** Total gross winning trades divided by total gross losing trades. A profit factor of 1.5 means the system makes $1.50 for every $1.00 it loses. Anything above 1.0 is profitable; above 1.3 is considered a meaningful edge.

**RSI (Relative Strength Index):** A 0-100 oscillator measuring the speed and change of price movements. Below 30 is traditionally "oversold" (used for long entries in mean-reversion strategies). Above 70 is "overbought" (used for short entries).

**Walk-Forward Validation:** A test methodology that prevents overfitting by testing strategy performance on data that was completely excluded from the optimisation period. See the IS/OOS section for a full explanation.

---

## Worked Example: A Trade Through the Full Pipeline

This example illustrates how a single trade candidate flows through the system, using MMM (3M Company) as a hypothetical example.

**Day 0 — Signal fires:** The `confluence_rsi_obv` strategy fires on MMM. RSI is at 31 (oversold), OBV has turned positive after three down-days, and price is near the daily S1 pivot support. Three independent systems agree.

**Preliminary tier (Stage 1 — rule-based):** One strategy fired. No smart money signals found (no recent congressional trades, no insider cluster buy). Preliminary tier = LOW. A LOW tier means the position will not be opened regardless of what agents say — this is a watch-only signal.

**With smart money added:** Suppose congressional data shows Senator X disclosed a $50,000 MMM purchase 12 days ago. Now: one strategy + congressional buy within 30 days = MEDIUM preliminary tier. Position size = 0.75% of capital.

**Agent pipeline (Stage 2 — AI-adjusted):** Six agents evaluate MMM. Technical agent finds the S1 support is a historically significant level. Fundamental agent notes the congressional trade but no insider cluster buy. Sentiment agent finds AAII sentiment is at extreme bearishness (contrarian bullish). Risk agent notes the yield curve is inverted (headwind) and CPI is due in 3 days (risk event). Bull/Bear debate: bull argues oversold bounce at support with smart money backing; bear argues earnings are in 11 days and macro headwinds are significant. Decision agent scores the trade 62 out of 100.

**Tier adjustment:** Score 62 is between 40 and 75 — no adjustment. Final tier stays at MEDIUM.

**Entry:** Next day's open. Position size = 0.75% × $10,000 = $75. At MMM price of $100, this is 0 shares (rounds to zero — position too small at this capital level). This illustrates why $10,000 minimum capital is required for the math to work, and why LOW and MEDIUM tiers are primarily educational at small capital.

**Exit:** ATR trailing stop set at 1× ATR below the highest closing price since entry. If ATR = $3, stop is $3 below the high. As price rises from $100 to $108, the stop rises to $105. If price falls from $108 to $104.50, the stop (checked against intraday low) triggers and the position is closed.

---

## Phase 1B Parallel Batch Architecture

Phase 1B runs 509 tickers across 4 years with AI agents evaluating each candidate. Running this sequentially would take 48-72 hours. The parallel batch approach reduces this to 12-15 hours.

**How it works:** The 509-ticker universe is split into 5 non-overlapping batches of ~101 tickers each. All 5 batches run simultaneously in separate terminal windows on a local laptop (not Codespaces — laptops don't time out). Each batch writes to its own output directory. The agent cache (one JSON file per analysis) is shared across all batches on disk — if two batches analyse the same ticker-date-strategy combination (they won't, since tickers don't overlap), the second would use the cached result.

**Race condition protection:** Two shared files can be written by multiple processes simultaneously — `index.json` (OHLCV cache index) and `info_cache.json` (company info). Both are protected with file locks (`filelock` library) to prevent corruption. Additionally, `scripts/prepopulate_cache_index.py` pre-fills both files for all 509 tickers before any batch starts, minimising live writes during the run.

**Crash recovery:** Every 100 trading days during a batch run, the in-memory trade log is written to `trade_log_checkpoint.csv`. If the process crashes, restarting the same batch will skip all already-cached agent analyses and rebuild the trade log from scratch — but the expensive API calls are not repeated.

**Merge process:** After all 5 batches complete, `scripts/merge_batch_outputs.py` concatenates all 5 trade logs and re-computes all strategy metrics on the combined dataset. Strategy metrics are never averaged across batches — they are always recomputed on the full combined trade log, because averaging metrics (e.g. averaging win rates) is statistically incorrect.

**Walk-forward in batch mode:** Per-batch walk-forward is suppressed (`--no-git` flag). Individual batches of 101 tickers rarely have 100+ trades per strategy in the IS period — the minimum required for statistical validity. Walk-forward is only run on the merged final result after all 5 batches complete.

---

## What Happens to Strategies That Fail Phase 1B

Strategies that fail Phase 1B criteria are not tuned or retested with adjusted parameters. This is a deliberate anti-overfitting rule.

**Why no parameter tuning:** If we test a strategy, see it fails with threshold X, adjust threshold X to make it pass, and report it as a success — this is data-mining and will produce strategies that look good on historical data but fail in live trading. The 10 passing criteria are set before the backtest runs and are not adjusted based on results.

**What "fail" means in practice:** For the 9 overall criteria (win rate, profit factor, etc.), pass/fail is binary — 8 of 9 is still a fail overall. For the per-regime criterion (criterion 10), failure is regime-specific. A strategy that fails in bull but passes in crisis is not discarded — it is tagged as a crisis-only strategy and deployed only when the regime classifier detects crisis. This is intentional: different regimes reward different strategies.

**Failed strategies are retained for reference.** The results CSV includes all strategies, including failures, with their exact metrics. This is valuable because: (1) a strategy that fails statistical minimum but shows strong win rates may reappear with more data in Phase 1D, (2) understanding why strategies fail informs the design of better strategies in future iterations.

**The exception — INSUFFICIENT_OOS_DATA:** A strategy with fewer than 30 OOS trades receives no pass/fail verdict. It is retested in Phase 1D with 5 years of data to see if the trade count becomes sufficient.

---

## Open Decision: News Sentiment (Alpha Vantage)

Alpha Vantage provides AI-powered news sentiment scores for all 509 tickers. The free tier provides only 25 API calls per day — insufficient to cover 509 tickers. The premium tier costs approximately $50 USD/month.

**The question:** Does news sentiment meaningfully improve agent confidence tier accuracy? Or do the existing signals (congressional trading, insider filings, technical signals, macro data) already capture enough context?

**How we're answering this:** A controlled A/B test on 5 tickers (MMM, AOS, ABT, ABBV, ACN) from January 2022 to October 2022. One run includes news sentiment in the Sentiment Agent context; the other run suppresses it entirely. We compare: how often does the news signal change the final confidence tier? Are the tier changes in the correct direction (did the news-influenced tier produce better outcomes)?

**Decision criteria:** If news changes tier assignments on >10% of candidates and those changes correlate positively with outcomes → pay for premium. If news rarely changes tiers or changes them in the wrong direction → proceed with Phase 1B without news, saving $50/month.

**Current status:** Both runs have completed and the agent cache is committed. Analysis pending.

---

## RESTORED SECTIONS — Original Detailed Reference (restored April 2026)
*The following sections were removed in commit 38e7ee2 and have been fully restored. These are the original detailed specifications.*

---

## 1. Vision

Build a validated algorithmic swing trading system that evolves from a daily stock picks webpage into a fully automated trading engine covering US markets. Every stage must be proven before progressing. No real money is risked until strategies are validated through rigorous backtesting across multiple market regimes and confirmed through paper trading.

> **Intraday trading is a completely separate future project. Nothing in this plan applies to it.**

---

---

## 2. Non-Negotiable Rules

- Never skip paper trading before real money
- 3 years minimum backtesting — no exceptions
- Point-in-time data enforcement — no future data ever used in backtesting
- Stop loss mandatory on every live trade from Stage 4 onwards
- Each stage must earn the right to advance to the next
- Any win rate >75% or profit factor >1.5 must be audited for look-ahead bias first
- No leveraged ETFs anywhere in the universe
- Every rule, filter, threshold change requires explicit owner approval before implementation
- Human email approval required for every live trade in Stage 4 only. Stage 3 is fully automated paper trading.
- Backtests must mirror live trading scenarios as closely as possible. Every data source, signal, and API used in live trading must also be used in backtesting. If it is not backtested, it is not validated.
- Never run Phase 1B without complete data (all Quiver types 509/509, Finnhub 509/509, FRED to March 2026)
- Always run 25-ticker batch test and review agent outputs before full Phase 1B run
- Granular data before aggregates — always capture lowest-level data first

---

---

## 3. Risk Profile

**Medium-high risk, high return focus.** Drawdowns are accepted as part of the strategy. ROI over time is the goal, not minimising short-term volatility. The system buys dips including in volatile and crisis markets — the trailing stop system manages downside without needing to predict the bottom.

**On VIX spikes:** High-VIX environments (VIX > 40) represent the best entry opportunities, not reasons to stop trading. Position size is reduced but entries are not blocked. Tightening stops during high volatility causes whipsawing — stops are not tightened.

---

---

## 4. Five Stage Roadmap

### Stage 1 — Proof of Concept ✅
Daily stock picks webpage. Top gainers for US (NYSE/NASDAQ) and Canadian (TSX) markets. Updated daily via GitHub Actions at 6am UTC. Zero cost.

**APIs:** Alpha Vantage free, GitHub Actions, GitHub Pages

---

### Stage 2 — Strategy Validation (Current)

#### Objective
Determine which of 60 strategies, across which market regimes, using which exit method, produce statistically valid trading edges. Zero money at risk.

#### Phase Universe and Cost
| Phase | Instruments | Period | Agents | Est. Cost |
|---|---|---|---|---|
| 1A | SP50 + 17 ETFs = 67 | Jan 2022–Mar 2026 | None (no-agents flag) | $0 |
| 1B | 509 instruments | Jan 2022–Mar 2026 | Haiku | ~$116 CAD |
| 1C | All passing Phase 1B (max 30) | Jan 2022–Mar 2026 | Sonnet | ~$102 CAD |
| 1D | All passing Phase 1C | Jan 2020–Mar 2026 (5 years) | Sonnet | ~$38 CAD |

**Phase 1C/1D note:** All strategies passing criteria advance — not an arbitrary top 20% or top 5. The max 30 cap is a cost control measure only.

#### Walk-Forward Validation
| Period | Role | Dates |
|---|---|---|
| In-sample (IS) | Strategy development and validation | Jan 2022 — Dec 2024 |
| Out-of-sample (OOS) | Unseen data test — confirms edge is real | Jan 2025 — Mar 2026 |

**Two-window walk-forward (Phase 1B):**
- Window 1: IS = 2022-2023, OOS = 2024
- Window 2: IS = 2022-2024, OOS = 2025-Mar 2026
- ROBUST = passes BOTH windows. WEAK = passes one. OVERFIT = passes neither.
- Minimum 30 OOS trades required for ROBUST verdict. Below this: "INSUFFICIENT OOS DATA."

#### 7 Market Regimes Tested
| Regime | Period | Condition |
|---|---|---|
| Bear correction | Jan–Dec 2022 | S&P −19.4%, VIX 25+ |
| Rate rising | Mar 2022–Jul 2023 | Fed 0.25% → 5.50% |
| Strong bull | Jan–Dec 2023 | S&P +24.2% |
| Rate falling | Jan–Dec 2024 | Fed cuts begin |
| AI sector bull | Jan–Dec 2024 | Tech/AI driven outperformance |
| Tariff/policy shock | Jan–Jun 2025 | Trump tariff uncertainty, VIX spikes |
| AI divergence | Jul 2025–Mar 2026 | NVDA +100% vs broad market flat |

#### 10 Passing Criteria (ALL required simultaneously)
All thresholds are sector-adjusted (see Section 7). Values below are for medium-volatility sectors.

| # | Metric | Medium-vol threshold | Notes |
|---|---|---|---|
| 1 | Win rate | ≥ 55% | Sector-adjusted — see Section 7 |
| 2 | Profit factor | > 1.3 | Flag if > 1.5 — look-ahead audit required |
| 3 | Expected value | > 0 | (win_rate × avg_win) + (loss_rate × avg_loss) |
| 4 | Win/loss ratio | > 1.0 | avg_win / avg_loss |
| 5 | Max drawdown | < 20% | Sector-adjusted — see Section 7 |
| 6 | Total ROI | > 0% | Positive total return over full period |
| 7 | Smart money lift | ≥ 3pp win rate improvement | Trades with SM signal vs without, min 30 in each bucket |
| 8 | Macro correlation | ≥ 5pp win rate diff | Favourable vs unfavourable regime, min 20 trades per regime |
| 9 | Minimum trades | ≥ 500 | Statistical validity across 60 strategies |
| 10 | Regime coverage | Profitable in ≥ 2 of 7 regimes | Now 7 regimes since extending to Mar 2026 |

**OOS minimum:** 30 trades in OOS period. Below this = "INSUFFICIENT OOS DATA" — not ROBUST.

**Confidence intervals:** Win rates reported with 95% binomial confidence intervals. Strategies where lower CI bound < 50% are flagged — may not be statistically distinguishable from random.

#### Stage 2 Success Criteria
- Minimum 3 strategies pass all 10 criteria in Phase 1B
- Walk-forward shows ROBUST on BOTH windows for at least 2 strategies
- At least 1 short strategy fires and passes during 2022 bear market
- Smart money lift ≥ 3pp measurable on at least 3 strategies
- No win rate >75% or PF >1.5 without clean look-ahead bias audit
- All 13+ output files written cleanly including trade_exit_detail.csv

---

### Stage 3 — Paper Trading (Fully Automated)
**Duration:** 3-6 months minimum
**Capital at risk:** Zero
**Broker:** Alpaca paper trading (free)
**Execution:** Fully automated — no email approval. Candidates above VERY HIGH tier automatically paper traded via Alpaca.

#### Automated Workflow
1. Daily GitHub Actions cron job runs at 6am UTC
2. Screener runs on 509 instruments
3. Candidates pass through 6-agent pipeline (Sonnet)
4. Candidates above VERY HIGH: automatically paper traded via Alpaca API
5. Exit monitoring runs daily — trailing stops managed automatically
6. Results written to site JSON for website display
7. Weekly performance review email generated automatically

#### Success Criteria
- Live win rate within 10pp of backtest win rate
- Live profit factor within 0.2 of backtest
- System runs reliably for 3+ months without crashes
- Alpaca API reliability confirmed — zero missed executions
- Minimum 50 paper trades completed across all tiers
- All tiers tracked (not just published picks) for full distribution analysis

**Monthly cost:** ~$6 CAD (VPS only)

---

### Stage 4 — Live Trading Small
**Starting capital:** $500-1000 CAD maximum
**Human approval:** Email approval required for every single trade (retained from original design)

#### Risk Management Rules (Stage 4)
- Maximum position size: tiered by confidence (see Section 7)
- Maximum 10 open positions simultaneously
- Reduce position size 50% after 3 consecutive losses
- Congressional and insider signals checked before every trade
- All 5 circuit breakers active at all times
- Daily loss limit: TBD — to be calibrated from Stage 3 paper trading data
- Portfolio drawdown rules: at >10% drawdown, reduce all positions 25%. At >20%, reduce 50%. At >30%, suspend new entries.

#### Success Criteria
- 6 months live with at least 50 real trades
- Live win rate within 10pp of paper trading
- No single trade loss exceeding position size limit
- System fully stable — zero unplanned outages in last 60 days
- Profit factor > 1.0 on real trades (breaking even acceptable — validating system)

**Monthly cost:** ~$85-120 CAD

---

### Stage 5 — Full Automation
**Gate condition:** Stage 4 profitable for 6+ months, all systems proven reliable

**Monthly cost:** ~$300-360 CAD (full API stack)

---

---

## 5. Strategy Universe — 60 Strategies, 7 Categories

| Category | Count | Direction | Core logic |
|---|---|---|---|
| Pivot-based | 10 | Long | S1/S2/S3 bounces, R1/R2 breakouts, CPR bias, Camarilla, prev day H/L |
| Momentum | 9 | Long | MACD (×2), Hull+RSI, Williams%R, ROC, AO, StochRSI, PPO, UO |
| Trend following | 9 | Long | Golden cross (3 pairs), Parabolic SAR, TEMA/DEMA, Ichimoku, ADX, Supertrend |
| Mean reversion | 11 | Long + Short | RSI oversold (×3), RSI overbought short, MFI, CMF, Bollinger (×2), BB upper short, Keltner, Stochastic |
| Breakout | 6 | Long | Squeeze, Volume spike, 52-week high, Inside bar, Force Index, Donchian 10d |
| Candle pattern | 6 | Long + Short | Morning star, Bullish engulfing, Doji, Three white soldiers, Shooting star short, Evening star short |
| Confluence | 9 | Long | Multi-signal combinations requiring ≥2 independent signals simultaneously |

**Short strategy gap:** Only 5 of 60 strategies are short. In bull markets these rarely fire. Phase 1B will validate which short strategies generated adequate trades during the 2022 bear. Strategies with insufficient short data will be noted as untested for bear markets.

---

---

## 6. Exit System — 12 Methods Compared

**Primary exit (Phase 1A confirmed):** `atr_trail_1x` — trailing stop at 1× ATR below highest closing price. ATR-adaptive — adjusts to each stock's volatility. Confirmed as best exit method on 20/29 strategies in Phase 1A v3.

**Why ATR trailing not fixed %:** A fixed 10% trailing stop behaves differently across instruments. NVDA with 3-4% daily range hits a 10% stop in 2-3 days of normal movement. KO with 0.5% daily range needs 20 days of adverse movement. ATR normalises this — each stock gets a stop proportional to its actual volatility.

**12 exit methods tested simultaneously** via composite score (40% ROI + 30% profit factor + 30% lowest drawdown):

| Exit | Logic |
|---|---|
| ATR trail 1× | **Primary confirmed exit** — 1× ATR below highest close |
| Trailing 10% | Fixed 10% below highest close |
| Trailing 5% | Tighter — faster exit |
| Trailing 15% | Looser — stays in longer |
| ATR trail 2× | More room on trending stocks |
| Fixed 3:1 target | 3× ATR profit / 2× ATR stop |
| Next pivot target | Exit at next R1/R2/R3 above entry |
| MA exit EMA-9 | Exit when price crosses below EMA-9 |
| Time stop 10d | Force exit day 10 |
| Time stop 20d | Force exit day 20 |
| Breakeven + trail | Move to breakeven at 1× ATR profit, then trail 10% |
| Hybrid 50% target | Take 50% off at 3× ATR, trail remainder |

**Time stop backstop:** All trades also subject to 40-day maximum hold (2 months). If no meaningful price movement (< 5% in either direction from entry) by day 40, exit. Prevents capital being locked in sideways trades indefinitely.

**Exit slippage:** Entry slippage applied at entry AND exit. Circuit breaker exits apply 2× slippage to reflect gap scenarios.

**Stop simulation known limitation:** Daily Low checked against trailing stop each day. On gap-down opens where stock opens below stop, real fill is at open (worse). Circuit breaker 1 handles gaps >12%. Gaps 1-12% are not adjusted. Estimated impact: 0.1-0.3% optimism on affected trades (~15% of all stops triggered).

**5 circuit breakers** (priority order):
1. Overnight gap >12% wrong direction → exit at open
2. Earnings gap >8% wrong direction → exit at open
3. Intraday halt + down >15% from entry → exit on resume
4. S&P 500 market-wide halt → flag all, no new trades
5. VIX >40 → reduce NEW position sizes 50%, require VERY HIGH minimum tier. Do NOT tighten existing stops (causes whipsawing). VIX >50 → suspend new entries, manage existing only.

**Circuit breaker 5 rationale:** VIX >40 environments (March 2020, October 2022) contain the best entry opportunities for mean reversion and crisis buy strategies. Blocking entries contradicts the buy-the-dip philosophy in Section 3. Position size reduction manages risk without eliminating opportunity.

---

---

## 7. Confidence Tiers, Position Sizing & Sector-Adjusted Criteria

### Two-Stage Confidence Tiering

**Stage 1 — Rule-based preliminary tier (before agents run):**
Raw signal count determines preliminary tier. This prevents agents being gated by the same data they evaluate.

**Stage 2 — Agent-adjusted final tier:**
Agent final score adjusts preliminary tier ±1 level:
- Agent score ≥ 75 → upgrade one tier (e.g. VERY HIGH → EXCEPTIONAL)
- Agent score ≤ 40 → downgrade one tier (e.g. HIGH → MEDIUM_HIGH)
- AVOID tier never upgrades regardless of agent score

### Confidence Tiers

| Tier | Preliminary conditions (Stage 1) | Position size | Published | AVOID as short opportunity |
|---|---|---|---|---|
| EXCEPTIONAL | 3+ strategies + congressional + insider cluster (both) | 5% of capital | Active picks | — |
| VERY HIGH | 2+ strategies + congressional OR insider buy | 4% of capital | Active picks | — |
| HIGH | 3+ strategies, no smart money | 3% of capital | Watchlist | — |
| MEDIUM-HIGH | 2 strategies, no smart money | 1.5% of capital | Watchlist | — |
| MEDIUM | 1 strategy + any smart money buy | 0.75% of capital | Not published | — |
| LOW | 1 strategy only | 0% — watch only | Not published | — |
| AVOID | Congressional sell + insider cluster sell | 0% long — evaluate short | Not published | ✅ See below |

**MEDIUM tier note:** Previously 0% — changed to 0.75%. Congressional or insider buy signal is present. This is validated smart money data. Taking a small position is justified even with only 1 technical strategy.

**AVOID → Short opportunity:**
An AVOID signal means congressional sell AND insider cluster sell are both present. This is the highest-conviction informed selling signal available. It should be treated as a potential short setup:
- AVOID signal fires → check if any short strategy also triggers
- AVOID + short strategy signal = highest conviction short entry (EXCEPTIONAL short tier)
- AVOID alone (no short strategy) = do not take long, watch for short setup developing
- Never auto-short on AVOID alone — technical confirmation required
- This converts the strongest "don't buy" signal into a potential "sell short" signal, maximising use of smart money intelligence

### Sector-Adjusted Passing Criteria

Different sectors have inherently different volatility profiles. The same drawdown or win rate means different things in Energy vs Consumer Staples.

| Sector group | Sectors | Min win rate | Max drawdown | Min profit factor |
|---|---|---|---|---|
| High volatility | Energy, Information Technology, Health Care, Communication Services | 50% | 25% | 1.2 |
| Medium volatility | Financials, Industrials, Consumer Discretionary, Materials | 55% | 20% | 1.3 |
| Low volatility | Consumer Staples, Utilities, Real Estate | 58% | 15% | 1.4 |
| ETFs/Unknown | Broad Market, Commodities, Fixed Income | 55% | 20% | 1.3 |

### Position Sizing with Drawdown Scaling

Base sizes above apply at normal portfolio state. Scaling rules:
- Portfolio drawdown > 10% → reduce all position sizes 25%
- Portfolio drawdown > 20% → reduce all position sizes 50%
- Portfolio drawdown > 30% → suspend new entries, manage exits only

**Kelly Criterion check (post-Phase 1B):**
After Phase 1B results, calculate ¼ Kelly for each passing strategy. If Kelly suggests our tier size is >2× too large, flag for review. If Kelly suggests we're significantly undersizing, flag as opportunity.

---

---

## 8. Engine Operating Rules (Backtest Mode)

### Approved Rules — Backtest Only
| Rule | Value | Rationale |
|---|---|---|
| Open position cap | None — uncapped | Statistical validity requires all signals to fire |
| Trades per ticker per day | No limit — all strategies fire independently | Multiple signals on same ticker = multiple separate positions |
| Daily loss limit | None in backtest | Removed — calibrated from Stage 3 paper trading data |
| Correlation filter | None in backtest | Sectors trend — targeting trending sectors is the strategy |
| Regime position sizing | None — full size in all regimes | Backtest needs data across all conditions |
| Regime direction block | None — all directions allowed | Crisis = best entry prices. Flagged not blocked. |
| Crisis regime trades | Allowed. Flagged as `regime=CRISIS_FLAG` | Buy dips in volatile markets — trailing stop manages downside |
| Max candidates per day | 10 | Enough signals per strategy for statistical validity |
| Entry zone ATR — mean reversion | 1.0× | Raised from 0.5× — to be compared in Phase 1B analysis |
| Liquidity filter | Applied annually at Jan 1 of each year | Price > $5, avg volume > 500k, market cap > $100M. Re-checked annually not just at load. |
| Sector concentration | Unfiltered but logged | Track % portfolio per sector per day in trade log for Phase 1B analysis |
| Maximum hold period | 40 trading days | Time stop backstop — prevents capital locked in sideways trades |

### Rules That Remain Active in All Modes
| Rule | Value |
|---|---|
| Point-in-time data enforcement | Always — no future data ever |
| Primary exit | atr_trail_1x — ATR-adaptive trailing stop (Phase 1A confirmed) |
| Entry price | Next day open (D+1) + slippage |
| Slippage model — entry | 0.03% ETF, 0.08% large-cap, 0.15% high-vol |
| Slippage model — exit | Same as entry. Circuit breaker exits: 2× entry slippage |
| Transaction costs | 0.08% ETF, 0.10% large-cap, 0.15% mid-cap round trip. Min $1 per trade. |
| Survivorship bias haircut | Hold-adjusted: < 7d = 0.5%/yr, 7-14d = 1%/yr, 14-30d = 2%/yr, > 30d = 3%/yr |
| Walk-forward validation | Two windows — IS 2022-23/OOS 2024 AND IS 2022-24/OOS 2025-Mar26 |
| Minimum OOS trades | 30 — below this = INSUFFICIENT OOS DATA not ROBUST |
| Minimum total trades | 500 per strategy (statistical validity) |
| Look-ahead bias audit | Win rate >75% or PF >1.5 → flagged automatically |
| Smart money lift threshold | ≥ 3pp win rate improvement, min 30 trades per bucket |
| Macro correlation threshold | ≥ 5pp win rate diff favourable vs unfavourable, min 20 trades per regime |
| Confidence intervals | 95% binomial CI on all win rates. Flag if lower bound < 50%. |
| Congressional signal age | < 30 days: full weight. 30-60 days: 50% weight. > 60 days: not used. |
| Two-stage tiering | Rule-based prelim → agent adjusts ±1 level (score ≥75 upgrade, ≤40 downgrade) |
| Earnings proximity | Context and risk factor for agents — NOT a trade blocker |
| AVOID + short strategy | Evaluate as potential short entry — AVOID alone does not trigger short |

### Resolved Decisions
| Decision | Resolution |
|---|---|
| Multiple strategies on same ticker | Separate independent positions — all fire |
| Primary exit method | atr_trail_1x confirmed Phase 1A |
| Stage 3 execution | Fully automated paper trading — no email approval |
| Stage 4 execution | Email approval every trade — retained |
| AVOID signal | Do not go long. Evaluate short if short strategy also triggers. |
| Earnings proximity | Context not blocker — agents assess and may reduce size |

### Pending Decisions — Stage 4
| Decision | Status |
|---|---|
| Daily loss limit value | Calibrate from Stage 3 paper trading data |
| Maximum open positions live | TBD — Stage 3 paper trading will inform. Target 10. |
| Pyramiding rules | Flagged for Stage 4 and separate backtesting |
| Sector concentration limit live | TBD — informed by Phase 1B sector concentration analysis |

---

---

## 9. Signal Universe — 274 Fields Per Instrument Per Day

| Category | Signals |
|---|---|
| Pivots | Standard (P/R1-R3/S1-S3), Camarilla (R1-R4/S1-S4), Woodie's, CPR, Fibonacci (5 levels + extensions), VWAP + bands, Prev Day H/L/C |
| Momentum | RSI (9/14/21), Stochastic, StochRSI, Williams%R, ROC, MACD (×2), PPO, Awesome Oscillator, Ultimate Oscillator |
| Trend | EMA/SMA crossovers (9/21, 20/50, 50/200), ADX, Parabolic SAR, Ichimoku (all 5), Supertrend, Hull MA, DEMA, TEMA |
| Volatility | Bollinger Bands (3 sets), Keltner, Donchian (10+20d), ATR, Squeeze Momentum |
| Volume | OBV, Volume Spike (1.5×/2×/3×), VWAP deviation, A/D Line, CMF, MFI, Force Index, 52-week high |
| Candle | Inside/Outside bar, Engulfing, Pin bar, Hammer, Shooting Star, Morning/Evening Star, Doji, Three White Soldiers, Three Black Crows |
| Context | Sector ETF daily return, price vs 52w high/low, nearest support/resistance, above 200EMA flag |

---

---

## 10. Smart Money & Data Sources

| Source | Data | Cost | Tier | Point-in-time lag |
|---|---|---|---|---|
| yfinance | OHLCV, earnings dates, VIX | $0 | Free | None — historical |
| FRED | Yield curve, fed funds, CPI, unemployment, inflation expectations, treasury yields, corporate spread | $0 | Free | Monthly/weekly |
| Quiver Quantitative | Congressional trades, insider trades (Form 4), 13F institutional, government contracts, lobbying, Wikipedia page views, WallStreetBets mentions | $75/mo Trader | Trader | 45d congressional/13F, 2d insider |
| Finnhub | News sentiment per ticker | $0 | Free | Same day |
| AAII | Investor sentiment (weekly) | $0 | Free (CSV) | Weekly Thursday |
| CNN Fear & Greed | Market sentiment (daily) | $0 | Free (CSV) | Daily |

**Data lags enforced:**
- Congressional trades: 45-day disclosure lag (ReportDate used, not TransactionDate)
- Congressional signal age weighting: < 30 days = full, 30-60 days = 50%, > 60 days = not used
- Insider trades (Form 4): 2 business days
- 13F institutional: 45 days after quarter-end
- AAII: published Thursday — used from Friday onwards

**Data pre-fetched to Parquet cache — no live API calls during backtest:**
- All Quiver data: pre-fetched for all 509 tickers, 2020-Mar 2026
- FRED macro: all 7 series, 2020-Mar 2026
- AAII: 325 weekly readings, 2020-Mar 2026
- CNN Fear & Greed: 1,630 daily readings, 2020-Mar 2026
- Alpha Vantage news: all 509 tickers, 2022-2026 full coverage. AI-powered sentiment scores. Free tier (existing key). Replaces Finnhub which had 1-year lookback limitation.

---

---

## 11. API Stack by Stage

### Stage 1 — Daily stock picks
| API | Role | Cost |
|---|---|---|
| Alpha Vantage | Top gainers + TSX quotes | Free |
| GitHub Actions | Daily 6am UTC cron job | Free |

### Stage 2 — Backtesting (current)
| API | Role | Cost |
|---|---|---|
| yfinance | OHLCV historical data — pre-fetched to Parquet | Free |
| Quiver Trader | Congressional + insider + 13F + gov_contracts + lobbying + wikipedia + wsb | $75/mo — cancel after Phase 1B, re-subscribe Stage 3 |
| FRED | Macro series — pre-fetched to Parquet | Free |
| Alpha Vantage | News sentiment — pre-fetched to Parquet (replaces Finnhub — same key, better AI scores, full 2022-2026 coverage) | Free |
| Anthropic Haiku | Phase 1B agent pipeline | ~$116 CAD |
| Anthropic Sonnet | Phase 1C/1D agent pipeline | ~$140 CAD total |

**Phase 1B cost calculation:** 509 instruments × ~8 candidates/day average × 782 days × $0.00035/Haiku call × 6 agents = ~$116 CAD. Note: only candidates passing screener receive agents — not all instruments every day.

### Stage 3 — Paper trading (automated)
| API | Role | Cost |
|---|---|---|
| yfinance | Daily OHLCV for live screener | Free |
| Quiver Trader | Live congressional + insider + 13F signals | $75/mo |
| FRED | Live macro snapshot | Free |
| Alpha Vantage | Live news sentiment (same key as Stage 1) | Free |
| Unusual Whales | Options flow — Phase 1C validation + Stage 3 live | ~$50/mo |
| Anthropic Sonnet | Daily 6-agent pipeline for all candidates | ~$25/mo |
| Alpaca paper | Paper trade execution + tracking | Free |

### Stage 4 — Live trading
| API | Role | Cost |
|---|---|---|
| All Stage 3 APIs | Same role | Same cost |
| Ortex | Short interest — squeeze risk detection | ~$40/mo |
| IBKR Canada | Real trade execution | $0.005/share, $1 min commission |
| **Total Stage 4** | | **~$190/mo** |

### Phase 1C Addition
Unusual Whales (options flow) and Ortex (short interest) are added in Phase 1C. This validates their contribution before live use — consistent with the principle that backtests must mirror live trading.

---

---

## 12. How APIs Feed Into Confidence Tiers

Two-stage tiering: rule-based prelim → agent-adjusted final.

| Tier | Stage 1 — Raw signal conditions | Stage 2 — Agent adjustment |
|---|---|---|
| EXCEPTIONAL | 3+ strategies + congressional buy + insider cluster buy | Agent score ≥ 75 from VERY HIGH → upgrades to EXCEPTIONAL |
| VERY HIGH | 2+ strategies + congressional OR insider buy | Agent score ≥ 75 from HIGH → upgrades |
| HIGH | 3+ strategies, no smart money | Agent score ≤ 40 → downgrades to MEDIUM_HIGH |
| MEDIUM-HIGH | 2 strategies, no smart money | Agent score ≥ 75 → upgrades to HIGH |
| MEDIUM | 1 strategy + any smart money buy | 0.75% position |
| LOW | 1 strategy only | Agent score ≤ 40 from MEDIUM → downgrades to LOW |
| AVOID | Congressional sell + insider cluster sell | Never upgrades. Evaluate as short if short strategy fires. |

---

---

## 13. How APIs Feed Into the 6-Agent Pipeline

### What Each Agent Receives (as of Phase 1B)

| Agent | Data sources | Key additions vs original |
|---|---|---|
| Technical | 274 signals + strategy-specific signals + sector ETF daily return + price vs 52w range + nearest support/resistance | Sector halo effect, price positioning |
| Fundamental | Quiver insider + 13F + government contracts + lobbying spend + WallStreetBets + Wikipedia + earnings proximity | Gov contracts and lobbying now wired in |
| Sentiment | Quiver congressional detail (name, amount, party, top 3 trades) + AAII + CNN Fear & Greed + Finnhub news | Congressional detail not just composite score |
| Risk | FRED macro (7 series) + VIX + earnings proximity + DXY + corporate spread + sector volatility | Earnings and DXY now passed |
| Bull/Bear | All agent outputs + price vs support/resistance + strategies triggered | Price positioning context |
| Decision | All agent outputs + earnings days + sector volatility tier + position size modifier | Earnings and sector volatility context |

### Agent Quality Validation (Required Before Phase 1B Full Run)
Before scaling to full 509 instruments, manually review 10 batch test trades:
- EXCEPTIONAL tier trades: do they look like genuinely high-conviction setups?
- LOW tier trades: do they look like trades you'd avoid?
- Agent reasoning: is it specific and coherent, or generic boilerplate?
- Congressional detail: is the agent actually using name/amount in its reasoning?

### When Agents Run
| Phase | Agents | Model |
|---|---|---|
| Phase 1A | No (--no-agents flag) | None — pipeline validation only |
| Phase 1B | Yes | Haiku |
| Phase 1C | Yes | Sonnet |
| Phase 1D | Yes | Sonnet |
| Stage 3 paper | Yes | Sonnet |
| Stage 4+ live | Yes | Sonnet |

### Agent Cache Management
Agent results cached as JSON (ticker + date + strategies + phase). Cache must be invalidated when:
- Agent prompts change materially
- New data sources added to agents
- Phase changes (Haiku → Sonnet)

The 108 agent cache files from partial Phase 1B run were generated with old agents (no gov_contracts, lobbying, congressional detail, DXY). These must be cleared before Phase 1B restart.

---

---

## 14. Workflow — Making Changes

### Rule for Changes
No rule, filter, threshold, or strategy parameter is ever changed without explicit owner approval. Claude presents recommendations with reasoning and tradeoffs. Owner decides. Claude builds what is approved.

### GitHub Sync
1. Claude pushes changes to `claude-updates` branch
2. Owner triggers GitHub Actions → Sync from Claude → Run workflow
3. In Codespace: `git fetch origin ; git reset --hard origin/main`

---

---

## 15. Infrastructure

### Current (Stage 2)
- GitHub Codespaces — development and backtest execution
- GitHub Actions — daily stock fetch, sync workflow, data pre-fetch (Finnhub, Quiver)
- GitHub Pages — static website hosting
- All free

### Stage 3 onwards
- Hetzner CX11 VPS ($6 USD/month) — always-on process runner
- PostgreSQL on VPS — trade persistence
- Gmail SMTP — performance alert emails (not approval — Stage 3 is automated)
- Alpaca paper API — automated paper trade execution

### Stage 4+
- Email approval: every live trade requires reply APPROVE or REJECT within 30 minutes
- No auto-execution without approval in Stage 4
- Stage 5: automated execution, email alerts for unusual position sizes only

---

---

## 16. Output Files

| File | Contents |
|---|---|
| `trade_log.csv` | Every trade with 50+ fields including sector, raw SM signals, AAII/CNN readings at entry |
| `trade_log_in_sample.csv` | IS trades only (2022-2024) — for walk-forward window 1 analysis |
| `trade_log_out_of_sample.csv` | OOS trades only (2025-Mar 2026) — for walk-forward window 2 analysis |
| `trade_exit_detail.csv` | Every trade × every exit method — per-trade exit comparison |
| `backtest_results.csv` | All 60 strategies ranked by all 10 metrics with confidence intervals |
| `backtest_report.html` | Dark-themed visual report |
| `winning_strategies.json` | Passing strategies with optimal exit method |
| `exit_strategy_comparison.csv` | All 12 exits × all strategies with composite scores |
| `exit_strategy_best.csv` | Best exit per strategy |
| `regime_performance.csv` | Win rate + ROI per strategy per regime (7 regimes) |
| `walk_forward_validation.csv` | ROBUST/OVERFIT/WEAK/FAILS_BOTH/INSUFFICIENT_OOS per strategy, both windows |
| `improvements_summary.json` | Transaction costs, survivorship, walk-forward summary |
| `smart_money_combined.csv` | Win rate lift at each SM score tier, with confidence intervals |
| `agent_performance.csv` | Win rate by confidence tier — preliminary vs agent-adjusted |
| `skipped_trades.csv` | All skipped entries with reason |
| `circuit_breaker_log.csv` | All circuit breaker triggers |
| `analysis_dashboard_1a.html` | Phase 1A interactive 9-tab dashboard |
| `analysis_dashboard_1b.html` | Phase 1B interactive 9-tab dashboard including agent analysis tab |

---

---

## 17. Phase 1A Results — v3 (Final)

| Metric | Value | Notes |
|---|---|---|
| Trading days | 1,108 | Jan 2022 – Mar 2026 |
| Instruments | 67 | SP50 + 17 ETFs |
| Trades closed | 6,942 | Long and short |
| Strategies fired | 50/60 | 10 didn't fire on 67 instruments |
| Gross ROI | 19,685% | Before transaction costs |
| Net ROI | 18,349% | After transaction costs |
| Passing all criteria | 0 | Expected — 500 trade minimum not met on 67 instruments |
| Best exit method | atr_trail_1x | Wins 20/29 strategies — confirmed as primary |
| WEAK strategies (OOS 2024 only) | 4 | golden_cross_9_21, golden_cross_20_50, bollinger_lower, volume_spike_breakout |

**Key findings:**
- Pipeline clean — all output files written, no look-ahead bias detected
- atr_trail_1x confirmed as primary exit — switched from fixed 10% trailing
- Short strategies fired — validation in full 509-instrument Phase 1B expected

---

---

## 18. All 60 Strategies — Plain English

Each strategy fires when ALL listed conditions are true simultaneously. Entry at next day open (D+1).

### Category 1 — Pivot Based (10 strategies)

| # | Strategy | Direction | Conditions | What it means |
|---|---|---|---|---|
| 1 | pivot_s1_bounce | Long | Price near S1 support AND (hammer or pin bar candle) AND OBV rising | Stock at key daily support, buyers stepping in with volume confirmation |
| 2 | pivot_s2_bounce | Long | Price near S2 support AND RSI-14 < 40 AND (hammer or bullish engulfing) | Deeper support level with oversold momentum and bullish candle |
| 3 | pivot_s3_capitulation | Long | Price near S3 support AND RSI-14 < 30 AND volume spike 2× average | Extreme panic selling at deepest support — high reversal probability |
| 4 | pivot_r1_breakout | Long | Price above R1 resistance AND volume 1.5× AND MACD histogram positive | Resistance breakout with institutional volume and momentum confirmation |
| 5 | pivot_r2_continuation | Long | Price above R2 AND ADX > 25 (trending) AND EMA-50 above EMA-200 | Strong trend continuation — broke major resistance with trend structure intact |
| 6 | cpr_narrow_bullish | Long | CPR range is narrow AND price above CPR AND RSI-14 > 50 | Narrow CPR = directional day likely. Price already above = bullish bias |
| 7 | camarilla_s3_bounce | Long | Price near Camarilla S3 AND RSI-14 < 35 AND OBV rising | Primary Camarilla support with oversold RSI and accumulation volume |
| 8 | camarilla_r3_breakout | Long | Price above Camarilla R3 AND volume spike 2× | Breakout above Camarilla R3 = momentum likely to continue to R4 |
| 9 | prev_day_high_break | Long | Price above previous day high AND volume 1.5× AND above VWAP | Yesterday's high broken with volume and VWAP control — buyers in charge |
| 10 | prev_day_low_bounce | Long | Price near previous day low AND hammer candle AND CMF positive | Previous day low holding as support with buying pressure confirmed by money flow |

### Category 2 — Momentum (9 strategies)

| # | Strategy | Direction | Conditions | What it means |
|---|---|---|---|---|
| 11 | macd_crossover | Long | MACD 12/26/9 histogram crossed above zero | Standard MACD crossover — short-term momentum overtook long-term |
| 12 | macd_fast_crossover | Long | Fast MACD 8/21/5 histogram crossed above zero | Earlier version of MACD — catches momentum shift sooner, more trades |
| 13 | hull_rsi | Long | Hull MA rising AND price above Hull MA AND RSI-9 > 50 | Fast moving average bullish with momentum above midpoint |
| 14 | williams_r_oversold | Long | Williams %R < -80 (oversold) AND price above EMA-200 AND CMF positive | Short-term oversold in long-term uptrend with positive money flow |
| 15 | roc_burst | Long | ROC-12 flipped positive AND volume 1.5× | Rate of change turning up with participation — early momentum shift |
| 16 | awesome_oscillator | Long | AO crossed above zero AND price above EMA-20 | Bill Williams momentum signal turning positive within uptrend |
| 17 | stochrsi_oversold | Long | StochRSI < 20 (oversold) AND StochRSI K crossed above D AND RSI-14 < 55 | Highly sensitive oscillator oversold and turning with RSI context |
| 18 | ppo_crossover | Long | PPO crossed above signal line AND ADX > 25 | Percentage-normalised MACD crossover — works across all price levels |
| 19 | ultimate_oscillator | Long | Ultimate Oscillator < 30 AND price above SMA-200 | Triple-timeframe oscillator oversold — fewer false signals than single period |

### Category 3 — Trend Following (9 strategies)

| # | Strategy | Direction | Conditions | What it means |
|---|---|---|---|---|
| 20 | golden_cross_50_200 | Long | EMA-50 crossed above EMA-200 | Classic golden cross — structural shift from bearish to bullish |
| 21 | golden_cross_9_21 | Long | EMA-9 crossed above EMA-21 AND price above SMA-50 | Fast golden cross — earlier signal, more trades, uptrend context required |
| 22 | golden_cross_20_50 | Long | EMA-20 crossed above EMA-50 AND price above EMA-200 | Medium-term golden cross — between fast (9/21) and slow (50/200) |
| 23 | parabolic_sar_flip | Long | Parabolic SAR flipped from above price to below AND ADX > 25 | Unambiguous trend reversal signal with trend strength confirmed |
| 24 | tema_dema | Long | TEMA crossed above DEMA AND price above TEMA | Fast MA system catching trends earlier than standard EMAs |
| 25 | ichimoku_tk_cross | Long | Tenkan crossed above Kijun AND price not below cloud | Early Ichimoku signal — before full cloud breakout, not in bearish structure |
| 26 | ichimoku_cloud_breakout | Long | Price above Ichimoku cloud AND Tenkan above Kijun AND ADX trending | Full bullish Ichimoku structure — cloud, momentum, and trend all aligned |
| 27 | adx_initiation | Long | ADX crossed above 25 AND DI+ above DI- | Trend initiating from flat — catching the start of a new directional move |
| 28 | supertrend_macd | Long | Supertrend bullish AND MACD positive AND ADX > 20 | Two trend systems aligned with baseline trend strength |

### Category 4 — Mean Reversion (11 strategies)

| # | Strategy | Direction | Conditions | What it means |
|---|---|---|---|---|
| 29 | rsi_oversold | Long | RSI-14 < 35 AND price above SMA-50 | Classic oversold RSI in uptrend — buying the dip |
| 30 | rsi9_extreme | Long | RSI-9 < 20 AND price above EMA-200 AND RSI-9 rising | Extreme fast RSI oversold in long-term uptrend and already recovering |
| 31 | rsi21_slow | Long | RSI-21 < 35 AND price above SMA-50 | Slower RSI — higher quality signal, fewer false positives |
| 32 | rsi_overbought_short | **Short** | RSI-14 > 68 AND price below SMA-50 AND (bearish engulfing OR RSI falling) | Overbought rally in downtrend with bearish confirmation — fade the bounce |
| 33 | mfi_oversold | Long | MFI oversold AND near S1 or S2 AND OBV rising | Volume-weighted RSI oversold at pivot support with accumulation |
| 34 | cmf_flip | Long | CMF crossed above zero AND RSI-14 < 50 | Money flow turning positive — institutional buying starting, not overbought |
| 35 | bollinger_lower | Long | Price at lower Bollinger Band (20,2) AND RSI-14 < 40 AND ADX < 30 | Statistically extreme low with oversold RSI and no strong downtrend |
| 36 | bollinger_tight | Long | Price at lower Bollinger Band (20,2 or 20,1.5) AND RSI-14 < 45 | Tighter band version — slightly more frequent signal |
| 37 | bollinger_upper_short | **Short** | Price at upper Bollinger Band (20,2) AND RSI-14 > 70 AND shooting star candle | Overbought extreme with bearish candle — sellers rejecting the high |
| 38 | keltner_lower | Long | Price at lower Keltner Channel AND hammer candle AND OBV rising | ATR-based support with buyers defending and volume confirmed |
| 39 | stoch_oversold | Long | Stochastic < 20 AND K crossed above D AND price above EMA-20 | Classic stochastic oversold and turning within short-term uptrend |

### Category 5 — Breakout (6 strategies)

| # | Strategy | Direction | Conditions | What it means |
|---|---|---|---|---|
| 40 | squeeze_breakout | Long | BB squeeze released with positive momentum | Bollinger Bands were inside Keltner — coiling energy. Released upward. |
| 41 | volume_spike_breakout | Long | Broke 20-day Donchian high AND volume 2× AND above VWAP | 20-day high broken with institutional volume and intraday control |
| 42 | 52w_high_breakout | Long | Broke 52-week high AND volume 2× | New highs attract buyers. Most studied momentum signal. Volume confirms. |
| 43 | inside_bar_breakout | Long | Inside bar formed AND ADX trending AND above VWAP | Pre-breakout compression with trend and intraday bias bullish |
| 44 | force_index_breakout | Long | Force Index crossed above zero AND price above EMA-20 | Price × volume momentum turning positive within uptrend |
| 45 | donchian_10_breakout | Long | Broke 10-day Donchian high AND volume 1.5× AND MACD positive | Faster Donchian version — more trades, momentum confirmed |

### Category 6 — Candle Patterns (6 strategies)

| # | Strategy | Direction | Conditions | What it means |
|---|---|---|---|---|
| 46 | morning_star | Long | Morning star 3-bar pattern AND RSI-14 < 45 AND EMA-50 above EMA-200 | Classic 3-day reversal pattern in uptrend context while still oversold |
| 47 | bullish_engulfing_support | Long | Bullish engulfing candle AND at S1/S2/Fibonacci AND OBV rising | Engulfing at key level with volume — two systems confirming the same level |
| 48 | doji_at_support | Long | Doji candle AND at S1/S2/Fibonacci AND volume spike 1.5× | Indecision after downmove at support with volume — reversal often follows |
| 49 | three_white_soldiers | Long | Three consecutive bullish candles AND RSI-14 < 60 | Sustained 3-day buying pressure with room to run before overbought |
| 50 | shooting_star_short | **Short** | Shooting star candle AND at R1/R2 or upper Bollinger AND RSI-14 > 65 | Long upper wick at resistance with overbought momentum — sellers rejecting high |
| 51 | evening_star_short | **Short** | Evening star 3-bar pattern AND RSI-14 > 55 AND price below SMA-50 | 3-day bearish reversal in downtrend context — buyers exhausted |

### Category 7 — Confluence (9 strategies)

| # | Strategy | Direction | Conditions | What it means |
|---|---|---|---|---|
| 52 | rsi_volume_200ema | Long | RSI-14 < 35 AND volume 2× AND price above EMA-200 | Three independent systems: oversold + institutional buying + long-term uptrend |
| 53 | macd_ichimoku | Long | MACD crossover up AND price above Ichimoku cloud | Momentum signal confirmed by trend structure signal simultaneously |
| 54 | bb_squeeze_volume | Long | BB squeeze releasing AND volume 2× AND above VWAP | Compressed energy releasing with institutional participation |
| 55 | pivot_fib_confluence | Long | At S1 or S2 AND at key Fibonacci level AND bullish candle | Two independent price systems pointing to same level with candle confirmation |
| 56 | golden_cross_volume | Long | EMA-50 crossed above EMA-200 AND volume 2× on cross day | Golden cross with institutional participation on the exact cross day |
| 57 | cpr_narrow_momentum | Long | Narrow CPR AND above CPR AND RSI-14 > 50 AND MACD positive | Four signals confirming bullish bias — professional directional setup |
| 58 | camarilla_rsi_obv | Long | Near Camarilla S3 AND RSI-14 < 35 AND OBV rising AND CMF positive | Four independent signals at strongest Camarilla support — highest conviction |
| 59 | supertrend_ichimoku_adx | Long | Supertrend bullish AND above Ichimoku cloud AND ADX strong | Three trend systems all simultaneously bullish — very strong trend |
| 60 | williams_stoch_dual | Long | Williams %R oversold AND Stochastic oversold AND at S1/S2/Camarilla S3 | Two momentum oscillators both oversold at pivot support — rare confluence |

---

---

## 19. All Rules and Filters — Plain English

### Entry Rules

| Rule | Current value | Rationale |
|---|---|---|
| Max candidates per day | 10 | Statistical validity |
| Trades per ticker per day | No limit — all strategies fire independently | Multiple strategies open separate positions |
| Entry price | Next day open (D+1) + slippage | Signal fires at close. Entry simulates real execution. |
| Entry zone — breakout/momentum | Gap ≤ 2× ATR from signal close | Prevents chasing |
| Entry zone — trend/confluence | Gap ≤ 1.5× ATR | Tighter — trend entries must be close |
| Entry zone — pivot/candle | Gap ≤ 1.0× ATR | Tightest — pivot level entries must be precise |
| Entry zone — mean reversion | Gap ≤ 1.0× ATR | Raised from 0.5× — Phase 1B will compare vs original |
| Slippage | 0.03% ETF / 0.08% large-cap / 0.15% high-vol | Entry AND exit. 2× on circuit breaker exits. |
| Minimum price history | 30 trading days | Need 30 days before computing signals |
| Earnings proximity | Context for agents — NOT a blocker | Agents assess risk and may reduce position size |
| Liquidity filter | Annual re-check each Jan 1 | Price > $5, avg volume > 500k, market cap > $100M |
| Maximum hold period | 40 trading days | Time stop backstop — exits sideways trades |

### Portfolio Rules (Backtest Mode)

| Rule | Current value | Rationale |
|---|---|---|
| Open position cap | None — uncapped | Statistical validity |
| Daily loss limit | None | Calibrated from Stage 3 data |
| Correlation filter | None | Sectors trend — concentration logged for analysis |
| Sector concentration | Unfiltered — logged | Track for Phase 1B post-analysis |
| Regime position sizing | None — full size | Backtest needs data from all conditions |
| Crisis regime direction | Allowed — flagged | Best entries are in crisis |
| Liquidity filter | Annual re-check | Not just at load |

### Position Sizing by Confidence Tier

| Tier | Requirements | Size | Notes |
|---|---|---|---|
| EXCEPTIONAL | 3+ strategies + congressional buy + insider cluster buy | 5% | Both SM signals required |
| VERY HIGH | 2+ strategies + congressional OR insider buy | 4% | One SM signal |
| HIGH | 3+ strategies, no smart money | 3% | Technical only |
| MEDIUM-HIGH | 2 strategies, no smart money | 1.5% | Technical only |
| MEDIUM | 1 strategy + any smart money buy | 0.75% | Small size — SM present |
| LOW | 1 strategy only | 0% — watch only | No position |
| AVOID | Congressional sell + insider cluster sell | 0% long. Evaluate short if short strategy fires. | See AVOID → short logic |

All sizes subject to drawdown scaling (Section 7).

### Exit Rules — Priority Order

| Priority | Rule | Trigger |
|---|---|---|
| 1 | Circuit breaker 1 | Overnight gap > 12% wrong direction → exit at open |
| 2 | Circuit breaker 2 | Earnings gap > 8% wrong direction → exit at open |
| 3 | Circuit breaker 3 | Intraday halt + down > 15% from entry → exit on resume |
| 4 | Circuit breaker 4 | S&P 500 market-wide halt → no new trades, flag all |
| 5 | Circuit breaker 5 | VIX > 40 → reduce NEW position sizes 50%, VERY HIGH min. Do NOT tighten stops. VIX > 50 → suspend new entries. |
| 6 | Time stop | 40 trading days — exit if < 5% movement from entry |
| 7 (default) | ATR trailing stop | 1× ATR below highest closing price. Primary exit confirmed Phase 1A. |

### Data Integrity Rules

| Rule | Value |
|---|---|
| Point-in-time OHLCV | Every fetch sliced to as_of date only |
| Congressional trade lag | 45 days. ReportDate used, not TransactionDate. Age-weighted. |
| Insider trade lag | 2 business days |
| 13F institutional lag | 45 days after quarter end |
| Analyst data | Live only — NOT used in backtest |
| Look-ahead bias guard | Automated check on every data fetch |
| Audit flag | Win rate > 75% or profit factor > 1.5 → manual review |
| Agent cache invalidation | Clear cache when agents upgraded. Version tag in cache key. |

### Statistical Validity Rules

| Rule | Value |
|---|---|
| Minimum trades per strategy | 500 |
| Minimum OOS trades | 30 — below this = INSUFFICIENT OOS DATA |
| Walk-forward windows | Two windows required — both must show ROBUST |
| Smart money lift threshold | ≥ 3pp win rate improvement, min 30 trades per bucket |
| Macro correlation threshold | ≥ 5pp win rate diff, min 20 trades per regime |
| Confidence intervals | 95% binomial CI on all win rates |
| Flag for review | Lower CI bound < 50% |

### Improvements Applied to All Results

| Improvement | Value | Effect |
|---|---|---|
| Transaction costs | 0.08-0.15% per leg. Min $1/trade. | Reduces net ROI vs gross |
| Survivorship bias | Hold-adjusted: <7d=0.5%/yr, 7-14d=1%/yr, 14-30d=2%/yr, >30d=3%/yr | Realistic — proportional to exposure |
| Walk-forward | Two windows — both must pass for ROBUST | Eliminates single-window false positives |
| Bonferroni minimum | 500 trades (statistical validity — correctly labelled) | Not true Bonferroni but valid threshold |
| Slippage | Applied entry AND exit | Realistic fills |
| Kelly sanity check | ¼ Kelly computed post-Phase 1B | Validates tier position sizes |

### Pending Decisions — Stage 4

| Decision | Status |
|---|---|
| Daily loss limit value | Calibrate from Stage 3 paper trading data |
| Maximum open positions live | Target 10 — Stage 3 will inform |
| Pyramiding rules | Stage 4 backtesting required |
| Sector concentration limit live | Informed by Phase 1B concentration analysis |

---

---

## 20. Phase 1B Pre-Run Checklist

All items must be ✅ before Phase 1B runs. No exceptions.

| # | Item | Required |
|---|---|---|
| 1 | Quiver congressional | 509/509 tickers ✅ |
| 2 | Quiver insider | 509/509 tickers ✅ |
| 3 | Quiver institutional 13F | 509/509 tickers |
| 4 | Quiver gov_contracts | 509/509 tickers |
| 5 | Quiver lobbying | 509/509 tickers |
| 6 | Quiver wikipedia | 509/509 tickers |
| 7 | Quiver wallstreetbets | 509/509 tickers |
| 8 | Finnhub news sentiment | 509/509 tickers ✅ |
| 9 | FRED macro | Extended to March 2026 |
| 10 | OHLCV cache | Extended to March 2026 ✅ |
| 11 | AAII sentiment | Extended to March 2026 ✅ |
| 12 | CNN Fear & Greed | Extended to March 2026 ✅ |
| 13 | Agent cache cleared | Old 108 analyses with stale agents deleted |
| 14 | 25-ticker batch test | Agent outputs reviewed — qualitative + quantitative |
| 15 | Two-stage tiering validated | Confirm preliminary vs adjusted tier distribution |
| 16 | Sector ETF context | Passed to Technical Agent ✅ |

---

---

## 21. Website Design & Delivery

### What the Website Shows at Each Stage

| Stage | Website content |
|---|---|
| Stage 1 (current) | Daily top gainers from Alpha Vantage |
| Stage 2 | Analysis dashboards — local only |
| Stage 3 paper trading | Live screener candidates, confidence tiers, agent analysis, paper trade P&L |
| Stage 4 live trading | Full trade management — active positions, exits, P&L, historical performance |
| Stage 5 | Full institutional-grade dashboard |

### Stage 3 Website — Detailed Design

Static HTML/JS site updated daily via GitHub Actions. No server needed.

**Daily workflow:**
1. GitHub Actions cron job runs at 6am UTC
2. Screener runs on 509 instruments
3. Top candidates through 6-agent pipeline (Sonnet)
4. Results written to `site_picks/YYYY-MM-DD.json`
5. Website reads latest JSON and renders cards

**Site card per candidate:**
- Ticker, company, sector, price
- Confidence tier
- Strategies fired
- Entry price, position size %, stop level
- Days to earnings — flagged if < 14 days
- CNN Fear & Greed score
- Bull agent argument (2-3 sentences)
- Bear agent argument (2-3 sentences)
- Decision agent recommendation

**Paper trading tracker:**
- Open paper positions with P&L
- Trailing stop level
- Circuit breaker status
- All tiers tracked internally (not just published)

**Stage 3 — No email approval.** Fully automated. VERY HIGH and EXCEPTIONAL tiers auto-executed via Alpaca paper.

**Stage 4 email approval:** Every live trade requires APPROVE/REJECT reply within 30 minutes.

### Website Delivery Timeline

| Milestone | When |
|---|---|
| Analysis dashboards (1A, 1B) | ✅ Built — local use |
| Stage 3 screening website | After Phase 1D validates top strategies |
| Stage 3 paper trading tracker | Start of Stage 3 |
| Stage 4 live trading dashboard | After Stage 3 proves profitability |

---

---

## 22. API Role & Workflow Per Stage

### Stage 2 — Backtesting
| API | Role | Cost |
|---|---|---|
| yfinance | OHLCV historical — pre-fetched Parquet | Free |
| Quiver Trader | Congressional + insider + 13F + gov_contracts + lobbying + wikipedia + wsb | $75/mo |
| FRED | Macro series — pre-fetched | Free |
| Finnhub free | News sentiment — pre-fetched | Free |
| Anthropic Haiku | Phase 1B agents | ~$116 CAD |
| Anthropic Sonnet | Phase 1C/1D agents | ~$140 CAD |

**Unusual Whales + Ortex added in Phase 1C** — validates their contribution before live use.

### Stage 3 — Paper Trading
| API | Role | Cost |
|---|---|---|
| yfinance | Daily OHLCV | Free |
| Quiver Trader | Live SM signals | $75/mo |
| FRED | Live macro | Free |
| Finnhub free | Live news | Free |
| Unusual Whales | Options flow | ~$50/mo |
| Anthropic Sonnet | Daily agent pipeline | ~$25/mo |
| Alpaca paper | Auto execution | Free |

### Stage 4 — Live Trading
All Stage 3 APIs + Ortex ($40/mo) + Alpaca live. Total ~$190/mo.

---

---

## 23. Strategy Decay & Continuous Optimization

### The Problem
A strategy validated on 2022-2026 data may stop working in 2028.

### How We Handle It

**Phase structure:** Phase 1D validates on 5 years including COVID 2020. Walk-forward uses most recent data as OOS.

**Live trading monitoring:**
- Monthly performance review vs backtest expectations
- Strategy retirement: win rate drops >10pp below backtest for 3 consecutive months → retire
- Regime detection: VIX sustained >30 for 30+ days → re-evaluate strategy selection
- Annual re-backtest: run full Phase 1B-1D on extended data

**Re-validation triggers:**
- New market regime (VIX sustained >30 for 30+ days)
- Strategy underperforms backtest by >15pp for 2+ months
- Major market structure change
- Annual scheduled review

**Agent role in decay detection:**
- Risk agent explicitly flags when current regime differs from validation period
- Surfaces potential strategy decay before it shows in P&L

---

---

## 24. Best Practices & Open Source References

### Industry Best Practices Followed
- Point-in-time data enforcement
- Two-window walk-forward validation
- Hold-adjusted survivorship bias correction
- Realistic transaction cost modelling with minimum
- Entry AND exit slippage modelled
- Minimum OOS trade count (30) for ROBUST verdict
- Smart money lift with defined threshold (≥ 3pp)
- Macro correlation with defined threshold (≥ 5pp)
- 95% binomial confidence intervals on win rates
- Kelly criterion sanity check post-Phase 1B
- Sector-adjusted passing criteria
- Agent cache versioning — invalidate on prompt changes
- Batch test before scaling
- Backtests mirror live trading scenarios

### Currency Risk
All backtest and live trading returns are in USD. Portfolio is denominated in CAD.
USD/CAD exchange rate fluctuations affect actual CAD returns:
- USD strengthens 5% while holding US stock returning 10% → actual CAD return ~15%
- CAD strengthens 5% → actual CAD return ~5%

Phase 1B results are in USD. Stage 3+ performance tracked in both USD and CAD.
Currency hedging not implemented — documented as known exposure.

### Known Limitations vs Institutional Systems
- Daily bar data only — intraday stop precision limited
- Gap-down exits slightly optimistic (~0.1-0.3% on affected trades)
- No tick data — slippage model approximate
- Earnings surprise direction not modelled
- Sector contagion effects not modelled
- Regime detection is coincident/lagging — VIX spikes after market drops
- 2020 Phase 1D data lacks smart money context — flagged as limitation
- Congressional signal 60+ days old excluded — recency weighting applied

### Open Source Systems Evaluated
- **TradingAgents** — integrated as core 6-agent pipeline
- **NautilusTrader** — evaluated for Stage 4+ execution layer
- **Backtrader** — evaluated, replaced with custom engine for agent integration
- **QuantConnect** — evaluated, proprietary
- **Zipline** — considered, unmaintained

### Design Gaps — Post-Phase 1B Analysis
These are known gaps to be addressed with Phase 1B data:
- Kelly criterion vs current tier sizes
- Optimal VIX threshold for regime classification (let data determine, not round numbers)
- ATR 1.0× vs 0.5× entry zone comparison
- Sector concentration frequency and impact analysis
- EXCEPTIONAL tier trade count — if < 1%, tier needs redesign
- Short strategy validation for 2022 bear market