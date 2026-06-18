"""B910 (2026-06-19) - sector_history.csv refresh scaffold per owner directive Dec-3.

# Source: per CHECKLIST #77 + owner directive 2026-06-19 Dec-3 (a else b)
# = Polygon ticker events primary; S&P DJI scrape fallback.

# Investigation finding: Polygon `/v3/reference/tickers/{ticker}` returns
# `sic_code` + `sic_description` (SIC classification), NOT GICS. GICS is
# owned by S&P + MSCI and not licensed to Polygon. Therefore Dec-3 (a)
# Polygon ticker events does NOT provide GICS reclassifications.

# Fallback: Dec-3 (b) S&P DJI press release scrape pattern (L88 one-time
# historical exception applies: laptop-local, manual verification, not
# runtime). This script is the SCAFFOLD that consumes manually-researched
# GICS events; it does NOT autonomously scrape S&P DJI press releases
# (that requires owner-directed data acquisition per CHECKLIST #114
# STOP #5 + L86/L95 small-test-batch rule).

Usage:
    # Validate existing sector_history.csv schema
    python scripts/refresh_sector_history.py --validate

    # Append new manually-researched GICS reclassification events
    python scripts/refresh_sector_history.py --append events.json

    # events.json schema:
    # [
    #   {
    #     "Symbol": "FLT",
    #     "Sector": "Information Technology",
    #     "added_date": "2023-03-17",
    #     "removed_date": null,
    #     "source": "S&P DJI press release 2023-03-10",
    #     "notes": "Reclassified from Financials to Information Technology"
    #   },
    #   ...
    # ]

Status (B910 2026-06-19): SCAFFOLD READY; data acquisition gap surfaced
to owner. sector_history.csv stale since 2023-03-17 affects 10
classification_change_* strategies. Per B902-A-DATA-GAP ticket.
"""
# Source: Owner directive 2026-06-19 Dec-3 + B902-A-DATA-GAP ticket +
#         B902-A-classification-change-truly-quiet-audit findings (2026-06-18).
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
SECTOR_HISTORY_CSV = REPO / "Backtesting universe" / "sector_history.csv"

REQUIRED_COLUMNS = ["Symbol", "Sector", "added_date", "removed_date"]


def validate_schema(csv_path: Path) -> dict[str, Any]:
    """Validate sector_history.csv structure + return summary stats."""
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("pandas required for schema validation") from e

    if not csv_path.exists():
        return {"status": "MISSING", "path": str(csv_path)}

    # Skip comment lines (start with #)
    df = pd.read_csv(csv_path, comment="#")

    # Schema check
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        return {"status": "SCHEMA_FAIL", "missing_columns": missing_cols}

    # Date range
    df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce")
    df["removed_date"] = pd.to_datetime(df["removed_date"], errors="coerce")

    return {
        "status": "OK",
        "path": str(csv_path),
        "total_events": len(df),
        "unique_tickers": int(df["Symbol"].nunique()),
        "added_date_range": [
            str(df["added_date"].min().date()) if not df["added_date"].isna().all() else None,
            str(df["added_date"].max().date()) if not df["added_date"].isna().all() else None,
        ],
        "last_event_date": str(df["added_date"].max().date()) if not df["added_date"].isna().all() else None,
        "days_stale_from_today": (
            (date.today() - df["added_date"].max().date()).days
            if not df["added_date"].isna().all() else None
        ),
    }


def append_events(events_json_path: Path, dry_run: bool = True) -> dict[str, Any]:
    """Append manually-researched GICS reclassification events to sector_history.csv.

    Validates each event against required schema before append. Sorts by
    added_date. Preserves existing comment-header lines.
    """
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("pandas required for append") from e

    with open(events_json_path) as f:
        new_events = json.load(f)

    if not isinstance(new_events, list):
        raise ValueError(f"events JSON must be a list; got {type(new_events).__name__}")

    # Validate each event
    invalid = []
    for i, ev in enumerate(new_events):
        if not isinstance(ev, dict):
            invalid.append({"index": i, "reason": "not a dict", "value": str(ev)[:100]})
            continue
        for col in REQUIRED_COLUMNS:
            if col not in ev:
                invalid.append({"index": i, "reason": f"missing {col}", "ticker": ev.get("Symbol", "?")})

    if invalid:
        return {"status": "VALIDATION_FAIL", "invalid_events": invalid[:10], "total_invalid": len(invalid)}

    # Read existing comment header
    with open(SECTOR_HISTORY_CSV, "r", encoding="utf-8") as f:
        lines = f.readlines()
    header_lines = [ln for ln in lines if ln.startswith("#")]

    # Read existing data
    df_existing = pd.read_csv(SECTOR_HISTORY_CSV, comment="#")
    df_new = pd.DataFrame(new_events)

    # Use only required columns (preserve source/notes in commented section if present)
    df_new_canonical = df_new[REQUIRED_COLUMNS].copy()

    # Combine + sort
    df_combined = pd.concat([df_existing, df_new_canonical], ignore_index=True)
    df_combined = df_combined.sort_values("added_date").reset_index(drop=True)

    if dry_run:
        return {
            "status": "DRY_RUN_OK",
            "existing_events": len(df_existing),
            "new_events": len(df_new_canonical),
            "combined_events": len(df_combined),
            "would_write_to": str(SECTOR_HISTORY_CSV),
        }

    # Write
    with open(SECTOR_HISTORY_CSV, "w", encoding="utf-8") as f:
        for hl in header_lines:
            f.write(hl)
        df_combined.to_csv(f, index=False)

    return {
        "status": "WRITTEN",
        "path": str(SECTOR_HISTORY_CSV),
        "existing_events": len(df_existing),
        "new_events": len(df_new_canonical),
        "combined_events": len(df_combined),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B910 sector_history.csv refresh scaffold per Dec-3.",
    )
    parser.add_argument("--validate", action="store_true", help="Validate schema + show staleness")
    parser.add_argument("--append", type=Path, help="JSON file of new GICS reclassification events")
    parser.add_argument("--commit", action="store_true", help="Commit append (default dry-run)")
    args = parser.parse_args()

    if args.validate:
        result = validate_schema(SECTOR_HISTORY_CSV)
        print(json.dumps(result, indent=2))
        return 0

    if args.append:
        if not args.append.exists():
            print(f"ERROR: events JSON not found: {args.append}", file=sys.stderr)
            return 1
        result = append_events(args.append, dry_run=not args.commit)
        print(json.dumps(result, indent=2))
        return 0

    print(
        "B910 sector_history.csv refresh scaffold.\n"
        "\n"
        "Dec-3 INVESTIGATION FINDING: Polygon /v3/reference/tickers does NOT provide\n"
        "GICS reclassifications (returns SIC; GICS is S&P/MSCI licensed). Dec-3 (a)\n"
        "primary fails. Dec-3 (b) S&P DJI press release scrape is owner-directed\n"
        "manual data acquisition per L88 + #114 STOP #5.\n"
        "\n"
        "USAGE:\n"
        "  python scripts/refresh_sector_history.py --validate\n"
        "    Validate existing CSV schema + report staleness.\n"
        "\n"
        "  python scripts/refresh_sector_history.py --append events.json\n"
        "    Dry-run: validate JSON schema + report what would change.\n"
        "\n"
        "  python scripts/refresh_sector_history.py --append events.json --commit\n"
        "    Write the combined CSV (Symbol,Sector,added_date,removed_date).\n"
        "\n"
        "DATA SOURCE: GICS reclassifications must be manually researched from\n"
        "S&P DJI press releases (Indices.News@spglobal.com archive). 14 events\n"
        "from 2023-03-17 already in CSV (per Batch 561+561a). Post-2023-03-17 gap.\n",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
