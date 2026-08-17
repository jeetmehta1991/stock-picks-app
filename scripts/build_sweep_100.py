"""B1571 -- build the FIXED 100-ticker search universe (owner ruling 2026-08-14).

CRITERION: top 100 of the 544 R5 universe by average dollar volume, measured
over the WARMUP window 2021-05-06 -> 2022-05-05, which precedes the locked
backtest window so selection carries no lookahead into the measured period.

B1618 (owner ruled 544, 2026-08-17): this builder READ `r5_universe_381.txt` -
the ABANDONED A-C chunk (100pct A-C, zero mega-caps, 248 tickers the real R5
never ran). The live `_sweep_100.txt` was correct, because it had been rebuilt
from 544 by hand; the BUILDER was never repointed. Re-running it would have
silently replaced the correct universe with one sharing only **31 of 100**
tickers - and the runbook said "Rebuild ONLY if the 381-universe changes",
instructing exactly that. CHECKLIST #199: a correction downstream of a
generator is temporary. MEASURED both ways:

    source r5_universe_381.txt : eligible 340, excluded 41, overlap  31/100
    source r5_universe_544.txt : eligible 522, excluded 22, overlap 100/100
                                 and reproduces the live file EXACTLY, order included.

ONE list, shared by EVERY strategy. The previous per-strategy builder ranked by
that strategy's own R5 fire count, which is in-sample selection: it inflates
apparent edge, by a different amount per strategy, corrupting cross-strategy
comparison as well.

KNOWN BIAS: requiring 100 warmup bars structurally excludes every ticker that
listed after 2021-05-06 -- MEASURED at **22 of 544** (the long-standing "41 of
381" was the abandoned chunk's figure, wrong in BOTH halves). Those 22 remain in
the 544 used for Phase-2 validation, so nothing is ADMITTED on the biased
universe -- but rankings are derived from one. Documented in
STRATEGY_OPTIMISATION_PLAN.md STEP 1.1.
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
           (REPO / "output_audit" / "r5_universe_544.txt").read_text().split()
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
