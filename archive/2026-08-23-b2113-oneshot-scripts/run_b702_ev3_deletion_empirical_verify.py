# Source: B702 (2026-06-11) adversarial review per CHECKLIST #77
"""
run_b702_ev3_deletion_empirical_verify.py
==========================================

B702 HIGHEST-PRIORITY ticket: empirical correlation measurement to decide
whether B682's deletion of strat_pead_long_high_yoy_growth_only (EV-3) +
strat_pead_short_negative_yoy_growth (EV-4) stands or reverts.

CONTEXT (from STAGE_4_EVENT_DRIVEN_CLUSTER_B702_ADVERSARIAL_REVIEW.md):
  EV-1 (strat_pead_long) fires when:
      within_pead_window AND pead_positive_surprise
      = within_pead_window AND (yoy_growth > 0 AND ann_return > 0.02)

  EV-3 (strat_pead_long_high_yoy_growth_only, DELETED B682) fires when:
      within_pead_window AND yoy_surprise_high
      = within_pead_window AND (yoy_growth >= 0.05)

B682 rationale claimed EV-3 is a "deterministic strict subset" of EV-1.
B702 source-grep at screener.py:3873-3876 showed the deletion comment
ITSELF acknowledges asymmetry: "EV-1's ann_ret > +2% gate adds a
narrowing axis EV-3 lacks". So EV-3 can fire where EV-1 doesn't:
high yoy_growth (>=5%) with weak announcement reaction (ann_ret <= 0.02).

DECISION RULE:
  Pearson correlation between (yoy_surprise_high) and (pead_positive_surprise)
  across all bars where within_pead_window=True on T1a sample 2020-2026.

  >= 0.85: B682 stands; amend deletion comment to "near-subset under
           empirical correlation"
  < 0.70:  REVERT B682; EV-3 captures a materially distinct population;
           re-register EV-3/EV-4
  0.70 - 0.85: owner decision; surface both populations' size

OUTPUT: output_audit/b702_ev3_deletion_empirical_verify_<DATE>.json
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from backtest.signals.pead import compute_pead_signals  # noqa: E402

YOY_SURPRISE_HIGH_THRESHOLD = 0.05  # +5% YoY = "high" yoy surprise


def _t1a_sample(n: int = 30) -> list:
    """Alphabetical sample of T1a current-snapshot tickers."""
    csv_path = REPO / "Backtesting universe" / "Current Snapshot_SP500 Tickers_May 2026.csv"
    if not csv_path.exists():
        raise SystemExit(f"[FATAL] T1a CSV not found at {csv_path}")
    df = pd.read_csv(csv_path)
    if "Symbol" in df.columns:
        symbols = sorted(df["Symbol"].dropna().astype(str).tolist())
    elif "Ticker" in df.columns:
        symbols = sorted(df["Ticker"].dropna().astype(str).tolist())
    else:
        # fallback to first column
        symbols = sorted(df.iloc[:, 0].dropna().astype(str).tolist())
    return symbols[:n]


def _load_ohlcv(ticker: str) -> pd.DataFrame | None:
    safe = ticker.replace(".", "-")
    p = REPO / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{safe}.parquet"
    if not p.exists():
        return None
    try:
        df = pd.read_parquet(p)
    except Exception:
        return None
    if df is None or df.empty:
        return None
    # Normalize index to DatetimeIndex
    if "date" in df.columns:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
    elif not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            return None
    return df


def measure(start_date: str = "2020-01-01", end_date: str = "2026-05-31",
            n_tickers: int = 30) -> dict:
    tickers = _t1a_sample(n_tickers)
    print(f"[INFO] Sampling {len(tickers)} T1a alphabetical: {tickers[0]} ... {tickers[-1]}")
    start = pd.Timestamp(start_date).date()
    end = pd.Timestamp(end_date).date()

    # Per-bar boolean records: (in_window, yoy_surprise_high, pead_positive_surprise)
    bars_in_window = 0
    bars_yoy_high = 0
    bars_pead_pos = 0
    bars_both = 0       # yoy_high AND pead_pos
    bars_only_yoy = 0   # yoy_high AND NOT pead_pos
    bars_only_pead = 0  # NOT yoy_high AND pead_pos
    n_tickers_ok = 0

    # Sample bars every 5 trading days to keep wall-clock manageable on 30x ~1500 bars
    # (full daily resolution = ~45k probes; 5-day = ~9k; sufficient for correlation)
    SAMPLE_STRIDE = 5

    for ticker in tickers:
        df = _load_ohlcv(ticker)
        if df is None or len(df) < 100:
            print(f"  [skip] {ticker}: no/short OHLCV cache")
            continue
        n_tickers_ok += 1
        # Probe dates: every Nth business day from start to end
        probe_dates = []
        for d in pd.bdate_range(start, end, freq="B"):
            if d.date() >= start and d.date() <= end:
                probe_dates.append(d.date())
        probe_dates = probe_dates[::SAMPLE_STRIDE]
        n_ticker_in_window = 0
        for as_of in probe_dates:
            sliced = df[df.index.date <= as_of]
            if len(sliced) < 30:
                continue
            try:
                sig = compute_pead_signals(ticker, sliced, as_of)
            except Exception:
                continue
            if not sig.get("within_pead_window", False):
                continue
            bars_in_window += 1
            n_ticker_in_window += 1
            yoy = sig.get("earnings_eps_yoy_growth")
            yoy_high = yoy is not None and yoy >= YOY_SURPRISE_HIGH_THRESHOLD
            pead_pos = bool(sig.get("pead_positive_surprise", False))
            if yoy_high:
                bars_yoy_high += 1
            if pead_pos:
                bars_pead_pos += 1
            if yoy_high and pead_pos:
                bars_both += 1
            elif yoy_high and not pead_pos:
                bars_only_yoy += 1
            elif not yoy_high and pead_pos:
                bars_only_pead += 1
        print(f"  [ok] {ticker}: {n_ticker_in_window} in-window probes")

    # Phi coefficient (Pearson correlation for 2 binary variables)
    # Phi = (n11*n00 - n10*n01) / sqrt((n11+n10)(n01+n00)(n11+n01)(n10+n00))
    n11 = bars_both
    n10 = bars_only_yoy            # yoy_high True, pead_pos False
    n01 = bars_only_pead           # yoy_high False, pead_pos True
    n00 = bars_in_window - n11 - n10 - n01
    denom_sq = (n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00)
    phi = ((n11 * n00 - n10 * n01) / (denom_sq ** 0.5)) if denom_sq > 0 else float("nan")

    # Subset overlap metrics
    pct_yoy_in_pead = (bars_both / bars_yoy_high) if bars_yoy_high > 0 else float("nan")
    pct_pead_in_yoy = (bars_both / bars_pead_pos) if bars_pead_pos > 0 else float("nan")

    # Verdict
    if phi >= 0.85:
        verdict = "STAND_B682_AMEND_COMMENT"
        verdict_msg = (
            "phi >= 0.85 -> EV-3 fires are near-subset of EV-1 fires empirically. "
            "B682 deletion stands. Amend screener.py:3856-3896 comment to remove "
            "'deterministic strict subset' framing; use 'near-subset under empirical "
            f"correlation phi={phi:.3f}'."
        )
    elif phi < 0.70:
        verdict = "REVERT_B682"
        verdict_msg = (
            f"phi < 0.70 (phi={phi:.3f}) -> EV-3 captures a materially distinct "
            "population from EV-1. Recommend revert: re-register "
            "strat_pead_long_high_yoy_growth_only + strat_pead_short_negative_"
            "yoy_growth in screener.py + ALL_STRATEGIES. Strategy roster count "
            "218 -> 220."
        )
    else:
        verdict = "OWNER_DECISION"
        verdict_msg = (
            f"phi in [0.70, 0.85) (phi={phi:.3f}) -> intermediate. Owner direction "
            f"needed. EV-3 fires={bars_yoy_high}; EV-1 fires={bars_pead_pos}; "
            f"distinct EV-3-only population={n10} bars."
        )

    result = {
        "batch": "B702-EV-3-DELETION-EMPIRICAL-VERIFY",
        "computed_at": datetime.utcnow().isoformat(),
        "params": {
            "yoy_surprise_high_threshold": YOY_SURPRISE_HIGH_THRESHOLD,
            "pead_positive_surprise_yoy_threshold": 0.0,
            "pead_positive_surprise_ann_return_threshold": 0.02,
            "sample_stride_bdays": SAMPLE_STRIDE,
            "date_range": {"start": start_date, "end": end_date},
            "n_tickers_target": n_tickers,
            "n_tickers_with_data": n_tickers_ok,
        },
        "tickers_used": tickers,
        "metrics": {
            "n_bars_within_pead_window": bars_in_window,
            "n_bars_yoy_surprise_high":   bars_yoy_high,
            "n_bars_pead_positive_surprise": bars_pead_pos,
            "n_bars_both_true":           n11,
            "n_bars_only_yoy_high":       n10,
            "n_bars_only_pead_positive":  n01,
            "n_bars_neither":             n00,
            "phi_correlation":            round(phi, 4) if not (phi != phi) else None,
            "pct_yoy_high_in_pead_pos":   round(pct_yoy_in_pead, 4) if not (pct_yoy_in_pead != pct_yoy_in_pead) else None,
            "pct_pead_pos_in_yoy_high":   round(pct_pead_in_yoy, 4) if not (pct_pead_in_yoy != pct_pead_in_yoy) else None,
        },
        "verdict": verdict,
        "verdict_message": verdict_msg,
    }
    return result


def main():
    print("=" * 80)
    print("B702 EV-3 DELETION EMPIRICAL VERIFY")
    print("=" * 80)
    result = measure()
    print()
    print("=" * 80)
    print("RESULT")
    print("=" * 80)
    print(json.dumps(result["metrics"], indent=2))
    print()
    print(f"VERDICT: {result['verdict']}")
    print(f"  {result['verdict_message']}")

    out_dir = REPO / "output_audit"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"b702_ev3_deletion_empirical_verify_{date.today().isoformat()}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n[INFO] Result written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
