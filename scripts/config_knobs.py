"""S6-B3386 (B3139q-r162b): set backtest.config knobs for the length of a
block WITHOUT reloading the module.

WHY. A script that must run a producer at a landed arm's knobs used to export
the knobs to os.environ and call importlib.reload(backtest.config). Reload
re-executes the module and REBINDS every module-level name to a new object,
so a module that imported one by value - exit_manager's
`from backtest.config import CIRCUIT_BREAKERS` - keeps the old object, and
every later mock.patch.dict of the config name patches a dict the engine
never reads. In the battery's own subprocess that is harmless; called in
process (a test) it broke test_bug_30 and test_bug_232 in the full suite
while both passed alone - the third time (L330, L484, L1002; CHECKLIST #209).

HOW. `applied(env)` exports each value, evaluates config.py in a SCRATCH
namespace (runpy - so the parse and every range check are the engine's own,
and an out-of-range level raises ValueError exactly as an engine launch
would), then sets ONLY the named attributes on the live module. Nothing else
in the live module moves. On exit, success or not, the attributes and the
environment are put back as they were.

The knob's config attribute must carry its env name (SQUEEZE_KC_MULT reads
SQUEEZE_KC_MULT); a name the module does not define is refused before
anything is set (KeyError), because setting it would create an attribute no
producer reads.
"""
from __future__ import annotations

import contextlib
import os
import runpy
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "backtest" / "config.py"


@contextlib.contextmanager
def applied(env: dict):
    """Within the block, backtest.config.<NAME> is the value config.py parses
    from env[NAME] (None or "" -> the production default, L900) and
    os.environ[NAME] carries the raw value. Yields {NAME: parsed value}."""
    import backtest.config as cfg
    missing = sorted(k for k in env if not hasattr(cfg, k))
    if missing:
        raise KeyError(f"backtest.config defines no {missing} - a knob is set "
                       "on the attribute its env names, and none exists")
    prev_env = {k: os.environ.get(k) for k in env}
    prev_val = {k: getattr(cfg, k) for k in env}
    try:
        for k, v in env.items():
            os.environ[k] = "" if v is None else str(v)
        ns = runpy.run_path(str(CONFIG_PATH), run_name="config_knobs_scratch")
        parsed = {k: ns[k] for k in env}
        for k, v in parsed.items():
            setattr(cfg, k, v)
        yield parsed
    finally:
        for k, v in prev_val.items():
            setattr(cfg, k, v)
        for k, v in prev_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
