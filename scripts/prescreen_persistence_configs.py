"""S6-B2485: offline pre-screen of producer-parameter configs before engine spend.

WHY THIS EXISTS. An engine run costs a MEASURED 1.68 h; regenerating the
persistence artifact for one parameter set costs a MEASURED 283 s. So the 11
producer configs can be materialised offline in ~52 minutes and screened before
committing 18.5 engine-hours.

COST CORRECTION (S6-B2490, measured mid-run off this script's own artifact
mtimes): this docstring shipped saying 104.6 s and ~19 minutes, which
UNDERSTATED the real cost by 2.7x. The 104.6 s came from a warm in-process
sample of ONE snapshot; a config is FIVE snapshots, and per-snapshot cost
grows ~9x from 2022 to 2026 as 13F coverage thickens, so the mean is neither
104.6 s nor flat. Measured across 5 completed configs: mean 283 s, median
268 s, range 177-436 s. An effort estimate is a quantitative claim and
carries a measurement's burden (L506b).

WHAT IT MEASURES, and the limit stated up front (council, unanimous): this
computes the PRODUCER OUTPUT partition - which tickers land in the primary arm,
the fallback arm, or neither - per config per snapshot. It CANNOT compute fire
counts, which need the per-bar EMA regime gate and bar alignment only the engine
does. Nothing here is a prediction of engine results.

DESIGN, adopted from the council:
  * Compare SETS, not counts (Outsider). Two configs can both land near "255
    tickers passing" while sharing almost none of them.
    S6-B2498 CORRECTION to this design note: it originally claimed two configs
    with the same set "differ in nothing the gate reads" while comparing the
    PRIMARY sets only. The gate has a SECOND arm - committed==0 AND
    institutional_increased>=5 - and the artifact carries NO
    institutional_increased column (verified: 7 columns, none is it), so the
    full pass-set is NOT computable offline. Two configs with identical
    primary sets can still differ through the fallback arm, and fallback
    rates measured 0.054..0.333 across configs, so that difference is not
    negligible. The screen therefore now compares BOTH partitions pairwise:
    a DUPLICATE verdict requires primary AND fallback Jaccard high. The
    residual blind spot - which fallback members clear increased>=5 - stays
    with the engine, and is stated in `limit`.
  * Compare ALL PAIRS, not each against baseline (Contrarian). Two configs that
    both hijack the fallback can converge on the same fallback-dominated
    population - duplicates of each other, invisible to a config-vs-baseline
    check.
  * Judge the fallback rate PER YEAR against THAT YEAR's baseline (Outsider,
    Contrarian). The baseline zero-rate is 12.4% in 2022 and 1.9% in 2026, so
    any flat threshold false-positives on one end and false-negatives on the
    other.
  * Report on the 200-ticker SWEEP universe as well as the full artifact. The
    engine sweep trades the 200, not the ~470 in the artifact, and the 200 are
    the highest-ADV names where 13F coverage is densest - a verdict over the
    full artifact need not hold over the population actually traded.

ONLY committed_growth_holders MOVES under these three parameters - measured:
persistent_holders_4q/_8q and total_active_holders were invariant (0 of 8
tickers) under a tightened variant, because they derive from separate chain
thresholds this sweep does not touch. So they are not screened here.

Usage:
  python scripts/prescreen_persistence_configs.py --emit-only   # no rebuild
  python scripts/prescreen_persistence_configs.py               # full run
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
BUILDER = REPO / "scripts" / "build_institutional_persistence_precompute.py"
SWEEP_UNIVERSE = REPO / "output_audit" / "_sweep_200.txt"
SNAPSHOTS = ["2022-01-01", "2023-01-01", "2024-01-01",
             "2025-01-01", "2026-01-01"]

PRIMARY_MIN = 3        # committed_growth_holders >= 3 (screener.py:6648)
PRODUCTION = {"INST_MIN_CONSECUTIVE_QUARTERS": "4",
              "INST_GROWTH_LOOKBACK_QUARTERS": "4",
              "INST_GROWTH_MULTIPLE": "1.10"}

# the 11 one-at-a-time configs, production held on every other axis
CONFIGS = {}
for _v in ("2", "3", "6", "8"):
    CONFIGS[f"minq{_v}"] = {**PRODUCTION, "INST_MIN_CONSECUTIVE_QUARTERS": _v}
for _v in ("2", "3", "6", "8"):
    CONFIGS[f"lookback{_v}"] = {**PRODUCTION, "INST_GROWTH_LOOKBACK_QUARTERS": _v}
for _v in ("1.0", "1.25", "1.5"):
    CONFIGS[f"mult{_v}"] = {**PRODUCTION, "INST_GROWTH_MULTIPLE": _v}


def build(tag: str, env_over: dict) -> None:
    """Materialise one config into its OWN tagged cache. Never production."""
    assert tag, "an empty tag would write to the PRODUCTION path"
    for snap in SNAPSHOTS:
        env = {**os.environ, **env_over, "INST_PERSIST_CACHE_TAG": tag}
        r = subprocess.run([sys.executable, str(BUILDER), "--as-of", snap],
                           env=env, capture_output=True, text=True,
                           cwd=str(REPO))
        if r.returncode != 0:
            raise RuntimeError(f"{tag} {snap} failed: {r.stderr[-400:]}")


def partition(tag: str, universe: set | None) -> dict:
    """(snapshot -> {primary:set, fallback:set}) for one config.

    `primary` = committed_growth_holders >= PRIMARY_MIN (the OR's first arm).
    `fallback` = committed_growth_holders == 0 (the arm that SWITCHES ON, and
    thereby stops testing committed growth at all).
    """
    sys.path.insert(0, str(REPO / "scripts"))
    from build_institutional_persistence_precompute import persistence_cache_dir
    old = os.environ.get("INST_PERSIST_CACHE_TAG")
    os.environ["INST_PERSIST_CACHE_TAG"] = tag
    try:
        d = persistence_cache_dir(REPO)
    finally:
        if old is None:
            os.environ.pop("INST_PERSIST_CACHE_TAG", None)
        else:
            os.environ["INST_PERSIST_CACHE_TAG"] = old
    out = {}
    for snap in SNAPSHOTS:
        p = d / f"{snap}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        if universe is not None:
            df = df[df["ticker"].isin(universe)]
        g = df["committed_growth_holders"]
        out[snap] = {"primary": set(df.loc[g >= PRIMARY_MIN, "ticker"]),
                     "fallback": set(df.loc[g == 0, "ticker"]),
                     "n": len(df)}
    return out


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def screen(parts: dict) -> dict:
    """Pairwise set overlap + per-year fallback rate against that year's base."""
    base = parts["production"]
    rows = {"fallback": {}, "pairs": []}
    for tag, snaps in parts.items():
        per_year = {}
        for snap, v in snaps.items():
            b = base.get(snap, {})
            bn = max(1, b.get("n", 1))
            n = max(1, v["n"])
            per_year[snap] = {
                "rate": round(len(v["fallback"]) / n, 4),
                "baseline_rate": round(len(b.get("fallback", set())) / bn, 4),
                "primary_n": len(v["primary"]),
                "baseline_primary_n": len(b.get("primary", set())),
            }
        rows["fallback"][tag] = per_year
    tags = list(parts)
    for a, b in itertools.combinations(tags, 2):
        per_year, per_year_fb = {}, {}
        for snap in SNAPSHOTS:
            pa, pb = parts[a].get(snap), parts[b].get(snap)
            if not pa or not pb:
                continue
            per_year[snap] = round(jaccard(pa["primary"], pb["primary"]), 4)
            # S6-B2498: the fallback arm is part of the gate. Two configs with
            # identical primary sets can still admit different tickers through
            # committed==0 AND increased>=5, so a duplicate verdict needs BOTH
            # partitions to agree. Which fallback members clear increased>=5
            # is engine-only knowledge (the artifact has no such column).
            per_year_fb[snap] = round(jaccard(pa["fallback"], pb["fallback"]), 4)
        if per_year:
            fbv = list(per_year_fb.values())
            rows["pairs"].append({"a": a, "b": b, "per_year": per_year,
                                  "min": min(per_year.values()),
                                  "mean": round(
                                      sum(per_year.values()) / len(per_year), 4),
                                  "per_year_fallback": per_year_fb,
                                  "min_fallback": min(fbv) if fbv else None,
                                  "mean_fallback": (round(sum(fbv) / len(fbv), 4)
                                                    if fbv else None)})
    rows["pairs"].sort(key=lambda r: -r["mean"])
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-only", action="store_true",
                    help="skip rebuilding; screen whatever tagged caches exist")
    ap.add_argument("--out", default="output_audit/b2485_prescreen.json")
    a = ap.parse_args()

    uni = set(SWEEP_UNIVERSE.read_text().split()) if SWEEP_UNIVERSE.exists() else None
    print(f"sweep universe: {len(uni) if uni else 'ABSENT'} tickers")

    if not a.emit_only:
        for i, (tag, env) in enumerate(CONFIGS.items(), 1):
            print(f"[{i}/{len(CONFIGS)}] building {tag} ...", flush=True)
            build(tag, env)

    parts_full, parts_uni = {}, {}
    parts_full["production"] = partition("", None)
    parts_uni["production"] = partition("", uni)
    for tag in CONFIGS:
        pf = partition(tag, None)
        if pf:
            parts_full[tag] = pf
            parts_uni[tag] = partition(tag, uni)

    doc = {"ticket": "S6-B2485",
           "limit": ("PRODUCER OUTPUT partition only. Fire counts need the "
                     "per-bar EMA gate and bar alignment the engine does; "
                     "nothing here predicts engine results."),
           "primary_min": PRIMARY_MIN,
           "configs_screened": sorted(set(parts_full) - {"production"}),
           "full_artifact": screen(parts_full),
           "sweep_universe": screen(parts_uni) if uni else None}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"wrote {a.out}  ({len(doc['configs_screened'])} configs screened)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
