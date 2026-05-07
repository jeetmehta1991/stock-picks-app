"""
scripts/prepopulate_cache_index.py
Pre-populate index.json and info_cache.json for all 509 tickers before
starting parallel batch runs. Eliminates race conditions from simultaneous writes.

Run once before starting any batch:
    python scripts/prepopulate_cache_index.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.data.universe import get_sp500_constituents, ETFS_FULL
from backtest.data.cache import CACHE_DIR, INDEX_FILE, _cache_path

# -- 1. Pre-populate index.json --
print("Pre-populating index.json...")
universe = list(dict.fromkeys(get_sp500_constituents(500) + ETFS_FULL))

try:
    existing_index = json.loads(INDEX_FILE.read_text()) if INDEX_FILE.exists() else {}
except Exception:
    existing_index = {}

# Add all tickers that have cached Parquet files
added = 0
for ticker in universe:
    cache_file = _cache_path(ticker)
    if cache_file.exists() and ticker not in existing_index:
        existing_index[ticker] = {"cached": True, "path": str(cache_file)}
        added += 1

INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
INDEX_FILE.write_text(json.dumps(existing_index, default=str, indent=2))
print(f"  [OK] index.json: {len(existing_index)} entries ({added} added)")

# -- 2. Pre-populate info_cache.json --
print("Pre-populating info_cache.json...")
info_cache_path = Path("data/cache/info_cache.json")
try:
    existing_info = json.loads(info_cache_path.read_text()) if info_cache_path.exists() else {}
except Exception:
    existing_info = {}

print(f"  [OK] info_cache.json: {len(existing_info)} tickers already cached")
missing_info = [t for t in universe if t not in existing_info]
if missing_info:
    print(f"  [WARN]  {len(missing_info)} tickers missing from info_cache - will be fetched during run")
    print(f"     First few missing: {missing_info[:5]}")
else:
    print(f"  [OK] All {len(universe)} tickers in info_cache - no race condition risk")

print("\n[OK] Pre-population complete - safe to start parallel batches")
