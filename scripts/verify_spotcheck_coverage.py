#!/usr/bin/env python
"""B1634 / CHECKLIST #214 - can the spot check actually verify THIS strategy?

Owner correction 2026-08-17: step 4 of MANDATORY POST-CONFIG ANALYSIS is a
STANDARD, not a check written for one strategy. `smc_breaker_block_long` reads
two OHLCV-derived signals, so an OHLCV-only spot check happens to be complete
for it. **That is a property of the strategy, not of the check.** The next
strategies in the roster read smart-money, congressional, insider, news,
earnings, index-rebalance and short-interest signals - and for those, an
OHLCV-only re-derivation certifies nothing while looking identical in the
output.

So the check declares WHAT IT CAN VERIFY, the strategy declares WHAT IT READS,
and this script refuses to certify the gap. Fail-CLOSED (#211): a key it cannot
classify counts as unverifiable, because an unrecognised input is exactly the
one nobody thought about.

Usage:
    python scripts/verify_spotcheck_coverage.py smc_breaker_block_long
    python scripts/verify_spotcheck_coverage.py --all
Exit: 0 = every key the strategy reads is verifiable; 2 = a gap.

**WIRED (header corrected B3139q-r186, S6-B3397).** This block used to read
"HAND-RUN-ONLY ... nothing invokes this automatically" (B1704), and that is
false now: scripts/run_postconfig.py's spot_coverage runs audit() on EVERY landing
with the family checker's own verifiable families (checker_verifies), and
step 4 says CERTIFIED or NOT CERTIFIED with the gap named (census 1874).
A banner left saying nothing calls a gate teaches every reader that the gate
is decorative (#224; the prelaunch_gate precedent, B2159).
"""
from __future__ import annotations

import argparse
import re
import sys

# What `spot_check_trades.py` can INDEPENDENTLY re-derive today: OHLCV bars
# plus everything computed from them (SMC primitives, EMAs, ATR, candles...).
VERIFIABLE_FAMILIES = {"ohlcv"}

# key prefix/substring -> data family. Order matters: first match wins.
FAMILY_RULES: tuple[tuple[str, str], ...] = (
    # S6-B3397 (B3139q-r186): OHLCV-derived keys the patterns below misfiled or
    # missed, MEASURED on the 17 battery families - force_index_* matched
    # `index_` and read as an index EVENT (it is price x volume); camarilla
    # (above_cam_*), floor pivots (above_r1 / below_s1), the naked POC (a
    # volume-profile level), the pairs spread keys and xs_ivol (idiosyncratic
    # vol from returns) matched nothing and counted UNKNOWN. Most specific first.
    (r"^(force_index_|above_cam_|below_cam_|above_r\d|below_s\d|naked_poc_|"
     r"pair_|xs_ivol)", "ohlcv"),
    (r"^committed_growth_", "smart_money"),
    # SPECIFIC families FIRST. B1634: `sma` matched inside `smart_money_score`
    # and classified a smart-money signal as OHLCV - a substring collision, the
    # exact L472 class (a match is not evidence of the RIGHT presence). Ordering
    # by specificity is the fix; the loose indicator regex is a catch-all and a
    # catch-all must never run first.
    (r"(smart_money|insider|congress|lobby|13f|institutional|whale|"
     r"cluster_buy|cluster_sell|activist)", "smart_money"),
    (r"(news|sentiment|headline|apewisdom|reddit|trends)", "news"),
    (r"(earnings|eps_|revenue|guidance|pead|yoy|surprise|blackout)", "fundamental"),
    (r"(short_interest|borrow|days_to_cover|squeeze_risk)", "short_interest"),
    (r"(index_|rebalance|sp500_|nasdaq_|russell)", "index_events"),
    (r"(sector|etf|macro|vix|dxy|yield|fred|aaii|fear_greed|cot_)", "macro"),
    (r"(8k|10q|10k|sec_|filing|m_and_a|buyback|spinoff|ipo)", "filings"),
    (r"(classification_change|sector_classification)", "reference_data"),
    # then price-derived
    (r"^(smc_|ict_|po3_|judas|mmbm|mmsm|turtle_soup)", "ohlcv"),
    (r"^(near_[rs]\d|at_support|at_resistance|above_prev_|below_prev_|"
     r"xs_momentum|xs_combined|inside_bar|outside_bar|nr7|wide_range)", "ohlcv"),
    (r"(ema|sma|rsi|macd|atr|adx|obv|vwap|avwap|bollinger|bb_|donchian|"
     r"keltner|supertrend|hull|ichimoku|stoch|cci|mfi|roc|cmf|psar|"
     r"pivot|camarilla|cpr|fib|squeeze|volume|vol_|price_|close_|high_|"
     r"low_|open_|gap_|range_|candle|doji|hammer|engulf|star|soldier|"
     r"crow|marubozu|pin_bar|harami|tweezer|52w|dc20|breakout|breakdown|"
     r"retest|trend|regime|swing|hh_|ll_|higher_|lower_)", "ohlcv"),
)


# S6-B3397 (census 1874): what each battery spot checker's legs re-derive
# INDEPENDENTLY of the engine record, by input family - read from each
# checker's own leg docstring at B3139q-r186. The raw-arithmetic and producer
# checkers recompute their condition from cached bars; the institutional
# checker also reads the 13F persistence precompute directly (its leg A);
# spot_check_replay's leg A IS the engine record and leg B replays the
# strategy on it, so it re-derives no input family at all. A checker missing
# here verifies nothing (fail closed, L642).
CHECKER_VERIFIES: dict = {
    "spot_check_trades.py": frozenset({"ohlcv"}),
    "spot_check_smc_family.py": frozenset({"ohlcv"}),
    "spot_check_smc_lsr.py": frozenset({"ohlcv"}),
    "spot_check_smc_obb.py": frozenset({"ohlcv"}),
    "spot_check_bollinger.py": frozenset({"ohlcv"}),
    "spot_check_npoc.py": frozenset({"ohlcv"}),
    "spot_check_pairs.py": frozenset({"ohlcv"}),
    "spot_check_candle.py": frozenset({"ohlcv"}),
    "spot_check_producer.py": frozenset({"ohlcv"}),
    "spot_check_institutional.py": frozenset({"ohlcv", "smart_money"}),
    "spot_check_replay.py": frozenset(),
}


def checker_verifies(checker_script: str) -> frozenset:
    """The input families `checker_script` re-derives independently; empty
    for a checker this table does not name (fail closed)."""
    return CHECKER_VERIFIES.get(str(checker_script), frozenset())


def classify(key: str) -> str:
    k = str(key).lower()
    for pat, fam in FAMILY_RULES:
        if re.search(pat, k):
            return fam
    return "UNKNOWN"


def keys_for(strategy_name: str) -> list[str]:
    """The signal keys a strategy DECLARES it uses (`signals_used` in `_strat`).

    Declared rather than runtime-recorded on purpose: a runtime probe only sees
    the branches that a synthetic input happens to take, and `and` short-circuits
    hide the rest - the same blind spot that made static and runtime key
    discovery fail in COMPLEMENTARY directions during B1565.
    """
    import inspect
    from backtest.signals import screener
    fn = screener.ALL_STRATEGIES.get(strategy_name)
    if fn is None:
        raise SystemExit(f"unknown strategy: {strategy_name}")
    src = inspect.getsource(fn)
    keys: list[str] = []
    for lst in re.findall(r"\[([^\]]*?)\]", src, re.S):
        if '"' not in lst and "'" not in lst:
            continue
        for k in re.findall(r"""["']([a-zA-Z0-9_<>=.]+)["']""", lst):
            if len(k) > 2 and not k.startswith(("Above", "Below", "Bearish", "Bullish")):
                keys.append(k)
    # `s.get("key", ...)` reads too - they are the real gates
    keys += re.findall(r"""s\.get\(\s*["']([a-zA-Z0-9_]+)["']""", src)
    return sorted(set(keys))


def audit(strategy_name: str, verifiable=None) -> tuple[dict, list[str]]:
    """(input families -> keys, the families the check cannot verify).
    `verifiable` is the checker's own set (checker_verifies); None keeps the
    CLI's OHLCV-only model."""
    can = VERIFIABLE_FAMILIES if verifiable is None else verifiable
    fams: dict[str, list[str]] = {}
    for k in keys_for(strategy_name):
        fams.setdefault(classify(k), []).append(k)
    gaps = [f for f in fams if f not in can]
    return fams, sorted(gaps)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("strategy", nargs="?")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    from backtest.signals import screener
    names = (sorted(screener.ALL_STRATEGIES) if a.all
             else [a.strategy] if a.strategy else [])
    if not names:
        ap.error("give a strategy name or --all")

    bad = 0
    for n in names:
        fams, gaps = audit(n)
        if a.all and not gaps:
            continue
        print(f"\n{n}")
        for f, ks in sorted(fams.items()):
            mark = "ok " if f in VERIFIABLE_FAMILIES else "GAP"
            print(f"   [{mark}] {f:<15} {ks[:6]}{' ...' if len(ks) > 6 else ''}")
        if gaps:
            bad += 1
            print(f"   -> spot check CANNOT verify: {gaps}. An OHLCV-only "
                  f"re-derivation would certify this strategy without ever "
                  f"reading its {gaps[0]} input.")
    if a.all:
        print(f"\n{bad} of {len(names)} strategies have inputs the spot check "
              f"cannot verify.")
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
