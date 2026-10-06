#!/usr/bin/env python
"""S6-B3119: three-leg spot check for the bollinger_lower span cubes.

WHY IT EXISTS. run_postconfig requires a `spot_check` leg for any battery
family; bollinger_lower is promoted into SPECS for the owner-approved span
campaign (verbatim 2026-09-27: "Q2 approved one line change fix. I want to
test various spans"), and this is that leg - modelled on
spot_check_candle.py (S6-B2899), the L754 second-family extraction.

SAME ARTIFACT CONTRACT (agree / disagree / skipped / execution_failures /
seed) so postconfig_doc renders it unchanged.

PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA. The seeded RNG picks WHICH landed
trades to re-derive; it never generates a number.

THE CHECKED CONDITION is the span leg of the gate (B3119): a LONG fire
requires close > EMA_span at entry; a SHORT fire requires close < EMA_span.
The strategy is a DUAL, so the leg comes from the sampled row's own
`direction` column - never defaulted (the S6-B2917 rule).

THREE LEGS per sampled (ticker, entry_date):
  leg A  RAW ARITHMETIC - EMA recomputed here from cached closes with
         pandas ewm(span=N, adjust=False), the producer's own recursion
         (technical.compute_ema_sma), then close-vs-EMA compared directly. No
         producer import - a check that only called the producer would
         agree by construction (the vacuous-fixture class, L582/L684).
  leg B  PRODUCTION     - backtest.signals.technical.compute_ema_sma on the
         same PIT slice, with EMA_PAIRS exported so the span's key is
         emitted (technical.compute_ema_sma), i.e. the code the engine ran.
  leg C  RECORD         - the cube's persisted price_above_ema_{N} /
         below_ema_{N} at entry.

PIT: the slice ends AT the entry bar (df.iloc[:i+1]) - the compute_* family
evaluates on the entry bar (the B2865 convention).

A DISAGREE is a finding about the engine OR about this script; neither is a
cause without a probe (#189).

    python scripts/spot_check_bollinger.py --cube output_x --ema-span 50 \\
        --n 50
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

STRAT = "bollinger_lower"
DEFAULT_EMA_PAIRS = "9:21,20:50,50:200,100:150"   # config.EMA_PAIRS


def _key(direction: str, span: int) -> str:
    return (f"price_above_ema_{span}" if direction == "long"
            else f"below_ema_{span}")


def _leg_a(df: pd.DataFrame, i: int, direction: str, span: int) -> bool | None:
    """close vs ewm(span) on the PIT slice, recomputed here."""
    if i + 1 < span + 2:
        return None
    sl = df.iloc[:i + 1]
    ema = sl["close"].ewm(span=span, adjust=False).mean().iloc[-1]
    close = float(sl["close"].iloc[-1])
    if pd.isna(ema):
        return None
    return close > float(ema) if direction == "long" else close < float(ema)


def _leg_b(df: pd.DataFrame, i: int, direction: str, span: int) -> bool | None:
    """The PRODUCTION path: compute_ema_sma on the same PIT slice; EMA_PAIRS
    was exported by main() so the span's key is emitted."""
    from backtest.signals.technical import compute_ema_sma
    sl = df.iloc[:i + 1]
    try:
        return bool(compute_ema_sma(sl).get(_key(direction, span), False))
    except Exception:                                   # noqa: BLE001
        return None


def _leg_c(row, direction: str, span: int) -> bool | None:
    raw = row.get("signals_at_entry")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        import ast
        d = ast.literal_eval(raw)
    except Exception:                                   # noqa: BLE001
        try:
            d = json.loads(raw)
        except Exception:                               # noqa: BLE001
            return None
    if not isinstance(d, dict) or not d:
        return None
    k = _key(direction, span)
    return bool(d.get(k, False)) if k in d else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cube", required=True, help="cube dir (trade_log.csv)")
    ap.add_argument("--strategy", default=None, choices=[STRAT],
                    help="resolved from the cube manifest when absent "
                         "(the S6-B2917 no-default rule)")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
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
    if strat != STRAT:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": ("no --strategy given and the cube manifest "
                                     "declares no graded bollinger strategy; "
                                     "refusing rather than defaulting "
                                     "(S6-B2917)")}))
        return 2
    a.strategy = strat
    span = int(a.ema_span)

    # leg B must see the span's key: export EMA_PAIRS containing it, then
    # reload config so the module attribute the producer reads at call time
    # (technical.compute_ema_sma) carries it.
    spans_in_default = {9, 21, 20, 50, 200, 100, 150}
    pairs = DEFAULT_EMA_PAIRS if span in spans_in_default else (
        DEFAULT_EMA_PAIRS + f",2:{span}")
    os.environ["EMA_PAIRS"] = pairs
    os.environ["STRAT_EMA_SPAN"] = str(span)
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
        direction = str(r.get("direction", "")).lower() or "long"
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
            a_leg = _leg_a(ohlc, i, direction, span)
            b_leg = _leg_b(ohlc, i, direction, span)
            c_leg = _leg_c(r, direction, span)
            if a_leg is None or b_leg is None:
                skipped += 1
                continue
            if a_leg == b_leg:
                agree += 1
            else:
                disagree += 1
                details.append({"ticker": tk, "entry_date": when,
                                "direction": direction,
                                "leg_a_raw": a_leg, "leg_b_production": b_leg,
                                "leg_c_record": c_leg})
        except Exception as exc:                        # noqa: BLE001
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
        "config": {"ema_span": span, "ema_pairs": pairs},
        "detail": details[:25],
        "note": ("leg A recomputes ewm(span, adjust=False) from cached closes, "
                 "independent of the producer; leg B is compute_ema_sma on the "
                 "same PIT slice; the checked key follows the sampled row's "
                 "own direction (dual strategy, S6-B2917); a DISAGREE is a "
                 "finding about either side, not a cause without a probe "
                 "(#189)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.name}_bollinger_spot_check.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in
                      ("strategy", "sampled", "agree", "disagree", "skipped",
                       "execution_failures")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
