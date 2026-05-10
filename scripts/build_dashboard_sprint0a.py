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


def compute_field_coverage_matrix(cache_paths_list: list, universe: list[str], universe_size: int) -> list[dict]:
    """Per-(api, endpoint, field) coverage table.

    For each cache directory in CACHE_PATHS:
    - per_ticker: sample up to 200 non-empty parquets; for each column, count
      how many sampled tickers have a non-null value; estimate universe coverage
      as (sampled_with_field / sampled_non_empty) * (n_files_total / universe_size).
      Universe coverage = % of universe tickers with non-null in this field.
    - single: read the single parquet; per-field coverage = non-null rows / total rows.
    - global: similar to single but may span multiple files; concat samples.

    Returns rows ready for HTML table:
      {api, endpoint, field, kind, coverage_pct, commentary, n_observed,
       pyramid_status, coded, wired, tested, cached, testing_layers}.
    """
    import random
    rows: list[dict] = []
    universe_set = set(universe)

    # Heuristic commentary lookup based on (api, endpoint) facts. Updated
    # 2026-05-10 v8h+1 with findings from CAV-075 (delisting empirically
    # confirmed 0/246 in SEC active map), DEC-605/CAV-074 (Finnhub
    # social_sentiment EXCLUDED Phase 1A), DEC-606/CAV-076 (Finnhub
    # financials_reported EXCLUDED ALL phases), INV-047/CAV-077 (Quiver
    # etfholdings refresh dead-end), global-feed completeness audit
    # (CFTC/Polygon-economy/FRED/ALFRED all empirically COMPLETE).
    KNOWN_GAPS = {
        # SEC EDGAR per-form: empirically confirmed delisting (CAV-075)
        ("sec_edgar", "10_K"):                "CAV-075: 246 missing tickers EMPIRICALLY confirmed delisted/acquired/renamed/foreign (0/246 in SEC active CIK map). Examples: ABMD->JNJ, ANSS->Synopsys, ADS->BFH, ALXN->AstraZeneca, AGN->AbbVie. Immutable at source.",
        ("sec_edgar", "10_Q"):                "CAV-075: same 246 SEC-unfileable as 10-K (delisting/acquisition; immutable)",
        ("sec_edgar", "8_K"):                 "CAV-075: same delisting baseline; some non-public companies",
        ("sec_edgar", "form_4"):              "CAV-075: same delisting baseline; tickers without insider transactions in window",
        ("sec_edgar", "DEF_14A"):             "CAV-075: same baseline + non-proxy filers",
        ("sec_edgar", "S_1"):                 "CAV-075: same baseline; tickers without recent IPO filings",
        ("sec_edgar", "S_1_A"):               "CAV-075: same baseline; tickers without S-1 amendments",
        ("sec_edgar", "SC_13D"):              "CAV-075: same baseline; activist filings sparse by ticker",
        ("sec_edgar", "SC_13D_A"):            "CAV-075: same baseline; activist amendments sparse",
        ("sec_edgar", "SC_13G"):              "CAV-075: same baseline; not all tickers have >5% holders",
        ("sec_edgar", "SC_13G_A"):            "CAV-075: same baseline; passive amendments sparse",
        ("sec_edgar", "xbrl_companyfacts"):   "CAV-075: 275 tickers without recent XBRL filings (delisted/foreign overlap)",
        # Polygon reference: same delisting confirmation (CAV-075)
        ("polygon", "events"):                "INV-029: only ticker_change events captured; other event types deferred (P2 Phase 1B+)",
        ("polygon", "reference"):             "CAV-075: ~251 delisted tickers (overlap with SEC unfileable); immutable at source",
        ("polygon", "reference_extended"):    "CAV-075: ~251 delisted; INV-030 RESOLVED for available 1686 (extended fields populated)",
        # Wikipedia: source-availability ceiling
        ("wikipedia", "pageviews"):           "523 tickers without dedicated Wikipedia page (small-cap / recent IPO; e.g. AAOI, ABSI, AEYE, AFRM). Source-availability ceiling, not delisting.",
        ("quiver", "wikipedia_mirror"):       "Same WP page-availability ceiling as wikipedia.pageviews",
        # Quiver etfholdings: refresh dead-end (INV-047/CAV-077)
        ("quiver", "etfholdings"):            "INV-047/CAV-077: STATIC SNAPSHOT only - all Quiver+Polygon refresh endpoints return 404; existing 1563 files from deprecated source. Owner-pending decision: accept static (default), paid 3rd-party (~$30-50/mo), or scraping infra.",
        # Pytrends: deferred per DEC-599
        ("pytrends", "interest_over_time"):   "DEC-599: DEFERRED Phase 1C (Google 429 anti-bot blocks free pytrends); StockTwits + Apewisdom + Polygon news cover retail-attention layer at free tier",
        # Finnhub financials_reported: EXCLUDED ALL phases (DEC-606/CAV-076)
        ("finnhub", "financials_reported"):   "DEC-606/CAV-076: EXCLUDED COMPLETELY from all phases (1A+1B+1C+Stage3+Stage4). Superseded by SEC EDGAR XBRL companyfacts (1662, free) + Polygon /vX/reference/financials (1937, already paid). Premium not worth subscribing.",
        # Finnhub social_sentiment: EXCLUDED Phase 1A (DEC-605/CAV-074)
        ("finnhub", "social_sentiment"):      "DEC-605/CAV-074: PREMIUM-LOCKED; EXCLUDED from Phase 1A. Apewisdom + StockTwits + Polygon news insights_json cover ~90% of retail-attention signal at free tier. Phase 1B+ eligible if Premium added.",
        # Single-file global feeds: empirically COMPLETE (CFTC / Polygon economy / FRED / ALFRED)
        ("aaii", "weekly_sentiment"):         "Single global parquet (13-col extended; 2,022 rows 1987-2026 fresh through 2026-05-07). Not per-ticker. COMPLETE per DEC-601.",
        ("aaii", "asset_allocation_survey"):  "Single global parquet (11-col; 445 monthly rows 1987-2026 fresh through 2026-04). Not per-ticker. COMPLETE per DEC-601 sister entry (owner-supplied 2026-05-09).",
        # CFTC: 19 contracts complete (audit 2026-05-10)
        ("cftc", "tff_disagg_combined"):      "Audit 2026-05-10: 19 contract series ALL non-empty (commodities + currencies + e-mini equity + treasuries + VIX); most span 2006-06-13 to 2026-04-28 (current week). COMPLETE per Sprint 0A.4.",
        ("cftc", "extended"):                 "Audit 2026-05-10: 19-contract universe; same fetch as tff_disagg_combined. COMPLETE.",
        # Polygon economy: 3 series complete
        ("polygon_economy", "inflation"):              "Audit 2026-05-10: 951 monthly rows 1947-01 to 2026-03 (CPI+PCE core/total). COMPLETE.",
        ("polygon_economy", "inflation_expectations"): "Audit 2026-05-10: 532 monthly rows 1982-01 to 2026-04 (Fed model + market 1Y/5Y/10Y/30Y). COMPLETE.",
        ("polygon_economy", "treasury_yields"):        "Audit 2026-05-10: 16,071 daily rows 1962-01-02 to 2026-05-06 (1M/3M/1Y/2Y/5Y/10Y/30Y curve). COMPLETE.",
        # FRED: 90 series complete (over-delivered vs Sprint 0A.2 spec ~50)
        ("fred", "observations"):             "Audit 2026-05-10: 90 series ALL non-empty (vs Sprint 0A.2 spec ~50; over-delivered). Date coverage varies by frequency (quarterly series ~33 rows; daily series 2,000+ rows). All current through 2026-04 to 2026-05.",
        # ALFRED: 80 series with vintage history
        ("alfred", "vintage_observations"):   "Audit 2026-05-10: 80 series ALL non-empty with vintage observations (e.g. AAA10Y has 41,058 rows = full vintage history). Sprint 0A.2 spec satisfied at higher count.",
    }

    def commentary(api, endpoint, field, pct, kind=None):
        # KNOWN_GAPS lookup wins for endpoint-level explanations regardless of pct
        key = (api, endpoint)
        if key in KNOWN_GAPS:
            return KNOWN_GAPS[key]
        if pct >= 99.5:
            return ""
        # Kind-aware default text per CHECKLIST methodology rule (Pass 53 v8h+1):
        # global feeds (single/global) use different completeness semantics.
        if kind in ("single", "global"):
            if pct == 0:
                return "Global feed: field present in schema but unpopulated; investigate source"
            if pct < 50:
                return "Global feed: data-quality gap; field sparse across observations"
            return "Global feed: minor data-quality gap; some observations lack this field"
        # per_ticker default
        if pct == 0:
            return "Field present in schema but no values populated; investigate source"
        if pct < 50:
            return "Major gap; field may be sparse-by-design or source-limited"
        return "Minor gap; tickers without this field likely delisted/foreign or non-applicable"

    def per_endpoint_row(api, endpoint, kind, fields_data, n_observed, n_universe):
        """Roll up endpoint-level summary row."""
        avg_cov = sum(d["coverage_pct"] for d in fields_data.values()) / max(len(fields_data), 1)
        return {
            "api": api,
            "endpoint": endpoint,
            "field": "(endpoint summary)",
            "kind": kind,
            "coverage_pct": round(avg_cov, 1),
            "commentary": f"Avg per-field coverage; {len(fields_data)} fields tracked",
            "n_observed": n_observed,
            "n_universe": n_universe,
            "is_summary": True,
        }

    for tup in cache_paths_list:
        api, endpoint, path, kind = tup
        cache_path = Path(path)

        if kind == "single":
            # Single global parquet (e.g. AAII weekly sentiment, AAS).
            # Completeness metric: row_count + latest_obs_date freshness.
            if not cache_path.exists() or not cache_path.is_file():
                continue
            try:
                df = pd.read_parquet(cache_path)
            except Exception:
                continue
            # Find latest observation date (first date-like column)
            latest_obs = None
            date_col = next((c for c in df.columns if c.lower() in
                              {"date", "time", "timestamp", "filing_date", "report_date",
                               "execution_date", "ex_dividend_date", "snapshot_date",
                               "transactiondate", "attime"}), None)
            if date_col:
                try:
                    d = pd.to_datetime(df[date_col], errors="coerce").dropna()
                    if len(d):
                        latest_obs = str(d.max().date())
                except Exception:
                    pass
            fields_data = {}
            for col in df.columns:
                non_null = df[col].notna().sum()
                pct = float(non_null) / max(len(df), 1) * 100
                fields_data[col] = {
                    "coverage_pct": round(pct, 1),
                    "n_observed": int(non_null),
                }
                rows.append({
                    "api": api,
                    "endpoint": endpoint,
                    "field": col,
                    "kind": kind,
                    "coverage_pct": round(pct, 1),
                    "commentary": commentary(api, endpoint, col, pct, kind),
                    "n_observed": int(non_null),
                    "n_universe": len(df),
                    "row_count": len(df),
                    "latest_obs_date": latest_obs,
                    "is_summary": False,
                })
            rows.append(per_endpoint_row(api, endpoint, kind, fields_data, len(df), len(df)))

        elif kind == "per_ticker":
            if not cache_path.is_dir():
                continue
            # Sample up to 200 non-empty parquets
            all_parqs = sorted(cache_path.glob("*.parquet"))
            non_empty_sample = []
            for parq in all_parqs:
                stem = parq.stem
                if stem.startswith("_") or stem in ("all", "global", "index"):
                    continue
                try:
                    if parq.stat().st_size < 200:
                        continue
                    df = pd.read_parquet(parq)
                    if df.empty:
                        continue
                    non_empty_sample.append((stem.upper(), df))
                except Exception:
                    continue
                if len(non_empty_sample) >= 50:
                    break
            if not non_empty_sample:
                continue
            n_total_files = len(all_parqs)
            n_universe_with_data_estimate = min(n_total_files, universe_size)
            # Per-field: count sampled tickers with non-null
            field_tickers: dict[str, int] = {}
            field_non_null_total: dict[str, int] = {}
            field_total_obs: dict[str, int] = {}
            for ticker, df in non_empty_sample:
                for col in df.columns:
                    non_null = int(df[col].notna().sum())
                    if non_null > 0:
                        field_tickers[col] = field_tickers.get(col, 0) + 1
                    field_non_null_total[col] = field_non_null_total.get(col, 0) + non_null
                    field_total_obs[col] = field_total_obs.get(col, 0) + len(df)
            fields_data = {}
            sampled = len(non_empty_sample)
            for col, tickers_with in field_tickers.items():
                # Estimate universe coverage = (sample_field_rate) * (universe_with_data / sampled)
                sample_rate = tickers_with / sampled
                # Apply universe ceiling: tickers with this field cannot exceed total cached files
                est_universe_pct = sample_rate * (n_universe_with_data_estimate / max(universe_size, 1)) * 100
                fields_data[col] = {
                    "coverage_pct": round(est_universe_pct, 1),
                    "n_observed": tickers_with,
                }
                rows.append({
                    "api": api,
                    "endpoint": endpoint,
                    "field": col,
                    "kind": kind,
                    "coverage_pct": round(est_universe_pct, 1),
                    "commentary": commentary(api, endpoint, col, est_universe_pct, kind),
                    "n_observed": tickers_with,
                    "n_universe": universe_size,
                    "n_sampled": sampled,
                    "n_files_total": n_total_files,
                    "is_summary": False,
                })
            rows.append(per_endpoint_row(api, endpoint, kind, fields_data, sampled, universe_size))

        elif kind == "global":
            # Global directory of multiple parquets (e.g. fred/observations).
            # Completeness metrics: series_count + non_empty_pct + latest_obs_date.
            if not cache_path.is_dir():
                continue
            all_parqs_list = sorted(cache_path.glob("*.parquet"))
            n_total_files = len(all_parqs_list)
            all_parqs = all_parqs_list[:50]  # cap for speed
            field_seen: dict[str, int] = {}
            n_files_with_data = 0
            latest_obs_global = None
            for parq in all_parqs:
                try:
                    if parq.stat().st_size < 200:
                        continue
                    df = pd.read_parquet(parq)
                    if df.empty:
                        continue
                    n_files_with_data += 1
                    for col in df.columns:
                        if df[col].notna().sum() > 0:
                            field_seen[col] = field_seen.get(col, 0) + 1
                    # Track latest obs across sampled files
                    date_col = next((c for c in df.columns if c.lower() in
                                      {"date", "time", "timestamp", "report_date"}), None)
                    if date_col:
                        try:
                            d = pd.to_datetime(df[date_col], errors="coerce").dropna()
                            if len(d):
                                m = str(d.max().date())
                                if not latest_obs_global or m > latest_obs_global:
                                    latest_obs_global = m
                        except Exception:
                            pass
                except Exception:
                    continue
            fields_data = {}
            for col, count in field_seen.items():
                pct = float(count) / max(n_files_with_data, 1) * 100
                fields_data[col] = {"coverage_pct": round(pct, 1), "n_observed": count}
                rows.append({
                    "api": api,
                    "endpoint": endpoint,
                    "field": col,
                    "kind": kind,
                    "coverage_pct": round(pct, 1),
                    "commentary": commentary(api, endpoint, col, pct, kind),
                    "n_observed": count,
                    "n_universe": n_total_files,
                    "n_sampled": n_files_with_data,
                    "series_count": n_total_files,
                    "non_empty_pct": round(100.0 * n_files_with_data / max(len(all_parqs), 1), 1),
                    "latest_obs_date": latest_obs_global,
                    "is_summary": False,
                })
            rows.append(per_endpoint_row(api, endpoint, kind, fields_data, n_files_with_data, n_total_files))

    return rows


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
    "quiver.etfholdings": {"use_case": "Per-ticker ETF inclusion list + % weight (no PIT)", "stage": "Phase 1B ETF flow proxy. STATIC SNAPSHOT only (INV-047 / CAV-077 2026-05-10): all Quiver and Polygon refresh endpoints return 404; existing 1563 files came from deprecated source that no longer responds. Phase 1A baseline does not consume; Phase 1B+ must treat as single-point-in-time reference.", "criticality": "P2 (static snapshot; refresh dead-end pending owner data-source decision)"},
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
    "aaii.weekly_sentiment": {"use_case": "AAII weekly bullish/bearish % (contrarian signal at extremes); 13-col extended schema with 8wk MA + long-term avg +/- 1stdev bands + S&P weekly OHLC reference", "stage": "Phase 1A regime classifier", "criticality": "P1"},
    "aaii.asset_allocation_survey": {"use_case": "AAII monthly stocks/bonds/cash % allocation (retail contrarian indicator; long-term avg ~62% stocks; >75% = euphoria warning, <50% = capitulation buy signal)", "stage": "Phase 1A regime overlay (long-term cycle), Phase 1B+ contrarian timing", "criticality": "P2"},
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
    "finnhub.financials_reported": {"use_case": "Reported financial statements", "stage": "EXCLUDED COMPLETELY per DEC-606 (owner 2026-05-10). Superseded by SEC EDGAR XBRL companyfacts (1662 tickers, free) + Polygon financials (1937 tickers, paid tier already covered). Free Finnhub coverage capped at 46% (891/1937); Premium ~$10-30/mo not worth it given strictly superior alternatives. See CAV-076.", "criticality": "EXCLUDED (permanent supersedence)"},
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
    "finnhub.social_sentiment": {
        "use_case": "Per-ticker daily Reddit + Twitter mention counts + bullish/bearish weighted score. Cross-platform retail-attention signal (complements Apewisdom Reddit-only + StockTwits Twitter-of-finance). Use cases: (1) Phase 1B News Analyst gets cross-platform mention z-score per candidate; (2) Risk Debaters get high-mention-spike anomaly flag; (3) Trader gets sentiment trend reversal signal; (4) Phase 1C contrarian strategies fade retail euphoria when score AND mentions both extreme.",
        "stage": "EXCLUDED from Phase 1A per DEC-605 (owner 2026-05-09). PREMIUM-LOCKED at our Finnhub free tier; cost-benefit analysis says skip ($360/yr marginal vs Apewisdom+StockTwits+Polygon news coverage at free tier). Phase 1B+ eligible IF Finnhub Premium subscribed. Script BUILT (prefetch_finnhub_social_sentiment.py); zero runtime references in Phase 1A pipeline (verified 2026-05-09 grep). See CAV-074.",
        "criticality": "P3 (Phase 1A EXCLUDED; Phase 1B+ deferred-pending-tier)",
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
    ("aaii", "asset_allocation_survey", "data_prefetch/aaii/asset_allocation_survey.parquet", "single"),
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

    # Owner directive 2026-05-09: per-(api, endpoint, field) coverage matrix
    # in a new dashboard page. For each field: coverage % across universe,
    # commentary on why <100%, plus per-endpoint pyramid status indicators.
    print("Computing per-field coverage matrix ...")
    universe_list = list(universe["Symbol"]) if "Symbol" in universe.columns else []
    coverage_matrix = compute_field_coverage_matrix(ENDPOINTS, universe_list, universe_size)
    # Augment each row with cached/coded/wired/tested heuristics from existing
    # endpoint scan results
    ep_lookup = {(e["api"], e["endpoint"]): e for e in snapshot["endpoints"]}
    # Build a 'consumer-references' set: which APIs are referenced in
    # backtest/data,engine,signals,results,agents (the runtime hot-path).
    prod_corpus = ""
    for d in ("backtest/data", "backtest/engine", "backtest/signals",
              "backtest/results", "backtest/agents"):
        dd = Path(d)
        if dd.exists():
            for py in dd.rglob("*.py"):
                try:
                    prod_corpus += py.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
    tests_corpus = ""
    td = Path("backtest/tests")
    if td.exists():
        for py in td.rglob("*.py"):
            try:
                tests_corpus += py.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
    for row in coverage_matrix:
        api = row["api"]
        endpoint = row["endpoint"]
        ep = ep_lookup.get((api, endpoint), {})
        # cached: any non-empty parquet exists for the endpoint
        row["cached"] = (ep.get("non_empty_files", 0) > 0
                         or ep.get("files_count", 0) > 0)
        row["files_count"] = ep.get("files_count", 0)
        row["endpoint_coverage_pct"] = ep.get("coverage_pct")
        # coded: cache path string appears in any production module
        path_str = next((p for (a, e, p, k) in ENDPOINTS
                         if a == api and e == endpoint), "")
        row["coded"] = path_str in prod_corpus or path_str.replace("/", ".") in prod_corpus
        # wired: cache path is read at runtime (a 'pd.read_parquet' / 'Path(' call references it)
        wired_signal = (
            f'"{path_str}"' in prod_corpus or
            f"'{path_str}'" in prod_corpus or
            f'Path("{path_str}")' in prod_corpus
        )
        row["wired"] = wired_signal
        # tested: any test file references the cache path or api+endpoint
        test_signal = (
            path_str in tests_corpus or
            f"{api}/{endpoint}" in tests_corpus or
            f"{api}.{endpoint}" in tests_corpus
        )
        row["tested"] = test_signal

    snapshot["coverage_matrix"] = coverage_matrix
    print(f"  coverage matrix rows: {len(coverage_matrix)}")

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
