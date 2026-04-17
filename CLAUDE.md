# Stock Picks & Automated Trading System

## Project Vision
Build a validated algorithmic swing trading system evolving from a daily stock picks webpage to a fully automated trading engine covering US markets (S&P 200 + ETFs). Every stage must be proven before progressing. No real money risked until strategies are validated through rigorous backtesting across multiple market regimes and confirmed through paper trading.

## Five Stage Roadmap
- Stage 1: Proof of Concept — webpage live — COMPLETE
- Stage 2: Strategy Validation — backtest all signals, 55%+ win rate across regimes — NEXT
- Stage 3: Paper Trading — validate live with fake money — NOT STARTED
- Stage 4: Live Trading Small — $500-1000 CAD, human approval — NOT STARTED
- Stage 5: Full Automation — autonomous trading with risk management — NOT STARTED

## Current Files
- fetch_stocks.py — fetches top 5 US stocks via Alpha Vantage, writes index.html
- .github/workflows/update_stocks.yml — runs daily at 6am UTC
- index.html — live dark-themed webpage
- CLAUDE.md — this file

## Stage 2: Backtesting Engine

### Stock Universe
- S&P 200 (top 200 S&P 500 stocks by market cap)
- ETFs: SPY, QQQ, IWM, DIA, VTI, XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLU, XLB, XLRE, VXX, UVXY, TLT, HYG, LQD, GLD, SLV, USO, GDX, TQQQ, SQQQ, SPXL, EEM, EFA
- Total: ~235 instruments
- TSX excluded — add in future phase after US strategies validated

### Market Regimes To Cover (Non-Negotiable)
- Strong bull market (2023-2024)
- Bear market / correction (2022)
- High volatility / crisis (March 2020)
- Rate rising environment (2022-2023)
- Rate falling environment (2019, 2024)
- All regimes must be represented in backtest

### Three Pool Approach
- Pool 1: Backtesting Universe — 235 instruments, 3 years historical data
- Pool 2: Daily Screening — same 235 instruments scanned daily with liquidity filters
- Pool 3: Active Candidates — 50-200 instruments passing strategy filters per day

### Minimum Liquidity Filters
- Price above $5
- Average daily volume above 500,000 shares
- Listed minimum 1 year
- Market cap above $100M

### Complete Signal Universe

#### Category 1: Technical Indicators
Pivot & Price Levels: CPR (daily/weekly/monthly), Standard Pivots (R1/R2/R3, S1/S2/S3), Camarilla, Woodie's, Fibonacci Retracement (23.6/38.2/50/61.8/78.6%), Fibonacci Extensions, VWAP + deviation bands, Previous Day High/Low/Close
Momentum: RSI (9/14/21), Stochastic (fast/slow), Stochastic RSI, Williams %R, ROC, MACD (12/26/9 and 8/21/5), PPO, Awesome Oscillator, Ultimate Oscillator
Trend: EMA crossovers (9/21, 20/50, 50/200), SMA same, ADX, Parabolic SAR, Ichimoku Cloud (all 5), Supertrend, Hull MA, DEMA/TEMA
Volatility/Bands: Bollinger Bands (20,2 and 20,1.5 and 10,2), Keltner Channels, Donchian Channels, ATR + ATR stops, Squeeze Momentum (BB inside KC), Std dev bands, Envelope channels
Volume: OBV, Volume spike (2x/3x avg), VWAP deviation, A/D Line, Chaikin Money Flow, MFI, Force Index
Patterns: Inside/outside bar, Engulfing candles, Pin bars/hammer/shooting star, Morning/evening star, Cup and handle, Flag/pennant, Doji

#### Category 2: Smart Money Signals
Congressional Trades (STOCK Act): Quiver Quantitative free — 45-day disclosure, Senate stronger than House, defense/finance committee correlation, cluster buys strongest signal
Insider Trades (Form 4): OpenInsider + SEC EDGAR + Quiver free — 2-day disclosure, CEO discretionary buy strongest signal, cluster buying (3+ insiders 30 days) very strong, ignore options exercises and 10b5-1 plan sales
Institutional/Hedge Fund (13F/13D/13G): WhaleWisdom + SEC EDGAR + Quiver free — quarterly 13F filings, 13D activist crossing 5% very strong, multiple funds initiating same position strong
Short Interest: FINRA free — high short + positive catalyst = squeeze setup, declining short = bullish

#### Category 3: Options Intelligence
Put/Call ratio (CBOE free), IV rank for earnings strategy selection

#### Category 4: Macro Filters
Yield curve 2yr/10yr (FRED free), DXY (yfinance), VIX regime (yfinance), Economic calendar — avoid CPI/NFP/FOMC entries (FRED free), Fed rate direction

#### Category 5: Sentiment Signals
AAII sentiment survey (AAII.com free), CNN Fear & Greed (CNN free), COT report (CFTC.gov free), Reddit mentions (Quiver free)

#### Category 6: Company Signals
Analyst estimate revisions (Quiver free), analyst rating changes (Quiver free), share buybacks (SEC EDGAR free), dividend changes (yfinance)

### TradingAgents Integration — Combined Pipeline
Static indicators and agents work together — NOT separately.
Step 1: Technical indicators scan full universe — fast and free
Step 2: Smart money signals checked for flagged instruments
Step 3: Macro filters applied — yield curve, VIX, economic calendar
Step 4: Sentiment signals checked
Step 5: 50-100 candidates pass to TradingAgents
Step 6: TradingAgents deep analysis:
  - Technical Agent: confirms all indicators at exact historical date
  - Fundamental Agent: earnings risk, buybacks, analyst revisions, insider trades, 13F activity
  - Sentiment Agent: news, congressional trades, AAII, Fear/Greed, social
  - Risk Agent: yield curve, VIX, DXY, short interest, economic calendar
  - Bull/Bear Agents: debate full signal set
  - Decision Agent: final combined confidence score
Step 7: Final score = technical + smart money + macro + sentiment + agent confidence
Step 8: Highest scores published to webpage

### Agent-To-API Mapping
Technical Agent: yfinance + pandas-ta + Alpha Vantage free
Fundamental Agent: yfinance + OpenInsider + SEC EDGAR + WhaleWisdom + Quiver free
Sentiment Agent: Quiver free + Alpha Vantage News + AAII.com + CNN Markets
Risk Agent: FRED API + yfinance (DXY/VIX) + CBOE + FINRA + CFTC.gov
All APIs: $0 cost

### Complete Free API Stack
- yfinance: price, volume, fundamentals, dividends, splits (free, unlimited)
- pandas-ta: all technical indicator calculations
- Alpha Vantage free: real-time prices, earnings, news (25 calls/day)
- Quiver Quantitative free: congressional, insider, 13F, analyst revisions, Reddit
- SEC EDGAR: Form 4, 13D/13G, buyback filings
- OpenInsider: insider trades structured
- WhaleWisdom: 13F hedge fund filings
- Federal Reserve FRED API: yield curve, economic data
- CBOE website: put/call ratio
- FINRA: short interest
- AAII.com: weekly sentiment survey
- CNN Markets: Fear & Greed Index
- CFTC.gov: COT report
Total cost: $0

### Strategy Alignment Logic
Each instrument evaluated against ALL strategies independently.
Flagged when it aligns with ANY validated strategy.
Different stocks suit different strategies — no instrument must pass all strategies.
Confidence scoring:
- 3+ strategies + congressional + insider cluster buy + agents agree = EXCEPTIONAL
- 2+ strategies + congressional OR insider buy + agents agree = VERY HIGH
- 3+ strategies + no smart money = HIGH
- 2 strategies + no smart money = MEDIUM-HIGH
- 1 strategy + any smart money buy = MEDIUM
- 1 strategy only = LOW — watch list only
- Any + congressional sell + insider cluster sell = STRONG NEGATIVE — avoid

### AI Model Strategy
Haiku: ~$0.021/analysis — fast, good for volume scanning — Phases 1A and 1B
Sonnet: ~$0.08/analysis — significantly smarter, catches nuance — Phases 1C and 1D only

### Optimized Cost Model ($300 CAD budget)
Phase 1A: S&P 50 + 20 ETFs, FULL 3 years, Haiku — ~$30 CAD — pipeline validation across all regimes
Phase 1B: Full S&P 200 + all ETFs, 3 years, Haiku, batched by sector — ~$116 CAD — full universe backtest
Phase 1C: Top 20% strategies from 1B, 3 years, Sonnet — ~$102 CAD — quality validation
Phase 1D: Top 5 final strategies, extended to 5 years, Sonnet — ~$38 CAD — maximum regime coverage
Buffer: reruns and fixes — ~$20 CAD
Total: ~$306 CAD

IMPORTANT: Phase 1A uses FULL 3 YEARS on small universe — NOT 1 year. Single year = single market regime = invalid results.

### Phase 1B Sector Batching
Batch 1: Technology (~$15 CAD) → review → Batch 2: Financials (~$15) → review → Batch 3: Healthcare/Energy/Consumer (~$25) → review → Batch 4: ETFs (~$15) → review → Batch 5: Remaining S&P 200 (~$46)

### Phase Quality Gates
1A pass: zero look-ahead bias, point-in-time data confirmed, 100+ trades per strategy, pipeline clean
1B pass: 3+ strategies at 55%+ win rate, works across 2+ regimes, smart money shows measurable lift
1C pass: Sonnet confirms 2+ strategies, no hidden risks found
1D pass: top 5 maintain 55%+ over 5 years across all regimes — advance to Stage 3

### Data Integrity Rules — NON-NEGOTIABLE
POINT-IN-TIME ENFORCEMENT: Every API call during backtesting retrieves data as it existed on exact backtest date only. Never use any information not publicly available at that moment.
- Technical data: only OHLCV available at market close on backtest date
- Form 4 filings: only filings submitted on or before backtest date
- Congressional trades: only disclosures published on or before backtest date
- 13F filings: only filings available on backtest date — not future quarters
- All API calls must include strict date ceiling parameter

LOOK-AHEAD BIAS PREVENTION:
- Never use future information to make past decisions
- Example violation: using June 13F filing to make March trade decision
- Automated date ceiling check built into every API wrapper function
- Any backtest showing unusually high win rates must be audited for look-ahead bias first

### Backtesting Output Files
- backtest_results.csv — all strategies ranked by win rate, return, drawdown
- backtest_report.html — visual summary with charts per strategy and regime
- winning_strategies.json — strategies passing all criteria, ready for Stage 3
- congressional_correlation.csv — congressional signal analysis by chamber and committee
- insider_correlation.csv — insider signal analysis by type, size, cluster
- smart_money_combined.csv — win rate when multiple smart money signals align
- agent_performance.csv — win rate contribution by each TradingAgent
- regime_performance.csv — strategy performance by market regime

## Risk Management Rules (Stage 4+)
- Maximum 2% of capital per trade
- Maximum 5% daily loss limit — stop trading if hit
- Stop loss mandatory on every trade
- No more than 5 open positions at once
- Reduce position size after 3 consecutive losses
- Congressional and insider signals checked before every trade

## API Upgrade Path
- Stage 1-2: All free APIs listed above — $0
- Stage 3: Add Polygon.io + Finnhub — $78 USD/month
- Stage 4: Add Alpaca live + Interactive Brokers Canada — $88 USD/month
- Stage 5: Add Quiver API + Unusual Whales + Ortex + Twilio — $263 USD/month

## Coding Standards
- Python only
- All API keys in environment variables — never in code
- Every script must have error handling and fallback messages
- Point-in-time date ceiling enforced in every API wrapper
- All strategies backtested before going live
- Never skip paper trading before real money

## Non-Negotiable Rules
- Never skip paper trading before real money
- 3 years backtesting non-negotiable
- Phase 1A uses full 3 years even on small universe
- Point-in-time data enforcement — no future data ever used in backtesting decisions
- Maximum 2% capital per trade always
- Stop loss mandatory on every trade from Stage 4 onwards
- Each stage must earn the right to advance to the next
- Never use a single year for backtesting — always minimum 3 years
- Sector batch Phase 1B to preserve budget if early results are disappointing
- Smart money signals must align before maximum position size is deployed
- Congressional and insider signals checked before every live trade in Stage 4 and beyond
