"""scripts/preengine_gate.py (B1328 Council 360): HARD pre-engine gate that
runs on the instance AFTER env_fingerprint --emit but BEFORE the engine starts,
so a bad environment ABORTS with zero engine spend (owner directive - every
batch must refuse to spend on a broken env).

Checks (all must pass):
  - smc_active is True         (else 22 SMC/ICT strategies silent - B1317/B4)
  - calendar_backend == nyse_mcal (else degraded Mon-Fri grid - L207)
  - code_sha == expected SHA   (else STALE cloud code - B1324)

Usage (in user-data):
  python3.11 scripts/preengine_gate.py output_chunkN/env_fingerprint.json <EXPECTED_SHA>
Exit 0 = PASS (run the engine); exit 3 = FAIL (abort, do not spend).
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("PREENGINE_GATE_FAIL usage: <fingerprint.json> <expected_sha>")
        return 3
    fp_path, expected = sys.argv[1], sys.argv[2][:12]
    try:
        fp = json.load(open(fp_path, encoding="utf-8"))
    except Exception as exc:
        print(f"PREENGINE_GATE_FAIL no/unreadable fingerprint: {exc}")
        return 3
    bad = []
    if not fp.get("smc_active"):
        bad.append(f"smc_active={fp.get('smc_active')} "
                   f"(lib={fp.get('smc_lib_importable')} phase={fp.get('smc_phase')})")
    if fp.get("calendar_backend") != "nyse_mcal":
        bad.append(f"calendar_backend={fp.get('calendar_backend')}")
    cloud_sha = str(fp.get("code_sha", ""))[:12]
    if cloud_sha != expected:
        bad.append(f"code_sha={cloud_sha} != expected={expected}")
    if bad:
        print("PREENGINE_GATE_FAIL:", "; ".join(bad))
        return 3
    print(f"PREENGINE_GATE_PASS smc_active=True calendar=nyse_mcal "
          f"code_sha={cloud_sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
