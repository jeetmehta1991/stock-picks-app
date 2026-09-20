#!/usr/bin/env python
"""S6-B2899: three-leg spot check for the candle anatomy cubes.

WHY IT EXISTS. run_postconfig requires a `spot_check` leg for any battery
family (_TOOLS_REQUIRED). three_white_soldiers / three_black_crows_short were
promoted into SPECS at B2897 so the 54-config anatomy campaign can run (owner
ruling 2026-09-20, "Candle goes first"), and the missing spot_check was the one
remaining adapter gap - family_refusal reported exactly that, and nothing else.

SAME ARTIFACT CONTRACT as spot_check_institutional.py (agree / disagree /
skipped / execution_failures / seed) so postconfig_doc renders it unchanged.

PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA. The seeded RNG here picks WHICH
landed trades to re-derive; it never generates a number. Every figure this
script reports is computed from real cached bars and a real cube, so a value
quoted from it is a measurement, not a draw. The B1719b declaration is
deliberately NOT "SYNTHETIC" - labelling a sampler as synthetic would be the
false provenance that check exists to prevent.

THREE LEGS per sampled (ticker, entry_date):
  leg A  RAW ARITHMETIC - the anatomy condition re-derived here, from cached
         OHLCV, with explicit bar arithmetic and no import of the producer.
         This is what makes the check independent: if it only called the
         producer it would agree with the engine by construction and test
         nothing (the vacuous-fixture class, L582/L684).
  leg B  PRODUCTION     - backtest.signals.technical.compute_candles on the
         same PIT slice with the config's env knobs set, i.e. the exact code
         the engine ran.
  leg C  RECORD         - the cube's own signals_at_entry for the pattern key.

PIT: the slice ends AT the entry bar (df.iloc[:i+1]). MEASURED at B2865, the
producer evaluates the pattern on the ENTRY bar, not the prior one - the
prior-bar convention reproduced only 0.17 of landed fires while the entry-bar
convention reproduced 1350/1350 soldiers and 1535/1535 crows. Using the wrong
convention here would manufacture a disagreement on ~83 pct of trades.

A DISAGREE is a finding about the engine OR about this script. Both are
reported; neither is a cause without a probe (CHECKLIST #189).

    python scripts/spot_check_candle.py --cube output_x --n-bars 3 \\
        --min-body-pct 0.0 --min-step-pct 0.0 --max-wick-pct '' --n 50
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

BULLISH = "three_white_soldiers"
BEARISH = "three_black_crows_short"

# S6-B2899: the STRATEGY name is not the SIGNAL key. compute_candles
# emits "three_black_crows"; the strategy that consumes it is
# "three_black_crows_short". MEASURED by this very check on its first
# run - leg B asked for the strategy name, got nothing, and returned
# False for 40 of 40 rows while leg A returned True. Soldiers agreed
# only because its two names happen to coincide, which is exactly the
# near-identical-name trap L699 records.
SIGNAL_KEY = {BULLISH: "three_white_soldiers",
              BEARISH: "three_black_crows"}


def _leg_a(df: pd.DataFrame, i: int, bullish: bool, n_bars: int,
           min_body: float, min_step: float,
           max_wick: float | None) -> bool | None:
    """The anatomy condition, re-derived from raw bars. None when the slice is
    too short to decide - counted as SKIPPED, never guessed."""
    if i + 1 < max(5, n_bars + 1):
        return None
    o = df["open"].values
    h = df["high"].values
    lo = df["low"].values
    c = df["close"].values
    # index i is the entry bar; bar -k of the producer's view is i - (k - 1)
    for k in range(1, n_bars + 1):
        j = i - (k - 1)
        rng = h[j] - lo[j]
        if bullish and not (c[j] > o[j]):
            return False
        if (not bullish) and not (c[j] < o[j]):
            return False
        if abs(c[j] - o[j]) < min_body * rng:
            return False
        if max_wick is not None:
            wick = ((h[j] - max(c[j], o[j])) if bullish
                    else (min(c[j], o[j]) - lo[j]))
            if wick > float(max_wick) * rng:
                return False
    for k in range(1, n_bars):
        j = i - (k - 1)
        prev_rng = h[j - 1] - lo[j - 1]
        step = (c[j] - c[j - 1]) if bullish else (c[j - 1] - c[j])
        if not (step > min_step * prev_rng):
            return False
        if bullish and not (o[j] > o[j - 1]):
            return False
        if (not bullish) and not (o[j] < o[j - 1]):
            return False
    return True


def _leg_b(df: pd.DataFrame, i: int, key: str) -> bool | None:
    """The PRODUCTION path: compute_candles on the same PIT slice, with the
    knobs already exported to the environment by main()."""
    from backtest.signals.technical import compute_candles
    sl = df.iloc[:i + 1]
    try:
        return bool(compute_candles(sl).get(key, False))
    except Exception:
        return None


def _leg_c(row) -> bool | None:
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
    return bool(d.get(_KEY, False)) if _KEY in d else None


_KEY = BULLISH


def main() -> int:
    global _KEY
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cube", required=True, help="cube dir (trade_log.csv)")
    ap.add_argument("--strategy", default=BULLISH,
                    choices=[BULLISH, BEARISH])
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-bars", type=int, required=True)
    ap.add_argument("--min-body-pct", type=float, required=True)
    ap.add_argument("--min-step-pct", type=float, required=True)
    ap.add_argument("--max-wick-pct", default="",
                    help="empty string means NO wick bound (the None level)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    _KEY = SIGNAL_KEY[a.strategy]
    bullish = a.strategy == BULLISH
    wick = None if str(a.max_wick_pct).strip() == "" else float(a.max_wick_pct)

    # the PRODUCTION leg must see the config's knobs. compute_candles reads
    # them at CALL time via getattr on the config module (B2865), so exporting
    # here and re-importing is what makes leg B the engine's own behaviour.
    os.environ["CANDLE_N_BARS"] = str(a.n_bars)
    os.environ["CANDLE_MIN_BODY_PCT"] = str(a.min_body_pct)
    os.environ["CANDLE_MIN_STEP_PCT"] = str(a.min_step_pct)
    os.environ["CANDLE_MAX_WICK_PCT"] = "" if wick is None else str(wick)
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
    rows = df[df["strategy"] == a.strategy] if "strategy" in df.columns else df
    if rows.empty:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no {a.strategy} rows in {tl.name}"}))
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
            a_leg = _leg_a(ohlc, i, bullish, a.n_bars, a.min_body_pct,
                           a.min_step_pct, wick)
            b_leg = _leg_b(ohlc, i, SIGNAL_KEY[a.strategy])
            c_leg = _leg_c(r)
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
        "strategy": a.strategy,
        "cube": str(cube),
        "seed": a.seed,
        "sampled": len(idx),
        "agree": agree,
        "disagree": disagree,
        "skipped": skipped,
        "execution_failures": failures,
        "config": {"n_bars": a.n_bars, "min_body_pct": a.min_body_pct,
                   "min_step_pct": a.min_step_pct, "max_wick_pct": wick},
        "detail": details[:25],
        "note": ("leg A is raw bar arithmetic, independent of the producer; "
                 "leg B is compute_candles on the same PIT slice; a DISAGREE "
                 "is a finding about either side and is not a cause without a "
                 "probe (#189)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.name}_candle_spot_check.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in
                      ("strategy", "sampled", "agree", "disagree", "skipped",
                       "execution_failures")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
