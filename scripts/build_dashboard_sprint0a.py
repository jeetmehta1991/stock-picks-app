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


def load_universe() -> pd.DataFrame:
    """Return Master Universe DataFrame with Symbol + resolved_tier columns."""
    if not MASTER_UNIVERSE.exists():
        return pd.DataFrame(columns=["Symbol", "resolved_tier", "Sector"])
    df = pd.read_csv(MASTER_UNIVERSE, comment="#")
    df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()
    return df


def scan_dir_files(dir_path: Path) -> dict[str, dict]:
    """Return {ticker: {file_size, row_count, columns, has_date_col, last_date}}
    for each .parquet in dir_path. Per-ticker shards only — skip _index/_checkpoint
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
    # Polygon Indices/Forex/Futures Basic
    ("polygon_indices", "aggs", "data_prefetch/polygon/indices", "global"),
    ("polygon_forex", "aggs", "data_prefetch/polygon/forex", "global"),
    ("polygon_futures", "aggs", "data_prefetch/polygon/futures/aggs", "global"),
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


def main() -> int:
    print(f"=== Building Sprint 0A dashboard data ===")
    universe = load_universe()
    universe_size = len(universe)
    print(f"Master Universe: {universe_size} tickers")

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
            ep_data["status"] = "OK" if ep_data["coverage_pct"] >= 80 else "PARTIAL" if ep_data["coverage_pct"] >= 30 else "LOW"
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
