#!/usr/bin/env python
# Source: <cube_dir>/gate_receipt.json + <cube_dir>/run_manifest.json
# (written by scripts/launch_sweep.py at launch), per CHECKLIST #77.
"""B2622 (S6-B2540a): re-issue an M10 gate receipt after a LEGITIMATE
manifest repair - mechanically, with the reason recorded.

THE GAP THIS CLOSES: the M10 receipt pins manifest_sha256 as the launch gate
read it, so any later manifest edit makes the battery's 1_cube_sanity FAIL -
correctly, because the check exists to catch a manifest swapped after
approval. But a LEGITIMATE repair (the B2540 grading-key backfill on
output_icg_span9_span9) then carries a permanent FAIL, and the distinction
between a repaired manifest and a swapped one rested on prose in a ledger
row. This command makes the distinction mechanical: it re-reads the manifest,
records WHY it changed and WHAT the receipt said before, and issues a fresh
receipt whose `regate_history` preserves every prior state.

FAIL-CLOSED RULES (L642):
  - a cube with NO receipt is REFUSED: re-gating cannot retroactively bless a
    cube launched around the gate (that converts UNDECLARED into APPROVED);
  - --why is REQUIRED and must be non-trivial (>= 20 chars): a re-gate with
    no stated reason is the swap the check exists to catch;
  - a receipt already matching the manifest is a no-op (exit 0, says so).

Usage:
  python scripts/regate_manifest.py --cube-dir output_icg_span9_span9 \
      --why "B2540 grading-key backfill: engine env untouched, grid P9_span=9 matches"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def regate(cube_dir: Path, why: str) -> tuple[int, str]:
    """Returns (exit_code, message). Pure enough to pin."""
    why = (why or "").strip()
    if len(why) < 20:
        return 2, ("REFUSED: --why must state the repair in >= 20 chars - a "
                   "re-gate with no reason is the manifest swap M10 exists to catch")
    rp = cube_dir / "gate_receipt.json"
    mp = cube_dir / "run_manifest.json"
    if not rp.exists():
        return 2, ("REFUSED: no gate_receipt.json - a cube launched AROUND the "
                   "gate cannot be blessed retroactively (L642); run the launch "
                   "gate path, do not re-gate")
    if not mp.exists():
        return 2, "REFUSED: no run_manifest.json beside the cube - nothing to re-gate to"
    rec = json.loads(rp.read_text(encoding="utf-8"))
    actual = hashlib.sha256(mp.read_bytes()).hexdigest()
    if rec.get("manifest_sha256") == actual:
        return 0, f"no-op: receipt already matches manifest sha {actual[:12]}"
    hist = rec.get("regate_history") or []
    hist.append({
        "previous_manifest_sha256": rec.get("manifest_sha256"),
        "previous_timestamp": rec.get("timestamp"),
        "why": why,
        "regated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    rec["regate_history"] = hist
    rec["manifest_sha256"] = actual
    rec["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rp.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return 0, (f"re-gated: manifest sha -> {actual[:12]}; prior sha and the "
               f"stated reason preserved in regate_history "
               f"({len(hist)} entr{'y' if len(hist) == 1 else 'ies'})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube-dir", required=True)
    ap.add_argument("--why", required=True,
                    help="the repair, stated (>= 20 chars); recorded verbatim")
    a = ap.parse_args()
    code, msg = regate(ROOT / a.cube_dir if not Path(a.cube_dir).is_absolute()
                       else Path(a.cube_dir), a.why)
    print(msg)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
