"""B914 (2026-06-19): cohort architectural audit per Council 34 HYBRID.

# Source: owner directive 2026-06-19 'HYBRID' (Council 34 option iii) +
# B913 micropilot finding (all 19 fire 0/yr local) per CHECKLIST #77.

Standalone-signal forward-return test on 13F producer signals across T1a
2020-2026 at 5/10/21/63-day horizons. Tests whether the 13F STATE producer
has STANDALONE edge before composing with technical EVENT gates.

Per Council 34: if cohort viable -> walk 4-6 archetypes (redundancy
collapsed from 19); if not viable -> bulk-delete + log per B619/B620/
B682/B722 precedent.

Reconciliation: also report B619 fire-count estimator predicted vs B913
measured 0/yr.
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


HORIZONS = [5, 10, 21, 63]

# Representative T1a sample (mix of mega-cap / large-cap / mid-cap)
T1A_SAMPLE = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "V", "XOM",
    "JNJ", "WMT", "UNH", "MA", "PG", "HD", "CVX", "ABBV", "LLY", "AVGO",
    "KO", "MRK", "PEP", "COST", "ORCL", "CRM", "BAC", "NFLX", "AMD", "ADBE",
    "PFE", "TMO", "CSCO", "ACN", "ABT", "DHR", "MCD", "VZ", "NKE", "TXN",
    "INTC", "IBM", "PM", "QCOM", "HON", "UPS", "SCHW", "MS", "BLK", "GS",
]

# Sample monthly dates 2020-2026 (~80 dates per ticker; last day of each month)
def _gen_dates() -> list[date]:
    out = []
    first = date(2020, 2, 1)
    end = date(2026, 5, 1)
    while first <= end:
        # last day of current month
        next_month_first = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = next_month_first - timedelta(days=1)
        out.append(last_day)
        first = next_month_first
    return out


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


def main() -> int:
    dates = _gen_dates()
    print(f"B914 cohort audit: {len(T1A_SAMPLE)} tickers x {len(dates)} dates "
          f"= {len(T1A_SAMPLE) * len(dates)} ticker-date samples")
    print(f"Horizons: {HORIZONS} trading days")
    print()

    # Buckets keyed by signal state -> list of fwd returns per horizon
    buckets: dict[str, dict[int, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    close_cache: dict[str, pd.DataFrame] = {}
    skipped = 0
    total = 0

    for ticker in T1A_SAMPLE:
        if ticker not in close_cache:
            close_cache[ticker] = _load_close(ticker)
        df = close_cache[ticker]
        if df.empty:
            skipped += len(dates)
            continue

        for as_of in dates:
            total += 1
            sig = institutional_signal(ticker, as_of) or {}
            kind = sig.get("signal", "none")
            new_pos = int(sig.get("new_positions", 0) or 0)
            increased = int(sig.get("increased", 0) or 0)

            # Compute fwd returns
            rets = {h: _fwd_return(df, as_of, h) for h in HORIZONS}
            if all(v is None for v in rets.values()):
                skipped += 1
                continue

            # Bucket the sample into ALL applicable categories
            buckets["ALL"][0]  # ensure key exists
            for h, r in rets.items():
                if r is None:
                    continue
                buckets["ALL_BASE"][h].append(r)
                if kind == "strong_buy":
                    buckets["signal_strong_buy"][h].append(r)
                if kind in ("buy", "strong_buy"):
                    buckets["signal_buy"][h].append(r)
                if kind == "negative":
                    buckets["signal_negative"][h].append(r)
                if new_pos >= 3:
                    buckets["new_positions_ge_3"][h].append(r)
                if new_pos >= 1:
                    buckets["new_positions_ge_1"][h].append(r)
                if increased >= 5:
                    buckets["increased_ge_5"][h].append(r)
                if increased >= 2:
                    buckets["increased_ge_2"][h].append(r)
                if new_pos >= 3 and increased >= 5:
                    buckets["strong_conviction_AND"][h].append(r)

    print(f"Samples processed: {total} | skipped (no fwd data): {skipped}")
    print()

    # Compute mean fwd return per bucket per horizon
    out_rows = []
    for bucket_name in ["ALL_BASE", "signal_strong_buy", "signal_buy",
                        "signal_negative", "new_positions_ge_3", "new_positions_ge_1",
                        "increased_ge_5", "increased_ge_2", "strong_conviction_AND"]:
        for h in HORIZONS:
            vals = buckets[bucket_name].get(h, [])
            n = len(vals)
            if n == 0:
                mean_r = None
                hit_rate = None
            else:
                mean_r = sum(vals) / n
                hit_rate = sum(1 for v in vals if v > 0) / n
            out_rows.append({
                "bucket": bucket_name,
                "horizon_days": h,
                "n": n,
                "mean_fwd_return_pct": round(100 * mean_r, 3) if mean_r is not None else None,
                "hit_rate_pct": round(100 * hit_rate, 2) if hit_rate is not None else None,
            })

    df_out = pd.DataFrame(out_rows)

    # Print table
    print(f"=== Mean forward returns by signal state ===")
    print(df_out.to_string(index=False))
    print()

    # Compute edge over base rate
    base_means = {h: next((r["mean_fwd_return_pct"] for r in out_rows
                           if r["bucket"] == "ALL_BASE" and r["horizon_days"] == h), None)
                  for h in HORIZONS}
    base_hits = {h: next((r["hit_rate_pct"] for r in out_rows
                          if r["bucket"] == "ALL_BASE" and r["horizon_days"] == h), None)
                 for h in HORIZONS}

    print(f"=== EDGE OVER BASE RATE (mean_return - base, hit_rate - base) ===")
    for bucket_name in ["signal_strong_buy", "signal_buy", "signal_negative",
                        "new_positions_ge_3", "new_positions_ge_1",
                        "increased_ge_5", "increased_ge_2", "strong_conviction_AND"]:
        for h in HORIZONS:
            row = next((r for r in out_rows
                        if r["bucket"] == bucket_name and r["horizon_days"] == h), None)
            if row is None or row["mean_fwd_return_pct"] is None:
                continue
            edge_r = row["mean_fwd_return_pct"] - (base_means[h] or 0)
            edge_h = row["hit_rate_pct"] - (base_hits[h] or 0)
            verdict = "EDGE" if abs(edge_r) > 0.5 or abs(edge_h) > 2.0 else "no-edge"
            print(f"  {bucket_name:30s} h={h:>2}d n={row['n']:>5}  "
                  f"ret_edge={edge_r:+6.3f}pp  hit_edge={edge_h:+5.2f}pp  {verdict}")

    # Write JSON output
    out_path = REPO / "output_audit" / "b914_cohort_audit_13f_fwd_returns.json"
    out_data = {
        "summary": {
            "sample_tickers": len(T1A_SAMPLE),
            "sample_dates": len(dates),
            "total_samples_processed": total,
            "samples_skipped_no_fwd": skipped,
            "horizons_trading_days": HORIZONS,
            "method": "13F producer signal standalone fwd-return test",
        },
        "base_rate": {f"h{h}d": {"mean_fwd_return_pct": base_means[h],
                                   "hit_rate_pct": base_hits[h]} for h in HORIZONS},
        "buckets": out_rows,
    }
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
