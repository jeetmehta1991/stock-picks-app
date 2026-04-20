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

---

## 18. All 60 Strategies — Plain English

Each strategy fires when ALL listed conditions are true simultaneously. Direction is either Long (buy) or Short (sell). Entry is always at next day's open price.

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
| Max candidates per day | 10 | How many instruments can generate new trades on any single day |
| Trades per ticker per day | No limit — all strategies fire independently | Multiple strategies on same ticker open separate positions. Removed to capture all valid signals |
| Entry price | Next day open (D+1) | Signal fires at market close. Entry at next morning's open. Simulates real execution. |
| Entry zone — breakout/momentum | Gap must be ≤ 2× ATR from signal close | Prevents entering too far above signal level — chasing |
| Entry zone — trend/confluence | Gap must be ≤ 1.5× ATR | Tighter — trend entries need to be closer to signal level |
| Entry zone — pivot/candle | Gap must be ≤ 1.0× ATR | Tightest — pivot level entries must be precise |
| Entry zone — mean reversion | Gap must be ≤ 1.0× ATR | Raised from 0.5× — captures more mean reversion trades |
| Slippage | 0.03% ETF / 0.08% large-cap / 0.15% high-vol | Applied at entry — realistic fill price vs official open |
| Minimum price history | 30 trading days | Instrument must have 30 days of data before signals are computed |

### Portfolio Rules (Backtest Mode)

| Rule | Current value | Rationale |
|---|---|---|
| Open position cap | None — uncapped | Statistical validity. All signals fire freely. |
| Daily loss limit | None | Removed for backtest. Will be decided at Stage 4 with live data. |
| Correlation filter | None | Removed. Sectors trend together — targeting trending sectors is the strategy. |
| Sector concentration | None | Removed with correlation filter. |
| Regime position sizing | None — full size in all regimes | Backtest needs data from all conditions, not reduced samples. |
| Crisis regime direction | Allowed — flagged as crisis_CRISIS_FLAG | Best entry prices are often in crisis. Trailing stop manages downside. |
| Liquidity filter | Applied once at load time | Price > $5, avg volume > 500k, market cap > $100M. Not re-checked daily. |

### Position Sizing by Confidence Tier

| Tier | Requirements | Size |
|---|---|---|
| EXCEPTIONAL | 3+ strategies + congressional buy + insider cluster buy | 5% of capital |
| VERY HIGH | 2+ strategies + congressional OR insider buy | 4% of capital |
| HIGH | 3+ strategies, no smart money | 3% of capital |
| MEDIUM-HIGH | 2 strategies, no smart money | 1.5% of capital |
| MEDIUM | 1 strategy + any smart money buy | 0% — watch only |
| LOW | 1 strategy only | 0% — watch only |
| AVOID | Congressional sell + insider cluster sell | 0% — avoid entirely |

### Exit Rules — Priority Order

| Priority | Rule | Trigger | Rationale |
|---|---|---|---|
| 1 — highest | Circuit breaker 1 | Overnight gap > 12% wrong direction → exit at open | Gap-down opens can blow through trailing stops |
| 2 | Circuit breaker 2 | Earnings gap > 8% wrong direction → exit at open | Earnings are binary events — can't be managed |
| 3 | Circuit breaker 3 | Intraday halt + down > 15% from entry → exit on resume | Halts often precede further decline |
| 4 | Circuit breaker 4 | S&P 500 market-wide halt → no new trades, flag all | Systemic risk — do not add exposure |
| 5 | Circuit breaker 5 | VIX > 40 → tighten all stops to 5%, no new longs | Crisis mode — protect capital |
| 6 — default | Trailing stop | 10% below highest closing price. Moves up, never reverses. | Primary exit for all strategies. Lets winners run. |

### Data Integrity Rules

| Rule | Value | Why non-negotiable |
|---|---|---|
| Point-in-time OHLCV | Every fetch sliced to as_of date only | Any future data = fictional results |
| Congressional trade lag | 45 days enforced | Real disclosure timeline |
| Insider trade lag | 2 business days | Real Form 4 filing timeline |
| 13F institutional lag | 45 days after quarter end | Real filing deadline |
| Analyst data | Live only — NOT used in backtest metrics | Cannot get historical analyst consensus from yfinance |
| Look-ahead bias guard | Automated check on every data fetch | Catches errors before they affect trades |
| Audit flag | Win rate > 75% or profit factor > 1.5 → manual review | Statistically unlikely without look-ahead bias |

### Improvements Applied to All Results

| Improvement | Value | Effect |
|---|---|---|
| Transaction costs | 0.08% ETF / 0.10% large-cap / 0.15% mid-cap round-trip | Reduces net ROI vs gross ROI |
| Survivorship bias haircut | 2% annual | Phase 1A: 6% total haircut over 3 years |
| Walk-forward validation | In-sample 2022-23 / Out-of-sample 2024 | ROBUST = real edge. OVERFIT = do not trade. |
| Bonferroni correction | 60 strategies → 500 trades minimum required | Prevents false positives from multiple testing |
| Slippage model | Spread + gap penalty at entry | Realistic fill prices |

### Pending Decisions — To Be Made at Stage 4

| Decision | Status |
|---|---|
| Daily loss limit value | To be determined from paper trading data |
| Maximum open positions for live trading | To be determined — Stage 3 cap 20, Stage 4 cap 10 |
| Pyramiding — adding to winning positions | Flagged for Stage 4 and separate backtesting |
| Sector concentration for live trading | To be determined |
| Multiple strategies on same ticker — separate positions or combined | **OPEN — needs owner decision before Phase 1A v3 run** |


---

## 20. TradingAgents Integration

### What it is
TradingAgents is a multi-agent AI framework integrated into our backtesting and live trading pipeline. Every candidate instrument passes through a 6-agent pipeline before receiving a confidence score and being published to the site card. It is not optional — it is the core intelligence layer that separates this system from a simple technical indicator screener.

The agents run in sequence, each analysing a different dimension of the trade. The Decision Agent synthesises all outputs into a final confidence score, position size recommendation, and plain-English site card paragraph.

### The 6-Agent Pipeline

| Agent | Model | Data sources | Output |
|---|---|---|---|
| Technical Agent | Haiku/Sonnet | yfinance OHLCV → 274 signals | Confirms all signals firing at exact historical date. Flags divergence. |
| Fundamental Agent | Haiku/Sonnet | Quiver (earnings, buybacks), Finnhub (news, SEC filings), yfinance (analyst consensus, EPS, price targets, revision direction) | Earnings risk, analyst sentiment, fundamental backdrop |
| Sentiment Agent | Haiku/Sonnet | Quiver (congressional), Unusual Whales (options flow, dark pool), AAII, CNN Fear & Greed, Finnhub (news sentiment) | Market and stock-specific sentiment score |
| Risk Agent | Haiku/Sonnet | FRED (yield curve), yfinance (VIX), Ortex (short interest), economic calendar | Macro regime score, short squeeze risk, earnings proximity, event risk |
| Bull Agent | Haiku/Sonnet | All of the above | Best case argument for the trade |
| Bear Agent | Haiku/Sonnet | All of the above | Worst case argument against the trade |
| Decision Agent | Haiku/Sonnet | All agent outputs | Final confidence score, position size, site card paragraph, optimal exit method |

### When Agents Run

| Phase | Agents | Model | Purpose |
|---|---|---|---|
| Phase 1A | No agents ( flag) | None | Pipeline validation only — zero cost |
| Phase 1B | Yes | Haiku (~/bin/sh.021/analysis) | Full universe backtest with agent confidence scoring |
| Phase 1C | Yes | Sonnet (~/bin/sh.08/analysis) | Higher quality validation — eliminates Haiku false positives |
| Phase 1D | Yes | Sonnet | Maximum conviction — top 5 strategies over 5 years |
| Stage 3 paper trading | Yes | Sonnet | Daily signal generation for paper trades |
| Stage 4+ live trading | Yes | Sonnet | Daily signal generation for live trades |

### The  Flag
Running with  skips the 6-agent pipeline entirely and uses rule-based confidence scoring instead. Used in Phase 1A to validate the pipeline at zero cost before spending on agents in Phase 1B.

### How Agent Output Feeds Into Confidence Tiers

The Decision Agent output directly determines the confidence tier assigned to each trade:

| Tier | Agent requirements |
|---|---|
| EXCEPTIONAL | 3+ technical strategies + congressional + insider cluster + agents agree |
| VERY HIGH | 2+ strategies + congressional OR insider + agents agree |
| HIGH | 3+ strategies, no smart money, agents positive |
| MEDIUM-HIGH | 2 strategies, agents neutral or positive |
| AVOID | Congressional sell + insider cluster sell regardless of agent output |

### Cost Per Analysis

| Model | Cost per analysis | Phase |
|---|---|---|
| Haiku | ~/bin/sh.021 | Phase 1B |
| Sonnet | ~/bin/sh.08 | Phase 1C, 1D, Stage 3+ |

Phase 1B cost estimate: 400 instruments × 782 days × 10 candidates × /bin/sh.021 = ~16 CAD
Phase 1C cost estimate: top 20% strategies × same universe × /bin/sh.08 = ~02 CAD
