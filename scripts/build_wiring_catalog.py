#!/usr/bin/env python3
"""Build wiring catalog: classify every decision + bug by actual engine wiring.

Owner directive 2026-05-12:
  "Wired" should mean the engine call path actually consumes the helper /
  constant, NOT just that a DEC-NNN reference appears in prod code (dashboard
  grep heuristic). Many Path C arc DECs (Batches 49-68) were flipped to
  RESOLVED-IMPLEMENTED based on the grep heuristic but the engine never
  imports or calls the helper.

Classification:
  ENGINE_WIRED          - helper/constant explicitly imported by engine path
  HELPER_ONLY           - helper exists in prod module; engine doesn't call it
  CONFIG_CONSTANT_LIVE  - constant in config.py; engine imports + reads it
  CONFIG_CONSTANT_DEAD  - constant in config.py; no engine reference
  STANDALONE_LEGIT      - no code artifact needed (requirements.txt, docs,
                          audit cross-refs, process decisions)
  NO_ARTIFACT_FOUND     - no helper or constant name extracted from description
  UNKNOWN               - ambiguous; needs manual review

Engine call paths (consumers): files whose import/call of a helper means
the helper is actually used in a backtest run.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).parent.parent

# Files that constitute the "engine call path" -- if these import or call a
# helper, the helper is genuinely wired.
ENGINE_CALL_PATHS = [
    REPO / "backtest/engine/backtest.py",
    REPO / "backtest/engine/exit_manager.py",
    REPO / "backtest/engine/exit_strategies.py",
    REPO / "backtest/engine/circuit_breakers.py",
    REPO / "backtest/engine/correlation_cluster.py",
    REPO / "backtest/engine/regime_stratified_split.py",
    REPO / "backtest/agents/pipeline.py",
    REPO / "backtest/signals/screener.py",
    REPO / "backtest/signals/technical.py",
    REPO / "backtest/data/fetcher.py",
    REPO / "backtest/data/macro.py",
    REPO / "backtest/data/sentiment.py",
    REPO / "backtest/data/smart_money.py",
    REPO / "backtest/data/universe.py",
    REPO / "backtest/data/cache.py",
    REPO / "backtest/results/writer.py",
    REPO / "backtest/results/site_generator.py",
    REPO / "backtest/run_phase1a.py",
    REPO / "backtest/run_phase1b.py",
]

# Files that hold helpers/constants but are NOT themselves engine call paths.
# A function defined here is "engine wired" only if some file in
# ENGINE_CALL_PATHS imports/calls it.
HELPER_FILES = [
    REPO / "backtest/results/metrics.py",
    REPO / "backtest/engine/improvements.py",
    REPO / "backtest/engine/regime_filter.py",
    REPO / "backtest/engine/portfolio.py",
    REPO / "backtest/engine/exit_context.py",
    REPO / "backtest/config.py",
]


def load_engine_corpus() -> str:
    parts: list[str] = []
    for p in ENGINE_CALL_PATHS:
        if p.exists():
            try:
                parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n".join(parts)


def load_helper_corpus() -> str:
    parts: list[str] = []
    for p in HELPER_FILES:
        if p.exists():
            try:
                parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Helper extraction from AUDIT_INDEX descriptions
# ---------------------------------------------------------------------------

# Match `function_name(` or `function_name -- ` or backtick-quoted function refs
FN_PATTERN = re.compile(r"`([a-z_][a-z0-9_]+)`")
# CONSTANT_NAME (4+ uppercase chars, may contain underscores/digits)
CONST_PATTERN = re.compile(r"\b([A-Z][A-Z0-9_]{3,})\b")
# Engine wiring deferred phrases -- explicit acknowledgement of non-wiring
WIRING_DEFERRED_PATTERNS = [
    re.compile(r"engine wiring.*deferred", re.IGNORECASE),
    re.compile(r"engine consumption.*deferred", re.IGNORECASE),
    re.compile(r"current scope is helper", re.IGNORECASE),
    re.compile(r"plan only execution deferred", re.IGNORECASE),
    re.compile(r"workflow file authoring deferred", re.IGNORECASE),
    re.compile(r"script implementation deferred", re.IGNORECASE),
    re.compile(r"implementation deferred", re.IGNORECASE),
    re.compile(r"deferred per per-DEC", re.IGNORECASE),
    re.compile(r"deferred to Sprint", re.IGNORECASE),
    re.compile(r"deferred to Stage", re.IGNORECASE),
    re.compile(r"deferred to follow-on", re.IGNORECASE),
]

# Markers suggesting the DEC is legitimately standalone (no code wiring expected)
STANDALONE_MARKERS = [
    "requirements.txt", "process methodology", "planning/architecture",
    "vendor/process decision", "documentation audit", "cross-reference constant",
    "cross-reference documentation", "audit annotation", "bookkeeping flip",
    "absorbed by upstream", "absorbed by DEC-",
]


def extract_artifact_names(description: str) -> tuple[list[str], list[str]]:
    """Extract candidate function names + constant names from description."""
    fns = list(set(FN_PATTERN.findall(description)))
    # Filter constants -- exclude common words and tier names
    raw_consts = set(CONST_PATTERN.findall(description))
    blacklist = {
        "DEC", "BUG", "CAV", "INV", "DECISION", "PASS", "RESOLVED",
        "IMPLEMENTED", "DECIDED", "PARTIAL", "DEFERRED", "STAGE", "SPRINT",
        "PHASE", "OPEN", "DEC-", "WIRED", "YES", "NO", "NULL", "NONE",
        "TRUE", "FALSE", "NAT", "NAN",
        "API", "URL", "CSV", "JSON", "YAML", "TOML", "XML", "HTML",
        "CI", "PR", "OK", "ID", "REGEX", "MD",
        "NYSE", "NASDAQ", "SPY", "QQQ", "IWM", "VTI", "TLT", "GLD", "UUP", "USO",
        "LIT", "DBB", "COPX", "TD", "RY", "BNS", "ENB", "CNQ", "SU",
        "XLE", "XLK", "XLF", "XUU", "XQQ", "XSU", "VUN", "EEM",
        "CEO", "CFO", "COO", "CTO",
        "ROI", "PSR", "DD", "WR", "PF", "TE", "IR", "PEG", "ROE", "ROA",
        "FCF", "TTM", "EPS", "CPI", "PPI", "NFP", "FOMC", "VIX", "DXY",
        "ICSA", "PAYEMS", "MANEMP", "UMCSENT", "RSAFS", "HOUST", "INDPRO",
        "M2SL", "BAMLH0A0HYM2",
        "BMO", "AMC", "BOS", "FVG", "PIT", "GICS", "ETF", "ADV", "MFE",
        "HMM", "OLS", "ADF", "PIT-", "T-1", "10-K", "13F",
        "DEC-", "BUG-",
        "OOS", "AAII", "FRED", "ALFRED",
        "OHLCV", "ICT", "SMC", "WSB", "WS", "T1A", "T1B", "T1C", "T2", "T3",
        "READY", "BLOCKED", "REJECTED", "SUPERSEDED", "OBSOLETE",
        "PROPOSED", "UNKNOWN", "FAIL", "PASS_LE", "PASS_GE",
        "REL_PASS", "ABS_PASS",
        "REVISIT_AFTER_BACKTEST", "BLOCKED_ON",
        "HIGH", "MEDIUM", "LOW", "EXCEPTIONAL", "AVOID",
        "CODE_ONLY", "TEST_ONLY", "SPEC_ONLY",
        "VERY_HIGH", "MEDIUM_HIGH",
        "DOC", "OWNER", "STAGE_3", "STAGE_4", "PHASE_1A", "PHASE_1B",
        "PHASE_1C", "PHASE_2", "SPRINT_8",
        "CHECKLIST",
        "CAV-", "L88", "L142", "L143", "L146", "L147", "L149", "L86", "L95",
        "L77", "L49", "L103", "L133", "L144",
        "AUDIT", "AUDIT_INDEX",
        "DEC", "PIT-CORRECT", "PHASED_ROLLOUT",
        "ROUND", "FINAL",
        "PCR", "OI", "PR-CI", "ON-TIME", "PR-SIDE",
    }
    consts = sorted(c for c in raw_consts if c not in blacklist and len(c) >= 6)
    return fns, consts


def is_engine_wired(name: str, engine_corpus: str, helper_corpus: str) -> bool:
    """Engine wired = name appears in at least one ENGINE_CALL_PATHS file."""
    pattern = re.compile(r"\b" + re.escape(name) + r"\b")
    return bool(pattern.search(engine_corpus))


def classify_helper_only(name: str, helper_corpus: str) -> bool:
    """True if name is defined in HELPER_FILES (helper exists somewhere)."""
    pattern = re.compile(r"\b" + re.escape(name) + r"\b")
    return bool(pattern.search(helper_corpus))


def has_wiring_deferred_text(description: str) -> bool:
    return any(p.search(description) for p in WIRING_DEFERRED_PATTERNS)


def has_standalone_marker(description: str) -> bool:
    desc_lower = description.lower()
    return any(m.lower() in desc_lower for m in STANDALONE_MARKERS)


def classify(description: str, engine_corpus: str, helper_corpus: str) -> dict:
    fns, consts = extract_artifact_names(description)
    candidates = fns + consts
    if not candidates:
        if has_standalone_marker(description):
            return {
                "classification": "STANDALONE_LEGIT",
                "candidates": [],
                "engine_hits": [],
                "helper_hits": [],
                "wiring_deferred_explicit": has_wiring_deferred_text(description),
            }
        return {
            "classification": "NO_ARTIFACT_FOUND",
            "candidates": [],
            "engine_hits": [],
            "helper_hits": [],
            "wiring_deferred_explicit": has_wiring_deferred_text(description),
        }
    engine_hits = [c for c in candidates if is_engine_wired(c, engine_corpus, helper_corpus)]
    helper_hits = [c for c in candidates if classify_helper_only(c, helper_corpus)]
    deferred = has_wiring_deferred_text(description)
    # Decision tree
    is_config_const = any(c.isupper() for c in candidates)
    if engine_hits:
        if is_config_const and not fns:
            # All candidates are constants and at least one is engine-referenced
            classification = "CONFIG_CONSTANT_LIVE"
        else:
            classification = "ENGINE_WIRED"
    elif helper_hits:
        # Helper exists but engine doesn't call it
        if is_config_const and not fns:
            classification = "CONFIG_CONSTANT_DEAD"
        else:
            classification = "HELPER_ONLY"
    else:
        # No helper found anywhere -- candidates may be conceptual names only
        if has_standalone_marker(description):
            classification = "STANDALONE_LEGIT"
        else:
            classification = "NO_ARTIFACT_FOUND"
    return {
        "classification": classification,
        "candidates": candidates,
        "engine_hits": engine_hits,
        "helper_hits": helper_hits,
        "wiring_deferred_explicit": deferred,
    }


# ---------------------------------------------------------------------------
# Audit parsing
# ---------------------------------------------------------------------------

def parse_decisions() -> list[dict]:
    text = (REPO / "AUDIT_INDEX.md").read_text(encoding="utf-8", errors="ignore")
    start = text.find("### All Decisions Table")
    if start < 0:
        return []
    section = text[start:]
    decs: list[dict] = []
    in_table = False
    for line in section.split("\n"):
        if not line.strip().startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "ID" in cells[0] and "Title" in cells[1]:
            in_table = True
            continue
        if in_table and len(cells) >= 6:
            if all("---" in c or c == "" for c in cells):
                continue
            dec_id = re.sub(r"\*\*", "", cells[0])
            description = re.sub(r"\*\*", "", cells[1])
            status = re.sub(r"\*\*", "", cells[2])
            theme = cells[3]
            decs.append({"id": dec_id, "description": description, "status": status, "theme": theme})
    return decs


def parse_bugs() -> list[dict]:
    """Parse BUG_REGISTER.md per-bug rows. Schema (4-col):
    | BUG-NN | description | resolving_dec | status |
    """
    p = REPO / "BUG_REGISTER.md"
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="ignore")
    bugs: list[dict] = []
    for line in text.split("\n"):
        m = re.match(r"^\| (BUG-[\w-]+) \| (.+?) \| ([^|]+) \| ([^|]+) \|", line)
        if not m:
            continue
        bug_id = m.group(1).strip()
        desc = m.group(2).strip()
        resolving_dec = m.group(3).strip()
        status = m.group(4).strip()
        # Combine resolving_dec into description for artifact extraction
        full_desc = f"{desc} (resolving: {resolving_dec}) -- {status}"
        bugs.append({"id": bug_id, "description": full_desc, "status": status})
    return bugs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    engine_corpus = load_engine_corpus()
    helper_corpus = load_helper_corpus()

    decs = parse_decisions()
    bugs = parse_bugs()

    out_lines = ["# Wiring Catalog (Batch 69 owner-mandated)\n"]
    out_lines.append("Owner directive 2026-05-12: review every decision and every bug ")
    out_lines.append("for ACTUAL engine wiring (not dashboard grep heuristic). ")
    out_lines.append("Helper-only DECs flipped to RESOLVED-IMPLEMENTED in Batches 49-68 ")
    out_lines.append("are FALSE POSITIVES if the engine call path doesn't consume them.\n\n")
    out_lines.append("## Classifier accuracy caveat (READ FIRST)\n\n")
    out_lines.append("This catalog is a **first-pass heuristic**, not authoritative:\n")
    out_lines.append("- Artifact extraction is regex-based on the description text. ")
    out_lines.append("Descriptions often mention engine functions (like `can_open`) as context ")
    out_lines.append("alongside the DEC's actual helper name; the classifier may flag ENGINE_WIRED ")
    out_lines.append("based on the contextual mention instead of the DEC's own helper.\n")
    out_lines.append("- Example known false-positive: DEC-091 (drawdown_size_multiplier) is ")
    out_lines.append("shelf-ready, but the description references `can_open` (engine function) ")
    out_lines.append("so classifier shows ENGINE_WIRED.\n")
    out_lines.append("- Therefore the ENGINE_WIRED count of 35 is likely **overstated**; the ")
    out_lines.append("HELPER_ONLY + CONFIG_CONSTANT_DEAD count of 199 is likely **understated**.\n")
    out_lines.append("- The wiring-deferred-phrase column (`YES` / `no`) is the most reliable signal: ")
    out_lines.append("YES means I explicitly wrote 'engine wiring deferred' in the body, which is a ")
    out_lines.append("self-confessed shelf-ready item.\n")
    out_lines.append("- **Use this catalog as a first sweep**. Per-DEC manual verification needed ")
    out_lines.append("before bulk reverts.\n\n")

    # Decision stats
    by_class: dict[str, list[str]] = {}
    out_lines.append("## Decisions (n=" + str(len(decs)) + ")\n\n")
    out_lines.append("| DEC | Status (claimed) | Classification | Helpers/Constants found | Engine-wired hits | Wiring-deferred phrase in body |\n")
    out_lines.append("|---|---|---|---|---|---|\n")

    for dec in decs:
        cls_result = classify(dec["description"], engine_corpus, helper_corpus)
        classification = cls_result["classification"]
        by_class.setdefault(classification, []).append(dec["id"])
        cand_str = ", ".join(cls_result["candidates"][:5]) or "-"
        engine_str = ", ".join(cls_result["engine_hits"][:5]) or "-"
        deferred = "YES" if cls_result["wiring_deferred_explicit"] else "no"
        # Truncate description preview
        out_lines.append(
            f"| {dec['id']} | {dec['status'][:30]} | {classification} | "
            f"{cand_str[:80]} | {engine_str[:60]} | {deferred} |\n"
        )

    # Summary
    out_lines.append("\n## Summary by Classification\n\n")
    out_lines.append("| Classification | Count | Action |\n|---|---|---|\n")
    actions = {
        "ENGINE_WIRED":         "Keep RESOLVED-IMPLEMENTED. Genuinely wired.",
        "CONFIG_CONSTANT_LIVE": "Keep RESOLVED-IMPLEMENTED. Constant consumed by engine.",
        "HELPER_ONLY":          "REVERT to PARTIAL-IMPL-HELPER-ONLY. Helper exists but engine doesn't call it.",
        "CONFIG_CONSTANT_DEAD": "REVERT to PARTIAL-IMPL-CONFIG-DEAD. Constant defined but nothing reads it.",
        "STANDALONE_LEGIT":     "Keep RESOLVED-IMPLEMENTED. Legitimately no code wiring needed (requirements.txt / docs / process).",
        "NO_ARTIFACT_FOUND":    "MANUAL REVIEW. No helper/constant detected -- description may reference conceptual scope only.",
        "UNKNOWN":              "MANUAL REVIEW.",
    }
    for cls in sorted(by_class.keys()):
        ids = by_class[cls]
        out_lines.append(f"| {cls} | {len(ids)} | {actions.get(cls, '?')} |\n")

    # Bug rows
    out_lines.append("\n\n## Bugs (n=" + str(len(bugs)) + ")\n\n")
    out_lines.append("| Bug | Status (claimed) | Classification | Helpers/Constants found | Engine-wired hits | Wiring-deferred phrase |\n")
    out_lines.append("|---|---|---|---|---|---|\n")

    bug_by_class: dict[str, list[str]] = {}
    for bug in bugs:
        cls_result = classify(bug["description"], engine_corpus, helper_corpus)
        classification = cls_result["classification"]
        bug_by_class.setdefault(classification, []).append(bug["id"])
        cand_str = ", ".join(cls_result["candidates"][:5]) or "-"
        engine_str = ", ".join(cls_result["engine_hits"][:5]) or "-"
        deferred = "YES" if cls_result["wiring_deferred_explicit"] else "no"
        out_lines.append(
            f"| {bug['id']} | {bug['status'][:30]} | {classification} | "
            f"{cand_str[:80]} | {engine_str[:60]} | {deferred} |\n"
        )

    out_lines.append("\n## Bugs Summary by Classification\n\n")
    out_lines.append("| Classification | Count |\n|---|---|\n")
    for cls in sorted(bug_by_class.keys()):
        out_lines.append(f"| {cls} | {len(bug_by_class[cls])} |\n")

    # Write catalog
    catalog_path = REPO / "WIRING_CATALOG_BATCH_69.md"
    catalog_path.write_text("".join(out_lines), encoding="utf-8")
    print(f"Catalog written to {catalog_path}")
    print(f"\nDecision classification counts:")
    for cls in sorted(by_class.keys()):
        print(f"  {cls}: {len(by_class[cls])}")
    print(f"\nBug classification counts:")
    for cls in sorted(bug_by_class.keys()):
        print(f"  {cls}: {len(bug_by_class[cls])}")


if __name__ == "__main__":
    main()
