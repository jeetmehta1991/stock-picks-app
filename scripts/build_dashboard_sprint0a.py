"""scripts/build_dashboard_sprint0a.py - Sprint 0A coverage dashboard data collector.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; one-shot data collector
for the Sprint 0A interactive HTML dashboard.

Walks every data_prefetch/* cache, reads parquet schemas, and produces a
snapshot JSON the dashboard can load.

Outputs:
  dashboard_sprint0a/data.json    -- structured snapshot
  dashboard_sprint0a/data.js      -- same data wrapped as JS const
  dashboard_sprint0a/last_run.txt -- timestamp marker

Run hourly via cron / Windows Scheduled Task / GitHub Actions:
  python scripts/build_dashboard_sprint0a.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

OUT_DIR = Path("dashboard_sprint0a")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATA_PREFETCH = Path("data_prefetch")
LEGACY_CACHE = Path("backtest/data/cache")
MASTER_UNIVERSE = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
INVENTORY_MD = Path("API_ENDPOINT_INVENTORY.md")


def parse_inventory_md(path: Path) -> list[dict]:
    """Parse API_ENDPOINT_INVENTORY.md tables into endpoint records.

    Per owner directive 2026-05-08: dashboard catalog source must be the
    inventory doc (canonical) NOT filesystem walks (memory). Each per-API
    section uses the standardized 5-column table:
        | Endpoint | Status | Sample fields | Currently cached? | Action |
    """
    import re
    text = path.read_text(encoding="utf-8")
    rows = []
    current_api = None
    in_table = False
    seen_header = False
    api_section_re = re.compile(r"^##\s+\d+\.\s+(.+?)(?:\s+\(.*)?$")
    for line in text.split("\n"):
        m = api_section_re.match(line)
        if m:
            api_label = m.group(1).strip()
            current_api = api_label
            in_table = False
            seen_header = False
            continue
        if not current_api:
            continue
        if line.startswith("|"):
            if "---" in line and "|---" in line.replace(" ", ""):
                in_table = True
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if not seen_header and cols and cols[0].lower() in ("endpoint", "endpoint path"):
                seen_header = True
                continue
            if in_table and len(cols) >= 5 and cols[0]:
                rows.append({
                    "api_label": current_api,
                    "endpoint_path": cols[0],
                    "status_raw": cols[1],
                    "sample_fields": cols[2],
                    "currently_cached": cols[3],
                    "action": cols[4],
                })
        else:
            if in_table and line.strip() == "":
                in_table = False
                seen_header = False
    return rows


# Inventory status emoji codepoints (chr() form - keeps file ASCII-pure
# per CHECKLIST #75 unicode-test).
_OK_MARK = chr(0x2705)         # check_mark
_RED_CIRCLE = chr(0x1F534)     # red_circle
_WARN_SIGN = chr(0x26A0)       # warning_sign
_QUESTION_MARK = chr(0x2753)   # question_mark
_EM_DASH = chr(0x2014)         # em-dash


def normalize_status(raw: str) -> str:
    """Map inventory status emoji/text to standard buckets."""
    if not raw:
        return "UNKNOWN"
    if _OK_MARK in raw:
        return "ACCESSIBLE"
    if _RED_CIRCLE in raw:
        if "404" in raw:
            return "DOES_NOT_EXIST"
        return "TIER_BLOCKED"
    if _WARN_SIGN in raw:
        return "PARTIAL"
    if _QUESTION_MARK in raw:
        return "UNPROBED"
    return "UNKNOWN"


def normalize_cached(raw: str):
    """Map 'Currently cached?' column to bucket + extract files count if present."""
    import re
    if not raw or raw.strip() in ("-", _EM_DASH):
        return ("NOT_CACHED", None)
    raw_l = raw.lower()
    if raw_l.startswith("no") and not raw_l.startswith("note"):
        return ("NOT_CACHED", None)
    m = re.search(r"(\d{1,7})\s*/", raw) or re.search(r"\((\d{1,7})", raw) or re.search(r"(\d{2,7})", raw)
    if "yes" in raw_l or _OK_MARK in raw or "in flight" in raw_l or "done" in raw_l:
        n = int(m.group(1)) if m else None
        return ("CACHED", n)
    return ("UNKNOWN", None)


def load_universe() -> pd.DataFrame:
    """Return Master Universe DataFrame with Symbol + resolved_tier columns."""
    if not MASTER_UNIVERSE.exists():
        return pd.DataFrame(columns=["Symbol", "resolved_tier", "Sector"])
    df = pd.read_csv(MASTER_UNIVERSE, comment="#")
    df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()
    return df


def scan_dir_files(dir_path: Path) -> dict[str, dict]:
    """Return {ticker: {file_size, row_count, columns, has_date_col, last_date}}
    for each .parquet in dir_path. Per-ticker shards only - skip _index/_checkpoint
    and global all.parquet."""
    out: dict[str, dict] = {}
    if not dir_path.exists():
        return out
    for parq in dir_path.glob("*.parquet"):
        stem = parq.stem
        if stem.startswith("_") or stem in ("all", "global", "index"):
            continue
        # Recover ticker from filename (strip safe-stem suffix)
        ticker = stem.replace("_", "-") if stem.endswith("_") and len(stem) > 1 else stem
        if stem.upper() in {"PRN_", "CON_", "AUX_", "NUL_"} or stem.upper().startswith(("COM", "LPT")) and stem.endswith("_"):
            ticker = stem.rstrip("_")
        try:
            file_size = parq.stat().st_size
        except Exception:
            file_size = 0
        try:
            df = pd.read_parquet(parq)
            row_count = len(df)
            columns = list(df.columns)
            # Find any date-like column
            date_cols = [c for c in columns if c.lower() in {"date", "time", "timestamp", "filing_date", "transactiondate", "report_date", "ex_dividend_date", "execution_date", "snapshot_date"}]
            last_date = None
            if date_cols and not df.empty:
                col = date_cols[0]
                try:
                    last_date = str(pd.to_datetime(df[col], errors="coerce").max().date())
                except Exception:
                    pass
        except Exception:
            row_count = 0
            columns = []
            last_date = None
        out[ticker.upper()] = {
            "file_size": file_size,
            "row_count": row_count,
            "columns": columns,
            "n_columns": len(columns),
            "last_date": last_date,
        }
    return out


def scan_global_file(path: Path) -> dict:
    """Single global parquet (e.g. quiver bulk). Return {row_count, columns, ...}."""
    if not path.exists():
        return {"present": False}
    try:
        df = pd.read_parquet(path)
        return {
            "present": True,
            "file_size": path.stat().st_size,
            "row_count": len(df),
            "columns": list(df.columns),
            "n_columns": len(df.columns),
        }
    except Exception:
        return {"present": False, "error": "read failed"}


# Realistic-max universe per endpoint family - used to compute
# "available coverage %" so endpoints capped by data-availability
# (e.g. SEC EDGAR ceiling = tickers with CIK; Polygon reference =
# tickers Polygon recognizes; Wikipedia = tickers with Wikipedia page)
# show as 100% when fully fetched against their realistic ceiling.
# None means "use raw 1937 universe" (default).
# Endpoint-level use-case + stage mapping (per owner directive 2026-05-08
# afternoon: "API usage and stage mapping, I need for each endpoint")
# Format: "{api}.{endpoint}" -> {use_case, stage, criticality}
ENDPOINT_USE_CASES = {
    # Polygon Stocks Starter
    "polygon.ohlcv": {"use_case": "Core daily OHLCV foundation for ALL strategies (Layer 1 baseline + layered roster ~108-133 classes per F-002)", "stage": "Phase 1A baseline", "criticality": "P0"},
    "polygon.news": {"use_case": "Per-ticker article-level news + per-ticker insights sentiment overlay (multi-ticker articles split correctly)", "stage": "Phase 1B sentiment overlay", "criticality": "P1"},
    "polygon.financials": {"use_case": "Quarterly financials (filing_date + period_of_report_date) for fundamentals strategies + value-tilt screening", "stage": "Phase 1B fundamental overlay", "criticality": "P1"},
    "polygon.events": {"use_case": "Ticker-change events for survivorship + symbology resolution", "stage": "Phase 1A backtest data integrity", "criticality": "P1"},
    "polygon.reference": {"use_case": "Sector / market_cap / SIC / IPO date reference (PIT for confidence_tier sizing + sector classification)", "stage": "Phase 1A baseline", "criticality": "P0"},
    "polygon.reference_extended": {"use_case": "Extended reference (FIGI cross-source ID, total_employees, description for LLM agents, address, branding)", "stage": "Phase 1B agent context", "criticality": "P2"},
    "polygon.dividends_full": {"use_case": "Full historical dividend events for dividend-yield strategies + ex-div date proximity signal", "stage": "Phase 1B+ overlay", "criticality": "P2"},
    "polygon.splits_full": {"use_case": "Full split history for OHLCV split-adjustment validation + post-split anomaly strategies", "stage": "Phase 1A data integrity", "criticality": "P1"},
    "polygon.ipos_full": {"use_case": "IPO calendar for T2 universe construction + post-IPO anomaly strategies", "stage": "Phase 1A T2 universe + Phase 1B overlay", "criticality": "P1"},
    # Polygon Indices Basic
    "polygon_indices.aggs": {"use_case": "Direct broad-market regime classification (NDX, COMP working; VIX/SPX/DJI/RUT license-gated)", "stage": "Phase 1A regime classifier (alt source)", "criticality": "P2"},
    # Polygon Forex Basic
    "polygon_forex.aggs": {"use_case": "Native FX pairs for DXY computation + risk-on/off via JPY/CHF/EM crosses", "stage": "Phase 1A regime + Phase 1B FX overlay", "criticality": "P1"},
    # Polygon Futures Basic
    "polygon_futures.aggs": {"use_case": "Term-structure signals (VX curve, treasury curve, contango/backwardation) - deferred per-contract dated logic", "stage": "Phase 1C+", "criticality": "P2"},
    # Polygon Economy
    "polygon_economy.inflation": {"use_case": "CPI alternative source (cross-check FRED CPIAUCSL)", "stage": "Phase 1A regime", "criticality": "P2"},
    "polygon_economy.inflation_expectations": {"use_case": "Forward inflation expectations (1y/5y/10y/30y models)", "stage": "Phase 1A regime", "criticality": "P1"},
    "polygon_economy.treasury_yields": {"use_case": "Treasury yields with daily granularity (alternative to FRED)", "stage": "Phase 1A regime", "criticality": "P1"},
    # Polygon Benzinga
    "polygon_benzinga.analyst_insights": {"use_case": "Per-analyst rating actions + price targets + insight reasoning", "stage": "Phase 1B agent overlay", "criticality": "P1"},
    "polygon_benzinga.ratings": {"use_case": "Analyst rating history (recommendation drift over time)", "stage": "Phase 1B agent overlay", "criticality": "P1"},
    "polygon_benzinga.earnings": {"use_case": "Earnings calendar + actual-vs-estimate surprise", "stage": "Phase 1B PEAD strategies", "criticality": "P1"},
    "polygon_benzinga.guidance": {"use_case": "Company forward guidance (raised/lowered/affirmed)", "stage": "Phase 1B post-guidance reaction", "criticality": "P1"},
    "polygon_benzinga.firm_details": {"use_case": "Analyst firm metadata (rank, accuracy track record)", "stage": "Phase 1B analyst-quality weighting", "criticality": "P2"},
    # Polygon Indicators
    "polygon_indicators.sma_50": {"use_case": "Cross-validation of locally-computed SMA50 vs Polygon precomputed", "stage": "Phase 1A signal validation", "criticality": "P2"},
    "polygon_indicators.sma_200": {"use_case": "Cross-validation of SMA200 + golden/death cross signals", "stage": "Phase 1A signal validation", "criticality": "P2"},
    "polygon_indicators.ema_20": {"use_case": "Cross-validation of EMA20 (short-term trend)", "stage": "Phase 1A signal validation", "criticality": "P2"},
    "polygon_indicators.ema_50": {"use_case": "Cross-validation of EMA50 (medium-term trend)", "stage": "Phase 1A signal validation", "criticality": "P2"},
    "polygon_indicators.rsi_14": {"use_case": "Cross-validation of RSI(14) momentum oscillator", "stage": "Phase 1A signal validation", "criticality": "P2"},
    "polygon_indicators.macd": {"use_case": "Cross-validation of MACD(12/26/9) trend-momentum", "stage": "Phase 1A signal validation", "criticality": "P2"},
    # Quiver Trader
    "quiver.congressional": {"use_case": "Congressional trade signals (smart_money composite); House+Senate aggregate", "stage": "Phase 1A baseline (smart_money)", "criticality": "P0"},
    "quiver.senatetrading": {"use_case": "Senate-only filing-trade signal (chamber-specific weighting)", "stage": "Phase 1B refined smart-money", "criticality": "P1"},
    "quiver.housetrading": {"use_case": "House-only filing-trade signal (chamber-specific weighting)", "stage": "Phase 1B refined smart-money", "criticality": "P1"},
    "quiver.spacs": {"use_case": "SPAC mention timeline (SPAC-specific universe + sentiment)", "stage": "Phase 1B SPAC overlay", "criticality": "P2"},
    "quiver.insider": {"use_case": "Per-ticker SEC Form 4 insider transactions (smart_money insider component)", "stage": "Phase 1A baseline", "criticality": "P0"},
    "quiver.institutional": {"use_case": "Per-ticker SEC 13F snapshots (smart_money institutional component)", "stage": "Phase 1A baseline", "criticality": "P0"},
    "quiver.gov_contracts": {"use_case": "Quarterly federal contract awards (Qtr+Year aggregate; daily-grain via USAspending pending)", "stage": "Phase 1A baseline", "criticality": "P1"},
    "quiver.lobbying": {"use_case": "Lobbying activity (issue-specific dollar amounts)", "stage": "Phase 1B lobbying overlay", "criticality": "P2"},
    "quiver.wallstreetbets": {"use_case": "WSB mention/sentiment time series (retail attention)", "stage": "Phase 1B retail overlay", "criticality": "P2"},
    "quiver.wikipedia_mirror": {"use_case": "DEPRECATED - use canonical wikipedia.pageviews instead", "stage": "DEPRECATED", "criticality": "skip"},
    "quiver.offexchange": {"use_case": "FINRA dark-pool short volume + dark-pool index (DPI) per ticker", "stage": "Phase 1B dark-pool overlay", "criticality": "P1"},
    "quiver.topshareholders": {"use_case": "Top 10 institutional shareholders snapshot (no PIT history)", "stage": "Phase 1B+ context (current snapshot)", "criticality": "P3"},
    "quiver.etfholdings": {"use_case": "Per-ticker ETF inclusion list + % weight (no PIT)", "stage": "Phase 1B ETF flow proxy", "criticality": "P2"},
    "quiver.patentmomentum_bulk": {"use_case": "Patent grant momentum (bulk; through 2022)", "stage": "Phase 1B+ innovation signal", "criticality": "P2"},
    "quiver.corporatedonors_bulk": {"use_case": "Corporate political donations (PIT cutoff via TransactionDate)", "stage": "Phase 1B+ political-bias overlay", "criticality": "P3"},
    "quiver.quivernews_bulk": {"use_case": "Quiver headline feed (general market news; not per-ticker)", "stage": "Phase 1B agent context", "criticality": "P3"},
    "quiver.sec13fchanges_bulk": {"use_case": "Quarterly 13F position changes (delta over time per fund x ticker)", "stage": "Phase 1A baseline (smart_money)", "criticality": "P0"},
    # SEC EDGAR
    "sec_edgar.10_K": {"use_case": "Annual report filing-event metadata (date + accession; line items via xbrl_companyfacts)", "stage": "Phase 1B fundamentals + filing-event overlay", "criticality": "P1"},
    "sec_edgar.10_Q": {"use_case": "Quarterly report filing-event metadata", "stage": "Phase 1B fundamentals + filing-event overlay", "criticality": "P1"},
    "sec_edgar.8_K": {"use_case": "Material event filings (acquisitions, results, officer changes) - catalyst signal", "stage": "Phase 1B catalyst-event overlay", "criticality": "P1"},
    "sec_edgar.form_4": {"use_case": "Insider transaction filings (SEC official; cross-validate Quiver insider)", "stage": "Phase 1B insider overlay", "criticality": "P1"},
    "sec_edgar.DEF_14A": {"use_case": "Proxy statement filings (governance + compensation context)", "stage": "Phase 1B+ governance overlay", "criticality": "P3"},
    "sec_edgar.S_1": {"use_case": "IPO registration filings (T2 universe pre-listing)", "stage": "Phase 1B+ IPO overlay", "criticality": "P3"},
    "sec_edgar.S_1_A": {"use_case": "IPO amendments", "stage": "Phase 1B+ IPO overlay", "criticality": "P3"},
    "sec_edgar.SC_13D": {"use_case": "Activist 5%+ holder filings (catalyst signal)", "stage": "Phase 1B+ activist overlay", "criticality": "P2"},
    "sec_edgar.SC_13D_A": {"use_case": "Activist holder amendments", "stage": "Phase 1B+ activist overlay", "criticality": "P2"},
    "sec_edgar.SC_13G": {"use_case": "Passive 5%+ holder filings", "stage": "Phase 1B+ ownership overlay", "criticality": "P2"},
    "sec_edgar.SC_13G_A": {"use_case": "Passive holder amendments", "stage": "Phase 1B+ ownership overlay", "criticality": "P2"},
    "sec_edgar.xbrl_companyfacts": {"use_case": "STRUCTURED financial line items (revenue/EPS/cash flow as time series; replaces Polygon Stocks Plus Filings + Fundamentals)", "stage": "Phase 1B fundamentals overlay", "criticality": "P0"},
    # FRED / ALFRED
    "fred.observations": {"use_case": "90+ macro series (yield curve / inflation / employment / sector employment / FX rates) for regime classification", "stage": "Phase 1A regime classifier", "criticality": "P0"},
    "alfred.vintage_observations": {"use_case": "Revision-aware FRED data (PIT-correct macro replay)", "stage": "Phase 1C+ revision-aware backtest", "criticality": "P3"},
    # AAII / CNN F&G
    "aaii.weekly_sentiment": {"use_case": "AAII weekly bullish/bearish % (contrarian signal at extremes)", "stage": "Phase 1A regime classifier", "criticality": "P1"},
    "cnn_fg.daily": {"use_case": "CNN F&G composite + 7 sub-components (VIX/breadth/momentum/etc.)", "stage": "Phase 1A regime classifier", "criticality": "P1"},
    # CFTC
    "cftc.tff_disagg_combined": {"use_case": "Trader-in-Financial-Futures + Disaggregated commodity positioning (latest combined)", "stage": "Phase 1A regime + Phase 1B positioning overlay", "criticality": "P1"},
    "cftc.extended": {"use_case": "Legacy + supplemental CFTC datasets (futures-only, supplemental CIT)", "stage": "Phase 1B positioning overlay", "criticality": "P2"},
    # Apewisdom / Wikipedia / pytrends
    "apewisdom.global": {"use_case": "Top-trending stocks across all subreddits (snapshot, forward-only)", "stage": "Phase 1B retail overlay", "criticality": "P2"},
    "apewisdom.subreddits": {"use_case": "Subreddit-specific timelines (WSB / stocks / investing / options / etc.)", "stage": "Phase 1B retail overlay", "criticality": "P2"},
    "wikipedia.pageviews": {"use_case": "Per-ticker Wikipedia daily pageviews (attention spike signal)", "stage": "Phase 1B+ attention overlay", "criticality": "P2"},
    "pytrends.interest_over_time": {"use_case": "Per-ticker Google Trends search-volume index (search-attention signal)", "stage": "Phase 1B+ attention overlay", "criticality": "P2"},
    # Finnhub
    "finnhub.quote": {"use_case": "Real-time delayed quote (current price snapshot)", "stage": "Phase 1B context (delayed)", "criticality": "P3"},
    "finnhub.profile2": {"use_case": "Company profile (industry classification cross-source vs Polygon)", "stage": "Phase 1A reference cross-check", "criticality": "P3"},
    "finnhub.peers": {"use_case": "Per-ticker peer companies (sector-relative strategies)", "stage": "Phase 1B sector-relative overlay", "criticality": "P2"},
    "finnhub.insider_transactions": {"use_case": "Insider transactions (cross-source vs Quiver insider + SEC Form 4)", "stage": "Phase 1B insider overlay", "criticality": "P1"},
    "finnhub.insider_sentiment": {"use_case": "Finnhub-derived insider sentiment composite (mspr score)", "stage": "Phase 1B insider sentiment overlay", "criticality": "P1"},
    "finnhub.recommendation": {"use_case": "Analyst recommendation distribution (buy/hold/sell counts over time)", "stage": "Phase 1B agent overlay", "criticality": "P1"},
    "finnhub.earnings": {"use_case": "EPS surprise time series (PEAD signal)", "stage": "Phase 1B PEAD strategies", "criticality": "P1"},
    "finnhub.company_news": {"use_case": "Per-ticker company news (cross-source confirm vs Polygon news)", "stage": "Phase 1B sentiment overlay", "criticality": "P2"},
    "finnhub.financials_reported": {"use_case": "Reported financial statements (cross-source vs SEC XBRL)", "stage": "Phase 1B fundamentals overlay", "criticality": "P2"},
    "finnhub.metric": {"use_case": "Per-ticker financial ratios (PE/PB/ROE/etc.)", "stage": "Phase 1B fundamental ratios", "criticality": "P1"},
    "finnhub.calendar_earnings": {"use_case": "Forward earnings calendar (days_to_earnings cube dim)", "stage": "Phase 1A days-to-earnings", "criticality": "P0"},
    "finnhub.calendar_ipo": {"use_case": "Forward IPO calendar (T2 universe maintenance)", "stage": "Phase 1A T2 universe", "criticality": "P1"},
    "finnhub.calendar_economic": {"use_case": "Economic event calendar (FOMC/CPI/NFP scheduling)", "stage": "Phase 1A days-to-event signal", "criticality": "P1"},
}


# API-level use-case + stage mapping (legacy; kept for backwards-compat)
API_USE_CASES = {
    "polygon": {
        "use_case": "Core OHLCV for all Layer 1 baseline + layered roster (~108-133 classes per F-002); news sentiment overlay; fundamentals; corporate actions; reference/sector/market_cap PIT",
        "stage": "Phase 1A baseline",
        "criticality": "P0",
    },
    "polygon_indices": {
        "use_case": "Cross-validation of broad-market regime vs ETF proxies (NDX, COMP working; VIX/SPX gated by license)",
        "stage": "Phase 1A regime classifier (alt source)",
        "criticality": "P2",
    },
    "polygon_options": {
        "use_case": "Put/call ratio, IV surface, options chain, unusual activity signals",
        "stage": "Phase 1A: chain-reference cache (H10 ep1 IN PROGRESS owner-approved 2026-05-08). Phase 1B+ overlay: per-contract OHLCV (ep2) DEFERRED to on-demand fetch per owner 2026-05-08 to avoid 100GB+ precompute.",
        "criticality": "P1",
    },
    "polygon_futures": {
        "use_case": "Term-structure signals (VX curve, treasury curve, commodity contango/backwardation)",
        "stage": "Phase 1C+",
        "criticality": "P2",
    },
    "polygon_forex": {
        "use_case": "Native DXY computation; risk-on/off proxies via JPY/CHF; EM currency stress",
        "stage": "Phase 1A regime + Phase 1B FX overlay",
        "criticality": "P1",
    },
    "polygon_economy": {
        "use_case": "Macro regime classification (CPI/treasury yields/inflation expectations)",
        "stage": "Phase 1A regime classifier",
        "criticality": "P1",
    },
    "polygon_benzinga": {
        "use_case": "Analyst momentum (ratings + price targets); earnings guidance reaction; consensus drift",
        "stage": "Phase 1B agent overlay",
        "criticality": "P1",
    },
    "polygon_indicators": {
        "use_case": "Cross-validation of locally-computed technicals (SMA/EMA/RSI/MACD)",
        "stage": "Phase 1A signal validation",
        "criticality": "P2",
    },
    "quiver": {
        "use_case": "Smart-money composite signal (congress/senate/house/insider/sec13f); retail attention (WSB/SPACs); off-exchange dark-pool flow; ETF flows",
        "stage": "Phase 1A baseline (smart_money composite) + Phase 1B+ overlays",
        "criticality": "P0",
    },
    "fred": {
        "use_case": "90+ macro series for regime classifier; yield curve; inflation; employment; sector employment; FX rates",
        "stage": "Phase 1A regime classifier",
        "criticality": "P0",
    },
    "alfred": {
        "use_case": "Vintage data for revision-aware backtesting (PIT-correct macro replay)",
        "stage": "Phase 1C+ revision-aware",
        "criticality": "P3",
    },
    "sec_edgar": {
        "use_case": "Structured fundamentals (XBRL companyfacts); filing-event signals (8-K material events; insider Form 4); 13D/G activist holdings",
        "stage": "Phase 1B fundamental overlay + Phase 1B+ filing-event overlay",
        "criticality": "P1",
    },
    "finnhub": {
        "use_case": "Cross-source confirm; analyst recommendations; insider sentiment; earnings/IPO/economic calendars; company news",
        "stage": "Phase 1B overlay",
        "criticality": "P1",
    },
    "alphavantage": {
        "use_case": "Cross-source confirm of free-tier technical indicators + listing status (premium endpoints inaccessible)",
        "stage": "Phase 1A signal validation (limited)",
        "criticality": "P3",
    },
    "cftc": {
        "use_case": "Speculator vs commercial positioning across financial + commodity futures",
        "stage": "Phase 1A regime + Phase 1B positioning overlay",
        "criticality": "P1",
    },
    "apewisdom": {
        "use_case": "Retail attention signal across 8 subreddits (WSB, options, investing, etc.)",
        "stage": "Phase 1B retail-overlay",
        "criticality": "P2",
    },
    "pytrends": {
        "use_case": "Search-attention signal (per-ticker SVI; geographic dimension; related queries)",
        "stage": "DEFERRED to Phase 1C per owner 2026-05-08. Apewisdom (already cached, 8 subreddits) covers ~90% of retail-attention signal at zero incremental cost. Pytrends needs paid proxy/SerpAPI to bypass Google 429.",
        "criticality": "P3 (deferred)",
    },
    "aaii": {
        "use_case": "Weekly investor sentiment survey (bullish/bearish %; contrarian signal)",
        "stage": "Phase 1A regime classifier - STATUS QUO confirmed owner 2026-05-08 (5-col weekly file sufficient; 8-week MA + long-term comparison computable locally; AAII Asset Allocation Survey optional ~30 min add).",
        "criticality": "P1",
    },
    "cnn_fg": {
        "use_case": "Composite sentiment + 7 sub-components (VIX/breadth/momentum/etc.)",
        "stage": "Phase 1A regime classifier",
        "criticality": "P1",
    },
    "wikipedia": {
        "use_case": "Page-view attention proxy (spike-detection signal)",
        "stage": "Phase 1B+ overlay",
        "criticality": "P3",
    },
    "usaspending": {
        "use_case": "Daily-grain federal contract awards (alternate to Quiver govcontracts quarterly aggregate; INV-024 fix)",
        "stage": "Phase 1B+ smart-money overlay",
        "criticality": "P2",
    },
}


EXPECTED_MAX = {
    # SEC EDGAR / XBRL - capped by CIK-map availability
    "sec_edgar.10_K": 1686,
    "sec_edgar.10_Q": 1686,
    "sec_edgar.8_K": 1686,
    "sec_edgar.form_4": 1686,
    "sec_edgar.DEF_14A": 1686,
    "sec_edgar.S_1": 1686,
    "sec_edgar.S_1_A": 1686,
    "sec_edgar.SC_13D": 1686,
    "sec_edgar.SC_13D_A": 1686,
    "sec_edgar.SC_13G": 1686,
    "sec_edgar.SC_13G_A": 1686,
    "sec_edgar.xbrl_companyfacts": 1686,
    # Polygon reference - capped by delisted tickers (251 not in Polygon)
    "polygon.reference": 1686,
    "polygon.reference_extended": 1686,
    "polygon.financials": 1686,
    "polygon.events": 1686,
    "polygon.dividends_full": 1686,
    "polygon.splits_full": 1686,
    "polygon.ipos_full": 1686,
    # Polygon news - same delisted ceiling
    "polygon.news": 1686,
    # Polygon indicators - Polygon-recognized only
    "polygon_indicators.sma_50": 1686,
    "polygon_indicators.sma_200": 1686,
    "polygon_indicators.ema_20": 1686,
    "polygon_indicators.ema_50": 1686,
    "polygon_indicators.rsi_14": 1686,
    "polygon_indicators.macd": 1686,
    # Polygon Benzinga - paid partner data, US listings only
    "polygon_benzinga.analyst_insights": 1686,
    "polygon_benzinga.ratings": 1686,
    "polygon_benzinga.earnings": 1686,
    "polygon_benzinga.guidance": 1686,
    "polygon_benzinga.firm_details": 1686,
    # Wikipedia - only tickers with a public Wikipedia page (~1414 max observed)
    "wikipedia.pageviews": 1414,
    # pytrends - Google Trends has-data ceiling (~1417 observed)
    "pytrends.interest_over_time": 1417,
    # Finnhub - same delisted ceiling
    "finnhub.quote": 1686,
    "finnhub.profile2": 1686,
    "finnhub.peers": 1686,
    "finnhub.insider_transactions": 1686,
    "finnhub.insider_sentiment": 1686,
    "finnhub.recommendation": 1686,
    "finnhub.earnings": 1686,
    "finnhub.company_news": 1686,
    "finnhub.financials_reported": 1686,
    "finnhub.metric": 1686,
    # Quiver - covers full Master Universe; default 1937
}


# Per-ticker endpoint definitions
# (api, endpoint_label, dir_path, type='per_ticker' or 'global')
ENDPOINTS = [
    # Polygon Stocks Starter
    ("polygon", "ohlcv", "backtest/data/cache/ohlcv", "per_ticker"),
    ("polygon", "news", "data_prefetch/polygon/news", "per_ticker"),
    ("polygon", "financials", "data_prefetch/polygon/financials", "per_ticker"),
    ("polygon", "events", "data_prefetch/polygon/events", "per_ticker"),
    ("polygon", "reference", "data_prefetch/polygon/reference", "per_ticker"),
    ("polygon", "reference_extended", "data_prefetch/polygon/reference_extended", "per_ticker"),
    ("polygon", "dividends_full", "data_prefetch/polygon/dividends_full", "per_ticker"),
    ("polygon", "splits_full", "data_prefetch/polygon/splits_full", "per_ticker"),
    ("polygon", "ipos_full", "data_prefetch/polygon/ipos_full", "per_ticker"),
    # Polygon Indices/Forex/Futures/Options Basic
    ("polygon_indices", "aggs", "data_prefetch/polygon/indices", "global"),
    ("polygon_forex", "aggs", "data_prefetch/polygon/forex", "global"),
    ("polygon_futures", "aggs", "data_prefetch/polygon/futures/aggs", "global"),
    ("polygon_options", "options_chains", "data_prefetch/polygon/options_chains", "per_ticker"),
    # Polygon Economy
    ("polygon_economy", "inflation", "data_prefetch/polygon/economy/inflation.parquet", "single"),
    ("polygon_economy", "inflation_expectations", "data_prefetch/polygon/economy/inflation_expectations.parquet", "single"),
    ("polygon_economy", "treasury_yields", "data_prefetch/polygon/economy/treasury_yields.parquet", "single"),
    # Polygon Benzinga
    ("polygon_benzinga", "analyst_insights", "data_prefetch/polygon/benzinga/analyst_insights", "per_ticker"),
    ("polygon_benzinga", "ratings", "data_prefetch/polygon/benzinga/ratings", "per_ticker"),
    ("polygon_benzinga", "earnings", "data_prefetch/polygon/benzinga/earnings", "per_ticker"),
    ("polygon_benzinga", "guidance", "data_prefetch/polygon/benzinga/guidance", "per_ticker"),
    ("polygon_benzinga", "firm_details", "data_prefetch/polygon/benzinga/firm_details", "per_ticker"),
    # Polygon indicators
    ("polygon_indicators", "sma_50", "data_prefetch/polygon/indicators/sma_50", "per_ticker"),
    ("polygon_indicators", "sma_200", "data_prefetch/polygon/indicators/sma_200", "per_ticker"),
    ("polygon_indicators", "ema_20", "data_prefetch/polygon/indicators/ema_20", "per_ticker"),
    ("polygon_indicators", "ema_50", "data_prefetch/polygon/indicators/ema_50", "per_ticker"),
    ("polygon_indicators", "rsi_14", "data_prefetch/polygon/indicators/rsi_14", "per_ticker"),
    ("polygon_indicators", "macd", "data_prefetch/polygon/indicators/macd", "per_ticker"),
    # Quiver Trader
    ("quiver", "congressional", "data_prefetch/quiver/congressional", "per_ticker"),
    ("quiver", "senatetrading", "data_prefetch/quiver/senatetrading", "per_ticker"),
    ("quiver", "housetrading", "data_prefetch/quiver/housetrading", "per_ticker"),
    ("quiver", "spacs", "data_prefetch/quiver/spacs", "per_ticker"),
    ("quiver", "insider", "data_prefetch/quiver/insider", "per_ticker"),
    ("quiver", "institutional", "data_prefetch/quiver/institutional", "per_ticker"),
    ("quiver", "gov_contracts", "data_prefetch/quiver/gov_contracts", "per_ticker"),
    ("quiver", "lobbying", "data_prefetch/quiver/lobbying", "per_ticker"),
    ("quiver", "wallstreetbets", "data_prefetch/quiver/wallstreetbets", "per_ticker"),
    ("quiver", "wikipedia_mirror", "data_prefetch/quiver/wikipedia", "per_ticker"),
    ("quiver", "offexchange", "data_prefetch/quiver/offexchange", "per_ticker"),
    ("quiver", "topshareholders", "data_prefetch/quiver/topshareholders", "per_ticker"),
    ("quiver", "etfholdings", "data_prefetch/quiver/etfholdings", "per_ticker"),
    ("quiver", "patentmomentum_bulk", "data_prefetch/quiver/patentmomentum/global.parquet", "single"),
    ("quiver", "corporatedonors_bulk", "data_prefetch/quiver/corporatedonors/global.parquet", "single"),
    ("quiver", "quivernews_bulk", "data_prefetch/quiver/quivernews/global.parquet", "single"),
    ("quiver", "sec13fchanges_bulk", "data_prefetch/quiver/sec13fchanges/global.parquet", "single"),
    # StockTwits (Pass 53 v8h+1 owner-approved 2026-05-08, retail attention layer)
    ("stocktwits", "streams", "data_prefetch/stocktwits", "per_ticker"),
    # Finnhub social_sentiment (Pass 53 v8h+1; PREMIUM-LOCKED at free tier - kept for future)
    ("finnhub", "social_sentiment", "data_prefetch/finnhub/social_sentiment", "per_ticker"),
    # SEC EDGAR per-form
    ("sec_edgar", "10_K", "data_prefetch/sec_edgar/10_K", "per_ticker"),
    ("sec_edgar", "10_Q", "data_prefetch/sec_edgar/10_Q", "per_ticker"),
    ("sec_edgar", "8_K", "data_prefetch/sec_edgar/8_K", "per_ticker"),
    ("sec_edgar", "form_4", "data_prefetch/sec_edgar/4", "per_ticker"),
    ("sec_edgar", "DEF_14A", "data_prefetch/sec_edgar/DEF_14A", "per_ticker"),
    ("sec_edgar", "S_1", "data_prefetch/sec_edgar/S_1", "per_ticker"),
    ("sec_edgar", "S_1_A", "data_prefetch/sec_edgar/S_1_A", "per_ticker"),
    ("sec_edgar", "SC_13D", "data_prefetch/sec_edgar/SC_13D", "per_ticker"),
    ("sec_edgar", "SC_13D_A", "data_prefetch/sec_edgar/SC_13D_A", "per_ticker"),
    ("sec_edgar", "SC_13G", "data_prefetch/sec_edgar/SC_13G", "per_ticker"),
    ("sec_edgar", "SC_13G_A", "data_prefetch/sec_edgar/SC_13G_A", "per_ticker"),
    ("sec_edgar", "xbrl_companyfacts", "data_prefetch/sec_xbrl", "per_ticker"),
    # FRED / ALFRED
    ("fred", "observations", "data_prefetch/fred/observations", "global"),
    ("alfred", "vintage_observations", "data_prefetch/alfred", "global"),
    # AAII / CNN F&G
    ("aaii", "weekly_sentiment", "data_prefetch/aaii/weekly_sentiment.parquet", "single"),
    ("cnn_fg", "daily", "data_prefetch/cnn_fg/daily.parquet", "single"),
    # CFTC
    ("cftc", "tff_disagg_combined", "data_prefetch/cftc", "global"),
    ("cftc", "extended", "data_prefetch/cftc/legacy_combined", "global"),
    # Apewisdom / Wikipedia / pytrends
    ("apewisdom", "global", "data_prefetch/apewisdom/global.parquet", "single"),
    ("apewisdom", "subreddits", "data_prefetch/apewisdom/subreddits", "global"),
    ("wikipedia", "pageviews", "data_prefetch/wikipedia", "per_ticker"),
    ("pytrends", "interest_over_time", "data_prefetch/pytrends", "per_ticker"),
    # Finnhub free tier
    ("finnhub", "quote", "data_prefetch/finnhub/quote", "per_ticker"),
    ("finnhub", "profile2", "data_prefetch/finnhub/profile2", "per_ticker"),
    ("finnhub", "peers", "data_prefetch/finnhub/peers", "per_ticker"),
    ("finnhub", "insider_transactions", "data_prefetch/finnhub/insider_transactions", "per_ticker"),
    ("finnhub", "insider_sentiment", "data_prefetch/finnhub/insider_sentiment", "per_ticker"),
    ("finnhub", "recommendation", "data_prefetch/finnhub/recommendation", "per_ticker"),
    ("finnhub", "earnings", "data_prefetch/finnhub/earnings", "per_ticker"),
    ("finnhub", "company_news", "data_prefetch/finnhub/company_news", "per_ticker"),
    ("finnhub", "financials_reported", "data_prefetch/finnhub/financials_reported", "per_ticker"),
    ("finnhub", "metric", "data_prefetch/finnhub/metric", "per_ticker"),
    ("finnhub", "calendar_earnings", "data_prefetch/finnhub/calendar_earnings.parquet", "single"),
    ("finnhub", "calendar_ipo", "data_prefetch/finnhub/calendar_ipo.parquet", "single"),
    ("finnhub", "calendar_economic", "data_prefetch/finnhub/calendar_economic.parquet", "single"),
]


def load_codebase_text() -> tuple[str, str]:
    """Return (production_text, total_text) for field-wiring grep.

    production_text: backtest/data + engine + signals + results (active code path)
    total_text: all of backtest/ + scripts/ (anywhere coded)
    """
    prod_parts = []
    total_parts = []
    for sub in ("backtest/data", "backtest/engine", "backtest/signals", "backtest/results"):
        p = Path(sub)
        if not p.exists():
            continue
        for f in p.rglob("*.py"):
            try:
                prod_parts.append(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
    backtest_root = Path("backtest")
    if backtest_root.exists():
        for f in backtest_root.rglob("*.py"):
            try:
                total_parts.append(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
    scripts_root = Path("scripts")
    if scripts_root.exists():
        for f in scripts_root.rglob("*.py"):
            try:
                total_parts.append(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
    return "\n".join(prod_parts), "\n".join(total_parts)


def field_wiring_status(field: str, prod: str, total: str) -> dict:
    """Return {coded, wired, n_refs} for a field name.

    coded  = referenced anywhere (backtest/ + scripts/)
    wired  = referenced in backtest/{data,engine,signals,results}/ (active path)
    n_refs = approximate reference count (in quoted-string form)
    """
    if not field or len(field) < 2:
        return {"coded": False, "wired": False, "n_refs": 0}
    # Match common quotation patterns to avoid false positives on substrings
    patterns = [f'"{field}"', f"'{field}'", f'["{field}"]', f"['{field}']"]
    prod_count = sum(prod.count(p) for p in patterns)
    total_count = sum(total.count(p) for p in patterns)
    return {
        "coded": total_count > 0,
        "wired": prod_count > 0,
        "n_refs": total_count,
    }


def main() -> int:
    print(f"=== Building Sprint 0A dashboard data ===")
    universe = load_universe()
    universe_size = len(universe)
    print(f"Master Universe: {universe_size} tickers")

    print("Loading codebase text for field-wiring grep ...")
    prod_text, total_text = load_codebase_text()
    print(f"  production code: {len(prod_text)} chars")
    print(f"  total code: {len(total_text)} chars")

    # PRIMARY catalog source: API_ENDPOINT_INVENTORY.md (per CHECKLIST #77)
    # Filesystem walk is SUPPLEMENTARY - provides files/rows/schema for
    # endpoints we have cached. The catalog itself comes from the inventory.
    inventory_rows = []
    if INVENTORY_MD.exists():
        inventory_rows = parse_inventory_md(INVENTORY_MD)
        print(f"Parsed {len(inventory_rows)} endpoint rows from {INVENTORY_MD}")
    else:
        print(f"WARNING: {INVENTORY_MD} not found - falling back to ENDPOINTS list only")

    tier_counts = universe.groupby("resolved_tier", dropna=False).size().to_dict() if "resolved_tier" in universe.columns else {}

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe_size": universe_size,
        "tier_counts": {str(k): int(v) for k, v in tier_counts.items()},
        "endpoints": [],
        "per_ticker_coverage": {},
    }

    # Per-ticker coverage tracker
    ticker_coverage: dict[str, dict[str, int]] = {}
    for t in universe["Symbol"].dropna().astype(str).str.upper():
        ticker_coverage[t] = {}

    for api, endpoint, path_str, kind in ENDPOINTS:
        path = Path(path_str)
        ep_data = {
            "api": api,
            "endpoint": endpoint,
            "path": path_str,
            "kind": kind,
        }

        if kind == "per_ticker":
            files = scan_dir_files(path)
            ep_data["files_count"] = len(files)
            ep_data["coverage_pct"] = round(100.0 * len(files) / max(universe_size, 1), 2)
            # Available coverage: files / expected_max (realistic ceiling)
            key = f"{api}.{endpoint}"
            expected_max = EXPECTED_MAX.get(key, universe_size)
            ep_data["expected_max_universe"] = expected_max
            raw_avail = 100.0 * len(files) / max(expected_max, 1)
            ep_data["available_coverage_pct"] = round(min(100.0, raw_avail), 2)
            # Flag when actual exceeds expected (broader-than-universe coverage)
            if raw_avail > 100.0:
                ep_data["coverage_note"] = f"broader-than-universe: {len(files)} files vs {expected_max} expected ({raw_avail:.0f}%)"
            # Field/dimension audit
            all_columns: set = set()
            row_counts = []
            field_counts = []
            for ticker, info in files.items():
                all_columns.update(info["columns"])
                if info["row_count"] > 0:
                    row_counts.append(info["row_count"])
                field_counts.append(info["n_columns"])
                # mark coverage
                if ticker in ticker_coverage:
                    ticker_coverage[ticker][f"{api}.{endpoint}"] = info["row_count"]
            ep_data["unique_columns"] = sorted(all_columns)
            ep_data["n_unique_columns"] = len(all_columns)
            ep_data["avg_field_count"] = round(sum(field_counts) / max(len(field_counts), 1), 2)
            ep_data["min_field_count"] = min(field_counts) if field_counts else 0
            ep_data["max_field_count"] = max(field_counts) if field_counts else 0
            ep_data["non_empty_files"] = len(row_counts)
            ep_data["sample_row_counts"] = sorted(row_counts)[:5] + ["..."] + sorted(row_counts)[-5:] if len(row_counts) > 10 else sorted(row_counts)
            # Status keyed off AVAILABLE coverage (more meaningful than universe-wide)
            avail = ep_data["available_coverage_pct"]
            ep_data["status"] = "OK" if avail >= 80 else "PARTIAL" if avail >= 30 else "LOW"
        elif kind == "global":
            # Directory of global files (each one is its own dataset, not per-ticker)
            files_count = 0
            all_columns: set = set()
            row_counts = []
            if path.exists():
                for parq in path.glob("*.parquet"):
                    if parq.stem.startswith("_"):
                        continue
                    files_count += 1
                    try:
                        df = pd.read_parquet(parq)
                        all_columns.update(df.columns)
                        row_counts.append(len(df))
                    except Exception:
                        pass
            ep_data["files_count"] = files_count
            ep_data["unique_columns"] = sorted(all_columns)
            ep_data["n_unique_columns"] = len(all_columns)
            ep_data["total_rows"] = sum(row_counts)
            ep_data["avg_rows"] = round(sum(row_counts) / max(len(row_counts), 1), 2)
            ep_data["status"] = "OK" if files_count > 0 else "EMPTY"
        elif kind == "single":
            info = scan_global_file(path)
            ep_data.update(info)
            ep_data["status"] = "OK" if info.get("present") else "EMPTY"

        # Attach endpoint-level use-case / stage / criticality
        ep_key = f"{api}.{endpoint}"
        ep_meta = ENDPOINT_USE_CASES.get(ep_key, {})
        ep_data["use_case"] = ep_meta.get("use_case", "-")
        ep_data["stage_phase"] = ep_meta.get("stage", "-")
        ep_data["criticality"] = ep_meta.get("criticality", "-")

        # Per-field coding/wiring status (for API Usage / Stage tab field-level rows)
        fields_for_audit = ep_data.get("unique_columns") or ep_data.get("columns") or []
        field_statuses = []
        for f in fields_for_audit:
            status = field_wiring_status(f, prod_text, total_text)
            field_statuses.append({"field": f, **status})
        ep_data["field_statuses"] = field_statuses

        snapshot["endpoints"].append(ep_data)
        print(f"  {api}.{endpoint}: {ep_data.get('coverage_pct', '-')}% ({ep_data.get('files_count', '-')} files, status={ep_data['status']})")

    # Per-ticker summary
    for ticker, coverage in ticker_coverage.items():
        # Find ticker's tier
        row = universe[universe["Symbol"] == ticker]
        tier = str(row["resolved_tier"].iloc[0]) if "resolved_tier" in universe.columns and not row.empty else "unknown"
        sector = str(row["Sector"].iloc[0]) if "Sector" in universe.columns and not row.empty else "unknown"
        snapshot["per_ticker_coverage"][ticker] = {
            "tier": tier,
            "sector": sector,
            "endpoints_with_data": len(coverage),
            "endpoints_total": len([e for e in ENDPOINTS if e[3] == "per_ticker"]),
            "endpoint_row_counts": coverage,
        }

    # Per-API aggregation
    apis: dict[str, dict] = {}
    for ep in snapshot["endpoints"]:
        api = ep["api"]
        apis.setdefault(api, {"endpoints": 0, "ok_endpoints": 0, "total_files": 0})
        apis[api]["endpoints"] += 1
        if ep["status"] in ("OK",):
            apis[api]["ok_endpoints"] += 1
        apis[api]["total_files"] += ep.get("files_count", 0)
    snapshot["api_summary"] = apis
    snapshot["api_use_cases"] = API_USE_CASES

    # CANONICAL catalog from inventory MD (per CHECKLIST #77)
    catalog = []
    for r in inventory_rows:
        status = normalize_status(r["status_raw"])
        cached_bucket, cached_count = normalize_cached(r["currently_cached"])
        # Combine status + cached -> final bucket
        if status == "TIER_BLOCKED":
            final = "TIER_BLOCKED"
        elif status == "DOES_NOT_EXIST":
            final = "DOES_NOT_EXIST"
        elif status == "ACCESSIBLE" and cached_bucket == "CACHED":
            final = "CACHED"
        elif status == "ACCESSIBLE" and cached_bucket == "NOT_CACHED":
            final = "ACCESSIBLE_NOT_CACHED"
        elif status == "PARTIAL":
            final = "PARTIAL"
        elif status == "UNPROBED":
            final = "UNPROBED"
        else:
            final = "UNKNOWN"
        catalog.append({
            "api_label": r["api_label"],
            "endpoint_path": r["endpoint_path"],
            "tier_status": status,
            "cached_status": cached_bucket,
            "cached_count": cached_count,
            "final_bucket": final,
            "sample_fields": r["sample_fields"],
            "action": r["action"],
        })
    snapshot["catalog"] = catalog
    # Catalog status counts
    bucket_counts: dict[str, int] = {}
    for c in catalog:
        bucket_counts[c["final_bucket"]] = bucket_counts.get(c["final_bucket"], 0) + 1
    snapshot["catalog_bucket_counts"] = bucket_counts
    print(f"Catalog summary: {len(catalog)} endpoints | buckets: {bucket_counts}")

    # Output JSON
    out_json = OUT_DIR / "data.json"
    out_json.write_text(json.dumps(snapshot, indent=2, default=str))
    print(f"\nWrote {out_json}")

    # Also write as JS const for direct browser load (no fetch needed)
    out_js = OUT_DIR / "data.js"
    out_js.write_text(f"const DASHBOARD_DATA = {json.dumps(snapshot, default=str)};\n")
    print(f"Wrote {out_js}")

    # Timestamp marker
    (OUT_DIR / "last_run.txt").write_text(snapshot["generated_at"])
    print(f"\nGenerated at: {snapshot['generated_at']}")
    print(f"Endpoints: {len(snapshot['endpoints'])}")
    print(f"Per-ticker tracked: {len(snapshot['per_ticker_coverage'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
