# Source: Decision 5 Cat 1 critical path + B713 Phase 0 + B718b chunked refactor per CHECKLIST #77
"""B718b/c refactor harness -- convert pure-short strategies to explicit
`borrow_ok` gate at the call site.

Per S4-B713-INSPECT-CURRENTFRAME-REVERT-TO-EXPLICIT-GATE: replace the
inspect.currentframe-based borrow guard in `_strat` with explicit per-strategy
declarations. Each pure-short strategy (direction="short" via `_strat`, not
`_strat3`) gets two changes:

  1. Append `and not _short_borrow_trap_active(s)` to its `fires` boolean
     (creating an explicit visible-at-call-site borrow gate).
  2. Append `"borrow_ok"` to its `signals_used` list passed to `_strat()`
     (so the registration-time lint S4-B713-REGISTRATION-TIME-BORROW-GATE-LINT
     can assert presence).

`_strat`'s inspect.currentframe path is RETAINED in B718b/c as belt-and-braces;
B718d removes it once all 116 short strategies (51 pure-short + 63 dual `_strat3`)
have been converted AND the lint is enabled.

USAGE
-----
    python scripts/refactor_b718b_explicit_borrow_gate.py --chunk first
    python scripts/refactor_b718b_explicit_borrow_gate.py --chunk second
    python scripts/refactor_b718b_explicit_borrow_gate.py --chunk all  --dry-run

Each invocation:
  - Targets a documented subset of strategies (see SCRATCHPAD_FIRST_CHUNK / SECOND_CHUNK below)
  - Reads `backtest/signals/screener.py`
  - For each named strategy, walks its function body, modifies the fires assembly
    line AND the signals_used list, prints a per-strategy diff
  - Writes the modified file
  - Reports per-strategy success/skip with reason

This is a TRANSFORMATION script, not a one-shot. Its idempotency guard: detects
strategies that already contain `_short_borrow_trap_active(s)` and skips them
(no double-application). Re-runs are safe.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[1]
SCREENER_PATH = _REPO / "backtest" / "signals" / "screener.py"


# 51 pure-short strategies (enumerated 2026-06-13 via grep _strat\(.*"short").
# Splits: B740 = first 26 (#1-#26), B741 = second 25 (#27-#51).
ALL_51 = [
    # B740 (B718b first chunk)
    "strat_pivot_r3_blowoff_short",                  # 1
    "strat_rsi_overbought_short",                    # 2
    "strat_bollinger_upper_short",                   # 3
    "strat_52w_low_breakdown_pullback_short",        # 4
    "strat_donchian_breakdown_retest_short",         # 5
    "strat_doji_at_resistance_short",                # 6
    "strat_three_black_crows_short",                 # 7
    "strat_shooting_star_short",                     # 8
    "strat_death_cross_50_200_volume",               # 9
    "strat_supertrend_macd_short",                   # 10
    "strat_ichimoku_cloud_breakdown",                # 11
    "strat_parabolic_sar_flip_short",                # 12
    "strat_macd_crossover_short",                    # 13
    "strat_stochrsi_overbought_short",               # 14
    "strat_donchian_breakdown_short",                # 15
    "strat_52w_low_breakdown",                       # 16
    "strat_prev_day_low_breakdown",                  # 17
    "strat_camarilla_rsi_obv_short",                 # 18
    "strat_cpr_narrow_momentum_short",               # 19
    "strat_52wl_break_retest_short",                 # 20
    "strat_orb_stocks_in_play_short",                # 21
    "strat_xs_momentum_bottom_decile_short",         # 22
    "strat_po3_bearish",                             # 23
    "strat_htf_aligned_breakout_short",              # 24
    "strat_weekly_bias_pullback_short",              # 25
    "strat_smc_fvg_retest_short",                    # 26
    # B741 (B718b second chunk)
    "strat_smc_breaker_block_short",                 # 27
    "strat_smc_mitigation_block_short",              # 28
    "strat_smc_premium_short",                       # 29
    "strat_smc_ote_short",                           # 30
    "strat_smc_equal_highs_sweep_short",             # 31
    "strat_turtle_soup_short",                       # 32
    "strat_judas_swing_short",                       # 33
    "strat_mmsm_short",                              # 34
    "strat_week_opening_gap_fill_down",              # 35
    "strat_pead_short",                              # 36
    "strat_pead_short_negative_yoy_growth",          # 37
    "strat_avwap_20high_rejection_short",            # 38
    "strat_head_and_shoulders_top_short",            # 39
    "strat_inverted_cup_and_handle_short",           # 40
    "strat_triangle_descending_short",               # 41
    "strat_flag_bear_retest_short",                  # 42
    "strat_simple_below_ema_50_short",               # 43
    "strat_classification_change_to_defensive_short",# 44
    "strat_classification_change_from_tech_short",   # 45
    "strat_vol_spike_2x_below_ema_50_short",         # 46
    "strat_risk_off_bond_equity_short",              # 47
    "strat_dxy_headwind_multinational_short",        # 48
    "strat_pairs_mean_reversion_short",              # 49
    "strat_news_momentum_short",                     # 50
    "strat_news_reversal_short",                     # 51
]
FIRST_CHUNK = ALL_51[:26]   # B740 = #1-#26
SECOND_CHUNK = ALL_51[26:]  # B741 = #27-#51


_DEF_PAT = re.compile(r"^def (strat_\w+)\(s\):\s*$")
_RETURN_STRAT_SHORT_PAT = re.compile(
    r'^(\s+return _strat\()([^,]+),\s*"short",\s*("[^"]+"),\s*$'
)


def find_strategy_block(lines: list[str], strategy_name: str) -> tuple[int, int] | None:
    """Return (def_line_idx, end_idx_exclusive) for the strategy's body.
    End is the line AFTER the closing of the _strat(...) return call.
    """
    def_re = re.compile(rf"^def {re.escape(strategy_name)}\(s\):\s*$")
    start = None
    for i, line in enumerate(lines):
        if def_re.match(line):
            start = i
            break
    if start is None:
        return None
    # find the line containing `return _strat(`
    j = start + 1
    while j < len(lines) and "return _strat(" not in lines[j]:
        # bail if we hit the next def -- this strategy doesn't use _strat directly
        if j > start + 1 and _DEF_PAT.match(lines[j]):
            return None
        j += 1
    if j >= len(lines):
        return None
    return_open = j
    # find the matching closing paren (account for nested parens)
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
    """Mutate lines in-place to add explicit borrow gate to a single strategy.

    Returns (changed, note).
    """
    span = find_strategy_block(lines, strategy_name)
    if span is None:
        return (False, "function block not found")
    start, end = span

    # Idempotency: skip if `_short_borrow_trap_active(s)` already present
    body_text = "".join(lines[start:end])
    if "_short_borrow_trap_active(s)" in body_text:
        return (False, "already has explicit borrow gate -- skipped")
    # Check this is a short-direction call
    if not re.search(r'_strat\([^,]+,\s*"short"', body_text):
        return (False, "not a pure-short _strat call -- skipped")

    # Find `<var> = ...` assignment whose result feeds into `return _strat(<var>, "short", ...)`.
    # Variants: `fires`, `fs`, `f_short`, `fires_short` (any single short-side variable).
    # We detect by reading the return _strat call's first positional arg name.
    return_var = None
    for i in range(start, end):
        rm = re.search(r'return _strat\(\s*([A-Za-z_]\w*)\s*,\s*"short"', lines[i])
        if rm:
            return_var = rm.group(1)
            break
    if return_var is None:
        return (False, "return _strat short call not located")

    fires_line_idx = None
    fires_paren_depth_at_eq = None
    var_pat = re.compile(rf"^(\s*){re.escape(return_var)}\s*=\s*(.*)$")
    for i in range(start, end):
        m = var_pat.match(lines[i])
        if m:
            fires_line_idx = i
            tail = m.group(2)
            fires_paren_depth_at_eq = tail.count("(") - tail.count(")")
            break
    if fires_line_idx is None:
        return (False, f"{return_var} assignment not found")

    # Find the line where the fires assignment closes (paren depth returns to 0).
    # The fires assignment is either single-line OR uses one open paren which
    # closes later. We track the depth and find the line where the OUTERMOST
    # open paren of the fires assembly is closed.
    if fires_paren_depth_at_eq <= 0:
        # single-line: fires = expr (no wrapping parens or all-balanced)
        fires_close_idx = fires_line_idx
        # locate the position of end-of-expression on this single line
        # (handle inline comment + trailing newline)
        line = lines[fires_close_idx].rstrip("\n")
        # split off trailing comment for clean append
        code, comment_sep, comment = (line, "", "")
        if "#" in line:
            code, comment_sep, comment = line.partition("#")
            code = code.rstrip()
        # append the borrow gate condition; this is a SINGLE-LINE expression so
        # we just append ` and not _short_borrow_trap_active(s)` to the code.
        new_line = code + " and not _short_borrow_trap_active(s)"
        if comment_sep:
            new_line = new_line + "  # " + comment.strip()
        lines[fires_close_idx] = new_line + "\n"
    else:
        # multi-line: find the closing line by paren depth, then INSERT the new
        # condition BEFORE the closing `)` character on that line. This preserves
        # the chain's connective structure (the prior trailing `and` continues to
        # link to OUR inserted condition; our condition is the LAST one before `)`).
        depth = fires_paren_depth_at_eq
        j = fires_line_idx + 1
        while j < end:
            depth += lines[j].count("(") - lines[j].count(")")
            if depth <= 0:
                fires_close_idx = j
                break
            j += 1
        else:
            return (False, "fires assignment close not found")

        close_line = lines[fires_close_idx].rstrip("\n")
        # find the position of the closing `)` that brings depth to 0 on this line
        depth_in = fires_paren_depth_at_eq + sum(
            lines[k].count("(") - lines[k].count(")")
            for k in range(fires_line_idx + 1, fires_close_idx)
        )
        # walk close_line tracking depth, find the `)` index where depth hits 0
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
            return (False, "closing paren not located on close line")

        before = close_line[:close_paren_col]
        after = close_line[close_paren_col:]
        # detect whether `before` already has a trailing connective (and/or) on
        # the last token; if so, just append `not ...`; else prepend `and `.
        before_stripped = before.rstrip()
        # also need to strip a possible trailing comma (rare but possible)
        if before_stripped.endswith(("and", "or")):
            insertion = " not _short_borrow_trap_active(s)"
        else:
            # walk back to the last token; if the line above ends in `and`/`or`,
            # connective already in place; else need `and `
            prev_line_text = lines[fires_close_idx - 1].rstrip("\n")
            if "#" in prev_line_text:
                prev_code = prev_line_text.split("#", 1)[0].rstrip()
            else:
                prev_code = prev_line_text.rstrip()
            if before_stripped == "" and prev_code.endswith(("and", "or")):
                insertion = " not _short_borrow_trap_active(s)"
            else:
                insertion = " and not _short_borrow_trap_active(s)"
        lines[fires_close_idx] = before + insertion + after + "\n"

    # Now find the `return _strat(fires, "short", category, [signals_used], ...)`
    # call and append "borrow_ok" to the signals_used list.
    for i in range(fires_close_idx, end):
        if "return _strat(" in lines[i]:
            return_start = i
            break
    else:
        return (False, "return _strat call not found after fires")
    # The next non-blank line typically starts with `["sig1","sig2",...]`
    # signals_used list. Find the line containing the FIRST opening bracket
    # that's not on the return line.
    sig_line_idx = None
    for i in range(return_start, end):
        line = lines[i]
        # the signals_used list opens with `[` and may close on same or next line
        if "[" in line and i > return_start:
            # skip the return line itself; signals_used is the 4th positional arg
            sig_line_idx = i
            break
        if "[" in line and i == return_start:
            # signals_used could be inline on the return line for very short calls
            # e.g.  return _strat(fires, "short", "cat", ["a","b"], ["bullet1","bullet2"])
            sig_line_idx = i
            break
    if sig_line_idx is None:
        return (False, "signals_used [ not found")

    # find matching ] for the signals_used list (first [ after the category arg)
    line = lines[sig_line_idx]
    # locate the [ after the third comma (fires, short, category, [signals_used]
    # we use a forward scan from a position past the third comma on the return line
    if sig_line_idx == return_start:
        # inline -- find third comma on this line, then the [ after it
        sig_start_col = None
        commas = 0
        i_ch = 0
        while i_ch < len(line):
            ch = line[i_ch]
            if ch == ",":
                commas += 1
                if commas == 3:
                    # find next [
                    bracket_col = line.find("[", i_ch)
                    if bracket_col >= 0:
                        sig_start_col = bracket_col
                        break
            i_ch += 1
        if sig_start_col is None:
            return (False, "signals_used inline [ not located")
    else:
        # multi-line: signals_used is on its own line; find first [
        sig_start_col = line.find("[")

    # find matching ]
    depth = 0
    sig_end_line = sig_line_idx
    sig_end_col = -1
    start_col = sig_start_col
    cur_line = sig_line_idx
    cur_col = start_col
    while cur_line < end:
        line_text = lines[cur_line]
        for c in range(cur_col, len(line_text)):
            ch = line_text[c]
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    sig_end_line = cur_line
                    sig_end_col = c
                    break
        if sig_end_col >= 0:
            break
        cur_line += 1
        cur_col = 0
    if sig_end_col < 0:
        return (False, "signals_used ] not found")

    # Append ",\"borrow_ok\"" before the closing ]
    close_line_text = lines[sig_end_line]
    before = close_line_text[:sig_end_col]
    after = close_line_text[sig_end_col:]
    # detect whether to prepend a comma (yes if the char immediately before ] is not '[' and not already a comma)
    insert_str = ', "borrow_ok"'
    # strip trailing whitespace before checking
    stripped_before = before.rstrip()
    if stripped_before.endswith("[") or stripped_before.endswith(","):
        insert_str = '"borrow_ok"' if stripped_before.endswith(",") else '"borrow_ok"'
        if stripped_before.endswith("["):
            # empty list -- insert without comma
            insert_str = '"borrow_ok"'
        # comma case: just the string
    lines[sig_end_line] = before + insert_str + after

    return (True, f"refactored at lines {fires_close_idx+1}..{sig_end_line+1}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chunk", choices=["first", "second", "all"], required=True,
                   help="first = B740 (#1-#26); second = B741 (#27-#51); all = both")
    p.add_argument("--dry-run", action="store_true", help="don't write the file")
    args = p.parse_args()

    if args.chunk == "first":
        targets = FIRST_CHUNK
    elif args.chunk == "second":
        targets = SECOND_CHUNK
    else:
        targets = ALL_51

    src = SCREENER_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    n_lines_before = len(src)

    changed_count = 0
    skipped_count = 0
    report = []
    for name in targets:
        ok, note = transform_strategy(src, name)
        if ok:
            changed_count += 1
            report.append(f"  [OK]   {name}  -- {note}")
        else:
            skipped_count += 1
            report.append(f"  [SKIP] {name}  -- {note}")

    print(f"B718b refactor pass: chunk={args.chunk}  targets={len(targets)}")
    print(f"  changed: {changed_count}  skipped: {skipped_count}")
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
