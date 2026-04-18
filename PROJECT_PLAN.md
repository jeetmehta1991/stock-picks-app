# Stock Picks & Automated Trading System
### Project Plan & Technical Roadmap — Living Document
**Last updated:** April 2026 | **Version:** 5.1 | **Repo:** `jeetmehta1991/stock-picks-app`

---

## Quick Status
| Stage | Status | Notes |
|---|---|---|
| Stage 1 — Proof of Concept | ✅ Complete | Daily picks webpage live |
| Stage 2 Phase 1A | 🔜 Running | 67 instruments, 3 years, rules finalised |
| Stage 2 Phase 1B | ⏳ Pending | ~400 instruments, awaiting 1A results |
| Stage 2 Phase 1C | ⏳ Pending | Top 20% strategies, Sonnet agents |
| Stage 2 Phase 1D | ⏳ Pending | Top 5 strategies, 5-year extended |
| Stage 3 — Paper Trading | ⏳ Pending | 3-6 months minimum |
| Stage 4 — Live Small | ⏳ Pending | $500-1000 CAD |
| Stage 5 — Full Automation | ⏳ Pending | Full API stack |

---

## 1. Vision

Build a validated algorithmic swing trading system that evolves from a daily stock picks webpage into a fully automated trading engine covering US markets. Every stage must be proven before progressing. No real money is risked until strategies are validated through rigorous backtesting across multiple market regimes and confirmed through paper trading.

> **Intraday trading is a completely separate future project.** Nothing in this plan applies to it.

---

## 2. Non-Negotiable Rules

- Never skip paper trading before real money
- 3 years minimum backtesting — no exceptions
- Point-in-time data enforcement — no future data ever used in backtesting
- Stop loss mandatory on every live trade from Stage 4 onwards
- Each stage must earn the right to advance to the next
- Any win rate >75% or profit factor >1.5 must be audited for look-ahead bias first
- No leveraged ETFs anywhere in the universe
- **Every rule, filter, threshold change requires explicit owner approval before implementation**
- Human email approval required for every live trade in Stage 4

---

## 3. Risk Profile

**Medium-high risk, high return focus.** Drawdowns are accepted as part of the strategy. ROI over time is the goal, not minimising short-term volatility. The system buys dips including in volatile and crisis markets — the trailing stop system manages downside without needing to predict the bottom.

---

## 4. Five Stage Roadmap

### Stage 1 — Proof of Concept ✅
Daily stock picks webpage. Top gainers for US (NYSE/NASDAQ) and Canadian (TSX) markets. Updated daily via GitHub Actions at 6am UTC. Zero cost.

**APIs:** Alpha Vantage free, GitHub Actions, GitHub Pages

---

### Stage 2 — Strategy Validation (Current)

#### Objective
Determine which of 60 strategies, across which market regimes, using which exit method, produce statistically valid trading edges. Zero money at risk.

#### Universe
| Phase | Instruments | Cost |
|---|---|---|
| 1A | SP50 + 17 ETFs = 67 | $0 |
| 1B | Filtered S&P 500 + all ETFs ≈ 400 | ~$116 CAD (Haiku agents) |
| 1C | Top 20% from 1B | ~$102 CAD (Sonnet) |
| 1D | Top 5 strategies, 5 years (incl. COVID 2020) | ~$38 CAD (Sonnet) |

#### 5 Market Regimes Tested
| Regime | Period | Condition |
|---|---|---|
| Bear correction | 2022 | S&P −19.4%, VIX 25+ |
| Rate rising | Mar 2022 – Jul 2023 | Fed 0.25% → 5.50% |
| Strong bull | 2023 | S&P +24.2% |
| Rate falling | 2024 | Fed cuts begin |
| AI sector bull | 2024 | Tech/AI driven |

#### 10 Passing Criteria (ALL required simultaneously)
| # | Metric | Threshold |
|---|---|---|
| 1 | Win rate | ≥ 55% |
| 2 | Profit factor | > 1.2 (flag if > 1.5) |
| 3 | Expected value | > 0 |
| 4 | Win/loss ratio | > 1.0 |
| 5 | Max drawdown | < 20% |
| 6 | Total ROI | > 0% |
| 7 | Smart money lift | Measurable improvement |
| 8 | Macro correlation | Higher win rate in favourable regime |
| 9 | Minimum trades | ≥ 100 (1A) / 500 Bonferroni-corrected (1B) |
| 10 | Regime coverage | Profitable in ≥ 2 of 5 regimes |

#### Stage 2 Success Criteria
- Minimum 3 strategies pass all 10 criteria in Phase 1B
- Walk-forward shows ROBUST on at least 2 strategies (passes 2022-23 AND 2024)
- At least 1 short strategy fires and passes during 2022 bear market
- Smart money lift measurable — strategies with congressional + insider outperform by ≥3pp
- No win rate >75% or PF >1.5 without clean look-ahead bias audit
- All 13 output files written cleanly

---

### Stage 3 — Paper Trading
**Duration:** 3-6 months minimum  
**Capital at risk:** Zero  
**Broker:** Alpaca paper trading (free)

#### Success Criteria
- Live win rate within 10pp of backtest win rate
- Live profit factor within 0.2 of backtest
- System runs reliably for 3+ months without crashes
- Email approval workflow confirmed working
- Minimum 50 paper trades completed

**Monthly cost:** ~$6 CAD (VPS only)

---

### Stage 4 — Live Trading Small
**Starting capital:** $500-1000 CAD maximum  
**Human approval:** Email approval required for every single trade

#### Risk Management Rules (Stage 4)
- Maximum position size: tiered by confidence (see below)
- Maximum 10 open positions simultaneously
- Reduce position size 50% after 3 consecutive losses
- Congressional and insider signals checked before every trade
- All 5 circuit breakers active at all times
- Daily loss limit: TBD (to be decided at Stage 4 based on paper trading data)

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

---

## 6. Exit System — 12 Methods Compared

**Primary exit:** Trailing stop at 10% below highest closing price. Moves up with price, never reverses.

**12 exit methods tested simultaneously** via composite score (40% ROI + 30% profit factor + 30% lowest drawdown):

| Exit | Logic |
|---|---|
| Trailing 10% | Primary confirmed exit |
| Trailing 5% | Tighter — faster exit |
| Trailing 15% | Looser — stays in longer |
| ATR trail 1× | Adapts to each stock's volatility |
| ATR trail 2× | More room on trending stocks |
| Fixed 3:1 target | 3× ATR profit / 2× ATR stop |
| Next pivot target | Exit at next R1/R2/R3 above entry |
| MA exit EMA-9 | Exit when price crosses below EMA-9 |
| Time stop 10d | Force exit day 10 |
| Time stop 20d | Force exit day 20 |
| Breakeven + trail | Move to breakeven at 1× ATR profit, then trail 10% |
| Hybrid 50% target | Take 50% off at 3× ATR, trail remainder |

**5 circuit breakers** override trailing stop (in priority order):
1. Overnight gap >12% wrong direction → exit at open
2. Earnings gap >8% wrong direction → exit at open
3. Intraday halt + down >15% from entry → exit on resume
4. S&P 500 market-wide halt → flag all, no new trades
5. VIX >40 → tighten stops to 5%, crisis flag added to trade

---

## 7. Confidence Tiers & Position Sizing

| Tier | Conditions | Position size | Published |
|---|---|---|---|
| EXCEPTIONAL | 3+ strategies + congressional + insider cluster | 5% of capital | Active picks |
| VERY HIGH | 2+ strategies + congressional OR insider | 4% of capital | Active picks |
| HIGH | 3+ strategies, no smart money | 3% of capital | Watchlist |
| MEDIUM-HIGH | 2 strategies, no smart money | 1.5% of capital | Watchlist |
| MEDIUM | 1 strategy + any smart money buy | 0% — watch only | Not published |
| LOW | 1 strategy only | 0% — watch only | Not published |
| AVOID | Congressional sell + insider cluster sell | 0% — avoid | Not published |

---

## 8. Engine Operating Rules (Backtest Mode)

### Approved rules — backtest only
| Rule | Value | Rationale |
|---|---|---|
| Open position cap | None — uncapped | Statistical validity requires all signals to fire |
| Trades per ticker per day | No limit — all strategies fire independently | Multiple signals on same ticker = multiple positions |
| Daily loss limit | None in backtest | Removed — to be decided at Stage 4 |
| Correlation filter | None in backtest | Sectors trend — targeting trending sectors is the strategy |
| Regime position sizing | None — full size in all regimes | Backtest needs data across all conditions |
| Regime direction hard block | None — all directions allowed in all regimes | Crisis = best entry prices. Flagged not blocked. |
| Crisis regime trades | Allowed. Flagged as `regime=crisis_CRISIS_FLAG` | Buy dips in volatile markets — trailing stop manages downside |
| Regime confidence scaling | None in backtest | Full size always |
| Max candidates per day | 10 | Enough signals per strategy for statistical validity |
| Entry zone ATR — mean reversion | 1.0× | Raised from 0.5× to capture more trades |
| Liquidity filter | Applied once at universe load | Not daily — stable universe for full 3-year run |

### Rules that remain active in all modes
| Rule | Value |
|---|---|
| Point-in-time data enforcement | Always — no future data ever |
| Entry zone ATR — breakout/momentum | 2.0× |
| Entry zone ATR — trend/confluence | 1.5× |
| Entry zone ATR — pivot/candle | 1.0× |
| Entry price | Next day open (D+1) |
| Slippage model | 0.03% ETF, 0.08% large-cap, 0.15% high-vol |
| Transaction costs | 0.08% ETF, 0.10% large-cap, 0.15% mid-cap round-trip |
| Survivorship bias haircut | 2% annual |
| Walk-forward validation | In-sample 2022-23, out-of-sample 2024 |
| Bonferroni correction | 60 strategies → 500 trade minimum |
| Look-ahead bias audit | Win rate >75% or PF >1.5 → flagged |

### Pending decisions (to be made at Stage 4 with live data)
- Daily loss limit value
- Maximum open positions for live trading
- Pyramiding rules (adding to winning positions)
- Sector concentration limits for live trading

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

---

## 10. Smart Money & Data Sources

| Source | Data | Cost | Key required |
|---|---|---|---|
| yfinance | OHLCV, analyst consensus, price targets, EPS estimates | $0 | No |
| FRED | Yield curve (T10Y2Y) | $0 | Optional free |
| yfinance ^VIX | VIX daily | $0 | No |
| Quiver Quantitative | Congressional trades, insider trades, 13F holdings, analyst revisions | $0 free tier | Yes — free |
| SEC EDGAR | Form 4, 13F backup | $0 | No |
| OpenInsider | Insider trades backup | $0 | No |
| AAII | Investor sentiment | $0 scraped | No |
| CNN Fear & Greed | Market sentiment | $0 scraped | No |

**Analyst data (yfinance):** Buy/hold/sell counts, avg price target, % upside, target range, EPS estimate next quarter, recent upgrades/downgrades, revision direction. **Informational only — does not affect confidence tier.**

**Smart money data lags enforced:**
- Congressional trades: 45-day disclosure lag
- Insider trades (Form 4): 2 business days
- 13F institutional: 45 days after quarter-end

---

## 11. API Stack by Stage

| Stage | APIs added | Monthly CAD |
|---|---|---|
| 1-2 (now) | yfinance, Alpha Vantage free, Quiver free, FRED, CBOE, FINRA, AAII, CNN | $0 |
| 3 (paper) | + Alpaca paper, Gmail SMTP, Anthropic Sonnet | ~$25 |
| 4 (live small) | + Alpaca live, Questrade/IBKR Canada | ~$85-120 |
| 5 (full) | + Quiver paid, Unusual Whales, Ortex, Finnhub, Polygon.io | ~$300-360 |

### Stage 5 Full API Stack
| API | Purpose | USD/month |
|---|---|---|
| Quiver Quantitative paid | Congressional, insider, 13F, analyst revisions, govt contracts | $50 |
| Unusual Whales | Options flow, dark pool, additional congressional tracking | $30 |
| Ortex | Short interest, days-to-cover, squeeze risk | $35 |
| Finnhub | Real-time news sentiment, earnings surprises, SEC filing alerts | $50 |
| Polygon.io | Tick-level prices, after-hours data | $29 |
| Anthropic Sonnet | Daily 6-agent pipeline for all candidates | ~$75 |
| Hetzner VPS | Application server 24/7 | $7 |
| PostgreSQL managed | Trade database with backups | $15 |
| Backblaze B2 | Backup storage | $1 |
| **Total** | | **~$292 USD (~$400 CAD)** |

---

## 12. How APIs Feed Into Confidence Tiers

| Tier | APIs contributing |
|---|---|
| EXCEPTIONAL | yfinance (technical) + Quiver (congressional buy) + Quiver/Unusual Whales (insider cluster buy) + Ortex (short interest check) |
| VERY HIGH | yfinance (technical) + Quiver (congressional OR insider buy) |
| HIGH | yfinance only |
| MEDIUM-HIGH | yfinance only |
| AVOID | Quiver (congressional sell) + Quiver/Unusual Whales (insider cluster sell) |

---

## 13. How APIs Feed Into the 6-Agent Pipeline

| Agent | Data sources | Output |
|---|---|---|
| Technical | yfinance OHLCV → 274 signals | Confirms all signals at exact historical date |
| Fundamental | Quiver (earnings, buybacks), Finnhub (news, SEC), yfinance (analyst consensus, EPS, price targets) | Earnings risk, analyst sentiment, fundamental backdrop |
| Sentiment | Quiver (congressional), Unusual Whales (options flow, dark pool), AAII, CNN Fear & Greed, Finnhub (news sentiment) | Market and stock-specific sentiment score |
| Risk | FRED (yield curve), yfinance (VIX), Ortex (short interest), economic calendar | Macro regime, short squeeze risk, event risk |
| Bull/Bear | All of the above | Structured debate — best and worst case for the trade |
| Decision | All agent outputs | Final confidence score, site card paragraph, optimal exit method |

---

## 14. Workflow — Making Changes

### GitHub sync workflow
1. Claude pushes changes to `claude-updates` branch
2. Owner triggers **GitHub → Actions → Sync from Claude → Run workflow**
3. Types description of what changed
4. Clicks Run (takes ~2 minutes)
5. In Codespace terminal: `git pull origin main`

### Rule for changes
**No rule, filter, threshold, or strategy parameter is ever changed without explicit owner approval.** Claude presents recommendations with reasoning and tradeoffs. Owner decides. Claude builds what is approved.

---

## 15. Infrastructure

### Current (Stage 2)
- GitHub Codespaces — development environment
- GitHub Actions — daily stock fetch + sync workflow
- GitHub Pages — static website hosting
- All free

### Stage 3 onwards
- Hetzner CX11 VPS ($6 USD/month) — always-on process runner
- PostgreSQL on VPS — trade persistence across restarts
- Gmail SMTP — email approval workflow
- devcontainer.json — auto-installs all dependencies on Codespace start
- Parquet cache — OHLCV data persists across sessions (committed to repo)

### Future (Stage 4+)
- Email approval: every live trade requires reply APPROVE or REJECT within 30 minutes
- No auto-execution without approval in Stage 4
- Stage 5: automated execution with email alerts for unusual position sizes only

---

## 16. Output Files

| File | Contents |
|---|---|
| `trade_log.csv` | Every trade with 40+ fields |
| `backtest_results.csv` | All strategies ranked by all 10 metrics |
| `backtest_report.html` | Dark-themed visual report |
| `winning_strategies.json` | Passing strategies with optimal exit method |
| `exit_strategy_comparison.csv` | All 12 exits × all strategies with composite scores |
| `exit_strategy_best.csv` | Best exit per strategy |
| `regime_performance.csv` | Win rate + ROI per strategy per regime |
| `walk_forward_validation.csv` | ROBUST / OVERFIT / WEAK / FAILS_BOTH per strategy |
| `improvements_summary.json` | Transaction costs, survivorship, walk-forward summary |
| `smart_money_combined.csv` | Win rate lift at each smart money score tier |
| `agent_performance.csv` | Win rate by confidence tier |
| `skipped_trades.csv` | All skipped entries with reason |
| `circuit_breaker_log.csv` | All circuit breaker triggers |
| `analysis_dashboard.html` | Interactive 9-tab analysis dashboard |

---

## 17. Current Phase 1A Results (April 18, 2026 — v1 run)

| Metric | Value | Notes |
|---|---|---|
| Trading days | 782 | Jan 2022 – Dec 2024 |
| Instruments | 66/67 | DIS data issue — non-critical |
| Trades closed | 198 | All long — no shorts fired |
| Strategies fired | 17/60 | 43 didn't fire with old 5-cand/day cap |
| Skipped trades | 9,974 | Gap filter + old correlation filter |
| Gross ROI | 780% | Before transaction costs |
| Net ROI | 742% | After 38.5% total transaction costs |
| Adjusted ROI | 736% | After 6% survivorship haircut |
| Passing all criteria | 0 | Expected — 100 trade minimum not met |

**Key findings:**
- Zero short trades — correct, short conditions are strict and 67 instruments is too few
- cpr_narrow_bullish fired 99 times — closest to 100-trade minimum
- Pipeline clean — all 13 output files written, no look-ahead bias detected

**Changes made before rerun (all owner-approved):**
- Removed open position cap
- Removed daily loss limit from backtest
- Removed correlation filter from backtest
- Removed regime position sizing from backtest
- Removed regime direction hard blocks — crisis trades flagged not blocked
- Removed one-trade-per-ticker-per-day limit
- Increased max candidates 5 → 10
- Mean reversion ATR multiplier 0.5× → 1.0×
- Liquidity filter applied once at load, not daily
- Position sizing: EXCEPTIONAL 5%, VERY HIGH 4%, HIGH 3%, MEDIUM-HIGH 1.5%

---

*This document is the single source of truth for the project. Updated directly on GitHub — no Word documents needed.*
