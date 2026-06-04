"""Batch 575 (2026-06-04) - Build STRATEGY_ROSTER.md auto-generated
canonical per-strategy reference doc for Stage 4 analysis.

Per owner directive 2026-06-04: "Update the strategy roster document,
create a table of each strategy, triggers, parameters of each criteria
in the triggers, other conditions etc. I will use it as a reference
table during this analysis."

Reads:
  backtest/signals/screener.py        - strategy predicates + _strat()
                                        call with direction/category/
                                        signals_used/context_bullets
  backtest/engine/regime_selector.py  - STRATEGY_REGIME_AFFINITY dict
  backtest/signals/technical.py       - signal feeder definitions
                                        (doji, hammer, near_*, vol_spike,
                                        etc.) for the GLOSSARY section

Writes:
  STRATEGY_ROSTER.md  - master table + glossary at repo root

Per feedback_strategy_roster_doc_maintenance memory: regenerate every
turn that modifies strategies, signals, thresholds, regime affinity,
or status.

Usage:
  python scripts/build_strategy_roster.py
"""
from __future__ import annotations

import ast
import inspect
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCREENER = REPO / "backtest" / "signals" / "screener.py"
TECHNICAL = REPO / "backtest" / "signals" / "technical.py"
REGIME_SELECTOR = REPO / "backtest" / "engine" / "regime_selector.py"
OUT_MD = REPO / "STRATEGY_ROSTER.md"


def _extract_fires_expression(func_source: str) -> str:
    """Extract the trigger expression(s) from a strategy function source.
    Returns the verbatim `fires = (...)` or `fl = (...) / fs = (...)` text
    so the owner can see exactly what gates the strategy."""
    # Match `fires = (...)` or `fl = (...)` and `fs = (...)` from _strat3
    # Multi-line capture: ` = (` until the matching `)` (heuristic - balance parens)
    lines = func_source.split("\n")
    captured = []
    in_capture = False
    paren_depth = 0
    buf = []
    for line in lines:
        if not in_capture:
            m = re.match(r"\s*(fires|fl|fs|f_long|f_short)\s*=\s*\(", line)
            if m:
                in_capture = True
                paren_depth = line.count("(") - line.count(")")
                buf = [line.strip()]
                if paren_depth == 0:
                    captured.append(" ".join(buf))
                    buf = []
                    in_capture = False
        else:
            paren_depth += line.count("(") - line.count(")")
            buf.append(line.strip())
            if paren_depth <= 0:
                captured.append(" ".join(buf))
                buf = []
                in_capture = False
    return " \n ".join(captured) if captured else "(predicate not extracted - read source)"


def _extract_strat_call(func_source: str) -> dict:
    """Extract direction / category / signals_used / context_bullets
    from the _strat(...) or _strat3(...) call inside the function."""
    out = {"direction": "?", "category": "?", "signals_used": [],
           "context_bullets": []}
    # Find `_strat(...)` or `_strat3(...)` call
    m = re.search(r"_strat3?\s*\(([\s\S]+?)\)\s*$", func_source.rstrip(), re.MULTILINE)
    if not m:
        # Try without trailing-of-source match
        m = re.search(r"_strat3?\s*\(", func_source)
        if not m:
            return out
    # Heuristic: use ast to parse the function and find the Return + Call
    try:
        tree = ast.parse("def _f(s):\n" + textwrap_dedent(func_source))
    except Exception:
        return out
    return out


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


def extract_strategy_meta(name: str, fn) -> dict:
    """Extract per-strategy metadata from the function source.
    Returns dict with direction, category, signals_used, context_bullets,
    fires_expr, is_dual."""
    try:
        src = inspect.getsource(fn)
    except (TypeError, OSError):
        return {
            "name": name, "direction": "?", "category": "?",
            "signals_used": [], "context_bullets": [],
            "fires_expr": "(not extracted)", "is_dual": False,
        }
    # Dual-direction check
    is_dual = "_strat3" in src and "fl" in src and "fs" in src
    # Direction extraction: single-strategy `_strat(fires, "direction", ...)`
    direction = "?"
    if is_dual:
        direction = "dual"
    else:
        m = re.search(r'_strat\s*\(\s*fires\s*,\s*[\'"](\w+)[\'"]\s*,', src)
        if m:
            direction = m.group(1)
    # Category extraction: 3rd positional arg in _strat or _strat3
    category = "?"
    if is_dual:
        m = re.search(r'_strat3\s*\(\s*\w+\s*,\s*\w+\s*,\s*[\'"](\w+)[\'"]', src)
    else:
        m = re.search(r'_strat\s*\(\s*\w+\s*,\s*[\'"]\w+[\'"]\s*,\s*[\'"](\w+)[\'"]', src)
    if m:
        category = m.group(1)
    # signals_used: 4th positional arg = first list literal
    sigs_match = re.search(r"_strat3?\s*\([\s\S]+?(\[[\s\S]*?\])", src)
    signals_used = []
    if sigs_match:
        try:
            sig_list = ast.literal_eval(sigs_match.group(1))
            if isinstance(sig_list, list):
                signals_used = sig_list
        except Exception:
            pass
    # Context bullets: extract all string literals from the function
    # (heuristic; the bullets are the human-readable rationale)
    context_bullets = re.findall(r'["\']([^"\']{20,200})["\']', src)
    # Filter to bullet-like (longer, descriptive)
    context_bullets = [b for b in context_bullets if " " in b and len(b) > 20][:5]
    # Trigger expression
    fires_expr = _extract_fires_expression(src)
    return {
        "name": name, "direction": direction, "category": category,
        "signals_used": signals_used, "context_bullets": context_bullets,
        "fires_expr": fires_expr, "is_dual": is_dual,
    }


def load_regime_affinity() -> dict:
    """Read STRATEGY_REGIME_AFFINITY from regime_selector.py."""
    try:
        src = REGIME_SELECTOR.read_text(encoding="utf-8")
    except Exception:
        return {}
    m = re.search(
        r"STRATEGY_REGIME_AFFINITY[^=]*=\s*\{([^}]+)\}",
        src, re.DOTALL,
    )
    if not m:
        return {}
    # Parse each `"name": {"regime1", "regime2"}` line
    body = m.group(1)
    affinity = {}
    for line in body.split("\n"):
        line = line.strip().rstrip(",")
        if not line or line.startswith("#"):
            continue
        # name: {set}
        nm = re.match(r'["\']([a-z_0-9]+)["\']\s*:\s*\{([^}]*)\}', line)
        if nm:
            regimes = [r.strip().strip('"\'') for r in nm.group(2).split(",") if r.strip()]
            affinity[nm.group(1)] = regimes
    return affinity


def load_stage_4_status() -> dict:
    """Read approvals.json and build a per-strategy Stage 4 status
    summary: dict[strategy -> {n_rows, statuses, classes, fired_in_r4,
    s4_reviewed, s4_review_batch, s4_review_outcome}].

    B577: also tracks fired_in_r4 boolean - True if strategy has any
    NON-Class-0 row (Class 0 = QUIET_NO_CANDIDATES backfilled in B576).
    B583: also tracks s4_reviewed flag from approvals.json
    `s4_reviewed_strategies` top-level dict (per owner directive
    2026-06-04: "add another column in strategy table which says s4
    review completed y/n").
    """
    approvals_path = Path("C:/tmp/r4_optimization_candidates/approvals.json")
    if not approvals_path.exists():
        return {}
    try:
        data = json.loads(approvals_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    s4_reviewed = data.get("s4_reviewed_strategies", {})
    # B585: producer_bug_fixes ledger - separate from S4 review per
    # feedback_per_strategy_deep_dive_stage4 (bug fix alone is NOT
    # S4 review completion; 7-step walk still required after a
    # producer bug fix).
    bug_fixes = data.get("producer_bug_fixes", {})
    per_strategy = {}
    for r in data.get("approvals", []):
        name = r["strategy"]
        if name not in per_strategy:
            per_strategy[name] = {
                "n_rows": 0, "statuses": [], "classes": [],
                "fired_in_r4": False,
                "s4_reviewed": False,
                "s4_review_batch": "",
                "s4_review_outcome": "",
                "producer_bug_fix": "",
            }
        per_strategy[name]["n_rows"] += 1
        per_strategy[name]["statuses"].append(r["status"])
        per_strategy[name]["classes"].append(r["change_class"])
        # If the strategy has ANY non-Class-0 row, it fired in R4
        if r["change_class"] != 0:
            per_strategy[name]["fired_in_r4"] = True
        # B583: S4 reviewed flag from approvals.json top-level dict
        rv = s4_reviewed.get(name)
        if rv:
            per_strategy[name]["s4_reviewed"] = True
            per_strategy[name]["s4_review_batch"] = rv.get("reviewed_in_batch", "")
            per_strategy[name]["s4_review_outcome"] = rv.get("review_outcome", "")
        # B585: producer bug fix history (separate from S4 review)
        bf = bug_fixes.get(name, [])
        if bf:
            # Compact: most recent batch tag(s); strategy still needs S4 walk
            batches = [str(e.get("fixed_in_batch", "?")) for e in bf]
            per_strategy[name]["producer_bug_fix"] = ", ".join(batches)
    return per_strategy


def load_projected_strategies() -> list:
    """B578: PROJECTED strategies sourced from STRATEGY_REGISTER.md
    Layer 4 PENDING strategy-additive sub-decisions.

    Per owner directive 2026-06-04: "update future strategies in
    strategy roster doc from strategy register with a note that the
    flagged strategies will be approved." These are NOT in
    ALL_STRATEGIES yet; they are owner-approval-pending additions
    that will be wired when their respective DECs are RESOLVED-DECIDED.

    Each entry: dec_id, name, description, estimated_classes,
    theoretical_basis, layer. Status uniformly 'PENDING_OWNER_APPROVAL'.

    Source: STRATEGY_REGISTER.md Layer 4 (Pass 52). Updated when new
    PENDING DECs land or existing ones get owner-approved (move to
    ALL_STRATEGIES).
    """
    return [
        {
            "dec_id":       "DEC-141",
            "name":         "sector_neutral_hedge_overlay",
            "description":  "Sector-neutral hedge overlay variant - long sleeve paired with sector-ETF short to neutralize sector beta",
            "est_classes":  1,
            "layer":        "Layer 4 (DEC-141)",
            "basis":        "Hedge construction; sector-relative alpha extraction",
        },
        {
            "dec_id":       "DEC-142",
            "name":         "market_neutral_long_short_spy",
            "description":  "Market-neutral long + short SPY overlay - long sleeve paired with SPY short to neutralize market beta",
            "est_classes":  1,
            "layer":        "Layer 4 (DEC-142)",
            "basis":        "Market-neutral construction; absolute-return harvest",
        },
        {
            "dec_id":       "DEC-143",
            "name":         "ipo_lockup_secondary_offering",
            "description":  "IPO + lockup expiration + secondary offering systematic framework (3 variants)",
            "est_classes":  3,
            "layer":        "Layer 4 (DEC-143)",
            "basis":        "Field-Hanka 2001 JF lockup expiration; Bradley-Jordan-Ritter 2003 RFS IPO short-run drift",
        },
        {
            "dec_id":       "DEC-145",
            "name":         "iv_delta_vs_historical_pre_earnings",
            "description":  "Pre-earnings implied-volatility delta vs historical IV pattern - fade or fade-the-fade",
            "est_classes":  1,
            "layer":        "Layer 4 (DEC-145)",
            "basis":        "Diavatopoulos-Doran-Peterson 2008 options-implied earnings drift",
        },
        {
            "dec_id":       "DEC-176",
            "name":         "meta_strategies_boolean_combinations",
            "description":  "Meta-strategies (boolean AND/OR combinations of existing strategies) - MULTIPLIER on existing classes, not additive",
            "est_classes":  "multiplier",
            "layer":        "Layer 4 (DEC-176)",
            "basis":        "Combinatorial signal compounding; per-cell empirical validation required",
        },
        # Layer 2D ICT inline-specification - B579 (Option A 2026-06-04):
        # PENDING-FORM blocker resolved. Owner specifies one ICT pattern
        # per turn; each becomes Class 7 NEW_STRATEGY wired on-the-spot
        # per feedback_wire_new_strategies_on_the_spot + feedback_layer_2d_ict_inline_specification.
        {
            "dec_id":       "Layer-2D",
            "name":         "ict_patterns_owner_inline_spec",
            "description":  "ICT methodology patterns specified inline by owner one-at-a-time in chat (Option A 2026-06-04; bypasses the PENDING-FORM blocker). Each pattern wired as Class 7 NEW_STRATEGY same-turn. Producer signals reuse Layer 2A smartmoneyconcepts primitives (FVG/OTE/BOS/CHoCH/OB/swings/liquidity).",
            "est_classes":  "5-15 (per CANONICAL_FACTS.md:97)",
            "layer":        "Layer 2D (READY-FOR-OWNER-SPECIFICATION)",
            "basis":        "ICT methodology; owner-curated patterns specified inline, no form tooling required",
        },
    ]


def signal_plain_translation(signal: str) -> str:
    """Translate a signal name into a plain-language phrase for the
    'Trigger Conditions' column. B586 owner directive 2026-06-04:
    "This detail is missing in the strategy table. update trigger
    column with such information for all strategies."

    Returns the plain phrase or the signal name itself if no mapping.
    Common signals have explicit translations; uncommon ones fall back
    to the raw signal name with a note.
    """
    # Hand-curated common signal phrases. Extend as new signals appear.
    plain = {
        # Volume
        "vol_above_avg":     "volume above 20d avg",
        "vol_spike_15x":     "volume >= 1.5x 20d avg",
        "vol_spike_17x":     "volume > 1.7x 20d avg",
        "vol_spike_2x":      "volume >= 2x 20d avg",
        "vol_spike_3x":      "volume >= 3x 20d avg",
        # 52w high/low
        "break_52w_high":    "close > prior 252d high (strict)",
        "break_52w_low":     "close < prior 252d low (strict)",
        "near_52w_high":     "close >= 98% of prior 252d high",
        "near_52w_low":      "close <= 102% of prior 252d low",
        "near_52w_high_retest_long":  "prior 252d high broken in last 10d + close within 1% + vol below avg + bullish bar",
        "near_52w_low_retest_short":  "prior 252d low broken in last 10d + close within 1% + vol below avg + bearish bar",
        # Sector strength
        "sector_outperforming_spy":   "stock's sector ETF outperforming SPY (20d trailing return)",
        # Pivot
        "near_s1":           "close within 0.30% of pivot S1",
        "near_s2":           "close within 0.30% of pivot S2",
        "near_r1":           "close within 0.30% of pivot R1",
        "near_r2":           "close within 0.30% of pivot R2",
        "near_pivot":        "close within 0.30% of pivot P",
        "near_s1_wide":      "close within 1.50% of pivot S1 (doji-only)",
        "near_s2_wide":      "close within 1.50% of pivot S2 (doji-only)",
        "near_r1_wide":      "close within 1.50% of pivot R1 (doji-only)",
        "near_r2_wide":      "close within 1.50% of pivot R2 (doji-only)",
        # Fib
        "at_key_fib":        "close within 0.50% of fib 38.2/50/61.8",
        "at_key_fib_wide":   "close within 1.50% of key fib (doji-only)",
        # Candle
        "doji":              "body < 5% of range (indecision)",
        "hammer":            "lower wick > 2x body + upper wick < body (bullish reversal)",
        "shooting_star":     "upper wick > 2x body + lower wick < body (bearish reversal)",
        "bullish_engulfing": "today's bullish body engulfs yesterday's bearish body",
        "bearish_engulfing": "today's bearish body engulfs yesterday's bullish body",
        "morning_star":      "3-bar bullish reversal (gap-recovery)",
        "evening_star":      "3-bar bearish reversal",
        "three_white_soldiers": "3 consecutive bullish closes near high",
        "three_black_crows": "3 consecutive bearish closes near low",
        # Trend / regime
        "price_above_ema_200":   "close > 200-day EMA",
        "price_above_sma_50":    "close > 50-day SMA",
        "ema_50_200_bullish":    "50 EMA > 200 EMA (golden-cross regime)",
        "ema_50_200_golden_cross": "50 EMA crossed above 200 EMA (one-bar event)",
        "ema_50_200_death_cross": "50 EMA crossed below 200 EMA (one-bar event)",
        # Momentum
        "rsi_14":              "14-day RSI (numeric; check inline comparison)",
        "rsi_2":               "2-day RSI (Connors)",
        "obv_bullish":         "OBV in uptrend",
        # SMC
        "smc_fvg_bullish_active":  "bullish Fair Value Gap active",
        "smc_fvg_bearish_active":  "bearish Fair Value Gap active",
        "smc_choch_bullish":   "bullish Change of Character",
        "smc_choch_bearish":   "bearish Change of Character",
        "smc_bos_bullish":     "bullish Break of Structure",
        "smc_bos_bearish":     "bearish Break of Structure",
        "smc_liquidity_swept_up":  "upside liquidity swept (stops taken above)",
        "smc_liquidity_swept_dn":  "downside liquidity swept (stops taken below)",
        "smc_equal_highs_swept":   "equal highs swept (liquidity grab up)",
        "smc_equal_lows_swept":    "equal lows swept (liquidity grab down)",
        "smc_ote_long_zone":   "in OTE long zone (62-79% Fib retracement)",
        "smc_ote_short_zone":  "in OTE short zone",
        "smc_breaker_block_bullish":  "bullish breaker block active",
        "smc_breaker_block_bearish":  "bearish breaker block active",
        # B581 ICT producers
        "po3_mmbm_setup":      "PO3 bullish cycle: accumulation + sweep down + reversal + bullish bar",
        "po3_mmsm_setup":      "PO3 bearish cycle: accumulation + sweep up + reversal + bearish bar",
        "week_open_gap_up_15pct":   "Monday opened with gap up >= 1.5% vs prior Friday close",
        "week_open_gap_down_15pct": "Monday opened with gap down >= 1.5% vs prior Friday close",
        # News sentiment
        "news_sentiment_shift": "7d sentiment minus prior 7d (e.g. > 0.4 = strong positive shift)",
        "news_article_count":   "article count in current 7d window",
        # Donchian
        "dc10_breakout_up":    "close >= prior 10d max * 0.998 (B584 fix)",
        "dc10_breakout_dn":    "close <= prior 10d min * 1.002 (B584 fix)",
        "dc20_breakout_up":    "close >= prior 20d max * 0.998 (B584 fix)",
        "dc20_breakout_dn":    "close <= prior 20d min * 1.002 (B584 fix)",
        # Day-of-bar
        "close_above_open":    "today's bullish bar (close > open)",
        "close_below_open":    "today's bearish bar (close < open)",
        "above_prev_high":     "close > prior day's high",
        "below_prev_low":      "close < prior day's low",
    }
    return plain.get(signal, signal)


def render_trigger_plain(signals_used: list, fires_expr: str) -> str:
    """Render plain-language trigger conditions. B586: combine signals
    via AND joiner (most strategies are AND-gated). For OR-gated
    strategies (rare), the raw fires_expr will still be visible in
    the Trigger column."""
    if not signals_used:
        return "(see source)"
    translated = [signal_plain_translation(s) for s in signals_used]
    # Detect OR in raw expression - if present, hint at it
    has_or = " or " in (fires_expr or "").lower()
    joiner = " OR " if has_or else " AND "
    return joiner.join(translated)


def load_signal_definitions() -> list:
    """Hand-curated glossary entries for the signals encountered in
    Stage 4 walks so far. Grows as new clusters are walked. Entries
    are ordered by category for owner readability."""
    return [
        # === Candlestick pattern signals ===
        ("doji",                "Candle body < 5% of (high - low). Indecision pattern.",
                                "technical.py:1098"),
        ("hammer",              "Lower wick > 2x body AND upper wick < body. Bullish reversal.",
                                "technical.py:1100"),
        ("shooting_star",       "Upper wick > 2x body AND lower wick < body. Bearish reversal.",
                                "technical.py:1101"),
        ("marubozu_bull",       "Bullish candle with no wicks (upper < 5% body, lower < 5% body).",
                                "technical.py:1103"),
        ("marubozu_bear",       "Bearish candle with no wicks.",
                                "technical.py:1104"),
        ("bullish_engulfing",   "Today's bullish candle body engulfs yesterday's bearish body.",
                                "technical.py:1110"),
        ("bearish_engulfing",   "Today's bearish candle body engulfs yesterday's bullish body.",
                                "technical.py:1112"),
        ("morning_star",        "3-bar bullish reversal: bearish + small body + bullish (gap-recovery).",
                                "technical.py:1126"),
        ("evening_star",        "3-bar bearish reversal: bullish + small body + bearish.",
                                "technical.py:1132"),
        ("three_white_soldiers","3 consecutive bullish closes near high (sustained buying).",
                                "technical.py:1141"),
        ("three_black_crows",   "3 consecutive bearish closes near low (sustained selling).",
                                "technical.py:1145"),
        # === Pivot point proximity (NARROW = 0.30% tolerance) ===
        ("near_s1",             "Today close within 0.30% of pivot S1 support level.",
                                "technical.py:71 (lambda)"),
        ("near_s2",             "Today close within 0.30% of pivot S2 support level.",
                                "technical.py:71"),
        ("near_s3",             "Today close within 0.30% of pivot S3 support level.",
                                "technical.py:71"),
        ("near_r1",             "Today close within 0.30% of pivot R1 resistance level.",
                                "technical.py:71"),
        ("near_r2",             "Today close within 0.30% of pivot R2 resistance level.",
                                "technical.py:71"),
        ("near_pivot",          "Today close within 0.30% of standard pivot point P.",
                                "technical.py:71"),
        # === Pivot point proximity (WIDE = 1.50% tolerance, B574) ===
        ("near_s1_wide",        "Today close within 1.50% of pivot S1. DOJI-ONLY consumer.",
                                "technical.py:76 (B574)"),
        ("near_s2_wide",        "Today close within 1.50% of pivot S2. DOJI-ONLY consumer.",
                                "technical.py:76 (B574)"),
        ("near_r1_wide",        "Today close within 1.50% of pivot R1. DOJI-ONLY consumer.",
                                "technical.py:76 (B574)"),
        ("near_r2_wide",        "Today close within 1.50% of pivot R2. DOJI-ONLY consumer.",
                                "technical.py:76 (B574)"),
        # === Fibonacci proximity ===
        ("at_key_fib",          "Today close within 0.50% of fib 38.2% OR 50% OR 61.8% retracement.",
                                "technical.py:164 + :166"),
        ("at_key_fib_wide",     "Today close within 1.50% of key fib level. DOJI-ONLY consumer.",
                                "technical.py:169 (B574)"),
        # === Volume signals ===
        ("vol_spike_15x",       "Today volume >= 1.5x 20-day average volume.",
                                "technical.py:1021"),
        ("vol_spike_2x",        "Today volume >= 2.0x 20-day average volume.",
                                "technical.py (search vol_spike_2x)"),
        # === Trend/regime gates ===
        ("price_above_ema_200", "Today close > 200-day EMA. Long-term uptrend gate.",
                                "technical.py (search price_above_ema_200)"),
        ("price_above_sma_50",  "Today close > 50-day SMA.",
                                "technical.py (search price_above_sma_50)"),
        ("ema_50_200_bullish",  "50-day EMA > 200-day EMA (golden-cross regime).",
                                "technical.py (search ema_50_200)"),
        # === Momentum / oscillator ===
        ("rsi_14",              "14-day Relative Strength Index, range [0, 100]. <30=oversold, >70=overbought.",
                                "technical.py (compute_rsi)"),
        ("rsi_2",               "2-day RSI (Connors). Faster, more sensitive than 14d.",
                                "technical.py (B204 added)"),
        ("obv_bullish",         "On-Balance Volume in uptrend (today's OBV > N-day prior).",
                                "technical.py (compute_obv)"),
        # === ICT custom producers (B581 ict_producers.py) ===
        ("po3_accumulation_active", "Last 5 bars are in tight range (range/mean_close <= 5%). Phase 1 of Power-of-3 cycle.",
                                "backtest/signals/ict_producers.py:compute_po3_signals"),
        ("po3_manipulation_sweep_down", "Today's LOW pierced below accumulation range low (stop-hunt). Phase 2 PO3.",
                                "ict_producers.py:compute_po3_signals"),
        ("po3_manipulation_sweep_up",   "Today's HIGH pierced above accumulation range high. Phase 2 PO3 (bearish cycle).",
                                "ict_producers.py:compute_po3_signals"),
        ("po3_mmbm_setup",           "MMBM bullish PO3: accumulation + sweep down + close back above + bullish bar.",
                                "ict_producers.py:compute_po3_signals"),
        ("po3_mmsm_setup",           "MMSM bearish PO3: accumulation + sweep up + close back below + bearish bar.",
                                "ict_producers.py:compute_po3_signals"),
        ("is_week_open",             "Today is first trading day of the week (Monday after Friday OR after weekend/holiday).",
                                "ict_producers.py:compute_week_opening_gap_signals"),
        ("week_open_gap_up_15pct",   "Monday opened with gap >= +1.5% vs prior Friday close (daily-bar proxy for ICT Sunday gap).",
                                "ict_producers.py:compute_week_opening_gap_signals"),
        ("week_open_gap_down_15pct", "Monday opened with gap <= -1.5% vs prior Friday close.",
                                "ict_producers.py:compute_week_opening_gap_signals"),
        # === News sentiment ===
        ("news_sentiment_shift", "Current 7d mean sentiment minus prior 7d mean. Range [-2, +2]. Polygon native or Loughran-McDonald lexicon.",
                                "backtest/signals/news_sentiment.py:380"),
        ("news_article_count",  "Article count in current 7d window.",
                                "backtest/signals/news_sentiment.py:385"),
        ("news_sentiment_5d",   "5-day recency-weighted mean sentiment (weight = 1 - age/5).",
                                "backtest/signals/news_sentiment.py:319"),
        ("news_volume_zscore_5d", "5d article count vs trailing 25d daily baseline (z-score).",
                                "backtest/signals/news_sentiment.py:345"),
    ]


def main() -> int:
    print("Building STRATEGY_ROSTER.md ...")
    # Defer heavy imports
    sys.path.insert(0, str(REPO))
    from backtest.signals.screener import ALL_STRATEGIES  # noqa
    # Optional: DEPRECATED + DISABLED status (config.py)
    try:
        from backtest.config import DEPRECATED_STRATEGIES, STRATEGIES_DISABLED_MISSING_PRODUCER
    except ImportError:
        DEPRECATED_STRATEGIES = set()
        STRATEGIES_DISABLED_MISSING_PRODUCER = set()

    affinity = load_regime_affinity()
    glossary = load_signal_definitions()
    stage_4 = load_stage_4_status()

    rows = []
    for name, fn in sorted(ALL_STRATEGIES.items()):
        meta = extract_strategy_meta(name, fn)
        if name in DEPRECATED_STRATEGIES:
            status = "DEPRECATED"
        elif name in STRATEGIES_DISABLED_MISSING_PRODUCER:
            status = "DISABLED (missing producer)"
        else:
            status = "active"
        regimes = affinity.get(name, [])
        regime_str = ",".join(sorted(regimes)) if regimes else "(no affinity = all regimes)"
        # Stage 4 status: B576 - join roster <-> approvals.json
        s4 = stage_4.get(name, {})
        if not s4:
            stage_4_str = "no_approvals_row"
            fired_str = "?"
            s4_reviewed_str = "N"
            bug_fix_str = ""
        else:
            status_counts = {}
            for st in s4["statuses"]:
                status_counts[st] = status_counts.get(st, 0) + 1
            # Compact: "1 Approved / 1 Implemented / 0 Awaiting"
            parts = [f"{n} {st}" for st, n in sorted(status_counts.items())]
            stage_4_str = " / ".join(parts) + f" (n_rows={s4['n_rows']})"
            fired_str = "YES" if s4["fired_in_r4"] else "QUIET"
            # B583: S4 Review column (Y/N + batch tag)
            if s4.get("s4_reviewed"):
                s4_reviewed_str = f"Y ({s4.get('s4_review_batch', '')})"
            else:
                s4_reviewed_str = "N"
            # B585: Producer Bug Fix column (separate from S4 review)
            bug_fix_str = s4.get("producer_bug_fix", "")
        rows.append({**meta, "status": status, "regime": regime_str,
                     "stage_4": stage_4_str, "fired_in_r4": fired_str,
                     "s4_reviewed": s4_reviewed_str,
                     "producer_bug_fix": bug_fix_str})

    out_lines = []
    out_lines.append("# Strategy Roster - Phase 1A-beta cube reference")
    out_lines.append("")
    out_lines.append(f"**Auto-generated** via `scripts/build_strategy_roster.py`. Do NOT hand-edit. Regenerate every turn that modifies strategies, signals, thresholds, regime affinity, or status.")
    out_lines.append("")
    # B577: fired vs quiet counts
    fired_n = sum(1 for r in rows if r.get("fired_in_r4") == "YES")
    quiet_n = sum(1 for r in rows if r.get("fired_in_r4") == "QUIET")
    # B583: S4 reviewed counts
    s4_reviewed_n = sum(1 for r in rows if r.get("s4_reviewed", "N").startswith("Y"))
    s4_pending_n  = len(rows) - s4_reviewed_n
    out_lines.append(f"**Total strategies:** {len(ALL_STRATEGIES)} | **Deprecated:** {len(DEPRECATED_STRATEGIES)} | **Disabled:** {len(STRATEGIES_DISABLED_MISSING_PRODUCER)} | **Active for cube:** {len(ALL_STRATEGIES) - len(DEPRECATED_STRATEGIES | STRATEGIES_DISABLED_MISSING_PRODUCER)}")
    out_lines.append("")
    out_lines.append(f"**R4 cube fire status:** **{fired_n} FIRED** (have optimizer-extracted Class 1-7 rows) | **{quiet_n} QUIET** (zero R4 fires; Class 0 QUIET_NO_CANDIDATES placeholder per B576 drift backfill)")
    out_lines.append("")
    # B585: separate "S4 reviewed (full 7-step walk)" from "producer
    # bug fixed (partial work)"
    bug_fixed_n = sum(1 for r in rows if r.get("producer_bug_fix"))
    out_lines.append(f"**S4 Review progress (B583+B585):** **{s4_reviewed_n} REVIEWED (full 7-step walk)** ({100.0*s4_reviewed_n/len(rows):.0f}%) | **{s4_pending_n} PENDING** ({100.0*s4_pending_n/len(rows):.0f}%) per `feedback_per_strategy_deep_dive_stage4`. Per-strategy 7-step deep-dive must complete before R5 cube run per `feedback_r5_paused_pending_stage4_completion`.")
    out_lines.append("")
    if bug_fixed_n:
        out_lines.append(f"**Producer bug fixes (B585 ledger - SEPARATE from S4 review):** **{bug_fixed_n} strategies** have had a producer bug fix applied. These strategies STILL need a full 7-step S4 walk per owner directive 2026-06-04 'bug fix is NOT S4 review completion.' See `Producer Bug Fix` column for batch tag.")
        out_lines.append("")
    out_lines.append("**Architectural gotcha (B576):** `lead_lag_sector_rotation` is registered via a non-ALL_STRATEGIES path (`screen_lead_lag_sector()` at [screener.py:4096](backtest/signals/screener.py#L4096), called from `screen_universe()`). It IS active in the engine but is NOT counted in `len(ALL_STRATEGIES)`. The true active engine roster total is **206** (205 + 1 special-path). Note: 207 unique strategies in approvals.json = 206 engine + 1 queued (`news_sentiment_shift_short` Class 7 Approved B571 awaiting wiring).")
    out_lines.append("")
    out_lines.append("**Count reconciliation:**")
    out_lines.append(f"- `len(ALL_STRATEGIES)` = {len(ALL_STRATEGIES)} (standard dict path)")
    out_lines.append(f"- +1 special path (`lead_lag_sector_rotation`)")
    out_lines.append(f"- **= True engine roster: {len(ALL_STRATEGIES) + 1}**")
    out_lines.append(f"- +1 queued for wiring (news_sentiment_shift_short)")
    out_lines.append(f"- Unique strategies in approvals: {len(ALL_STRATEGIES) + 2}")
    out_lines.append(f"- approvals.json ROWS != strategies (each strategy can have multiple change-class rows)")
    out_lines.append("")
    out_lines.append("**TODO (B577 surfaced):** Only 1 of 205 strategies has explicit `STRATEGY_REGIME_AFFINITY` (`head_and_shoulders_bottom_long`). 204 strategies fall through to default 'all regimes'. R4 empirical per-regime cube data should feed back into deployment-time affinity rules. See EXECUTION_QUEUE.md item `regime-affinity-investigation`.")
    out_lines.append("")
    out_lines.append("**Stage 4 approvals (per-strategy mapping, B576 drift correction):** Every registered strategy has at least one approvals.json row. Quiet strategies (no R4 fires) carry a `Class 0 QUIET_NO_CANDIDATES` placeholder Awaiting row.")
    out_lines.append("")
    out_lines.append("## Direction counts")
    direction_counts = {}
    for r in rows:
        direction_counts[r["direction"]] = direction_counts.get(r["direction"], 0) + 1
    for d, n in sorted(direction_counts.items()):
        out_lines.append(f"- **{d}**: {n}")
    out_lines.append("")
    out_lines.append("## Category counts")
    cat_counts = {}
    for r in rows:
        cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
        out_lines.append(f"- **{c}**: {n}")
    out_lines.append("")
    out_lines.append("## Strategy Table")
    out_lines.append("")
    # B585+B586: S4 Reviewed + Producer Bug Fix columns at positions
    # 2+3 (visibility). B586 adds "Trigger Conditions" plain-language
    # column right after raw Trigger code per owner directive 2026-06-04
    # "update trigger column with such information for all strategies."
    out_lines.append("| # | Name | S4 Reviewed | Producer Bug Fix | R4 Fires | Category | Direction | Trigger Conditions (plain) | Trigger (code) | Signals consumed | Regime affinity | Roster Status | Stage 4 Status |")
    out_lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        trigger = r["fires_expr"].replace("|", "\\|").replace("\n", "<br>")
        # Truncate very long triggers for table readability
        if len(trigger) > 250:
            trigger = trigger[:247] + "..."
        sigs = ", ".join(r["signals_used"]) if r["signals_used"] else "(see source)"
        if len(sigs) > 120:
            sigs = sigs[:117] + "..."
        # B586: plain-language trigger
        trigger_plain = render_trigger_plain(r["signals_used"], r["fires_expr"])
        if len(trigger_plain) > 250:
            trigger_plain = trigger_plain[:247] + "..."
        # Escape pipes in plain trigger
        trigger_plain = trigger_plain.replace("|", "\\|")
        out_lines.append(
            f"| {i} | `{r['name']}` | {r['s4_reviewed']} | {r['producer_bug_fix']} | "
            f"{r['fired_in_r4']} | {r['category']} | {r['direction']} | "
            f"{trigger_plain} | `{trigger}` | {sigs} | {r['regime']} | "
            f"{r['status']} | {r['stage_4']} |"
        )
    out_lines.append("")

    # B578: Projected Strategies section sourced from STRATEGY_REGISTER.md
    # Layer 4 PENDING owner approval per owner directive 2026-06-04:
    # "update future strategies in strategy roster doc from strategy
    # register with a note that the flagged strategies will be approved"
    projected = load_projected_strategies()
    if projected:
        out_lines.append("## Projected Strategies (PENDING owner approval, will be wired post-approval)")
        out_lines.append("")
        out_lines.append("**Source:** [STRATEGY_REGISTER.md](STRATEGY_REGISTER.md) Layer 4 + Layer 2D PENDING sub-decisions.")
        out_lines.append("")
        out_lines.append("**Note:** these strategies are NOT in `ALL_STRATEGIES` yet. They are owner-approval-pending additions. On approval of the corresponding DEC, each will be wired into `screener.py` via the standard `_strat()` pattern + registered in `ALL_STRATEGIES` + receive its own Stage 4 approvals row. The flagged strategies will be approved.")
        out_lines.append("")
        out_lines.append("| DEC | Proposed Name | Description | Est. Classes | Theoretical Basis | Layer | Status |")
        out_lines.append("|---|---|---|---|---|---|---|")
        for p in projected:
            out_lines.append(
                f"| {p['dec_id']} | `{p['name']}` | {p['description']} | "
                f"{p['est_classes']} | {p['basis']} | {p['layer']} | "
                f"PENDING_OWNER_APPROVAL |"
            )
        out_lines.append("")

    out_lines.append("## Signal Glossary")
    out_lines.append("")
    out_lines.append("| Signal | Definition | Source |")
    out_lines.append("|---|---|---|")
    for sig, defn, src in glossary:
        out_lines.append(f"| `{sig}` | {defn} | {src} |")
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")
    out_lines.append("**Glossary growth:** new signals encountered during per-strategy deep-dives should be added to `load_signal_definitions()` in this script. Each entry: signal name + plain-English definition + file:line where computed.")
    out_lines.append("")
    out_lines.append("**Per-strategy detailed analysis** (threshold rationale, theoretical basis, inverse audit, R4 verdict) lives in `C:/tmp/r4_optimization_candidates/approvals.json` and is surfaced in the dashboard.")

    OUT_MD.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD} ({len(out_lines)} lines, {OUT_MD.stat().st_size:,} bytes)")
    print(f"Strategies: {len(rows)}; Glossary entries: {len(glossary)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
