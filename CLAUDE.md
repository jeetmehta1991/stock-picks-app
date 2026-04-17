# Stock Picks & Automated Trading System

## Project Vision
Build a validated algorithmic trading system that evolves from a daily stock picks webpage to a fully automated trading engine for US (NYSE/NASDAQ) and Canadian (TSX) markets.

## Five Stage Roadmap

### Stage 1: Proof of Concept (Current)
- Static webpage showing daily top 5 US and top 5 TSX stock picks
- Data source: Alpha Vantage free tier
- Hosting: GitHub Pages
- Automation: GitHub Actions runs daily at 6am UTC
- Status: IN PROGRESS

### Stage 2: Strategy Validation
- Backtest 20+ indicator combinations on 3-5 years historical data
- Indicators: RSI, MACD, EMA crossovers, Bollinger Bands, Volume, Moving Averages
- Target: Find strategies with 55%+ win rate
- Tool: TradingAgents framework + backtesting.py
- Status: NOT STARTED

### Stage 3: Paper Trading
- Run validated strategies on live market with fake money
- Duration: Minimum 3-6 months
- Tool: Alpaca paper trading account
- Goal: Confirm backtested strategies work in real market conditions
- Status: NOT STARTED

### Stage 4: Live Trading Small Size
- Deploy with small real capital ($500-1000)
- Maximum 2% of capital per trade
- Human approval required for every trade
- Broker: Alpaca or Interactive Brokers Canada
- Status: NOT STARTED

### Stage 5: Fully Automated Trading
- System runs autonomously end to end
- Includes risk management, execution, monitoring, alerts
- Daily report sent via email or SMS
- Status: NOT STARTED

## Current Files
- fetch_stocks.py — fetches top 5 US and TSX stocks via Alpha Vantage, writes index.html
- .github/workflows/update_stocks.yml — runs fetch_stocks.py daily at 6am UTC
- index.html — dark themed webpage showing daily stock picks

## Tech Stack Evolution
- Now: Alpha Vantage, GitHub Pages, GitHub Actions
- Phase 2: TradingAgents, backtesting.py, historical data APIs
- Phase 3: Alpaca paper trading
- Phase 4: Alpaca live or Interactive Brokers Canada
- Phase 5: Polygon.io, Finnhub, Alpaca, Twilio SMS alerts

## Risk Management Rules (Stage 4+)
- Maximum 2% of capital per trade
- Maximum 5% daily loss limit
- Stop loss mandatory on every trade
- No more than 5 open positions at once
- Reduce position size after 3 consecutive losses

## APIs
- Alpha Vantage: free tier, 25 calls/day, stored as ALPHA_VANTAGE_KEY in GitHub Secrets
- Future: Polygon.io, Finnhub, Quandl, Alpaca, Interactive Brokers

## Coding Standards
- Python only
- All API keys stored as environment variables never in code
- Every script must have error handling and fallback messages
- All strategies must be backtested before going live
- Never skip paper trading before using real money
