# Stock Picks & Automated Trading System
### Project Plan & Technical Roadmap — Living Document
**Last updated:** April 2026 | **Version:** 6.0 | **Repo:** `jeetmehta1991/stock-picks-app`

---

## Quick Status
| Stage | Status | Notes |
|---|---|---|
| Stage 1 — Proof of Concept | ✅ Complete | Daily picks webpage live |
| Stage 2 Phase 1A | ✅ Complete | 67 instruments, Jan 2022–Mar 2026, 6,942 trades, 50/60 strategies fired |
| Stage 2 Phase 1B | 🔄 Pre-fetch running | 509 instruments, Jan 2022–Mar 2026, all data downloading |
| Stage 2 Phase 1C | ⏳ Pending | All strategies passing Phase 1B (max 30), Sonnet agents |
| Stage 2 Phase 1D | ⏳ Pending | All strategies passing Phase 1C, 5-year test incl. COVID 2020 |
| Stage 3 — Paper Trading | ⏳ Pending | Fully automated — 3-6 months minimum |
| Stage 4 — Live Small | ⏳ Pending | $500-1000 CAD, email approval every trade |
| Stage 5 — Full Automation | ⏳ Pending | Full API stack, no approval needed |

**Backtest period:** Jan 1 2022 — Mar 31 2026
**IS period:** Jan 2022 — Dec 2024 (3 years)
**OOS period:** Jan 2025 — Mar 2026 (15 months)
**Universe:** 509 instruments (482 S&P 500 + 27 sector/macro ETFs)

---

## 1. Vision

Build a validated algorithmic swing trading system that evolves from a daily stock picks webpage into a fully automated trading engine covering US markets. Every stage must be proven before progressing. No real money is risked until strategies are validated through rigorous backtesting across multiple market regimes and confirmed through paper trading.

> **Intraday trading is a completely separate future project. Nothing in this plan applies to it.**

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

## 3. Risk Profile

**Medium-high risk, high return focus.** Drawdowns are accepted as part of the strategy. ROI over time is the goal, not minimising short-term volatility. The system buys dips including in volatile and crisis markets — the trailing stop system manages downside without needing to predict the bottom.

**On VIX spikes:** High-VIX environments (VIX > 40) represent the best entry opportunities, not reasons to stop trading. Position size is reduced but entries are not blocked. Tightening stops during high volatility causes whipsawing — stops are not tightened.

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
- Finnhub news: all 509 tickers, 2025-2026 only (free tier 1-year lookback). 2022-2024 news unavailable on free tier. Upgrade to Finnhub paid ($50/mo) for full coverage in Phase 1C.

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
| Finnhub free | News sentiment — pre-fetched to Parquet | Free |
| Anthropic Haiku | Phase 1B agent pipeline | ~$116 CAD |
| Anthropic Sonnet | Phase 1C/1D agent pipeline | ~$140 CAD total |

**Phase 1B cost calculation:** 509 instruments × ~8 candidates/day average × 782 days × $0.00035/Haiku call × 6 agents = ~$116 CAD. Note: only candidates passing screener receive agents — not all instruments every day.

### Stage 3 — Paper trading (automated)
| API | Role | Cost |
|---|---|---|
| yfinance | Daily OHLCV for live screener | Free |
| Quiver Trader | Live congressional + insider + 13F signals | $75/mo |
| FRED | Live macro snapshot | Free |
| Finnhub free | Live news sentiment | Free |
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

## 14. Workflow — Making Changes

### Rule for Changes
No rule, filter, threshold, or strategy parameter is ever changed without explicit owner approval. Claude presents recommendations with reasoning and tradeoffs. Owner decides. Claude builds what is approved.

### GitHub Sync
1. Claude pushes changes to `claude-updates` branch
2. Owner triggers GitHub Actions → Sync from Claude → Run workflow
3. In Codespace: `git fetch origin ; git reset --hard origin/main`

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
