# -*- coding: utf-8 -*-
"""Write a Python file only after it parses (B1883 / S6-B1864d).

MEASURED: a patch script called `path.write_text(src)` and THEN
`ast.parse(path.read_text())`. The source had a `\\`-continuation followed by
implicit string concatenation - a syntax error - so it landed in
`test_unit.py` and pytest collection failed for the ENTIRE suite. **The
validator existed; it was positioned after the damage.**

A check that runs after the mutation reports a fact you can no longer act on.
"""
from __future__ import annotations

import ast
import pathlib


class WouldNotParse(SyntaxError):
    """The candidate source is invalid - nothing was written."""


def safe_write_py(path, source: str, *, encoding: str = "utf-8") -> pathlib.Path:
    """Parse `source`, then write it. Never the other way round.

    Raises `WouldNotParse` and leaves the file untouched if the candidate is
    invalid, so a generator cannot corrupt a module it is editing.
    """
    p = pathlib.Path(path)
    try:
        ast.parse(source)
    except SyntaxError as exc:
        raise WouldNotParse(
            f"refusing to write {p}: candidate source does not parse "
            f"({exc.msg} at line {exc.lineno}). The file is UNCHANGED. "
            "Validate before the mutation, not after - a check that runs "
            "afterwards reports a fact you can no longer act on."
        ) from exc
    p.write_text(source, encoding=encoding)
    return p


def safe_append_py(path, block: str, *, encoding: str = "utf-8") -> pathlib.Path:
    """Append `block`, but only if the RESULT parses."""
    p = pathlib.Path(path)
    current = p.read_text(encoding=encoding) if p.exists() else ""
    return safe_write_py(p, current + block, encoding=encoding)
