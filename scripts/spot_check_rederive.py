"""S6-B3427 (B3139q-r212c): the certification checker leg for families whose
spot check re-derives no input family (spot_check_replay's four).

Re-derives each GATE KEY the spot check sampled, from its SOURCE, and compares
with the trade log's signals_at_entry - the method the news_momentum_long hand
disposition proved (output_audit/b3139q_lv4s2_news_momentum_long_step4_hand_disposition.json:
300 of 300 agree; previous-bar control 24-31 of 50 agree, so the formulas can
disagree and the agreement is informative).

KEYED BY SIGNAL KEY, never by strategy (#291): KEY_DERIVERS maps a persisted
key to a derivation over the cached bars; news keys route through the producer
on the raw article files. A sampled key with NO route is UNCOVERED - exit 2
with the residue NAMED, and the battery keeps step 4 OPEN for a hand
disposition of exactly those keys. The previous-bar control must DISAGREE on
every derived price key (a derivation that agrees on every bar proves nothing
- L686: mutate toward the useless version).

Writes --out only (no production path; S6-B3418's confinement rule applies
from birth).
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _bars(cache: dict, t: str) -> pd.DataFrame:
    if t not in cache:
        p = ROOT / "backtest" / "data" / "cache" / "ohlcv" / (
            t.replace("-", "_").replace(".", "_") + ".parquet")
        df = pd.read_parquet(p)
        df.columns = [str(c).lower() for c in df.columns]
        if "date" in df.columns:
            df = df.set_index("date")
        df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
        cache[t] = df.sort_index()
    return cache[t]


def _ohlcv_asof(df: pd.DataFrame, d: str):
    sub = df[df.index <= pd.Timestamp(d)]
    if sub.empty or sub.index[-1] != pd.Timestamp(d):
        return None
    return sub


# ---- the key registry: key -> f(window_df) -> value --------------------------
# window_df's LAST row is the as-of bar; derivations read ONLY that frame.
def _d_close_above_open(w):
    t = w.iloc[-1]
    return float(t["close"]) > float(t["open"])


def _d_close_in_top_40(w):
    t = w.iloc[-1]
    rng = float(t["high"]) - float(t["low"])
    return ((float(t["high"]) - float(t["close"])) / rng) <= 0.40 if rng > 0 else False


def _d_dc20_up(w):
    t = w.iloc[-1]
    upper_prior = float(w.iloc[:-1]["high"].tail(20).max())
    return float(t["close"]) >= upper_prior * 0.998


def _d_vol_above_avg(w):
    avg20 = float(w["volume"].rolling(20).mean().iloc[-1])
    return (float(w.iloc[-1]["volume"]) / avg20 >= 1.0) if avg20 > 0 else False


KEY_DERIVERS = {
    "close_above_open": _d_close_above_open,
    "close_in_top_40pct_of_range": _d_close_in_top_40,
    "dc20_breakout_up": _d_dc20_up,
    "vol_above_avg": _d_vol_above_avg,
}

# keys served by a PRODUCER call rather than bar arithmetic: key -> producer
NEWS_KEYS = ("news_sentiment_5d", "news_volume_zscore_5d")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", required=True)
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--spot", required=True, help="the spot check's json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cube_dir = Path(a.cube) if Path(a.cube).is_absolute() else ROOT / a.cube
    spot = json.loads(Path(a.spot).read_text(encoding="utf-8"))
    tl = pd.read_csv(cube_dir / "trade_log.csv", low_memory=False,
                     usecols=["ticker", "entry_date", "strategy", "signals_at_entry"])
    tl = tl[tl["strategy"] == a.strategy]
    rows_in = spot.get("rows") or []
    if not rows_in:
        print("[FAIL] the spot check json carries no rows - nothing to re-derive")
        return 2

    # the sampled-key population is the spot check's own gate_keys_by_side -
    # the GATE keys it verified, never the whole persisted signal dict (the
    # first draft fell back to sig.keys() and demanded a route for ~400
    # keys; the artifact names its population, so read it - L823)
    gk = spot.get("gate_keys_by_side") or {}
    sampled = {k for side in gk.values() for k in side}
    if not sampled:
        print("[FAIL] the spot check json names no gate_keys_by_side - the "
              "sampled-key population is unreadable (fail closed, L642)")
        return 2
    bars_cache: dict = {}
    agree, checked = {}, {}
    problems, out_rows = [], []
    prev_agree, prev_checked = {}, {}
    uncovered = set()
    from backtest.signals.news_sentiment import compute_news_sentiment_signals

    for r in rows_in:
        t, d = r["ticker"], r["entry_date"]
        m = tl[(tl["ticker"] == t) & (tl["entry_date"] == d)]
        if m.empty:
            problems.append(f"{t} {d}: not in the trade log")
            continue
        sig = json.loads(m.iloc[0]["signals_at_entry"])
        keys = sorted(sampled)
        try:
            w = _ohlcv_asof(_bars(bars_cache, t), d)
        except (OSError, ValueError, KeyError) as exc:
            problems.append(f"{t} {d}: bars unreadable ({exc!r})")
            w = None
        nk = None
        row = {"ticker": t, "entry_date": d, "keys": {}}
        for k in keys:
            pv = sig.get(k)
            dv = None
            if k in KEY_DERIVERS:
                if w is None:
                    problems.append(f"{t} {d} {k}: no bar window")
                    continue
                dv = KEY_DERIVERS[k](w)
                # previous-bar control
                if len(w) > 1:
                    pdv = KEY_DERIVERS[k](w.iloc[:-1])
                    prev_checked[k] = prev_checked.get(k, 0) + 1
                    prev_agree[k] = prev_agree.get(k, 0) + int(bool(pdv) == bool(pv))
            elif k in NEWS_KEYS:
                if nk is None:
                    nk = compute_news_sentiment_signals(t, date.fromisoformat(d))
                dv = nk.get(k)
            else:
                uncovered.add(k)
                continue
            if dv is None:
                problems.append(f"{t} {d} {k}: producer returned none")
                continue
            checked[k] = checked.get(k, 0) + 1
            if isinstance(dv, bool) or isinstance(pv, bool):
                ok = bool(pv) == bool(dv)
            else:
                ok = pv is not None and abs(float(pv) - float(dv)) <= 1e-4
            agree[k] = agree.get(k, 0) + int(ok)
            row["keys"][k] = {"persisted": pv, "rederived": dv, "agree": ok}
            if not ok:
                problems.append(f"{t} {d} {k}: persisted {pv!r}, re-derived {dv!r}")
        out_rows.append(row)

    vacuous = sorted(k for k in prev_checked
                     if prev_agree.get(k, 0) == prev_checked[k])
    disagreements = [p for p in problems if "persisted" in p]
    doc = {"cube": cube_dir.name, "strategy": a.strategy,
           "sampled_rows": len(rows_in), "trades_checked": len(out_rows),
           "agree": agree, "checked": checked,
           "uncovered_keys": sorted(uncovered),
           "previous_bar_agreement": prev_agree,
           "previous_bar_checked": prev_checked,
           "vacuous_controls": vacuous,
           "problems": problems, "rows": out_rows, "method": __doc__}
    outp = Path(a.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")
    if uncovered:
        print(f"[FAIL] UNCOVERED keys (no derivation route): {sorted(uncovered)} "
              f"- step 4 stays OPEN for a hand disposition of exactly these")
        return 2
    if vacuous:
        print(f"[FAIL] vacuous control: previous-bar derivation agreed on every "
              f"row for {vacuous} - the derivation cannot disagree, so its "
              f"agreement proves nothing (L686)")
        return 2
    bad = [k for k in checked if agree.get(k, 0) != checked[k]]
    if bad or disagreements:
        print(f"[FAIL] re-derivation DISAGREES on {bad}; first: "
              f"{disagreements[:3]}")
        return 1
    if not checked:
        print("[FAIL] nothing checked - no sampled key had a route and a row")
        return 2
    print("[PASS] re-derived " + "; ".join(
        f"{k} {agree[k]}/{checked[k]}" for k in sorted(checked))
        + f"; previous-bar control disagrees on "
          f"{sum(prev_checked[k]-prev_agree.get(k,0) for k in prev_checked)} "
          f"row-keys across {len(prev_checked)} keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
