"""B1338 (Council 365, owner-approved): Stop-hook v2 -- live-run churn
whitelist (ends the .stop_exempt waste cycles) + mechanical compliance-marker
check (skill Phase 6: a turn that commits must end with the CHECKLIST
compliance statement).
"""
import scripts.verify_turn_compliance as vtc


def test_churn_only_passes():
    subst, churn = vtc.split_churn([
        " M data/cache/info_cache.json",
        " M backtest/data/economic_calendar.json",
        "M STRATEGY_ROSTER.md",
    ])
    assert subst == [] and len(churn) == 3


def test_substantive_still_blocks():
    subst, churn = vtc.split_churn([
        " M data/cache/info_cache.json",
        " M backtest/engine/backtest.py",
    ])
    assert len(subst) == 1 and "backtest.py" in subst[0]


def _turn(commit: bool, marker: bool):
    entries = [
        {"type": "user", "message": {"content": "do the thing"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "input": {"command": "git commit -m 'x'" if commit
                                           else "ls"}}]}},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "*CHECKLIST compliance: #45 ok*" if marker
             else "done."}]}},
    ]
    return entries


def test_marker_scan_commit_without_marker_flagged():
    commit_made, marker = vtc.scan_transcript_entries(_turn(True, False))
    assert commit_made is True and marker is False


def test_marker_scan_commit_with_marker_ok():
    commit_made, marker = vtc.scan_transcript_entries(_turn(True, True))
    assert commit_made is True and marker is True


def test_marker_scan_no_commit_ok():
    commit_made, marker = vtc.scan_transcript_entries(_turn(False, False))
    assert commit_made is False


def test_marker_scan_only_counts_after_last_user_message():
    # a commit in a PRIOR turn (before the latest user message) must not count
    entries = _turn(True, False) + [
        {"type": "user", "message": {"content": "new question"}},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "answer, no commit"}]}},
    ]
    commit_made, _ = vtc.scan_transcript_entries(entries)
    assert commit_made is False
