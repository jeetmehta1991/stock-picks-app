"""S6-B3329: hand pytest a list of node ids or paths in an ARGFILE.

pytest reads arguments from a file named with "@" (its parser's
fromfile_prefix_chars), one argument per line, so a selection of any size
travels in a file and the command line stays short. MEASURED: a 421-id
selection (34,819 bytes) exited 126 'Argument list too long' before any test
ran (B3139q-r131), and a 493-id one died on WinError 206 (B3139q-r139).

Every launch that expands an unbounded list onto pytest's command line goes
through argfile(); test_b3329 sweeps scripts/ and backtest/ for one that does
not.
"""
from __future__ import annotations

import contextlib
import os
import tempfile


@contextlib.contextmanager
def argfile(items, prefix: str = "pytest_args_"):
    """Yield "@<path>" for a temp file holding one item per line; the file is
    removed on exit. An EMPTY list is refused: pytest given an empty argfile
    collects its whole default suite (MEASURED, 4 of 4 tests in a throwaway
    directory), the opposite of a selection."""
    items = [str(i) for i in items]
    if not items:
        raise ValueError("argfile: an empty selection would run pytest's "
                         "whole default suite")
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=".txt")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write("".join(i + "\n" for i in items))
        yield "@" + path
    finally:
        os.unlink(path)
