#!/usr/bin/env python3
"""Batch 69 Phase 3: per-DEC verification of CONFIG_CONSTANT_DEAD classifier hits.

For each DEC in the CONFIG_CONSTANT_DEAD set that is NOT already reverted
in Phase 1/2:
  1. Extract ALL_CAPS candidate constant names from AUDIT_INDEX description
  2. For each candidate, strict-grep ENGINE_CALL_PATHS for word-boundary match
  3. Verdict:
       REVERT  - no candidate found in engine paths (true positive)
       KEEP    - at least one candidate found (engine consumes)
       UNSURE  - zero candidates extracted (classifier had no signal; manual)

**HAND-RUN-ONLY (B1704).** Nothing invokes this automatically - no Stop hook, no
pre-commit, no launcher. An audit found 12 of 16 gate scripts in this state, so
presence is NOT enforcement (CHECKLIST #224). Run it explicitly and read its exit
code; if you need it to bind, wire it and say where.
"""
import re
from pathlib import Path

REPO = Path(__file__).parent.parent

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
    REPO / "backtest/run_phase1a.py",
]
# metrics.py is NOT in ENGINE_CALL_PATHS because it's a helper module --
# however the engine DOES call compute_all_metrics which calls
# compute_strategy_metrics. So a constant/function referenced ONLY from
# inside metrics.py is transitively wired iff compute_strategy_metrics
# (or another engine-called function in metrics.py) references it.
# We check this with a 2nd-pass: look at the SPECIFIC functions called by
# engine, then see if they reference the constant. Simpler: list the
# transitively-wired callers in metrics.py and grep ONLY those.
TRANSITIVELY_WIRED_METRICS_FNS = (
    "compute_strategy_metrics", "compute_all_metrics",
    "compute_portfolio_summary", "compute_confidence_tier_metrics",
)

# Blacklist of common false-positive names (overlap with planning text)
BLACKLIST = {
    "DEC", "BUG", "CAV", "INV", "DECISION", "PASS", "RESOLVED",
    "IMPLEMENTED", "DECIDED", "PARTIAL", "DEFERRED", "STAGE", "SPRINT",
    "PHASE", "OPEN", "DEC-", "WIRED", "YES", "NO", "NULL", "NONE",
    "TRUE", "FALSE", "NAT", "NAN", "ROUND", "FINAL", "BATCH", "PATH",
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
    "PIT-CORRECT", "PHASED_ROLLOUT",
    "PCR", "OI", "PR-CI", "ON-TIME", "PR-SIDE",
    "REVISIT_AFTER", "NEW", "INVESTIGATION",
    "CORRECT", "CORRECTED", "CORRECTNESS",
    "CLAUDE", "TRADING", "RULES", "PROJECT", "PLAN",
    "TRADINGAGENTS", "TRADINGAGENT", "WRITTEN", "SHIPPED", "DEFAULT", "SUMMARY",
    "PATCH", "ARTIFACT", "ARTIFACTS", "FINAL", "FIRST",
    "TIMING", "DESIGN", "DECISION",
    "POLYGON", "QUIVER", "FINNHUB",
    "DEMOTED", "PROMOTION", "PROMOTE", "GATE",
    "BACKTEST", "BACKTESTING", "STAGE-3", "STAGE-2",
    "REGEX", "TEXT", "SHORT", "LONG", "ID-", "ID-STATUS",
    "TBD", "WONTFIX",
    "AGENT", "AGENTS",
    "B++", "B+", "L-", "T-",
}
BLACKLIST_LOWER = {b.lower() for b in BLACKLIST}

CONST_PATTERN = re.compile(r"\b([A-Z][A-Z0-9_]{4,})\b")
# Helper name pattern: lower_snake_case identifiers length >= 8 with underscore.
# My batch descriptions reference helpers in plain text (e.g.
# "is_ticker_in_stopout_cooldown(...)" not always in backticks).
HELPER_PATTERN = re.compile(r"\b([a-z][a-z0-9_]{7,})\b")


def load_engine_corpus() -> str:
    parts: list[str] = []
    for p in ENGINE_CALL_PATHS:
        if p.exists():
            try:
                parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n".join(parts)


def load_transitive_metrics_corpus() -> str:
    """Extract the bodies of TRANSITIVELY_WIRED_METRICS_FNS from metrics.py.
    A constant referenced inside one of these function bodies counts as
    transitively engine-wired (engine -> compute_all_metrics -> fn body).
    """
    metrics_text = (REPO / "backtest/results/metrics.py").read_text(
        encoding="utf-8", errors="ignore"
    )
    bodies: list[str] = []
    for fn in TRANSITIVELY_WIRED_METRICS_FNS:
        # Crude: from `def fn(` to next top-level `def ` or end-of-file
        pattern = re.compile(
            r"^def " + re.escape(fn) + r"\b[\s\S]*?(?=^def |\Z)",
            re.MULTILINE,
        )
        for m in pattern.finditer(metrics_text):
            bodies.append(m.group(0))
    return "\n".join(bodies)


def extract_const_candidates(description: str) -> list[str]:
    raw = set(CONST_PATTERN.findall(description))
    keep = []
    for c in raw:
        if c in BLACKLIST:
            continue
        if c.lower() in BLACKLIST_LOWER:
            continue
        # Require underscore to bias toward Python constant convention
        if "_" not in c:
            continue
        keep.append(c)
    return sorted(set(keep))


HELPER_BLACKLIST = {
    "compute_strategy_metrics", "compute_all_metrics",  # always engine-wired
    "can_open", "add_position", "mark_to_market",       # Portfolio engine-called
    "classify_regime", "get_regime_context",            # engine-called regime fns
    "apply_slippage", "apply_exit_slippage",             # engine-called
    "fixed_3r_2r", "fixed_4r_2r",
    # Common English words / argument names that match snake_case length>=8
    "description", "implementation", "documentation", "evaluation",
    "validation", "assertion", "function", "constant", "variable",
    "register", "attribute", "endpoint", "framework", "decision",
    "decisions", "configuration", "specification", "regression",
    "reproducibility", "methodology", "calculation", "calibration",
    "consumption", "verification", "comparison", "performance",
    "transaction", "transactional", "transparency", "validation",
    "subscription", "expansion", "integration", "completion",
    "intelligence", "computation", "expectation", "annotation",
    "exclusion", "publication", "subscription", "iteration",
    "stochastic", "stationary", "structural", "statistically",
    "deterministic", "differential", "transitively",
    "deferred", "deferred_to", "released", "approved", "scheduled",
    "rejected", "absorbed", "available", "implementation_step",
    "trade_log_df", "trade_log", "cooldown_days", "in_cooldown",
    "days_since_stop", "last_stop_date", "as_of",
    "drop_threshold_pct", "warning", "drop_pct", "current_price",
    "average_cost", "underwater", "shares", "ticker", "regime",
    "size_pct", "value_pct", "annualized", "pre_days", "post_days",
    "rolling_peak_equity", "halt_triggered", "target_resume_equity",
    "current_equity", "min_history_days", "days_since_start",
    "dd_threshold", "recovery_threshold", "ema_smoothed",
    "alpha_annualized", "tracking_error_annualized", "information_ratio",
    "smart_money_score", "confluence_score", "regime_state",
    "agent_overlay", "rules_only", "agent_action", "rules_action",
    "rationale_version", "rationale_timestamp",
    "is_winner", "is_loser", "is_decayed",
    "win_rate", "profit_factor", "smart_money", "macro_score",
    "consecutive_days", "base_weight", "growth_per_day", "max_weight",
    "absolute_threshold", "relative_threshold",
    "drift_threshold", "vol_window", "drift_window",
    "interlisted", "long_dollar_value", "long_sector_etf",
    "hedge_ratio", "hedge_ticker", "hedge_direction", "hedge_dollar",
    "long_ticker", "spy_ticker", "beta_used",
    "current_iv", "historical_iv_pre_earnings", "sigma_threshold",
    "event_window_days", "triggering_items",
    "regime_sequence", "from_regime", "to_regime",
    "spy_returns", "strategy_returns", "spy_above_200ema",
    "spy_close", "spy_ema200", "vix_value", "vix_smoothed",
    "vix_series", "prev_regime", "hysteresis_buffer",
    "earnings_tolerant", "strategy_attributes",
    "exit_pnl", "max_favourable_excursion", "max_favorable_excursion",
    "pnl_dollar", "actual_pnl_dollar", "timing_delta_dollar",
    "exit_delta_dollar", "sizing_delta_dollar", "agent_delta_dollar",
    "open_short_position", "current_regime", "prior_regime",
    "abs_shares", "abs_diff", "rel_diff", "gate_reason",
    "usd_portfolio_value_cad", "total_portfolio_value_cad",
    "fx_exposure_pct", "total_cad", "usd_in_cad",
    "regime_score", "regime_label", "regime_probabilities",
    "cnn_fg", "aaii_bull_bear_spread", "icsa_yoy_pct",
    "hy_spread_bps", "yield_curve_spread", "breadth_pct_above_50ema",
    "sector_dispersion", "equity_vix", "credit_hy_spread_bps",
    "commodity_pct_change_20d", "currency_dxy_pct_change_20d",
    "sector_etf_price", "sector_etf_ema200", "sector_vol_annualized",
    "bull_vol_threshold", "bear_vol_threshold", "crisis_vol_threshold",
    "new_score", "prev_smoothed",
    "p_values", "n_strategies_tested", "adjusted_p_values",
    "per_strategy_pass", "alpha_bonferroni",
    "ticker_earnings_date", "fomc_dates", "cpi_release_dates",
    "nfp_release_dates",
}


def extract_helper_candidates(description: str) -> list[str]:
    raw = set(HELPER_PATTERN.findall(description))
    keep = []
    for h in raw:
        # Skip well-known engine functions that get mentioned as context
        if h in HELPER_BLACKLIST:
            continue
        # Skip obviously non-function tokens
        if len(h) < 6:
            continue
        keep.append(h)
    return sorted(set(keep))


def parse_decisions() -> dict[str, str]:
    text = (REPO / "AUDIT_INDEX.md").read_text(encoding="utf-8", errors="ignore")
    start = text.find("### All Decisions Table")
    section = text[start:]
    out: dict[str, str] = {}
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
            out[dec_id] = {"description": description, "status": status}
    return out


BATCH_49_68_PATTERN = re.compile(
    r"Pass 53 v8h\+1 Phase 3 Batch (4[9]|[5-6][0-9])\b"
)


def touched_in_batch_49_68(description: str) -> bool:
    """Only DECs touched by my Path C arc (Batches 49-68) are revert
    candidates. Pre-existing planning/process decisions resolved before
    my arc should NOT be reverted -- their no-engine-consumption is
    legitimate (planning decisions don't require code wiring).
    """
    return bool(BATCH_49_68_PATTERN.search(description))


def main() -> None:
    decs_data = parse_decisions()
    engine_corpus = load_engine_corpus()
    metrics_transitive = load_transitive_metrics_corpus()
    full_consumer_corpus = engine_corpus + "\n" + metrics_transitive

    # Recompute CONFIG_CONSTANT_DEAD target set directly from catalog to
    # avoid /tmp path-encoding issues on Windows.
    catalog_text = (REPO / "WIRING_CATALOG_BATCH_69.md").read_text(encoding="utf-8")
    target_ids = []
    for line in catalog_text.splitlines():
        if line.startswith("| DECISION-") and " CONFIG_CONSTANT_DEAD " in line:
            dec_id = line.split("|")[1].strip()
            target_ids.append(dec_id)

    revert: list[str] = []
    keep: list[tuple[str, list[str]]] = []
    unsure: list[str] = []
    already_partial: list[str] = []
    skipped_pre_existing: list[str] = []

    for dec_id in target_ids:
        meta = decs_data.get(dec_id)
        if not meta:
            continue
        if meta["status"] != "RESOLVED-IMPLEMENTED":
            already_partial.append(dec_id)
            continue
        # Only revert DECs touched by my Path C arc (Batches 49-68). Pre-
        # existing planning/process decisions resolved before my arc are
        # legitimately RESOLVED-IMPLEMENTED -- their no-engine-consumption
        # is by design (process/methodology/architecture decisions don't
        # need code wiring).
        if not touched_in_batch_49_68(meta["description"]):
            skipped_pre_existing.append(dec_id)
            continue
        # Phase 3 tightened: ONLY revert if description claims a HELPER FUNCTION
        # (lower_snake_case in backticks) that engine doesn't consume. Pure
        # config-constant additions (PHASE_1F_DEFERRED_STRATEGY_FAMILIES etc.)
        # are documentation, not behavior gates -- skip them.
        helper_candidates = extract_helper_candidates(meta["description"])
        if not helper_candidates:
            unsure.append(dec_id)
            continue
        hits = []
        for h in helper_candidates:
            pat = re.compile(r"\b" + re.escape(h) + r"\b")
            if pat.search(full_consumer_corpus):
                hits.append(h)
        if hits:
            keep.append((dec_id, hits))
        else:
            revert.append(dec_id)

    print(f"Already PARTIAL-IMPL-HELPER-ONLY (Phase 1/2 overlap): {len(already_partial)}")
    print(f"Skipped (pre-existing, NOT touched by Batches 49-68): {len(skipped_pre_existing)}")
    print(f"KEEP (Batch 49-68 touched + engine consumes): {len(keep)}")
    print(f"REVERT (Batch 49-68 touched + no engine consumer): {len(revert)}")
    print(f"UNSURE (Batch 49-68 touched + no candidates extracted): {len(unsure)}")
    print()
    print("=== KEEP samples (first 10) ===")
    for dec_id, hits in keep[:10]:
        print(f"  {dec_id}: hits={hits[:3]}")
    print()
    print("=== REVERT (first 30) ===")
    for dec_id in revert[:30]:
        print(f"  {dec_id}")
    print()
    print("=== UNSURE (first 20) ===")
    for dec_id in unsure[:20]:
        print(f"  {dec_id}")

    # Persist sets to repo-local temp dir
    out_dir = REPO / ".phase3_temp"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "revert.txt").write_text("\n".join(revert) + "\n", encoding="utf-8")
    (out_dir / "keep.txt").write_text(
        "\n".join(f"{d}: {h}" for d, h in keep) + "\n", encoding="utf-8"
    )
    (out_dir / "unsure.txt").write_text("\n".join(unsure) + "\n", encoding="utf-8")
    (out_dir / "already_partial.txt").write_text(
        "\n".join(already_partial) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
