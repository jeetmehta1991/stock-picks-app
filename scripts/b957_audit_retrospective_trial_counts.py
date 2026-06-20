# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 per CHECKLIST #77 + Council 61+62 verdict.
"""B957 (2026-06-20): Phase P1 batch 17 - retrospective trial-count audit.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 61+62 UNANIMOUS verdict
# per owner directive 2026-06-20 'C then B. When i say parameter optimization
# i mean two things: Exit parameter or gate optimizations, Strategy gate
# optimizations (similar to stage 4). Both of these will help improve
# performance of strategies in r5. The combination of these will help
# determine winner extraction post r5. Council this. Be thorough.' per
# CHECKLIST #77.

PURPOSE
-------
Pre-R5 retrospective trial-count audit per Council 61 critical finding
+ Council 62 unconditional ship verdict.

PROBLEM (Council 61 Quant + 3 advisors converged):
  DEC #5 set DSR N = 5,694 (219 strategies x 26 exits).
  BUT Stage 4 walks edited gates across approx221 strategies over 100+
  batches (B500-B956). Each gate edit was a TRIAL against the same
  2020-2026 data.
  The roster you have today is the SURVIVOR of an UNBUDGETED SEARCH.
  Real N_effective likely 10,000-50,000+, not 5,694.
  DSR >=0.95 gate calibrated for N=5,694 may be unreachable BEFORE
  R5 runs.

METHODOLOGY (Council 62 Executor spec):
  1. Parse git log B500-B956 for every commit (approx457 batches)
  2. Per-commit, classify what was changed:
     - new strategy registered (gates not yet tuned)
     - strategy deleted (no longer in trial budget but counted as
       earlier trials)
     - gate added/removed (trial)
     - threshold changed (trial)
     - regime affinity edit (trial)
     - STATE -> EVENT conversion (trial)
     - producer rewrite (trial)
  3. Per-strategy trial count
  4. Cumulative N_effective vs DEC #5 baseline 5,694
  5. DSR recalibration estimate

NOT a verdict driver. Read-only measurement. Output informs B (Phase 6.5)
design decisions.

NO MUTATION. NO schema change. NO param change.
"""
from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

# Batch trial classification heuristics (commit message keyword -> trial type)
TRIAL_KEYWORDS = {
    "new_strategy": [
        re.compile(r"NEW_STRATEGY|Class 7 NEW|class 7 new|wired.*new strat|added.*strat_", re.IGNORECASE),
        re.compile(r"\+1\s+strategy|\+\d+\s+strategies", re.IGNORECASE),
    ],
    "strategy_deletion": [
        re.compile(r"DELETED?|delete\s+strat_|-\s*1\s+strategy", re.IGNORECASE),
        re.compile(r"-\d+\s+strategies", re.IGNORECASE),
    ],
    "gate_change": [
        re.compile(r"\bgate\b|gate.stack|gate.add|gate.remov|gate.delete", re.IGNORECASE),
        re.compile(r"loosen|tighten|swap\b", re.IGNORECASE),
    ],
    "threshold_change": [
        re.compile(r"threshold|cutoff|min_\w+|max_\w+", re.IGNORECASE),
        re.compile(r"RSI\s*[<>=]|EMA[_\s]\d+|ATR\s*\*", re.IGNORECASE),
    ],
    "regime_affinity": [
        re.compile(r"regime[_\s]affinity|regime[_\s]selector|STRATEGY_REGIME_AFFINITY", re.IGNORECASE),
    ],
    "state_event_conversion": [
        re.compile(r"STATE\s*->\s*EVENT|state.to.event|STATE-EVENT|EVENT-anchored", re.IGNORECASE),
    ],
    "producer_rewrite": [
        re.compile(r"producer.*fix|producer.*rewrite|F1\s+|F2\s+|F3\s+|F3b\s+", re.IGNORECASE),
    ],
    "docstring_only": [
        re.compile(r"docstring|doc[\s_]sync|doc.fix|doc[\s_]update", re.IGNORECASE),
    ],
}


def _classify_commit(message: str) -> set[str]:
    """Classify commit message into trial categories."""
    categories = set()
    for cat, patterns in TRIAL_KEYWORDS.items():
        for p in patterns:
            if p.search(message):
                categories.add(cat)
                break
    return categories


def _extract_batch_number(message: str) -> int | None:
    m = re.search(r"Batch\s+(\d{3,4})", message)
    if m:
        return int(m.group(1))
    m = re.search(r"^B(\d{3,4})\s*[:-]", message)
    if m:
        return int(m.group(1))
    return None


def _get_walk_era_commits(start_batch: int, end_batch: int) -> list[dict[str, Any]]:
    """Walk git log; return list of {batch, sha, message, classification}."""
    cmd = ["git", "log", "--format=%H%x09%s", "--since=2026-04-01"]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(REPO), timeout=120,
            encoding="utf-8", errors="replace",
        )
    except Exception as e:
        logger.error("git log failed: %s", e)
        return []
    stdout = result.stdout or ""
    commits = []
    for line in stdout.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        sha = parts[0]
        subject = parts[1]
        body = parts[2] if len(parts) > 2 else ""
        message = subject + " " + body[:500]
        batch = _extract_batch_number(message)
        if batch is None:
            continue
        if not (start_batch <= batch <= end_batch):
            continue
        cats = _classify_commit(message)
        commits.append({
            "sha": sha[:10],
            "batch": batch,
            "subject": subject[:200],
            "categories": sorted(cats),
        })
    return commits


def _strategy_count_history() -> dict[int, int]:
    """Per CLAUDE.md banner: strategy count evolved from approx200 to 219 over walk era."""
    # Reference points from CLAUDE.md banner inline parenthetical
    return {
        467: 198, 487: 208, 519: 210, 531: 212, 572: 213, 580: 215, 581: 221,
        591: 223, 599: 222, 603: 224, 605: 225, 607: 226, 610: 227, 611: 226,
        613: 226, 615: 227, 620: 226, 636: 227, 639: 226, 641: 226, 642: 226,
        645: 227, 682: 223, 685: 226, 686: 227, 709: 229, 722: 226, 874: 219,
        956: 219,
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    start_batch = 500
    end_batch = 956

    logger.info("Scanning walk-era commits B%d-B%d...", start_batch, end_batch)
    commits = _get_walk_era_commits(start_batch, end_batch)
    logger.info("Found %d walk-era commits", len(commits))

    # Per-category trial counts
    category_counts = Counter()
    batch_to_categories = {}
    for c in commits:
        for cat in c["categories"]:
            category_counts[cat] += 1
        batch_to_categories[c["batch"]] = c["categories"]

    # Trial-budget reasoning per Council 62 + DEC #5
    # Each gate_change / threshold_change / regime_affinity / state_event /
    # producer_rewrite commit = 1 trial against shared 2020-2026 data.
    # docstring_only commits are NOT trials.
    trial_categories = {
        "new_strategy", "strategy_deletion", "gate_change", "threshold_change",
        "regime_affinity", "state_event_conversion", "producer_rewrite",
    }
    trial_commits = [c for c in commits if any(cat in trial_categories for cat in c["categories"])]
    n_trial_commits = len(trial_commits)

    # Multi-strategy commits (e.g., walks affecting many strategies) inflate
    # per-strategy trial count; estimate average strategies-affected per commit.
    # B722 deleted 3 + B874 deleted 2 = average 1-3 strategies per commit
    avg_strategies_per_trial_commit = 2.0  # conservative estimate
    estimated_trials_per_strategy_avg = (n_trial_commits * avg_strategies_per_trial_commit) / 219

    # N_effective estimate
    # DEC #5 baseline: N=5,694 (219 strategies x 26 exits)
    # Council 61: real N includes walk-era trials
    # Each trial commit affects approx2 strategies on average
    # Total walk-era added trials approx n_trial_commits * 2
    n_effective_added = n_trial_commits * avg_strategies_per_trial_commit
    n_effective_total = 5694 + int(n_effective_added)
    inflation_factor = n_effective_total / 5694

    # DSR recalibration estimate
    # DSR threshold scales with sqrt(log(N))
    # At N=5,694: log(5694) approx= 8.6; sqrt approx= 2.94
    # At N=N_effective_total: log(N) / 8.6 inflates threshold proportionally
    import math
    base_log = math.log(5694)
    new_log = math.log(n_effective_total) if n_effective_total > 0 else base_log
    dsr_threshold_inflation = math.sqrt(new_log / base_log)

    # Per-strategy trial count (best-effort; commits don't always name strategies)
    per_strategy_trials = defaultdict(int)
    for c in trial_commits:
        # Try to extract strategy names from subject
        for m in re.finditer(r"strat_(\w+)|`([a-z][a-z0-9_]+)`", c["subject"]):
            strat = m.group(1) or m.group(2)
            if strat:
                per_strategy_trials[strat] += 1

    # Output JSON
    out_json = REPO / "output_audit" / "b957_retrospective_trial_count_audit.json"
    with open(out_json, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B957",
            "council_verdict": "61_critical_finding + 62_unconditional_ship",
            "scope": f"walk-era B{start_batch}-B{end_batch}",
            "n_commits_total": len(commits),
            "n_trial_commits": n_trial_commits,
            "trial_categories": {k: v for k, v in category_counts.most_common()},
            "trial_count_methodology": {
                "trial_definition": "Gate change / threshold change / regime affinity / STATE-EVENT / producer rewrite / new strategy / deletion",
                "non_trial_excluded": ["docstring_only"],
                "avg_strategies_affected_per_trial_commit": avg_strategies_per_trial_commit,
            },
            "dec_5_baseline_N": 5694,
            "estimated_walk_era_added_trials": int(n_effective_added),
            "n_effective_total_estimate": n_effective_total,
            "inflation_factor": inflation_factor,
            "estimated_trials_per_strategy_avg": estimated_trials_per_strategy_avg,
            "dsr_threshold_inflation_factor": dsr_threshold_inflation,
            "interpretation": (
                f"Walk-era B{start_batch}-B{end_batch} added approx{int(n_effective_added)} parameter trials "
                f"to DEC #5 baseline 5,694. N_effective approx{n_effective_total} ({inflation_factor:.2f}x inflation). "
                f"DSR threshold inflation approx{dsr_threshold_inflation:.3f}x means original 0.95 calibration "
                f"may correspond to approx{0.95 * dsr_threshold_inflation:.3f} at corrected N. "
                "Council 61 mandate: this measurement informs whether R5 PASS verdicts are statistically valid."
            ),
            "per_strategy_trials_named": dict(per_strategy_trials),
            "council_61_recommendation": (
                "If N_effective >> 5694, recalibrate DSR gate OR seal OOS 2026-Q2+ mandatory before R5 PASS honored."
            ),
            "council_62_phase_6_5_design_anchor": (
                "Phase 6.5 trial budget must include refinement trials. "
                "Type 1 POST-R5 narrow (+/-15% around passing gates) limits new trials to <200. "
                "Type 2 Track A (consolidation, pre-R5) adds 0 trials (deletion reduces N). "
                "Type 2 Track B (loosening borderline survivors, post-R5) trial-budgeted in DSR."
            ),
        }, f, indent=2, default=str)

    # Markdown summary
    lines = []
    lines.append("# Batch 957 (2026-06-20): Retrospective Trial-Count Audit\n\n")
    lines.append("# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 61+62 UNANIMOUS per CHECKLIST #77.\n\n")
    lines.append("## Owner Question Trigger (2026-06-20)\n\n")
    lines.append('> "In any phases will we be undertaking parameter optimization so we improve the performance of the strategies?"\n\n')
    lines.append("## Council 61 Critical Finding\n\n")
    lines.append("DEC #5 baseline DSR N = 5,694 (219 strategies x 26 exits). But Stage 4 walks edited gates across approx221 strategies over 100+ batches (B500-B956). Each gate edit was a TRIAL against the same 2020-2026 data. The roster you have today is the SURVIVOR of an UNBUDGETED SEARCH.\n\n")
    lines.append("## Council 62 Verdict (UNANIMOUS unconditional ship for C)\n\n")
    lines.append("- C (this audit) ships unconditionally: pure measurement, no DSR/OOS/B705 violation possible.\n")
    lines.append("- B (Phase 6.5 design) follows next turn with informed data, not assumption.\n")
    lines.append("- Council 62 REJECTS owner's proposed 28,500-cell pre-R5 exit sweep + 730-review FIRE_STARVED gate loosening as overfitting machines.\n")
    lines.append("- Council 62 RECOMMENDS NARROW Phase 6.5 (see batch 18).\n\n")

    lines.append("## Measurement Results\n\n")
    lines.append(f"- **Walk-era commits scanned:** {len(commits)} (B{start_batch}-B{end_batch})\n")
    lines.append(f"- **Trial commits (gate/threshold/regime/STATE-EVENT/producer/new-strat/deletion):** {n_trial_commits}\n")
    lines.append(f"- **Average strategies affected per trial commit:** {avg_strategies_per_trial_commit}\n")
    lines.append(f"- **Estimated walk-era added trials:** approx{int(n_effective_added)}\n")
    lines.append(f"- **DEC #5 baseline N:** 5,694\n")
    lines.append(f"- **N_effective total estimate:** approx{n_effective_total}\n")
    lines.append(f"- **Inflation factor vs baseline:** {inflation_factor:.2f}x\n")
    lines.append(f"- **DSR threshold inflation:** approx{dsr_threshold_inflation:.3f}x\n\n")

    lines.append("## Trial Categories (commits matching each pattern)\n\n")
    lines.append("| Category | Count |\n|---|---|\n")
    for cat, n in category_counts.most_common():
        lines.append(f"| {cat} | {n} |\n")
    lines.append("\n")

    lines.append("## Interpretation\n\n")
    lines.append(f"Walk-era B{start_batch}-B{end_batch} added approx{int(n_effective_added)} parameter trials to DEC #5 baseline 5,694. N_effective approx{n_effective_total} ({inflation_factor:.2f}x inflation).\n\n")
    lines.append(f"DSR threshold inflation approx{dsr_threshold_inflation:.3f}x means original 0.95 calibration may correspond to approx{0.95 * dsr_threshold_inflation:.3f} at corrected N.\n\n")

    lines.append("## Council 61 Recommendation (informs Phase 6.5)\n\n")
    lines.append("If N_effective >> 5,694, options:\n\n")
    lines.append("- Recalibrate DSR gate threshold downward to reflect inflated N\n")
    lines.append("- OR seal OOS 2026-Q2+ mandatory before R5 PASS honored\n")
    lines.append("- OR both\n\n")

    lines.append("## Council 62 Phase 6.5 Anchor (next turn batch 18)\n\n")
    lines.append("- Type 1 POST-R5 narrow refinement: limit to <200 new trials (cells within +/-15% of passing gates)\n")
    lines.append("- Type 2 Track A consolidation (pre-R5): 0 new trials added (deletion reduces N)\n")
    lines.append("- Type 2 Track B loosening (post-R5): trial-budgeted in DSR; survivor-only\n")
    lines.append("- Council 7 binding 'R5 -> no changes' RESET via logged DEC explicitly (not silent)\n")
    lines.append("- DEC #4 OOS seal preserved: 2026-Q2+ held-out for any refinement\n\n")

    lines.append("## Per-Strategy Named Trial Counts (best-effort from commit subjects)\n\n")
    if per_strategy_trials:
        lines.append("Top-20 strategies with most-named trial commits:\n\n")
        lines.append("| Strategy | Trials | \n|---|---|\n")
        for strat, n in Counter(per_strategy_trials).most_common(20):
            lines.append(f"| `{strat}` | {n} |\n")
    else:
        lines.append("No per-strategy named trials extracted (commit subjects use cluster IDs not strategy names).\n")
    lines.append("\n")

    lines.append("## Honest Limitations\n\n")
    lines.append("- Per-strategy trial count is BEST-EFFORT from commit subjects; cluster-walk commits affect multiple strategies\n")
    lines.append("- Trial classification uses keyword patterns; may miss / over-count\n")
    lines.append("- avg_strategies_per_trial_commit=2.0 is conservative; real may be 1-5\n")
    lines.append("- Earlier batches (B100-B499) NOT scanned this batch; Council 62 scope was B500-B956\n")
    lines.append("- DSR threshold inflation formula uses sqrt(log) approximation; exact recalibration requires Lo 2002 formula\n\n")

    lines.append("## Compliance Statement\n\n")
    lines.append("| Council 61+62 mandate | Status |\n|---|---|\n")
    lines.append("| C ships this turn unconditionally | OK |\n")
    lines.append("| Pure measurement; no DSR/OOS/B705 violation | OK |\n")
    lines.append("| Honest limitations surfaced | OK |\n")
    lines.append("| Informs B (Phase 6.5) next turn | OK |\n")
    lines.append("| Single artifact per Council 55-60 mandate | OK |\n")

    out_md = REPO / "output_audit" / "b957_retrospective_trial_count_audit_summary.md"
    with open(out_md, "w") as f:
        f.writelines(lines)

    logger.info("AUDIT COMPLETE:")
    logger.info("  Walk-era commits scanned: %d", len(commits))
    logger.info("  Trial commits: %d", n_trial_commits)
    logger.info("  DEC #5 baseline N: 5,694")
    logger.info("  Estimated added trials: approx%d", int(n_effective_added))
    logger.info("  N_effective total: approx%d (%.2fx inflation)", n_effective_total, inflation_factor)
    logger.info("  DSR threshold inflation: approx%.3fx", dsr_threshold_inflation)
    logger.info("  Output: %s", out_json.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
