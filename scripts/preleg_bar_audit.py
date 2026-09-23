"""S6-B2947 (owner-approved rec, ruling 2026-09-22): pre-leg OHLCV bar audit.

Source: owner ruling 2026-09-22 on S6-B2947 (per CHECKLIST #77); the bars
read are backtest/data/cache/ohlcv/ and the calendar is
backtest.engine.improvements, the engine's own.

NOTHING GATED BAR QUALITY BEFORE THE ENGINE LOOP - every existing check
(replay ATR-proxy lens, empty signals_at_entry share, resume integrity)
runs AFTER a cube lands, up to 4.5 h per config after launch. This script
audits the bars a config will ACTUALLY READ - the cached parquet under
backtest/data/cache/ohlcv/ for the resolved ticker list, sliced to the
resolved window - BEFORE the leg launches, and refuses above threshold.

Checks per ticker (the four the ticket names, measured over the window):
  missing_cache        - no cache parquet at all (HARD FAIL; this reader
                         never fetches, and the ENGINE's get_ohlcv WOULD
                         fetch from yfinance on the miss mid-run - the
                         Stage-2 HARD CUT violation this refusal prevents)
  nonpositive_price    - any open/high/low/close <= 0 (HARD FAIL)
  nan_share            - share of window rows with any NaN in OHLC
  gap_share            - NYSE trading days (the engine's own calendar:
                         backtest.engine.improvements) absent from the
                         ticker's bars, as a share of the INTERIOR span
                         [first bar, last bar] - a late listing or a
                         mid-window delisting (TWTR, ATVI, PXD, MRO in the
                         b2944 universe) is a sound, complete history, so
                         edge absence is reported, never failed
                         (cache.py:302's delisted-complete class; R5
                         graded this same universe without complaint)
  zero_volume_share    - share of window rows with volume == 0
  ABSENT (info)        - cache exists but zero rows in the window
                         (delisted before the window opens); reported

THRESHOLDS ARE PROVISIONAL DEFAULTS, disclosed in the artifact - the
ticket says "an owner-set threshold" and the owner has ruled the mechanism,
not the numbers. Override per run with --max-nan-share / --max-gap-share /
--max-zero-volume-share; the artifact records what it ran under.

Wiring: run_serial_chain.py invokes this per spec before LAUNCH and halts
the chain on exit 2 (inert for a chain already running - the launcher
loaded its code at chain start; live from the next chain, the
battery_path_hash precedent). Standalone:

    python scripts/preleg_bar_audit.py --spec output_audit/b2944_candle_tbc_c01_spec.json
    python scripts/preleg_bar_audit.py --tickers-file output_audit/_sweep_200.txt \
        --start 2022-05-05 --end 2026-05-05 --wave adhoc

Exit 0 = every ticker within threshold; exit 2 = refusal (artifact names
every failing ticker and why).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# provisional defaults - see docstring; every run's artifact records its own
DEFAULT_MAX_NAN_SHARE = 0.02
DEFAULT_MAX_GAP_SHARE = 0.02
DEFAULT_MAX_ZERO_VOLUME_SHARE = 0.10


def audit_frame(df, expected_days: list, *, max_nan_share: float,
                max_gap_share: float, max_zero_volume_share: float) -> dict:
    """Audit ONE ticker's window slice against the expected trading days.

    Pure over its inputs (a DataFrame with date/open/high/low/close/volume
    columns and a sorted list of datetime.date) so the pin test drives it
    with planted frames. Returns the per-ticker verdict row.
    """
    row: dict = {"rows": 0 if df is None else int(len(df)), "defects": []}
    if df is None or len(df) == 0:
        # A ticker with a cache file but no bars in the window is the
        # delisted-before-window class (cache.py:302's "delisted, complete"):
        # the engine trades nothing on it, exactly as R5 did over this same
        # universe. Reported, never failed - only a corrupt bar poisons a run.
        row["verdict"] = "ABSENT"
        return row

    import pandas as pd

    ohlc = df[["open", "high", "low", "close"]]
    nan_share = float(ohlc.isna().any(axis=1).mean())
    row["nan_share"] = round(nan_share, 4)
    # non-positive prices checked on rows that are not NaN (NaN already counted)
    nonpos = int((ohlc.fillna(1.0) <= 0).any(axis=1).sum())
    row["nonpositive_price_rows"] = nonpos

    vol = df["volume"] if "volume" in df.columns else pd.Series(dtype=float)
    zv_share = float((vol == 0).mean()) if len(vol) else 0.0
    row["zero_volume_share"] = round(zv_share, 4)

    have = {d.date() if hasattr(d, "date") else d
            for d in pd.to_datetime(df["date"]).tolist()}
    first, last = min(have), max(have)
    # INTERIOR gaps only: a late listing (bars start mid-window) and a
    # delisting (bars stop mid-window, e.g. MRO 2024-11) are sound,
    # complete histories - the engine simply has nothing to trade outside
    # [first, last]. Both edges are REPORTED so a human sees them.
    interior = [d for d in expected_days if first <= d <= last]
    missing = [d for d in interior if d not in have]
    gap_share = len(missing) / len(interior) if interior else 0.0
    row["expected_days"] = len(interior)
    row["gap_days"] = len(missing)
    row["gap_share"] = round(gap_share, 4)
    if missing:
        row["gap_sample"] = [str(d) for d in missing[:5]]
    lead = sum(1 for d in expected_days if d < first)
    trail = sum(1 for d in expected_days if d > last)
    if lead:
        row["leading_absent_days"] = lead
    if trail:
        row["trailing_absent_days"] = trail
        row["last_bar"] = str(last)

    if nonpos:
        row["defects"].append("nonpositive_price")
    if nan_share > max_nan_share:
        row["defects"].append("nan_share")
    if gap_share > max_gap_share:
        row["defects"].append("gap_share")
    if zv_share > max_zero_volume_share:
        row["defects"].append("zero_volume_share")
    row["verdict"] = "FAIL" if row["defects"] else "PASS"
    return row


def resolve_scope(spec: dict) -> dict:
    """A spec declaring `step` gets window + tickers_file from the phase
    table, exactly as run_wave.py resolves them (B2713); a legacy spec must
    carry both fields itself."""
    if "step" in spec and ("window" not in spec or "tickers_file" not in spec):
        sys.path.insert(0, str(ROOT / "scripts"))
        from phase_table import resolve as _resolve
        ruled = _resolve(int(spec["step"]))
        spec = dict(spec)
        spec["window"] = ruled["window"]
        spec["tickers_file"] = ruled["tickers_file"]
    if "window" not in spec or "tickers_file" not in spec:
        raise SystemExit("spec resolves neither window nor tickers_file")
    return spec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=None)
    ap.add_argument("--tickers-file", default=None)
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None)
    ap.add_argument("--wave", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-nan-share", type=float, default=DEFAULT_MAX_NAN_SHARE)
    ap.add_argument("--max-gap-share", type=float, default=DEFAULT_MAX_GAP_SHARE)
    ap.add_argument("--max-zero-volume-share", type=float,
                    default=DEFAULT_MAX_ZERO_VOLUME_SHARE)
    a = ap.parse_args()

    if a.spec:
        spec = resolve_scope(json.loads((ROOT / a.spec).read_text(encoding="utf-8")))
        wave = spec["wave"]
        tickers_file, window = spec["tickers_file"], spec["window"]
    else:
        if not (a.tickers_file and a.start and a.end):
            raise SystemExit("need --spec OR --tickers-file --start --end")
        wave = a.wave or "adhoc"
        tickers_file = a.tickers_file
        window = {"start": a.start, "end": a.end}

    sys.path.insert(0, str(ROOT))
    import pandas as pd
    from backtest.data.cache import _cache_path  # the engine's exact file
    from backtest.engine.improvements import (get_nyse_calendar_helper,
                                              is_nyse_trading_day)

    start = date.fromisoformat(window["start"])
    end = date.fromisoformat(window["end"])
    cal = get_nyse_calendar_helper()
    expected_days = [d.date() for d in pd.date_range(start, end, freq="D")
                     if is_nyse_trading_day(d.date(), calendar=cal)]

    tickers = (ROOT / tickers_file).read_text().split()
    per_ticker: dict = {}
    failing: list = []
    for t in tickers:
        f = _cache_path(t)
        if not f.exists():
            per_ticker[t] = {"rows": 0, "defects": ["missing_cache"],
                             "verdict": "FAIL"}
            failing.append(t)
            continue
        df = pd.read_parquet(f)
        if "date" not in df.columns:
            df = df.reset_index().rename(columns={"index": "date"})
        df["date"] = pd.to_datetime(df["date"])
        sl = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]
        row = audit_frame(sl, expected_days,
                          max_nan_share=a.max_nan_share,
                          max_gap_share=a.max_gap_share,
                          max_zero_volume_share=a.max_zero_volume_share)
        per_ticker[t] = row
        if row["verdict"] == "FAIL":
            failing.append(t)

    doc = {
        "ticket": "S6-B2947",
        "wave": wave,
        "tickers_file": tickers_file,
        "window": window,
        "n_tickers": len(tickers),
        "n_failing": len(failing),
        "failing": failing,
        "n_absent": sum(1 for r in per_ticker.values()
                        if r["verdict"] == "ABSENT"),
        "n_truncated": sum(1 for r in per_ticker.values()
                           if "trailing_absent_days" in r),
        "thresholds": {
            "max_nan_share": a.max_nan_share,
            "max_gap_share": a.max_gap_share,
            "max_zero_volume_share": a.max_zero_volume_share,
            "nonpositive_price": "any row fails",
            "note": ("PROVISIONAL DEFAULTS - the owner ruled the mechanism "
                     "(S6-B2947 rec approved 2026-09-22), not these numbers; "
                     "override per run via CLI flags"),
        },
        "expected_trading_days": len(expected_days),
        "calendar": "backtest.engine.improvements NYSE helper (the engine's own)",
        "per_ticker": per_ticker,
        "verdict": "FAIL" if failing else "PASS",
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = Path(a.out) if a.out else ROOT / "output_audit" / f"{wave}_preleg_bar_audit.json"
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"preleg bar audit {doc['verdict']}: {len(failing)} of "
          f"{len(tickers)} tickers defective -> {out.name}")
    if failing:
        for t in failing[:10]:
            print(f"  {t}: {','.join(per_ticker[t]['defects'])}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
