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
    # B589 owner directive: comprehensive unambiguous descriptions; do
    # not assume reader knows period defaults / formula details. Every
    # entry specifies: WHAT is measured + the COMPARISON OPERATOR +
    # the THRESHOLD + the LOOKBACK PERIOD / CALCULATION BASIS.
    plain = {
        # Volume (all use rolling 20-bar mean of daily volume as denominator)
        "vol_above_avg":     "today's volume >= 20-day average volume (ratio >= 1.0); 20-day window includes today",
        "vol_spike_12x":     "today's volume >= 1.2x the 20-day average volume (B589 owner-tightened for smart-money sleeves)",
        "vol_spike_15x":     "today's volume >= 1.5x the 20-day average volume",
        "vol_spike_17x":     "today's volume STRICTLY GREATER THAN 1.7x the 20-day average volume (B586 owner-picked from 1.5x-2x range for 52w breakouts)",
        "vol_spike_2x":      "today's volume >= 2.0x the 20-day average volume",
        "vol_spike_3x":      "today's volume >= 3.0x the 20-day average volume",
        # 52w high/low (lookback 252 trading days, EXCLUDES today's bar per B582 fix)
        "break_52w_high":    "today's close STRICTLY GREATER THAN the highest HIGH over prior 252 trading days (52 weeks; excludes today; B582 producer fix)",
        "break_52w_low":     "today's close STRICTLY LESS THAN the lowest LOW over prior 252 trading days (52 weeks; excludes today; B582 producer fix)",
        "near_52w_high":     "today's close >= 98% of the highest HIGH over prior 252 trading days (i.e. within 2% below the 52-week high)",
        "near_52w_low":      "today's close <= 102% of the lowest LOW over prior 252 trading days (i.e. within 2% above the 52-week low)",
        "near_52w_high_95pct": "today's close >= 95% of the highest HIGH over prior 252 trading days (broader 5% tolerance; B589 owner-directed for smart-money sleeve)",
        "near_52w_low_105pct": "today's close <= 105% of the lowest LOW over prior 252 trading days (broader 5% tolerance; B589 mirror)",
        "near_52w_high_retest_long":
            "All 7 must hold (B590-redesigned pullback retest detector + false-breakout filters). Reference level = PRE-BREAKOUT 52-week high = max HIGH over the 252 trading days ending 30 bars ago (year_high_pre30; STABLE - excludes the breakout window itself so it does not drift upward as the breakout prints new highs each day, fixing B586 logic flaw). (a) breakout_occurred: max CLOSE in the last 30 trading days (excluding today) > year_high_pre30 (stock punched through pre-breakout resistance somewhere in the last 30 days); (b) within_3pct_high: today's close within +/-3% of year_high_pre30 (returned to the broken level); (c) today_below_peak: today's close < 30-day max close * 0.99 (at least 1% below the breakout peak = pulled back); (d) vol_below_avg: today's volume / 20-bar average < 1.0 (low-volume retest); (e) close_above_open: today's close > today's open (bullish reversal bar); (f) breakout_3_candles_old: at least 3 trading days have elapsed between the FIRST bar in the 30-day window whose close exceeded year_high_pre30 and today (time filter - gives the retest time to form; B590 false-breakout filter); (g) within_atr_band_long: today's close >= year_high_pre30 - ATR(14) (volatility-adjusted band - a close more than 1 ATR below the broken resistance is a failed retest, not a pullback; B590 false-breakout filter). B590 redesign replaced B586's two-disjoint-window design (10-day cutoff + 252d) with a single 30-bar window; widened retest tolerance from 1% to 3%; added time + ATR filters per owner directive.",
        "near_52w_low_retest_short":
            "Mirror of near_52w_high_retest_long (B590). Reference = PRE-BREAKDOWN 52-week low = min LOW over the 252 trading days ending 30 bars ago (year_low_pre30; STABLE pre-breakdown reference). All 7 must hold: (a) breakdown_occurred: min CLOSE in last 30 trading days (excluding today) < year_low_pre30; (b) within_3pct_low: today's close within +/-3% of year_low_pre30; (c) today_above_trough: today's close > 30-day min close * 1.01 (bounced from breakdown trough); (d) vol_below_avg: today's volume / 20-bar avg < 1.0 (weak retest); (e) close_below_open: today's close < today's open (bearish bar); (f) breakdown_3_candles_old: at least 3 trading days elapsed between first breakdown bar and today (time filter); (g) within_atr_band_short: today's close <= year_low_pre30 + ATR(14) (volatility band - a close more than 1 ATR above the broken support is a failed retest).",
        # Range-position
        "close_in_top_40pct_of_range":
            "(today's high - today's close) / (today's high - today's low) <= 0.40 -- close is in the TOP 40% of today's bar range (strong-close bull signal; B589 added)",
        "close_in_bottom_40pct_of_range":
            "(today's close - today's low) / (today's high - today's low) <= 0.40 -- close is in the BOTTOM 40% of today's bar range (strong-close bear signal; B589 added)",
        # Sector strength (20-day trailing return of stock's GICS sector SPDR ETF vs SPY)
        "sector_outperforming_spy":
            "the GICS sector SPDR ETF mapped to this stock's sector has a 20-trading-day trailing return STRICTLY GREATER than SPY's 20-trading-day trailing return (B586). Sector map: Information Technology->XLK, Financials->XLF, Energy->XLE, Health Care->XLV, Industrials->XLI, Consumer Discretionary->XLY, Consumer Staples->XLP, Utilities->XLU, Materials->XLB, Real Estate->XLRE, Communication Services->XLC.",
        "sector_underperforming_spy":
            "mirror of sector_outperforming_spy: sector SPDR ETF 20-day trailing return STRICTLY LESS than SPY's 20-day trailing return (B587).",
        # Pivot points (standard pivot formula on PRIOR day's H/L/C; near = within +/-0.30% by default)
        "near_s1":           "today's close is within +/-0.30% of pivot point S1 (Standard pivot: S1 = 2P - H, where P = (prior_H + prior_L + prior_C)/3)",
        "near_s2":           "today's close is within +/-0.30% of pivot point S2 (Standard: S2 = P - (prior_H - prior_L))",
        "near_s3":           "today's close is within +/-0.30% of pivot point S3 (Standard: S3 = prior_L - 2*(prior_H - P))",
        "near_r1":           "today's close is within +/-0.30% of pivot point R1 (Standard: R1 = 2P - prior_L)",
        "near_r2":           "today's close is within +/-0.30% of pivot point R2 (Standard: R2 = P + (prior_H - prior_L))",
        "near_pivot":        "today's close is within +/-0.30% of the standard pivot point P (P = (prior_H + prior_L + prior_C)/3)",
        "near_s1_wide":      "today's close within +/-1.50% of pivot S1 (B574 doji-only wider tolerance variant)",
        "near_s2_wide":      "today's close within +/-1.50% of pivot S2 (B574 doji-only)",
        "near_r1_wide":      "today's close within +/-1.50% of pivot R1 (B574 doji-only)",
        "near_r2_wide":      "today's close within +/-1.50% of pivot R2 (B574 doji-only)",
        # Fibonacci (retracement levels on 50-bar swing high/low; near = within +/-0.50%)
        "at_key_fib":        "today's close is within +/-0.50% of one of: fib 38.2% / fib 50.0% / fib 61.8% (retracement from prior 50-bar swing-high to swing-low)",
        "at_key_fib_wide":   "today's close within +/-1.50% of key fib (B574 doji-only wider tolerance)",
        # Candle patterns (all use today's bar OHLC + 1-3 prior bars depending on pattern)
        "doji":              "today's |close - open| < 5% of today's (high - low) range -- indecision candle (buyers and sellers equally matched)",
        "hammer":             "today's lower-wick (open/close-low) > 2x today's body AND upper-wick (high-open/close) < today's body -- bullish reversal candle",
        "shooting_star":     "today's upper-wick > 2x today's body AND lower-wick < today's body -- bearish reversal candle",
        "bullish_engulfing": "today's open <= yesterday's close AND today's close >= yesterday's open AND today is bullish AND yesterday was bearish -- bullish reversal 2-bar pattern",
        "bearish_engulfing": "today's open >= yesterday's close AND today's close <= yesterday's open AND today is bearish AND yesterday was bullish -- bearish reversal 2-bar pattern",
        "morning_star":      "3-bar bullish reversal: bar -2 strongly bearish, bar -1 small-body (any direction), today strongly bullish closing in upper half of bar -2's body",
        "evening_star":      "3-bar bearish reversal: bar -2 strongly bullish, bar -1 small-body, today strongly bearish closing in lower half of bar -2's body",
        "three_white_soldiers": "3 consecutive bullish bars (close > open each), each closing in upper 25% of its range AND each above the prior bar's close",
        "three_black_crows": "3 consecutive bearish bars (close < open each), each closing in lower 25% of its range AND each below the prior bar's close",
        # Trend / regime (EMAs computed on close series; SMAs same)
        "price_above_ema_200":   "today's close STRICTLY GREATER THAN the 200-day exponential moving average of close (long-term uptrend gate)",
        "price_above_sma_50":    "today's close STRICTLY GREATER THAN the 50-day simple moving average of close",
        "ema_50_200_bullish":    "today's 50-day EMA STRICTLY GREATER THAN today's 200-day EMA (golden-cross regime - bullish trend backdrop)",
        "ema_50_200_golden_cross": "ONE-BAR EVENT: today's 50d EMA > today's 200d EMA AND yesterday's 50d EMA <= yesterday's 200d EMA",
        "ema_50_200_death_cross": "ONE-BAR EVENT: today's 50d EMA < today's 200d EMA AND yesterday's 50d EMA >= yesterday's 200d EMA",
        # Oscillator / momentum
        "rsi_14":              "14-day Relative Strength Index of close (Wilder smoothing). Numeric value [0, 100]; check inline strategy code for the specific comparison threshold (e.g. < 30 = oversold, > 70 = overbought)",
        "rsi_2":               "2-day RSI of close (Connors RSI methodology; faster and more sensitive than 14-day)",
        "obv_bullish":         "On-Balance Volume in uptrend: today's OBV > OBV from 5 bars ago (cumulative volume on up-days minus volume on down-days)",
        "obv_rising":          "today's OBV STRICTLY GREATER than OBV from 5 bars ago. Institutional accumulation proxy (Granville 1963).",
        "obv_falling":         "today's OBV STRICTLY LESS than OBV from 5 bars ago (B608 F2 - symmetric to obv_rising; fixes silent-gap where strat_break_retest_volume SHORT side previously used `not obv_rising` which auto-passed when key was missing). Institutional distribution proxy.",
        "macd_12_26_9_bearish":"MACD 12/26/9 histogram STRICTLY LESS than 0 (B609 F2 - symmetric to macd_12_26_9_bullish; fixes silent-gap where strat_break_retest_confluence SHORT used `not macd_bullish` which auto-passed when key was missing).",
        "below_ema_20":        "today's close STRICTLY LESS than 20-day EMA (B609 F2 - symmetric to price_above_ema_20; fixes silent-gap on strat_break_retest_confluence SHORT side).",
        "below_ema_50":        "today's close STRICTLY LESS than 50-day EMA (B609 F2 - symmetric to price_above_ema_50).",
        # SMC (signals from smartmoneyconcepts library; computed on swing_length=20 by default)
        "smc_fvg_bullish_active":  "Bullish Fair Value Gap (3-bar imbalance where bar -2's high < bar 0's low) is active and unfilled within recent window",
        "smc_fvg_bearish_active":  "Bearish Fair Value Gap (3-bar imbalance where bar -2's low > bar 0's high) is active and unfilled within recent window",
        "smc_choch_bullish":   "Change of Character bullish: market structure shifted from down-trend to up-trend (last lower-high failed, broke a recent swing-high)",
        "smc_choch_bearish":   "Change of Character bearish: market structure shifted from up-trend to down-trend",
        "smc_bos_bullish":     "Break of Structure bullish: price broke above the most recent confirmed swing-high (trend continuation)",
        "smc_bos_bearish":     "Break of Structure bearish: price broke below the most recent confirmed swing-low",
        "smc_liquidity_swept_up":   "Price spiked above a documented liquidity zone (equal-highs cluster) then closed back below -- retail stops above were taken out",
        "smc_liquidity_swept_dn":   "Price spiked below a documented liquidity zone (equal-lows cluster) then closed back above -- retail stops below were taken out",
        "smc_equal_highs_swept":    "Equal-highs (cluster of 2+ swing-highs at same level) were taken out by today's high (specific liquidity-grab variant)",
        "smc_equal_lows_swept":     "Equal-lows (cluster of 2+ swing-lows at same level) were taken out by today's low",
        "smc_ote_long_zone":   "Price is in the Optimal Trade Entry long zone: 62%-79% Fib retracement of the most recent bullish leg",
        "smc_ote_short_zone":  "Price is in the OTE short zone: 62%-79% Fib retracement of the most recent bearish leg",
        "smc_breaker_block_bullish":  "Active bullish breaker block (failed bearish order block that price reversed back through; now acts as support)",
        "smc_breaker_block_bearish":  "Active bearish breaker block (failed bullish order block; now acts as resistance)",
        # B581 ICT producers (custom PO3 + week-open-gap)
        "po3_mmbm_setup":      "PO3 Market Maker Buy Model: (a) last 5 bars in tight range (range/mean_price <= 5%) = accumulation; (b) today's LOW < accumulation range low (sweep down = manipulation); (c) today's close > accumulation range low (closed back inside); (d) today's close > today's open (bullish bar). All 4 required.",
        "po3_mmsm_setup":      "PO3 Market Maker Sell Model: mirror of mmbm_setup -- accumulation + sweep UP + reversal back below range + bearish bar.",
        "week_open_gap_up_15pct":   "Today is first trading day of the week (Monday or post-weekend trading day) AND today's open >= 1.5% above prior Friday's close (daily-bar proxy for ICT 'Sunday gap up')",
        "week_open_gap_down_15pct": "Today is first trading day of the week AND today's open <= -1.5% below prior Friday's close",
        # News sentiment (Polygon news feed + Loughran-McDonald lexicon fallback)
        "news_sentiment_shift":     "(current 7d mean sentiment score) MINUS (prior 7d mean sentiment score). Range [-2, +2]. Positive value = sentiment IMPROVING. Strategies check thresholds like > 0.4 (strong positive shift) or < -0.4 (strong negative shift) inline.",
        "news_article_count":       "number of articles published about this ticker in the current 7-day window (coverage gate)",
        "news_sentiment_5d":        "5-day recency-weighted mean sentiment score (weight = 1 - age/5; more-recent articles weighted heavier)",
        "news_volume_zscore_5d":    "5-day article-count vs trailing 25-day baseline article-count, expressed as a z-score (Cohen-Frazzini-Malloy news-attention normalisation)",
        # Donchian (canonical N-bar channel; B584 fix excludes today from rolling window)
        "dc10_breakout_up":    "today's close >= 99.8% of the highest HIGH over the PRIOR 10 trading days (B584 fix excludes today). 0.2% slack permits 'almost a breakout'.",
        "dc10_breakout_dn":    "today's close <= 100.2% of the lowest LOW over the PRIOR 10 trading days (B584 fix). 0.2% slack permits 'almost a breakdown'.",
        "dc20_breakout_up":    "today's close >= 99.8% of the highest HIGH over the PRIOR 20 trading days (B584 fix)",
        "dc20_breakout_dn":    "today's close <= 100.2% of the lowest LOW over the PRIOR 20 trading days (B584 fix)",
        # B591 LOCAL 1pct-tolerance variants (consumed by donchian_10_breakout alone)
        "dc10_breakout_up_1pct": "today's close >= 99% of the highest HIGH over the PRIOR 10 trading days (1pct slack vs the 0.2pct default of dc10_breakout_up). LOCAL signal consumed by strat_donchian_10_breakout alone (B591).",
        "dc10_breakout_dn_1pct": "today's close <= 101% of the lowest LOW over the PRIOR 10 trading days (1pct slack vs 0.2pct default). LOCAL signal (B591).",
        # B592 LOCAL strong-breakout filter (consumed by donchian_10_breakout alone)
        "dc10_strong_breakout_up": "today's close >= (highest HIGH over prior 10 days) + 0.5*ATR(14). Volatility-adjusted strong-breakout filter -- close must meaningfully exceed the prior 10-day high, not just touch it. LOCAL signal (B592 close-out of B591 (e); EWM Wilder ATR period 14).",
        "dc10_strong_breakout_dn": "today's close <= (lowest LOW over prior 10 days) - 0.5*ATR(14). Mirror of dc10_strong_breakout_up (B592).",
        # Break-and-retest (BUG-111 / Batch 329) -- DC20-anchored multi-bar pattern
        "resistance_break_retest": "(BUG-111 multi-bar pattern, anchored on DC20 = prior-20-day max-CLOSE level). ALL conditions: (a) breakout: some bar 2-8 bars ago (lag in 2..8) closed STRICTLY ABOVE the max CLOSE of the 20 bars preceding that bar; (b) retest: between the breakout bar and today, at least one bar's LOW was <= (breakout_level + 1.5*ATR(14)) -- i.e. price came back to within 1.5 ATR of the broken level from above; (c) hold: today's close >= broken_level (still trading above the flipped resistance->support). All 3 required; first lag that satisfies all 3 fires the signal (TYPICAL: 3-5 bars post-breakout).",
        "support_break_retest":    "Mirror of resistance_break_retest (BUG-111). DC20-anchored on prior-20-day min-CLOSE. ALL: (a) breakdown 2-8 bars ago closed STRICTLY BELOW the prior 20d min CLOSE; (b) at least one subsequent bar's HIGH >= (breakdown_level - 1.5*ATR(14)) (retest came back within 1.5 ATR from below); (c) today's close <= broken_level (still below the flipped support->resistance). 1.5*ATR uses 14-bar EWM Wilder ATR.",
        # B605 (2026-06-06 F1 bug fix in 52wh_break_retest walk): 52w-anchored retest primitive.
        "year_high_break_retest_long":  "(B605 NEW; 52w-anchored, NOT DC20-anchored). ALL: (a) some bar 2-8 ago closed > year_high (prior-252-day max-HIGH excluding today; same year_high definition as break_52w_high and near_52w_high); (b) at least one subsequent bar's LOW touched within 1.5*ATR(14) of year_high (retest); (c) today's close >= year_high (still above broken level). Replaces the buggy DC20-anchored resistance_break_retest in strat_52wh_break_retest. LOCAL signal consumed by strat_52wh_break_retest only (B605).",
        "year_low_break_retest_short": "Mirror of year_high_break_retest_long (B605). ALL: (a) some bar 2-8 ago closed < year_low (prior-252-day min-LOW excluding today); (b) subsequent bar's HIGH touched within 1.5*ATR of year_low (retest from below); (c) today's close <= year_low (still below broken level). Consumed by Class 7 NEW strat_52wl_break_retest_short (B605).",
        # B606 (2026-06-06 F1 bug fix in r1_break_retest walk): R1/S1-anchored retest primitive.
        "r1_break_retest_long":  "(B606 NEW; R1-anchored, NOT DC20-anchored). ALL: (a) some bar B 2-8 ago closed > R1_at_B, where R1_at_B is computed from bar (B-1)'s H/L/C using standard pivot formula (R1 = 2*P - L; P = (H+L+C)/3); (b) subsequent bar's LOW touched within 1.5*ATR(14) of R1_at_B (retest); (c) today's close >= R1_at_B (still above broken R1). Replaces the buggy DC20-anchored resistance_break_retest in strat_r1_break_retest. LOCAL signal consumed by strat_r1_break_retest only (B606).",
        "s1_break_retest_short": "Mirror of r1_break_retest_long (B606). ALL: (a) some bar B 2-8 ago closed < S1_at_B (S1 = 2*P - H from bar B-1's H/L/C); (b) subsequent bar's HIGH touched within 1.5*ATR of S1_at_B (retest from below); (c) today's close <= S1_at_B (still below broken S1). Consumed by strat_r1_break_retest SHORT side.",
        # B607 (2026-06-07 F1 bug fix in flag_bull_retest_long walk): flag-anchored retest primitive.
        "flag_bull_break_retest_long":  "(B607 NEW; flag-anchored, NOT DC20-anchored). Runs detect_flag on a HISTORICAL slice ending K bars ago (K in 3..12) to find a bull flag (pole +10pct in 20 bars + tight <5pct flag in 10 bars). When found, anchors on the SPECIFIC flag_bull_breakout_level = max(flag_window.high). ALL: (a) some close in last K-1 bars exceeded breakout_level (break); (b) some subsequent bar's LOW touched within 1.5*ATR(14) of breakout_level (retest); (c) today's close >= breakout_level (still above). Replaces the buggy DC20-anchored resistance_break_retest in strat_flag_bull_retest_long.",
        "flag_bear_break_retest_short": "Mirror of flag_bull_break_retest_long (B607). Detects bear flag (pole <=-10pct in 20 bars + tight flag) completed K bars ago, anchors on flag_bear_breakdown_level = min(flag_window.low). ALL: (a) some close in last K-1 bars fell below breakdown_level; (b) some subsequent bar's HIGH touched within 1.5*ATR of breakdown_level (retest from below); (c) today's close <= breakdown_level. Consumed by Class 7 NEW strat_flag_bear_retest_short (B607).",
        # B594 LOCAL strong-breakout retest variants (consumed by
        # strat_donchian_20_breakout_retest alone). Same retest pattern
        # as the standard variant but ALSO requires the original break
        # bar to have cleared the level by >= 0.5*ATR(14), not just to
        # have crossed it.
        "dc20_resistance_break_retest_strong": "(B594 LOCAL strong variant of resistance_break_retest, consumed by strat_donchian_20_breakout_retest only). ALL conditions of resistance_break_retest PLUS: the original breakout bar (lag 2-8) closed by AT LEAST 0.5*ATR(14) ABOVE the prior-20-day max-close level (not merely crossed it). Filters trivial closes-just-above-level pseudo-breakouts on the retest pattern.",
        "dc20_support_break_retest_strong": "Mirror of dc20_resistance_break_retest_strong (B594 LOCAL). ALL conditions of support_break_retest PLUS: original breakdown bar closed by AT LEAST 0.5*ATR(14) BELOW the prior-20-day min-close level.",
        # B594 global vol_below_avg signal
        "vol_below_avg": "today's volume / 20-day average volume STRICTLY LESS THAN 1.0 (window includes today). Bulkowski 2005: retest pattern forms on LOWER volume than the initial break (supply absorption thesis).",
        # Brian Shannon (2022) Anchored VWAP signals (Batch 205, used by B597)
        "above_avwap_50low":  "today's close > AVWAP anchored at the lowest LOW of the prior 50 trading days. AVWAP cumulates (typical_price * volume) since the anchor bar; close above means the upleg from that swing low is still institutionally supported.",
        "above_avwap_20high": "today's close > AVWAP anchored at the highest HIGH of the prior 20 trading days. Close above means the breakout-day-to-now leg is still above the breakout reference price. Used INVERTED by volume_spike_breakout SHORT (B597): when close is BELOW this AVWAP, the recent rally has been given back.",
        "above_avwap_252low": "today's close > AVWAP anchored at the lowest LOW of the prior 252 trading days. 1-year leg reference.",
        "above_avwap_20low":  "today's close > AVWAP anchored at the lowest LOW of the prior 20 trading days (B598 added for symmetric anchor pair with above_avwap_20high). Used by volume_spike_breakout LONG (B598).",
        # B612 (2026-06-07 owner+AI critique post-B608/B609/B610): symmetric
        # below_avwap_* signals added to fix silent-gap on SHORT sides that
        # used `not s.get("above_avwap_20high")` without default=True.
        "below_avwap_20high": "today's close < AVWAP anchored at the highest HIGH of the prior 20 trading days (B612 F2 - symmetric to above_avwap_20high; fixes silent-gap on volume_spike_breakout SHORT, volume_spike_breakout_retest SHORT, r1_break_retest SHORT).",
        "below_avwap_20low":  "today's close < AVWAP anchored at the lowest LOW of the prior 20 trading days (B612 F2 - symmetric to above_avwap_20low).",
        "below_avwap_50low":  "today's close < AVWAP anchored at the lowest LOW of the prior 50 trading days (B612 F2).",
        "below_avwap_252low": "today's close < AVWAP anchored at the lowest LOW of the prior 252 trading days (B612 F2).",
        # Day-of-bar primitives
        "close_above_open":    "today's close STRICTLY GREATER THAN today's open (bullish bar)",
        "close_below_open":    "today's close STRICTLY LESS THAN today's open (bearish bar)",
        "above_prev_high":     "today's close STRICTLY GREATER THAN the prior trading day's high",
        "below_prev_low":      "today's close STRICTLY LESS THAN the prior trading day's low",
        "smart_money_buy":     "ONE-OR-MORE of these signals True: insider_cluster_active (multiple insiders bought recently), institutional_strong_buy, institutional_buy, cfo_buy (CFO insider buy), large_dollar_buy (single insider transaction > $1M). Composite OR. (helper: _has_smart_money_buy)",
        "smart_money_sell":    "ONE-OR-MORE of these signals True: insider_cluster_sell (multiple insiders sold recently), institutional_strong_sell, institutional_sell, concentrated_sell (single insider sold > 50% of holdings), cluster_sell. Composite OR. (helper: _has_smart_money_sell B588)",
    }
    return plain.get(signal, signal)


def render_trigger_plain(signals_used: list, fires_expr: str) -> str:
    """Render plain-language trigger conditions as bullet-point list.

    Batch 593 (2026-06-05 owner directive): "retain the description but
    put in bullet points to make it more readable." Each signal renders
    as a separate <br>-separated bullet inside the table cell so the
    column remains a single row but reads vertically.

    For OR-gated strategies (rare), the joiner is rendered as
    "OR" between bullets; for AND-gated (default), no explicit joiner
    is needed since all bullets must hold.
    """
    if not signals_used:
        return "(see source)"
    translated = [signal_plain_translation(s) for s in signals_used]
    has_or = " or " in (fires_expr or "").lower()
    if has_or:
        # OR-gated: insert "OR" between bullets to make the logic clear
        bullets = []
        for i, t in enumerate(translated):
            prefix = "- " if i == 0 else "- OR "
            bullets.append(f"{prefix}{t}")
    else:
        # AND-gated: all bullets must hold (implicit AND)
        bullets = [f"- {t}" for t in translated]
    return "<br>".join(bullets)


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
    # B894 (2026-06-18) Council 18 owner-approved: SCRUBBED stale data-source-
    # backed columns. Owner red-flagged repeated staleness across B874/B887/
    # B889/B892 caused by columns sourced from R4-era data (output_batch395
    # _final May 31 + approvals.json snapshot) without freshness audit. Per
    # CHECKLIST #111 (NEW B894): regenerated artifacts must list every data
    # source + refuse to claim "refreshed" if any source is stale.
    #
    # REMOVED COLUMNS (sourced from stale data):
    # - "R4 cube fire status: N FIRED | N QUIET" (sourced from R4 May 31 cube)
    # - "S4 Review progress: N REVIEWED / N PENDING" (stale s4_reviewed flags)
    # - "Producer bug fixes: N strategies" (stale ledger)
    # - Per-row "fired_in_r4" column = QUIET/FIRED (R4-era state)
    # - Per-row "X Awaiting (n_rows=X)" Stage 4 column (stale approvals.json)
    # - Per-row "s4_reviewed" Y/N column (stale flag)
    #
    # RETAINED COLUMNS (derivable from current screener.py + regime_selector.py):
    # name | category | direction | trigger | signals | conditions |
    # regime_affinity | active_status
    out_lines.append(f"**Total strategies:** {len(ALL_STRATEGIES)} | **Deprecated:** {len(DEPRECATED_STRATEGIES)} | **Disabled:** {len(STRATEGIES_DISABLED_MISSING_PRODUCER)} | **Active for cube:** {len(ALL_STRATEGIES) - len(DEPRECATED_STRATEGIES | STRATEGIES_DISABLED_MISSING_PRODUCER)}")
    out_lines.append("")
    out_lines.append("> **B894 NOTE (2026-06-18 Council 18 verdict per CHECKLIST #111):** R4 cube fire status, S4 Review progress, Producer Bug Fix ledger, and per-row Stage 4 Awaiting columns SCRUBBED from this doc - those data sources are stale (R4 era May 31; pre-B722/B874 deletions). Per `feedback_no_a_priori_strategy_pruning` + Council 18 Contrarian: \"anything that lies is worse than absent.\" Live cube fire status + S4 status will be restored after R5 cube execution with fresh data sources. Until then this doc shows only what's derivable from current `screener.py` + `regime_selector.py`.")
    out_lines.append("")
    # B892 (2026-06-18) Council 17 First Principles + Executor fix: remove
    # hardcoded literals from prose. Stale numerics (205/206/207) baked into
    # the template at B576-era were the root cause of owner's "STRATEGY_ROSTER
    # extremely stale" complaint. Replaced with live-computed values via
    # f-strings + the STRATEGY_REGIME_AFFINITY dict scan below.
    out_lines.append(f"**Architectural gotcha (B576):** `lead_lag_sector_rotation` is registered via a non-ALL_STRATEGIES path (`screen_lead_lag_sector()` at [screener.py:4096](backtest/signals/screener.py#L4096), called from `screen_universe()`). It IS active in the engine but is NOT counted in `len(ALL_STRATEGIES)`. The true active engine roster total is **{len(ALL_STRATEGIES) + 1}** ({len(ALL_STRATEGIES)} + 1 special-path).")
    out_lines.append("")
    out_lines.append("**Count reconciliation:**")
    out_lines.append(f"- `len(ALL_STRATEGIES)` = {len(ALL_STRATEGIES)} (standard dict path)")
    out_lines.append(f"- +1 special path (`lead_lag_sector_rotation`)")
    out_lines.append(f"- **= True engine roster: {len(ALL_STRATEGIES) + 1}**")
    out_lines.append(f"- approvals.json ROWS != strategies (each strategy can have multiple change-class rows)")
    out_lines.append("")
    # B892 live-computed STRATEGY_REGIME_AFFINITY count (was hardcoded "1 of 205")
    try:
        from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
        n_with_affinity = len(STRATEGY_REGIME_AFFINITY)
    except Exception:
        n_with_affinity = 0
    n_without_affinity = len(ALL_STRATEGIES) - n_with_affinity
    out_lines.append(f"**STRATEGY_REGIME_AFFINITY coverage (live count, B892):** {n_with_affinity} of {len(ALL_STRATEGIES)} strategies have explicit regime affinity declarations in `regime_selector.STRATEGY_REGIME_AFFINITY`. {n_without_affinity} strategies fall through to default 'all regimes'. Per CLAUDE.md criterion #11 + DEC-611 (B891), the per-regime PASS gate is `min_regimes_passing=1` so strategies without explicit affinity can still earn regime-specific deployment via cube empirical PASS in any regime.")
    out_lines.append("")
    # B894 SCRUB: Stage 4 approvals per-strategy mapping line removed - sourced
    # from stale approvals.json (R4-era; pre-B722/B874 deletions). Will be
    # restored post-R5 with fresh data per CHECKLIST #111.
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
    # B894 (2026-06-18) Council 18 SCRUB: removed columns sourced from stale
    # R4/approvals.json data: S4 Reviewed, Producer Bug Fix, R4 Fires,
    # Stage 4 Status. Retained: Name, Category, Direction, Trigger Conditions
    # plain, Trigger code, Signals consumed, Regime affinity, Roster Status.
    # Live cube fire status + S4 status will be re-introduced post-R5 via
    # CHECKLIST #111 freshness audit gate.
    out_lines.append("| # | Name | Category | Direction | Trigger Conditions (plain) | Trigger (code) | Signals consumed | Regime affinity | Roster Status |")
    out_lines.append("|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        trigger = r["fires_expr"].replace("|", "\\|").replace("\n", "<br>")
        # Truncate very long triggers for table readability
        if len(trigger) > 250:
            trigger = trigger[:247] + "..."
        sigs = ", ".join(r["signals_used"]) if r["signals_used"] else "(see source)"
        if len(sigs) > 120:
            sigs = sigs[:117] + "..."
        # B586 + B589: plain-language trigger. B589 owner directive
        # ("comprehensive information for a new reader") raised truncation
        # cap so detailed signal definitions are not cut.
        trigger_plain = render_trigger_plain(r["signals_used"], r["fires_expr"])
        # No truncation - owner wants comprehensive (B589). Long rows wrap
        # naturally in markdown table renderers; the GitHub Pages dashboard
        # already handles wide cells.
        # Escape pipes in plain trigger so they don't break the table
        trigger_plain = trigger_plain.replace("|", "\\|")
        out_lines.append(
            f"| {i} | `{r['name']}` | {r['category']} | {r['direction']} | "
            f"{trigger_plain} | `{trigger}` | {sigs} | {r['regime']} | "
            f"{r['status']} |"
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
