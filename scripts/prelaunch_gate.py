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

**HAND-RUN-ONLY (B1704).** Nothing invokes this automatically - no Stop hook, no
pre-commit, no launcher. An audit found 12 of 16 gate scripts in this state, so
presence is NOT enforcement (CHECKLIST #224). Run it explicitly and read its exit
code; if you need it to bind, wire it and say where.
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
    local_run = str(manifest.get("execution", "")).upper() == "LOCAL"
    for k in REQUIRED:
        # B1488: a LOCAL run selects its universe through the tier loader rather than an
        # explicit ticker list, so `universe` satisfies the requirement in its place. The
        # AWS sequence still needs `tickers` because its ledger enforces non-overlapping
        # per-batch splits, which only exist there.
        if local_run and k == "tickers" and manifest.get("universe"):
            continue
        if k not in manifest or manifest[k] in (None, "", []):
            fails.append(f"manifest missing/empty field: {k}")
    if fails:
        return fails  # can't meaningfully continue without the fields
    if manifest["isolation"] is not True:
        fails.append(f"isolation={manifest['isolation']} (cube sequence requires true)")
    if manifest["calendar"] != "nyse_mcal":
        fails.append(f"calendar={manifest['calendar']} != nyse_mcal (L207)")
    frozen = str(manifest["frozen_sha"])
    local = str(manifest.get("execution", "")).upper() == "LOCAL"
    if local:
        # LOCAL: no S3 artifact and no spend. Everything above this line still applies -
        # required fields, isolation, calendar - and the caller must still have answered
        # "what could make this run obsolete?" in the manifest (B1335 Rule 1).
        if not manifest.get("obsolescence_risks"):
            fails.append("LOCAL manifest missing obsolescence_risks (B1335 Rule 1)")
        if "wall_clock_projection_hours" not in manifest:
            fails.append("LOCAL manifest missing wall_clock_projection_hours "
                         "(wall clock is the scarce resource when dollars are not; L333)")
        return fails
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


def _universe_label(manifest: dict) -> str:
    """B1637: this line assumed `universe` was a DICT with a `tier` key and
    crashed on a string. `check()` only requires the field to be TRUTHY, so a
    LOCAL manifest naming a ticker file - the natural form - passed every gate
    and then died in the SUMMARY. Worse, the traceback went to stderr while the
    pipeline reported exit 0 (L486: the command returned, the work did not).
    """
    tk = manifest.get("tickers")
    if tk:
        return str(len(tk))
    u = manifest.get("universe")
    if isinstance(u, dict):
        return "universe:" + str(u.get("tier", "?"))
    return "universe:" + (str(u) if u else "?")


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
    # B1488 (S6-B1482a): LOCAL mode. This gate was built for the R5 AWS batch sequence -
    # it reads a tar SHA from S3 and budgets in USD. A LOCAL run has neither, so before this
    # the gate returned 3 unconditionally and a local launch was "blocked" by a check that
    # could never pass (L332). A manifest declaring "execution": "LOCAL" skips the S3 and
    # USD checks and keeps everything that still applies: required fields, isolation,
    # calendar, and the obsolescence enumeration.
    if str(manifest.get("execution", "")).upper() == "LOCAL":
        print("PRELAUNCH_GATE: LOCAL mode - skipping S3 tar sidecar and USD budget checks")
        tar_sha = None
    else:
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
          f"tickers={_universe_label(manifest)} "
          f"budget {manifest['spent_usd']}+{manifest['projected_batch_usd']}"
          f"<={manifest['budget_cap_usd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
