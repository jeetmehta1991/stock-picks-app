"""scripts/write_cache_schemas.py - Tier J8 (Pass 53 v8h+1 owner-mandated 2026-05-08).

Writes a `_schema.json` sidecar to each canonical cache directory, capturing
the locked column set from CANONICAL_SCHEMAS in test_schema_canonical.py.

Purpose: machine-readable schema lock so downstream consumers (dashboard,
agents, integrations) can validate cache shape without importing the test
module. Pairs with J4 regression test.

Run: python scripts/write_cache_schemas.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backtest.tests.test_schema_canonical import CANONICAL_SCHEMAS  # noqa: E402


def main() -> int:
    written = 0
    skipped_missing = 0
    for rel_dir, cols in sorted(CANONICAL_SCHEMAS.items()):
        d = REPO_ROOT / rel_dir
        if not d.is_dir():
            skipped_missing += 1
            continue
        out = d / "_schema.json"
        out.write_text(
            json.dumps(
                {
                    "cache_dir": rel_dir,
                    "canonical_columns": sorted(cols),
                    "source": "backtest/tests/test_schema_canonical.py CANONICAL_SCHEMAS",
                    "owner_directive": "Pass 53 J8 2026-05-08",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        written += 1
        print(f"  wrote {out.relative_to(REPO_ROOT)}")
    print(f"\n_schema.json sidecars: {written} written, {skipped_missing} skipped (cache absent).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
