#!/usr/bin/env python
"""S6-B3140: three-leg spot check for the pairs_mean_reversion_long cubes.

WHY IT EXISTS. run_postconfig requires a `spot_check` leg for any battery
family; pairs_mean_reversion_long enters SPECS for the owner-launched Step-1
campaign (verbatim 2026-10-08 "proceed with step 1"), and this is that leg -
modelled on spot_check_bollinger.py (S6-B3119), the L754 family-extraction
contract.

SAME ARTIFACT CONTRACT (agree / disagree / skipped / execution_failures /
seed) so postconfig_doc renders it unchanged.

PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA. The seeded RNG picks WHICH landed
trades to re-derive; it never generates a number.

THE CHECKED CONDITION is the z-score leg of the gate (screener
strat_pairs_mean_reversion_long): a fire requires pair_zscore_signed < -2.0
for the RECORDED counterparty pair. The strategy is LONG-only (the B2085/F24
owner re-scope), so no direction branch exists.

THREE LEGS per sampled (ticker, entry_date):
  leg A  RAW ARITHMETIC - the spread z-score recomputed HERE from the T5b
         snapshot row (hedge_ratio, intercept) and cached closes of both
         legs: spread = A - (intercept + hedge*B), rolling(--z-window)
         mean/std (60 at production; S6-B3141a),
         z = (last - mean)/std, signed by which side the ticker is. No
         producer import - a check that only called the producer would
         agree by construction (the vacuous-fixture class, L582/L684).
  leg B  PRODUCTION     - backtest.signals.pairs_trading.
         compute_pair_signals_for_ticker on the same PIT inputs the engine
         passes (screener.py: ticker_close = last 90 closes of the PIT
         slice), i.e. the code the engine ran.
  leg C  RECORD         - the cube's persisted pair_zscore_signed /
         pair_counterparty / pair_half_life at entry.

PIT: the slice ends AT the entry bar (df.iloc[:i+1]) - the compute_* family
evaluates on the entry bar (the B2865 convention).

A DISAGREE is a finding about the engine OR about this script; neither is a
cause without a probe (#189).

    python scripts/spot_check_pairs.py --cube output_x --n 50
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# adapter-dispatched family leg: no module-level STRAT constant
# (test_b3120d ratchet; the candle-grader shape)
PAIRS_LONG = "pairs_mean_reversion_long"
Z_TOL = 5e-4       # pair_zscore rounds to 4dp (pairs_trading.pair_zscore)
PAIRS_DIR = ROOT / "data_prefetch" / "derived" / "cointegrated_pairs_t1a"


def _snapshot_for(as_of):
    """Latest T5b snapshot parquet dated <= as_of (producer's own rule)."""
    from backtest.signals.pairs_trading import _load_pair_snapshots
    latest = None
    for snap_date, p in _load_pair_snapshots(PAIRS_DIR):
        if snap_date <= as_of:
            latest = p
    return latest


def _closes_to(tk: str, as_of, cache: dict, n_bars: int = 90):
    """Last-n_bars close series of `tk` ending at as_of, indexed by date -
    the shape the producer builds for the peer leg (n_bars follows the
    z-window, pairs_trading.pair_slice_bars; 90 at production)."""
    key = tk.replace(".", "-")
    df = cache.get(key)
    if df is None:
        p = ROOT / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{key}.parquet"
        if not p.exists():
            cache[key] = pd.DataFrame()
            return None
        df = pd.read_parquet(p)
        if "date" in df.columns:
            df = df.copy()
            df["date_dt"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df.sort_values("date_dt")
        cache[key] = df
    if df is None or df.empty or "date_dt" not in df.columns:
        return None
    sl = df[df["date_dt"] <= as_of]
    if sl.empty:
        return None
    return pd.Series(sl["close"].values[-n_bars:],
                     index=sl["date_dt"].values[-n_bars:])


def _leg_a(tk: str, peer: str, as_of, cache: dict, window: int = 60,
           significance: float = 0.05):
    """(signed z, snapshot half_life) recomputed here, or (None, why)."""
    snap = _snapshot_for(as_of)
    if snap is None:
        return None, "no T5b snapshot <= as_of"
    pairs = pd.read_parquet(snap)
    row = pairs[((pairs["ticker_a"] == tk) & (pairs["ticker_b"] == peer))
                | ((pairs["ticker_a"] == peer) & (pairs["ticker_b"] == tk))]
    if row.empty:
        return None, f"pair ({tk},{peer}) not in snapshot {Path(snap).name}"
    r = row.iloc[0]
    if significance < 0.05 and not float(r["pvalue"]) < significance:
        # the recorded pair could not exist under the declared level: a
        # finding, not a skip (the engine ran a different knob, or this
        # script was told the wrong one)
        return {"z_signed": float("nan"), "half_life": float(r["half_life"]),
                "filtered_out": float(r["pvalue"])}, ""
    is_a = r["ticker_a"] == tk
    from backtest.signals.pairs_trading import pair_slice_bars
    n_bars = pair_slice_bars(window)
    a_ser = _closes_to(str(r["ticker_a"]), as_of, cache, n_bars)
    b_ser = _closes_to(str(r["ticker_b"]), as_of, cache, n_bars)
    if a_ser is None or b_ser is None:
        return None, "cached closes unavailable for a leg"
    df = pd.concat([a_ser, b_ser], axis=1, join="inner").dropna()
    if len(df) < window + 1:
        return None, f"only {len(df)} joint bars (< window+1)"
    spread = df.iloc[:, 0] - (float(r["intercept"])
                              + float(r["hedge_ratio"]) * df.iloc[:, 1])
    mean = spread.rolling(window).mean().iloc[-1]
    std = spread.rolling(window).std().iloc[-1]
    if not (float(std) > 0):
        return None, "zero/NaN rolling std"
    z = (float(spread.iloc[-1]) - float(mean)) / float(std)
    signed = z if is_a else -z
    return {"z_signed": signed, "half_life": float(r["half_life"])}, ""


def _leg_b(tk: str, as_of, ohlc: pd.DataFrame, i: int, window: int = 60,
           significance: float = 0.05):
    """The PRODUCTION path on the engine's own input shape, with the
    declared knobs passed EXPLICITLY (never read from this process's env),
    so a cube whose engine ran other knobs disagrees instead of matching."""
    from backtest.signals.pairs_trading import (
        compute_pair_signals_for_ticker, pair_slice_bars)
    n = pair_slice_bars(window)
    sl = ohlc.iloc[:i + 1]
    dates = [ts.date() for ts in sl.index[-n:]]
    ticker_close = pd.Series(sl["close"].values[-n:], index=dates)
    return compute_pair_signals_for_ticker(
        tk, as_of, ticker_close, window=window,
        significance=significance) or {}


def _leg_c(row):
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
    return d if isinstance(d, dict) and d else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cube", required=True, help="cube dir (trade_log.csv)")
    ap.add_argument("--strategy", default=None, choices=[PAIRS_LONG],
                    help="resolved from the cube manifest when absent "
                         "(the S6-B2917 no-default rule)")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--z-window", type=int, default=60,
                    help="P6 pair z-score window the engine ran (S6-B3141a)")
    ap.add_argument("--eg-significance", type=float, default=0.05,
                    help="P5 Engle-Granger level the engine ran (S6-B3141a)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    strat = a.strategy
    if strat is None:
        try:
            import run_postconfig as _rp
            strat, _riders = _rp.graded_and_riders(Path(a.cube))
        except Exception:                               # noqa: BLE001
            strat = None
    if strat != PAIRS_LONG:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": ("no --strategy given and the cube manifest "
                                     "declares no graded pairs strategy; "
                                     "refusing rather than defaulting "
                                     "(S6-B2917)")}))
        return 2
    a.strategy = strat

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
    ohlc_cache: dict = {}
    peer_cache: dict = {}
    for ix in idx:
        r = rows.loc[ix]
        tk = str(r.get("ticker", ""))
        when = str(r.get("entry_date", ""))[:10]
        try:
            rec = _leg_c(r)
            peer = str((rec or {}).get("pair_counterparty", "") or "")
            if not peer:
                skipped += 1
                continue
            if tk not in ohlc_cache:
                ohlc_cache[tk] = load_ohlcv(tk)
            ohlc = ohlc_cache[tk]
            if ohlc is None:
                skipped += 1
                continue
            hit = ohlc.index.searchsorted(pd.Timestamp(when))
            if hit >= len(ohlc) or str(ohlc.index[hit].date()) != when:
                skipped += 1
                continue
            i = int(hit)
            as_of = ohlc.index[i].date()
            a_leg, why = _leg_a(tk, peer, as_of, peer_cache,
                                window=a.z_window,
                                significance=a.eg_significance)
            b_leg = _leg_b(tk, as_of, ohlc, i, window=a.z_window,
                           significance=a.eg_significance)
            c_z = (rec or {}).get("pair_zscore_signed")
            c_hl = (rec or {}).get("pair_half_life")
            if a_leg is None or not b_leg or c_z is None:
                skipped += 1
                if why:
                    details.append({"ticker": tk, "entry_date": when,
                                    "skip": why})
                continue
            b_z = b_leg.get("pair_zscore_signed")
            b_peer = str(b_leg.get("pair_counterparty", "") or "")
            # agreement: leg A arithmetic vs leg B production on the
            # RECORDED pair's z (when B selected the same peer), and the
            # gate condition (z < -2.0) equal across A and B.
            gate_a = a_leg["z_signed"] < -2.0
            gate_b = (b_z is not None) and (float(b_z) < -2.0)
            # S6-B3141a: leg C's recorded z is COMPARED, not only fetched -
            # without it a cube whose engine ran another z-window agreed
            # whenever the max-|z| peer happened not to move (MEASURED:
            # 15 of 20 agreed on the production cube checked at window 40)
            num_ok = (b_peer == peer
                      and b_z is not None
                      and abs(a_leg["z_signed"] - float(b_z)) <= Z_TOL
                      and abs(a_leg["z_signed"] - float(c_z)) <= Z_TOL)
            hl_ok = (c_hl is None
                     or abs(a_leg["half_life"] - float(c_hl)) <= 1e-6)
            if num_ok and gate_a == gate_b and hl_ok:
                agree += 1
            else:
                disagree += 1
                details.append({"ticker": tk, "entry_date": when,
                                "peer_recorded": peer, "peer_b": b_peer,
                                "leg_a_z": round(a_leg["z_signed"], 4),
                                "leg_b_z": b_z, "leg_c_z": c_z,
                                "leg_a_hl": a_leg["half_life"],
                                "leg_c_hl": c_hl,
                                "gate_a": gate_a, "gate_b": gate_b})
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
        "config": {"config": "production (zero-knob family)"},
        "detail": details[:25],
        "note": ("leg A recomputes the spread z-score from the T5b snapshot "
                 "row and cached closes, independent of the producer; leg B "
                 "is compute_pair_signals_for_ticker on the engine's own "
                 "input shape (screener.py pairs block); leg C is the "
                 "persisted record. LONG-only strategy (B2085/F24), no "
                 "direction branch. A DISAGREE is a finding about either "
                 "side, not a cause without a probe (#189)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.name}_pairs_spot_check.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in
                      ("strategy", "sampled", "agree", "disagree", "skipped",
                       "execution_failures")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
