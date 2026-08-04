"""scripts/audit_criteria_enforcement.py (B1456) -- which PASSING_CRITERIA keys are actually
ENFORCED, and which are only DEFINED?

OWNER QUESTION (2026-08-04): "Canonical criterion #11 - why was this missed and not implemented?
what are other such criteria?"

The generalization: #11 must not be audited alone. Every key in PASSING_CRITERIA is a candidate
for the same failure -- a threshold that exists in config, is pinned by a unit test asserting its
VALUE, and is read by nothing that gates anything. A value-pin test makes such a key look covered
while contributing zero enforcement, which is precisely how #11 survived 1,400+ batches.

Classification per key:
  ENFORCED  - read inside a gating expression (a `passes`/`gates` dict, or an if that rejects)
  ADVISORY  - read somewhere, but only to report/route, never to reject
  ORPHANED  - read by nothing outside config.py and the tests that pin its value

ORPHANED + a value-pin test is the dangerous combination: green tests, no implementation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.config import PASSING_CRITERIA as PC  # noqa: E402

# the modules that actually decide pass/fail
GATING = [
    REPO / "backtest" / "results" / "metrics.py",
    REPO / "scripts" / "build_phase_1b_roster.py",
    REPO / "scripts" / "canonical_criteria_check.py",
    REPO / "scripts" / "best_exit_by_gates.py",
]
SEARCH_DIRS = [REPO / "backtest", REPO / "scripts"]


def _py_files():
    for d in SEARCH_DIRS:
        for p in d.rglob("*.py"):
            # tests pin values; they are not enforcement
            if "test" in p.name:
                continue
            yield p


def main() -> int:
    src = {p: p.read_text(encoding="utf-8", errors="ignore") for p in _py_files()}
    gating_src = {p: src.get(p, "") for p in GATING if p in src}

    print("=" * 104)
    print("PASSING_CRITERIA ENFORCEMENT AUDIT (B1456)")
    print("=" * 104)
    print(f"  {len(PC)} keys in config | {len(src)} non-test .py files scanned")
    print(f"  gating modules: {', '.join(p.name for p in gating_src)}\n")

    rows = []
    for key in sorted(PC):
        pat = re.compile(r"""["']""" + re.escape(key) + r"""["']""")
        readers = sorted({p.name for p, s in src.items()
                          if p.name != "config.py" and pat.search(s)})
        in_gate = sorted({p.name for p, s in gating_src.items() if pat.search(s)})
        if in_gate:
            status = "ENFORCED"
        elif readers:
            status = "ADVISORY"
        else:
            status = "ORPHANED"
        rows.append((key, PC[key], status, readers))

    for status in ("ORPHANED", "ADVISORY", "ENFORCED"):
        sel = [r for r in rows if r[2] == status]
        print(f"--- {status}  ({len(sel)}) " + "-" * (78 - len(status)))
        for key, val, _, readers in sel:
            r = ", ".join(readers[:3]) + (" ..." if len(readers) > 3 else "")
            print(f"  {key:<36} = {str(val):<8} {r}")
        print()

    orph = [r for r in rows if r[2] == "ORPHANED"]
    print("=" * 104)
    print(f"  ORPHANED: {len(orph)} of {len(PC)} keys are defined but read by NO non-test module.")
    print("  These are thresholds the project believes it enforces and does not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
