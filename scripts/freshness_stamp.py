"""scripts/freshness_stamp.py - ONE writer for the shared generator-freshness
stamp (S6-B3139ap).

test_b1974 reads a generated artifact as fresh when this stamp holds the
sha256 of every generator source that produced it. That is what lets an
OUTPUT-PRESERVING generator edit - one whose regeneration leaves the artifact
byte-identical, so nothing is left to commit - be satisfied by running the
generator instead of by a no-op artifact commit (B1976). The file is SHARED by
every registered generator, so a writer reads it and updates its own keys,
never overwriting the others' (B2078 - a fresh-dict writer once deleted
another generator's entry on every run).

Callers: build_strategy_roster.py (S6-B3139ap), build_phase_1b_roster.py and
build_strategy_producer_map.py (S6-B3139bf, which retired their inline
writers). test_b3139bf holds the writer count at one.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STAMP = REPO / "output_audit" / "phase_1b_roster_freshness.json"


def stamp_generators(*rel_paths: str, stamp_path: Path | None = None,
                     root: Path | None = None) -> dict:
    """Record the sha256 of each generator source (repo-relative path) in the
    shared stamp and return the stamp. Call it AFTER the artifact is written:
    the stamp asserts that these sources produced what is on disk."""
    root = REPO if root is None else Path(root)
    sp = STAMP if stamp_path is None else Path(stamp_path)
    stamp = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    for rel in rel_paths:
        stamp[rel] = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    sp.write_text(json.dumps(stamp, indent=1), encoding="utf-8")
    return stamp
