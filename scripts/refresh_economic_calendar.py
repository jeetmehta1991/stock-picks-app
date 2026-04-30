"""
scripts/refresh_economic_calendar.py — Refresh CPI/NFP/FOMC dates in
backtest/data/economic_calendar.json from official sources.

DEC-304 fix (Pass 50): the calendar was previously hardcoded with coverage
ending Q1 2026 — live trading after that date silently treated every day as
"no event nearby." This script extends coverage from official sources.

Sources:
  - FOMC: federalreserve.gov publishes annual calendars in JSON via
    https://www.federalreserve.gov/json/ne-meetings.json
  - CPI:  bls.gov publishes annual schedule at
    https://www.bls.gov/schedule/news_release/cpi.htm (HTML scrape)
  - NFP:  bls.gov publishes annual schedule at
    https://www.bls.gov/schedule/news_release/empsit.htm (HTML scrape)

Run from Codespace where outbound HTTPS is allowed:
    python scripts/refresh_economic_calendar.py

After running, commit backtest/data/economic_calendar.json.

Implementation notes:
  - This script is intentionally defensive: if any source fails, it preserves
    existing dates and only ADDS new ones (never deletes).
  - HTML scraping is brittle. If the BLS page format changes, the regex below
    will need updating. Prefer official iCal/RSS feeds when discovered.
  - Owner should re-run this annually (typically in November when BLS
    publishes the next year's schedule).
"""
import json
import logging
import re
import sys
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CALENDAR_PATH = Path(__file__).parent.parent / "backtest" / "data" / "economic_calendar.json"


def fetch_fomc_dates() -> list[str]:
    """Fetch FOMC meeting dates from Federal Reserve JSON feed.

    Note: the Fed publishes meeting dates as ranges (1-2 day meetings); we
    take the SECOND day of each meeting (when the rate decision is announced).
    """
    url = "https://www.federalreserve.gov/json/ne-meetings.json"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        dates = []
        # Schema (subject to change): {"meetings": [{"endDate": "MM/DD/YYYY", ...}]}
        for m in data.get("meetings", []):
            end_str = m.get("endDate") or m.get("end_date")
            if not end_str:
                continue
            try:
                # FOMC typically formats as "MM/DD/YYYY"
                parts = end_str.split("/")
                if len(parts) == 3:
                    mm, dd, yyyy = parts
                    dates.append(f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}")
            except (ValueError, IndexError):
                continue
        return sorted(set(dates))
    except Exception as exc:
        logger.warning("FOMC fetch failed: %s — preserving existing dates", exc)
        return []


def fetch_bls_dates(release_url: str) -> list[str]:
    """Scrape BLS schedule HTML page for release dates.

    BLS pages list release dates in YYYY-MM-DD format inside <td> cells.
    This regex picks up any ISO-formatted date on the page.
    """
    try:
        r = requests.get(release_url, timeout=15,
                         headers={"User-Agent": "stock-picks-app calendar refresh"})
        r.raise_for_status()
        # Match YYYY-MM-DD strings that look like release dates
        matches = re.findall(r"(20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))", r.text)
        return sorted(set(matches))
    except Exception as exc:
        logger.warning("BLS fetch %s failed: %s — preserving existing dates", release_url, exc)
        return []


def merge_dates(existing: list[str], new: list[str]) -> list[str]:
    """Union of two date-string lists, sorted."""
    return sorted(set(existing) | set(new))


def main():
    if not CALENDAR_PATH.exists():
        logger.error("Calendar JSON not found at %s. Run from project root.", CALENDAR_PATH)
        sys.exit(1)

    raw = json.loads(CALENDAR_PATH.read_text())
    logger.info("Existing: CPI=%d, NFP=%d, FOMC=%d",
                len(raw.get("CPI_DATES", [])),
                len(raw.get("NFP_DATES", [])),
                len(raw.get("FOMC_DATES", [])))

    new_fomc = fetch_fomc_dates()
    logger.info("Fetched FOMC: %d dates from federalreserve.gov", len(new_fomc))

    new_cpi = fetch_bls_dates("https://www.bls.gov/schedule/news_release/cpi.htm")
    logger.info("Fetched CPI: %d dates from bls.gov", len(new_cpi))

    new_nfp = fetch_bls_dates("https://www.bls.gov/schedule/news_release/empsit.htm")
    logger.info("Fetched NFP: %d dates from bls.gov", len(new_nfp))

    # Merge (additive — never remove existing dates)
    raw["CPI_DATES"]  = merge_dates(raw.get("CPI_DATES", []),  new_cpi)
    raw["NFP_DATES"]  = merge_dates(raw.get("NFP_DATES", []),  new_nfp)
    raw["FOMC_DATES"] = merge_dates(raw.get("FOMC_DATES", []), new_fomc)

    # Update metadata
    if "_metadata" not in raw:
        raw["_metadata"] = {}
    raw["_metadata"]["last_updated"] = date.today().isoformat()
    all_dates = raw["CPI_DATES"] + raw["NFP_DATES"] + raw["FOMC_DATES"]
    if all_dates:
        raw["_metadata"]["coverage_through"] = max(all_dates)

    CALENDAR_PATH.write_text(json.dumps(raw, indent=2))
    logger.info("Updated: CPI=%d, NFP=%d, FOMC=%d (latest: %s)",
                len(raw["CPI_DATES"]),
                len(raw["NFP_DATES"]),
                len(raw["FOMC_DATES"]),
                raw["_metadata"].get("coverage_through", "unknown"))
    logger.info("Wrote %s — commit this file to extend coverage in production.", CALENDAR_PATH)


if __name__ == "__main__":
    main()
