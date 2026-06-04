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
        rows.append({**meta, "status": status, "regime": regime_str})

    out_lines = []
    out_lines.append("# Strategy Roster - Phase 1A-beta cube reference")
    out_lines.append("")
    out_lines.append(f"**Auto-generated** via `scripts/build_strategy_roster.py`. Do NOT hand-edit. Regenerate every turn that modifies strategies, signals, thresholds, regime affinity, or status.")
    out_lines.append("")
    out_lines.append(f"**Total strategies:** {len(ALL_STRATEGIES)} | **Deprecated:** {len(DEPRECATED_STRATEGIES)} | **Disabled:** {len(STRATEGIES_DISABLED_MISSING_PRODUCER)} | **Active for cube:** {len(ALL_STRATEGIES) - len(DEPRECATED_STRATEGIES | STRATEGIES_DISABLED_MISSING_PRODUCER)}")
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
    out_lines.append("| # | Name | Category | Direction | Trigger | Signals consumed | Regime affinity | Status |")
    out_lines.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        trigger = r["fires_expr"].replace("|", "\\|").replace("\n", "<br>")
        # Truncate very long triggers for table readability
        if len(trigger) > 250:
            trigger = trigger[:247] + "..."
        sigs = ", ".join(r["signals_used"]) if r["signals_used"] else "(see source)"
        if len(sigs) > 120:
            sigs = sigs[:117] + "..."
        out_lines.append(
            f"| {i} | `{r['name']}` | {r['category']} | {r['direction']} | "
            f"`{trigger}` | {sigs} | {r['regime']} | {r['status']} |"
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
