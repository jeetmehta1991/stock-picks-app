"""Instrumented breaker-block pass - S6-B1500c.

Records, at every bar where smc_breaker_block_bullish would fire, the
diagnostics that SET the tightening level values (L356: levels must be derived
from measured distributions, never chosen):

  - age_bars     : bars between the qualifying OB event and the current bar.
                   This is the distribution that would set a recency level.
  - break_pct    : (close - top) / top, how far beyond the zone price broke.
                   This is the distribution that would set a break-margin level.
  - rank         : position of the qualifying event counting back from the most
                   recent OB event (0 = newest). Sets the tail(N) level.
  - n_ob_events  : total OB events available at that bar.

Replicates the production breaker logic EXACTLY as read from smc_ict.py:266-298
(bearish OB, mitigated, close above its top). PIT is preserved by recomputing
swings/ob per bar on ohlc.iloc[:i+1], the same slicing production uses.

Read-only. Mutates no production signal and writes only to output_audit/.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

# The vendored library prints a banner with a non-cp1252 codepoint at import,
# which raises UnicodeEncodeError on Windows consoles. smc_ict.py guards the
# same way; mirror it rather than inventing a different mechanism.
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc


def _load(ticker: str) -> pd.DataFrame:
    for rel in (f"backtest/data/cache/ohlcv/{ticker}.parquet",
                f"data/cache/ohlcv/{ticker}.parquet"):
        p = Path(rel)
        if p.exists():
            df = pd.read_parquet(p)
            if not isinstance(df.index, pd.DatetimeIndex) and "date" in df.columns:
                df = df.set_index("date")
            if not isinstance(df.index, pd.DatetimeIndex):
                # B2047 (S6-B2018b): META.parquet stores str dates; coerce as
                # the engine does (cache.py:335) or Timestamp lookups explode.
                _i = pd.to_datetime(df.index)
                df.index = _i.tz_localize(None) if _i.tz is not None else _i
            return df.sort_index()
    raise FileNotFoundError(f"no cached OHLCV for {ticker}")


def instrument(df: pd.DataFrame, start: str, end: str, swing_length: int = 20,
               tail_n: int = 20, min_history: int = 250) -> list[dict]:
    """Walk PIT and record every qualifying breaker event."""
    idx = df.index
    mask = (idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))
    rows: list[dict] = []
    for i in range(len(df)):
        if not mask[i] or i < min_history:
            continue
        sub = df.iloc[:i + 1]
        swings = _smc.swing_highs_lows(sub, swing_length=swing_length)
        ob_df = _smc.ob(sub, swings)
        if ob_df is None or "OB" not in ob_df.columns:
            continue
        nz = ob_df[ob_df["OB"].fillna(0) != 0]
        if nz.empty:
            continue
        tail = nz.tail(tail_n)
        close = float(sub["close"].iloc[-1]) if "close" in sub.columns \
            else float(sub["Close"].iloc[-1])
        n_events = len(nz)
        # positional index of each tail row within the sliced frame
        pos = {lbl: p for p, lbl in enumerate(ob_df.index)}
        qualifying = []
        for rank_from_new, (lbl, row) in enumerate(
                list(tail.iterrows())[::-1]):
            ob_val, top, bot = row.get("OB"), row.get("Top"), row.get("Bottom")
            mit = row.get("MitigatedIndex")
            if pd.isna(ob_val) or ob_val == 0 or pd.isna(top) or pd.isna(bot):
                continue
            is_mitigated = (not pd.isna(mit)) and mit > 0 and int(mit) < i
            # production bullish-breaker condition, smc_ict.py:283-284
            if is_mitigated and ob_val == -1 and close > float(top):
                qualifying.append({
                    "rank": rank_from_new,
                    "age_bars": i - pos.get(lbl, i),
                    "break_pct": (close - float(top)) / float(top),
                })
        if qualifying:
            rows.append({
                "bar": str(idx[i].date()),
                "n_ob_events": n_events,
                "n_qualifying": len(qualifying),
                "min_rank": min(q["rank"] for q in qualifying),
                "min_age_bars": min(q["age_bars"] for q in qualifying),
                "max_break_pct": max(q["break_pct"] for q in qualifying),
                "events": qualifying,
            })
    return rows


def summarise(rows: list[dict]) -> dict:
    if not rows:
        return {"firing_bars": 0}
    ages = pd.Series([r["min_age_bars"] for r in rows])
    ranks = pd.Series([r["min_rank"] for r in rows])
    brks = pd.Series([r["max_break_pct"] for r in rows])
    nq = pd.Series([r["n_qualifying"] for r in rows])
    q = [0.1, 0.25, 0.5, 0.75, 0.9]
    return {
        "firing_bars": len(rows),
        "age_bars_quantiles": {str(k): float(v) for k, v in ages.quantile(q).items()},
        "age_bars_min_max": [int(ages.min()), int(ages.max())],
        "rank_quantiles": {str(k): float(v) for k, v in ranks.quantile(q).items()},
        "break_pct_quantiles": {str(k): float(v) for k, v in brks.quantile(q).items()},
        "n_qualifying_mean": float(nq.mean()),
        "n_qualifying_max": int(nq.max()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--start", default="2022-05-05")
    ap.add_argument("--end", default="2025-05-05")
    ap.add_argument("--out", default="output_audit/b1501_breaker_instrumented.json")
    a = ap.parse_args()

    df = _load(a.ticker)
    rows = instrument(df, a.start, a.end)
    s = summarise(rows)
    print(f"{a.ticker} {a.start}..{a.end}")
    for k, v in s.items():
        print(f"  {k}: {v}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(
        {"ticker": a.ticker, "window": [a.start, a.end],
         "summary": s, "rows": rows}, indent=2))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
