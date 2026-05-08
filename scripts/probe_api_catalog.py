"""scripts/probe_api_catalog.py - One-shot API endpoint catalog probe.

Authoritative method per CHECKLIST #76 column-(b): hit each documented
endpoint with one test call using our actual API key, capture HTTP
status + sample response schema. More authoritative than docs scraping
(which is currently 403/404 on most sites) because it directly verifies
tier access.

Outputs JSON report at API_ENDPOINT_PROBE_REPORT.json.

Usage: python scripts/probe_api_catalog.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
def _load_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
QUIVER_KEY = os.environ.get("QUIVER_API_KEY", "")
FRED_KEY = os.environ.get("FRED_API_KEY", "")
ALPHAVANTAGE_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "")
FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "")

TIMEOUT = 15
TEST_TICKER = "AAPL"
TEST_CIK = "0000320193"  # AAPL
TEST_DATE = "2025-01-15"


def probe(label: str, url: str, headers: dict | None = None,
          params: dict | None = None) -> dict:
    """Issue one GET; report status + sample response schema."""
    out: dict[str, Any] = {"label": label, "url": url}
    try:
        r = requests.get(url, headers=headers or {}, params=params or {},
                         timeout=TIMEOUT)
        out["status"] = r.status_code
        if r.status_code == 200:
            try:
                data = r.json()
                if isinstance(data, dict):
                    out["top_keys"] = list(data.keys())[:30]
                    # Look for results/data array structure
                    for k in ("results", "data", "observations", "items",
                              "tickers", "values"):
                        if k in data and isinstance(data[k], list) and data[k]:
                            sample = data[k][0]
                            if isinstance(sample, dict):
                                out["sample_record_keys"] = list(sample.keys())
                                break
                elif isinstance(data, list) and data:
                    sample = data[0]
                    if isinstance(sample, dict):
                        out["sample_record_keys"] = list(sample.keys())
                    out["count"] = len(data)
            except Exception as e:
                out["parse_error"] = str(e)[:80]
                out["preview"] = r.text[:200]
        else:
            out["preview"] = r.text[:200]
    except Exception as e:
        out["error"] = str(e)[:120]
    return out


def probe_polygon() -> list[dict]:
    """Probe Polygon (Massive) endpoints. Tries Stocks Starter (paid) +
    Indices/Options/Futures/Currencies Basic (free upgrades)."""
    base = "https://api.polygon.io"
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    results = []
    endpoints = [
        # Stocks (paid Starter — known working)
        ("stocks_aggs_daily", f"{base}/v2/aggs/ticker/AAPL/range/1/day/2025-01-01/2025-01-15", None),
        ("stocks_aggs_minute", f"{base}/v2/aggs/ticker/AAPL/range/1/minute/2025-01-15/2025-01-15", None),
        ("stocks_open_close", f"{base}/v1/open-close/AAPL/2025-01-15", None),
        ("stocks_grouped_daily", f"{base}/v2/aggs/grouped/locale/us/market/stocks/2025-01-15", None),
        ("stocks_previous_close", f"{base}/v2/aggs/ticker/AAPL/prev", None),
        # Reference
        ("ref_tickers", f"{base}/v3/reference/tickers", {"limit": 1}),
        ("ref_ticker_detail", f"{base}/v3/reference/tickers/AAPL", None),
        ("ref_ticker_types", f"{base}/v3/reference/tickers/types", None),
        ("ref_related", f"{base}/v1/related-companies/AAPL", None),
        ("ref_news", f"{base}/v2/reference/news", {"limit": 1}),
        ("ref_dividends", f"{base}/v3/reference/dividends", {"ticker": "AAPL", "limit": 1}),
        ("ref_splits", f"{base}/v3/reference/splits", {"ticker": "AAPL", "limit": 1}),
        ("ref_ipos", f"{base}/vX/reference/ipos", {"limit": 1}),
        ("ref_events", f"{base}/v3/reference/tickers/AAPL/events", None),
        ("ref_financials", f"{base}/vX/reference/financials", {"ticker": "AAPL", "limit": 1}),
        ("ref_short_interest", f"{base}/stocks/v1/short-interest/AAPL", None),
        ("ref_short_volume", f"{base}/stocks/v1/short-volume/AAPL", None),
        ("ref_conditions", f"{base}/v3/reference/conditions", {"limit": 1}),
        ("ref_exchanges", f"{base}/v3/reference/exchanges", None),
        ("ref_market_holidays", f"{base}/v1/marketstatus/upcoming", None),
        ("ref_market_status", f"{base}/v1/marketstatus/now", None),
        # Filings (Massive's structured SEC parsed)
        ("filings_10k_sections", f"{base}/stocks/v1/filings/10-k", {"ticker": "AAPL", "limit": 1}),
        ("filings_13f", f"{base}/stocks/v1/filings/13-f", {"ticker": "AAPL", "limit": 1}),
        ("filings_8k_text", f"{base}/stocks/v1/filings/8-k", {"ticker": "AAPL", "limit": 1}),
        ("filings_form3", f"{base}/stocks/v1/filings/form-3", {"ticker": "AAPL", "limit": 1}),
        ("filings_form4", f"{base}/stocks/v1/filings/form-4", {"ticker": "AAPL", "limit": 1}),
        ("filings_edgar_idx", f"{base}/stocks/v1/filings/edgar-index", {"ticker": "AAPL", "limit": 1}),
        ("filings_risk_categories", f"{base}/stocks/v1/filings/risk-categories", {"ticker": "AAPL"}),
        ("filings_risk_factors", f"{base}/stocks/v1/filings/risk-factors", {"ticker": "AAPL"}),
        # Fundamentals (Massive's structured)
        ("fund_balance_sheets", f"{base}/stocks/v1/fundamentals/balance-sheets", {"ticker": "AAPL", "limit": 1}),
        ("fund_cash_flow", f"{base}/stocks/v1/fundamentals/cash-flow", {"ticker": "AAPL", "limit": 1}),
        ("fund_income_statements", f"{base}/stocks/v1/fundamentals/income-statements", {"ticker": "AAPL", "limit": 1}),
        ("fund_ratios", f"{base}/stocks/v1/fundamentals/ratios", {"ticker": "AAPL", "limit": 1}),
        ("fund_float", f"{base}/stocks/v1/fundamentals/float", {"ticker": "AAPL"}),
        # Snapshots
        ("snap_full_market", f"{base}/v2/snapshot/locale/us/markets/stocks/tickers", {"limit": 1}),
        ("snap_single_ticker", f"{base}/v2/snapshot/locale/us/markets/stocks/tickers/AAPL", None),
        ("snap_top_movers", f"{base}/v2/snapshot/locale/us/markets/stocks/gainers", None),
        ("snap_unified", f"{base}/v3/snapshot", {"ticker.any_of": "AAPL"}),
        # Technical Indicators (Polygon precomputed)
        ("ind_sma", f"{base}/v1/indicators/sma/AAPL", {"timestamp": "2025-01-15", "timespan": "day", "window": 50, "series_type": "close"}),
        ("ind_ema", f"{base}/v1/indicators/ema/AAPL", {"timestamp": "2025-01-15", "timespan": "day", "window": 50, "series_type": "close"}),
        ("ind_rsi", f"{base}/v1/indicators/rsi/AAPL", {"timestamp": "2025-01-15", "timespan": "day", "window": 14, "series_type": "close"}),
        ("ind_macd", f"{base}/v1/indicators/macd/AAPL", {"timestamp": "2025-01-15", "timespan": "day", "series_type": "close"}),
        # Last Trade / Quote
        ("last_trade", f"{base}/v2/last/trade/AAPL", None),
        ("last_quote", f"{base}/v2/last/nbbo/AAPL", None),
        ("trades", f"{base}/v3/trades/AAPL", {"limit": 1}),
        ("quotes", f"{base}/v3/quotes/AAPL", {"limit": 1}),
        # Economy (Massive's macroeconomic)
        ("econ_inflation", f"{base}/fed/v1/inflation", None),
        ("econ_inflation_exp", f"{base}/fed/v1/inflation-expectations", None),
        ("econ_labor", f"{base}/fed/v1/labor", None),
        ("econ_treasury_yields", f"{base}/fed/v1/treasury-yields", None),
        # Indices Basic (free upgrade)
        ("idx_aggs_spx", f"{base}/v2/aggs/ticker/I:SPX/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_ndx", f"{base}/v2/aggs/ticker/I:NDX/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_dji", f"{base}/v2/aggs/ticker/I:DJI/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_rut", f"{base}/v2/aggs/ticker/I:RUT/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_vix", f"{base}/v2/aggs/ticker/I:VIX/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_vix9d", f"{base}/v2/aggs/ticker/I:VIX9D/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_vix3m", f"{base}/v2/aggs/ticker/I:VIX3M/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_vvix", f"{base}/v2/aggs/ticker/I:VVIX/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_aggs_oex", f"{base}/v2/aggs/ticker/I:OEX/range/1/day/2025-01-01/2025-01-15", None),
        ("idx_tickers_all", f"{base}/v3/reference/tickers", {"market": "indices", "limit": 1}),
        ("idx_snapshot", f"{base}/v3/snapshot/indices", {"ticker.any_of": "I:SPX"}),
        # Options Basic (free upgrade)
        ("opt_contracts", f"{base}/v3/reference/options/contracts", {"underlying_ticker": "AAPL", "limit": 1}),
        ("opt_aggs", f"{base}/v2/aggs/ticker/O:AAPL250117C00200000/range/1/day/2024-01-01/2025-01-15", None),
        ("opt_snapshot_chain", f"{base}/v3/snapshot/options/AAPL", None),
        ("opt_trades", f"{base}/v3/trades/O:AAPL250117C00200000", {"limit": 1}),
        ("opt_quotes", f"{base}/v3/quotes/O:AAPL250117C00200000", {"limit": 1}),
        # Futures Basic (free upgrade)
        ("fut_contracts", f"{base}/futures/v1/contracts", {"limit": 1}),
        ("fut_products", f"{base}/futures/v1/products", {"limit": 1}),
        ("fut_aggs_es", f"{base}/v2/aggs/ticker/ES/range/1/day/2025-01-01/2025-01-15", None),
        ("fut_aggs_vx", f"{base}/v2/aggs/ticker/VX/range/1/day/2025-01-01/2025-01-15", None),
        ("fut_schedules", f"{base}/futures/v1/schedules", {"limit": 1}),
        # Forex Basic (free upgrade)
        ("fx_aggs_eurusd", f"{base}/v2/aggs/ticker/C:EURUSD/range/1/day/2025-01-01/2025-01-15", None),
        ("fx_aggs_usdjpy", f"{base}/v2/aggs/ticker/C:USDJPY/range/1/day/2025-01-01/2025-01-15", None),
        ("fx_conversion", f"{base}/v1/conversion/USD/EUR", {"amount": 100}),
        ("fx_tickers_all", f"{base}/v3/reference/tickers", {"market": "fx", "limit": 1}),
        # Partner Data (likely paid — probe to confirm)
        ("benzinga_analyst", f"{base}/benzinga/v1/analyst-insights", {"ticker": "AAPL", "limit": 1}),
        ("etfglobal_constituents", f"{base}/etfg/v1/constituents", {"ticker": "SPY", "limit": 1}),
        ("tmx_corporate_events", f"{base}/tmx/v1/corporate-events", {"limit": 1}),
    ]
    for label, url, params in endpoints:
        results.append(probe(f"polygon.{label}", url, headers=h, params=params))
        time.sleep(0.1)
    return results


def probe_quiver() -> list[dict]:
    """Probe Quiver Trader endpoints — every documented + suspected endpoint."""
    base = "https://api.quiverquant.com/beta"
    h = {"Authorization": f"Token {QUIVER_KEY}"}
    results = []
    # historical (per-ticker)
    historical = [
        "congresstrading", "senatetrading", "housetrading", "govcontracts",
        "lobbying", "wikipedia", "wallstreetbets", "twitter", "patentmomentum",
        "appratings", "sec13fchanges", "insidertrading", "earningsbeats",
        "redditpoliticians", "reddittendies", "snptrend", "swaps", "googletrends",
        "linkedindata", "iposcalendar", "spacs", "optionsflow", "estimates",
    ]
    for ep in historical:
        url = f"{base}/historical/{ep}/AAPL"
        results.append(probe(f"quiver.historical.{ep}", url, headers=h))
        time.sleep(0.5)
    # live (per-ticker + bulk)
    live = [
        "insiders", "sec13f", "sec13fchanges", "offexchange", "topshareholders",
        "etfholdings", "corporatedonors", "patentmomentum", "quivernews",
        "wikipedia", "wallstreetbets", "twitter", "iposcalendar", "spacs",
    ]
    for ep in live:
        url = f"{base}/live/{ep}"
        params = {"ticker": "AAPL"}
        results.append(probe(f"quiver.live.{ep}", url, headers=h, params=params))
        time.sleep(0.5)
    # bulk (no ticker)
    bulk = [
        "bulk/congresstrading", "bulk/senatetrading", "bulk/housetrading",
        "bulk/insiders", "bulk/sec13f", "bulk/govcontracts", "bulk/lobbying",
        "bulk/wikipedia", "bulk/wallstreetbets", "bulk/twitter",
        "bulk/patentmomentum", "bulk/corporatedonors", "bulk/appratings",
    ]
    for ep in bulk:
        url = f"{base}/{ep}"
        results.append(probe(f"quiver.{ep.replace('/', '.')}", url, headers=h))
        time.sleep(0.5)
    return results


def probe_fred() -> list[dict]:
    """Probe FRED/ALFRED."""
    base = "https://api.stlouisfed.org/fred"
    base_alfred = "https://api.stlouisfed.org/fred"  # ALFRED uses same base + realtime params
    common = {"api_key": FRED_KEY, "file_type": "json"}
    results = []
    endpoints = [
        ("series", f"{base}/series", {"series_id": "VIXCLS", **common}),
        ("series_observations", f"{base}/series/observations", {"series_id": "VIXCLS", "limit": 1, **common}),
        ("series_categories", f"{base}/series/categories", {"series_id": "VIXCLS", **common}),
        ("series_release", f"{base}/series/release", {"series_id": "VIXCLS", **common}),
        ("series_search", f"{base}/series/search", {"search_text": "vix", "limit": 1, **common}),
        ("series_tags", f"{base}/series/tags", {"series_id": "VIXCLS", **common}),
        ("series_updates", f"{base}/series/updates", {"limit": 1, **common}),
        ("series_vintagedates", f"{base}/series/vintagedates", {"series_id": "VIXCLS", **common}),
        ("category", f"{base}/category", {"category_id": 32991, **common}),
        ("category_children", f"{base}/category/children", {"category_id": 32991, **common}),
        ("category_related", f"{base}/category/related", {"category_id": 32991, **common}),
        ("category_series", f"{base}/category/series", {"category_id": 32991, "limit": 1, **common}),
        ("category_tags", f"{base}/category/tags", {"category_id": 32991, **common}),
        ("category_related_tags", f"{base}/category/related_tags", {"category_id": 32991, "tag_names": "usa", **common}),
        ("release", f"{base}/release", {"release_id": 53, **common}),
        ("releases", f"{base}/releases", {"limit": 1, **common}),
        ("releases_dates", f"{base}/releases/dates", {"limit": 1, **common}),
        ("release_dates", f"{base}/release/dates", {"release_id": 53, **common}),
        ("release_series", f"{base}/release/series", {"release_id": 53, "limit": 1, **common}),
        ("release_sources", f"{base}/release/sources", {"release_id": 53, **common}),
        ("release_tags", f"{base}/release/tags", {"release_id": 53, **common}),
        ("source", f"{base}/source", {"source_id": 1, **common}),
        ("sources", f"{base}/sources", {"limit": 1, **common}),
        ("source_releases", f"{base}/source/releases", {"source_id": 1, "limit": 1, **common}),
        ("tags", f"{base}/tags", {"limit": 1, **common}),
        ("related_tags", f"{base}/related_tags", {"tag_names": "usa", "limit": 1, **common}),
        ("tags_series", f"{base}/tags/series", {"tag_names": "usa", "limit": 1, **common}),
        # ALFRED vintage
        ("alfred_observations_vintage", f"{base}/series/observations",
         {"series_id": "VIXCLS", "realtime_start": "2024-01-01",
          "realtime_end": "2024-01-31", "limit": 1, **common}),
    ]
    for label, url, params in endpoints:
        results.append(probe(f"fred.{label}", url, params=params))
        time.sleep(0.2)
    return results


def probe_finnhub() -> list[dict]:
    """Probe Finnhub free/premium endpoints."""
    base = "https://finnhub.io/api/v1"
    common = {"token": FINNHUB_KEY}
    results = []
    endpoints = [
        ("quote", f"{base}/quote", {"symbol": "AAPL", **common}),
        ("profile2", f"{base}/stock/profile2", {"symbol": "AAPL", **common}),
        ("peers", f"{base}/stock/peers", {"symbol": "AAPL", **common}),
        ("financials_reported", f"{base}/stock/financials-reported", {"symbol": "AAPL", **common}),
        ("financials", f"{base}/stock/metric", {"symbol": "AAPL", "metric": "all", **common}),
        ("insider_transactions", f"{base}/stock/insider-transactions", {"symbol": "AAPL", **common}),
        ("insider_sentiment", f"{base}/stock/insider-sentiment", {"symbol": "AAPL", "from": "2024-01-01", "to": "2024-12-31", **common}),
        ("recommendation", f"{base}/stock/recommendation", {"symbol": "AAPL", **common}),
        ("price_target", f"{base}/stock/price-target", {"symbol": "AAPL", **common}),
        ("upgrade_downgrade", f"{base}/stock/upgrade-downgrade", {"symbol": "AAPL", **common}),
        ("eps_surprise", f"{base}/stock/earnings", {"symbol": "AAPL", **common}),
        ("revenue_estimate", f"{base}/stock/revenue-estimate", {"symbol": "AAPL", **common}),
        ("eps_estimate", f"{base}/stock/eps-estimate", {"symbol": "AAPL", **common}),
        ("ebit_estimate", f"{base}/stock/ebit-estimate", {"symbol": "AAPL", **common}),
        ("ebitda_estimate", f"{base}/stock/ebitda-estimate", {"symbol": "AAPL", **common}),
        ("dividend", f"{base}/stock/dividend", {"symbol": "AAPL", "from": "2024-01-01", "to": "2024-12-31", **common}),
        ("split", f"{base}/stock/split", {"symbol": "AAPL", "from": "2020-01-01", "to": "2024-12-31", **common}),
        ("calendar_earnings", f"{base}/calendar/earnings", {"from": "2025-01-01", "to": "2025-01-31", **common}),
        ("calendar_ipo", f"{base}/calendar/ipo", {"from": "2025-01-01", "to": "2025-01-31", **common}),
        ("calendar_economic", f"{base}/calendar/economic", {"from": "2025-01-01", "to": "2025-01-31", **common}),
        ("news_general", f"{base}/news", {"category": "general", **common}),
        ("news_company", f"{base}/company-news", {"symbol": "AAPL", "from": "2025-01-01", "to": "2025-01-31", **common}),
        ("news_sentiment", f"{base}/news-sentiment", {"symbol": "AAPL", **common}),
        ("social_sentiment", f"{base}/stock/social-sentiment", {"symbol": "AAPL", **common}),
        ("scan_pattern", f"{base}/scan/pattern", {"symbol": "AAPL", "resolution": "D", **common}),
        ("scan_support_resistance", f"{base}/scan/support-resistance", {"symbol": "AAPL", "resolution": "D", **common}),
        ("forex_symbol", f"{base}/forex/symbol", {"exchange": "oanda", **common}),
        ("crypto_symbol", f"{base}/crypto/symbol", {"exchange": "binance", **common}),
        ("symbol_lookup", f"{base}/search", {"q": "apple", **common}),
        ("stock_symbol", f"{base}/stock/symbol", {"exchange": "US", **common}),
        ("ownership", f"{base}/stock/ownership", {"symbol": "AAPL", **common}),
        ("fund_ownership", f"{base}/stock/fund-ownership", {"symbol": "AAPL", **common}),
        ("etf_holdings", f"{base}/etf/holdings", {"symbol": "SPY", **common}),
        ("etf_country", f"{base}/etf/country", {"symbol": "SPY", **common}),
        ("etf_sector", f"{base}/etf/sector", {"symbol": "SPY", **common}),
        ("etf_industry", f"{base}/etf/industry", {"symbol": "SPY", **common}),
        ("indices_constituents", f"{base}/index/constituents", {"symbol": "^GSPC", **common}),
        ("indices_history", f"{base}/index/historical-constituents", {"symbol": "^GSPC", **common}),
    ]
    for label, url, params in endpoints:
        results.append(probe(f"finnhub.{label}", url, params=params))
        time.sleep(1.1)  # Free 60/min = 1/sec
    return results


def probe_sec_edgar() -> list[dict]:
    """Probe SEC EDGAR Data API endpoints (no key needed)."""
    h = {"User-Agent": "stock-picks-app probe@example.com"}
    results = []
    endpoints = [
        ("submissions", f"https://data.sec.gov/submissions/CIK{TEST_CIK}.json"),
        ("companyconcept_us_gaap_revenue",
         f"https://data.sec.gov/api/xbrl/companyconcept/CIK{TEST_CIK}/us-gaap/Revenues.json"),
        ("companyfacts", f"https://data.sec.gov/api/xbrl/companyfacts/CIK{TEST_CIK}.json"),
        ("frames_revenues",
         "https://data.sec.gov/api/xbrl/frames/us-gaap/Revenues/USD/CY2023Q4I.json"),
        ("efts_search",
         "https://efts.sec.gov/LATEST/search-index?q=%22Apple%22&dateRange=custom&startdt=2024-01-01&enddt=2024-01-31"),
    ]
    for label, url in endpoints:
        results.append(probe(f"sec.{label}", url, headers=h))
        time.sleep(0.2)  # SEC EDGAR rate limit: 10/sec
    return results


def main():
    print("Probing API catalogs...")
    all_results: dict[str, list[dict]] = {}

    if POLYGON_KEY:
        print("Polygon...")
        all_results["polygon"] = probe_polygon()
    else:
        print("(skip polygon — no key)")

    if QUIVER_KEY:
        print("Quiver...")
        all_results["quiver"] = probe_quiver()
    else:
        print("(skip quiver — no key)")

    if FRED_KEY:
        print("FRED...")
        all_results["fred"] = probe_fred()
    else:
        print("(skip fred — no key)")

    if FINNHUB_KEY:
        print("Finnhub...")
        all_results["finnhub"] = probe_finnhub()
    else:
        print("(skip finnhub — no key)")

    print("SEC EDGAR...")
    all_results["sec_edgar"] = probe_sec_edgar()

    out_path = Path("API_ENDPOINT_PROBE_REPORT.json")
    out_path.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\nProbe report: {out_path}")
    # Quick summary
    for src, rows in all_results.items():
        ok = sum(1 for r in rows if r.get("status") == 200)
        total = len(rows)
        print(f"  {src}: {ok}/{total} 200 OK")


if __name__ == "__main__":
    main()
