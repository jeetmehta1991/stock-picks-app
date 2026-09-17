#!/usr/bin/env python
"""B2850 (S6-B2848c contract, owner word 'do SPECS + the 0.5 smoke' 2026-09-17):
the ladder's STEP 0.5 for the candle pair - count fires at PRODUCTION params
on live cached OHLCV for 6 megacaps. A zero here is a producer defect, not a
search (SS11.2 step 0.5).

Fidelity: the pattern legs are re-stated from technical.py:2104-2111 VERBATIM
(strict inequalities over the last 3 bars) and rsi_14 uses the same Wilder
form the producer emits; the borrow-trap leg of the short is DATA-DEPENDENT
(days_to_cover) and is NOT evaluated here - both counts are reported and the
gate count is therefore an UPPER BOUND for the short. Baseline holdout_n and
window per strategy come from the R5 cube itself.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MEGACAPS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META")
START, END = "2022-05-05", "2026-05-05"


def load(t):
    from backtest.data.cache import _cache_path
    p = _cache_path(t)
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["date"] = pd.to_datetime(d["date"])
    d = d.set_index("date").sort_index()
    return d.loc[START:END]


def rsi14(close: pd.Series) -> pd.Series:
    delta = close.diff()
    g = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    ls = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    return 100 - 100 / (1 + g / ls.replace(0, np.nan))


def main() -> int:
    counts = {"three_white_soldiers": {"pattern": 0, "pattern_and_rsi": 0},
              "three_black_crows_short": {"pattern": 0, "pattern_and_rsi": 0}}
    used = []
    for t in MEGACAPS:
        df = load(t)
        if df is None or len(df) < 40:
            continue
        used.append(t)
        c, o = df["close"].values, df["open"].values
        r = rsi14(df["close"]).values
        for i in range(4, len(df)):
            up = (all(c[i - k] > o[i - k] for k in range(0, 3))
                  and all(c[i - k] > c[i - k - 1] for k in range(0, 2))
                  and all(o[i - k] > o[i - k - 1] for k in range(0, 2)))
            dn = (all(c[i - k] < o[i - k] for k in range(0, 3))
                  and all(c[i - k] < c[i - k - 1] for k in range(0, 2))
                  and all(o[i - k] < o[i - k - 1] for k in range(0, 2)))
            if up:
                counts["three_white_soldiers"]["pattern"] += 1
                if not np.isnan(r[i]) and r[i] < 60:
                    counts["three_white_soldiers"]["pattern_and_rsi"] += 1
            if dn:
                counts["three_black_crows_short"]["pattern"] += 1
                if not np.isnan(r[i]) and r[i] > 40:
                    counts["three_black_crows_short"]["pattern_and_rsi"] += 1

    # baseline facts from the R5 cube, per strategy
    tl = pd.read_csv(ROOT / "output_r5_merged_1_7" / "trade_log.csv",
                     low_memory=False,
                     usecols=["strategy", "ticker", "entry_date"])
    base = {}
    for s in counts:
        sub = tl[tl["strategy"] == s].drop_duplicates(["ticker", "entry_date"])
        ed = pd.to_datetime(sub["entry_date"])
        base[s] = {"fires": int(len(sub)),
                   "holdout_n": int((ed >= "2025-05-05").sum()),
                   "window": f"{ed.min().date()}..{ed.max().date()}"}

    rec = {"_doc": ("SS11.2 step 0.5 smoke at PRODUCTION params, 6 megacaps, "
                    f"{START}..{END}; borrow leg NOT evaluated (data-dependent) "
                    "- the short's gate count is an UPPER BOUND"),
           "tickers_used": used, "counts": counts, "r5_baseline": base}
    out = ROOT / "output_audit" / "b2850_candle_step05_smoke.json"
    out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
