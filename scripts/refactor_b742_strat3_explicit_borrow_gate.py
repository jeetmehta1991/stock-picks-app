# Source: Decision 5 Cat 1 critical path + B713 Phase 0 + B742/B743 dual _strat3 refactor per CHECKLIST #77 + owner-approved Option A 2026-06-13
"""B742/B743 refactor harness -- convert dual `_strat3` strategies to add
explicit `borrow_ok` borrow gate on the SHORT branch at the call site.

Per S4-B713-INSPECT-CURRENTFRAME-REVERT-TO-EXPLICIT-GATE + owner-approved
Option A (consistent with B740/B741 pattern). Each dual `_strat3` strategy
gets two changes:

  1. Append `and not _short_borrow_trap_active(s)` to its SHORT fires variable
     assembly (the 2nd positional arg to `_strat3(...)`).
  2. Append `"borrow_ok"` to its `signals_used_short` list (5th positional arg
     to `_strat3(...)`).

The LONG branch is UNAFFECTED -- direction="long" is not gated by the borrow
trap. `_strat3` continues to apply its inspect.currentframe path as
belt-and-braces; full removal staged for B718d after lint enabled.

USAGE
-----
    python scripts/refactor_b742_strat3_explicit_borrow_gate.py --chunk first
    python scripts/refactor_b742_strat3_explicit_borrow_gate.py --chunk second
    python scripts/refactor_b742_strat3_explicit_borrow_gate.py --chunk all --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[1]
SCREENER_PATH = _REPO / "backtest" / "signals" / "screener.py"


# 61 dual _strat3 strategies (enumerated 2026-06-13 via grep return _strat3\().
# Splits: B742 = first 31 (#1-#31), B743 = second 30 (#32-#61).
ALL_61 = [
    # B742 (first chunk)
    "strat_pivot_s1_bounce",                # 1
    "strat_pivot_s2_bounce",                # 2
    "strat_pivot_r1_breakout",              # 3
    "strat_pivot_r2_continuation",          # 4
    "strat_cpr_narrow_bullish",             # 5
    "strat_camarilla_s3_bounce",            # 6
    "strat_camarilla_r4_breakout",          # 7
    "strat_prev_day_high_break",            # 8
    "strat_prev_day_low_bounce",            # 9
    "strat_macd_crossover",                 # 10
    "strat_macd_fast_crossover",            # 11
    "strat_hull_rsi",                       # 12
    "strat_williams_r_oversold",            # 13
    "strat_roc_burst",                      # 14
    "strat_awesome_oscillator",             # 15
    "strat_stochrsi_oversold",              # 16
    "strat_ppo_crossover",                  # 17
    "strat_ultimate_oscillator",            # 18
    "strat_golden_cross_50_200",            # 19
    "strat_golden_cross_9_21",              # 20
    "strat_golden_cross_20_50",             # 21
    "strat_parabolic_sar_flip",             # 22
    "strat_tema_dema",                      # 23
    "strat_ichimoku_tk_cross",              # 24
    "strat_ichimoku_cloud_breakout",        # 25
    "strat_adx_initiation",                 # 26
    "strat_supertrend_macd",                # 27
    "strat_rsi_oversold",                   # 28
    "strat_rsi21_slow",                     # 29
    "strat_mfi_oversold",                   # 30
    "strat_cmf_flip",                       # 31
    # B743 (second chunk)
    "strat_bollinger_lower",                # 32
    "strat_bollinger_tight",                # 33
    "strat_keltner_lower",                  # 34
    "strat_stoch_oversold",                 # 35
    "strat_volume_spike_breakout",          # 36
    "strat_force_index_breakout",           # 37
    "strat_donchian_10_breakout",           # 38
    "strat_morning_star",                   # 39
    "strat_bullish_engulfing_support",      # 40
    "strat_rsi_volume_200ema",              # 41
    "strat_macd_ichimoku",                  # 42
    "strat_bb_squeeze_volume",              # 43
    "strat_pivot_fib_confluence",           # 44
    "strat_golden_cross_volume",            # 45
    "strat_cpr_narrow_momentum",            # 46
    "strat_camarilla_rsi_obv",              # 47
    "strat_supertrend_ichimoku_adx",        # 48
    "strat_williams_stoch_dual",            # 49
    "strat_dc20_break_retest",              # 50
    "strat_r1_break_retest",                # 51
    "strat_break_retest_volume",            # 52
    "strat_break_retest_confluence",        # 53
    "strat_smc_inverse_fvg",                # 54
    "strat_smc_bos_retest_entry",           # 55
    "strat_smc_bos_continuation",           # 56
    "strat_smc_choch_reversal",             # 57
    "strat_smc_order_block_bounce",         # 58
    "strat_smc_liquidity_sweep_reversal",   # 59
    "strat_avwap_252_breakout",             # 60
    "strat_avwap_50_reclaim",               # 61
]
FIRST_CHUNK = ALL_61[:31]   # B742 = #1-#31
SECOND_CHUNK = ALL_61[31:]  # B743 = #32-#61


def find_strategy_block(lines: list[str], strategy_name: str) -> tuple[int, int] | None:
    """Return (def_line_idx, end_idx_exclusive) for the strategy's function body."""
    def_re = re.compile(rf"^def {re.escape(strategy_name)}\(s\):\s*$")
    start = None
    for i, line in enumerate(lines):
        if def_re.match(line):
            start = i
            break
    if start is None:
        return None
    j = start + 1
    while j < len(lines) and "return _strat3(" not in lines[j]:
        if j > start + 1 and re.match(r"^def strat_\w+\(s\):\s*$", lines[j]):
            return None
        j += 1
    if j >= len(lines):
        return None
    return_open = j
    depth = 0
    k = return_open
    while k < len(lines):
        for ch in lines[k]:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return (start, k + 1)
        k += 1
    return None


def transform_strategy(lines: list[str], strategy_name: str) -> tuple[bool, str]:
    """Mutate lines in-place to add explicit borrow gate to the SHORT branch
    of a `_strat3` dual strategy.

    Returns (changed, note).
    """
    span = find_strategy_block(lines, strategy_name)
    if span is None:
        return (False, "function block not found")
    start, end = span

    body_text = "".join(lines[start:end])
    if "_short_borrow_trap_active(s)" in body_text:
        return (False, "already has explicit borrow gate -- skipped")
    if "return _strat3(" not in body_text:
        return (False, "not a _strat3 dual call -- skipped")

    # Locate the `return _strat3(<long>, <short>, ...)` call to extract the
    # SHORT variable name (2nd positional arg).
    short_var = None
    return_start = None
    for i in range(start, end):
        rm = re.search(
            r"return _strat3\(\s*([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*,", lines[i]
        )
        if rm:
            short_var = rm.group(2)
            return_start = i
            break
    if short_var is None:
        return (False, "could not extract SHORT var from return _strat3 call")

    # Find the `<short_var> = ...` assignment line in the function body BEFORE
    # the return call.
    var_pat = re.compile(rf"^(\s*){re.escape(short_var)}\s*=\s*(.*)$")
    short_line_idx = None
    short_paren_depth_at_eq = None
    for i in range(start, return_start):
        m = var_pat.match(lines[i])
        if m:
            short_line_idx = i
            tail = m.group(2)
            short_paren_depth_at_eq = tail.count("(") - tail.count(")")
            # don't break -- take the LAST one (in case there are multiple)
    if short_line_idx is None:
        return (False, f"{short_var} assignment not found")

    # Find the closing line of the short_var assignment.
    if short_paren_depth_at_eq <= 0:
        # single-line
        short_close_idx = short_line_idx
        line = lines[short_close_idx].rstrip("\n")
        code, comment_sep, comment = (line, "", "")
        if "#" in line:
            code, comment_sep, comment = line.partition("#")
            code = code.rstrip()
        new_line = code + " and not _short_borrow_trap_active(s)"
        if comment_sep:
            new_line += "  # " + comment.strip()
        lines[short_close_idx] = new_line + "\n"
    else:
        depth = short_paren_depth_at_eq
        j = short_line_idx + 1
        short_close_idx = None
        while j < return_start:
            depth += lines[j].count("(") - lines[j].count(")")
            if depth <= 0:
                short_close_idx = j
                break
            j += 1
        if short_close_idx is None:
            return (False, f"{short_var} assignment close not found")

        close_line = lines[short_close_idx].rstrip("\n")
        depth_in = short_paren_depth_at_eq + sum(
            lines[k].count("(") - lines[k].count(")")
            for k in range(short_line_idx + 1, short_close_idx)
        )
        depth_walk = depth_in
        close_paren_col = -1
        for col, ch in enumerate(close_line):
            if ch == "(":
                depth_walk += 1
            elif ch == ")":
                depth_walk -= 1
                if depth_walk == 0:
                    close_paren_col = col
                    break
        if close_paren_col < 0:
            return (False, "closing paren not located on short close line")

        before = close_line[:close_paren_col]
        after = close_line[close_paren_col:]
        before_stripped = before.rstrip()
        if before_stripped.endswith(("and", "or")):
            insertion = " not _short_borrow_trap_active(s)"
        else:
            prev_line_text = lines[short_close_idx - 1].rstrip("\n")
            prev_code = prev_line_text.split("#", 1)[0].rstrip() if "#" in prev_line_text else prev_line_text.rstrip()
            if before_stripped == "" and prev_code.endswith(("and", "or")):
                insertion = " not _short_borrow_trap_active(s)"
            else:
                insertion = " and not _short_borrow_trap_active(s)"
        lines[short_close_idx] = before + insertion + after + "\n"

    # Now find signals_used_short = 5th positional arg in `_strat3` call.
    # We need to walk the args from `return _strat3(` and find the 5th positional.
    # The call structure: _strat3(fl, fs, category, signals_used_long,
    #                              signals_used_short, bullets_long, bullets_short)
    # Walk character-by-character, tracking paren+bracket depth, counting commas
    # at depth==1 (inside the _strat3 args only).
    text_lines = []
    line_starts = []  # cumulative char offset where each line starts (relative to scan)
    cum = 0
    for i in range(return_start, end):
        text_lines.append(lines[i])
        line_starts.append(cum)
        cum += len(lines[i])
    flat = "".join(text_lines)

    # find '_strat3(' position in flat
    s3 = flat.find("_strat3(")
    if s3 < 0:
        return (False, "_strat3( not located after fix")
    paren_open = s3 + len("_strat3")  # position of `(`
    depth_paren = 0
    depth_bracket = 0
    arg_index = 0          # which positional arg we're currently inside
    in_string = False
    string_char = None
    sig_short_open_offset = None
    sig_short_close_offset = None
    pos = paren_open
    while pos < len(flat):
        ch = flat[pos]
        if in_string:
            if ch == "\\":
                pos += 2
                continue
            if ch == string_char:
                in_string = False
            pos += 1
            continue
        if ch in ('"', "'"):
            in_string = True
            string_char = ch
            pos += 1
            continue
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
            if depth_paren == 0:
                # end of _strat3 call
                break
        elif ch == "[":
            depth_bracket += 1
            # The OPENING `[` of arg_index==4 marks signals_used_short.
            if depth_paren == 1 and depth_bracket == 1 and arg_index == 4 and sig_short_open_offset is None:
                sig_short_open_offset = pos
        elif ch == "]":
            depth_bracket -= 1
            if depth_paren == 1 and depth_bracket == 0 and arg_index == 4 and sig_short_close_offset is None:
                sig_short_close_offset = pos
        elif ch == "," and depth_paren == 1 and depth_bracket == 0:
            arg_index += 1
        pos += 1

    if sig_short_open_offset is None or sig_short_close_offset is None:
        return (False, "signals_used_short list not located (arg_index 4)")

    # Convert flat offset back to (line_idx, col).
    def flat_to_pos(offset):
        for li in range(len(line_starts) - 1, -1, -1):
            if line_starts[li] <= offset:
                return (return_start + li, offset - line_starts[li])
        return (return_start, offset)

    sig_end_line, sig_end_col = flat_to_pos(sig_short_close_offset)
    sig_open_line, sig_open_col = flat_to_pos(sig_short_open_offset)

    # Insert `, "borrow_ok"` just before the `]` of signals_used_short.
    close_line_text = lines[sig_end_line]
    before = close_line_text[:sig_end_col]
    after = close_line_text[sig_end_col:]
    insert_str = ', "borrow_ok"'
    if before.rstrip().endswith("["):
        insert_str = '"borrow_ok"'
    elif before.rstrip().endswith(","):
        insert_str = '"borrow_ok"'
    lines[sig_end_line] = before + insert_str + after

    return (True, f"refactored short var={short_var} at lines {short_close_idx+1}..{sig_end_line+1}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chunk", choices=["first", "second", "all"], required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    targets = FIRST_CHUNK if args.chunk == "first" else (SECOND_CHUNK if args.chunk == "second" else ALL_61)

    src = SCREENER_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    n_lines_before = len(src)

    changed = 0
    skipped = 0
    report = []
    for name in targets:
        ok, note = transform_strategy(src, name)
        if ok:
            changed += 1
            report.append(f"  [OK]   {name}  -- {note}")
        else:
            skipped += 1
            report.append(f"  [SKIP] {name}  -- {note}")

    print(f"B742/B743 _strat3 refactor: chunk={args.chunk}  targets={len(targets)}")
    print(f"  changed: {changed}  skipped: {skipped}")
    print(f"  lines: {n_lines_before} -> {len(src)} (delta {len(src) - n_lines_before:+})")
    print()
    for line in report:
        print(line)

    if args.dry_run:
        print()
        print("[DRY-RUN] no file written")
        return 0
    SCREENER_PATH.write_text("".join(src), encoding="utf-8")
    print()
    print(f"[WROTE] {SCREENER_PATH.relative_to(_REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
