"""scripts/prelaunch_gate.py (B1337, Council 365, owner-approved) -- the
CHECKLIST #160/#161 executable: refuses a batch launch until measurement
semantics are frozen and artifact provenance is verified, LOCALLY, before any
instance spend.

Checks (all must pass; exit 0 PASS / exit 3 FAIL with reasons):
  1. run_manifest.json complete: sequence, batch, frozen_sha, isolation=true,
     calendar=nyse_mcal, tickers, budget_cap_usd, spent_usd, projected_batch_usd
  2. S3 tar provenance: payload/r5_code.tar.sha sidecar == frozen_sha
     (the stale-07-17-tar class, caught pre-spend instead of on-instance)
  3. Ticker disjointness vs every prior batch in the ledger
  4. All prior ledger batches have outputs committed (committed: true)
  5. Budget: spent + projected <= cap

Usage:
  python scripts/prelaunch_gate.py --manifest run_manifest.json \
      [--ledger output_batches/batch_ledger.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BUCKET = "stock-picks-r5-jm-2026"
SIDECAR_KEY = "payload/r5_code.tar.sha"
REQUIRED = ("sequence", "batch", "frozen_sha", "isolation", "calendar",
            "tickers", "budget_cap_usd", "spent_usd", "projected_batch_usd")


def s3_tar_sha() -> str:
    """Read the tar's .sha sidecar from S3 (tiny; 1 API call). Tests
    monkeypatch this."""
    import boto3
    obj = boto3.client("s3", region_name="us-east-1").get_object(
        Bucket=BUCKET, Key=SIDECAR_KEY)
    return obj["Body"].read().decode().strip()


def check(manifest: dict, ledger: dict, tar_sha: str) -> list[str]:
    fails = []
    for k in REQUIRED:
        if k not in manifest or manifest[k] in (None, "", []):
            fails.append(f"manifest missing/empty field: {k}")
    if fails:
        return fails  # can't meaningfully continue without the fields
    if manifest["isolation"] is not True:
        fails.append(f"isolation={manifest['isolation']} (cube sequence requires true)")
    if manifest["calendar"] != "nyse_mcal":
        fails.append(f"calendar={manifest['calendar']} != nyse_mcal (L207)")
    frozen = str(manifest["frozen_sha"])
    if not tar_sha:
        fails.append("S3 tar .sha sidecar missing/unreadable -- rebuild+upload "
                     "via build_r5_code_tar --sha <frozen> --upload (#161)")
    elif not (tar_sha.startswith(frozen) or frozen.startswith(tar_sha[:12])):
        fails.append(f"S3 tar sha={tar_sha[:12]} != manifest frozen_sha="
                     f"{frozen[:12]} (STALE ARTIFACT -- the chunk-2 class)")
    mine = set(manifest["tickers"])
    for b in ledger.get("batches", []):
        overlap = mine & set(b.get("tickers", []))
        if overlap:
            fails.append(f"tickers overlap batch {b.get('batch')}: "
                         f"{sorted(overlap)[:5]} (append plan requires disjoint)")
        if not b.get("committed", False):
            fails.append(f"prior batch {b.get('batch')} outputs NOT committed "
                         "(CSV-first + C10)")
    projected = float(manifest["spent_usd"]) + float(manifest["projected_batch_usd"])
    if projected > float(manifest["budget_cap_usd"]):
        fails.append(f"budget breach: spent {manifest['spent_usd']} + projected "
                     f"{manifest['projected_batch_usd']} > cap {manifest['budget_cap_usd']}")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--ledger", default="output_batches/batch_ledger.json")
    args = ap.parse_args()
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"PRELAUNCH_GATE_FAIL: manifest unreadable: {exc}")
        return 3
    ledger = {"batches": []}
    lp = Path(args.ledger)
    if lp.exists():
        try:
            ledger = json.loads(lp.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"PRELAUNCH_GATE_FAIL: ledger unreadable: {exc}")
            return 3
    try:
        tar_sha = s3_tar_sha()
    except Exception as exc:
        print(f"PRELAUNCH_GATE_FAIL: cannot read S3 tar sidecar: {exc}")
        return 3
    fails = check(manifest, ledger, tar_sha)
    if fails:
        print("PRELAUNCH_GATE_FAIL (#160/#161):")
        for f in fails:
            print(f"  - {f}")
        return 3
    print(f"PRELAUNCH_GATE_PASS batch={manifest['batch']} "
          f"frozen_sha={str(manifest['frozen_sha'])[:12]} "
          f"tickers={len(manifest['tickers'])} "
          f"budget {manifest['spent_usd']}+{manifest['projected_batch_usd']}"
          f"<={manifest['budget_cap_usd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
