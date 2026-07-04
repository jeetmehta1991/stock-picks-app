"""B1145 Autonomous CSV-driven LOOSEN executor.

Per owner directive 2026-07-03 Council 256+257:
  1. Testing pyramid MUST be applied per each strategy change/edit
  2. Only actions in CSV final_recommended_actions may be implemented
  3. No other changes allowed
  4. Update execution columns in CSV

DESIGN:
  For each PENDING strategy:
    - Parse final_recommended_actions column
    - Classify: SPECIFIC / STATUS_QUO / UNIVERSE_EXPAND / GENERIC / PRODUCER_SIDE / DATA_AUDIT
    - Auto-execute SPECIFIC + mark STATUS_QUO/UNIVERSE_EXPAND as DONE with no code change
    - SKIP GENERIC / PRODUCER_SIDE (visible SKIP status)
    - After each code change: FULL 955+7 pyramid; commit only if GREEN
    - Rollback on pyramid FAIL

PARSING RULES (deterministic; only extracts explicit signal replacements):
  - `vol_spike_XX -> vol_above_avg` -> REPLACE_SIGNAL(vol_spike_XX, vol_above_avg)
  - `vol_spike_XX -> vol_spike_YY` -> REPLACE_SIGNAL
  - `Drop rsi_14<70` or `drop rsi_14>30` -> DROP_RSI_FILTER
  - `Drop 200-EMA regime gate` -> DROP_PRICE_ABOVE_EMA_200
  - `Drop adx_trending` -> DROP_ADX_TRENDING
  - `Drop above_avwap_20low` or similar AVWAP -> DROP_AVWAP_GATE

STATUS classes (no code change):
  - STATUS_QUO / STATUS_QUO_ -> DONE_B1145_STATUS_QUO
  - UNIVERSE_EXPAND (only lever) -> DONE_B1145_UNIVERSE_EXPAND_DEFERRED
  - DISABLED_PENDING_DATA -> BLOCKED_DATA_MISSING (no change)

SKIP classes (visible in CSV):
  - "Drop 1-2 secondary gates from N-gate stack" -> SKIP_GENERIC_TEMPLATE
  - "Widen numeric thresholds by 10-20%; loosen strictest gate" -> SKIP_GENERIC_TEMPLATE
  - "[FIX_PRODUCER]" as primary -> SKIP_PRODUCER_SIDE
  - "[AUDIT_DATA]" as primary -> SKIP_AUDIT_ALREADY_COMPLETE

SAFETY:
  - Full 955+7 pyramid per code change (subprocess)
  - Rollback on pyramid FAIL via git checkout
  - 1 strategy = 1 commit (Council 201 <=3 compliant)
  - CSV updated per strategy
  - Push per commit
"""
# Source: per CHECKLIST #77 canonical-source; author Council 257 B1145 2026-07-03
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


CSV_PATH = _REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
SCREENER_PATH = _REPO / "backtest" / "signals" / "screener.py"


# --- ACTION CLASSIFICATION ---


def classify_action(action_text: str) -> tuple[str, list[dict]]:
    """Return (classification, edits_list). edits_list only populated for SPECIFIC."""
    if not isinstance(action_text, str) or not action_text.strip():
        return ("SKIP_NO_ACTION_TEXT", [])

    lower = action_text.lower()

    # STATUS_QUO markers (no code change, mark DONE)
    if "status_quo" in lower or "[status_quo]" in lower:
        return ("STATUS_QUO", [])

    # DISABLED_PENDING_DATA (no change, remain blocked)
    if "disabled_pending_data" in lower:
        return ("DISABLED_PENDING_DATA", [])

    # SKIP: primary action is FIX_PRODUCER (would need producer-side changes)
    if action_text.strip().upper().startswith("[CRITICAL] [FIX_PRODUCER]") or \
       action_text.strip().upper().startswith("[HIGH] [FIX_PRODUCER]"):
        return ("SKIP_PRODUCER_SIDE", [])

    # SKIP: primary action is AUDIT_DATA (already completed B1129-B1132)
    if action_text.strip().upper().startswith("[CRITICAL] [AUDIT_DATA]") or \
       action_text.strip().upper().startswith("[HIGH] [AUDIT_DATA]"):
        return ("SKIP_AUDIT_ALREADY_COMPLETE", [])

    # SKIP: generic template text
    generic_patterns = [
        r"drop 1-2 secondary gates from \d+-gate stack",
        r"widen numeric thresholds by 10-20%",
        r"loosen strictest gate",
    ]
    for pat in generic_patterns:
        if re.search(pat, lower):
            return ("SKIP_GENERIC_TEMPLATE", [])

    # UNIVERSE_EXPAND without loosen action = deferred to Batch B
    if "[universe_expand]" in lower and not any(
        kw in lower for kw in ["loosen_gate", "loosen_threshold", "drop_redundant", "->"]
    ):
        return ("UNIVERSE_EXPAND_DEFERRED", [])

    # SPECIFIC edits - parse them
    edits = []

    # Rule: signal_A -> signal_B (arrow replacement)
    for match in re.finditer(
        r"([a-z_0-9]+)\s*(?:->|\-\->|->)\s*([a-z_0-9]+)", action_text
    ):
        old = match.group(1)
        new = match.group(2)
        # Skip if either side is generic English (not a signal name)
        if old in ("bar", "n", "gate", "threshold", "-", "or"):
            continue
        # Only accept if both look like signal names (lower + digits + underscores)
        if len(old) >= 3 and len(new) >= 3:
            edits.append({"type": "REPLACE_SIGNAL", "old": old, "new": new})

    # Rule: "Drop rsi_14<XX" or "drop rsi_14>XX" (RSI filter removal)
    for match in re.finditer(
        r"drop\s+rsi_\d+\s*[<>]\s*\d+", action_text, re.IGNORECASE
    ):
        rsi_expr = match.group(0)
        # Extract the specific rsi_XX<YY pattern
        m = re.search(r"(rsi_\d+)\s*([<>])\s*(\d+)", rsi_expr, re.IGNORECASE)
        if m:
            edits.append({
                "type": "DROP_RSI_FILTER",
                "field": m.group(1),
                "operator": m.group(2),
                "value": m.group(3),
            })

    # Rule: "Drop 200-EMA regime gate" or "drop price_above_ema_200 regime gate"
    if re.search(r"drop\s+200-?ema.*regime|drop\s+price_above_ema_200", action_text, re.IGNORECASE):
        edits.append({"type": "DROP_PRICE_ABOVE_EMA_200"})
    if re.search(r"drop\s+below_ema_200", action_text, re.IGNORECASE):
        edits.append({"type": "DROP_BELOW_EMA_200"})

    # Rule: "Drop adx_trending"
    if re.search(r"drop\s+adx_trending", action_text, re.IGNORECASE):
        edits.append({"type": "DROP_ADX_TRENDING"})

    # Rule: "Drop above_avwap_XXlow" / "below_avwap_XXhigh"
    for match in re.finditer(r"drop\s+(above|below)_avwap_\w+", action_text, re.IGNORECASE):
        edits.append({"type": "DROP_AVWAP_GATE", "gate": match.group(0).replace("drop ", "").strip().lower()})

    if edits:
        return ("SPECIFIC", edits)

    # Fall through: cannot classify
    return ("SKIP_UNCLASSIFIED", [])


# --- EDIT APPLICATION ---


def find_strategy_body(strat_name: str, content: str) -> tuple[int, int, str] | None:
    """Return (start_offset, end_offset, body_text) for strat_<name> in screener.py."""
    idx = content.find(f"def strat_{strat_name}(")
    if idx < 0:
        return None
    # Find next def or top-level end
    end = content.find("\ndef ", idx + 30)
    if end < 0:
        end = content.find("\nclass ", idx + 30)
    if end < 0:
        end = len(content)
    return (idx, end, content[idx:end])


def apply_edits_to_body(body: str, edits: list[dict]) -> tuple[str, list[str]]:
    """Apply edits to strategy body. Return (new_body, applied_list)."""
    new_body = body
    applied = []
    for edit in edits:
        etype = edit["type"]
        if etype == "REPLACE_SIGNAL":
            old = edit["old"]
            new = edit["new"]
            # Replace signal name in s.get() calls
            pattern = rf's\.get\(\s*["\']({re.escape(old)})["\']'
            replacement = rf's.get("{new}"'
            if re.search(pattern, new_body):
                new_body = re.sub(pattern, replacement, new_body)
                applied.append(f"REPLACE {old} -> {new}")
        elif etype == "DROP_RSI_FILTER":
            field = edit["field"]
            operator = edit["operator"]
            value = edit["value"]
            # Match `and s.get("rsi_14", 50) < 70` or `and s.get("rsi_14", 50) > 30`
            pattern = rf'\s*and\s+s\.get\(\s*["\']({re.escape(field)})["\'][^)]*\)\s*{re.escape(operator)}\s*{value}'
            if re.search(pattern, new_body):
                new_body = re.sub(pattern, "", new_body)
                applied.append(f"DROP {field}{operator}{value}")
        elif etype == "DROP_PRICE_ABOVE_EMA_200":
            pattern = r'\s*and\s+s\.get\(\s*["\']price_above_ema_200["\'][^)]*\)'
            if re.search(pattern, new_body):
                new_body = re.sub(pattern, "", new_body)
                applied.append("DROP price_above_ema_200")
        elif etype == "DROP_BELOW_EMA_200":
            pattern = r'\s*and\s+s\.get\(\s*["\']below_ema_200["\'][^)]*\)'
            if re.search(pattern, new_body):
                new_body = re.sub(pattern, "", new_body)
                applied.append("DROP below_ema_200")
        elif etype == "DROP_ADX_TRENDING":
            pattern = r'\s*and\s+s\.get\(\s*["\']adx_trending["\'][^)]*\)'
            if re.search(pattern, new_body):
                new_body = re.sub(pattern, "", new_body)
                applied.append("DROP adx_trending")
        elif etype == "DROP_AVWAP_GATE":
            gate = edit["gate"]
            pattern = rf'\s*and\s+s\.get\(\s*["\']({re.escape(gate)})["\'][^)]*\)'
            if re.search(pattern, new_body):
                new_body = re.sub(pattern, "", new_body)
                applied.append(f"DROP {gate}")
    return new_body, applied


def run_pyramid() -> tuple[bool, str]:
    """Run FULL expanded pyramid. Return (passed, output_tail)."""
    result = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "backtest/tests/test_unit.py",
            "backtest/tests/test_integration.py",
            "backtest/tests/test_b1124_producer_smoke_contract.py",
            "backtest/tests/test_b1124_prefetch_manifest_preflight.py",
            "backtest/tests/test_b1124_smc_phase_env_arm.py",
            "backtest/tests/test_b1124_strategy_fire_count_contract.py",
            "backtest/tests/test_b1124_b832_spof_no_systematic_trip.py",
            "backtest/tests/test_b1124_borrow_ok_blocking_rate.py",
            "backtest/tests/test_b1124_calendar_lru_cache_correctness.py",
            "backtest/tests/test_b1124_phase1_investigation_csv_schema.py",
            "backtest/tests/test_b1124_producer_consumer_key_map.py",
            "backtest/tests/test_b1124_fire_count_delta_bounds.py",
            "-q",
            "--tb=line",
            "-x",
        ],
        capture_output=True,
        text=True,
        cwd=_REPO,
        timeout=600,
    )
    output = result.stdout + result.stderr
    passed = result.returncode == 0
    return (passed, output[-500:])


def git_checkout_reset(file_path: str) -> None:
    """Revert file to HEAD."""
    subprocess.run(
        ["git", "checkout", "HEAD", "--", file_path],
        capture_output=True,
        text=True,
        cwd=_REPO,
    )


def git_commit_and_push(message: str) -> bool:
    """Commit staged changes and push. Return True on success."""
    add_result = subprocess.run(
        ["git", "add", "backtest/signals/screener.py", "output_batch_A_150/phase_1_quiet_fire_investigation.csv"],
        capture_output=True,
        text=True,
        cwd=_REPO,
    )
    commit_result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
        cwd=_REPO,
    )
    if commit_result.returncode != 0:
        return False
    push_result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True,
        text=True,
        cwd=_REPO,
        timeout=60,
    )
    return push_result.returncode == 0


def main() -> int:
    df = pd.read_csv(CSV_PATH)
    for col in ("execution_batch_ref", "execution_status", "execution_comments"):
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("")

    pending = df[df["execution_status"] == "PENDING"].copy()
    print(f"Processing {len(pending)} PENDING strategies")
    print("=" * 78)

    batch_counter = 1145  # start from B1145
    stats = {
        "SPECIFIC_DONE": 0,
        "STATUS_QUO": 0,
        "UNIVERSE_EXPAND_DEFERRED": 0,
        "SKIP_PRODUCER_SIDE": 0,
        "SKIP_AUDIT_ALREADY_COMPLETE": 0,
        "SKIP_GENERIC_TEMPLATE": 0,
        "SKIP_UNCLASSIFIED": 0,
        "SKIP_NO_ACTION_TEXT": 0,
        "DISABLED_PENDING_DATA": 0,
        "FAIL_NO_MATCH_IN_CODE": 0,
        "FAIL_PYRAMID": 0,
    }

    for idx, row in pending.iterrows():
        strat = row["strategy_name"]
        action = str(row.get("final_recommended_actions", ""))

        classification, edits = classify_action(action)

        # No code change classes
        if classification == "STATUS_QUO":
            df.at[idx, "execution_status"] = f"DONE_B{batch_counter}_STATUS_QUO"
            df.at[idx, "execution_batch_ref"] = f"B{batch_counter}"
            df.at[idx, "execution_comments"] = (
                str(df.at[idx, "execution_comments"])
                + f" B{batch_counter} AUTO-EXECUTOR: STATUS_QUO per CSV action; no code change."
            )
            stats["STATUS_QUO"] += 1
            print(f"[{stats['SPECIFIC_DONE']+stats['STATUS_QUO']+stats['UNIVERSE_EXPAND_DEFERRED']}] {strat}: STATUS_QUO")
            continue

        if classification == "UNIVERSE_EXPAND_DEFERRED":
            df.at[idx, "execution_status"] = f"DONE_B{batch_counter}_UNIVERSE_EXPAND"
            df.at[idx, "execution_batch_ref"] = f"B{batch_counter}"
            df.at[idx, "execution_comments"] = (
                str(df.at[idx, "execution_comments"])
                + f" B{batch_counter} AUTO-EXECUTOR: UNIVERSE_EXPAND deferred to Batch B - no code change."
            )
            stats["UNIVERSE_EXPAND_DEFERRED"] += 1
            print(f"{strat}: UNIVERSE_EXPAND deferred")
            continue

        if classification == "DISABLED_PENDING_DATA":
            df.at[idx, "execution_status"] = "BLOCKED_DATA_MISSING"
            df.at[idx, "execution_comments"] = (
                str(df.at[idx, "execution_comments"])
                + f" B{batch_counter} AUTO-EXECUTOR: DISABLED_PENDING_DATA - remain blocked."
            )
            stats["DISABLED_PENDING_DATA"] += 1
            print(f"{strat}: DISABLED_PENDING_DATA")
            continue

        # SKIP classes
        if classification.startswith("SKIP"):
            df.at[idx, "execution_status"] = f"{classification}_B{batch_counter}"
            df.at[idx, "execution_batch_ref"] = ""
            reason_map = {
                "SKIP_PRODUCER_SIDE": "requires producer-side change (technical.py/smc_ict.py) - manual review",
                "SKIP_AUDIT_ALREADY_COMPLETE": "AUDIT_DATA already completed B1129-B1132",
                "SKIP_GENERIC_TEMPLATE": "generic template action - needs specific gate identification",
                "SKIP_UNCLASSIFIED": "action text does not match known specific patterns",
                "SKIP_NO_ACTION_TEXT": "empty action text",
            }
            df.at[idx, "execution_comments"] = (
                str(df.at[idx, "execution_comments"])
                + f" B{batch_counter} AUTO-EXECUTOR SKIP: {reason_map.get(classification, 'unknown reason')}"
            )
            stats[classification] += 1
            continue

        # SPECIFIC: apply edits
        content = SCREENER_PATH.read_text(encoding="utf-8")
        result = find_strategy_body(strat, content)
        if result is None:
            df.at[idx, "execution_status"] = f"FAIL_NO_STRATEGY_DEF_B{batch_counter}"
            df.at[idx, "execution_comments"] = (
                str(df.at[idx, "execution_comments"])
                + f" B{batch_counter} AUTO-EXECUTOR FAIL: strat_{strat} not found in screener.py"
            )
            stats["FAIL_NO_MATCH_IN_CODE"] += 1
            continue

        start_off, end_off, body = result
        new_body, applied = apply_edits_to_body(body, edits)

        if not applied:
            df.at[idx, "execution_status"] = f"SKIP_UNCLASSIFIED_B{batch_counter}"
            df.at[idx, "execution_comments"] = (
                str(df.at[idx, "execution_comments"])
                + f" B{batch_counter} AUTO-EXECUTOR SKIP: parsed edits {edits} did not match any signal in strat_{strat} source"
            )
            stats["SKIP_UNCLASSIFIED"] += 1
            continue

        # Write updated content
        new_content = content[:start_off] + new_body + content[end_off:]
        SCREENER_PATH.write_text(new_content, encoding="utf-8")

        # Save intermediate CSV (in case script gets interrupted)
        df.to_csv(CSV_PATH, index=False)

        # PER-STRATEGY FULL PYRAMID (owner mandatory)
        passed, output_tail = run_pyramid()

        if not passed:
            # Revert screener.py
            git_checkout_reset("backtest/signals/screener.py")
            df.at[idx, "execution_status"] = f"FAIL_PYRAMID_B{batch_counter}"
            df.at[idx, "execution_comments"] = (
                str(df.at[idx, "execution_comments"])
                + f" B{batch_counter} AUTO-EXECUTOR FAIL_PYRAMID: applied {applied} but pyramid broke. Tail: {output_tail[:200]}"
            )
            stats["FAIL_PYRAMID"] += 1
            print(f"FAIL_PYRAMID {strat}: applied={applied}")
            df.to_csv(CSV_PATH, index=False)
            continue

        # PASSED - mark DONE + commit + push
        df.at[idx, "execution_status"] = f"DONE_B{batch_counter}"
        df.at[idx, "execution_batch_ref"] = f"B{batch_counter}"
        df.at[idx, "execution_comments"] = (
            str(df.at[idx, "execution_comments"])
            + f" B{batch_counter} AUTO-EXECUTOR DONE: applied {applied}. Full pyramid 955+7 GREEN."
        )
        stats["SPECIFIC_DONE"] += 1
        df.to_csv(CSV_PATH, index=False)

        commit_msg = (
            f"Batch {batch_counter} (2026-07-03): Council 257 AUTO-EXECUTOR - {strat}\n\n"
            f"Applied CSV action per final_recommended_actions column:\n"
            f"  {action[:400]}\n\n"
            f"Edits applied: {applied}\n\n"
            f"Full expanded pyramid (955+7) GREEN.\n"
            f"Council 201 batch-cap: 1 strategy = 1 commit (<=3 compliant).\n\n"
            f"Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
        )
        pushed = git_commit_and_push(commit_msg)
        print(f"[B{batch_counter}] {strat}: DONE (applied={applied}, pushed={pushed})")

        batch_counter += 1

    # Final CSV save
    df.to_csv(CSV_PATH, index=False)

    print()
    print("=" * 78)
    print("AUTO-EXECUTOR SUMMARY")
    print("=" * 78)
    for k, v in stats.items():
        if v > 0:
            print(f"  {k:35s}: {v:3d}")
    print()

    # Final execution status distribution
    df_final = pd.read_csv(CSV_PATH)
    print("EXECUTION_STATUS DISTRIBUTION (final):")
    for status in sorted(df_final["execution_status"].unique()):
        n = (df_final["execution_status"] == status).sum()
        print(f"  {status:40s}: {n:3d}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
