# Stock Picks & Automated Trading System
## Project Plan — Complete Reference
**Last updated:** April 2026 | **Repo:** github.com/jeetmehta1991/stock-picks-app

---

## What This Project Is

This project builds an automated swing trading system for US equities from scratch. It starts as a simple stock picks webpage and evolves into a fully automated trading engine. Every stage is proven before money is risked, and every strategy is mathematically validated before being deployed live.

**Swing trading** means holding positions for days to weeks — not intraday. We buy when a stock shows multiple signals of strength and sell when the trailing stop triggers or the setup breaks down. We are not day traders.

**The core philosophy:** Find edges that have worked consistently across multiple market conditions. Validate them rigorously. Deploy them with strict risk management. Accept that drawdowns will happen and manage them, rather than trying to avoid them entirely.

---

## Current Status

| Stage | Status | What it means |
|---|---|---|
| Stage 1 — Daily stock picks | ✅ Complete | Live website showing top US and Canadian gainers |
| Stage 2 Phase 1A — Proof of concept | ✅ Complete | Tested 67 instruments across 4 years. Pipeline works. |
| Stage 2 Phase 1B — Full validation | 🔄 Data downloading | Testing all 509 instruments. Waiting on data. |
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
10. **Profitable in ≥ 2 of 7 regimes** — must work across multiple market conditions

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

### Before Phase 1B Runs (Blockers)
All Quiver data types must be complete (currently blocked by API outage — retry when recovered). Alpha Vantage news batches must complete (running overnight). 25-ticker batch test must be reviewed and agent outputs approved before scaling to 509 instruments.

### Phase 1C Additions
Unusual Whales options flow and Ortex short interest data are added in Phase 1C. This is intentional — we test their contribution in Phase 1C before committing to them in live trading.

### Stage 3 Design (When Phase 1D Completes)
- IBKR Canada paper trading account setup (Alpaca for US users; IBKR for Canadian)
- Daily screening cron job implementation
- Position persistence mechanism (PostgreSQL)
- Website with live paper trade tracking

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

### Known Limitations
- Daily bar data only — intraday stop precision limited
- Gap-down exits slightly optimistic (estimated 0.1-0.3% on affected trades)
- Earnings dates from yfinance not always point-in-time historical
- Sector contagion effects not explicitly modelled (AMD rallying when Intel beats)
- Regime detection is coincident/lagging — VIX spikes after market drops
- 2020 Phase 1D data lacks smart money context (Quiver history may not extend to 2020)

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

