# Source: B748e SC13D-INCREMENTAL-REFRESH owner-approved 2026-06-14 + CHECKLIST #15 + #68 per CHECKLIST #77
"""B748e -- INCREMENTAL SC_13D / SC_13D/A decoder.

Reads the freshly-refreshed INDEX cache at `data_prefetch/sec_edgar/<form>/
<TICKER>.parquet` and decodes only filings NOT already present in
`data_prefetch/sec_edgar_decoded/<form>/<TICKER>.parquet`. Appends new
rows to the decoded cache (preserves existing).

Reuses the pilot's `extract_sc_13d_fields` parser from
`backtest/signals/sec_edgar_extractor`. SEC EDGAR rate-limit honored
via `RATE_LIMIT_SLEEP_SEC`.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.extract_sec_edgar_xml_pilot import (  # noqa: E402
    RATE_LIMIT_SLEEP_SEC,
    _fetch_html,
)
from backtest.signals.sec_edgar_extractor import (  # noqa: E402
    build_edgar_filing_url,
    extract_sc_13d_fields,
)


INDEX_BASE = _REPO / "data_prefetch" / "sec_edgar"
DECODED_BASE = _REPO / "data_prefetch" / "sec_edgar_decoded"


def _decoded_accession_set(decoded_path: Path) -> set[str]:
    """Return the accession numbers already in the decoded parquet."""
    if not decoded_path.exists():
        return set()
    try:
        df = pd.read_parquet(decoded_path)
        if "accession_number" in df.columns:
            return set(df["accession_number"].astype(str).tolist())
    except Exception:
        pass
    return set()


def incremental_decode(form_name: str, form_dir_name: str,
                       limit_tickers: int | None = None,
                       dry_run: bool = False,
                       start_date: str | None = None) -> dict:
    """For each ticker in INDEX, find filings not in DECODED and decode them.

    form_name: "SC 13D" or "SC 13D/A"
    form_dir_name: "SC_13D" or "SC_13D_A"
    """
    index_dir = INDEX_BASE / form_dir_name
    decoded_dir = DECODED_BASE / form_dir_name
    decoded_dir.mkdir(parents=True, exist_ok=True)
    if not index_dir.exists():
        return {"error": f"index dir missing: {index_dir}"}
    index_files = sorted(index_dir.glob("*.parquet"))
    if limit_tickers is not None:
        index_files = index_files[:limit_tickers]
    total_new = total_decoded = total_errors = 0
    n_tickers_with_new = 0
    started = time.time()
    print(f"=== B748e incremental decode: {form_name} ({len(index_files)} tickers) ===")
    for i, idx_path in enumerate(index_files, 1):
        ticker = idx_path.stem
        decoded_path = decoded_dir / f"{ticker}.parquet"
        try:
            idx_df = pd.read_parquet(idx_path)
        except Exception:
            continue
        if idx_df.empty or "accession_number" not in idx_df.columns:
            continue
        existing = _decoded_accession_set(decoded_path)
        # Find filings in INDEX but not in DECODED
        new_rows = idx_df[~idx_df["accession_number"].astype(str).isin(existing)]
        # B748e per CHECKLIST #56 scope filter: restrict to filings after
        # start_date if specified. Matches the original ticket scope of
        # "post 2024-12-16" (the 17-month staleness gap). The broader
        # backfill of pre-2024 undecoded filings is a separate finding
        # surfaced as INV-055.
        if start_date is not None and "filing_date" in new_rows.columns:
            fd = pd.to_datetime(new_rows["filing_date"], errors="coerce")
            new_rows = new_rows[fd >= pd.Timestamp(start_date)]
        if new_rows.empty:
            continue
        n_tickers_with_new += 1
        total_new += len(new_rows)
        if dry_run:
            continue
        # Fetch + parse each new filing
        decoded_rows = []
        for _, row in new_rows.iterrows():
            cik = str(row.get("cik", ""))
            acc = str(row.get("accession_number", ""))
            doc = str(row.get("primary_doc", ""))
            if not cik or not acc or not doc:
                total_errors += 1
                continue
            try:
                url = build_edgar_filing_url(cik, acc, doc)
            except Exception:
                total_errors += 1
                continue
            time.sleep(RATE_LIMIT_SLEEP_SEC)
            html = _fetch_html(url)
            if html is None:
                total_errors += 1
                decoded_rows.append({
                    "ticker": ticker,
                    "filing_date": row["filing_date"],
                    "accession_number": acc, "primary_doc": doc,
                    "url": url,
                    "filer_identity": "", "percent_owned": None,
                    "item_4_purpose": "",
                    "decoded_status": "fetch_error",
                })
                continue
            fields = extract_sc_13d_fields(html)
            decoded_rows.append({
                "ticker": ticker,
                "filing_date": row["filing_date"],
                "accession_number": acc, "primary_doc": doc,
                "url": url,
                "filer_identity": fields.get("filer_identity", "") if fields else "",
                "percent_owned": fields.get("percent_owned") if fields else None,
                "item_4_purpose": fields.get("item_4_purpose", "") if fields else "",
                "decoded_status": "ok" if fields else "parse_failed",
            })
            total_decoded += 1
        if decoded_rows:
            new_df = pd.DataFrame(decoded_rows)
            if decoded_path.exists():
                old_df = pd.read_parquet(decoded_path)
                # Schema alignment
                for c in set(old_df.columns) | set(new_df.columns):
                    if c not in old_df.columns:
                        old_df[c] = None
                    if c not in new_df.columns:
                        new_df[c] = None
                combined = pd.concat([old_df, new_df], ignore_index=True)
            else:
                combined = new_df
            combined.to_parquet(decoded_path, index=False)
        if i % 50 == 0 or i == len(index_files):
            elapsed = time.time() - started
            rate = i / elapsed if elapsed > 0 else 0
            eta_s = (len(index_files) - i) / rate if rate > 0 else 0
            print(f"  [{i}/{len(index_files)}] new_filings={total_new}  "
                  f"decoded={total_decoded}  errors={total_errors}  "
                  f"rate={rate:.1f} tk/s  ETA={eta_s/60:.1f}m", flush=True)
    return {
        "form": form_name,
        "n_index_files": len(index_files),
        "n_tickers_with_new": n_tickers_with_new,
        "n_new_filings": total_new,
        "n_decoded": total_decoded,
        "n_errors": total_errors,
        "wall_min": (time.time() - started) / 60,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=False)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--forms", nargs="+", default=["SC 13D", "SC 13D/A"])
    p.add_argument("--start-date", type=str, default=None,
                   help="Only decode filings on/after this YYYY-MM-DD (matches B748e ticket scope)")
    args = p.parse_args()
    form_dir_map = {"SC 13D": "SC_13D", "SC 13D/A": "SC_13D_A"}
    for form in args.forms:
        if form not in form_dir_map:
            print(f"skipping unknown form: {form}")
            continue
        result = incremental_decode(form, form_dir_map[form], args.limit,
                                     args.dry_run, args.start_date)
        print(f"=== {form} summary ===")
        for k, v in result.items():
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
