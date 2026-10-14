#!/usr/bin/env python
"""S6-B3155a (owner ruling 2026-10-14, verbatim "S6-B3155a b"): confirm a
disputed engine-cache bar against ONE third source, and say which local cache
holds the full session.

WHY. On 2026-05-05 - the last bar of the R5 window and of every Step-2 window
ending that day - the engine cache (backtest/data/cache/ohlcv, what the engine
prices from) and the prefetch cache (data_prefetch/polygon/ohlcv_daily) hold
DIFFERENT bars for hundreds of tickers, while the prior bar is identical in
both for 1,687 of 1,688 tickers (the exception, CVNA, carries a 5.0x scale on
every bar - a different defect, checked per ticker in `verdicts`). The engine
cache's bar looks like a partial session. Neither local file
can settle it, because each is one of the two disputed records.

THE THIRD SOURCE is Yahoo Finance via yfinance (auto_adjust=False): independent
of Polygon, which supplies BOTH local caches (Massive's API is Polygon's, so it
is not a third source; Alpha Vantage refuses daily history past its latest
100 bars without a premium plan). yfinance is pinned in requirements.txt for
one-time SETUP reads only - this is one, outside the backtest; nothing in the
engine imports this file.

SUBCOMMANDS
  read      download the third source for every ticker whose engine cache
            ends on --date, beside both local caches, for --date and --prior
            (raw JSON; the only step that touches the network)
  classify  offline, deterministic over the raw JSON:
            1. corporate actions: Yahoo restates history for later splits and
               spin-offs, so a factor k = yahoo_close(prior) / local_close(prior)
               is measured on the UNDISPUTED prior bar and Yahoo's disputed bar
               is divided (prices) / multiplied (volume) by it;
            2. calibration on CONTROLS only - tickers whose two local caches
               hold the identical --date bar: tolerances are the 99th
               percentile of the normalised Yahoo-vs-local differences, fixed
               before any disputed ticker is classified;
            3. verdicts per disputed ticker (local caches differ on --date):
               CONFIRMED (Yahoo reproduces the prefetch bar and not the
               engine bar), CONFIRMED_PRIOR_DIFFERS (as CONFIRMED, but the
               two caches' --prior bars differ, so a one-row repair would
               splice two price bases - never repaired), REFUTED (the
               reverse), AMBIGUOUS (both), UNRESOLVED (neither), NO_YAHOO;
               for tickers with no prefetch file,
               N_MATCHES / N_DIFFERS / N_NO_YAHOO against the engine bar.
               "Reproduces" = close within the close tolerance AND volume
               within the volume tolerance.
            CONFIRMED rows are the repair set for
            scripts/repair_final_bar_partial_session.py: their values come
            from the PREFETCH (the cache's own vendor), never from Yahoo.

usage:
  python scripts/final_bar_third_source_check.py read --date 2026-05-05 \
      --prior 2026-05-04 --out output_audit/b3155a_final_bar_third_source_raw.json
  python scripts/final_bar_third_source_check.py classify \
      --raw output_audit/b3155a_final_bar_third_source_raw.json \
      --out output_audit/b3155a_final_bar_third_source.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit(f"final_bar_third_source_check: {ROOT} is not the repo root (L846)")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

PREFETCH_DIR = ROOT / "data_prefetch" / "polygon" / "ohlcv_daily"
FIELDS = ("open", "high", "low", "close", "volume")
PRICES = ("open", "high", "low", "close")
IDENTICAL_REL = 1e-6        # two local copies of one vendor's bar: float noise only
CAL_PERCENTILE = 99


def prefetch_file(ticker: str):
    """The prefetch spells class shares with '-'; the engine index may not."""
    for cand in (ticker, ticker.replace(".", "-"), ticker.replace("-", "."),
                 ticker.replace("_", "-")):
        f = PREFETCH_DIR / f"{cand}.parquet"
        if f.exists():
            return f
    return None


def yahoo_symbol(ticker: str) -> str:
    return ticker.replace(".", "-").replace("_", "-")


def _bar(df, day):
    import pandas as pd
    if df is None:
        return None
    r = df[df["date"] == pd.Timestamp(day)]
    if len(r) != 1:
        return None
    return {c: float(r[c].iloc[0]) for c in FIELDS}


def read(date: str, prior: str, out: Path, chunk: int = 100, pause: float = 2.0) -> dict:
    """The network step: Yahoo bars for (prior, date) for every ticker whose
    engine cache ends on `date`, beside both local caches."""
    import pandas as pd
    import yfinance as yf
    from backtest.data.cache import _cache_path

    idx = json.loads((ROOT / "backtest" / "data" / "cache" / "index.json").read_text())
    days = (prior, date)
    local = {}
    for t in sorted(idx):
        ef = _cache_path(t)
        if not ef.exists():
            continue
        e = pd.read_parquet(ef)
        e["date"] = pd.to_datetime(e["date"]).dt.normalize()
        if e["date"].max() != pd.Timestamp(date):
            continue
        pf = prefetch_file(t)
        p = None
        if pf is not None:
            p = pd.read_parquet(pf)
            p["date"] = pd.to_datetime(p["date"]).dt.normalize()
        local[t] = {"engine_file": str(ef.relative_to(ROOT)).replace("\\", "/"),
                    "prefetch_file": (str(pf.relative_to(ROOT)).replace("\\", "/") if pf else None),
                    "engine": {d: _bar(e, d) for d in days},
                    "prefetch": {d: _bar(p, d) for d in days}}
    syms = sorted({yahoo_symbol(t) for t in local})
    end_excl = (pd.Timestamp(date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    yahoo, failures = {}, []
    t0 = time.time()
    for i in range(0, len(syms), chunk):
        part = syms[i:i + chunk]
        raw = None
        for attempt in (1, 2):
            try:
                raw = yf.download(part, start=prior, end=end_excl, interval="1d",
                                  auto_adjust=False, actions=False, progress=False,
                                  group_by="ticker", threads=True)
                break
            except Exception as exc:  # recorded in the artifact, never swallowed
                failures.append({"chunk_start": i, "attempt": attempt, "error": repr(exc)})
                time.sleep(5)
        if raw is not None:
            for s in part:
                try:
                    y = raw[s] if isinstance(raw.columns, pd.MultiIndex) else raw
                    y = y.dropna(how="all").reset_index()
                    y = y.rename(columns={"Date": "date", "Open": "open", "High": "high",
                                          "Low": "low", "Close": "close", "Volume": "volume"})
                    y["date"] = pd.to_datetime(y["date"]).dt.tz_localize(None).dt.normalize()
                    yahoo[s] = {d: _bar(y, d) for d in days}
                except Exception as exc:
                    yahoo[s] = {"error": repr(exc)}
        time.sleep(pause)
    for t in local:
        local[t]["yahoo_symbol"] = yahoo_symbol(t)
        local[t]["yahoo"] = yahoo.get(yahoo_symbol(t))
    doc = {"ticket": "S6-B3155a", "date": date, "prior": prior,
           "source": f"Yahoo Finance via yfinance {yf.__version__}, auto_adjust=False",
           "read_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "download_seconds": round(time.time() - t0, 1), "n_tickers": len(local),
           "n_symbols": len(syms), "chunks_failed": failures, "rows": local}
    out.write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8",
                   newline="\n")
    return doc


def _rel(a, b):
    return None if (a is None or b is None or b == 0) else a / b - 1.0


def _identical(x, y) -> bool:
    return x is not None and y is not None and all(
        abs(_rel(x[f], y[f]) or 0.0) <= IDENTICAL_REL for f in FIELDS)


def _yahoo(r, day):
    y = r.get("yahoo")
    return y.get(day) if isinstance(y, dict) else None


def corporate_action_factor(r, prior: str):
    """k measured on the undisputed prior bar; None when unmeasurable."""
    y = _yahoo(r, prior)
    ref = r["prefetch"].get(prior) or r["engine"].get(prior)
    if y is None or ref is None or not ref["close"]:
        return None
    return y["close"] / ref["close"]


def yahoo_normalised(r, date: str, prior: str):
    y = _yahoo(r, date)
    k = corporate_action_factor(r, prior)
    if y is None or k is None:
        return None
    out = {f: y[f] / k for f in PRICES}
    out["volume"] = y["volume"] * k
    return out


def _reproduces(y, x, tol_c: float, tol_v: float) -> bool:
    return (abs(_rel(y["close"], x["close"])) <= tol_c and x["volume"] > 0
            and abs(_rel(y["volume"], x["volume"])) <= tol_v)


def calibrate(rows: dict, date: str, prior: str) -> dict:
    import numpy as np
    cc, cv = [], []
    for r in rows.values():
        e, p = r["engine"].get(date), r["prefetch"].get(date)
        y = yahoo_normalised(r, date, prior)
        if y is None or not _identical(e, p):
            continue
        cc.append(abs(_rel(y["close"], p["close"])))
        if p["volume"]:
            cv.append(abs(_rel(y["volume"], p["volume"])))
    cc, cv = np.array(cc), np.array(cv)
    return {"controls": int(len(cc)),
            "close_absdiff": {str(q): round(float(np.percentile(cc, q)), 6)
                              for q in (50, 90, 99, 99.9, 100)},
            "volume_absdiff": {str(q): round(float(np.percentile(cv, q)), 6)
                               for q in (50, 90, 99, 99.9, 100)},
            "rule": (f"tolerance = {CAL_PERCENTILE}th percentile of the control "
                     "differences after prior-bar normalisation, fixed before any "
                     "disputed ticker is classified"),
            "tol_close": float(np.percentile(cc, CAL_PERCENTILE)),
            "tol_volume": float(np.percentile(cv, CAL_PERCENTILE))}


def verdicts(rows: dict, date: str, prior: str, tol_c: float, tol_v: float) -> dict:
    out = {}
    for t, r in rows.items():
        e, p = r["engine"].get(date), r["prefetch"].get(date)
        y = yahoo_normalised(r, date, prior)
        if p is None:
            out[t] = ("N_NO_YAHOO" if y is None
                      else "N_MATCHES" if _reproduces(y, e, tol_c, tol_v) else "N_DIFFERS")
        elif _identical(e, p):
            out[t] = "AGREE"
        elif y is None:
            out[t] = "NO_YAHOO"
        else:
            rp, re_ = _reproduces(y, p, tol_c, tol_v), _reproduces(y, e, tol_c, tol_v)
            v = ("CONFIRMED" if rp and not re_ else "REFUTED" if re_ and not rp
                 else "AMBIGUOUS" if rp and re_ else "UNRESOLVED")
            # A ONE-ROW repair keeps the series continuous only if the bars
            # before it are on the prefetch's basis. Checked PER TICKER, never
            # assumed from the population (B3139q-r69n: 1,687 of 1,688
            # prior bars agree, and the one that does not - CVNA, a 5.0x scale
            # whose repair the owner dropped - was spliced to a fake -80% day).
            if v == "CONFIRMED" and not _identical(r["engine"].get(prior),
                                                   r["prefetch"].get(prior)):
                v = "CONFIRMED_PRIOR_DIFFERS"
            out[t] = v
    return out


def prices_differ(a, b) -> bool:
    return any(abs(_rel(a[f], b[f])) > IDENTICAL_REL for f in PRICES)


def classify(raw: dict) -> dict:
    from phase_table import resolve
    date, prior, rows = raw["date"], raw["prior"], raw["rows"]
    cal = calibrate(rows, date, prior)
    tc, tv = cal["tol_close"], cal["tol_volume"]
    v = verdicts(rows, date, prior, tc, tv)
    step2 = resolve(2)
    ruled = set((ROOT / step2["tickers_file"]).read_text().split())
    counts, by_ruled = {}, {}
    for t, x in v.items():
        counts[x] = counts.get(x, 0) + 1
        k = f"{x}|{'in' if t in ruled else 'outside'}_step2_universe"
        by_ruled[k] = by_ruled.get(k, 0) + 1
    sens = {}
    for name, f in (("half_tolerance", 0.5), ("double_tolerance", 2.0)):
        alt = verdicts(rows, date, prior, tc * f, tv * f)
        sens[name] = {"changed": sorted(t for t in v if alt[t] != v[t]),
                      "confirmed": sum(1 for x in alt.values() if x == "CONFIRMED")}
    repair = []
    for t in sorted(t for t, x in v.items() if x == "CONFIRMED"):
        r = rows[t]
        e, p = r["engine"][date], r["prefetch"][date]
        y = yahoo_normalised(r, date, prior)
        repair.append({
            "ticker": t, "engine_file": r["engine_file"], "prefetch_file": r["prefetch_file"],
            "shape": "PARTIAL_SESSION" if prices_differ(e, p) else "VOLUME_ONLY",
            "in_step2_universe": t in ruled,
            "engine_before": e, "prefetch": p,
            "yahoo_normalised": {"close": y["close"], "volume": y["volume"]},
            "corporate_action_factor": round(corporate_action_factor(r, prior), 6)})
    lists = {x: sorted(t for t, y in v.items() if y == x)
             for x in sorted(set(v.values())) if x not in ("AGREE", "CONFIRMED", "N_DIFFERS")}
    unconfirmed_partial = sorted(
        t for t in lists.get("NO_YAHOO", [])
        if prices_differ(rows[t]["engine"][date], rows[t]["prefetch"][date]))
    moved = {t: round(k, 6) for t, k in
             ((t, corporate_action_factor(r, prior)) for t, r in rows.items())
             if k is not None and abs(k - 1.0) > 1e-3}
    return {
        "ticket": "S6-B3155a", "date": date, "prior": prior,
        "generator": "scripts/final_bar_third_source_check.py classify",
        "third_source": raw.get("source"), "read_at_utc": raw.get("read_at_utc"),
        "step2_universe": {"tickers_file": step2["tickers_file"], "n": len(ruled),
                           "window": step2["window"]},
        "population": {"engine_cache_ends_on_date": len(rows),
                       "yahoo_bar_present": sum(1 for r in rows.values() if _yahoo(r, date))},
        "calibration": cal,
        "corporate_action_factors": moved,
        "counts": counts, "counts_by_step2_universe": dict(sorted(by_ruled.items())),
        "repair_shapes": {s: sum(1 for r in repair if r["shape"] == s)
                          for s in ("PARTIAL_SESSION", "VOLUME_ONLY")},
        "sensitivity": sens,
        "unconfirmed_partial_bars": unconfirmed_partial,
        "no_prefetch_differs": sorted(t for t, x in v.items() if x == "N_DIFFERS"),
        "other_verdicts": lists,
        "repair": repair,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read")
    r.add_argument("--date", required=True)
    r.add_argument("--prior", required=True)
    r.add_argument("--out", required=True)
    c = sub.add_parser("classify")
    c.add_argument("--raw", required=True)
    c.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "read":
        doc = read(a.date, a.prior, Path(a.out))
        got = sum(1 for x in doc["rows"].values() if isinstance(x["yahoo"], dict)
                  and x["yahoo"].get(a.date))
        print(f"read {doc['n_tickers']} tickers, third-source bar present for {got}, "
              f"{len(doc['chunks_failed'])} chunk failure(s) -> {a.out}")
        return 0 if not doc["chunks_failed"] else 3
    raw = json.loads(Path(a.raw).read_text(encoding="utf-8"))
    doc = classify(raw)
    Path(a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("counts:", json.dumps(doc["counts"]))
    print("repair set:", len(doc["repair"]), json.dumps(doc["repair_shapes"]),
          "| tolerances close", round(doc["calibration"]["tol_close"], 6),
          "volume", round(doc["calibration"]["tol_volume"], 6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
