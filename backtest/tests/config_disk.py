"""backtest/tests/config_disk.py (B1481, tickets S6-B1480a/b) -- read a constant's ON-DISK value
from `backtest/config.py` WITHOUT reloading the module into the live process.

WHY THIS EXISTS
Three tests asserted the on-disk default of a config constant by calling `importlib.reload(cfg)`.
That is the right INTENT -- they want the committed value, not whatever the current process has
monkeypatched -- implemented in the one way that corrupts the whole test session.

`importlib.reload()` re-executes the module and REBINDS every module-level name to a NEW object.
Modules that imported by value keep the OLD object:

    # backtest/engine/exit_manager.py
    from backtest.config import CIRCUIT_BREAKERS      # binds the object, not the name

After a reload, `backtest.config.CIRCUIT_BREAKERS` is a DIFFERENT dict from the one
`exit_manager` holds. `mock.patch.dict("backtest.config.CIRCUIT_BREAKERS", ...)` then patches an
object the engine never reads. That is the S6-B1468a polluter: it made two GATE tests
(`test_bug_30_check_circuit_breakers_gate_on_config`, `test_bug_232_...`) fail in a full run while
passing alone, and took 430 -> 13 -> 2 files to isolate because no SINGLE file reproduces it --
one file must import the victim first, another must reload (L330).

Crucially, no pytest isolation mechanism protects against this. monkeypatch, fixtures and
`patch.dict` all restore by OBJECT IDENTITY, which reload has already invalidated.

THE FIX
Parse the assignment out of the source file with `ast`. No import, no execution, no global state
touched -- and it answers the actual question ("what is committed?") more directly than a reload
ever did, because it cannot be affected by anything the process has already done.
"""
from __future__ import annotations

import ast
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.py"


def disk_value(name: str, path: Path | None = None):
    """Return the literal assigned to `name` at module level in config.py, from DISK.

    Raises LookupError if the name is absent or its value is not a literal (a computed
    value cannot be read without executing the module, which is the thing being avoided).
    """
    src = (path or CONFIG_PATH).read_text(encoding="utf-8")
    tree = ast.parse(src)
    found = None
    for node in tree.body:                      # module level only, deliberately
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        for t in targets:
            if isinstance(t, ast.Name) and t.id == name:
                found = node.value if isinstance(node, ast.Assign) else node.value
    if found is None:
        raise LookupError(f"{name!r} is not assigned at module level in {path or CONFIG_PATH}")
    try:
        return ast.literal_eval(found)
    except ValueError as exc:                   # preflight-allow: re-raised with context
        raise LookupError(
            f"{name!r} is assigned a non-literal in config.py, so its on-disk value cannot be "
            f"read without executing the module: {ast.dump(found)[:120]}"
        ) from exc
