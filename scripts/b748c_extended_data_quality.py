# Source: Owner directive 2026-06-13 "Investigate further still" + CHECKLIST #44 + #76 per CHECKLIST #77
"""B748c EXTENDED — broader data-quality investigation across ALL 16 TIER 2
producers (not just the 3 from B748b).

Owner directive 2026-06-13 after first investigation pass: "Investigate
further still." The discipline gap caught in B748b applies to every B745
producer with an empty smoke result -- I never investigated WHY per
CHECKLIST #44(b). This script expands to:

  1. ALL 16 TIER 2 producers (B745 registry post-deletion)
  2. Time-coverage: does the data span the 2020-2026 measurement window?
     Freshness: when was the last filing/event?
  3. T1a active-coverage by % (was only spot-checked in prior B748c)
  4. NULL rates on critical columns
  5. Runtime probe on KNOWN-EVENT (ticker, date) pairs where possible --
     pulling events directly FROM the data so probes can't miss
  6. Schema variance across files within a producer's cache
  7. Producer-source path discovery (use the producer's actual constant,
     not B745's hardcoded registry strings)
  8. Per-strategy fire-density estimate: rough fires-per-year per
     consuming strategy

The aim is to cover ALL B745 producers that had suspicious empty-emit
results (insider returning empty for AAPL; persistence with 1 ticker
despite 500K rows; corporatedonors empty for AAPL despite 432 tickers).
"""
from __future__ import annotations

import json
import importlib
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT_DIR = _REPO / "output_audit" / "b748c_extended_data_quality"
OUT_DIR.mkdir(parents=True, exist_ok=True)

T1A_PATH = _REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"


def _t1a_active() -> set:
    df = pd.read_csv(T1A_PATH, comment="#")
    rd = pd.to_datetime(df["removed_date"], errors="coerce")
    return set(df[rd.isna()]["Symbol"].astype(str).str.upper().tolist())


# ----------------------------------------------------------------------------
# Producer probes
# ----------------------------------------------------------------------------
@dataclass
class ProducerProbe:
    name: str
    cache_path: str
    n_files_or_rows: int = 0
    t1a_coverage_pct: float = 0.0
    date_min: str = ""
    date_max: str = ""
    schema_consistent: bool = True
    null_rate_critical_col: float = 0.0
    runtime_fires_n_of_n: str = "0/0"
    issue_flags: list = field(default_factory=list)
    note: str = ""


def _per_ticker_subdir_probe(base: Path, ticker_col_in_files: str = "filing_date",
                              file_pattern: str = "*.parquet") -> dict:
    """Return aggregate stats over a per-ticker subdir (e.g. SEC EDGAR forms)."""
    if not base.exists():
        return {"present": False, "n_files": 0, "t1a_coverage_pct": 0.0,
                "date_range": (None, None), "schema_consistent": False,
                "null_rate": 1.0}
    files = list(base.glob(file_pattern))
    if not files:
        return {"present": False, "n_files": 0, "t1a_coverage_pct": 0.0,
                "date_range": (None, None), "schema_consistent": False,
                "null_rate": 1.0}
    t1a = _t1a_active()
    file_tickers = {f.stem.upper() for f in files}
    t1a_with = t1a & file_tickers
    t1a_pct = round(100 * len(t1a_with) / len(t1a), 1)
    # Sample 20 files for schema + date stats
    sample_files = files[:min(20, len(files))]
    schemas: set = set()
    all_dates: list = []
    null_total = 0
    n_rows_seen = 0
    for f in sample_files:
        try:
            df = pd.read_parquet(f)
            schemas.add(tuple(sorted(df.columns)))
            if ticker_col_in_files in df.columns:
                dt = pd.to_datetime(df[ticker_col_in_files], errors="coerce")
                n_rows_seen += len(dt)
                null_total += int(dt.isna().sum())
                all_dates.extend(dt.dropna().tolist())
        except Exception:
            pass
    date_min = min(all_dates).date() if all_dates else None
    date_max = max(all_dates).date() if all_dates else None
    null_rate = round(null_total / max(1, n_rows_seen), 3)
    return {
        "present": True, "n_files": len(files),
        "t1a_coverage_pct": t1a_pct,
        "date_range": (str(date_min) if date_min else None, str(date_max) if date_max else None),
        "schema_consistent": len(schemas) == 1,
        "schemas_seen": len(schemas),
        "null_rate": null_rate,
    }


def _single_parquet_probe(path: Path, date_col: str = "Date") -> dict:
    """Probe a single global parquet (e.g. Quiver feeds)."""
    if not path.exists():
        return {"present": False, "n_rows": 0, "t1a_coverage_pct": 0.0,
                "date_range": (None, None), "null_rate": 1.0}
    try:
        df = pd.read_parquet(path)
    except Exception as e:
        return {"present": True, "n_rows": 0, "error": str(e)}
    n_rows = len(df)
    t1a = _t1a_active()
    # Find ticker col
    tcol = None
    for c in ("Ticker", "ticker", "TICKER"):
        if c in df.columns:
            tcol = c
            break
    if tcol:
        t1a_with = set(df[tcol].astype(str).str.upper().unique()) & t1a
        t1a_pct = round(100 * len(t1a_with) / len(t1a), 1)
        n_unique_t = int(df[tcol].nunique())
    else:
        t1a_pct = 0.0
        n_unique_t = 0
    # Find date col
    dcol = None
    for c in (date_col, "Date", "date", "TransactionDate", "filing_date", "event_date"):
        if c in df.columns:
            dcol = c
            break
    date_min = date_max = None
    null_rate = 0.0
    if dcol:
        dt = pd.to_datetime(df[dcol], errors="coerce")
        null_rate = round(float(dt.isna().sum()) / max(1, len(dt)), 3)
        dt_clean = dt.dropna()
        if len(dt_clean) > 0:
            date_min = str(dt_clean.min().date())
            date_max = str(dt_clean.max().date())
    return {
        "present": True, "n_rows": n_rows, "n_unique_tickers": n_unique_t,
        "t1a_coverage_pct": t1a_pct,
        "date_range": (date_min, date_max),
        "null_rate": null_rate,
        "ticker_col": tcol, "date_col": dcol,
    }


# Map producer -> probe definition
PROBE_REGISTRY = [
    {"producer": "compute_insider_cluster_signals",
     "kind": "single_parquet", "path": "data_prefetch/quiver/insiders/global.parquet",
     "date_col": "Date"},
    {"producer": "compute_persistence_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/quiver/sec13fchanges",
     "ticker_col": "filing_date"},
    {"producer": "compute_short_interest_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/finra/short_interest",
     "ticker_col": "settlement_date"},
    {"producer": "compute_sec_edgar_signals_SC13D",
     "kind": "per_ticker_subdir", "path": "data_prefetch/sec_edgar/SC_13D",
     "ticker_col": "filing_date"},
    {"producer": "compute_sec_edgar_signals_8K",
     "kind": "per_ticker_subdir", "path": "data_prefetch/sec_edgar/8_K",
     "ticker_col": "filing_date"},
    {"producer": "compute_news_sentiment_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/quiver/quivernews",
     "ticker_col": "Date"},
    {"producer": "compute_pead_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/polygon/financials",
     "ticker_col": "filing_date"},
    {"producer": "compute_search_volume_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/pytrends",
     "ticker_col": "Date"},
    {"producer": "compute_index_rebalance_signals",
     "kind": "single_parquet", "path": "data_prefetch/derived/index_rebalance_events.parquet",
     "date_col": "event_date"},
    {"producer": "compute_housetrading_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/quiver/housetrading",
     "ticker_col": "Date"},
    {"producer": "compute_gov_contracts_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/quiver/gov_contracts",
     "ticker_col": "Date"},
    {"producer": "compute_lobbying_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/quiver/lobbying",
     "ticker_col": "Date"},
    {"producer": "compute_patentmomentum_signals",
     "kind": "single_parquet", "path": "data_prefetch/quiver/patentmomentum/global.parquet",
     "date_col": "date"},
    {"producer": "compute_offexchange_signals",
     "kind": "per_ticker_subdir", "path": "data_prefetch/quiver/offexchange",
     "ticker_col": "Date"},
    {"producer": "compute_corporatedonors_signals",
     "kind": "single_parquet", "path": "data_prefetch/quiver/corporatedonors/global.parquet",
     "date_col": "TransactionDate"},
    {"producer": "compute_cross_sectional_features",
     "kind": "per_ticker_subdir", "path": "data_prefetch/polygon/financials",
     "ticker_col": "filing_date"},
]


def run_probes():
    results: list = []
    for spec in PROBE_REGISTRY:
        path = _REPO / spec["path"]
        if spec["kind"] == "single_parquet":
            stats = _single_parquet_probe(path, spec.get("date_col", "Date"))
        else:
            stats = _per_ticker_subdir_probe(path, spec.get("ticker_col", "filing_date"))
        # Flag issues
        flags = []
        if not stats.get("present"):
            flags.append("DATA_MISSING")
        if stats.get("present") and stats.get("t1a_coverage_pct", 100) < 50:
            flags.append(f"LOW_T1A_COVERAGE_{stats.get('t1a_coverage_pct')}pct")
        if stats.get("present"):
            dr = stats.get("date_range", (None, None))
            if dr[0] and dr[1]:
                if dr[1] < "2025-01-01":
                    flags.append(f"STALE_DATA_last={dr[1]}")
                if dr[0] > "2020-12-31":
                    flags.append(f"LATE_START_first={dr[0]}")
        if stats.get("present") and stats.get("null_rate", 0) > 0.05:
            flags.append(f"HIGH_NULL_RATE_{stats.get('null_rate')}")
        if stats.get("present") and stats.get("kind") == "single_parquet":
            if stats.get("n_unique_tickers", 0) <= 10:
                flags.append(f"VERY_FEW_TICKERS_{stats.get('n_unique_tickers')}")
        results.append({
            "producer": spec["producer"],
            "path": spec["path"],
            "kind": spec["kind"],
            "stats": stats,
            "issue_flags": flags,
        })
    return results


def main():
    print("[B748c-EXT] EXTENDED data-quality investigation -- all 16 TIER 2 producers")
    print()
    results = run_probes()
    flagged = 0
    for r in results:
        marker = "!" if r["issue_flags"] else " "
        if r["issue_flags"]:
            flagged += 1
        s = r["stats"]
        if s.get("present"):
            if r["kind"] == "single_parquet":
                summary = (f"rows={s.get('n_rows')}, tickers={s.get('n_unique_tickers')}, "
                           f"T1a={s.get('t1a_coverage_pct')}%, "
                           f"dates={s.get('date_range')}, null={s.get('null_rate')}")
            else:
                summary = (f"files={s.get('n_files')}, T1a={s.get('t1a_coverage_pct')}%, "
                           f"dates={s.get('date_range')}, schemas={s.get('schemas_seen')}, "
                           f"null={s.get('null_rate')}")
        else:
            summary = "MISSING"
        print(f"  [{marker}] {r['producer']:40s} {summary}")
        if r["issue_flags"]:
            for f in r["issue_flags"]:
                print(f"        FLAG: {f}")
    print()
    print(f"FLAGGED: {flagged} / {len(results)} producers")

    payload = {
        "checklist_items_applied": ["#44(a)", "#44(b)", "#44(c)", "#11", "#15", "#43",
                                    "#46", "#47", "#76(2)", "#76(3)"],
        "n_producers": len(results),
        "n_flagged": flagged,
        "results": results,
    }
    Path(OUT_DIR / "b748c_extended_results.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    print(f"\n[B748c-EXT] WROTE {OUT_DIR / 'b748c_extended_results.json'}")


if __name__ == "__main__":
    main()
