"""S6-B3358 (B3139q-r140): the owner's launch word at the engine itself.

MEASURED at B3139q-r138, the word was checked on 2 of the 8 routes that start
the engine as a process (run_wave, and launch_sweep through prelaunch_gate);
backtest/run_phase1a.py run directly and five older launchers reached the
engine past every launch refusal. MEASURED at B3139q-r140, four more scripts
build a BacktestEngine in-process and never pass run_phase1a's main
(profile_engine.py, smoke_test_cube_stage_d.py, smoke_test_screen_pool.py,
validate_smc_panel_cache_semantic.py) - a population the r138 census, which
counted scripts that spawn a process, could not see. So the check has ONE
definition here, called in two places: run_phase1a.main, before any engine
work, and BacktestEngine.run, which every route that runs an engine reaches.

The word arrives in scripts/owner_word.ENV_KEY (launch_sweep sets it from the
manifest; a direct, older-launcher or in-process run sets it by hand with
owner_word.env_value) and is checked against the ledger the launcher names:
STOCKPICKS_LANDING_ROOT - the main repo a pinned worktree lands into, whose
ledger holds rulings recorded after the pin - when it holds
EXECUTION_QUEUE.md, else this engine's own repo. owner_word is loaded from
this engine's own tree, and sys.path is restored after, so nothing the check
imports reaches the engine's import path. Fails CLOSED (L642): a word that
cannot be checked is a refusal. MEASURED: one check takes about 0.04 s.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TAG = "[S6-B3358 OWNER WORD]"


def engine_word_refusals(environ=None) -> list:
    """[] when the environment carries a word its launcher's ledger records;
    else one refusal naming what is missing."""
    environ = os.environ if environ is None else environ
    landing = environ.get("STOCKPICKS_LANDING_ROOT")
    base = (Path(landing) if landing and (Path(landing) / "EXECUTION_QUEUE.md").is_file()
            else REPO)
    saved = list(sys.path)
    try:
        import importlib.util as _ilu
        spec = _ilu.spec_from_file_location("owner_word_engine_entry",
                                            REPO / "scripts" / "owner_word.py")
        ow = _ilu.module_from_spec(spec)
        spec.loader.exec_module(ow)
        return ow.env_refusals(environ, door="engine entry",
                               queue=base / "EXECUTION_QUEUE.md")
    except Exception as exc:  # noqa: BLE001 - an unchecked word must not pass
        return [f"REFUSED (engine entry, S6-B3358): the owner-word check could not "
                f"run ({type(exc).__name__}) - fail closed (L642)"]
    finally:
        sys.path[:] = saved


def require_engine_word(environ=None) -> None:
    """Raise SystemExit with the refusal when the word does not pass."""
    refused = engine_word_refusals(environ)
    if refused:
        raise SystemExit(f"{TAG} {refused[0]}")
