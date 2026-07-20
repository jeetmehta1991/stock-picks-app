"""scripts/build_r5_code_tar.py (B1325 Council 357): build + upload the LEAN
code tar to S3, replacing the stale 5.8GB monolithic r5_code.tar (which bundled
the whole repo incl .git + data_prefetch and went stale -> cloud ran 07-17 code,
B1324).

Uses `git archive HEAD` = tracked files ONLY (backtest/ + scripts/ + vendored/ +
requirements + configs) at the CURRENT commit. No .git, no untracked data/
outputs/caches. The data comes separately from the stable r5_payload.tar
(data_prefetch), which the launcher extracts after the code tar.

SHA-tied: the tar is the current HEAD, so env_fingerprint code_sha on the
instance must equal this SHA -- that's the code_sha parity gate (coverage_smoke).

Usage:
  python scripts/build_r5_code_tar.py            # build + report size/SHA
  python scripts/build_r5_code_tar.py --upload   # also upload to S3
"""
from __future__ import annotations

import os
import subprocess
import sys

BUCKET = "stock-picks-r5-jm-2026"
KEY = "payload/r5_code.tar"
OUT = "r5_code.tar"
# Runtime code + small config/universe only. The big OHLCV (data_prefetch,
# 3.2GB) comes from the stable r5_payload.tar. Excludes tracked-but-not-needed
# data/output dirs (data_prefetch, archive, .archive, output_*, dashboards)
# that bloated the old 5.8GB whole-repo tar.
INCLUDE_PATHS = [
    "backtest", "scripts", "vendored", "requirements.txt",
    "Backtesting universe", "data",
]


def main() -> int:
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        print("WARN: tracked files are modified/uncommitted -- git archive uses "
              "HEAD (committed state), so those changes will NOT be in the tar:")
        print(dirty[:500])
    subprocess.run(["git", "archive", "--format=tar", "-o", OUT, "HEAD", "--",
                    *INCLUDE_PATHS], check=True)
    size_mb = os.path.getsize(OUT) / 1e6
    print(f"built {OUT}: {size_mb:.0f} MB  @ SHA {sha[:12]}")
    if "--upload" in sys.argv:
        import boto3
        print(f"uploading -> s3://{BUCKET}/{KEY} ...")
        boto3.client("s3", region_name="us-east-1").upload_file(OUT, BUCKET, KEY)
        print(f"uploaded. Cloud runs will now use SHA {sha[:12]}. "
              f"env_fingerprint code_sha must match (coverage_smoke code_sha gate).")
    else:
        print("(dry run -- pass --upload to push to S3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
