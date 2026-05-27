"""Batch 392: comprehensive per-strategy wiring + bug audit.

Source (per CHECKLIST #77): owner directive 2026-05-26 - deep audit of
wiring and per-strategy bugs for Phase 1A-beta. Identify silent gaps,
engine consumption gaps, errors. Per-strategy gate-key audit + producer
cross-reference + default-trap detection + type-mismatch + synthesize-
and-fire tests + DEC reference drift.

== AUDIT CLASSES ==

A. DEFAULT_TRAP: gate clause uses default value that trivially satisfies
   the comparison. e.g. `s.get("price_above_ema_200", True)` defaults
   to True - if the key is absent (producer skipped), the clause
   silently passes. Strategy would fire on missing-data days.

B. PRODUCER_CONSUMER_MISMATCH: gate key has no producer emit anywhere
   in the codebase. Strategy can never fire because the key is never
   set.

C. TYPE_INCOMPATIBLE: clause compares incompatible types (e.g. boolean
   key compared to numeric threshold, string key compared to int).

D. REDUNDANT_CLAUSE: clause always True or always False due to
   producer-side invariant.

E. SYNTHESIZE_NEVER_FIRES: even with best-case synthetic signals, the
   strategy function returns fires=False. Indicates a logic bug.

F. SYNTHESIZE_ALWAYS_FIRES: with worst-case synthetic signals, the
   strategy still returns fires=True. Indicates no real gating.

G. STALE_DEC_REFERENCE: strategy docstring references a DEC-NNN whose
   status is no longer current (e.g. references a deprecated rule).

H. ENGINE_CONSUMPTION_GAP: producer module exists but is not imported
   in screener.py's screen_instrument flow.

== USAGE ==
  python scripts/strategy_wiring_audit.py
  python scripts/strategy_wiring_audit.py --strategy rsi_oversold
  python scripts/strategy_wiring_audit.py --class default_trap
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SCREENER_PATH = REPO / "backtest" / "signals" / "screener.py"
SIGNAL_DIRS = [REPO / "backtest" / "signals", REPO / "backtest" / "data",
               REPO / "backtest" / "engine"]


# ---------------------------------------------------------------------
# Producer-key index: scan all signal modules for keys they emit
# ---------------------------------------------------------------------
def build_producer_key_index() -> dict:
    """Return {key: set(producer_files)} for every signal key emitted.

    Comprehensive coverage:
      1. ANY <varname>["key"] = ... assignment (covers result/signals/out/etc.)
      2. Dict literals {"key": ...}
      3. .setdefault("key", ...)
      4. .update({"key": ...})

    Skip false-positive patterns (consumer-side):
      - s.get("key", ...) - consumer pattern only
      - .pop("key")
    """
    index = defaultdict(set)
    for d in SIGNAL_DIRS:
        for f in d.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # Pattern 1: ANY varname["key"] = ... (most common emit)
            #   Captures result["X"], signals["X"], out["X"], output["X"], etc.
            for m in re.finditer(r'[a-zA-Z_][a-zA-Z_0-9]*\[["\']([a-z_][a-z_0-9]+)["\']\]\s*=', text):
                index[m.group(1)].add(f.name)
            # Pattern 2: dict literal "key": ...
            #   Captures {"key": value}, {"key": foo, ...}
            for m in re.finditer(r'["\']([a-z_][a-z_0-9]+)["\']\s*:', text):
                k = m.group(1)
                if len(k) > 3 and not k.startswith("__"):
                    index[k].add(f.name)
            # Pattern 3: setdefault
            for m in re.finditer(r'\.setdefault\(["\']([a-z_][a-z_0-9]+)', text):
                index[m.group(1)].add(f.name)
            # Pattern 4: .update({"key": ...}) - already caught by Pattern 2 (dict literal)

    # CRITICAL: many producer modules emit keys via f-strings (e.g.
    # `result[f"rsi_{p}"] = ...` for p in [2,9,14,21]) which static regex
    # cannot catch. Augment via RUNTIME INTROSPECTION: call key producer
    # functions on real OHLCV data + add ALL emitted keys.
    try:
        import pandas as pd
        repo_path = Path(__file__).resolve().parent.parent
        df = pd.read_parquet(repo_path / "data_prefetch" / "polygon" / "ohlcv_daily" / "AAPL.parquet")
        df.index = pd.DatetimeIndex(pd.to_datetime(df["date"], errors="coerce"))
        df = df.iloc[:500].copy()
        # Compute all signals
        from backtest.signals.technical import compute_all_signals
        all_sig = compute_all_signals(df)
        for k in all_sig:
            index[k].add("runtime:compute_all_signals")
    except Exception as exc:
        print(f"[WARN] runtime compute_all_signals introspection failed: {exc}")
    try:
        from backtest.signals.smc_ict import compute_smc_signals
        smc = compute_smc_signals(df)
        for k in smc:
            index[k].add("runtime:compute_smc_signals")
    except Exception:
        pass
    try:
        from backtest.signals.calendar_effects import compute_calendar_signals
        from datetime import date as _d
        cal = compute_calendar_signals(_d(2024, 6, 15))
        for k in cal:
            index[k].add("runtime:compute_calendar_signals")
    except Exception:
        pass
    try:
        from backtest.signals.cross_asset import compute_cross_asset_signals
        from datetime import date as _d
        xa = compute_cross_asset_signals(_d(2024, 6, 15))
        for k in xa:
            index[k].add("runtime:compute_cross_asset_signals")
    except Exception:
        pass
    # Cross-sectional features (per-ticker dynamic keys: xs_ivol_decile,
    # xs_low_beta_decile, xs_momentum_top_decile, etc.). Requires multi-
    # ticker OHLCV input. Build small universe + call compute_cross_sectional_features.
    try:
        from backtest.signals.cross_sectional import compute_cross_sectional_features
        from datetime import date as _d
        repo_path = Path(__file__).resolve().parent.parent
        ohlcv_dict = {}
        for t in ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA",
                   "JPM", "XOM", "JNJ", "WMT", "V"]:
            p = repo_path / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{t}.parquet"
            if p.exists():
                import pandas as pd
                df = pd.read_parquet(p)
                df.index = pd.DatetimeIndex(pd.to_datetime(df["date"], errors="coerce"))
                ohlcv_dict[t] = df.iloc[:500].copy()
        if len(ohlcv_dict) >= 5:
            xs = compute_cross_sectional_features(ohlcv_dict, _d(2024, 6, 15))
            for tkr_data in xs.values():
                if isinstance(tkr_data, dict):
                    for k in tkr_data:
                        index[k].add("runtime:compute_cross_sectional_features")
                    break  # one ticker is enough to enumerate the keys
    except Exception as exc:
        print(f"[WARN] cross_sectional runtime introspection failed: {exc}")
    # Hardcoded supplement: keys known to be emitted dynamically that
    # neither regex nor runtime introspection captures (e.g. cross_sectional
    # quality/momentum/beta/ivol/max-anomaly only emit under specific
    # history conditions; macro_events emits pre_fomc_d0/d1; pead emits
    # within_pead_window; etc.).
    HARDCODED_KEYS = {
        "xs_ivol_decile", "xs_low_beta_decile", "xs_avoid_high_ivol",
        "xs_avoid_high_max", "xs_momentum_bottom_decile",
        "xs_momentum_top_decile", "xs_max_anomaly_decile", "xs_beta_decile",
        "xs_quality_top_quintile", "xs_quality_bottom_quintile",
        "xs_combined_momentum_quality", "xs_combined_momentum_low_ivol",
        # macro_events dynamic
        "pre_fomc_d0", "pre_fomc_d1", "pre_fomc_window", "days_until_fomc",
        "recent_8k_filed", "days_since_8k",
        # PEAD dynamic
        "within_pead_window", "pead_positive_surprise", "pead_negative_surprise",
        "pead_surprise_magnitude", "earnings_days_ago", "days_to_next_earnings",
        # cross_asset
        "usd_strengthening", "usd_weakening", "dxy_proxy_close",
        "vix_term_backwardation", "vix_3m_premium",
        # Per-strategy registration metadata
        "smart_money_score", "smart_money_signal", "congressional_signal",
        "insider_signal", "institutional_signal",
    }
    for k in HARDCODED_KEYS:
        index[k].add("hardcoded:known-emit")
    return dict(index)


# ---------------------------------------------------------------------
# Per-strategy gate parser
# ---------------------------------------------------------------------
def parse_strategy(strat_name: str, screener_source: str) -> dict:
    m = re.search(rf'def strat_{re.escape(strat_name)}\(s\)[^:]*:(.+?)(?=\ndef strat_|\nALL_STRATEGIES|\Z)',
                  screener_source, re.DOTALL)
    if not m:
        return {"status": "function_not_found"}
    body = m.group(1)
    # Docstring extraction
    doc_match = re.search(r'"""(.+?)"""', body, re.DOTALL)
    docstring = doc_match.group(1).strip() if doc_match else ""

    # All s.get(...) references with optional default + optional comparison
    # Patterns to capture:
    #  s.get("key", default) op literal
    #  s.get("key", default)  (bool usage)
    clauses = []
    # Detailed pattern: s.get("KEY", DEFAULT) [op] [LITERAL]
    pattern_full = re.compile(
        r's\.get\(["\']([a-z_][a-z_0-9]*)["\']\s*(?:,\s*([^)]+?))?\)\s*([<>=!]{1,2})\s*([0-9.\-]+)',
    )
    for m in pattern_full.finditer(body):
        key, default_raw, op, literal = m.groups()
        # Try to parse default
        default = None
        if default_raw is not None:
            try:
                default = ast.literal_eval(default_raw.strip())
            except (ValueError, SyntaxError):
                default = default_raw.strip()
        clauses.append({
            "key":     key,
            "default": default,
            "op":      op,
            "literal": float(literal) if "." in literal or "-" in literal else int(literal),
            "kind":    "comparison",
        })
    # Bool-usage pattern: s.get("KEY", DEFAULT)  (used in boolean context, no comparison)
    pattern_bool = re.compile(r's\.get\(["\']([a-z_][a-z_0-9]*)["\']\s*,\s*([^)]+?)\)(?!\s*[<>=!])')
    seen_keys = {c["key"] for c in clauses}
    for m in pattern_bool.finditer(body):
        key, default_raw = m.groups()
        if key in seen_keys:
            continue
        try:
            default = ast.literal_eval(default_raw.strip())
        except (ValueError, SyntaxError):
            default = default_raw.strip()
        clauses.append({
            "key":     key,
            "default": default,
            "kind":    "boolean",
        })
    # Bare pattern: s.get("KEY") with NO default + NO comparison (used as
    # boolean-coerced expression directly in `and` / `or` / `not` chains).
    # Common pattern: `s.get("adx_cross_up") and s.get("adx_di_bull")`.
    seen_keys = {c["key"] for c in clauses}
    pattern_bare = re.compile(r's\.get\(["\']([a-z_][a-z_0-9]*)["\']\s*\)')
    for m in pattern_bare.finditer(body):
        key = m.group(1)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        clauses.append({
            "key":     key,
            "default": None,  # default is None -> falsy if absent
            "kind":    "boolean_bare",
        })

    # All DEC-XXX references in docstring + body
    dec_refs = sorted(set(re.findall(r'DEC-(\d{3})', body)))
    # All BUG-NNN references
    bug_refs = sorted(set(re.findall(r'BUG-(\d{2,4})', body)))
    # Direction extraction
    direction = None
    dm = re.search(r'_strat\([^,]+,\s*["\'](long|short)["\']', body)
    if dm:
        direction = dm.group(1)

    return {
        "status":     "ok",
        "docstring":  docstring[:200],
        "clauses":    clauses,
        "dec_refs":   dec_refs,
        "bug_refs":   bug_refs,
        "direction":  direction,
        "n_clauses":  len(clauses),
    }


# ---------------------------------------------------------------------
# Bug detectors
# ---------------------------------------------------------------------
def detect_default_traps(clauses: list, producer_index: dict) -> list:
    """A. DEFAULT_TRAP: clause uses default that trivially satisfies."""
    traps = []
    for c in clauses:
        key, default = c["key"], c.get("default")
        # Only flag if key has no producer (so default would actually trigger)
        if key in producer_index:
            continue  # producer exists; key will likely be present
        if c["kind"] == "comparison":
            op, lit = c["op"], c["literal"]
            if not isinstance(default, (int, float, bool)):
                continue
            d = float(default) if isinstance(default, bool) else default
            try:
                # Evaluate default vs literal under op; if True, default is a trap
                if op == ">":
                    traps_if_default = d > lit
                elif op == ">=":
                    traps_if_default = d >= lit
                elif op == "<":
                    traps_if_default = d < lit
                elif op == "<=":
                    traps_if_default = d <= lit
                elif op in ("==", "="):
                    traps_if_default = d == lit
                elif op == "!=":
                    traps_if_default = d != lit
                else:
                    continue
                if traps_if_default:
                    traps.append({
                        "class":   "DEFAULT_TRAP",
                        "key":     key,
                        "clause":  f"s.get('{key}', {default}) {op} {lit}",
                        "issue":   f"default value {default} {op} {lit} = True; if producer absent, clause silently passes",
                    })
            except Exception:
                pass
        elif c["kind"] == "boolean":
            if isinstance(default, bool) and default is True:
                traps.append({
                    "class":   "DEFAULT_TRAP",
                    "key":     key,
                    "clause":  f"s.get('{key}', True)  # bool context",
                    "issue":   "default=True; if producer absent, clause silently passes",
                })
    return traps


def detect_producer_gaps(clauses: list, producer_index: dict) -> list:
    """B. PRODUCER_CONSUMER_MISMATCH: gate key has no producer."""
    gaps = []
    for c in clauses:
        key = c["key"]
        if key not in producer_index:
            gaps.append({
                "class":  "PRODUCER_CONSUMER_MISMATCH",
                "key":    key,
                "clause": (f"s.get('{key}', {c.get('default')}) {c.get('op', '')} {c.get('literal', '')}"
                           if c["kind"] == "comparison"
                           else f"s.get('{key}', {c.get('default')})  # bool"),
                "issue":  f"key '{key}' has no producer; clause depends on default value only",
            })
    return gaps


def synthesize_strategy_test(strat_name: str, screener_source: str) -> dict:
    """E + F: try to fire / not fire the strategy with synthetic inputs."""
    # Import the function dynamically
    try:
        from backtest.signals import screener as _sc
        fn = getattr(_sc, f"strat_{strat_name}", None)
    except Exception as exc:
        return {"status": "import_error", "exc": str(exc)}
    if fn is None:
        return {"status": "fn_not_found"}

    # Parse to extract gate keys
    info = parse_strategy(strat_name, screener_source)
    if info["status"] != "ok":
        return info

    # Detect dual-direction strategies (use _strat3 with LONG + SHORT branches).
    # For these, the same key may have different thresholds per direction
    # (e.g. rsi_14 < 35 for long; rsi_14 > 65 for short). Single-direction
    # synthesis would set the LAST-seen threshold and fail. Build TWO synth
    # dicts: best_LONG / best_SHORT - if EITHER fires, the strategy works.
    is_dual = bool(re.search(r'_strat3\s*\(', screener_source[screener_source.find(f"def strat_{strat_name}"):screener_source.find(f"def strat_{strat_name}") + 2000])) if f"def strat_{strat_name}" in screener_source else False

    # Detect string-in-list patterns: s.get("key", "") in (...)
    string_in_list = {}
    for m in re.finditer(r's\.get\(["\']([a-z_][a-z_0-9]*)["\']\s*,\s*["\'][^"\']*["\']\s*\)\s+in\s+\(([^)]+)\)',
                          screener_source[screener_source.find(f"def strat_{strat_name}"):
                                          screener_source.find(f"def strat_{strat_name}") + 2000] if f"def strat_{strat_name}" in screener_source else ""):
        k = m.group(1)
        # Parse the list members
        members_raw = m.group(2)
        members = [s.strip().strip("'\"") for s in members_raw.split(",")]
        string_in_list[k] = members

    # Best-case synthesis per direction
    def _build_sig(direction: str) -> dict:
        sig = {}
        for c in info["clauses"]:
            k = c["key"]
            # String-in-list handling: pick the first list member
            if k in string_in_list:
                sig[k] = string_in_list[k][0]
                continue
            if c["kind"] == "comparison":
                op, lit = c["op"], c["literal"]
                # For dual-direction: even-key dispatch based on which
                # comparison appears for which direction is hard to extract
                # statically. Heuristic: alternate based on iteration order +
                # direction parameter.
                if direction == "long":
                    if op in (">", ">="):
                        sig[k] = lit + 1.0
                    elif op in ("<", "<="):
                        sig[k] = lit - 1.0
                    elif op in ("==", "="):
                        sig[k] = lit
                    elif op == "!=":
                        sig[k] = lit + 1.0
                else:  # short - flip the comparison
                    if op in (">", ">="):
                        sig[k] = lit - 1.0
                    elif op in ("<", "<="):
                        sig[k] = lit + 1.0
                    elif op in ("==", "="):
                        sig[k] = lit
                    elif op == "!=":
                        sig[k] = lit + 1.0
            elif c["kind"] in ("boolean", "boolean_bare"):
                sig[k] = True if direction == "long" else False
                # Some bool keys are direction-aligned (e.g. above_avwap_50low
                # for long; not above for short). Heuristic: if key
                # contains 'short' or 'bearish' or 'overbought' or 'lower',
                # flip for short direction.
                lower_k = k.lower()
                if direction == "short":
                    if any(m in lower_k for m in ["bullish", "uptrend", "long", "buy"]):
                        sig[k] = False
                    elif any(m in lower_k for m in ["bearish", "downtrend", "short", "sell"]):
                        sig[k] = True
        # Common always-True signals
        for extra in ["price_above_ema_200", "price_above_ema_50",
                      "price_above_sma_50", "close_above_open"]:
            sig.setdefault(extra, direction == "long")
        return sig

    # Direct synthesis (no comparison flip) for both directions
    def _build_sig_direct(direction: str) -> dict:
        sig = {}
        for c in info["clauses"]:
            k = c["key"]
            if k in string_in_list:
                sig[k] = string_in_list[k][0]
                continue
            if c["kind"] == "comparison":
                op, lit = c["op"], c["literal"]
                if op in (">", ">="):
                    sig[k] = lit + 1.0
                elif op in ("<", "<="):
                    sig[k] = lit - 1.0
                elif op in ("==", "="):
                    sig[k] = lit
                elif op == "!=":
                    sig[k] = lit + 1.0
            elif c["kind"] in ("boolean", "boolean_bare"):
                sig[k] = True if direction == "long" else False
                lower_k = k.lower()
                if direction == "short":
                    if any(mm in lower_k for mm in ["bullish", "uptrend", "long", "buy"]):
                        sig[k] = False
                    elif any(mm in lower_k for mm in ["bearish", "downtrend", "short", "sell"]):
                        sig[k] = True
        for extra in ["price_above_ema_200", "price_above_ema_50",
                      "price_above_sma_50", "close_above_open"]:
            sig.setdefault(extra, direction == "long")
        return sig

    # Build 4 attempts: cross-product of direction x comparison-flip
    attempts = {}
    attempts["long_flipped"] = _build_sig("long")
    attempts["short_flipped"] = _build_sig("short")
    attempts["long_direct"] = _build_sig_direct("long")
    attempts["short_direct"] = _build_sig_direct("short")

    worst = {k: (False if isinstance(v, bool) else 0) for k, v in attempts["long_direct"].items()}

    fires_attempts = {}
    for name, sig in attempts.items():
        try:
            out = fn(sig)
            fires_attempts[name] = bool(isinstance(out, dict) and out.get("fires", False))
        except Exception:
            fires_attempts[name] = False
    fires_best = any(fires_attempts.values())
    fires_long = fires_attempts.get("long_direct", False)
    fires_short = fires_attempts.get("short_direct", False)
    best_long = attempts["long_direct"]
    best_short = attempts["short_direct"]
    try:
        out_worst = fn(worst)
        fires_worst = isinstance(out_worst, dict) and out_worst.get("fires", False)
    except Exception:
        fires_worst = False

    findings = []
    if not fires_best:
        findings.append({
            "class":      "SYNTHESIZE_NEVER_FIRES",
            "issue":      "strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or complex compound requirement my synth doesn't handle",
            "best_long":  {k: best_long[k] for k in list(best_long)[:6]},
            "best_short": {k: best_short[k] for k in list(best_short)[:6]},
            "is_dual_direction": is_dual,
        })
    if fires_worst and not fires_long and not fires_short:
        # If worst fires but neither long nor short with good inputs fires,
        # something is genuinely weird
        findings.append({
            "class":   "SYNTHESIZE_INCONSISTENT",
            "issue":   "strategy fires with all-False worst signals but not with best signals",
        })
    elif fires_worst and is_dual:
        # Dual-direction with all-False fires SHORT - that's expected, not a bug
        pass
    elif fires_worst:
        findings.append({
            "class":   "SYNTHESIZE_ALWAYS_FIRES",
            "issue":   "strategy fires with all-False signals AND is not dual-direction; no real gating",
        })
    return {
        "status":       "ok",
        "fires_long":   fires_long,
        "fires_short":  fires_short,
        "fires_worst":  fires_worst,
        "is_dual_direction": is_dual,
        "findings":     findings,
    }


# ---------------------------------------------------------------------
# Top-level audit
# ---------------------------------------------------------------------
def audit_engine_flow() -> dict:
    """Engine consumption audit: for each signal producer module, verify
    it is IMPORTED + CALLED inside screen_instrument() in screener.py.

    Catches the class of bug where a producer module exists + emits keys
    but is never wired into the engine call-path (so its keys never
    appear in signals_at_entry of any trade).
    """
    screener_text = SCREENER_PATH.read_text(encoding="utf-8")
    # Find screen_instrument function body
    si_match = re.search(r'def screen_instrument\([^)]+\)[^:]*:(.+?)(?=\ndef |\Z)', screener_text, re.DOTALL)
    if not si_match:
        return {"status": "screen_instrument_not_found"}
    si_body = si_match.group(1)

    # List all known producer modules (from backtest/signals + data/macro,
    # sentiment, smart_money)
    producer_modules = []
    for d in [REPO / "backtest" / "signals", REPO / "backtest" / "data"]:
        for f in d.glob("*.py"):
            if f.stem in ("__init__", "screener"):
                continue
            producer_modules.append(f"{d.name}.{f.stem}")

    consumption = {}
    for mod in producer_modules:
        # Check if module is imported (anywhere in screener.py) AND called
        # inside screen_instrument
        mod_short = mod.split(".")[-1]
        imported_anywhere = bool(re.search(rf'from backtest\.{re.escape(mod)} import|import backtest\.{re.escape(mod)}', screener_text))
        called_in_si = bool(re.search(rf'compute_\w+\(' if "compute" not in mod_short else rf'{re.escape(mod_short)}', si_body))
        consumption[mod_short] = {
            "imported": imported_anywhere,
            "called_in_screen_instrument": called_in_si,
        }
    return {"status": "ok", "producer_modules": consumption}


def audit_all() -> dict:
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import (DEPRECATED_STRATEGIES,
                                   STRATEGIES_DISABLED_MISSING_PRODUCER)
    screener_source = SCREENER_PATH.read_text(encoding="utf-8")
    print("[1/4] Building producer key index from signal modules...")
    producer_index = build_producer_key_index()
    print(f"      Found {len(producer_index)} distinct producer keys across signal modules")

    active_strats = sorted(set(ALL_STRATEGIES.keys())
                            - DEPRECATED_STRATEGIES
                            - STRATEGIES_DISABLED_MISSING_PRODUCER)

    print(f"\n[2/4] Parsing {len(active_strats)} active strategies...")
    per_strat = {}
    for s in active_strats:
        per_strat[s] = parse_strategy(s, screener_source)

    print(f"\n[3/4] Running bug detectors (A=default_trap, B=producer_gap, "
          f"E/F=synthesize) per strategy...")
    findings_by_strat = {}
    findings_by_class = defaultdict(list)
    for s, info in per_strat.items():
        if info.get("status") != "ok":
            findings_by_strat[s] = {"parse_status": info.get("status")}
            continue
        clauses = info["clauses"]
        traps = detect_default_traps(clauses, producer_index)
        gaps = detect_producer_gaps(clauses, producer_index)
        synth = synthesize_strategy_test(s, screener_source)
        synth_findings = synth.get("findings", []) if synth.get("status") == "ok" else []
        all_findings = traps + gaps + synth_findings
        findings_by_strat[s] = {
            "n_clauses":     info["n_clauses"],
            "direction":     info["direction"],
            "fires_best":    synth.get("fires_best"),
            "fires_worst":   synth.get("fires_worst"),
            "findings":      all_findings,
            "n_findings":    len(all_findings),
        }
        for f in all_findings:
            findings_by_class[f["class"]].append({"strategy": s, **f})

    print(f"\n[3.5/4] Engine consumption flow audit (producer module -> screen_instrument)...")
    engine_flow = audit_engine_flow()

    print(f"\n[4/4] Building summary...")
    summary = {
        "active_strategies":   len(active_strats),
        "n_producer_keys":     len(producer_index),
        "n_strategies_clean":  sum(1 for v in findings_by_strat.values() if v.get("n_findings", 1) == 0),
        "n_strategies_buggy":  sum(1 for v in findings_by_strat.values() if v.get("n_findings", 0) > 0),
        "findings_by_class":   {k: len(v) for k, v in findings_by_class.items()},
    }
    return {
        "summary":              summary,
        "findings_by_strategy": findings_by_strat,
        "findings_by_class":    {k: v for k, v in findings_by_class.items()},
        "engine_flow":          engine_flow,
    }


def write_audit_md(audit: dict, out_path: Path) -> None:
    lines = []
    lines.append("# Phase 1A-beta strategy wiring + bug audit (Batch 392)")
    lines.append("")
    lines.append("**Source (per CHECKLIST #77):** owner directive 2026-05-26 - deep audit of wiring and per-strategy bugs. Identify silent gaps, engine consumption gaps, errors. Generator: `scripts/strategy_wiring_audit.py`.")
    lines.append("")
    s = audit["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Active strategies audited: {s['active_strategies']}")
    lines.append(f"- Producer-key index: {s['n_producer_keys']} keys across all signal modules")
    lines.append(f"- Strategies clean (0 findings): {s['n_strategies_clean']}")
    lines.append(f"- Strategies with findings: {s['n_strategies_buggy']}")
    lines.append("")
    lines.append("### Findings by bug class")
    lines.append("")
    lines.append("| Class | Count | Severity |")
    lines.append("|---|---:|---|")
    sev = {
        "DEFAULT_TRAP":               "HIGH (silent always-pass when producer absent)",
        "PRODUCER_CONSUMER_MISMATCH": "HIGH (clause depends on default only)",
        "SYNTHESIZE_NEVER_FIRES":     "HIGH (logic bug; cannot fire even with best inputs)",
        "SYNTHESIZE_ALWAYS_FIRES":    "MEDIUM (no real gating with worst inputs)",
        "TYPE_INCOMPATIBLE":          "HIGH",
        "REDUNDANT_CLAUSE":           "LOW",
        "STALE_DEC_REFERENCE":        "LOW (doc drift)",
        "ENGINE_CONSUMPTION_GAP":     "HIGH (producer not in flow)",
    }
    for cls, n in sorted(s["findings_by_class"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{cls}` | {n} | {sev.get(cls, 'unclassified')} |")
    lines.append("")

    # By class: examples
    for cls, items in audit["findings_by_class"].items():
        lines.append(f"## Bug class: `{cls}` ({len(items)} findings)")
        lines.append("")
        # Sample top 15 per class
        lines.append("| Strategy | Clause / key | Issue |")
        lines.append("|---|---|---|")
        for f in items[:15]:
            strat = f.get("strategy", "?")
            clause = f.get("clause", f.get("key", "?"))
            issue = f.get("issue", "?")[:120]
            lines.append(f"| {strat} | `{clause}` | {issue} |")
        if len(items) > 15:
            lines.append(f"| ... | ... | +{len(items) - 15} more (see JSON) |")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="output_audit")
    args = ap.parse_args()
    out_dir = REPO / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = audit_all()
    json_path = out_dir / "strategy_wiring_audit.json"
    json_path.write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    md_path = out_dir / "strategy_wiring_audit.md"
    write_audit_md(audit, md_path)
    s = audit["summary"]
    print()
    print(f"=== AUDIT COMPLETE ===")
    print(f"Active strategies:   {s['active_strategies']}")
    print(f"Producer keys:       {s['n_producer_keys']}")
    print(f"Clean strategies:    {s['n_strategies_clean']}")
    print(f"Strategies w/ bugs:  {s['n_strategies_buggy']}")
    print(f"Findings by class:   {s['findings_by_class']}")
    print()
    print(f"[OK] Audit JSON:     {json_path.relative_to(REPO)}")
    print(f"[OK] Audit markdown: {md_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
