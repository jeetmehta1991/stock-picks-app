r"""Batch 463 (2026-05-29) -- AU7 unused-config-flags registry.

QUEUE FRAMING WAS WRONG (102 vs 18):
  The queue claimed 18 unused config flags in backtest/config.py. A re-scan
  with strict reference detection (skip tests/ + config.py itself, only
  look for whole-word `\bNAME\b` matches in backtest/* + scripts/*) shows
  102 unused constants. The queue listed a subset only.

NO CODE DELETION IN THIS BATCH:
  Per CLAUDE.md "ALL decisions need explicit owner approval before
  implementation", deleting or moving constants is a behavior change that
  needs owner sign-off. This batch ships only the REGISTRY + drift guard,
  with each unused constant classified into one of:

    a -- "implement now"  : Phase 1A-beta / pre-1B feature work; the
                            constant defines a value that SHOULD be
                            consumed by code but the consumer never
                            landed. Owner approval needed for the build.
    b -- "delete"         : truly orphaned (no semantic value beyond
                            being typed in config.py). Owner approval
                            needed for deletion.
    c -- "defer"          : Phase 1B / Stage 4 / future-phase config
                            (e.g. EMAIL_*, FORM_144_*); intentionally
                            unused in Stage 2.
    d -- "documentation"  : constant whose value is a string/dict
                            DOCUMENTING a decision or boundary (e.g.
                            FORK_FIRST_PRINCIPLE_NOTE, DEC_*_SUPERSEDED_BY,
                            BATCH_64_*); not a config flag at all.
    e -- "schema-spec"    : metadata about a data schema referenced
                            externally (dashboard / docs) but not by
                            runtime code yet.

REGISTRY purpose:
  - Pre-commit drift guard: this test fails if the *_unused-set_ in
    config.py changes without the registry being updated. Forces every
    new unreferenced constant to get classified.
  - Discoverability: the test serves as the live document of pending
    decisions per constant.

ACTIONABLE FOLLOW-UP (owner-approved separately):
  Once owner has reviewed the registry, follow-up batches can ship
  individual decisions (delete / implement / defer-mark) per constant.
  This batch does NOT make those decisions; it surfaces them.
"""
from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# CLASSIFICATION REGISTRY  (one entry per unused constant)
# --------------------------------------------------------------------------
# Each value is (class_letter, one_line_reason).
CLASSIFICATION: dict[str, tuple[str, str]] = {
    # --- a: implement now (Phase 1A-beta / pre-1B blocker if owner says ship) ---
    "WALK_FORWARD_FOLDS":             ("a", "DEC-505 fold count -- should be consumed by walk_forward_batch414_cells.py"),
    "TIER_3_POSITION_SIZE_PCT":       ("a", "Tier 3 sizing -- backtest engine should read"),
    "CASH_MANAGEMENT_TRIGGER_PCT":    ("a", "DEC-135 max-loss-cap analog -- engine should gate on this"),
    "DROPPED_STRATEGY_REEVAL_DAYS":   ("a", "Re-evaluation cooldown -- engine should respect after deprecation"),
    "TIER_3_MAX_TICKERS":             ("a", "Tier 3 universe cap (DEC-364) -- T3 builder should enforce"),
    "RR_RATIO_MINIMUM":               ("a", "DEC-426 R:R gate threshold -- should be the GATE_RR_MIN source"),
    "BURST_DAY_STRESS_START_YEAR":    ("a", "DEC-082 stress window start -- writer should slice"),
    "SECTOR_PASSING_CRITERIA":        ("a", "DEC-153 per-sector gates -- metrics.py should apply"),

    # --- b: delete (truly orphaned; pre-approved autonomous deletes) ---
    # Batch 468 (2026-05-29): all 25 (b) "delete" entries removed from
    # backtest/config.py per owner pre-approval. Registry's b-bucket is
    # now empty by design.

    # --- c: defer (intentionally unused in Stage 2; Phase 1B+ / Stage 4) ---
    "EMAIL_DAILY_SUMMARY_ENABLED":    ("c", "Stage 4 email gateway -- defer until Stage 4 starts"),
    "EMAIL_APPROVAL_GATEWAY_DISABLED": ("c", "Stage 4 email gateway"),
    "FORM_144_SOURCE_PRIORITY":       ("c", "Stage 4 Form 144 monitoring"),
    "PHASE_1D_START":                 ("c", "Phase 1D placeholder; defer"),
    "FINNHUB_SOCIAL_SENTIMENT_PHASE_1B_REVISIT": ("c", "Phase 1B+ deferred"),
    "AGENT_AB_DECAY_NET_SHARPE_FLOOR": ("c", "Phase 1B-beta agent A/B framework"),
    "AGENT_AB_NET_LIFT_FORMULA":      ("c", "Phase 1B-beta"),
    "AGENT_AB_THREE_CASE_PAIRING":    ("c", "Phase 1B-beta"),
    "AB_TEST_MIN_ARMS":               ("c", "Phase 1B-beta"),
    "AB_ORCHESTRATOR_MODULE_PATH":    ("c", "Phase 1B-beta"),
    "AB_ORCHESTRATOR_DETERMINISTIC_SEEDS": ("c", "Phase 1B-beta"),
    "FMP_FALLBACK_ENABLED":           ("c", "Future fundamentals source"),
    "FMP_SUBSCRIPTION_COST_USD_MO":   ("c", "Future cost projection"),
    "ORTEX_SHORT_INTEREST_STAGE_2_IN_SCOPE": ("c", "Sprint 5 ORTEX integration"),
    "ORTEX_HIGH_SHORT_THRESHOLD_PCT": ("c", "Sprint 5 ORTEX"),
    "ORTEX_SHORT_INTEREST_FIELDS":    ("c", "Sprint 5 ORTEX"),
    "POLYGON_OPTIONS_STAGE_2_IN_SCOPE": ("c", "Phase 1B+ options data"),
    "INSIDER_EXCLUDE_10B5_1_PLANNED": ("c", "Future insider-quality refinement"),
    "INSIDER_OFFICER_ROLE_WEIGHTS":   ("c", "P14 queue item -- future"),
    "EXIT_FIXED_TARGET_DEFAULTS":     ("c", "Future fixed-target exit family"),
    "PORTFOLIO_REBALANCE_VOL_DRIFT_PCT": ("c", "Future portfolio rebalancing"),
    "RR_RATIO_SWEEP_VALUES":          ("c", "Future R:R sweep optimization"),
    "QUIVER_PAID_ENDPOINTS":          ("c", "Future paid-tier upgrade"),
    "QUIVER_SUPPLEMENTAL_SOURCES":    ("c", "Future Quiver expansion"),
    "EARNINGS_TRANSCRIPTS_DROP_REASON": ("c", "Phase 1B+ earnings transcripts"),
    "EARNINGS_TIME_OF_DAY_VALUES":    ("c", "Future earnings timing"),

    # --- d: documentation (string/dict documenting a decision; not a flag) ---
    "BACKTEST_SEED_OUTPUT_FIELD":     ("d", "Documents the seed-output field name"),
    "CACHE_STORES_CORP_ACTIONS":      ("d", "Documents cache stores corp-actions"),
    "CANONICAL_FUNDAMENTALS_SOURCES": ("d", "Documents source-priority decision"),
    "CANONICAL_NEWS_SOURCE":          ("d", "Documents news-source decision"),
    "FUNDAMENTALS_SOURCE_PRIORITY":   ("d", "Documents priority order"),
    "FUNDAMENTALS_PIT_FILING_LAG_DAYS": ("d", "Documents PIT filing-lag policy"),
    "CI_REGRESSION_BEHAVIOR_ASSERTIONS": ("d", "Documents CI assertions"),
    "CI_REGRESSION_WORKFLOW_PATH":    ("d", "Documents workflow path"),
    "COLD_START_CI_MAX_MINUTES":      ("d", "Documents CI budget"),
    "COLD_START_CI_WORKFLOW_PATH":    ("d", "Documents workflow path"),
    "DIFFERENTIAL_TESTING_DEFENSE_LAYER": ("d", "Documents defense layer"),
    "DIFFERENTIAL_TESTING_TARGETS":   ("d", "Documents target list"),
    "GOLDEN_MASTER_TESTING_DEFENSE_LAYER": ("d", "Documents defense layer"),
    "GOLDEN_MASTER_TESTING_ARTIFACT_DIR": ("d", "Documents artifact dir"),
    "GOLDEN_MASTER_TESTING_DIFF_TOLERANCE": ("d", "Documents diff tolerance"),
    "PROPERTY_BASED_TESTING_DEFENSE_LAYER": ("d", "Documents defense layer"),
    "PROPERTY_BASED_TESTING_TARGETS": ("d", "Documents target list"),
    "STRATEGY_PROMOTION_REGISTER_PATH": ("d", "Documents register path"),
    "TEST_RUN_AUDIT_GATE_REQUIRED_FIELDS": ("d", "Documents audit gate fields"),
    "TEST_RUN_AUDIT_GATE_RESULTS_PATH": ("d", "Documents results path"),

    # --- e: schema-spec (metadata about a schema referenced externally) ---
    "AAII_EXTENDED_SCHEMA_VERSION":   ("e", "AAII schema version"),
    "EARNINGS_CACHE_DIR":             ("e", "Earnings cache directory"),
    "EARNINGS_CACHE_SCHEMA":          ("e", "Earnings cache schema spec"),
    "ICTSMC_CACHE_SCHEMA":            ("e", "ICT/SMC cache schema spec"),
    "OPTIONS_CHAIN_CACHE_DIR":        ("e", "Options cache directory"),
    "OPTIONS_CHAIN_CACHE_SCHEMA":     ("e", "Options cache schema spec"),
    "SEC_EDGAR_DIFFERENTIAL_CACHE_DIR": ("e", "SEC EDGAR cache directory"),
    "POLYGON_CORP_ACTIONS_API_PATHS": ("e", "Polygon API path list"),
    "POLYGON_STOCKS_STARTER_TIER":    ("e", "Polygon tier name"),
    "POLYGON_TIER_HISTORY_YEARS":     ("e", "Polygon tier history depth"),
    "FUNDAMENTALS_REQUIRED_FIELDS":   ("e", "Fundamentals required-fields schema"),
    "FUNDAMENTALS_COMPUTED_FIELDS":   ("e", "Fundamentals computed-fields schema"),
    "NASDAQ_SYMBOL_DIFF_THRESHOLD_USD": ("e", "NASDAQ symbol-diff threshold"),
    "NASDAQ_SYMBOL_DIRECTORY_URL":    ("e", "NASDAQ directory URL"),
    "OUR_AGENT_STATE_EXTENDS":        ("e", "Agent state inheritance spec"),
    "OUR_AGENT_STATE_NEW_FIELDS":     ("e", "Agent state new fields"),
    "CROSS_ASSET_STRATEGIES":         ("e", "Cross-asset strategy list spec"),
    "PARALLEL_BACKTEST_EXECUTOR":     ("e", "Executor type spec"),
    "TIER_3_MOMENTUM_LOOKBACK_DAYS":  ("e", "T3 momentum lookback spec"),
    "TIER_3_MOMENTUM_METHODOLOGY":    ("e", "T3 momentum methodology spec"),
    "TIER_3_MOMENTUM_RISK_ADJUSTMENT": ("e", "T3 momentum risk-adjustment spec"),
    "TIER_3_MOMENTUM_SKIP_DAYS":      ("e", "T3 momentum skip days"),
    "TIER_3_MOMENTUM_TIE_BREAKERS":   ("e", "T3 momentum tie-breakers"),
}


def _scan_unused_constants() -> list[str]:
    """Replicate the AU7 unused-constants sweep: top-level UPPERCASE
    constants in backtest/config.py with no whole-word reference in any
    non-test, non-config file under backtest/ + scripts/."""
    config_text = (REPO / "backtest" / "config.py").read_text(encoding="utf-8")
    constants = {m.group(1)
                 for m in re.finditer(r"^([A-Z][A-Z0-9_]+)\s*=",
                                        config_text, flags=re.MULTILINE)}
    files = []
    for sub in ("backtest", "scripts"):
        root = REPO / sub
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if "tests" in p.parts:
                continue
            if p.name == "config.py":
                continue
            files.append(p)
    ref_re = {c: re.compile(rf"\b{c}\b") for c in constants}
    unused = []
    for c in sorted(constants):
        found = False
        for p in files:
            try:
                t = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if ref_re[c].search(t):
                found = True
                break
        if not found:
            unused.append(c)
    return unused


def test_registry_covers_all_unused_constants():
    """Drift guard: every actually-unused constant in config.py must have
    an entry in CLASSIFICATION. If this fails, a new unreferenced constant
    was added without classification -- update CLASSIFICATION before
    landing the config change."""
    unused = set(_scan_unused_constants())
    classified = set(CLASSIFICATION.keys())
    missing = sorted(unused - classified)
    assert not missing, \
        f"{len(missing)} unused constants are not in CLASSIFICATION: {missing[:20]}{'...' if len(missing) > 20 else ''}. " \
        "Add each to the registry with class letter + reason."


def test_registry_has_no_stale_entries():
    """Drift guard (reverse): if a classified constant is now USED, it
    should be removed from CLASSIFICATION (otherwise the registry lies)."""
    unused = set(_scan_unused_constants())
    classified = set(CLASSIFICATION.keys())
    stale = sorted(classified - unused)
    assert not stale, \
        f"{len(stale)} CLASSIFICATION entries are now consumed " \
        f"(remove from registry): {stale}"


def test_every_class_letter_in_legal_set():
    """All classification letters must be one of a/b/c/d/e."""
    legal = {"a", "b", "c", "d", "e"}
    bad = {k: v for k, v in CLASSIFICATION.items() if v[0] not in legal}
    assert not bad, \
        f"Illegal classification letters in registry: {bad}"


def test_classification_distribution_reported():
    """Print classification distribution for visibility (no assertion)."""
    counts: dict[str, int] = {}
    for letter, _reason in CLASSIFICATION.values():
        counts[letter] = counts.get(letter, 0) + 1
    total = sum(counts.values())
    # Sanity: registry total should match the actual scan count.
    unused_count = len(_scan_unused_constants())
    assert total == unused_count, \
        f"registry size {total} != actual unused {unused_count}"
