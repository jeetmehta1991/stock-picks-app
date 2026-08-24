#!/usr/bin/env python
"""B1612 / CHECKLIST #207 - is every SWEPT parameter reachable by the ENGINE?

The optimisation sweep grades SUBSET-SAFE parameters OFFLINE, re-deriving fires
from cached OHLCV instead of re-running the engine. That is what makes 4,000
combinations affordable. It also means the search space can contain gates the
ENGINE CANNOT APPLY - and nothing noticed, because the grader is perfectly happy
to simulate a filter that exists only inside itself.

WHEN THIS WAS FIRST RUN (2026-08-17) four of six swept parameters were
grader-only. B1616 CLOSED that under owner approval, so all six now reach the
engine; the history is kept because it is what the check exists to prevent:

    P2 close_mitigation  WAS  smc_ict calling _smc.ob(ohlc, swings)
    P3 tail_n            WAS  a hardcoded .tail(20)
    P4 age_bars_max      WAS  a breaker loop with no age filter at all
    P5 break_pct_max     WAS  absent from engine code entirely

A winning combination on any of them would NOT have been DEPLOYABLE: the engine
would have kept firing at its hardcoded values, and cfg2's graded winner - 68
fires at Sharpe 2.239 - would have run live as 420 fires at Sharpe 0.789, with a
different exit method selected on the different fire set. That is the
`regime_flip` failure (L461), a number carrying a label whose logic never ran,
moved one stage earlier from exits to entry gates.

This check asserts the ENGINE-side facts against live source, so drift is caught
in BOTH directions: a parameter silently losing its wiring, and a parameter
quietly gaining it without the table being updated.

Usage:  python scripts/verify_engine_implemented.py
Exit:   0 = every swept parameter is implemented or DECLARED unimplemented with
            an open ticket; 2 = an undeclared gap, or the table has drifted.

**HAND-RUN-ONLY (B1704).** Nothing invokes this automatically - no Stop hook, no
pre-commit, no launcher. An audit found 12 of 16 gate scripts in this state, so
presence is NOT enforcement (CHECKLIST #224). Run it explicitly and read its exit
code; if you need it to bind, wire it and say where.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

QUEUE = Path("EXECUTION_QUEUE.md")

# param -> (implemented?, file, the exact source token that proves it, ticket)
# `token` is matched against the file's live text. For an UNIMPLEMENTED entry the
# token is the evidence it is NOT parameterised (e.g. the hardcoded literal), so
# the check fails if someone implements it without updating this table.
PARAMS = {
    "P1 swing_length": (
        True, "backtest/signals/screener.py",
        "swing_length=_cfg.SMC_SWING_LENGTH", None),
    # B1616 (S6-B1612f, owner-approved): P2-P5 now REACH the engine. Each token
    # below is the live expression that carries the value into the producer, so
    # this check fails if any of them is removed or renamed.
    "P2 close_mitigation": (
        # B2114 sweep: the SIBLING of the P4 brittleness fixed the same turn -
        # this token also ended at a call's closing paren, so any future
        # kwarg on the _smc.ob call would break the anchor while the wiring
        # stayed true. The kwarg expression alone IS the fact being asserted.
        True, "backtest/signals/smc_ict.py",
        "close_mitigation=close_mitigation", None),
    # B1619: the loop moved into `_breaker_scan`, shared by the base path and
    # every variant so the two cannot drift. The anchors follow it - what must
    # hold is that the CONFIGURED value reaches the scan, not where the scan lives.
    "P3 tail_n": (
        True, "backtest/signals/smc_ict.py",
        "ob_df, close, current_idx, ob_tail_n,", None),
    "P4 age_bars_max": (
        # B2114: the base call grew optional kwargs (ohlc/retest_out for the
        # retest events), so the old anchor's trailing `)` stopped matching
        # while the WIRING stayed true - the #275 format-brittleness class.
        # The anchor now ends at the comma: the configured values still reach
        # the scan whatever follows them in the call.
        True, "backtest/signals/smc_ict.py",
        "breaker_age_bars_max, breaker_break_pct_max,", None),
    "P5 break_pct_max": (
        True, "backtest/signals/smc_ict.py",
        "break_max is not None", None),
    "P6 ema span": (
        True, "backtest/signals/screener.py",
        '_ema_key = f"price_above_ema_{_cfg.STRAT_EMA_SPAN}"', None),
}
# Reaching the producer's SIGNATURE is not the same as the engine PASSING a
# value: the call site must read config, or the knobs are dead in production.
CALL_SITE = "backtest/signals/screener.py"
CALL_SITE_TOKENS = (
    'close_mitigation=getattr(_cfg, "SMC_OB_CLOSE_MITIGATION", False)',
    'ob_tail_n=getattr(_cfg, "SMC_OB_TAIL_N", 20)',
    'breaker_age_bars_max=getattr(_cfg, "SMC_BREAKER_AGE_BARS_MAX", None)',
    'breaker_break_pct_max=getattr(_cfg, "SMC_BREAKER_BREAK_PCT_MAX", None)',
    'breaker_variants=getattr(_cfg, "SMC_BREAKER_VARIANTS", None)',
)
# The breaker loop must now CONTAIN an age filter. Before B1616 this same
# region was asserted to contain NONE - the inversion is the shipped change.
# The scan body must still CONTAIN an age filter. Anchored on `_breaker_scan`
# now that the loop lives there; before B1616 this same region was asserted to
# contain NO age filter, and the inversion is the shipped change.
# NON-greedy stopped at the EARLY-RETURN guard, before the age filter, and
# reported a false FAIL. Greedy spans to the function's final return. A gate
# that cries wolf gets ignored, so the anchor has to be right (L474).
BREAKER_LOOP = r"def _breaker_scan\(.*return breaker_bull, breaker_bear"
AGE_FILTER = r"age_max is not None"


def _code_only(src: str) -> str:
    """Source with comments and string literals BLANKED IN PLACE.

    B1621: this gate matched raw text, so a token inside a comment or a
    docstring satisfied it. VERIFIED:

        "break_max is not None" in "# if break_max is not None:  # DISABLED"  -> True

    A disabled parameter would therefore report ENGINE-IMPLEMENTED - the
    `wired=yes` grep heuristic this project banned after ~150 false RESOLVED
    claims, re-implemented inside the guard against exactly that.

    Blanking IN PLACE rather than dropping tokens is deliberate: a tokenizer
    that re-joins with spaces turns `_cfg.SMC_SWING_LENGTH` into
    `_cfg . SMC_SWING_LENGTH` and every anchor in this file stops matching.
    Preserving offsets keeps both substring and REGEX anchors working.
    """
    import io
    import tokenize
    lines = src.splitlines(keepends=True)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        return src  # tokenizer failed: fall back rather than pass silently
    # A STRING at STATEMENT position is a docstring or a bare string expression
    # and can hide a token. A STRING inside an expression is real code - the
    # call-site anchors are literally `getattr(_cfg, "SMC_OB_TAIL_N", 20)`, so
    # blanking every string would delete the very thing being asserted.
    prev = tokenize.NEWLINE
    drop = []
    for tok in toks:
        if tok.type == tokenize.COMMENT:
            drop.append(tok)
        elif tok.type == tokenize.STRING and prev in (
                tokenize.NEWLINE, tokenize.NL, tokenize.INDENT,
                tokenize.DEDENT, tokenize.ENCODING):
            drop.append(tok)
        if tok.type not in (tokenize.COMMENT, tokenize.NL):
            prev = tok.type
    for tok in drop:
        (r1, c1), (r2, c2) = tok.start, tok.end
        for r in range(r1, r2 + 1):
            ln = lines[r - 1]
            body = ln.rstrip("\n")
            nl = ln[len(body):]
            lo = c1 if r == r1 else 0
            hi = c2 if r == r2 else len(body)
            lines[r - 1] = body[:lo] + " " * max(0, hi - lo) + body[hi:] + nl
    return "".join(lines)


def check() -> list[str]:
    failures: list[str] = []
    queue = QUEUE.read_text(encoding="utf-8", errors="ignore") if QUEUE.exists() else ""
    for name, (implemented, rel, token, ticket) in PARAMS.items():
        src = Path(rel).read_text(encoding="utf-8", errors="ignore")
        # B1621: match against CODE only. Whitespace is normalised by the
        # tokenizer, so compare on a whitespace-collapsed token too.
        code = _code_only(src)
        present = token in code
        if implemented and not present:
            failures.append(
                f"{name}: declared ENGINE-IMPLEMENTED but `{token}` is gone from "
                f"{rel}. Either the wiring regressed or the table is stale - "
                f"a swept parameter the engine cannot apply produces a winner "
                f"that will not reproduce live (L475).")
        if not implemented:
            if not present:
                failures.append(
                    f"{name}: declared NOT-IMPLEMENTED on the evidence of "
                    f"`{token}` in {rel}, and that token is GONE. If it is now "
                    f"parameterised, update this table and close {ticket}.")
            elif ticket and ticket not in queue:
                failures.append(
                    f"{name}: NOT implemented in the engine and ticket {ticket} "
                    f"is absent from EXECUTION_QUEUE.md. An unimplemented swept "
                    f"parameter must carry an open implementation ticket.")

    # P4 is an ABSENCE-turned-PRESENCE: assert the age filter is INSIDE the
    # breaker loop, not merely somewhere in the file.
    smc = _code_only(Path("backtest/signals/smc_ict.py").read_text(
        encoding="utf-8", errors="ignore"))
    m = re.search(BREAKER_LOOP, smc, re.S)
    if not m:
        failures.append(
            "P4 age_bars_max: could not locate the breaker-block loop in "
            "smc_ict.py - this check has gone stale and must be re-anchored.")
    elif not re.search(AGE_FILTER, m.group(0)):
        failures.append(
            "P4 age_bars_max: the age filter is GONE from the breaker loop. "
            "The parameter would be accepted and silently ignored - worse than "
            "not having it, because the signature implies it works.")

    # B1619: `_breaker_scan` must be called by the BASE path AND the variant
    # path. One call site means variants are not actually parameterised; a
    # second implementation means base and variant can drift.
    n_scan = len(re.findall(r"_breaker_scan\(", smc))
    if n_scan < 3:  # def + base call + variant call
        failures.append(
            f"_breaker_scan appears {n_scan} times in smc_ict.py; expected the "
            f"definition plus a BASE call and a VARIANT call. Either variants "
            f"are not parameterised, or a second copy of the loop exists and "
            f"can drift from the base (L475).")

    # The producer accepting a parameter proves nothing if the engine never
    # passes one. Assert the call site reads config for all four.
    call = _code_only(Path(CALL_SITE).read_text(encoding="utf-8", errors="ignore"))
    for tok in CALL_SITE_TOKENS:
        if tok not in call:
            failures.append(
                f"call site {CALL_SITE} does not pass `{tok}` - the knob exists "
                f"in the producer's signature but the engine never sets it, "
                f"which is 'wired' in name only (L475).")
    return failures


def main() -> int:
    failures = check()
    impl = [k for k, v in PARAMS.items() if v[0]]
    gap = [k for k, v in PARAMS.items() if not v[0]]
    print(f"swept parameters: {len(PARAMS)}")
    print(f"  ENGINE-IMPLEMENTED ({len(impl)}): {', '.join(impl)}")
    print(f"  GRADER-ONLY ({len(gap)}): {', '.join(gap)}")
    if gap:
        print("\n  A winner using a GRADER-ONLY value is NOT DEPLOYABLE until "
              "the engine\n  can apply it - the live strategy would not "
              "reproduce its own backtest.")
    if failures:
        print("\nFAIL:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 2
    print("\nPASS - " + ("every swept parameter reaches the engine."
                        if not gap else
                        "every gap is DECLARED and carries an open ticket."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
