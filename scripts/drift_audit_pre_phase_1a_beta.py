"""Comprehensive pre-Phase-1A-beta drift audit.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-25 Batch 360 "do a detailed alignment between all documents and
codebase and trade results. Identify and flag all drifts!"

Produces PHASE_1A_BETA_PRE_RUN_ALIGNMENT_AUDIT.md with:
  1. Live authoritative values (code-derived)
  2. Trade result anchors (output_phase_1a_beta_merged_local + cube)
  3. Per-doc drift table classified as:
     - ACTIVE_CLAIM: doc states a count that doesn't match live; needs fix
     - HISTORICAL_NARRATIVE: doc describes a past drift / bug that has been
       fixed; reference can stay (BUG-NNN context)
     - AMBIGUOUS: regex match needs human eyeball

Output is UTF-8 to a file (not stdout) to avoid console codec issues.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parent.parent

# ---------------------------------------------------------------------
# LIVE authoritative values
# ---------------------------------------------------------------------
sys.path.insert(0, str(REPO))


def live_values() -> dict:
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import DEPRECATED_STRATEGIES, STRATEGY_EXIT_OVERRIDE
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    import pandas as pd

    tl_path = REPO / "output_phase_1a_beta_merged_local" / "trade_log.csv"
    cube_path = REPO / "output_audit" / "trade_exit_detail_phase_1a_beta_rebuilt.csv"

    out = {
        "strategy_total":      len(ALL_STRATEGIES),
        "deprecated_count":    len(DEPRECATED_STRATEGIES),
        "strategy_active":     len(ALL_STRATEGIES) - len(DEPRECATED_STRATEGIES),
        "exit_method_total":   len(EXIT_STRATEGIES),
        "strategy_exit_override_count": len(STRATEGY_EXIT_OVERRIDE),
        "agent_count_dec_057": 11,  # DEC-057: 3 analysts + Bull/Bear/RM + Trader + 3 Risk + PM + Reflection
        "regime_count":        4,    # bull/bear/neutral/crisis
        "phase_1a_beta_actual_wall_hours": 10.5,  # 2026-05-24 Hetzner
        "phase_1a_beta_pool_speedup_target": "4-8x",  # Batch 322 theoretical
    }

    if tl_path.exists():
        tl = pd.read_csv(tl_path, low_memory=False)
        out["trade_log_trades"]            = len(tl)
        out["trade_log_strategies_fired"]  = int(tl["strategy"].nunique())
        out["trade_log_exit_reasons"]      = int(tl["exit_reason"].nunique())
        out["trade_log_tickers"]           = int(tl["ticker"].nunique())
        out["trade_log_regimes_fired"]     = dict(tl["regime"].value_counts())
        out["trade_log_sum_pp"]            = round(float(tl["pnl_pct"].sum()), 2)
        out["trade_log_wr_pct"]            = round(
            float(tl["win"].astype(bool).sum()) / len(tl) * 100, 2
        )

    if cube_path.exists():
        cube = pd.read_csv(cube_path, low_memory=False)
        out["cube_rows"]            = len(cube)
        out["cube_strategies_fired"] = int(cube["strategy"].nunique())
        out["cube_exit_methods"]     = int(cube["exit_method"].nunique())
        out["cube_cells"]            = int(cube.groupby(
                                            ["strategy", "exit_method"]).ngroups)

    # Tests
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q",
             str(REPO / "backtest" / "tests")],
            capture_output=True, text=True, timeout=180,
        )
        for line in res.stdout.splitlines()[::-1]:
            if "tests collected" in line:
                m = re.search(r"(\d+)\s+tests?\s+collected", line)
                if m:
                    out["tests_collected"] = int(m.group(1))
                    break
    except Exception as e:
        out["tests_collected"] = f"error: {e}"

    return out


# ---------------------------------------------------------------------
# Document inventory
# ---------------------------------------------------------------------
HISTORICAL_NARRATIVE_DOCS = {
    "AUDIT.md", "BUG_REGISTER.md", "AUDIT_INDEX.md", "AUDIT_BACKLOG.md",
    "AUDIT_TRIAGE.md", "ENGINEERING_REGISTER.md", "OPEN_INVESTIGATIONS.md",
    "LEARNINGS.md", "UNIVERSAL_LEARNINGS.md",
    "PASS_53_PRIORITIES.md", "TRIAGE_PREP_2026_05_19.md",
    "WIRING_CATALOG_BATCH_69.md", "DOCUMENTATION_REGISTER.md",
    "PROJECT_PLAN_ARCHIVE.md",   # ARCHIVE doc; pre-Batch-316a snapshot intentional
}

# Lines in canonical-source docs whose drift hits are FALSE POSITIVES because
# the line is itself the source-of-truth's enumeration of acceptable phrasings
# OR the meta-narrative about a prior drift (i.e., the doc is the drift fix).
FALSE_POSITIVE_LINES = {
    "CANONICAL_FACTS.md": {
        15, 16,        # Meta-narrative on the historical agent-count drift; canonical is 11 active agents per DEC-057
        45,            # F-001 Definition paragraph header
        77,            # F-001 Acceptable phrasing variants list
        137,           # F-002 Acceptable phrasing variants list
        216,           # F-004 "Value (planned target): 20" - planned-target variant
        262,           # F-004 Acceptable phrasing variants list (includes 25 LIVE)
    },
    "CHECKLIST.md": {
        140,           # Historical-drift narrative line (pre-DEC-057 stale phrasings); canonical is 11 active agents per DEC-057
    },
    "CLAUDE.md": {
        91, 143,       # Correctly states 11-active-agent pipeline (regex false hit)
    },
    "STRATEGY_ROSTER_FULL.md": {
        47,            # "60 baseline (long-direction) + 12 dedicated shorts = 72"
                       # is the Layer 1 sub-count narrative; total is in L43 (stale)
    },
    "TRADING_RULES_AND_INFORMATION.md": {
        2530,          # "18.7 Agent Value-Add Gate" - section number ".7" + "Agent"
                       # regex hit, not an agent-count claim
    },
    "DETAILED_PROJECT_PLAN.md": {
        51,            # "- 2.6 Agent overlay architecture" - section number
        649,           # "## 2.6 Agent overlay architecture" - section number
        653,           # "12 agent roles (11 active + Reflection)" - 11+1=12 is correct
    },
}
# These docs describe past drifts / RESOLVED bugs in their natural prose.
# Their drift mentions are CONTEXT, not active claims.

FORWARD_LOOKING_DOCS = {
    "CLAUDE.md", "CANONICAL_FACTS.md", "PROJECT_PLAN.md", "DETAILED_PROJECT_PLAN.md",
    "PROJECT_PLAN_ARCHIVE.md",
    "BUILD_PLAN_PROGRESS.md", "STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md",
    "CHECKLIST.md", "VERIFICATION_MATRIX.md",
    "IMPLEMENTATION_PLAN.md", "IMPLEMENTATION_DRAFTS_T1.md",
    "IMPLEMENTATION_READINESS_DASHBOARD.md",
    "LIMITATIONS_CAVEATS_ASSUMPTIONS.md", "TESTING_PYRAMID_REFERENCE.md",
    "TRADING_RULES_AND_INFORMATION.md", "TRADINGAGENTS_DATA_AUDIT.md",
    "PHASE_1A_BETA_SURVIVOR_ROSTER.md", "PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md",
    "PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md", "PHASE_1B_AUDIT_2026_05_25.md",
    "PHASE_1B_STATE_SCHEMA_DIFF.md", "PHASE_1A_PRELAUNCH_TODO.md",
    "T1A_COMPREHENSIVE_REVIEW_2026_05_20.md", "COMPREHENSIVE_REVIEW_2026_05_20.md",
    "DESIGN_AUDIT_2026_05_20.md", "DESIGN_AUDIT_PART_2_2026_05_20.md",
    "DESIGN_AUDIT_PART_3_2026_05_20.md",
    "README.md", "STRATEGY_REGISTER.md", "STRATEGY_ROSTER_FULL.md",
    "API_AUDIT.md", "API_ENDPOINT_INVENTORY.md", "BATCH_318_PROCESS_POOL_DESIGN.md",
    "EXPLANATION.md", "OHLCV_INTEGRITY_REPORT.md",
    "POST_MAY_29_OPERATION_GUIDE.md",
    "PREFETCH_COVERAGE_AUDIT.md", "SIGNAL_AUDIT_2026_05_21.md",
    "STAGE_3_PAPER_TRADING_ACTIVATION.md", "THEME_X53_SEQUENCING.md",
}

ALL_DOCS = sorted(HISTORICAL_NARRATIVE_DOCS | FORWARD_LOOKING_DOCS)


# ---------------------------------------------------------------------
# Drift patterns
# ---------------------------------------------------------------------
PATTERNS = [
    (r"\b(\d{2,3})\s*(?:active\s+|live\s+)?strateg(?:y|ies)\b", "strategy_count"),
    (r"\b(\d+)\s*exit\s+method(?:s)?\b", "exit_method_count"),
    (r"\b(\d+)\s+agent(?:s)?\b", "agent_count"),
    (r"\b(\d+)\s+regime(?:s)?\b", "regime_count"),
    (r"~?(\d+(?:\.\d+)?)\s*(?:h|hour|hr|HR)(?:\s+(?:on\s+Hetzner|wall|run\s+time|Phase\s+1A))", "timeline_hours"),
    (r"~?(\d+(?:-\d+)?)\s*day(?:s)?(?:\s+(?:run|compute|wall))", "timeline_days"),
    (r"\b(\d{3,5})\s+(?:passed|tests?(?:\s+(?:pass|collected|in\s+pyramid|baseline)))", "test_count"),
]

# Drift values to call out specifically per category
KNOWN_STALE = {
    "strategy_count":    [60, 72, 102, 108, 118, 119, 125, 133, 134, 148, 198, 199, 203, 213],
    "exit_method_count": [9, 12, 17, 20],
    "agent_count":       [6, 7, 9, 10, 12, 13],
}


def _is_meta_correction(line: str) -> bool:
    """Detect 'was X pre-Y' / 'X -> Y (live)' meta-correction lines where the
    stale number is being explicitly cited as the past state, not as a current
    claim. Also treats forward-looking planned-target references with explicit
    `(per F-002 ...)` / `Pass 53 expansion` / `CANONICAL_FACTS` provenance as
    NOT drift -- they are planned-target citations alongside the LIVE 186."""
    lc = line.lower()
    return any(marker in lc for marker in [
        "was ", "pre-batch", "pre-pass", "live `len(", "live count",
        "planned target", "(stale)", "stale; was", "snapshot",
        "stale)", " -> ", "(historical",  " " + chr(0x2192) + " ",
        "per f-002", "per canonical_facts", "f-002 pass 53",
        "pass 53 expansion", "canonical_facts f-002",
        "section 6 (line", "section 6 = baseline",  # cross-doc reference pointers
    ])


def scan_doc(doc_path: Path, live: dict) -> list[dict]:
    drifts = []
    if not doc_path.exists():
        return drifts
    text = doc_path.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(text.splitlines(), 1):
        line_lc = line.lower()
        if line.strip().startswith("# "):
            continue
        if _is_meta_correction(line):
            continue
        for pattern, key in PATTERNS:
            for m in re.finditer(pattern, line, re.IGNORECASE):
                try:
                    raw = m.group(1)
                    if "-" in raw:
                        continue
                    val = int(raw) if "." not in raw else float(raw)
                except (ValueError, IndexError):
                    continue
                if key in KNOWN_STALE and val in KNOWN_STALE[key]:
                    live_key = {
                        "strategy_count":    "strategy_total",
                        "exit_method_count": "exit_method_total",
                        "agent_count":       "agent_count_dec_057",
                    }.get(key)
                    live_val = live.get(live_key) if live_key else None
                    if live_val is not None and val != live_val:
                        drifts.append({
                            "doc":     doc_path.name,
                            "line":    i,
                            "key":     key,
                            "stated":  val,
                            "live":    live_val,
                            "snippet": line.strip()[:160],
                        })
    return drifts


def main():
    live = live_values()
    output = []
    output.append("# Phase 1A-beta pre-run alignment audit")
    output.append("")
    output.append("**Source** (per CHECKLIST #77 canonical-source attribution):")
    output.append("- Owner directive 2026-05-25 Batch 360: comprehensive alignment audit before Phase 1A-beta cube re-run.")
    output.append("- Code SSOT: `backtest/signals/screener.py::ALL_STRATEGIES`, `backtest/engine/exit_strategies.py::EXIT_STRATEGIES`, `backtest/config.py::DEPRECATED_STRATEGIES`.")
    output.append("- Trade results SSOT: `output_phase_1a_beta_merged_local/trade_log.csv` + `output_audit/trade_exit_detail_phase_1a_beta_rebuilt.csv`.")
    output.append("- Generator: `scripts/drift_audit_pre_phase_1a_beta.py`.")
    output.append("")
    output.append("## 1. Live authoritative values (code + trade results)")
    output.append("")
    output.append("| Fact | Live value | Source |")
    output.append("|---|---|---|")
    for k, v in live.items():
        output.append(f"| `{k}` | {v} | code/trade-log |")
    output.append("")

    drifts: dict[str, list] = defaultdict(list)
    false_positives: dict[str, list] = defaultdict(list)
    docs_missing = []
    for doc_name in ALL_DOCS:
        doc_path = REPO / doc_name
        if not doc_path.exists():
            docs_missing.append(doc_name)
            continue
        fp_lines = FALSE_POSITIVE_LINES.get(doc_name, set())
        for d in scan_doc(doc_path, live):
            if d["line"] in fp_lines:
                false_positives[doc_name].append(d)
            else:
                drifts[doc_name].append(d)

    # Summary table
    output.append("## 2. Drift summary by document")
    output.append("")
    output.append("Drifts split: ACTIVE_CLAIM (forward-looking doc citing stale count) vs HISTORICAL_NARRATIVE (audit/bug doc describing past drift, context-only).")
    output.append("")
    output.append("| Doc | Drift hits | Classification |")
    output.append("|---|---:|---|")
    total_active = 0
    total_hist = 0
    for doc_name in ALL_DOCS:
        n = len(drifts.get(doc_name, []))
        if n == 0:
            continue
        cls = "HISTORICAL_NARRATIVE" if doc_name in HISTORICAL_NARRATIVE_DOCS else "ACTIVE_CLAIM"
        if cls == "ACTIVE_CLAIM":
            total_active += n
        else:
            total_hist += n
        output.append(f"| `{doc_name}` | {n} | {cls} |")
    output.append("")
    output.append(f"**Total drift hits**: {total_active + total_hist}")
    output.append(f"**Active drifts (need fix)**: {total_active}")
    output.append(f"**Historical drifts (context-only)**: {total_hist}")
    output.append(f"**Docs scanned**: {len(ALL_DOCS) - len(docs_missing)}")
    output.append(f"**Docs missing from filesystem**: {len(docs_missing)}: {docs_missing}")
    output.append("")

    # Active drifts in detail
    output.append("## 3. ACTIVE drift detail (forward-looking docs needing fix)")
    output.append("")
    for doc_name in sorted(FORWARD_LOOKING_DOCS):
        ds = drifts.get(doc_name, [])
        if not ds:
            continue
        output.append(f"### {doc_name}")
        output.append("")
        output.append("| Line | Key | Stated | Live | Snippet |")
        output.append("|---:|---|---:|---:|---|")
        for d in ds[:30]:
            snip = d["snippet"].replace("|", "\\|")[:120]
            output.append(f"| {d['line']} | `{d['key']}` | {d['stated']} | {d['live']} | `{snip}` |")
        if len(ds) > 30:
            output.append(f"| ... | ... | ... | ... | +{len(ds) - 30} more |")
        output.append("")

    # Historical context
    output.append("## 4. HISTORICAL_NARRATIVE drifts (context-only, no action needed)")
    output.append("")
    for doc_name in sorted(HISTORICAL_NARRATIVE_DOCS):
        ds = drifts.get(doc_name, [])
        if not ds:
            continue
        output.append(f"- `{doc_name}`: {len(ds)} hits (audit/bug doc historical prose)")
    output.append("")

    # False positives explicitly listed
    output.append("## 5. False positives (regex hit but not actually drift)")
    output.append("")
    output.append("Lines explicitly whitelisted as canonical-source-of-truth listings")
    output.append("(e.g., CANONICAL_FACTS Acceptable-phrasing-variants section) or")
    output.append("correct-but-regex-matched statements (CLAUDE.md '11 active agents').")
    output.append("")
    n_fp_total = sum(len(v) for v in false_positives.values())
    output.append(f"**False positive count**: {n_fp_total}")
    output.append("")
    for doc_name in sorted(false_positives.keys()):
        output.append(f"- `{doc_name}`: {len(false_positives[doc_name])} false-positive hits")
    output.append("")

    # Fix priority list
    output.append("## 6. Fix priority order (forward-looking docs only)")
    output.append("")
    output.append("**HIGH** (directly informs Phase 1A-beta cube re-run scope):")
    output.append("")
    for doc_name in [
        "PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md",
        "PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md",
        "PHASE_1A_BETA_SURVIVOR_ROSTER.md",
        "BUILD_PLAN_PROGRESS.md",
        "STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md",
        "STRATEGY_REGISTER.md",
        "STRATEGY_ROSTER_FULL.md",
        "TRADINGAGENTS_DATA_AUDIT.md",
    ]:
        n = len(drifts.get(doc_name, []))
        if n > 0:
            output.append(f"- `{doc_name}`: {n} drifts")
    output.append("")
    output.append("**MEDIUM** (project-plan reference docs; impact next-batch planning):")
    output.append("")
    for doc_name in [
        "DETAILED_PROJECT_PLAN.md", "PROJECT_PLAN.md", "TRADING_RULES_AND_INFORMATION.md",
        "CANONICAL_FACTS.md", "LIMITATIONS_CAVEATS_ASSUMPTIONS.md", "EXPLANATION.md",
        "CHECKLIST.md", "CLAUDE.md",
    ]:
        n = len(drifts.get(doc_name, []))
        if n > 0:
            output.append(f"- `{doc_name}`: {n} drifts")
    output.append("")
    output.append("**LOW** (specialized / less-frequently-read docs):")
    output.append("")
    remaining = sorted(FORWARD_LOOKING_DOCS - {
        "PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md",
        "PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md",
        "PHASE_1A_BETA_SURVIVOR_ROSTER.md",
        "BUILD_PLAN_PROGRESS.md",
        "STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md",
        "STRATEGY_REGISTER.md", "STRATEGY_ROSTER_FULL.md",
        "TRADINGAGENTS_DATA_AUDIT.md", "DETAILED_PROJECT_PLAN.md",
        "PROJECT_PLAN.md", "TRADING_RULES_AND_INFORMATION.md",
        "CANONICAL_FACTS.md", "LIMITATIONS_CAVEATS_ASSUMPTIONS.md",
        "EXPLANATION.md", "CHECKLIST.md", "CLAUDE.md",
    })
    for doc_name in remaining:
        n = len(drifts.get(doc_name, []))
        if n > 0:
            output.append(f"- `{doc_name}`: {n} drifts")
    output.append("")

    out_path = REPO / "PHASE_1A_BETA_PRE_RUN_ALIGNMENT_AUDIT.md"
    out_path.write_text("\n".join(output), encoding="utf-8")
    print(f"[OK] {out_path} ({total_active + total_hist} drifts; {total_active} active)")

    # Also dump live values JSON for reference
    json_path = REPO / "output_audit" / "drift_audit_live_values.json"
    json_path.parent.mkdir(exist_ok=True)
    # Convert numpy ints
    clean = {k: (int(v) if hasattr(v, "item") else
                 {kk: int(vv) if hasattr(vv, "item") else vv for kk, vv in v.items()}
                 if isinstance(v, dict) else v)
             for k, v in live.items()}
    json_path.write_text(json.dumps(clean, indent=2, default=str), encoding="utf-8")
    print(f"[OK] {json_path}")


if __name__ == "__main__":
    main()
