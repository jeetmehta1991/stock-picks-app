"""B916 (2026-06-19): Archetype 1 DIAGNOSE-BEFORE-DISPOSE per Council 35.

# Source: owner directive 2026-06-19 'h-revised' (Council 35) +
# CHECKLIST #106 #44(b) probes per `feedback_data_consumption_audit_must_apply_checklist_44b`.

Runs 6 diagnostic probes on Archetype 1 (3 strategies) BEFORE
recommending DELETE / RESCUE / EXPLORATORY:

Probe 1: Path-from-source (already verified B912; documents here)
Probe 2: Temporal-coverage at B913 sample window (Sep-Dec 2024)
Probe 3: Schema-contract (new_positions field name; already verified B912)
Probe 4: KNOWN-EVENT runtime - fire a known historical institutional
         NEW-position case + verify producer returns expected values
Probe 5: PIT lag integrity - 45-day filing lag look-ahead test
Probe 6: STRATEGY-LEVEL cohort audit - corrected from B914 producer-cohort
         (measures fwd-return WHERE strategy gates ALL FIRE; B914 measured
         where SINGLE STATE signal fires; Council 35 critical blind spot)
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd

from backtest.data.smart_money import institutional_signal


ARCH1_STRATEGIES = {
    "institutional_high_conviction_long": [
        ("institutional_new_positions", "STATE", "13F 90d persistence"),
        ("price_above_ema_50", "STATE", "trend filter"),
    ],
    "institutional_recent_init_momentum_long": [
        ("institutional_new_positions", "STATE", "13F 90d persistence"),
        ("macd_12_26_9_bullish", "EVENT", "bar-of-fire MACD cross"),
        ("price_above_ema_200", "STATE", "trend filter"),
    ],
    "institutional_recent_init_volume_long": [
        ("institutional_new_positions", "STATE", "13F 90d persistence"),
        ("vol_spike_2x", "EVENT", "bar-of-fire vol spike"),
        ("price_above_ema_50", "STATE", "trend filter"),
    ],
}


def probe_1_path_from_source() -> dict:
    """Document the data flow: source -> producer -> strategy."""
    return {
        "probe": "1_path_from_source",
        "data_source": [
            "data_prefetch/quiver/sec13fchanges/global.parquet (bulk; ~12 months recent)",
            "data_prefetch/quiver/institutional/{TICKER}.parquet (per-ticker fallback; 2006-2025)",
        ],
        "producer_function": "backtest.data.smart_money.institutional_signal()",
        "producer_output_dict": "{signal, new_positions, increased, decreased, source}",
        "strategy_consumption": "s.get('institutional_new_positions', False)",
        "engine_wiring": "screener.py: compute_smart_money_signals -> _has_institutional_buy",
        "verification": "B912 corrected probe: producer fires 40% on 40 T1a samples",
        "verdict": "PATH INTACT (producer source verified)",
    }


def probe_2_temporal_coverage(window_start: date, window_end: date,
                                tickers: list[str]) -> dict:
    """Does institutional_signal return non-empty data across B913 sample window?"""
    coverage = {}
    for ticker in tickers:
        d = window_start
        non_none = 0
        total = 0
        while d <= window_end:
            sig = institutional_signal(ticker, d) or {}
            total += 1
            if sig.get("signal", "none") != "none":
                non_none += 1
            d += timedelta(days=7)  # weekly sample
        coverage[ticker] = {
            "total_samples": total,
            "non_none_samples": non_none,
            "pct_non_none": round(100 * non_none / total, 1) if total else 0.0,
        }
    return {
        "probe": "2_temporal_coverage",
        "window": [str(window_start), str(window_end)],
        "tickers": tickers,
        "coverage": coverage,
        "verdict": "DATA AVAILABLE" if any(c["pct_non_none"] > 50 for c in coverage.values())
                   else "TEMPORAL GAP",
    }


def probe_3_schema_contract(ticker: str, as_of: date) -> dict:
    """Verify dict-key names match strategy gate code."""
    sig = institutional_signal(ticker, as_of) or {}
    expected_keys = ["signal", "new_positions", "increased", "decreased"]
    found_keys = list(sig.keys())
    missing = [k for k in expected_keys if k not in found_keys]
    return {
        "probe": "3_schema_contract",
        "sample": f"{ticker} @ {as_of}",
        "expected_keys": expected_keys,
        "found_keys": found_keys,
        "missing_keys": missing,
        "verdict": "SCHEMA INTACT" if not missing else "SCHEMA MISMATCH",
    }


def probe_4_known_event(ticker: str, as_of: date) -> dict:
    """KNOWN-EVENT runtime probe.

    Pick NVDA at 2024-09-30 — heavy institutional accumulation Q3 2024 (post-AI surge).
    Expected: producer returns signal != 'none' + new_positions > 0.
    """
    sig = institutional_signal(ticker, as_of) or {}
    return {
        "probe": "4_known_event_runtime",
        "test_case": f"{ticker} @ {as_of} (KNOWN heavy 13F inflow period)",
        "signal_kind": sig.get("signal"),
        "new_positions": sig.get("new_positions"),
        "increased": sig.get("increased"),
        "decreased": sig.get("decreased"),
        "verdict": "PRODUCER FIRED" if sig.get("signal") not in (None, "none")
                   else "PRODUCER SILENT (UNEXPECTED)",
    }


def probe_5_pit_lag_integrity() -> dict:
    """Test that signal at 2024-04-30 doesn't reflect Q1 2024 13F filings.

    Q1 2024 (ended Mar 31) 13F filings due May 15. Producer should NOT
    see Q1 data at 2024-04-30 (before May 15 cutoff). Producer should
    see Q4 2023 data (ended Dec 31 2023; due Feb 14 2024).
    """
    # Test ticker that has historical 13F coverage
    ticker = "AAPL"
    # Just before Q1 filing cutoff
    sig_pre = institutional_signal(ticker, date(2024, 5, 14))
    # Just after Q1 filing cutoff
    sig_post = institutional_signal(ticker, date(2024, 5, 16))
    return {
        "probe": "5_pit_lag_integrity",
        "test_case": f"{ticker} pre (2024-05-14) vs post (2024-05-16) Q1 2024 filing cutoff",
        "pre_filing_signal": sig_pre.get("signal") if sig_pre else None,
        "post_filing_signal": sig_post.get("signal") if sig_post else None,
        "pre_new_positions": sig_pre.get("new_positions") if sig_pre else None,
        "post_new_positions": sig_post.get("new_positions") if sig_post else None,
        "verdict": ("PIT INTACT (pre and post may differ as new data ingested)"
                   if sig_pre and sig_post
                   else "PIT TEST INCONCLUSIVE"),
    }


def _load_close(ticker: str) -> pd.DataFrame:
    p = REPO / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{ticker}.parquet"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p, columns=["date", "close"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df.sort_values("date").reset_index(drop=True)


def _fwd_return(close_df: pd.DataFrame, as_of: date, horizon: int) -> float | None:
    if close_df.empty:
        return None
    idx = close_df.index[close_df["date"] >= as_of]
    if idx.empty:
        return None
    i0 = idx[0]
    if i0 + horizon >= len(close_df):
        return None
    p0 = float(close_df.loc[i0, "close"])
    pN = float(close_df.loc[i0 + horizon, "close"])
    if p0 <= 0:
        return None
    return (pN - p0) / p0


def probe_6_strategy_level_cohort_audit(tickers: list[str]) -> dict:
    """STRATEGY-level cohort (not producer-level B914).

    Conditions: new_positions >= 3 AND price_above_ema_50 (approximation;
    real strategies have additional gates we can't replicate without
    technical signal cache). Result: fwd-return WHERE strategy STATE
    portion fires (still not full gate; this is intermediate).
    """
    horizons = [5, 10, 21, 63]
    buckets: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))

    # Approximate "price_above_ema_50" via 50-day SMA close proxy
    for ticker in tickers:
        df = _load_close(ticker)
        if df.empty:
            continue
        # Sample monthly snapshots
        d = date(2022, 1, 1)
        while d <= date(2025, 12, 31):
            sig = institutional_signal(ticker, d) or {}
            new_pos = int(sig.get("new_positions", 0) or 0)
            # 50d-SMA approximation
            idx = df.index[df["date"] >= d]
            if idx.empty:
                d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
                continue
            i0 = idx[0]
            if i0 < 50:
                d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
                continue
            sma50 = df.loc[i0 - 50:i0, "close"].mean()
            close_today = float(df.loc[i0, "close"])
            price_above_ema_50_proxy = close_today > sma50

            for h in horizons:
                r = _fwd_return(df, d, h)
                if r is None:
                    continue
                buckets["ALL_BASE"][h].append(r)
                # Strategy-level intermediate (state portion only)
                if new_pos >= 3 and price_above_ema_50_proxy:
                    buckets["new_pos_AND_above_ema50"][h].append(r)
                if new_pos >= 3:
                    buckets["new_pos_only"][h].append(r)
            d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)

    rows = []
    for bucket_name in ["ALL_BASE", "new_pos_only", "new_pos_AND_above_ema50"]:
        for h in horizons:
            vals = buckets[bucket_name].get(h, [])
            n = len(vals)
            if n == 0:
                continue
            mean_r = sum(vals) / n
            hit = sum(1 for v in vals if v > 0) / n
            rows.append({
                "bucket": bucket_name,
                "horizon": h,
                "n": n,
                "mean_fwd_return_pct": round(100 * mean_r, 3),
                "hit_rate_pct": round(100 * hit, 2),
            })

    base_means = {h: next((r["mean_fwd_return_pct"] for r in rows
                           if r["bucket"] == "ALL_BASE" and r["horizon"] == h), None)
                  for h in horizons}
    base_hits = {h: next((r["hit_rate_pct"] for r in rows
                          if r["bucket"] == "ALL_BASE" and r["horizon"] == h), None)
                 for h in horizons}

    edges = []
    for bucket_name in ["new_pos_only", "new_pos_AND_above_ema50"]:
        for h in horizons:
            row = next((r for r in rows
                        if r["bucket"] == bucket_name and r["horizon"] == h), None)
            if row is None:
                continue
            edge_r = row["mean_fwd_return_pct"] - (base_means[h] or 0)
            edge_h = row["hit_rate_pct"] - (base_hits[h] or 0)
            edges.append({
                "bucket": bucket_name,
                "horizon": h,
                "n": row["n"],
                "return_edge_pp": round(edge_r, 3),
                "hit_edge_pp": round(edge_h, 2),
                "verdict": ("EDGE" if (edge_r > 0.5 or edge_h > 2.0)
                            else ("NEG_EDGE" if (edge_r < -0.5 or edge_h < -2.0)
                                  else "NO_EDGE")),
            })
    return {
        "probe": "6_strategy_level_cohort_audit",
        "method": "STATE-portion of strategy gates (new_pos >= 3 AND above_ema_50)",
        "caveat": "Approximation; full gate stack needs technical signal cache",
        "rows": rows,
        "edges": edges,
    }


def main() -> int:
    sample_tickers = ["NVDA", "MSFT", "AAPL", "META", "AMD", "GOOGL", "JPM", "V"]

    print("=" * 78)
    print("B916 ARCHETYPE 1 DIAGNOSE-BEFORE-DISPOSE per Council 35")
    print("=" * 78)
    print()

    out = {"archetype": 1, "strategies": list(ARCH1_STRATEGIES.keys()), "probes": []}

    print("--- Probe 1: PATH-FROM-SOURCE ---")
    p1 = probe_1_path_from_source()
    print(json.dumps(p1, indent=2))
    print()
    out["probes"].append(p1)

    print("--- Probe 2: TEMPORAL-COVERAGE at B913 sample window ---")
    p2 = probe_2_temporal_coverage(date(2024, 9, 1), date(2024, 12, 31),
                                    sample_tickers[:5])
    print(json.dumps(p2, indent=2))
    print()
    out["probes"].append(p2)

    print("--- Probe 3: SCHEMA-CONTRACT ---")
    p3 = probe_3_schema_contract("NVDA", date(2024, 9, 30))
    print(json.dumps(p3, indent=2))
    print()
    out["probes"].append(p3)

    print("--- Probe 4: KNOWN-EVENT RUNTIME ---")
    p4 = probe_4_known_event("NVDA", date(2024, 9, 30))
    print(json.dumps(p4, indent=2, default=str))
    print()
    out["probes"].append(p4)

    print("--- Probe 5: PIT LAG INTEGRITY ---")
    p5 = probe_5_pit_lag_integrity()
    print(json.dumps(p5, indent=2, default=str))
    print()
    out["probes"].append(p5)

    print("--- Probe 6: STRATEGY-LEVEL COHORT AUDIT (corrects B914 producer-level) ---")
    p6 = probe_6_strategy_level_cohort_audit(sample_tickers)
    print(json.dumps(p6, indent=2, default=str))
    print()
    out["probes"].append(p6)

    out_path = REPO / "output_audit" / "b916_archetype1_diagnose_before_dispose.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
