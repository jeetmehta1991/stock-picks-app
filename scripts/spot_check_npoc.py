#!/usr/bin/env python
"""S6-B3171a: three-leg spot check for the naked-POC (volume_profile) cubes.

WHY IT EXISTS. run_postconfig requires a `spot_check` leg for any battery
family (_TOOLS_REQUIRED). The owner's "Engine" word (2026-10-15) sequenced
the first engine leg for naked_poc_retest_long; this is adapter piece 2,
after the grade leg (grade_npoc_config.py, B3139q-r69y).

SAME ARTIFACT CONTRACT as spot_check_candle.py / spot_check_institutional.py
(agree / disagree / skipped / execution_failures / seed) so postconfig_doc
renders it unchanged.

PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA. The seeded RNG picks WHICH landed
trades to re-derive; it never generates a number (the B1719b declaration -
deliberately NOT "SYNTHETIC").

THREE LEGS per sampled (ticker, entry_date):
  leg A  RAW ARITHMETIC - the naked-POC condition re-derived here from cached
         OHLCV with explicit bin arithmetic and NO import of the producer:
         the trailing `lookback` bars are cut into `n_periods` chunks
         (floor-divided chunk size, a chunk under 5 bars skipped), each
         chunk's POC is the midpoint of its highest-volume price bin with
         each bar's volume spread uniformly across the bins its low..high
         overlaps, and the condition is POC count > 0 AND the nearest POC
         within `max_distance_pct` of the entry close, AND (S6-B3175, P1 swept)
         when a span is given - the CLI requires --ema-span - the entry close
         above that EMA computed from the raw closes as compute_ema_sma does
         (close.ewm(span, adjust=False)); measured before shipping on config
         6's cube: 527 of 527 recorded flags reproduced at each of spans
         9/20/50/100/150/200.
  leg B  PRODUCTION     - volume_profile.compute_period_pocs on the same PIT
         slice, with the knobs exported to the environment and
         backtest.config reloaded, then passed exactly as the screener
         passes them (screener.py's naked-POC block) - i.e. the engine's own
         env -> config -> producer chain; the span's flag comes from
         technical.compute_ema_sma on the same slice (S6-B3175).
  leg C  RECORD         - the cube's own signals_at_entry naked_poc_count /
         naked_poc_nearest_distance_pct and price_above_ema_<span>, under the
         same condition (a span the record never stored is SKIPPED).

PIT: the slice ends AT the entry bar (df.iloc[:i+1]) - the engine's signal
convention, MEASURED at B2865 on the same signal path (the prior-bar
convention reproduced 0.17 of landed fires; entry-bar reproduced 1350/1350).

A DISAGREE is a finding about the engine OR about this script. Both are
reported; neither is a cause without a probe (CHECKLIST #189).

    python scripts/spot_check_npoc.py --cube output_x --lookback 252 \\
        --n-periods 6 --n-bins 40 --max-distance-pct 0.02 --n 50
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

LONG = "naked_poc_retest_long"


def _leg_a(df: pd.DataFrame, i: int, lookback: int, n_periods: int,
           n_bins: int, max_dist: float,
           ema_span: int | None = None) -> bool | None:
    """The naked-POC condition re-derived from raw bars. None when the slice
    cannot decide (too short, zero close) - counted as SKIPPED, never guessed."""
    sl = df.iloc[:i + 1]
    if len(sl) < lookback:
        return None
    window = sl.tail(lookback)
    chunk_size = max(1, len(window) // n_periods)
    pocs: list[float] = []
    for k in range(n_periods):
        chunk = window.iloc[k * chunk_size: (k + 1) * chunk_size]
        if len(chunk) < 5:
            continue
        lo = float(chunk["low"].min())
        hi = float(chunk["high"].max())
        if hi <= lo:
            continue
        edges = np.linspace(lo, hi, n_bins + 1)
        mids = (edges[:-1] + edges[1:]) / 2.0
        vols = np.zeros(n_bins)
        for _, row in chunk.iterrows():
            rh, rl = float(row["high"]), float(row["low"])
            rv = float(row["volume"])
            if rh <= rl or rv <= 0:
                continue
            for b in range(n_bins):
                ol = max(edges[b], rl)
                oh = min(edges[b + 1], rh)
                if oh > ol:
                    vols[b] += rv * (oh - ol) / (rh - rl)
        if float(vols.sum()) <= 0:
            continue
        pocs.append(float(mids[int(np.argmax(vols))]))
    if not pocs:
        return False                      # naked_poc_count > 0 fails
    close = float(sl["close"].iloc[-1])
    if close <= 0:
        return None
    dist = min(abs(close - p) / close for p in pocs)
    if not dist < max_dist or ema_span is None:
        return dist < max_dist
    ema = float(sl["close"].ewm(span=ema_span, adjust=False).mean().iloc[-1])
    return close > ema


def _leg_b(df: pd.DataFrame, i: int, max_dist: float) -> bool | None:
    """The PRODUCTION path: compute_period_pocs on the same PIT slice, knobs
    read back from the reloaded config - the engine's own env->config chain."""
    import backtest.config as _cfg
    from backtest.signals.volume_profile import compute_period_pocs
    sl = df.iloc[:i + 1]
    try:
        pocs = compute_period_pocs(
            sl, period_lookback=_cfg.NAKED_POC_LOOKBACK,
            n_periods=_cfg.NAKED_POC_N_PERIODS, n_bins=_cfg.NAKED_POC_N_BINS)
    except Exception:
        return None
    if not pocs:
        return False
    close = float(sl["close"].iloc[-1])
    if close <= 0:
        return None
    dist = min(abs(close - p) / close for p in pocs)
    if not dist < max_dist:
        return False
    from backtest.signals.technical import compute_ema_sma
    key = f"price_above_ema_{_cfg.STRAT_EMA_SPAN}"
    try:
        flag = compute_ema_sma(sl).get(key)
    except Exception:
        return None
    return None if flag is None else bool(flag)


def _leg_c(row, max_dist: float,
           ema_span: int | None = None) -> bool | None:
    """The RECORD: what the cube persisted at entry."""
    raw = row.get("signals_at_entry")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        import ast
        d = ast.literal_eval(raw)
    except Exception:
        try:
            d = json.loads(raw)
        except Exception:
            return None
    if not isinstance(d, dict) or not d:
        return None
    if "naked_poc_count" not in d:
        return None
    if not d.get("naked_poc_count", 0):
        return False
    dist = d.get("naked_poc_nearest_distance_pct")
    if dist is None:
        return None
    if not float(dist) < max_dist or ema_span is None:
        return float(dist) < max_dist
    above = d.get(f"price_above_ema_{ema_span}")
    return None if above is None else bool(above)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cube", required=True, help="cube dir (trade_log.csv)")
    # the S6-B2917 rule kept: NO leg default. The family has one member, but
    # the refusal shape is preserved so a future mirror cannot inherit a
    # silent default.
    ap.add_argument("--strategy", default=None, choices=[LONG])
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--lookback", type=int, required=True)
    ap.add_argument("--n-periods", type=int, required=True)
    ap.add_argument("--n-bins", type=int, required=True)
    ap.add_argument("--max-distance-pct", type=float, required=True)
    ap.add_argument("--ema-span", type=int, required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    strat = a.strategy
    if strat is None:
        try:
            import run_postconfig as _rp
            strat, _riders = _rp.graded_and_riders(Path(a.cube))
        except Exception:                               # noqa: BLE001
            strat = None
    if strat != LONG:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": ("no --strategy given and the cube manifest "
                                     "declares no graded naked-POC strategy; "
                                     "refusing rather than defaulting to a leg "
                                     "(S6-B2917 rule kept)")}))
        return 2

    # the PRODUCTION leg must see the config's knobs (env -> config reload,
    # the S6-B3171 actuators) - leg B then reads them back from _cfg exactly
    # as the screener does.
    os.environ["NAKED_POC_LOOKBACK"] = str(a.lookback)
    os.environ["NAKED_POC_N_PERIODS"] = str(a.n_periods)
    os.environ["NAKED_POC_N_BINS"] = str(a.n_bins)
    os.environ["NAKED_POC_MAX_DISTANCE_PCT"] = str(a.max_distance_pct)
    os.environ["STRAT_EMA_SPAN"] = str(a.ema_span)
    import importlib
    import backtest.config as _cfg
    importlib.reload(_cfg)

    cube = Path(a.cube)
    tl = cube / "trade_log.csv"
    if not tl.exists():
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no trade_log.csv at {tl}"}))
        return 2
    df = pd.read_csv(tl)
    rows = df[df["strategy"] == strat] if "strategy" in df.columns else df
    if rows.empty:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no {strat} rows in {tl.name}"}))
        return 2

    rnd = random.Random(a.seed)
    idx = list(rows.index)
    rnd.shuffle(idx)
    idx = idx[:a.n]

    from spot_check_trades import load_ohlcv
    agree = disagree = skipped = failures = 0
    details: list[dict] = []
    cache: dict = {}
    for ix in idx:
        r = rows.loc[ix]
        tk = str(r.get("ticker", ""))
        when = str(r.get("entry_date", ""))[:10]
        try:
            if tk not in cache:
                cache[tk] = load_ohlcv(tk)
            ohlc = cache[tk]
            if ohlc is None:
                skipped += 1
                continue
            hit = ohlc.index.searchsorted(pd.Timestamp(when))
            if hit >= len(ohlc) or str(ohlc.index[hit].date()) != when:
                skipped += 1
                continue
            i = int(hit)
            a_leg = _leg_a(ohlc, i, a.lookback, a.n_periods, a.n_bins,
                           a.max_distance_pct, a.ema_span)
            b_leg = _leg_b(ohlc, i, a.max_distance_pct)
            c_leg = _leg_c(r, a.max_distance_pct, a.ema_span)
            if a_leg is None or b_leg is None:
                skipped += 1
                continue
            if a_leg == b_leg:
                agree += 1
            else:
                disagree += 1
                details.append({"ticker": tk, "entry_date": when,
                                "leg_a_raw": a_leg, "leg_b_production": b_leg,
                                "leg_c_record": c_leg})
        except Exception as exc:                   # noqa: BLE001
            failures += 1
            details.append({"ticker": tk, "entry_date": when,
                            "execution_failure": f"{type(exc).__name__}: {exc}"})

    doc = {
        "strategy": strat,
        "cube": str(cube),
        "seed": a.seed,
        "sampled": len(idx),
        "agree": agree,
        "disagree": disagree,
        "skipped": skipped,
        "execution_failures": failures,
        "config": {"lookback": a.lookback, "n_periods": a.n_periods,
                   "n_bins": a.n_bins, "max_distance_pct": a.max_distance_pct,
                   "ema_span": a.ema_span},
        "detail": details[:25],
        "note": ("leg A is raw bin arithmetic, independent of the producer; "
                 "leg B is compute_period_pocs on the same PIT slice through "
                 "the env->config chain; a DISAGREE is a finding about either "
                 "side and is not a cause without a probe (#189)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.name}_npoc_spot_check.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in
                      ("strategy", "sampled", "agree", "disagree", "skipped",
                       "execution_failures")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
