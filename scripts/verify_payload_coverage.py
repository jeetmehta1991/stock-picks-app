"""scripts/verify_payload_coverage.py (B1341, Council 368) -- pre-spend gate:
confirm the S3 data payload contains OHLCV for every ticker in a run manifest
BEFORE launching a spot instance. Stage 2 is NO-LIVE-API, so the instance can
only trade tickers whose OHLCV is inside payload.tar; a missing ticker silently
under-trades (wasted spend). Streams the tar listing from S3 (no full download
needed once all tickers are found).

Usage: python scripts/verify_payload_coverage.py --manifest <run_manifest.json>
Exit 0 = all covered; exit 3 = missing tickers (do NOT launch).
"""
from __future__ import annotations

import argparse
import json
import sys
import tarfile
from pathlib import Path

BUCKET = "stock-picks-r5-jm-2026"
PAYLOAD_KEY = "payload/r5_payload.tar"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--bucket", default=BUCKET)
    ap.add_argument("--key", default=PAYLOAD_KEY)
    args = ap.parse_args()

    tickers = set(json.loads(Path(args.manifest).read_text(encoding="utf-8"))["tickers"])
    print(f"verifying {len(tickers)} tickers against s3://{args.bucket}/{args.key}")

    import boto3
    s3 = boto3.client("s3", region_name="us-east-1")
    body = s3.get_object(Bucket=args.bucket, Key=args.key)["Body"]
    tf = tarfile.open(fileobj=body, mode="r|")  # streaming, non-seeking

    found: set[str] = set()
    ohlcv_seen = 0
    for m in tf:
        n = m.name
        if "ohlcv/" in n and n.endswith(".parquet"):
            ohlcv_seen += 1
            stem = n.split("/")[-1][:-8]
            if stem in tickers:
                found.add(stem)
                if found == tickers:
                    break
    missing = sorted(tickers - found)
    print(f"ohlcv files scanned: {ohlcv_seen}")
    print(f"FOUND ({len(found)}): {sorted(found)}")
    if missing:
        print(f"PAYLOAD_COVERAGE_FAIL: MISSING ({len(missing)}): {missing}")
        print("Do NOT launch -- rebuild payload to include these, then re-verify.")
        return 3
    print("PAYLOAD_COVERAGE_PASS: all manifest tickers have OHLCV in payload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
