"""
scripts/prefetch_vix_dxy.py — Populate the OHLCV cache with real ^VIX and
DX-Y.NYB index data.

Why this exists (DEC-302, Pass 50):
The OHLCV cache currently only has VXX and UUP — futures-based ETF proxies
that don't accurately track ^VIX and DXY. macro.py was using these as
fallbacks, biasing regime classifications. macro.py now PREFERS real ^VIX
and DX-Y.NYB but falls back to the proxies with a warning if they aren't
cached. This script populates the real-index cache.

Run from Codespace (where yfinance network is allowed):
    python scripts/prefetch_vix_dxy.py

Then re-run any backtest — the warning will disappear and regime
classification will use actual VIX values.

Validation:
After running, check `python -c "import json; print(json.load(open('backtest/data/cache/index.json'))['^VIX'])"`
should show a populated entry with several years of rows.
"""
import logging
import sys
from datetime import date
from pathlib import Path

# Allow running from project root or scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.data.cache import get_ohlcv  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    # Match macro.py expectations: 2020-01-01 onwards
    start = date(2020, 1, 1)
    end   = date.today()

    targets = [
        ("^VIX",      "VIX volatility index (CBOE)"),
        ("DX-Y.NYB",  "DXY US Dollar Index (ICE)"),
    ]

    for ticker, description in targets:
        logger.info("Fetching %s — %s", ticker, description)
        df = get_ohlcv(ticker, start=start, end=end, force_refresh=False)
        if df.empty:
            logger.error(
                "  FAILED: yfinance returned empty for %s. "
                "Check network access and retry.", ticker,
            )
        else:
            logger.info(
                "  OK: %s cached, %d rows, %s → %s",
                ticker, len(df), df.index[0].date(), df.index[-1].date(),
            )

    logger.info(
        "Done. macro.py will now use real ^VIX/DX-Y.NYB values; "
        "VXX/UUP proxy fallback no longer needed."
    )


if __name__ == "__main__":
    main()
