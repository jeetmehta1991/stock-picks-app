#!/bin/bash
# Download full S&P 500 + ETF cache and commit to main
# Run with: bash scripts/download_cache.sh

set -e

echo "=== Cache Download Script ==="
echo "Pulling latest code..."
git pull origin main

echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages -q

echo "Starting download (~509 instruments, 25-35 mins)..."
python -c "
from backtest.data.universe import get_sp500_constituents, ETFS_FULL
from backtest.data.cache import get_ohlcv_bulk
from backtest.config import DATA_LOAD_START, BACKTEST_END
sp500 = get_sp500_constituents(500)
all_tickers = list(dict.fromkeys(sp500 + ETFS_FULL))
print(f'Downloading {len(all_tickers)} instruments...')
result = get_ohlcv_bulk(all_tickers, DATA_LOAD_START, BACKTEST_END)
print(f'Done: {len(result)} tickers cached')
"

echo "Committing to main..."
git add backtest/data/cache/
git commit -m "Cache: full S&P 500 + ETFs downloaded"
git push origin main

echo "=== Complete — data safe in repo ==="
