"""scripts/data_readiness_audit.py - one-shot pre-R5 data-readiness audit.

# Source: per CHECKLIST #77 canonical-source; B1264 Council 305
# S6-B1259-DATA-READINESS-AUDIT owner-approved 2026-07-08 (decision B:
# audit BEFORE scope lock; replaces the serial-gap-discovery pattern that
# found news/shares_outstanding/rebalance/triangle gaps one at a time).

For every data source the producers consume, emits:
  - presence (dir exists, file count)
  - ticker coverage vs the R5 universe reference (Master Dedup CSV)
  - temporal span (min/max dates across sampled files, per CHECKLIST #156)
  - known-critical field checks (FINRA shares_outstanding NULL-rate,
    persistence T1a coverage, rebalance parquet presence, VIX series)

Output: output_audit/DATA_READINESS_AUDIT_<date>.json (machine) +
prints a summary table (human). Re-runnable at every R5 ladder rung.

Usage: python scripts/data_readiness_audit.py [--sample N]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DP = REPO / "data_prefetch"
sys.path.insert(0, str(REPO))

import pandas as pd  # noqa: E402


def load_universe() -> set:
    """R5 universe reference = Master Dedup CSV symbols."""
    candidates = list((REPO / "Backtesting universe").glob("*aster*edup*.csv"))
    if not candidates:
        candidates = list((REPO / "Backtesting universe").glob("*Master*.csv"))
    if not candidates:
        return set()
    df = pd.read_csv(candidates[0], comment="#")
    col = "Symbol" if "Symbol" in df.columns else df.columns[0]
    return set(df[col].dropna().astype(str).str.upper())


def per_ticker_dir_report(dir_path: Path, universe: set, sample: int,
                          date_cols=("date", "published_date", "settlement_date",
                                     "datetime", "filed_date", "transaction_date")) -> dict:
    """Generic per-ticker parquet dir: coverage + temporal span (sampled)."""
    if not dir_path.exists():
        return {"present": False}
    files = list(dir_path.glob("*.parquet"))
    tickers = {f.stem.replace("-", ".").upper() for f in files}
    covered = len(tickers & universe) if universe else len(tickers)
    dmin, dmax, checked = None, None, 0
    step = max(1, len(files) // max(sample, 1))
    for f in files[::step][:sample]:
        try:
            df = pd.read_parquet(f)
        except Exception:
            continue
        checked += 1
        for c in date_cols:
            if c in df.columns and len(df):
                try:
                    s = pd.to_datetime(df[c], errors="coerce", unit=(
                        "s" if df[c].dtype.kind in "iu" and df[c].max() > 1e9 else None))
                except (TypeError, ValueError):
                    s = pd.to_datetime(df[c], errors="coerce")
                s = s.dropna()
                if len(s):
                    lo, hi = str(s.min().date()), str(s.max().date())
                    dmin = lo if dmin is None or lo < dmin else dmin
                    dmax = hi if dmax is None or hi > dmax else dmax
                break
    return {"present": True, "files": len(files),
            "universe_coverage": covered,
            "universe_coverage_pct": round(100 * covered / len(universe), 1) if universe else None,
            "sampled": checked, "date_min": dmin, "date_max": dmax}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=25,
                    help="files sampled per source for temporal span (CHECKLIST #154 floor)")
    args = ap.parse_args()

    universe = load_universe()
    report: dict = {"audit_date": str(date.today()),
                    "universe_size": len(universe), "sources": {}}
    S = report["sources"]

    # -- OHLCV (the backbone) --
    ohlcv_dirs = [REPO / "backtest" / "data" / "cache" / "ohlcv",
                  DP / "polygon" / "ohlcv_daily"]
    for d in ohlcv_dirs:
        S[f"ohlcv:{d.relative_to(REPO)}"] = per_ticker_dir_report(d, universe, args.sample)

    # -- per-ticker prefetch sources --
    per_ticker_sources = {
        "finra_short_interest": DP / "finra" / "short_interest",
        "finnhub_profile2": DP / "finnhub" / "profile2",
        "finnhub_company_news": DP / "finnhub" / "company_news",
        "polygon_news": DP / "polygon" / "news",
        "quiver_congress": DP / "quiver" / "congressional",
        "quiver_insider": DP / "quiver" / "insider",
        "quiver_institutional": DP / "quiver" / "institutional",
        "sec_edgar_13d": DP / "sec_edgar" / "SC_13D",
        "sec_edgar_8k": DP / "sec_edgar" / "8_K",
        # earnings dates derive from polygon financials filing_date
        # (fetcher.fetch_earnings_dates:244-248) - no separate earnings dir
        "polygon_financials_earnings_source": DP / "polygon" / "financials",
    }
    for name, d in per_ticker_sources.items():
        # tolerate alternate layouts: if dir missing, try first existing child match
        if not d.exists() and d.parent.exists():
            alts = [c for c in d.parent.iterdir() if c.is_dir()
                    and d.name.split("_")[-1][:6] in c.name]
            if alts:
                d = alts[0]
        S[name] = per_ticker_dir_report(d, universe, args.sample)
        S[name]["path"] = str(d.relative_to(REPO)) if d.exists() else str(d)

    # -- singleton/critical artifacts --
    crit = {
        "index_rebalance_events": REPO / "Backtesting universe" / "index_rebalance_events.parquet",
        "fred_vixcls": DP / "fred" / "observations" / "VIXCLS.parquet",
        "fred_t10y2y": DP / "fred" / "observations" / "T10Y2Y.parquet",
        "aaii_weekly": DP / "aaii" / "weekly_sentiment.parquet",
        "institutional_persistence_t1a": DP / "derived" / "institutional_persistence_t1a",
        "cointegrated_pairs_t1a": DP / "derived" / "cointegrated_pairs_t1a",
    }
    for name, p in crit.items():
        if p.suffix == ".parquet":
            entry = {"present": p.exists()}
            if p.exists():
                try:
                    df = pd.read_parquet(p)
                    entry["rows"] = len(df)
                except Exception as exc:
                    entry["read_error"] = str(exc)[:120]
            S[name] = entry
        else:
            S[name] = per_ticker_dir_report(p, universe, args.sample)

    # -- known-critical field checks --
    # FINRA shares_outstanding NULL rate (B1214/B1240 finding class)
    finra = DP / "finra" / "short_interest"
    if finra.exists():
        nulls, rows = 0, 0
        for f in list(finra.glob("*.parquet"))[:args.sample]:
            try:
                df = pd.read_parquet(f)
                if "shares_outstanding" in df.columns:
                    # null OR <=0 counted once (fillna(0) folds NaN into <=0)
                    nulls += int((df["shares_outstanding"].fillna(0) <= 0).sum())
                    rows += len(df)
            except Exception:
                continue
        S["finra_short_interest"]["shares_outstanding_null_or_zero_rate"] = (
            round(nulls / rows, 3) if rows else None)

    # VIX consumability (B1250 regime-hysteresis dependency)
    try:
        from backtest.data.macro import get_vix
        vdf = get_vix(date(2020, 1, 1), date.today())
        S["fred_vixcls"]["get_vix_rows"] = 0 if vdf is None else len(vdf)
    except Exception as exc:
        S["fred_vixcls"]["get_vix_error"] = str(exc)[:120]

    out = REPO / "output_audit" / f"DATA_READINESS_AUDIT_{date.today().isoformat()}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # human summary
    print(f"DATA READINESS AUDIT {report['audit_date']} | universe={len(universe)}")
    for name, e in S.items():
        if not e.get("present"):
            print(f"  MISSING   {name}")
            continue
        cov = e.get("universe_coverage_pct")
        span = f"{e.get('date_min')}..{e.get('date_max')}" if e.get("date_min") else "-"
        extra = ""
        if "shares_outstanding_null_or_zero_rate" in e:
            extra = f" so_null_rate={e['shares_outstanding_null_or_zero_rate']}"
        if "rows" in e:
            extra += f" rows={e['rows']}"
        if "get_vix_rows" in e:
            extra += f" get_vix_rows={e['get_vix_rows']}"
        print(f"  ok        {name}: files={e.get('files', '-')} cov={cov}% span={span}{extra}")
    print(f"written: {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
