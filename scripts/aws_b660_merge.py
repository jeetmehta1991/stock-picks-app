"""B695 (2026-06-11): merge per-shard B660 outputs from S3 into one
fire_count_measured_b660_post_b689_extended.json. Mirrors the per-strategy
aggregation pattern that the single-instance harness produces, summing
fires across all shards (the universe is a disjoint partition).

Reads `s3://<bucket>/b660_outputs/shard_<N>.json` for N=1..shards (or
auto-detect via shard_<N>_COMPLETE sentinels) and emits the merged JSON
to a local path matching the single-instance harness output schema.

Usage:
    python scripts/aws_b660_merge.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --output output_audit/fire_count_measured_b660_post_b689_extended.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def list_shard_outputs(bucket: str, prefix: str) -> list[int]:
    """Return list of shard indices with completion sentinels present."""
    r = subprocess.run(
        ["aws", "s3", "ls", f"s3://{bucket}/{prefix}/", "--recursive"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise SystemExit(f"[FATAL] s3 ls failed: {r.stderr}")
    completes = []
    for line in r.stdout.splitlines():
        # Format: "DATE SIZE prefix/shard_N_COMPLETE"
        parts = line.split()
        if not parts:
            continue
        key = parts[-1]
        if key.endswith("_COMPLETE"):
            # extract shard index
            name = key.split("/")[-1]
            try:
                idx = int(name.replace("shard_", "").replace("_COMPLETE", ""))
                completes.append(idx)
            except ValueError:
                pass
    return sorted(completes)


def download_shard_json(bucket: str, prefix: str, shard: int, local_dir: Path) -> Path:
    local_path = local_dir / f"shard_{shard}.json"
    cmd = ["aws", "s3", "cp",
           f"s3://{bucket}/{prefix}/shard_{shard}.json",
           str(local_path), "--no-progress"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise SystemExit(f"[FATAL] s3 cp shard_{shard} failed: {r.stderr}")
    return local_path


def merge_results(shard_jsons: list[dict]) -> dict:
    """Merge per-shard fire counts. The universe is partitioned across
    shards (disjoint), so per-strategy fire counts sum cleanly. Gate
    marginals are weighted by per-shard n_tickers_sampled and re-averaged.

    The merged output mirrors the single-instance harness schema so
    downstream consumers (banner script, cluster-diff report, etc.) need
    no changes.
    """
    if not shard_jsons:
        raise SystemExit("[FATAL] no shard JSONs to merge")

    # Metadata: take from shard 1 + sum tickers
    meta_fields = [
        "as_of", "universe", "ticker_sample_strategy", "ticker_sample_seed",
        "date_range",
    ]
    merged = {f: shard_jsons[0].get(f) for f in meta_fields}
    merged["n_tickers_full_t1a_pit_active"] = shard_jsons[0].get("n_tickers_full_t1a_pit_active")
    merged["n_tickers_sampled"] = sum(s.get("n_tickers_sampled", 0) for s in shard_jsons)
    merged["n_cache_misses"] = sum(s.get("n_cache_misses", 0) for s in shard_jsons)
    merged["n_bars_total"] = sum(s.get("n_bars_total", 0) for s in shard_jsons)
    merged["projection_scale_factor"] = round(
        merged["n_tickers_full_t1a_pit_active"] / max(merged["n_tickers_sampled"], 1), 2
    )
    merged["non_representativeness_caveat"] = shard_jsons[0].get("non_representativeness_caveat", "")
    merged["merged_from_n_shards"] = len(shard_jsons)

    # Per-strategy aggregation. Each shard has its own results[] list of
    # strategy dicts; sum the fire counts, weighted-average the marginals.
    per_strategy: dict[str, dict] = defaultdict(lambda: {
        "n_fires_long": 0, "n_fires_short": 0, "n_fires_avoid": 0,
        "n_bars_evaluated": 0, "n_tickers_sampled": 0,
        "gate_marginals_acc": defaultdict(lambda: [0, 0]),  # [sum_p_times_n, sum_n]
        "first_fire_date": None, "last_fire_date": None,
    })

    for shard in shard_jsons:
        for r in shard.get("results", []):
            name = r["strategy"]
            agg = per_strategy[name]
            agg["n_fires_long"] += r.get("n_fires_long", 0)
            agg["n_fires_short"] += r.get("n_fires_short", 0)
            agg["n_fires_avoid"] += r.get("n_fires_avoid", 0)
            agg["n_bars_evaluated"] += r.get("n_bars_evaluated", 0)
            agg["n_tickers_sampled"] += r.get("n_tickers_sampled", 0)
            # Gate marginals - weighted by shard n_bars
            n_bars = r.get("n_bars_evaluated", 0)
            for k, v in r.get("gate_marginals", {}).items():
                agg["gate_marginals_acc"][k][0] += v * n_bars
                agg["gate_marginals_acc"][k][1] += n_bars
            # first/last fire date - keep extremes
            for fd_key, op in (("first_fire_date", min), ("last_fire_date", max)):
                shard_fd = r.get(fd_key)
                if shard_fd is None:
                    continue
                cur = agg[fd_key]
                agg[fd_key] = shard_fd if cur is None else op(cur, shard_fd)

    # Build the merged results[] list with the same schema as single-instance.
    # Compute calendar_year_span from date_range to match the to_dict()
    # calculation in StrategyResult.
    from datetime import date
    dr = merged["date_range"]
    cal_yrs = max((date.fromisoformat(dr["end"]) - date.fromisoformat(dr["start"])).days / 365.25, 1e-9)

    n_full_t1a = merged["n_tickers_full_t1a_pit_active"]
    results_out = []
    for name in sorted(per_strategy.keys()):
        agg = per_strategy[name]
        # Re-average marginals
        gate_marginals = {}
        for k, (psum, nsum) in agg["gate_marginals_acc"].items():
            if nsum > 0:
                gate_marginals[k] = round(psum / nsum, 4)
        # Recompute the fires/yr + verdicts to match single-instance schema
        total_fires = agg["n_fires_long"] + agg["n_fires_short"]
        n_samp = max(agg["n_tickers_sampled"], 1)
        scale = n_full_t1a / n_samp
        fires_long_per_yr = agg["n_fires_long"] / cal_yrs
        fires_short_per_yr = agg["n_fires_short"] / cal_yrs
        proj_long = fires_long_per_yr * scale
        proj_short = fires_short_per_yr * scale
        proj_total = proj_long + proj_short
        # Verdict thresholds match single-instance
        if proj_total < 30:
            proj_verdict = "FAIL_FIRE_STARVED"
        elif proj_total < 60:
            proj_verdict = "BORDERLINE"
        else:
            proj_verdict = "PASS_CUBE"
        if (fires_long_per_yr + fires_short_per_yr) < 30:
            verdict = "FAIL_FIRE_STARVED"
        elif (fires_long_per_yr + fires_short_per_yr) < 60:
            verdict = "BORDERLINE"
        else:
            verdict = "PASS_CUBE"
        results_out.append({
            "strategy": name,
            "n_fires_long": agg["n_fires_long"],
            "n_fires_short": agg["n_fires_short"],
            "n_fires_avoid": agg["n_fires_avoid"],
            "n_bars_evaluated": agg["n_bars_evaluated"],
            "n_tickers_sampled": agg["n_tickers_sampled"],
            "calendar_year_span": round(cal_yrs, 2),
            "measured_fires_per_calendar_year_long_sampled": round(fires_long_per_yr, 2),
            "measured_fires_per_calendar_year_short_sampled": round(fires_short_per_yr, 2),
            "measured_fires_per_calendar_year_total_sampled": round(fires_long_per_yr + fires_short_per_yr, 2),
            "projected_fires_per_calendar_year_long_full_t1a": round(proj_long, 1),
            "projected_fires_per_calendar_year_short_full_t1a": round(proj_short, 1),
            "projected_fires_per_calendar_year_total_full_t1a": round(proj_total, 1),
            "projected_verdict_full_t1a": proj_verdict,
            "projection_scale_factor": round(scale, 2),
            "n_tickers_full_t1a_used_for_projection": n_full_t1a,
            "first_fire_date": agg["first_fire_date"],
            "last_fire_date": agg["last_fire_date"],
            "verdict": verdict,
            "gate_marginals": gate_marginals,
            "notes": f"B695 merged from {len(shard_jsons)} shards",
        })

    merged["results"] = results_out
    return merged


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--output-key-prefix", default="b660_outputs",
                    help="S3 prefix for shard outputs")
    ap.add_argument("--output", default="output_audit/fire_count_measured_b660_post_b689_extended.json",
                    help="local merged JSON output")
    ap.add_argument("--expected-shards", type=int, default=5,
                    help="expected shard count; warn if fewer found")
    ap.add_argument("--workdir", default=None,
                    help="local download dir for shard JSONs (default tmp)")
    args = ap.parse_args()

    completes = list_shard_outputs(args.bucket, args.output_key_prefix)
    print(f"[INFO] found {len(completes)} complete shards: {completes}")
    if len(completes) < args.expected_shards:
        missing = set(range(1, args.expected_shards + 1)) - set(completes)
        print(f"[WARN] expected {args.expected_shards} shards; missing: {sorted(missing)}")
        print(f"[WARN] proceeding with partial merge ({len(completes)} / {args.expected_shards})")

    workdir = Path(args.workdir) if args.workdir else REPO / "output_audit" / "_b660_shard_downloads"
    workdir.mkdir(parents=True, exist_ok=True)

    shard_jsons = []
    for idx in completes:
        local = download_shard_json(args.bucket, args.output_key_prefix, idx, workdir)
        shard_jsons.append(json.loads(local.read_text()))
        print(f"[OK] loaded shard_{idx}.json ({len(shard_jsons[-1].get('results', []))} strategies)")

    merged = merge_results(shard_jsons)
    out_path = REPO / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, indent=2))
    print(f"\n[OK] merged JSON written to {out_path}")
    print(f"  {len(merged['results'])} strategies across {merged['merged_from_n_shards']} shards")
    print(f"  {merged['n_tickers_sampled']} total tickers in merged universe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
