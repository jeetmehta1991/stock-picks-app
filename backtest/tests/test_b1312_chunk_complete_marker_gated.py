"""B1312 pin: the AWS chunk launcher must gate the CHUNK_COMPLETE heartbeat
marker on ACTUAL window completion (engine_state status='complete'), never
write it unconditionally after process exit.

Root cause it guards: chunk 2 hit --max-run-hours at day 669/~1002 (status
still 'running'); the old user-data wrote CHUNK2_COMPLETE regardless, which
fooled the auto-resume controller (resumes=0) into stopping a 67%-done run.
Class fix -> completion markers reflect real completion, not process exit.
"""
import re
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "scripts" / "aws_chunk_launch.py"


def _template() -> str:
    txt = LAUNCHER.read_text(encoding="utf-8")
    m = re.search(r'USERDATA_TEMPLATE = r"""(.*?)"""', txt, re.S)
    assert m, "USERDATA_TEMPLATE not found in aws_chunk_launch.py"
    return m.group(1)


def test_complete_marker_is_status_gated():
    body = _template()
    # The COMPLETE marker must be guarded by a status=='complete' check.
    assert 'if [ "$ST" = "complete" ]' in body, (
        "CHUNK_COMPLETE must be gated on engine_state status=='complete'"
    )
    # A capped/interrupted exit must emit a resume-triggering CAPPED marker.
    assert "CHUNK@N@_CAPPED" in body, "non-complete exit must emit CAPPED marker"


def test_no_unconditional_complete_echo():
    body = _template()
    # The specific pre-B1312 bug: an echo of CHUNK_COMPLETE with no preceding
    # status test. Ensure every COMPLETE echo sits inside the status branch.
    for line in body.splitlines():
        if "CHUNK@N@_COMPLETE" in line:
            # the only permitted COMPLETE echo lives after the status gate;
            # assert it carries the day suffix introduced with the gate.
            assert "day=$DY" in line, (
                "CHUNK_COMPLETE echo must be the gated one (day=$DY suffix)"
            )
