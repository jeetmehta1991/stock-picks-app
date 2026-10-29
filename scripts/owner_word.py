#!/usr/bin/env python
"""S6-B3338 (B3139q-r138): THE OWNER'S WORD AT A ONE-WAY DOOR, CHECKED AGAINST
THE LEDGER WHERE IT IS RECORDED.

WHY. The owner asked 2026-10-29T13:14:30Z (delivered mid-turn 13:20:17Z),
verbatim 'Why wasnt breath step followed if all runbook workflow is
mechanically enforced? Same for why werent bands shown for approval before
triggering run if mechanically enforced?'. The
2026-10-28 runbook census (output_audit/b3139q_r137_runbook_enforcement_census.json)
classes 'never launch the engine without the owner's launch word' UNENFORCED
and 'T3: no grid runs before the owner's word' TEXT-PIN-ONLY on the engine
path: the offline Step-1 tools require a --band-ruling
(step1_gates.require_band_ruling), but make_spec, run_wave and launch_sweep
checked none, and a depth candidate's Step-2 holdout read
(offline_holdout_read.py) took no ruling at all. The owner approved
mechanizing these doors 2026-10-28T16:50:12Z ('your rec approved' on
'Mechanize the your-word steps ... first').

WHAT IT CHECKS. A door's word is {"ticket": <S6 id>, "verbatim": <the owner's
words>}. It passes when the ticket has a row in EXECUTION_QUEUE.md that quotes
the words - compared after whitespace is collapsed and curly quotes are
straightened - so a launch or a read cites a ruling the ledger records, where
the owner reads it. ONE definition (L593) for the doors that use it: the
engine launch (run_wave.main, before any arm; make_spec.main, before a spec is
written; prelaunch_gate.check, at every leg and on a hand-run launch_sweep),
a depth candidate's Step-2 holdout read (offline_holdout_read.main), a widened
breadth axis (breadth_step1_grid.widen_word) and the reopening of a terminal
strategy (producer_variant_table._terminal_status_refusals; make_spec
--reopen-word / --reopen-word-ticket writes that word into a spec, and a --dry
draft prints the terminal status as a NOTE, as it needs no launch word).

THE LEDGER IS A REPOSITORY FACT (L792 / #305): it is read from the CODE tree,
never from a run's root that a test or a staged launch may relocate; QUEUE is
the one attribute a test points at a fixture ledger.

LIMITS, stated so the check is not over-read. It proves the cited words are
RECORDED on the cited ticket, not that the owner typed them - the session
transcript is the only record of that, and none of the door scripts reads it
('transcript' appears in none of run_wave, make_spec, launch_sweep,
prelaunch_gate or offline_holdout_read, MEASURED 2026-10-29); a row
written with invented words is a fabrication, which the truth standard
governs, not this check. A ruling's scope (which levels, which strategies) is
read by the person citing it: the check matches words, not meaning. MIN_CHARS
= 8 is CHOSEN, not measured (L740): it is the length of 'approved', the owner's
whole ruling at 2026-10-28T16:50:12Z (recorded on S6-B3304 and S6-B3248), so a
ruling that short can be cited, and a citation shorter than any ruling seen
would match unrelated row text.

WHERE THE ENGINE DOOR SITS - TWO ROUTES OF EIGHT (MEASURED 2026-10-29). The
run_wave route (make_spec writes the spec, run_wave launches it through
launch_sweep), the route the runbook prescribes (S6-B3154a) - a chain takes it
too, since run_serial_chain.py and launch_detached.py start run_wave for each
spec - and, from B3139q-r139, launch_sweep.py run by hand, whose
prelaunch_gate.check now checks the word where B2578 put launch_refusals: all
four launchers S6-B3338's first row counts. Of the 21 scripts that name the
engine and spawn a process, 5 more build an engine command and are NOT
checked: coverage_smoke.py, run_phase_1a_beta_local.py, universe_ladder_run.py,
launch_phase_1a_beta_multibatch.py and aws_chunk_launch.py (EC2 user-data);
nor is backtest/run_phase1a.py run directly. aws_b660_launch.py and
aws_batch395_launch.py name the engine only in text and were not classified.
These routes bypass every launch refusal, not only this one: S6-B3358.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "EXECUTION_QUEUE.md"
MIN_CHARS = 8
_CURLY = {chr(0x2018): "'", chr(0x2019): "'", chr(0x201C): '"', chr(0x201D): '"'}


def normalise(text) -> str:
    """Whitespace collapsed, curly quotes straightened, surrounding quotes and
    spaces dropped - the ONLY transformation between a word and its row."""
    s = "".join(_CURLY.get(c, c) for c in str(text or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s.strip("'\" ").strip()


def _rows(ticket: str) -> list:
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    import queue_state as _qs
    return [row for _n, row in _qs.history(ticket, path=str(QUEUE))]


def refusals(word, *, door: str) -> list:
    """[] when `word` cites a ticket whose ledger rows quote its words; else one
    refusal naming what is missing. Fails CLOSED on every absent part (L642)."""
    if not isinstance(word, dict):
        return [f"REFUSED ({door}, S6-B3338): no owner word - this door needs "
                "{'ticket': <S6 id>, 'verbatim': <the owner's words>} citing the "
                "ledger row that records the ruling"]
    ticket = str(word.get("ticket") or "").strip()
    verbatim = normalise(word.get("verbatim"))
    if not ticket:
        return [f"REFUSED ({door}, S6-B3338): the owner word names no ticket"]
    if len(verbatim) < MIN_CHARS:
        return [f"REFUSED ({door}, S6-B3338): the owner word {verbatim!r} is under "
                f"{MIN_CHARS} characters - quote the ruling as the ledger row records it"]
    try:
        rows = _rows(ticket)
    except Exception as e:
        return [f"REFUSED ({door}, S6-B3338): the ledger could not be read "
                f"({type(e).__name__}) - fail closed (L642)"]
    if not rows:
        return [f"REFUSED ({door}, S6-B3338): {ticket} has no row in "
                f"{Path(QUEUE).name} - record the ruling on its ticket first"]
    if not any(verbatim in normalise(r) for r in rows):
        return [f"REFUSED ({door}, S6-B3338): no row of {ticket} quotes "
                f"{verbatim[:120]!r} - record the owner's words on the ticket, "
                "verbatim, before this door opens"]
    return []


def spec_refusals(spec) -> list:
    """The engine-launch door: a spec carries its owner word in 'owner_word'."""
    return refusals((spec or {}).get("owner_word"), door="engine launch")
