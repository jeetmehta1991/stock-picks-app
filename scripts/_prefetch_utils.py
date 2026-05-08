"""scripts/_prefetch_utils.py - shared helpers for prefetch scripts.

Pass 53 Day-9 v8h+1 owner-mandated 2026-05-08 (Tier J6).

All NEW prefetch scripts must use safe_filename_stem() for any per-ticker
filename to avoid Windows reserved-name collisions (CON / PRN / AUX / NUL /
COM1-9 / LPT1-9). Existing scripts may continue using inline copies; the empirical
risk is zero (verified 2026-05-08: 0 collisions across 139,823 parquets), but
this is the canonical helper going forward.

INV-043 lineage: corp_actions cache hit a CON.parquet collision pre-fix.
"""

from __future__ import annotations

# Windows reserved names (case-insensitive) that cannot be used as filenames.
RESERVED_WIN: frozenset[str] = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


def safe_filename_stem(ticker: str) -> str:
    """Return a filesystem-safe stem for a ticker.

    Replaces '-' with '_' (a common ticker convention) and appends '_' to any
    Windows-reserved name to prevent OS-level filename collisions.

    Examples:
        AAPL  -> AAPL
        BRK-B -> BRK_B
        CON   -> CON_
        nul   -> nul_  (case preserved; reserved check is case-insensitive)
    """
    safe = str(ticker).replace("-", "_")
    if safe.upper() in RESERVED_WIN:
        safe = safe + "_"
    return safe
