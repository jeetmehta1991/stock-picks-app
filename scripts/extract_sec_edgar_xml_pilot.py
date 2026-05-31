#!/usr/bin/env python3
"""Batch 509 (2026-05-31) -- P17a SEC EDGAR pilot extractor.

Source: per CHECKLIST #77 + owner directive 2026-05-31 (P17a option =
pilot 10 tickers x 5 years).
Queue row: EXECUTION_QUEUE.md item P17a.

Pilot scope: 10 hand-picked SP500 names x 2021-2026 (5 yrs) x 3 forms
(SC 13D, SC 13G, 8-K) = ~300-1000 HTTP fetches at SEC EDGAR's 10/sec
rate limit (throttled to 8/sec for safety) = ~3 minutes wall time.

The pilot validates the extractor against REAL EDGAR HTML before
committing to the full ~300k extraction. Owner approves scale-up after
pilot output looks correct.

USAGE (operator-run after owner approval):

  python scripts/extract_sec_edgar_xml_pilot.py --dry-run
  python scripts/extract_sec_edgar_xml_pilot.py --no-dry-run

Outputs to `data_prefetch/sec_edgar_decoded/<form>/<TICKER>.parquet`.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional
import urllib.error
import urllib.request

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
# Allow direct script invocation (python scripts/...) without PYTHONPATH.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Pilot ticker set (10 SP500 names with diverse SEC activity)
PILOT_TICKERS = (
    "AAPL", "MSFT", "AMZN", "GOOGL", "META",
    "JPM", "DIS", "NFLX", "KO", "XOM",
)

PILOT_YEAR_START = 2021
PILOT_YEAR_END   = 2026

# Forms to extract (Form 4 SKIPPED per Batch 453 -- Quiver already decodes)
PILOT_FORMS = ("SC_13D", "SC_13G", "8_K")

# SEC EDGAR rate limit: 10 req/sec. Throttle to 8/sec for safety.
RATE_LIMIT_SLEEP_SEC = 0.125

# SEC requires identifiable User-Agent in `Name email@domain.com` format.
# Batch 518 (2026-05-31): UA hotfix -- prior "jeetmehta1991-stock-picks-
# app/1.0 (...@noreply...)" returned 403. SEC's standard format accepted.
USER_AGENT = "Stock Picks Research jeetmehta1991@gmail.com"


def _filter_pilot_window(df: pd.DataFrame) -> pd.DataFrame:
    """Filter cache rows to PILOT_YEAR_START-PILOT_YEAR_END window."""
    if df.empty or "filing_date" not in df.columns:
        return df.iloc[0:0]
    df = df.copy()
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    mask = (
        (df["filing_date"].dt.year >= PILOT_YEAR_START)
        & (df["filing_date"].dt.year <= PILOT_YEAR_END)
    )
    return df[mask].reset_index(drop=True)


def _fetch_html(url: str, timeout: int = 30) -> Optional[str]:
    """Fetch the HTML body of an EDGAR primary_doc URL.

    Returns text content or None on error. Honors SEC's User-Agent
    requirement (rejection without UA is HTTP 403).
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def extract_one_form_one_ticker(
    form: str,
    ticker: str,
    dry_run: bool = True,
) -> dict:
    """Extract a single (form, ticker) decoded parquet.

    Returns a manifest dict {status, n_filings, n_decoded, error_count}.
    On --dry-run, builds URLs + reports counts WITHOUT making HTTP calls.
    """
    from backtest.signals.sec_edgar_extractor import (
        build_edgar_filing_url,
        extract_8k_item_codes,
        extract_sc_13d_fields,
    )
    safe = ticker.replace(".", "-").upper()
    idx_path = REPO / "data_prefetch" / "sec_edgar" / form / f"{safe}.parquet"
    out_dir  = REPO / "data_prefetch" / "sec_edgar_decoded" / form
    out_path = out_dir / f"{safe}.parquet"
    if not idx_path.exists():
        return {"status": "no_index_cache", "n_filings": 0, "n_decoded": 0,
                "error_count": 0, "ticker": ticker, "form": form}
    idx_df = pd.read_parquet(idx_path)
    idx_df = _filter_pilot_window(idx_df)
    n_filings = len(idx_df)
    if n_filings == 0:
        return {"status": "empty_window", "n_filings": 0, "n_decoded": 0,
                "error_count": 0, "ticker": ticker, "form": form}
    rows = []
    err = 0
    for _, row in idx_df.iterrows():
        cik = str(row.get("cik", ""))
        acc = str(row.get("accession_number", ""))
        doc = str(row.get("primary_doc", ""))
        if not cik or not acc or not doc:
            err += 1
            continue
        try:
            url = build_edgar_filing_url(cik, acc, doc)
        except ValueError:
            err += 1
            continue
        if dry_run:
            rows.append({
                "ticker":             ticker,
                "filing_date":        row["filing_date"],
                "accession_number":   acc,
                "primary_doc":        doc,
                "url":                url,
                "decoded_status":     "dry_run",
            })
            continue
        # Real fetch + parse
        time.sleep(RATE_LIMIT_SLEEP_SEC)
        html = _fetch_html(url)
        if html is None:
            err += 1
            rows.append({"ticker": ticker, "filing_date": row["filing_date"],
                         "accession_number": acc, "primary_doc": doc,
                         "url": url, "decoded_status": "fetch_error"})
            continue
        if form == "8_K":
            item_codes = extract_8k_item_codes(html)
            rows.append({
                "ticker":           ticker,
                "filing_date":      row["filing_date"],
                "accession_number": acc,
                "primary_doc":      doc,
                "url":              url,
                "item_codes":       ",".join(item_codes),
                "decoded_status":   "ok",
            })
        elif form in ("SC_13D", "SC_13G"):
            fields = extract_sc_13d_fields(html)
            rows.append({
                "ticker":           ticker,
                "filing_date":      row["filing_date"],
                "accession_number": acc,
                "primary_doc":      doc,
                "url":              url,
                "filer_identity":   fields["filer_identity"],
                "percent_owned":    fields["percent_owned"],
                "item_4_purpose":   fields["item_4_purpose"],
                "decoded_status":   "ok",
            })
        else:
            err += 1
    decoded = pd.DataFrame(rows)
    if not dry_run and not decoded.empty:
        out_dir.mkdir(parents=True, exist_ok=True)
        decoded.to_parquet(out_path, index=False)
    return {
        "status":      "ok",
        "n_filings":   n_filings,
        "n_decoded":   len([r for r in rows if r.get("decoded_status") == "ok"]),
        "error_count": err,
        "ticker":      ticker,
        "form":        form,
        "output":      str(out_path) if not dry_run else "dry_run",
    }


def run_pilot(dry_run: bool = True,
               tickers: tuple[str, ...] = PILOT_TICKERS,
               forms: tuple[str, ...] = PILOT_FORMS) -> list[dict]:
    """Iterate (form, ticker) for the pilot scope; return manifest list."""
    manifest = []
    for form in forms:
        for ticker in tickers:
            result = extract_one_form_one_ticker(form, ticker, dry_run)
            manifest.append(result)
            print(f"[{form:6s} {ticker:6s}] {result['status']} "
                  f"filings={result['n_filings']} "
                  f"decoded={result['n_decoded']} "
                  f"errors={result['error_count']}")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", default=True,
                   help="Build URLs + count filings WITHOUT HTTP calls "
                        "(default: dry-run for safety)")
    p.add_argument("--no-dry-run", dest="dry_run", action="store_false",
                   help="Actually fetch + parse + write decoded parquets")
    p.add_argument("--tickers", nargs="*", default=None,
                   help="Override pilot ticker list")
    p.add_argument("--forms", nargs="*", default=None,
                   help="Override pilot form list")
    args = p.parse_args()
    tickers = tuple(args.tickers) if args.tickers else PILOT_TICKERS
    forms = tuple(args.forms) if args.forms else PILOT_FORMS
    print(f"Pilot mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print(f"Tickers: {tickers}")
    print(f"Forms:   {forms}")
    print(f"Window:  {PILOT_YEAR_START}-{PILOT_YEAR_END}")
    print(f"User-Agent: {USER_AGENT}")
    print()
    manifest = run_pilot(args.dry_run, tickers, forms)
    # Summary
    total_filings = sum(m["n_filings"] for m in manifest)
    total_decoded = sum(m["n_decoded"] for m in manifest)
    total_errors  = sum(m["error_count"] for m in manifest)
    print()
    print(f"=== SUMMARY ===")
    print(f"Total filings in pilot window: {total_filings}")
    print(f"Decoded successfully:          {total_decoded}")
    print(f"Errors:                        {total_errors}")
    print(f"Output: data_prefetch/sec_edgar_decoded/<form>/<TICKER>.parquet")


if __name__ == "__main__":
    main()
