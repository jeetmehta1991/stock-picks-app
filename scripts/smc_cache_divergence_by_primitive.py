"""Per-PRIMITIVE divergence of the SMC panel cache - S6-B1541a.

The existing B554/B560 suites PIN an aggregate tolerance (`assert rate < 0.05`)
and say so explicitly: "it does NOT assert exact parity". So 22 green tests mean
the divergence is STABLE, not that the cache is safe. This script answers the
question those tests do not: **WHICH primitives diverge, and by how much.**

Why it matters: the cache's documented defect is confined to ONE primitive -
`ob()` has forward-mutating state, so an order block precomputed on the full
series carries information from bars AFTER the as_of date. That is lookahead,
and `smc_breaker_block_bullish` is defined off OB mitigation state, i.e. the
contamination lands inside the strategy under optimisation.

If FVG and the other families are clean, the cache can be enabled for them and
left off for OB - partial speedup, zero contamination. If OB dominates the cost,
the safely-recoverable share is far below the headline 27.2pct, and that is the
honest finding.

GROUND TRUTH is the per-call path on a TRUNCATED frame (`ohlc.iloc[:i+1]`),
which is what production runs and what cannot see the future by construction.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]

# Signal-name prefix -> primitive family. Derived from smc_ict.py's emission
# blocks; anything unmatched is reported under "other" rather than silently
# folded into a family (a wrong family assignment would hide the OB result).
FAMILY = [
    ("smc_fvg", "fvg"),
    ("smc_ob", "ob"),
    ("smc_breaker", "ob"),
    ("smc_mitigation", "ob"),
    ("smc_bos", "bos_choch"),
    ("smc_choch", "bos_choch"),
    ("smc_liquidity", "liquidity"),
    ("smc_equal", "liquidity"),
    ("smc_ote", "retracements"),
    ("smc_discount", "retracements"),
    ("smc_premium", "retracements"),
    ("smc_dealing", "retracements"),
]


def family_of(key: str) -> str:
    for pref, fam in FAMILY:
        if key.startswith(pref):
            return fam
    return "other"


def load(ticker: str):
    for rel in (f"backtest/data/cache/ohlcv/{ticker}.parquet",
                f"data/cache/ohlcv/{ticker}.parquet"):
        p = REPO / rel
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
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", default="", help="comma list; default from R5 universe")
    ap.add_argument("--n-tickers", type=int, default=25)   # CHECKLIST #154 floor
    ap.add_argument("--n-dates", type=int, default=8)      # >=4, spanning >=12 months
    ap.add_argument("--out", default="output_audit/b1542_cache_divergence.json")
    a = ap.parse_args()

    import backtest.config as cfg
    from backtest.signals import smc_ict
    from backtest.signals import smc_panel_cache as pc

    if a.tickers:
        tickers = [t.strip() for t in a.tickers.split(",") if t.strip()]
    else:
        uni = (REPO / "output_audit" / "r5_universe_381.txt").read_text().split()
        tickers = uni[:a.n_tickers]

    per_family = defaultdict(lambda: {"checked": 0, "diverged": 0})
    per_key = defaultdict(lambda: {"checked": 0, "diverged": 0})
    samples = 0
    used = []

    for t in tickers:
        df = load(t)
        if df is None or len(df) < 400:
            continue
        used.append(t)
        # dates spread across the back 2/3 of the series so warmup is covered
        lo, hi = int(len(df) * 0.35), len(df) - 1
        idxs = [lo + (hi - lo) * k // max(a.n_dates - 1, 1) for k in range(a.n_dates)]

        # GROUND TRUTH: per-call on truncated frames, cache OFF
        cfg.USE_SMC_PANEL_CACHE = False
        truth = {i: smc_ict.compute_smc_signals(df.iloc[:i + 1]) for i in idxs}

        # CACHED: prime from the FULL series, then read at each as_of
        cfg.USE_SMC_PANEL_CACHE = True
        try:
            # B1542: the module docstring names `prime_all_tickers(ohlcv_dict)`,
            # which DOES NOT EXIST. The real API is per-ticker
            # `prime_ticker_primitives(ticker, full_ohlc, swing_length=20)` -
            # the same call the engine makes at backtest.py:736.
            pc.reset_cache()
            pc.prime_ticker_primitives(t, df, swing_length=20)
            if not pc.is_primed(t):
                raise RuntimeError("prime_ticker_primitives left cache unprimed")
        except Exception as e:  # priming must never be silent (CHECKLIST #122)
            print(f"  {t}: PRIME FAILED {e!r} - skipping ticker")
            cfg.USE_SMC_PANEL_CACHE = False
            continue
        cached = {i: smc_ict.compute_smc_signals(df.iloc[:i + 1], ticker=t) for i in idxs}
        cfg.USE_SMC_PANEL_CACHE = False

        for i in idxs:
            samples += 1
            a_, b_ = truth[i], cached[i]
            for k in set(a_) | set(b_):
                fam = family_of(k)
                per_family[fam]["checked"] += 1
                per_key[k]["checked"] += 1
                va, vb = a_.get(k), b_.get(k)
                same = (va == vb) if not (
                    isinstance(va, float) and isinstance(vb, float)) else (
                    abs(va - vb) < 1e-9 or (va != va and vb != vb))
                if not same:
                    per_family[fam]["diverged"] += 1
                    per_key[k]["diverged"] += 1
        print(f"  {t}: {len(idxs)} as_of points compared")

    print(f"\ntickers used: {len(used)} | (ticker, as_of) samples: {samples}")
    print(f"\n{'family':<16}{'checked':>10}{'diverged':>10}{'rate':>9}")
    rows = {}
    for fam, d in sorted(per_family.items(), key=lambda x: -x[1]["diverged"]):
        rate = d["diverged"] / max(d["checked"], 1)
        rows[fam] = {**d, "rate": round(rate, 4)}
        print(f"{fam:<16}{d['checked']:>10}{d['diverged']:>10}{rate:>8.2%}")

    worst = sorted(per_key.items(), key=lambda x: -x[1]["diverged"])[:10]
    print(f"\nworst individual signals:")
    for k, d in worst:
        if d["diverged"]:
            print(f"  {k:<44}{d['diverged']:>5}/{d['checked']:<5}"
                  f"{d['diverged']/max(d['checked'],1):>8.2%}  [{family_of(k)}]")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({
        "tickers_used": used, "samples": samples,
        "per_family": rows,
        "per_key": {k: v for k, v in per_key.items() if v["diverged"]},
    }, indent=2))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
