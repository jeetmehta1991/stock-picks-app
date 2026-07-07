"""B1169 Council 274: Fix change_from_original + updated_producer_signals columns.

Per owner directive 2026-07-04:
  1. change_from_original was FALSE for 48 rows (stamped 'threshold widened'
     without checking git diff). Fix: check git log for actual code change
     to that strategy in the batch_ref commit range.

  2. updated_producer_signals was CSV-list format. Change to logical formula
     showing AND/OR gate structure. Example:
       BEFORE: 'bearish_engulfing,below_prev_low,recent_blowoff_at_r3,shooting_star,vol_below_avg'
       AFTER:  'recent_blowoff_at_r3 AND vol_below_avg AND (bearish_engulfing OR shooting_star OR below_prev_low)'

  3. change_from_original must specify old->new numeric where a threshold
     changed (e.g., 'rsi_14 <40 -> <45') not just 'threshold widened'.
"""
# Source: per CHECKLIST #77 canonical-source; Council 274 B1169 2026-07-04
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd

CSV_PATH = _REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
SCREENER_PATH = _REPO / "backtest" / "signals" / "screener.py"


def get_strategy_body(strat_name: str, content: str) -> str | None:
    """Return function body for strat_<name> or None."""
    idx = content.find(f"def strat_{strat_name}(")
    if idx < 0:
        return None
    end = content.find("\ndef ", idx + 30)
    if end < 0:
        end = len(content)
    return content[idx:end]


def extract_logical_formula(body: str) -> str:
    """Extract fires-logic and return logical formula representation.

    Parses the fires = (...) construct to produce:
      SignalA AND SignalB AND (SignalC OR SignalD) AND borrow_ok
    """
    if not body:
        return ""

    def _extract_paren_expr(text, start):
        """Extract from open-paren at start through matching close-paren."""
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return text[start:]

    # Try patterns in priority:
    # 1. fires = (...)  -- most common
    # 2. fl = (...) ... fs = (...) -- dual LONG/SHORT (e.g., pivot_s2_bounce)
    # 3. single-line return _strat(bool(...), ...) -- inline
    exprs = []
    for m in re.finditer(r'\b(fires|fl|fs)\s*=\s*\(', body):
        var = m.group(1)
        e = _extract_paren_expr(body, m.end() - 1)
        exprs.append((var, e))

    if not exprs:
        # Fallback: layered pattern (layer1 = (...) ... fires = layer1 and layer2 ...)
        # Try to extract each layerN or named intermediate
        layer_exprs = {}
        for m in re.finditer(r'\b([a-z][a-z_0-9]*_(?:positioning|catalyst|confirmation|layer\d+|trigger|filter))\s*=\s*\(', body):
            name = m.group(1)
            e = _extract_paren_expr(body, m.end() - 1)
            layer_exprs[name] = e
        if layer_exprs:
            # Look for fires = <combination>
            fires_line = re.search(r'fires\s*=\s*([^\n#]+)', body)
            if fires_line:
                combined = fires_line.group(1).strip()
                # Substitute each layer name with its expression
                for name, e in layer_exprs.items():
                    combined = combined.replace(name, e)
                exprs = [("fires", combined)]

    if not exprs:
        return ""

    # Compose display: single 'fires', or 'LONG: ... | SHORT: ...' for fl/fs
    if len(exprs) == 1 and exprs[0][0] == "fires":
        expr = exprs[0][1]
    else:
        by_var = {v: e for v, e in exprs}
        parts_out = []
        if "fl" in by_var:
            parts_out.append(f"LONG: {by_var['fl']}")
        if "fs" in by_var:
            parts_out.append(f"SHORT: {by_var['fs']}")
        if "fires" in by_var:
            parts_out.append(f"FIRES: {by_var['fires']}")
        expr = " | ".join(parts_out)

    # Normalize: strip Python comments
    expr = re.sub(r'#[^\n]*', '', expr)
    # Collapse whitespace
    expr = ' '.join(expr.split())

    # Replace s.get("key") with just "key"
    expr = re.sub(r's\.get\(\s*["\']([a-z_0-9]+)["\'](?:\s*,\s*[^)]+)?\)', r'\1', expr)
    # Replace s["key"] with just "key"
    expr = re.sub(r's\[\s*["\']([a-z_0-9]+)["\']\s*\]', r'\1', expr)
    # Replace "not X" with "NOT X"
    expr = re.sub(r'\bnot\s+', 'NOT ', expr)
    # Replace helper calls _short_borrow_trap_active(s) -> short_borrow_trap
    expr = re.sub(r'_short_borrow_trap_active\(s\)', 'short_borrow_trap', expr)
    # Replace inequalities: rsi_14 < 40 -> rsi_14<40
    expr = re.sub(r'\s*(<=?|>=?|==)\s*', r'\1', expr)
    # Replace "and" with "AND", "or" with "OR"
    expr = re.sub(r'\band\b', 'AND', expr)
    expr = re.sub(r'\bor\b', 'OR', expr)

    return expr.strip()


def git_show_screener_at(commit: str) -> str | None:
    """Return screener.py content at commit, or None if fails."""
    try:
        r = subprocess.run(
            ["git", "show", f"{commit}:backtest/signals/screener.py"],
            capture_output=True, text=True, timeout=30, cwd=str(_REPO),
        )
        if r.returncode == 0:
            return r.stdout
    except Exception:
        pass
    return None


def find_batch_commits(batch_ref: str) -> list[str]:
    """Return ALL commit hashes matching Batch <NNNN> (newest first)."""
    if not batch_ref or not batch_ref.startswith("B"):
        return []
    n = batch_ref[1:].split("_")[0]  # B1145 -> 1145; B1145_STATUS_QUO -> 1145
    try:
        r = subprocess.run(
            ["git", "log", "--all", "--format=%H", "--grep", f"Batch {n} "],
            capture_output=True, text=True, timeout=30, cwd=str(_REPO),
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().split("\n")
    except Exception:
        pass
    return []


_PRODUCER_FILES = (
    "backtest/signals/technical.py",
    "backtest/signals/chart_patterns.py",
    "backtest/signals/smc_ict.py",
    "backtest/signals/pead.py",
    "backtest/signals/calendar_effects.py",
    "backtest/signals/smart_money.py",
    "backtest/data/universe.py",
    "backtest/data/fetcher.py",
)


def get_producer_files_touched(batch_ref: str) -> list[str]:
    """Return list of producer files (non-screener) touched by any commit in batch."""
    commits = find_batch_commits(batch_ref)
    touched = set()
    for c in commits:
        try:
            r = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", c],
                capture_output=True, text=True, timeout=10, cwd=str(_REPO),
            )
            if r.returncode == 0:
                for line in r.stdout.strip().split("\n"):
                    line = line.strip()
                    if line in _PRODUCER_FILES:
                        touched.add(Path(line).name)
        except Exception:
            pass
    return sorted(touched)


def find_batch_commit_for_strategy(batch_ref: str, strat_name: str) -> str | None:
    """Return the commit within the batch group that actually modified strat_<name>."""
    commits = find_batch_commits(batch_ref)
    for c in commits:
        changed, _ = strategy_changed_at_commit(strat_name, c)
        if changed:
            return c
    # None found: return first commit as fallback so caller sees "no change"
    return commits[0] if commits else None


def strategy_changed_at_commit(strat_name: str, commit: str) -> tuple[bool, str]:
    """Return (changed, diff_summary) for whether strat_<name> body changed at commit.

    diff_summary is a short human-readable delta (e.g., 'rsi_14 <40 -> <45').
    """
    if not commit:
        return False, ""

    # Get before/after content
    parent = commit + "^"
    before = git_show_screener_at(parent)
    after = git_show_screener_at(commit)

    if before is None or after is None:
        return False, ""

    body_before = get_strategy_body(strat_name, before) or ""
    body_after = get_strategy_body(strat_name, after) or ""

    if body_before == body_after:
        return False, ""

    # There IS a change. Try to summarize it.
    # Extract thresholds pre/post
    # Use (key, comparison_op_direction) as key so LONG (<) and SHORT (>) are separate.
    def get_thresholds(body):
        d = {}
        for m in re.finditer(r's\.get\(\s*["\']([a-z_0-9]+)["\'][^)]*\)\s*(<=?|>=?|==)\s*(\d+\.?\d*)', body):
            k = m.group(1)
            op = m.group(2)
            val = m.group(3)
            # Group by direction: < / <= (LONG) vs > / >= (SHORT)
            direction = "lt" if op.startswith("<") else "gt" if op.startswith(">") else "eq"
            d[(k, direction)] = f"{op}{val}"
        for m in re.finditer(r'\brsi_(\d+)\s*(<=?|>=?)\s*(\d+)', body):
            k = f"rsi_{m.group(1)}"
            op = m.group(2)
            val = m.group(3)
            direction = "lt" if op.startswith("<") else "gt"
            d.setdefault((k, direction), f"{op}{val}")
        return d

    def get_signals(body):
        s = set(re.findall(r's\.get\(\s*["\']([a-z_0-9]+)["\']', body))
        return s

    t_before = get_thresholds(body_before)
    t_after = get_thresholds(body_after)
    s_before = get_signals(body_before)
    s_after = get_signals(body_after)

    parts = []
    # Threshold changes - keys are now (name, direction) tuples
    for k in sorted(set(t_before) | set(t_after)):
        b = t_before.get(k, "")
        a = t_after.get(k, "")
        label = k[0]  # signal name
        if b != a and b and a:
            parts.append(f"{label} {b}->{a}")
        elif not b and a:
            parts.append(f"{label} added ({a})")
        elif b and not a:
            parts.append(f"{label} removed (was {b})")

    # Signal set changes
    added = sorted(s_after - s_before)
    removed = sorted(s_before - s_after)
    if added:
        parts.append(f"added: {', '.join(added[:5])}" + ("..." if len(added) > 5 else ""))
    if removed:
        parts.append(f"removed: {', '.join(removed[:5])}" + ("..." if len(removed) > 5 else ""))

    return True, "; ".join(parts) if parts else "structural edit (see source diff)"


def main() -> int:
    df = pd.read_csv(CSV_PATH)

    with open(SCREENER_PATH) as f:
        current_src = f.read()

    updated_col = []
    change_col = []

    n_fixed = 0
    n_verified_change = 0
    n_status_quo = 0

    print("Processing 192 strategies...")
    for idx, row in df.iterrows():
        strat = str(row["strategy_name"])
        status = str(row.get("execution_status", ""))
        batch_ref = str(row.get("execution_batch_ref", ""))

        # Extract current logical formula
        body = get_strategy_body(strat, current_src)
        formula = extract_logical_formula(body) if body else ""
        updated_col.append(formula)

        # Determine change_from_original
        if not body:
            change_col.append("strategy definition not found in screener.py")
            continue

        # If status indicates admin cleanup / no code change, don't check git
        if any(x in status for x in ("STATUS_QUO", "UNIVERSE_EXPAND", "AUDIT_COMPLETE",
                                     "SECONDARY", "PRODUCER_CASCADE", "MARGINAL_NO_LOOSEN")):
            # Verify no code change actually happened
            commit = find_batch_commit_for_strategy(batch_ref, strat) if batch_ref else None
            if commit:
                changed, summary = strategy_changed_at_commit(strat, commit)
                if changed:
                    change_col.append(f"UNEXPECTED code change in {batch_ref}: {summary}")
                else:
                    # Truly no code change
                    if "STATUS_QUO" in status:
                        change_col.append("no code change; recommendation was keep-as-is")
                    elif "UNIVERSE_EXPAND" in status:
                        change_col.append("no code change; UNIVERSE_EXPAND deferred to Batch B")
                    elif "AUDIT_COMPLETE" in status:
                        change_col.append("no code change; audit-only directive fulfilled")
                    elif "SECONDARY" in status:
                        change_col.append("no primary code change; side-effect of primary batch")
                    elif "PRODUCER_CASCADE" in status:
                        change_col.append("no consumer code change; upstream producer edited")
                    elif "MARGINAL_NO_LOOSEN" in status:
                        change_col.append("no code change; MARGINAL tier per CHECKLIST #148")
                    else:
                        change_col.append("no code change")
                    n_status_quo += 1
            else:
                change_col.append(f"no code change (batch {batch_ref} not resolved to commit)")
            continue

        if status.startswith("PENDING_OWNER_APPROVED_REVERT"):
            change_col.append("reverted to pre-invention state per owner directive B1168")
            continue

        if status.startswith("SKIP_"):
            change_col.append("no code change; awaits owner-approved specific action per CHECKLIST #150")
            continue

        if status.startswith("BLOCKED_"):
            change_col.append("no code change; blocked on Sprint 5 data dependency")
            continue

        if status.startswith("FAIL_"):
            change_col.append("attempted edit reverted after pyramid FAIL; needs fixture update")
            continue

        # DONE_B* without qualifier - should have actual code change
        # B1206 (2026-07-07 Council 279 Fix #2): whitelist known non-strategy-body batches
        # to avoid false-positive NO GIT-VERIFIED CHANGE flags.
        # - B1180: modified _cached_calendar_signals decorator (not strategy body) for
        #   totm_long / pre_holiday_long / halloween_seasonal_long (calendar cache fix)
        # - B1186: SMC producer probe (no code change; documentation-only)
        # - B1187: DTC threshold accept (no code change; owner decision)
        DECORATOR_CASCADE_BATCHES = {
            "B1180": "screener.py lru_cache decorator (calendar cache maxsize fix)",
            "B1186": "no code change - SMC producer real-market probe (verification only)",
            "B1187": "no code change - DTC threshold owner decision (accept current 5.0)",
        }
        commit = find_batch_commit_for_strategy(batch_ref, strat) if batch_ref else None
        if commit:
            changed, summary = strategy_changed_at_commit(strat, commit)
            if changed:
                change_col.append(f"{batch_ref}: {summary}")
                n_verified_change += 1
            else:
                # Check if batch modified any producer file (upstream cascade)
                producer_files = get_producer_files_touched(batch_ref)
                if producer_files:
                    change_col.append(
                        f"upstream producer change in {batch_ref} ({', '.join(producer_files)}); "
                        f"consumer gate list unchanged"
                    )
                elif batch_ref in DECORATOR_CASCADE_BATCHES:
                    # B1206: whitelisted non-body change - not a miss
                    change_col.append(
                        f"{batch_ref}: {DECORATOR_CASCADE_BATCHES[batch_ref]}"
                    )
                else:
                    change_col.append(f"NO GIT-VERIFIED CHANGE at {batch_ref} despite DONE status - INVESTIGATE")
                    n_fixed += 1
        else:
            change_col.append(f"batch {batch_ref} commit not found")

    df["updated_producer_signals"] = updated_col
    df["change_from_original"] = change_col
    df.to_csv(CSV_PATH, index=False)

    print(f"\nDONE. Fixed columns for 192 strategies.")
    print(f"  Verified real code changes: {n_verified_change}")
    print(f"  DONE_B* without verified change (FLAGGED): {n_fixed}")
    print(f"  Status-quo/admin/no-code-change: {n_status_quo}")

    # Sample output
    print("\n=== Sample updated_producer_signals + change_from_original ===")
    for strat in ["pivot_r3_blowoff_short", "cpr_narrow_momentum", "squeeze_setup_long",
                  "pivot_s2_bounce", "camarilla_s3_bounce"]:
        r = df[df["strategy_name"] == strat]
        if not r.empty:
            print(f"\n{strat}:")
            print(f"  UPDATED_FORMULA: {r['updated_producer_signals'].values[0][:200]}")
            print(f"  CHANGE_FROM_ORIG: {r['change_from_original'].values[0][:200]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
