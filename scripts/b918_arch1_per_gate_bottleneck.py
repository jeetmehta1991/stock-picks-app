"""B918 (2026-06-19): per-gate bottleneck probe for Archetype 1.

# Source: B917 micropilot found gate-stacking confirmed even on broad sample.
# Per Council 35 + Council 34 walk template Step 7: identify WHICH gate kills.

For 10 broad-stratified tickers x B913 window (Sep-Dec 2024):
- Per-gate fire rates on each strategy's gate stack
- Identifies bottleneck gate (lowest fire rate)
- Tests loosened-threshold variants

Output informs disposition: (a) GATE-LOOSEN (if 1 gate is bottleneck) /
(f) DELETE (if all gates jointly impossible) / (g) DROP_STATE_KEEP_TECH
(if STATE gate is bottleneck).
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd

from backtest.data.smart_money import institutional_signal


BROAD_SAMPLE = ["A", "ABNB", "ACGL", "ADM", "ADP", "ALL", "AMTM", "GEN", "AAPL", "ABBV"]
WINDOW_START = date(2024, 9, 1)
WINDOW_END = date(2024, 12, 31)


def _load_close(ticker: str) -> pd.DataFrame:
    p = REPO / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{ticker}.parquet"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df.sort_values("date").reset_index(drop=True)


def _compute_technical_gates(df: pd.DataFrame, as_of: date) -> dict:
    """Compute key technical gate signals at as_of bar."""
    idx = df.index[df["date"] >= as_of]
    if idx.empty or idx[0] < 200:
        return {}
    i = idx[0]
    close = float(df.loc[i, "close"])
    # EMA approximation via SMA (consistent with B916 Probe 6)
    sma_50 = float(df.loc[i - 50:i, "close"].mean())
    sma_200 = float(df.loc[i - 200:i, "close"].mean())
    # Volume spike
    vol_today = float(df.loc[i, "volume"])
    vol_avg_20 = float(df.loc[i - 20:i, "volume"].mean())
    vol_spike_2x = vol_today >= 2.0 * vol_avg_20
    # MACD: 12/26 EMA difference - simplified
    if i >= 26:
        # very rough macd_bullish_cross approximation: 12d-EMA-proxy > 26d-EMA-proxy
        # AND 12d-EMA-proxy yesterday <= 26d-EMA-proxy yesterday
        sma_12_today = float(df.loc[i - 12:i, "close"].mean())
        sma_26_today = float(df.loc[i - 26:i, "close"].mean())
        sma_12_yest = float(df.loc[i - 13:i - 1, "close"].mean())
        sma_26_yest = float(df.loc[i - 27:i - 1, "close"].mean())
        macd_bullish_cross = (sma_12_today > sma_26_today) and (sma_12_yest <= sma_26_yest)
    else:
        macd_bullish_cross = False
    return {
        "price_above_ema_50": close > sma_50,
        "price_above_ema_200": close > sma_200,
        "vol_spike_2x": vol_spike_2x,
        "macd_12_26_9_bullish": macd_bullish_cross,
    }


def per_gate_probe() -> dict:
    """Count per-gate True rate across 10 tickers x window."""
    counts = {
        "institutional_new_positions_ge_3": 0,
        "institutional_new_positions_ge_1": 0,
        "institutional_buy_or_strong_buy": 0,
        "price_above_ema_50": 0,
        "price_above_ema_200": 0,
        "vol_spike_2x": 0,
        "macd_12_26_9_bullish": 0,
        "TOTAL_SAMPLES": 0,
    }
    # Strategy-level conjunction counts
    strat_counts = {
        "high_conviction_long_(new_pos>=3 AND above_ema_50)": 0,
        "recent_init_momentum_long_(new_pos>=3 AND macd AND above_ema_200)": 0,
        "recent_init_volume_long_(new_pos>=3 AND vol_spike AND above_ema_50)": 0,
        # Loosened variants
        "LOOSE_high_conviction_(new_pos>=1 AND above_ema_50)": 0,
        "LOOSE_recent_init_volume_(new_pos>=1 AND vol_spike AND above_ema_50)": 0,
        "DROP_STATE_recent_init_volume_(vol_spike AND above_ema_50)": 0,
        "DROP_TREND_high_conviction_(new_pos>=3 only)": 0,
    }

    for ticker in BROAD_SAMPLE:
        df = _load_close(ticker)
        if df.empty:
            continue
        d = WINDOW_START
        while d <= WINDOW_END:
            counts["TOTAL_SAMPLES"] += 1
            sig = institutional_signal(ticker, d) or {}
            new_pos = int(sig.get("new_positions", 0) or 0)
            sig_kind = sig.get("signal", "none")

            tech = _compute_technical_gates(df, d)
            if not tech:
                d += timedelta(days=1)
                continue

            # Individual gate counts
            if new_pos >= 3: counts["institutional_new_positions_ge_3"] += 1
            if new_pos >= 1: counts["institutional_new_positions_ge_1"] += 1
            if sig_kind in ("buy", "strong_buy"):
                counts["institutional_buy_or_strong_buy"] += 1
            if tech.get("price_above_ema_50"): counts["price_above_ema_50"] += 1
            if tech.get("price_above_ema_200"): counts["price_above_ema_200"] += 1
            if tech.get("vol_spike_2x"): counts["vol_spike_2x"] += 1
            if tech.get("macd_12_26_9_bullish"): counts["macd_12_26_9_bullish"] += 1

            # Strategy-level conjunctions
            if new_pos >= 3 and tech.get("price_above_ema_50"):
                strat_counts["high_conviction_long_(new_pos>=3 AND above_ema_50)"] += 1
            if new_pos >= 3 and tech.get("macd_12_26_9_bullish") and tech.get("price_above_ema_200"):
                strat_counts["recent_init_momentum_long_(new_pos>=3 AND macd AND above_ema_200)"] += 1
            if new_pos >= 3 and tech.get("vol_spike_2x") and tech.get("price_above_ema_50"):
                strat_counts["recent_init_volume_long_(new_pos>=3 AND vol_spike AND above_ema_50)"] += 1

            # Loosened variants
            if new_pos >= 1 and tech.get("price_above_ema_50"):
                strat_counts["LOOSE_high_conviction_(new_pos>=1 AND above_ema_50)"] += 1
            if new_pos >= 1 and tech.get("vol_spike_2x") and tech.get("price_above_ema_50"):
                strat_counts["LOOSE_recent_init_volume_(new_pos>=1 AND vol_spike AND above_ema_50)"] += 1
            if tech.get("vol_spike_2x") and tech.get("price_above_ema_50"):
                strat_counts["DROP_STATE_recent_init_volume_(vol_spike AND above_ema_50)"] += 1
            if new_pos >= 3:
                strat_counts["DROP_TREND_high_conviction_(new_pos>=3 only)"] += 1

            d += timedelta(days=1)
    return {"individual_gate_counts": counts, "strategy_level_counts": strat_counts}


def main() -> int:
    print("=" * 78)
    print("B918 ARCHETYPE 1 PER-GATE BOTTLENECK PROBE")
    print("=" * 78)
    print(f"Sample: {len(BROAD_SAMPLE)} broad-stratified tickers")
    print(f"Window: {WINDOW_START} -> {WINDOW_END}")
    print()

    result = per_gate_probe()
    total = result["individual_gate_counts"]["TOTAL_SAMPLES"]

    print(f"Total ticker-bar samples: {total}")
    print()
    print("=== Individual gate fire rates ===")
    for gate, n in result["individual_gate_counts"].items():
        if gate == "TOTAL_SAMPLES":
            continue
        pct = 100 * n / total if total else 0
        print(f"  {gate:50s} {n:>5} ({pct:5.1f}%)")
    print()
    print("=== Strategy-level conjunction counts ===")
    for strat, n in result["strategy_level_counts"].items():
        pct = 100 * n / total if total else 0
        flag = " <-- FIRES!" if n > 0 else ""
        print(f"  {strat:65s} {n:>5} ({pct:5.2f}%){flag}")
    print()

    out_path = REPO / "output_audit" / "b918_arch1_per_gate_bottleneck.json"
    with open(out_path, "w") as f:
        json.dump({
            "window": [str(WINDOW_START), str(WINDOW_END)],
            "sample": BROAD_SAMPLE,
            "results": result,
        }, f, indent=2, default=str)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
