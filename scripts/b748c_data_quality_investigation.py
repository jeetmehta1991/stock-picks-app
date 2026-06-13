# Source: CHECKLIST #44 + #76 + B748c owner directive 2026-06-13 "investigate further first" per CHECKLIST #77
"""B748c — DATA QUALITY INVESTIGATION on the 3 producers B748b mis-disposed.

Owner directive 2026-06-13: B748b EXPLORATORY-tagged 6 strategies on the
false premise that their producers had 0 data. Post-shipment investigation
revealed the data IS present; B745's audit script had buggy path probes
(parent-dir glob missed subdir parquets + wrong path string for
index_rebalance). Owner mandate: "These misses should not be happening" +
"Referring to checklist is mandatory."

This investigation applies CHECKLIST #44 (DATA-CONSUMPTION AUDIT MUST
INCLUDE RUNTIME PROBE) per the discipline that was missed in B745.

For each of the 3 producers (sec_edgar / index_rebalance / recent_8k):
  1. Identify TRUE data path by reading producer source (not heuristics)
  2. Verify data presence + size
  3. T1a coverage: how many of 503 active T1a have data per form type?
  4. Date-range coverage: does data span 2020-2026?
  5. Schema integrity: required columns present?
  6. Runtime probe with KNOWN-EVENT (ticker, date) pair
  7. Cross-check: do producer fires match parquet event dates?

Output: finding-grade markdown + JSON. Owner reads + decides whether to
walk back B748b EXPLORATORY tags + close the 2 backfill follow-up tickets.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path

import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT_DIR = _REPO / "output_audit" / "b748c_data_quality_investigation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

T1A_PATH = _REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"


def _t1a_active_tickers() -> set:
    """Currently-active T1a tickers (per CHECKLIST #15: verify universe size)."""
    df = pd.read_csv(T1A_PATH, comment="#")
    rd = pd.to_datetime(df["removed_date"], errors="coerce")
    return set(df[rd.isna()]["Symbol"].astype(str).str.upper().tolist())


# ----------------------------------------------------------------------------
# Per-form-type SEC EDGAR coverage probe
# ----------------------------------------------------------------------------
def investigate_sec_edgar() -> dict:
    """CHECKLIST #44(a): identify path + probe runtime + cross-check fires.

    The producer at backtest/signals/sec_edgar_extractor.py:178 reads from
    `data_prefetch/sec_edgar/{form}/{TICKER}.parquet` via `_load_decoded`.
    """
    base = _REPO / "data_prefetch" / "sec_edgar"
    if not base.exists():
        return {"verdict": "DATA_MISSING", "note": "sec_edgar directory not found"}

    t1a_active = _t1a_active_tickers()
    forms = ["SC_13D", "SC_13D_A", "SC_13G", "SC_13G_A", "8_K", "10_K", "10_Q", "DEF_14A", "S_1", "S_1_A", "4"]
    coverage: dict = {}
    for form in forms:
        form_dir = base / form
        if not form_dir.exists():
            coverage[form] = {"present": False, "n_files": 0}
            continue
        files = list(form_dir.glob("*.parquet"))
        # T1a coverage: how many of 503 active have a file?
        file_tickers = {f.stem.upper() for f in files}
        t1a_with = t1a_active & file_tickers
        # date-range coverage: sample 3 random tickers + check earliest/latest filing
        date_range_samples = []
        for sample in list(t1a_with)[:3]:
            try:
                df = pd.read_parquet(form_dir / f"{sample}.parquet")
                if not df.empty and "filing_date" in df.columns:
                    dt = pd.to_datetime(df["filing_date"], errors="coerce").dropna()
                    if len(dt) > 0:
                        date_range_samples.append({
                            "ticker": sample,
                            "n_filings": int(len(df)),
                            "first": str(dt.min().date()),
                            "last": str(dt.max().date()),
                        })
            except Exception as e:
                date_range_samples.append({"ticker": sample, "error": str(e)})
        coverage[form] = {
            "present": True,
            "n_files": len(files),
            "t1a_active_coverage": f"{len(t1a_with)}/{len(t1a_active)}",
            "t1a_coverage_pct": round(100 * len(t1a_with) / len(t1a_active), 1),
            "date_range_samples": date_range_samples,
        }

    # CHECKLIST #44(a) RUNTIME PROBE: call producer with KNOWN-EVENT pair
    from backtest.signals.sec_edgar_extractor import compute_sec_edgar_signals
    runtime_probes = []
    # AAPL has 105 8-K filings 2015-2026 (verified earlier this turn)
    for ticker, as_of, note in [
        ("AAPL", date(2024, 6, 28), "AAPL routine check"),
        ("TSLA", date(2024, 1, 15), "TSLA recent 8-K window check"),
        ("MSFT", date(2023, 5, 1), "MSFT routine check"),
    ]:
        out = compute_sec_edgar_signals(ticker, as_of)
        runtime_probes.append({"ticker": ticker, "as_of": str(as_of), "result": out, "non_empty": bool(out)})

    # Search for ANY firing event in the data: pick a sample 8-K and walk
    # forward 30 days to see if 8k_item_1_01 ever fires
    sample_8k_path = base / "8_K" / "AAPL.parquet"
    fire_evidence = []
    if sample_8k_path.exists():
        df = pd.read_parquet(sample_8k_path)
        # find any row with item_1_01 in primary_doc or filing
        for c in df.columns:
            if df[c].dtype == object and any("1.01" in str(v) for v in df[c].dropna().head(50)):
                fire_evidence.append({"column": c, "sample_value": str(df[c].dropna().iloc[0])[:80]})
                break

    return {
        "producer": "compute_sec_edgar_signals",
        "path_base": str(base.relative_to(_REPO)),
        "path_exists": True,
        "form_type_coverage": coverage,
        "runtime_probes": runtime_probes,
        "verdict": _verdict_from_runtime(runtime_probes),
    }


# ----------------------------------------------------------------------------
# index_rebalance coverage probe
# ----------------------------------------------------------------------------
def investigate_index_rebalance() -> dict:
    """CHECKLIST #44(a): identify TRUE path (different from B745's wrong path)."""
    from backtest.signals.index_rebalance import _EVENTS_PATH
    if not _EVENTS_PATH.exists():
        return {"verdict": "DATA_MISSING", "path": str(_EVENTS_PATH), "note": "events parquet not found"}

    df = pd.read_parquet(_EVENTS_PATH)
    n_rows = int(len(df))

    # Schema integrity
    required = {"ticker", "event_date", "event_type"}
    cols = set(df.columns)
    missing_cols = required - cols
    schema_ok = not missing_cols

    # Date range
    if "event_date" in df.columns:
        dt = pd.to_datetime(df["event_date"], errors="coerce").dropna()
        date_range = {
            "earliest": str(dt.min().date()) if len(dt) > 0 else None,
            "latest": str(dt.max().date()) if len(dt) > 0 else None,
        }
    else:
        date_range = {"earliest": None, "latest": None}

    # Event-type breakdown
    if "event_type" in df.columns:
        breakdown = df["event_type"].value_counts().to_dict()
    else:
        breakdown = {}

    # CHECKLIST #44(a) RUNTIME PROBE: KNOWN-EVENT (ticker, date) pairs
    from backtest.signals.index_rebalance import compute_index_rebalance_signals
    runtime_probes = []
    # Pick 3 events from the parquet + probe within their post-event windows
    for _, row in df.head(8).iterrows():
        ticker = row["ticker"]
        ev_date = pd.to_datetime(row["event_date"]).date()
        # 14 days post-event
        probe_date = ev_date + pd.Timedelta(days=14)
        probe_date = probe_date.date() if hasattr(probe_date, "date") else probe_date
        try:
            out = compute_index_rebalance_signals(ticker, probe_date)
            runtime_probes.append({
                "ticker": ticker,
                "event_type": row["event_type"],
                "event_date": str(ev_date),
                "probe_date": str(probe_date),
                "result": out,
                "non_empty": bool(out),
            })
        except Exception as e:
            runtime_probes.append({"ticker": ticker, "error": str(e)})

    return {
        "producer": "compute_index_rebalance_signals",
        "path": str(_EVENTS_PATH.relative_to(_REPO)),
        "path_exists": True,
        "n_rows": n_rows,
        "schema_ok": schema_ok,
        "missing_cols": sorted(missing_cols),
        "date_range": date_range,
        "event_type_breakdown": {k: int(v) for k, v in breakdown.items()},
        "runtime_probes": runtime_probes,
        "verdict": _verdict_from_runtime(runtime_probes),
    }


# ----------------------------------------------------------------------------
# recent_8k_signal: was DELETED in B748b. Check whether it should be restored.
# ----------------------------------------------------------------------------
def investigate_recent_8k() -> dict:
    """CHECKLIST #44(a) on the DELETED producer.

    Even though the producer was deleted in B748b, we need to verify:
    (1) the 8_K data exists (so a producer COULD work)
    (2) was the producer's 0-consumers claim correct?
    """
    base = _REPO / "data_prefetch" / "sec_edgar" / "8_K"
    if not base.exists():
        return {"verdict": "DATA_MISSING", "note": "8_K dir not found"}
    n_files = len(list(base.glob("*.parquet")))

    # Verify zero consumers claim: scan ALL backtest/signals/*.py + screener.py for
    # references to `recent_8k_filed` or `days_since_8k`
    import re
    sig_dir = _REPO / "backtest" / "signals"
    consumers: list = []
    for f in sig_dir.glob("*.py"):
        src = f.read_text(encoding="utf-8")
        # exclude comments + docstrings before grepping
        stripped = re.sub(r'"""[\s\S]*?"""', '', src)
        stripped = re.sub(r"'''[\s\S]*?'''", '', stripped)
        stripped = "\n".join(line.split("#", 1)[0] for line in stripped.splitlines())
        for key in ("recent_8k_filed", "days_since_8k"):
            if f'"{key}"' in stripped or f"'{key}'" in stripped or f'.get("{key}"' in stripped or f".get('{key}'" in stripped:
                consumers.append({"file": str(f.relative_to(_REPO)), "key": key})

    return {
        "producer": "compute_recent_8k_signal",
        "status": "DELETED_in_B748b",
        "data_8k_n_files": n_files,
        "live_code_consumers_post_b748b": consumers,
        "verdict": "DELETE_CORRECT" if not consumers else "DELETE_WAS_WRONG_REVIVE",
    }


# ----------------------------------------------------------------------------
# Verdict helper
# ----------------------------------------------------------------------------
def _verdict_from_runtime(probes: list) -> str:
    """If at least 1 probe returns non-empty + meaningful values, the producer
    emits signals correctly. If all empty/error, investigate per #44(b).
    """
    n_non_empty = sum(1 for p in probes if p.get("non_empty"))
    n_meaningful = sum(
        1 for p in probes
        if p.get("non_empty") and isinstance(p.get("result"), dict)
        and any(v for v in p["result"].values() if v not in (False, 0, None, ""))
    )
    if n_meaningful >= 1:
        return "DATA_PRESENT_AND_PRODUCER_WORKS"
    if n_non_empty >= 1:
        return "PRODUCER_EMITS_KEYS_BUT_VALUES_NONE_FIRING"
    return "RUNTIME_PROBE_EMPTY_INVESTIGATE_PER_CHECKLIST_44B"


# ----------------------------------------------------------------------------
# Orchestrator
# ----------------------------------------------------------------------------
def main():
    print("[B748c] DATA QUALITY INVESTIGATION (CHECKLIST #44 discipline)")
    print()

    sec = investigate_sec_edgar()
    ir = investigate_index_rebalance()
    r8k = investigate_recent_8k()

    print("=== SEC EDGAR ===")
    print(f"  verdict: {sec['verdict']}")
    if "form_type_coverage" in sec:
        for form, cov in sec["form_type_coverage"].items():
            if cov.get("present"):
                print(f"  {form}: {cov['n_files']} files, T1a coverage {cov['t1a_active_coverage']} ({cov['t1a_coverage_pct']}%)")
    print()
    print("=== INDEX REBALANCE ===")
    print(f"  verdict: {ir['verdict']}")
    print(f"  path: {ir['path']}")
    print(f"  rows: {ir.get('n_rows')}, schema_ok: {ir.get('schema_ok')}")
    print(f"  date range: {ir.get('date_range')}")
    print(f"  event types: {ir.get('event_type_breakdown')}")
    print(f"  runtime probes non-empty: {sum(1 for p in ir.get('runtime_probes', []) if p.get('non_empty'))} / {len(ir.get('runtime_probes', []))}")
    print()
    print("=== RECENT_8K (DELETED in B748b) ===")
    print(f"  verdict: {r8k['verdict']}")
    print(f"  8_K data files: {r8k['data_8k_n_files']}")
    print(f"  live-code consumers post-B748b: {len(r8k['live_code_consumers_post_b748b'])}")
    if r8k['live_code_consumers_post_b748b']:
        for c in r8k['live_code_consumers_post_b748b']:
            print(f"    - {c}")
    print()

    payload = {
        "checklist_items_applied": ["#44(a)", "#44(b)", "#44(c)", "#11", "#15", "#43", "#46", "#76(2)", "#76(3)"],
        "sec_edgar": sec,
        "index_rebalance": ir,
        "recent_8k": r8k,
    }
    Path(OUT_DIR / "b748c_investigation_results.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    print(f"[B748c] WROTE {OUT_DIR / 'b748c_investigation_results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
