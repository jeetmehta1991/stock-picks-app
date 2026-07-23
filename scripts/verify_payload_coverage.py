"""scripts/verify_payload_coverage.py (B1341/B1344, Council 368/370) -- pre-spend
gate: confirm the S3 data payload can SERVE OHLCV for every ticker in a run
manifest BEFORE launching a spot instance. Stage 2 is NO-LIVE-API, so the
instance can only trade tickers the cache serves; a missing ticker silently
under-trades (wasted spend).

B1344 FIX (batch-2 lesson): the engine keys OHLCV off the cache INDEX
(backtest/data/cache/index.json), NOT raw file existence. BRK-B's parquet WAS
in the payload yet it got a cache MISS -> yfinance hard-cut -> 0 trades, because
BRK-B was not registered in the payload's index. So this gate now checks INDEX
registration (the thing the engine actually consults), not just file presence.
Both are verified; index is authoritative.

Usage: python scripts/verify_payload_coverage.py --manifest <run_manifest.json>
Exit 0 = all serveable; exit 3 = missing (do NOT launch).
"""
from __future__ import annotations

import argparse
import json
import sys
import tarfile
from pathlib import Path

BUCKET = "stock-picks-r5-jm-2026"
PAYLOAD_KEY = "payload/r5_payload.tar"


def check_local_cache_serveable(tickers) -> list:
    """B1349 FIX (batch-3 BRK-B/BF-B bug): the engine seeks OHLCV at the
    _cache_path ENCODED name (cache.py:57 maps -/. -> _), so BRK-B -> BRK_B.parquet.
    A file present under the raw name (BRK-B.parquet) is NEVER served. Since
    launches now ship the local cache as a refresh overlay, verify each roster
    ticker's _cache_path-encoded file exists in the LOCAL cache (authoritative
    for what the overlay serves). Returns list of un-serveable tickers."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from backtest.data.cache import _cache_path
    return sorted(t for t in tickers if not _cache_path(t).exists())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--bucket", default=BUCKET)
    ap.add_argument("--key", default=PAYLOAD_KEY)
    ap.add_argument("--local-cache", action="store_true",
                    help="B1349: check the LOCAL cache via _cache_path encoded "
                         "names (what the cache-refresh overlay ships) instead of "
                         "streaming the S3 payload -- instant + catches the "
                         "filename-encoding class (BRK-B seek BRK_B.parquet).")
    args = ap.parse_args()

    tickers = set(json.loads(Path(args.manifest).read_text(encoding="utf-8"))["tickers"])

    if args.local_cache:
        bad = check_local_cache_serveable(tickers)
        print(f"local-cache _cache_path check: {len(tickers)-len(bad)}/{len(tickers)} serveable")
        if bad:
            print(f"PAYLOAD_COVERAGE_FAIL: NOT SERVEABLE via _cache_path ({len(bad)}): {bad}")
            print("  (create the _cache_path-encoded parquet e.g. BRK_B.parquet, "
                  "then rebuild the cache-refresh overlay)")
            return 3
        print("PAYLOAD_COVERAGE_PASS: all roster tickers serveable via _cache_path "
              "in the local cache (= overlay).")
        return 0
    print(f"verifying {len(tickers)} tickers against s3://{args.bucket}/{args.key}")

    import boto3
    s3 = boto3.client("s3", region_name="us-east-1")
    body = s3.get_object(Bucket=args.bucket, Key=args.key)["Body"]
    tf = tarfile.open(fileobj=body, mode="r|")  # streaming, non-seeking

    found_file: set[str] = set()
    indexed: set[str] = set()
    index_seen = False
    for m in tf:
        n = m.name
        # B1344: the cache INDEX is authoritative (engine consults it, not files)
        if n.endswith("data/cache/index.json") and m.isfile():
            import json as _json
            idx = _json.loads(tf.extractfile(m).read().decode())
            keys = idx if isinstance(idx, list) else list(idx.keys())
            indexed = tickers & set(keys)
            index_seen = True
        if "ohlcv/" in n and n.endswith(".parquet"):
            stem = n.split("/")[-1][:-8]
            if stem in tickers:
                found_file.add(stem)
        if index_seen and found_file >= tickers:
            break
    missing_file = sorted(tickers - found_file)
    missing_index = sorted(tickers - indexed)
    print(f"index.json found in payload: {index_seen}")
    print(f"file-present ({len(found_file)}/{len(tickers)}); index-registered ({len(indexed)}/{len(tickers)})")
    if not index_seen:
        print("PAYLOAD_COVERAGE_FAIL: cache index.json not found in payload -- "
              "cannot confirm the engine will serve any ticker. Do NOT launch.")
        return 3
    if missing_index:
        print(f"PAYLOAD_COVERAGE_FAIL: NOT INDEX-REGISTERED ({len(missing_index)}): {missing_index}")
        print(f"  (file-present-but-unindexed: {sorted(set(missing_index) & found_file)} "
              f"-- exactly the BRK-B class: parquet exists but engine gets a cache MISS)")
        print("Do NOT launch -- refresh the payload's index.json, then re-verify.")
        return 3
    if missing_file:
        print(f"PAYLOAD_COVERAGE_FAIL: indexed but PARQUET MISSING ({len(missing_file)}): {missing_file}")
        return 3
    print("PAYLOAD_COVERAGE_PASS: all manifest tickers are index-registered AND "
          "have OHLCV parquet in the payload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
