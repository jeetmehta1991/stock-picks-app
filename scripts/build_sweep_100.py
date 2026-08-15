"""B1571 -- build the FIXED 100-ticker search universe (owner ruling 2026-08-14).

CRITERION: top 100 of the 381 R5 universe by average dollar volume, measured
over the WARMUP window 2021-05-06 -> 2022-05-05, which precedes the locked
backtest window so selection carries no lookahead into the measured period.

ONE list, shared by EVERY strategy. The previous per-strategy builder ranked by
that strategy's own R5 fire count, which is in-sample selection: it inflates
apparent edge, by a different amount per strategy, corrupting cross-strategy
comparison as well.

KNOWN BIAS: requiring 100 warmup bars structurally excludes every ticker that
listed after 2021-05-06 (41 of 381). Those remain in the 381 used for Phase-2
validation, so nothing is ADMITTED on the biased universe -- but rankings are
derived from one. Documented in STRATEGY_OPTIMISATION_PLAN.md STEP 1.1.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

WARMUP_LO, WARMUP_HI = date(2021, 5, 6), date(2022, 5, 5)
MIN_WARMUP_BARS = 100


def main() -> int:
    from backtest.data.cache import _cache_path

    uni = [t.strip() for t in
           (REPO / "output_audit" / "r5_universe_381.txt").read_text().split()
           if t.strip()]
    rows, skipped = [], []
    for t in uni:
        p = _cache_path(t)
        if not p.exists():
            skipped.append((t, "no parquet"))
            continue
        d = pd.read_parquet(p)
        if "date" not in d.columns:
            skipped.append((t, "no date column"))
            continue
        d["date"] = pd.to_datetime(d["date"])
        d = d.set_index("date")
        w = d[(d.index.date >= WARMUP_LO) & (d.index.date <= WARMUP_HI)]
        if len(w) < MIN_WARMUP_BARS:
            skipped.append((t, f"only {len(w)} warmup bars"))
            continue
        rows.append((t, float((w["close"] * w["volume"]).mean())))

    rows.sort(key=lambda r: -r[1])
    top = [t for t, _ in rows[:100]]
    out = REPO / "output_audit" / "_sweep_100.txt"
    out.write_text("\n".join(top) + "\n")

    print(f"universe {len(uni)} | eligible {len(rows)} | excluded {len(skipped)}")
    print(f"excluded sample: {[t for t, _ in skipped[:8]]}")
    print(f"top 5: {[(t, round(a / 1e6)) for t, a in rows[:5]]}  (ADV $M)")
    print(f"wrote {out} ({len(top)} tickers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
