"""B1049 launch script unbound-variable audit (PIVOT #29 catch).

# Source: HONEST-FINDING PIVOT #29 - Phase D B1048 launch HALTED at
# B1019 PREFLIGHT because PHASE_DIR was undefined at preflight invocation
# (set only inside run_phase function). Per CHECKLIST #126 + #122 +
# feedback_silent_failure_pairing_rule per CHECKLIST #77.

Bug class: under bash `set -uxo pipefail` (user-data heredoc directive),
referencing an unbound variable errors with non-zero exit. The `||`
fallback then fires + emits a misleading sentinel (the real failure is
shell-syntax, not application logic).

Pyramid catches:
- Variables referenced in launch script outside the function scope where
  they're defined
- Variables used in heredoc commands before they're assigned
- Specifically: PHASE_DIR (defined in run_phase function) must NOT be
  referenced outside that function
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LAUNCH = REPO / "scripts" / "launch_r5_master_4y_v2.sh"


def test_b1049_launch_script_phase_dir_only_inside_run_phase():
    """PHASE_DIR is set inside run_phase() function. Any reference to
    PHASE_DIR OUTSIDE that function would error under set -u in the
    user-data heredoc context.

    B1049 PIVOT #29: B1048 Phase D HALTED at preflight because
    `--output ${PHASE_DIR}/...` was referenced BEFORE run_phase fired.
    """
    content = LAUNCH.read_text()
    # Split at run_phase function boundaries
    # run_phase starts at "run_phase() {" and ends with the matching "}"
    # For static analysis: find lines referencing PHASE_DIR
    # Exempt: lines inside run_phase function body
    in_run_phase = False
    brace_depth = 0
    violations = []
    for i, line in enumerate(content.splitlines(), 1):
        if re.search(r"^\s*run_phase\s*\(\s*\)\s*\{", line):
            in_run_phase = True
            brace_depth = 1
            continue
        if in_run_phase:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                in_run_phase = False
                continue
        if "PHASE_DIR" in line and not in_run_phase:
            # Allow comments + the run_phase call itself
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Allow run_phase invocations that PASS PHASE_DIR as arg
            if re.search(r"^\s*run_phase\b", stripped):
                continue
            violations.append((i, stripped[:120]))
    assert not violations, (
        f"B1049 PIVOT #29: PHASE_DIR referenced outside run_phase() function "
        f"causes 'unbound variable' under set -u in user-data heredoc. "
        f"Violations: {violations}. Use literal path (e.g., 'output_phase_1') "
        f"or define PHASE_DIR before referencing."
    )


def test_b1049_launch_script_bash_n_syntax_valid():
    """bash -n syntax check on the launch script (no execution)."""
    import subprocess
    result = subprocess.run(
        ["bash", "-n", str(LAUNCH)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, (
        f"bash -n syntax error in {LAUNCH}: {result.stderr[:400]}"
    )


def test_b1049_preflight_invocation_uses_literal_output_dir():
    """B1049 PIVOT #29 fix: preflight --output uses literal path
    (output_phase_1/...) not undefined ${PHASE_DIR}/..."""
    content = LAUNCH.read_text()
    # Find the preflight invocation line
    preflight_block = None
    in_preflight = False
    for line in content.splitlines():
        if "B1019 PREFLIGHT" in line and "echo" in line:
            in_preflight = True
            preflight_block = []
        if in_preflight:
            preflight_block.append(line)
            if "exit 1" in line or len(preflight_block) > 10:
                break
    assert preflight_block is not None, "Preflight block not found"
    block_text = "\n".join(preflight_block)
    # The fix: literal output_phase_1 path, NOT ${PHASE_DIR} in this
    # scope
    assert "output_phase_1/b1019_a5_preflight_report.json" in block_text, (
        "B1049 PIVOT #29 fix: preflight --output must use literal "
        "output_phase_1 path (PHASE_DIR undefined at this point in user-data)"
    )
    # And the prior buggy pattern must be absent
    assert "\\${PHASE_DIR}/b1019_a5_preflight_report.json" not in block_text, (
        "Old buggy ${PHASE_DIR}/... preflight pattern still present"
    )
