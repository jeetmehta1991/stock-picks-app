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

WHERE THE ENGINE DOOR SITS - AT THE ENGINE'S OWN ENTRY (S6-B3358, B3139q-r140).
MEASURED at B3139q-r138, the word was checked on 2 of the 8 routes that start
the engine: the run_wave route (make_spec writes the spec, run_wave launches it
through launch_sweep; a chain takes it too, since run_serial_chain.py and
launch_detached.py start run_wave for each spec) and, from B3139q-r139,
launch_sweep.py run by hand (prelaunch_gate.check). The other six -
backtest/run_phase1a.py run directly, coverage_smoke.py,
run_phase_1a_beta_local.py, universe_ladder_run.py,
launch_phase_1a_beta_multibatch.py and aws_chunk_launch.py (EC2 user-data) -
bypassed every launch refusal; and that census, counting scripts that spawn a
process, missed four that build and run a BacktestEngine in-process
(profile_engine.py, smoke_test_cube_stage_d.py, smoke_test_screen_pool.py,
validate_smc_panel_cache_semantic.py - L986). So the check sits in the engine
itself: backtest/util/owner_word_gate.py, called by run_phase1a.main (after its
B1432 mode assert, before the engine is built) and by BacktestEngine.run, which
all 12 routes reach. The word arrives in the environment variable ENV_KEY
(env_value writes it; launch_sweep sets it from the manifest's owner_word, any
other launcher or in-process run sets it by hand), and env_refusals checks it
against the ledger the launcher names (STOCKPICKS_LANDING_ROOT, the main repo a
pinned worktree lands into) or the engine's own repo.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "EXECUTION_QUEUE.md"
ENV_KEY = "OWNER_WORD_JSON"     # S6-B3358: the engine entry's word, as JSON
MIN_CHARS = 8
_CURLY = {chr(0x2018): "'", chr(0x2019): "'", chr(0x201C): '"', chr(0x201D): '"'}


def normalise(text) -> str:
    """Whitespace collapsed, curly quotes straightened, surrounding quotes and
    spaces dropped - the ONLY transformation between a word and its row."""
    s = "".join(_CURLY.get(c, c) for c in str(text or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s.strip("'\" ").strip()


def _rows(ticket: str, queue=None) -> list:
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    import queue_state as _qs
    return [row for _n, row in _qs.history(ticket, path=str(queue or QUEUE))]


def refusals(word, *, door: str, queue=None) -> list:
    """[] when `word` cites a ticket whose ledger rows quote its words; else one
    refusal naming what is missing. Fails CLOSED on every absent part (L642).
    `queue` names the ledger to read (S6-B3358: the engine entry reads the one
    its launcher names); None reads QUEUE."""
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
        rows = _rows(ticket, queue)
    except Exception as e:
        return [f"REFUSED ({door}, S6-B3338): the ledger could not be read "
                f"({type(e).__name__}) - fail closed (L642)"]
    if not rows:
        return [f"REFUSED ({door}, S6-B3338): {ticket} has no row in "
                f"{Path(queue or QUEUE).name} - record the ruling on its ticket first"]
    if not any(verbatim in normalise(r) for r in rows):
        return [f"REFUSED ({door}, S6-B3338): no row of {ticket} quotes "
                f"{verbatim[:120]!r} - record the owner's words on the ticket, "
                "verbatim, before this door opens"]
    return []


def spec_refusals(spec) -> list:
    """The engine-launch door: a spec carries its owner word in 'owner_word'."""
    return refusals((spec or {}).get("owner_word"), door="engine launch")


def env_value(word) -> str:
    """S6-B3358: the environment form of a word - what a launcher sets in
    ENV_KEY so the engine's own entry can read it."""
    w = word or {}
    return json.dumps({"ticket": str(w.get("ticket") or ""),
                       "verbatim": str(w.get("verbatim") or "")})


def env_refusals(environ=None, *, door: str, queue=None) -> list:
    """S6-B3358: the engine-entry door - the word in ENV_KEY, checked against
    `queue`. Absent or unparseable is a refusal, never a pass (L642)."""
    raw = (os.environ if environ is None else environ).get(ENV_KEY)
    if not raw:
        return [f"REFUSED ({door}, S6-B3358): no owner word in {ENV_KEY} - a launcher "
                "sets it from the spec's owner_word (launch_sweep does); a direct or "
                f"older-launcher run sets {ENV_KEY} to owner_word.env_value(word), the "
                "word citing the ledger row that records the ruling"]
    try:
        word = json.loads(raw)
    except ValueError:
        return [f"REFUSED ({door}, S6-B3358): {ENV_KEY} is not JSON - "
                "set it with owner_word.env_value"]
    return refusals(word, door=door, queue=queue)
