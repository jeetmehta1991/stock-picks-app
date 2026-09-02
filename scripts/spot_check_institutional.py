"""B2520: three-leg spot check for institutional_committed_growth_long cubes.

The smc spot check (spot_check_trades.py, B1588/B1631) re-derives every
sampled trade from raw OHLCV; nothing equivalent existed for the 13F family,
so step 4 was recorded SKIPPED on every institutional cube. This is the
family's counterpart, same artifact contract (agree / disagree / skipped /
execution_failures / seed / ema_span), so postconfig_doc renders it unchanged.

THREE LEGS per sampled (ticker, entry_date):
  leg A  RAW ARTIFACT  - the persistence-precompute parquet is read directly
         (own snapshot selection: newest snapshot dated <= entry_date) for
         committed_growth_holders; the EMA leg is re-derived from cached OHLCV
         with a PIT slice (ohlc.iloc[:i+1]) exactly as the smc check does.
  leg B  PRODUCTION    - backtest.signals.institutional_persistence_consumer.
         compute_persistence_signals(ticker, entry_date), the consumer the
         engine ran, called at the same inputs.
  leg C  RECORD        - the cube's own signals_at_entry (committed_growth_
         holders, institutional_increased, price_above_ema_<span>).
The gate is re-derived from legs A+B - committed >= P7 OR (committed == 0
AND increased >= P8), AND close > EMA(span) - and compared with the fact
that the engine fired. institutional_increased has no precompute to read
(it comes from the 13F delta path), so the fallback arm is taken from the
RECORD and labelled as such; a trade whose record is EMPTY and whose
committed leg is below P7 cannot be re-derived and is SKIPPED_NO_RECORD,
which is the S6-B2512 population, counted and named rather than hidden.

PIT: the snapshot chosen is <= entry_date; the OHLCV slice ends AT the entry
bar. A DISAGREE is a finding about either the engine or this script - both
are reported, neither is a cause without a probe (CHECKLIST #189).

The precompute directory is resolved through the SAME helper the producer
and consumer use (INST_PERSIST_CACHE_TAG-aware, S6-B2484), so this check
reads the artifact the engine read only when run under the run's own env -
the directory is recorded in the artifact for that reason.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

STRAT = "institutional_committed_growth_long"


def _precompute_dir() -> Path:
    from build_institutional_persistence_precompute import persistence_cache_dir
    return persistence_cache_dir(REPO)


def raw_committed(pre_dir: Path, ticker: str, when: _dt.date):
    """Leg A: newest snapshot dated <= when, read directly from parquet."""
    snaps = []
    for p in pre_dir.glob("*.parquet"):
        try:
            snaps.append((_dt.date.fromisoformat(p.stem), p))
        except ValueError:
            continue
    elig = sorted(d for d in snaps if d[0] <= when)
    if not elig:
        return None, None
    d, p = elig[-1]
    df = pd.read_parquet(p, columns=["ticker", "committed_growth_holders"])
    row = df[df["ticker"] == ticker]
    if row.empty:
        return None, str(d)
    return int(row["committed_growth_holders"].iloc[0] or 0), str(d)


def rederive(ticker: str, when: pd.Timestamp, ema_span: int, p7: int, p8: int,
             record: dict, pre_dir: Path, ohlcv) -> dict:
    from backtest.signals.institutional_persistence_consumer import (
        compute_persistence_signals)
    out: dict = {"ok": True}
    # EMA leg from raw OHLCV, PIT slice
    if ohlcv is None:
        return {"ok": False, "reason": "NO_OHLCV"}
    i = int(ohlcv.index.get_indexer([when], method="pad")[0])
    if i < ema_span:
        return {"ok": False, "reason": "insufficient_history"}
    sub = ohlcv.iloc[:i + 1]
    close = float(sub["close"].iloc[-1])
    ema = float(sub["close"].ewm(span=ema_span, adjust=False).mean().iloc[-1])
    out.update(close=close, ema=ema, above_ema=bool(close > ema), bar_index=i)

    raw, snap = raw_committed(pre_dir, ticker, when.date())
    prod = compute_persistence_signals(ticker, when.date())
    prod_committed = prod.get("committed_growth_holders")
    rec_committed = record.get("committed_growth_holders")
    rec_increased = record.get("institutional_increased")
    out.update(raw_committed=raw, raw_snapshot=snap,
               production_committed=prod_committed,
               record_committed=rec_committed, record_increased=rec_increased,
               record_above_ema=record.get(f"price_above_ema_{ema_span}"),
               legs_ab_agree=(raw == prod_committed))
    committed = prod_committed if prod_committed is not None else (raw or 0)
    increased = float(rec_increased or 0)
    primary = committed >= p7
    fallback = (committed == 0 and increased >= p8)
    if not primary and not record and committed == 0:
        # the fallback arm needs institutional_increased and the record is
        # empty (S6-B2512 population): not re-derivable, say so
        return {**out, "ok": False, "reason": "NO_RECORD",
                "committed_used": committed}
    out.update(committed_used=committed, primary_arm=bool(primary),
               fallback_arm=bool(fallback),
               fallback_from_record=bool(fallback),
               should_fire=bool((primary or fallback) and out["above_ema"]))
    return out


def check_execution(row, df, start, end) -> dict:
    out = {}
    ed = pd.Timestamp(row["entry_date"])
    out["entry_is_trading_day"] = bool(ed in df.index)
    out["entry_in_window"] = bool(start <= ed.date() <= end)
    xd = row.get("exit_date")
    if xd is not None and not pd.isna(xd):
        xd = pd.Timestamp(xd)
        out["exit_after_entry"] = bool(xd >= ed)
        out["exit_in_window"] = bool(xd.date() <= end)
        rec_hold = row.get("hold_days")
        if rec_hold is not None and not pd.isna(rec_hold):
            obs_cal = int((xd - ed).days)
            out["hold_days_matches"] = bool(abs(obs_cal - float(rec_hold)) <= 1)
    p = row.get("pnl_pct")
    out["pnl_finite"] = bool(p is not None and not pd.isna(p)
                             and np.isfinite(float(p)))
    return out


def run(cube_dir: Path, *, n: int = 50, seed: int = 42, ema_span: int = 200,
        p7: int = 3, p8: int = 5, start: str = "2024-05-05",
        end: str = "2026-05-05", out: Path | None = None) -> dict:
    from spot_check_trades import load_ohlcv
    tl = pd.read_csv(cube_dir / "trade_log.csv", low_memory=False,
                     usecols=["ticker", "strategy", "entry_date", "exit_date",
                              "hold_days", "pnl_pct", "signals_at_entry"])
    tl = tl[tl["strategy"] == STRAT]
    ent = tl.drop_duplicates(subset=["ticker", "entry_date"])
    random.seed(seed)
    idx = sorted(random.sample(range(len(ent)), min(n, len(ent))))
    sample = ent.iloc[idx]
    pre_dir = _precompute_dir()
    s_d, e_d = _dt.date.fromisoformat(start), _dt.date.fromisoformat(end)
    results, agree, disagree, skipped, exec_fail = [], 0, 0, 0, []
    cache: dict = {}
    for _, r in sample.iterrows():
        t = str(r["ticker"])
        raw = r.get("signals_at_entry")
        try:
            record = json.loads(raw) if isinstance(raw, str) and raw.strip() else {}
        except ValueError:
            record = {}
        if t not in cache:
            cache[t] = load_ohlcv(t)
        df = cache[t]
        when = pd.Timestamp(r["entry_date"])
        d = rederive(t, when, ema_span, p7, p8, record, pre_dir, df)
        ex = check_execution(r, df, s_d, e_d) if df is not None else {}
        bad = [k for k, v in ex.items() if isinstance(v, bool) and not v]
        if bad:
            exec_fail.append({"ticker": t, "entry_date": str(r["entry_date"]),
                              "failed": bad})
        if not d.get("ok"):
            skipped += 1
            status = "SKIPPED_" + str(d.get("reason"))
        elif d["should_fire"]:
            agree += 1
            status = "AGREE"
        else:
            disagree += 1
            status = "DISAGREE"
        results.append({"ticker": t, "entry_date": str(r["entry_date"])[:10],
                        "status": status, "record_empty": not record,
                        **d, "execution": ex})
    doc = {"cube": str(cube_dir / "trade_exit_detail.csv").replace("\\", "/"),
           "family": STRAT, "checker": "scripts/spot_check_institutional.py (B2520)",
           "n_sampled": int(len(sample)), "seed": seed,
           "swing_length": None, "close_mitigation": None, "tail_n": None,
           "ema_span": ema_span, "min_committed_growth": p7,
           "fallback_min_increased": p8,
           "precompute_dir": str(pre_dir).replace("\\", "/"),
           "agree": agree, "disagree": disagree, "skipped": skipped,
           "empty_records": int(sum(1 for x in results if x["record_empty"])),
           "legs_ab_disagree": int(sum(1 for x in results
                                       if x.get("legs_ab_agree") is False)),
           "execution_failures": exec_fail, "rows": results}
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", required=True, help="cube dir (holds trade_log.csv)")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ema-span", type=int, required=True)
    ap.add_argument("--min-committed-growth", type=int, default=3)
    ap.add_argument("--fallback-min-increased", type=int, default=5)
    ap.add_argument("--start", default="2024-05-05")
    ap.add_argument("--end", default="2026-05-05")
    ap.add_argument("--out", default=None,
                    help="default output_audit/<cube dir>_spot_check.json")
    a = ap.parse_args()
    cube = Path(a.cube)
    if cube.name == "trade_exit_detail.csv":
        cube = cube.parent
    out = Path(a.out) if a.out else (
        REPO / "output_audit" / f"{cube.name}_spot_check.json")
    doc = run(cube, n=a.n, seed=a.seed, ema_span=a.ema_span,
              p7=a.min_committed_growth, p8=a.fallback_min_increased,
              start=a.start, end=a.end, out=out)
    print(f"cube entries sampled {doc['n_sampled']} (seed {doc['seed']})\n"
          f"PRODUCER RE-DERIVATION: {doc['agree']} agree / {doc['disagree']} "
          f"DISAGREE / {doc['skipped']} skipped; empty records "
          f"{doc['empty_records']}; legs A/B disagree {doc['legs_ab_disagree']}\n"
          f"EXECUTION CHECKS: {len(doc['execution_failures'])} trades with >=1 "
          f"failed check\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
