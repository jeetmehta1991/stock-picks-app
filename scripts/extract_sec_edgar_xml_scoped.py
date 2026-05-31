#!/usr/bin/env python3
"""Batch 515 (2026-05-31) -- P17a SCOPED EDGAR extraction (full universe).

Source: per CHECKLIST #77 + owner directive 2026-05-31 ("P17a extract
for scope only").
Queue row: EXECUTION_QUEUE.md item P17a.

Scope = every ticker for which we have SEC EDGAR cache index parquets
at `data_prefetch/sec_edgar/{SC_13D,SC_13G,8_K}/<TICKER>.parquet`
(~1722 tickers as of 2026-05-31). Window: 2020-2026 to cover the cube
backtest. Form 4 SKIPPED per Batch 453 (Quiver decodes).

Reuses the proven pilot logic from `scripts/extract_sec_edgar_xml_pilot.py`
(URL construction, fetch, parse, write). Verified 100% success on the
10-ticker pilot (Batch 514: 1150/1150 OK after the UA hotfix).

Volume: ~1722 tickers x 3 forms = ~5,166 (ticker, form) pairs. Average
filings per (ticker, form): pilot showed ~38 per pair (most 8-K-heavy).
Total fetches estimate: ~50,000-150,000 over 2020-2026. At 8 req/sec
that's ~6,000-19,000 seconds = 1.5-5 hours wall time. Polite throttle
guards against SEC's hard 10/sec limit.

USAGE:
  python scripts/extract_sec_edgar_xml_scoped.py --dry-run
  python scripts/extract_sec_edgar_xml_scoped.py --no-dry-run
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Reuse pilot logic; override only scope.
from scripts.extract_sec_edgar_xml_pilot import (  # noqa: E402
    extract_one_form_one_ticker,
    PILOT_FORMS,  # SC_13D / SC_13G / 8_K
)


SCOPE_YEAR_START = 2020
SCOPE_YEAR_END   = 2026

# Override pilot's window (the pilot module uses module-level constants;
# re-export via the function does NOT need overriding because
# extract_one_form_one_ticker reads PILOT_YEAR_START/_END at call time
# from the module's globals; we monkey-patch them below).


def _cached_tickers() -> list[str]:
    """Tickers with at least one cache parquet across SC_13D/SC_13G/8_K."""
    tickers: set[str] = set()
    for form in PILOT_FORMS:
        d = REPO / "data_prefetch" / "sec_edgar" / form
        if d.exists():
            for f in d.glob("*.parquet"):
                tickers.add(f.stem)
    return sorted(tickers)


def run_scoped(dry_run: bool = True, limit: int | None = None) -> dict:
    # Monkey-patch the pilot module's window to 2020-2026
    from scripts import extract_sec_edgar_xml_pilot as pilot_mod
    pilot_mod.PILOT_YEAR_START = SCOPE_YEAR_START
    pilot_mod.PILOT_YEAR_END   = SCOPE_YEAR_END

    tickers = _cached_tickers()
    if limit is not None:
        tickers = tickers[:limit]
    print(f"Scope: {len(tickers)} tickers x {len(PILOT_FORMS)} forms")
    print(f"Window: {SCOPE_YEAR_START}-{SCOPE_YEAR_END}")
    print(f"Mode: {'DRY' if dry_run else 'LIVE'}")
    print()

    total_filings = total_decoded = total_errors = 0
    started = time.time()
    for i, ticker in enumerate(tickers, start=1):
        for form in PILOT_FORMS:
            result = extract_one_form_one_ticker(form, ticker, dry_run)
            total_filings += result["n_filings"]
            total_decoded += result["n_decoded"]
            total_errors += result["error_count"]
        elapsed = time.time() - started
        rate = i / elapsed if elapsed > 0 else 0
        eta_remaining_s = (len(tickers) - i) / rate if rate > 0 else 0
        if i % 25 == 0 or i == len(tickers):
            print(f"[{i:4d}/{len(tickers)}] filings={total_filings} "
                  f"decoded={total_decoded} errors={total_errors} "
                  f"rate={rate:.2f} tk/s ETA={eta_remaining_s/60:.1f}m",
                  flush=True)
    print()
    print(f"=== SUMMARY ({len(tickers)} tickers x {len(PILOT_FORMS)} forms) ===")
    print(f"Total filings:   {total_filings}")
    print(f"Decoded:         {total_decoded}")
    print(f"Errors:          {total_errors}")
    return {"filings": total_filings, "decoded": total_decoded,
            "errors": total_errors, "tickers": len(tickers)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Build URLs without HTTP")
    p.add_argument("--no-dry-run", dest="dry_run", action="store_false",
                   help="Actually fetch + parse + write decoded parquets")
    p.add_argument("--limit", type=int, default=None,
                   help="Cap on number of tickers (for testing)")
    args = p.parse_args()
    run_scoped(args.dry_run, args.limit)


if __name__ == "__main__":
    main()
