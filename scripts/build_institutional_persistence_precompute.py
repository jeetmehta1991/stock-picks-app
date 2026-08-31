"""Item 5 (2026-05-25 owner directive): build multi-quarter institutional
persistence precompute parquet.

Output: data_prefetch/derived/institutional_persistence_t1a/{snapshot_date}.parquet

Schema (per ticker):
  ticker                              str
  persistent_holders_4q               int   (funds held >=4 consecutive quarters)
  persistent_holders_8q               int   (funds held >=8 consecutive quarters)
  avg_position_age_quarters           float (mean quarters held across all current holders)
  committed_growth_holders            int   (funds grew position over 4+ quarters)
  total_active_holders                int   (funds with non-zero position this quarter)
  formation_end                       date

PIT correctness: only uses ReportPeriod <= snapshot_date - 45 days
(DEC-325 13F reporting lag).

Source: data_prefetch/quiver/institutional/{TICKER}.parquet
  Schema: Date, ReportPeriod, Name, Ticker, Fund, Class, Value, Shares,
          SH/PRN, Put/Call, Direction.

Literature: Yan-Zhang 2009 RFS (short-horizon institutional persistence
forecasts alpha); Frazzini-Lamont 2008 (institutional investor sentiment).

Compute: ~5-10s per ticker x T1a 614 = ~1-2h per snapshot. Use --tickers
to subset for smoke runs.

Run:
  Smoke: python scripts/build_institutional_persistence_precompute.py --smoke
  Full T1a one snapshot: python scripts/build_institutional_persistence_precompute.py --as-of 2024-01-01
"""
from __future__ import annotations

import argparse
import sys
from datetime import date as _date, timedelta
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
INSTITUTIONAL_DIR = REPO / "data_prefetch" / "quiver" / "institutional"
T1A_CSV = REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
def persistence_cache_dir(repo_root):
    """S6-B2484: resolve the persistence-precompute directory, tag-aware.

    ONE definition, imported by the producer AND the consumer. The council's
    Executor named the failure this prevents: if each side re-derives the tag
    string independently they drift, and a sweep then reads the production
    artifact while believing it read its variant.

    INST_PERSIST_CACHE_TAG unset or empty -> the production path, unchanged.
    Set -> a sibling directory suffixed with the tag, so a parameter sweep can
    never overwrite the artifact SEVEN 13F strategies read.
    """
    import os
    from pathlib import Path
    tag = (os.environ.get("INST_PERSIST_CACHE_TAG") or "").strip()
    base = Path(repo_root) / "data_prefetch" / "derived"
    return base / ("institutional_persistence_t1a" + (("_" + tag) if tag else ""))


OUT_DIR = persistence_cache_dir(REPO)

# S6-B2484: swept producer parameters. Defaults ARE production, so an
# untagged run reproduces today's artifact exactly.
import os as _os
MIN_CONSECUTIVE_QUARTERS = int(_os.environ.get("INST_MIN_CONSECUTIVE_QUARTERS", "4"))
GROWTH_LOOKBACK_QUARTERS = int(_os.environ.get("INST_GROWTH_LOOKBACK_QUARTERS", "4"))
GROWTH_MULTIPLE = float(_os.environ.get("INST_GROWTH_MULTIPLE", "1.10"))
if MIN_CONSECUTIVE_QUARTERS < 1 or GROWTH_LOOKBACK_QUARTERS < 1:
    raise ValueError("consecutive/lookback quarters must be >= 1")
if GROWTH_MULTIPLE <= 0:
    raise ValueError("growth multiple must be > 0")

REPORTING_LAG_DAYS = 45


def _per_ticker_persistence(ticker: str, as_of: _date) -> dict | None:
    """Compute persistence metrics for one ticker as of snapshot date.

    Returns dict (or None when no usable data) with the keys defined in
    the module docstring. PIT-respects 45-day reporting lag.
    """
    safe = ticker.replace(".", "-")
    p = INSTITUTIONAL_DIR / f"{safe}.parquet"
    if not p.exists():
        return None
    try:
        df = pd.read_parquet(p)
    except Exception:
        return None
    if df.empty:
        return None
    # PIT filter: ReportPeriod + 45 days <= as_of
    df["report_dt"] = pd.to_datetime(df["ReportPeriod"], errors="coerce").dt.date
    df = df.dropna(subset=["report_dt"])
    cutoff = as_of - timedelta(days=REPORTING_LAG_DAYS)
    df = df[df["report_dt"] <= cutoff]
    if df.empty:
        return None
    # Per-fund per-quarter shares (sum across multiple class entries)
    grp = df.groupby(["Fund", "report_dt"], dropna=False)["Shares"].sum().reset_index()
    grp = grp[grp["Shares"] > 0]
    if grp.empty:
        return None

    # Latest quarter cutoff = most recent report_dt <= cutoff
    latest_q = grp["report_dt"].max()
    # Per-fund consecutive-quarter holding counts ending at latest_q
    per_fund_counts = {}
    for fund, sub in grp.groupby("Fund"):
        quarters = sorted(sub["report_dt"].unique(), reverse=True)
        if quarters[0] != latest_q:
            continue  # fund not in current quarter
        # Count consecutive quarterly holdings ending at latest_q
        n = 1
        for i in range(1, len(quarters)):
            # Quarterly gap = 90 +/- 10 days
            gap = (quarters[i - 1] - quarters[i]).days
            if 70 <= gap <= 100:
                n += 1
            else:
                break
        per_fund_counts[fund] = n

    if not per_fund_counts:
        return None

    persistent_4q = sum(1 for n in per_fund_counts.values() if n >= 4)
    persistent_8q = sum(1 for n in per_fund_counts.values() if n >= 8)
    avg_age = float(sum(per_fund_counts.values())) / len(per_fund_counts)
    total_active = len(per_fund_counts)

    # Committed growth holders: funds that GREW position over 4+ quarters
    committed_growth = 0
    for fund, sub in grp.groupby("Fund"):
        # S6-B2484: was the literal 4. Lines above (persistent_4q >= 4,
        # _8q >= 8) are DIFFERENT parameters for OTHER strategies - not
        # touched.
        if per_fund_counts.get(fund, 0) < MIN_CONSECUTIVE_QUARTERS:
            continue
        sub_sorted = sub.sort_values("report_dt", ascending=False)
        recent_shares = sub_sorted.iloc[0]["Shares"]
        # S6-B2484 OFF-BY-ONE, flagged by the council: production lookback
        # 4 means iloc[3], so the index is (lookback - 1), never lookback.
        _lb = GROWTH_LOOKBACK_QUARTERS
        four_q_back = (sub_sorted.iloc[_lb - 1]["Shares"]
                       if len(sub_sorted) >= _lb else None)
        if (four_q_back is not None
                and recent_shares > four_q_back * GROWTH_MULTIPLE):
            committed_growth += 1

    return {
        "ticker":                    ticker,
        "persistent_holders_4q":     int(persistent_4q),
        "persistent_holders_8q":     int(persistent_8q),
        "avg_position_age_quarters": round(avg_age, 2),
        "committed_growth_holders":  int(committed_growth),
        "total_active_holders":      int(total_active),
        "formation_end":             latest_q,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default="2024-01-01")
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke: 5 mega-caps only")
    args = ap.parse_args()

    as_of = _date.fromisoformat(args.as_of)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{as_of.isoformat()}.parquet"

    if args.smoke:
        tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
    else:
        if not T1A_CSV.exists():
            print(f"ERROR: {T1A_CSV} missing")
            sys.exit(1)
        df_t1a = pd.read_csv(T1A_CSV, comment="#")
        df_t1a["added_dt"] = pd.to_datetime(df_t1a.get("added_date"), errors="coerce").dt.date
        df_t1a["removed_dt"] = pd.to_datetime(df_t1a.get("removed_date"), errors="coerce").dt.date
        active = df_t1a[
            (df_t1a["added_dt"].isna() | (df_t1a["added_dt"] <= as_of))
            & (df_t1a["removed_dt"].isna() | (df_t1a["removed_dt"] > as_of))
        ]
        tickers = list(active["Symbol"].unique())

    print(f"Computing persistence at {as_of} for {len(tickers)} tickers...")
    rows = []
    n_data = 0
    for i, t in enumerate(tickers):
        if i % 100 == 0 and i > 0:
            print(f"  ... {i}/{len(tickers)} tickers processed ({n_data} with persistence data)")
        out = _per_ticker_persistence(t, as_of)
        if out is not None:
            rows.append(out)
            n_data += 1
    if not rows:
        print(f"WARN: No persistence data extracted at {as_of}")
        empty = pd.DataFrame(columns=[
            "ticker", "persistent_holders_4q", "persistent_holders_8q",
            "avg_position_age_quarters", "committed_growth_holders",
            "total_active_holders", "formation_end",
        ])
        empty.to_parquet(out_path, index=False)
        return
    out_df = pd.DataFrame(rows)
    out_df.to_parquet(out_path, index=False)
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(out_df)} tickers with persistence data)")
    print(f"  persistent_holders_4q: min={out_df['persistent_holders_4q'].min()} "
          f"median={int(out_df['persistent_holders_4q'].median())} "
          f"max={out_df['persistent_holders_4q'].max()}")
    print(f"  total_active_holders:  min={out_df['total_active_holders'].min()} "
          f"median={int(out_df['total_active_holders'].median())} "
          f"max={out_df['total_active_holders'].max()}")


if __name__ == "__main__":
    main()
