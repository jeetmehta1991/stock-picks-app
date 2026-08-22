# -*- coding: utf-8 -*-
"""Read a Python file as CODE, with comments and docstrings blanked (B1906).

**A source-text assertion cannot tell code from prose.** The sentence that
explains a defect reads exactly like the defect, so a pin that greps raw source
fires on its own documentation. That has now happened ~11 times here, most
recently when B1905 pinned "the renderer must not print a nan" and the pin
failed on the COMMENT above the fix saying it no longer does.

Rewording the comment fixes one instance and leaves the class open. This blanks
the prose instead, so the assertion reads what the code DOES.

    from source_text import code_only
    src = code_only(path)
    assert "float('nan')" not in src

**Blanked in place, never rebuilt.** B1906b joined tokens with spaces and
`_measured.fmt` came back as `_measured . fmt` - which turns a `not in`
assertion True for the wrong reason. Character ranges are overwritten with
spaces so offsets, layout and every dotted name stay byte-identical.

Use `raw()` deliberately when the assertion really IS about prose - a required
comment marker, a docstring contract - so the choice is visible at the call
site rather than implied.
"""
from __future__ import annotations

import io
import pathlib
import tokenize

_STMT_BOUNDARY = (None, tokenize.NEWLINE, tokenize.NL, tokenize.INDENT,
                  tokenize.DEDENT, tokenize.ENCODING)


def _read(path_or_src) -> str:
    s = str(path_or_src)
    if "\n" in s or s.strip().startswith(("#", "import ", "def ")):
        return s
    return pathlib.Path(s).read_text(encoding="utf-8")


def code_only(path_or_src) -> str:
    """Source with comments and docstrings replaced by spaces.

    A docstring is a STRING token standing alone as a statement, so it is
    blanked; a string being assigned, called or compared is CODE and is kept -
    otherwise every assertion about a string literal would silently weaken.

    On a tokenize error the RAW text is returned rather than a partial strip: a
    half-blanked haystack makes an assertion quietly weaker, which is worse
    than one that reads too much.
    """
    src = _read(path_or_src)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return src

    lines = src.splitlines(keepends=True)
    buf = [list(ln) for ln in lines]
    # B2011: a docstring exists only at PAREN DEPTH 0. Without depth tracking,
    # a string following a comment INSIDE a dict/call was blanked as a
    # docstring - `"is_ci_lo": ...` after an inline comment vanished from the
    # haystack, failing a true `in` assertion loudly here and, worse, letting
    # any `not in` over such a region pass vacuously (L582's class).
    prev, depth = None, 0
    for tok in toks:
        if tok.type == tokenize.OP:
            if tok.string in "([{":
                depth += 1
            elif tok.string in ")]}":
                depth = max(0, depth - 1)
        drop = (tok.type == tokenize.COMMENT
                or (tok.type == tokenize.STRING and depth == 0
                    and prev in _STMT_BOUNDARY))
        if drop:
            (sr, sc), (er, ec) = tok.start, tok.end
            for row in range(sr, min(er, len(buf)) + 1):
                ln = buf[row - 1]
                a = sc if row == sr else 0
                b = ec if row == er else len(ln)
                for j in range(a, min(b, len(ln))):
                    if ln[j] != "\n":
                        ln[j] = " "
        if tok.type != tokenize.COMMENT:
            prev = tok.type
    return "".join("".join(ln) for ln in buf)


def raw(path) -> str:
    """The unmodified text - for assertions that ARE about the prose."""
    return pathlib.Path(path).read_text(encoding="utf-8")
