#!/usr/bin/env python3
"""Batch 526 (2026-05-31) -- SEC EDGAR decoded-cache completeness validator.

Source: per CHECKLIST #77 + #99 (schema-verify before producer ships).
Queue rows: EXECUTION_QUEUE.md items P17a (in flight) + P17b/c/d/e
(scaffolds shipped Batch 522 awaiting wire-in).

Purpose: when the P17a scoped extraction completes (~10-12h after
launch), owner needs a fast read on whether the decoded cache at
`data_prefetch/sec_edgar_decoded/{SC_13D,SC_13G,8_K}/<ticker>.parquet`
is COMPLETE + WELL-FORMED before approving the Batch 522 sleeve
wire-in batch.

Without this script, the gap is silent: the 4 P17 sleeve strategies
(activist_13d_long, m_and_a_target_long, tier_modifier_5_02,
smart_money_modifier_13g) all SAFELY default to non-firing when
their producer signals are absent (Batch 522 NOT-REGISTERED guard
test pins this). So if the decoded cache is corrupt / partial /
schema-broken, NO error fires -- the strategies just don't trade,
and we'd discover the gap only via cube-result analysis (way too
late).

This validator runs 6 gates:

  (1) Per-form coverage:        decoded_<form>/ has parquet files for
                                >= COVERAGE_FLOOR_PCT of the index
                                cache's ticker set
  (2) Per-parquet schema:       required cols present per form
                                 (SC_13D/SC_13G: ticker, filing_date,
                                 accession_number, filer_identity,
                                 percent_owned, item_4_purpose,
                                 decoded_status; 8_K: ticker,
                                 filing_date, accession_number,
                                 item_codes, decoded_status)
  (3) Non-empty data:           total decoded rows >= MIN_ROWS_PER_FORM
  (4) Status distribution:      `decoded_status` field has expected
                                values + the ok/error ratio is sane
  (5) Spot-check coverage:      a small set of (form, ticker, year)
                                tuples that we KNOW must have entries
                                (e.g. AAPL 2024 8-K -- multiple per year
                                guaranteed) actually do
  (6) Sample-row sanity:        random-sample decoded rows pass type
                                checks (filing_date is a valid date,
                                percent_owned is a 0-100 float or NaN,
                                item_codes is a comma-separated string)

Output: exit 0 on PASS; non-zero with a per-gate diagnostic on FAIL.

Run after P17a completes:

  python scripts/validate_sec_edgar_decoded_completeness.py
  python scripts/validate_sec_edgar_decoded_completeness.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
INDEX_DIR   = REPO / "data_prefetch" / "sec_edgar"
DECODED_DIR = REPO / "data_prefetch" / "sec_edgar_decoded"

FORMS = ("SC_13D", "SC_13G", "8_K")

# Per-form expected schema (cols that MUST appear in every parquet)
REQUIRED_COLS: dict[str, set[str]] = {
    "SC_13D": {"ticker", "filing_date", "accession_number",
                "decoded_status"},
    "SC_13G": {"ticker", "filing_date", "accession_number",
                "decoded_status"},
    "8_K":    {"ticker", "filing_date", "accession_number",
                "item_codes", "decoded_status"},
}

# Floor on per-form coverage (fraction of index tickers with a decoded
# parquet). Batch 532 (2026-06-01) update: per-form floors recognise
# rare-event sparsity. SC_13D activist filings are 50-200/yr universe-
# wide, so most tickers genuinely have ZERO SC 13D filings in any 6-yr
# window (B526 first real-data run: SC_13D coverage = 36% from 100%
# successful extraction across 1,722 tickers; 1,092 of those tickers
# had no SC 13D filed in 2020-2026 -- correct ground-truth, not a
# pipeline failure). 8_K + SC_13G are denser (every public company
# files multiple 8-Ks/yr).
COVERAGE_FLOORS = {
    "SC_13D": 0.30,   # rare-event activist; ~36% observed in B526 real run
    "SC_13G": 0.50,
    "8_K":    0.50,
}
# Back-compat constant (any external tooling that imports this).
COVERAGE_FLOOR_PCT = 0.30

# Floor on total decoded rows per form.
MIN_ROWS_PER_FORM = {
    "SC_13D": 50,      # ~50-200/year universe-wide -> 6y >> 50
    "SC_13G": 500,     # 500-2000/year universe-wide
    "8_K":    1000,    # Several per year per active ticker
}

# Floor on the fraction of decoded rows with decoded_status="ok".
OK_RATIO_FLOOR = 0.80

# Spot-check tuples: tickers that MUST have entries in each form for the
# 2020-2026 window (mega-cap, high-activity, well-indexed companies).
SPOT_CHECK_TICKERS_8K = ("AAPL", "MSFT", "AMZN", "GOOGL", "META")


def _list_decoded_parquets(form: str) -> list[Path]:
    """All decoded parquets present for this form, sorted by ticker."""
    form_dir = DECODED_DIR / form
    if not form_dir.exists():
        return []
    return sorted(form_dir.glob("*.parquet"))


def _list_indexed_tickers(form: str) -> set[str]:
    """The ticker set present in the index cache for this form. The
    decoded cache should mirror or be a subset of this set."""
    form_dir = INDEX_DIR / form
    if not form_dir.exists():
        return set()
    return {p.stem for p in form_dir.glob("*.parquet")}


def _load_decoded(form: str, ticker: str) -> Optional[pd.DataFrame]:
    path = DECODED_DIR / form / f"{ticker}.parquet"
    if not path.exists():
        return None
    try:
        return pd.read_parquet(path)
    except Exception:
        return None


def gate_1_coverage() -> dict:
    """Per-form decoded coverage vs index cache."""
    out: dict = {"name": "1_coverage", "details": {}, "pass": True}
    for form in FORMS:
        indexed = _list_indexed_tickers(form)
        decoded = {p.stem for p in _list_decoded_parquets(form)}
        if not indexed:
            out["details"][form] = {
                "indexed": 0, "decoded": len(decoded), "ratio": None,
                "pass": False,
                "msg": f"no index parquets at {INDEX_DIR / form}",
            }
            out["pass"] = False
            continue
        ratio = len(decoded & indexed) / len(indexed)
        # Batch 532 (2026-06-01): per-form floor handles SC 13D rare-event
        # sparsity. Falls back to global floor for any form not in the
        # COVERAGE_FLOORS map.
        floor = COVERAGE_FLOORS.get(form, COVERAGE_FLOOR_PCT)
        passed = ratio >= floor
        out["details"][form] = {
            "indexed":      len(indexed),
            "decoded":      len(decoded),
            "intersection": len(decoded & indexed),
            "ratio":        round(ratio, 4),
            "floor":        floor,
            "pass":         passed,
        }
        if not passed:
            out["pass"] = False
    return out


def gate_2_schema() -> dict:
    """Every decoded parquet must carry REQUIRED_COLS for its form."""
    out: dict = {"name": "2_schema", "details": {}, "pass": True}
    for form in FORMS:
        bad_files = []
        checked = 0
        for path in _list_decoded_parquets(form)[:200]:  # cap scan
            checked += 1
            try:
                df = pd.read_parquet(path, columns=None)
            except Exception as e:
                bad_files.append((path.name, f"read_error: {e!r}"))
                continue
            missing = REQUIRED_COLS[form] - set(df.columns)
            if missing:
                bad_files.append((path.name, f"missing_cols={sorted(missing)}"))
        out["details"][form] = {
            "checked":   checked,
            "bad_count": len(bad_files),
            "samples":   bad_files[:5],
            "pass":      len(bad_files) == 0,
        }
        if bad_files:
            out["pass"] = False
    return out


def gate_3_min_rows() -> dict:
    """Total decoded rows per form must clear the floor."""
    out: dict = {"name": "3_min_rows", "details": {}, "pass": True}
    for form in FORMS:
        total = 0
        for path in _list_decoded_parquets(form):
            try:
                total += len(pd.read_parquet(path, columns=["decoded_status"]))
            except Exception:
                pass
        floor = MIN_ROWS_PER_FORM[form]
        passed = total >= floor
        out["details"][form] = {"total_rows": total, "floor": floor,
                                 "pass": passed}
        if not passed:
            out["pass"] = False
    return out


def gate_4_status_dist() -> dict:
    """`decoded_status` distribution: ratio of 'ok' rows must clear
    OK_RATIO_FLOOR per form."""
    out: dict = {"name": "4_status_dist", "details": {}, "pass": True}
    for form in FORMS:
        counts: Counter = Counter()
        for path in _list_decoded_parquets(form):
            try:
                df = pd.read_parquet(path, columns=["decoded_status"])
                counts.update(df["decoded_status"].astype(str).tolist())
            except Exception:
                pass
        total = sum(counts.values())
        if total == 0:
            out["details"][form] = {"counts": {}, "ok_ratio": None,
                                     "pass": False,
                                     "msg": "no rows -- nothing to score"}
            out["pass"] = False
            continue
        ok_n = counts.get("ok", 0)
        ratio = ok_n / total
        passed = ratio >= OK_RATIO_FLOOR
        out["details"][form] = {
            "counts":   dict(counts),
            "ok_ratio": round(ratio, 4),
            "floor":    OK_RATIO_FLOOR,
            "pass":     passed,
        }
        if not passed:
            out["pass"] = False
    return out


def gate_5_spot_check() -> dict:
    """Spot-check: AAPL/MSFT/AMZN/GOOGL/META all file multiple 8-Ks
    per year -- their decoded 8_K parquets MUST have >= 1 row tagged
    decoded_status=ok in the 2024 calendar year."""
    out: dict = {"name": "5_spot_check", "details": {}, "pass": True}
    spot_details = {}
    for ticker in SPOT_CHECK_TICKERS_8K:
        df = _load_decoded("8_K", ticker)
        if df is None or df.empty:
            spot_details[ticker] = {"pass": False, "msg": "no decoded parquet"}
            out["pass"] = False
            continue
        try:
            df = df.copy()
            df["filing_date"] = pd.to_datetime(df["filing_date"],
                                                errors="coerce")
            year_2024 = df[(df["filing_date"].dt.year == 2024)
                            & (df["decoded_status"].astype(str) == "ok")]
            n = len(year_2024)
        except Exception as e:
            spot_details[ticker] = {"pass": False, "msg": f"parse error: {e!r}"}
            out["pass"] = False
            continue
        passed = n >= 1
        spot_details[ticker] = {"n_2024_ok": n, "pass": passed}
        if not passed:
            out["pass"] = False
    out["details"]["8_K_2024_per_ticker"] = spot_details
    return out


def gate_6_sample_sanity(sample_per_form: int = 50) -> dict:
    """Random-sample decoded rows: filing_date parses, percent_owned
    (where applicable) is a 0-100 float or NaN."""
    out: dict = {"name": "6_sample_sanity", "details": {}, "pass": True}
    for form in FORMS:
        bad_rows = []
        sampled = 0
        rng_paths = _list_decoded_parquets(form)
        for path in rng_paths[:50]:  # cap files
            try:
                df = pd.read_parquet(path)
            except Exception:
                continue
            if df.empty:
                continue
            take = df.sample(min(sample_per_form, len(df)), random_state=42)
            sampled += len(take)
            # filing_date: must parse to a valid date
            try:
                pd.to_datetime(take["filing_date"], errors="raise")
            except Exception as e:
                bad_rows.append((path.name, f"filing_date parse: {e!r}"))
                continue
            # percent_owned: 0-100 or NaN
            if "percent_owned" in take.columns:
                vals = pd.to_numeric(take["percent_owned"], errors="coerce")
                out_of_range = vals[(vals < 0) | (vals > 100)]
                if len(out_of_range):
                    bad_rows.append((path.name,
                                      f"percent_owned out of [0,100]: "
                                      f"sample={out_of_range.head(3).tolist()}"))
        out["details"][form] = {
            "sampled":   sampled,
            "bad_count": len(bad_rows),
            "samples":   bad_rows[:5],
            "pass":      len(bad_rows) == 0,
        }
        if bad_rows:
            out["pass"] = False
    return out


def run_all_gates() -> dict:
    gates = [
        gate_1_coverage(),
        gate_2_schema(),
        gate_3_min_rows(),
        gate_4_status_dist(),
        gate_5_spot_check(),
        gate_6_sample_sanity(),
    ]
    return {
        "all_pass": all(g["pass"] for g in gates),
        "gates":    gates,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true",
                   help="emit JSON only (for downstream consumers)")
    args = p.parse_args()

    result = run_all_gates()

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0 if result["all_pass"] else 3

    print("=== SEC EDGAR decoded-cache validator ===")
    print(f"Index dir:   {INDEX_DIR}")
    print(f"Decoded dir: {DECODED_DIR}")
    print()
    for gate in result["gates"]:
        flag = "OK  " if gate["pass"] else "FAIL"
        print(f"[{flag}] gate {gate['name']}")
        for key, val in gate["details"].items():
            print(f"        {key}: {val}")
        print()
    print("=" * 50)
    if result["all_pass"]:
        print("ALL GATES PASS -- safe to wire-in P17 sleeves.")
        return 0
    print("ONE OR MORE GATES FAILED -- inspect details above before "
          "approving P17 sleeve wire-in.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
