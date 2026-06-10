"""
signals/screener.py - All Layer 1 baseline 60 strategy classes (per CANONICAL_FACTS.md F-002 Layer 1) with entry zone logic and regime filter.

Note: This file implements the Layer 1 baseline. Layer 2 (Phase 0.D ICT/Earnings/Calendar),
Layer 2D (form-derived ICT), Layer 3 (Pass 52 RESOLVED chart-pattern + categories), and
Layer 4 (PENDING strategy-additive) are scheduled per AUDIT_INDEX DEC-045/259/355-362/367-371.
Full layered roster: ~108-133 classes per CANONICAL_FACTS.md F-002.

BUG-23 SUPERSEDED-BY-CANONICAL_FACTS-F-002 Pass 53 v8h+1 cross-reference 2026-05-10:
the "60 baseline classes" count is canonically correct per F-002 Layer 1; the bug
observation was incomplete (didn't account for layered architecture).
BUG-22 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
run_phase1a.py header docstring no longer references stale "60 strategies"
text (verified via grep absence 2026-05-10).

60 baseline classes across 7 categories:
  Pivot-based      (10): S1-S3 bounces, R1-R2 breakouts, CPR bias,
                         Camarilla S3/R3, prev day high/low
  Momentum         ( 9): MACD (2 sets), Hull+RSI, Williams%R, ROC,
                         Awesome Oscillator, StochRSI, PPO, Ultimate Oscillator
  Trend            ( 9): Golden cross (3 pairs), Parabolic SAR, TEMA/DEMA,
                         Ichimoku TK cross, Ichimoku cloud, ADX initiation,
                         Supertrend+MACD
  Mean Reversion   (11): RSI oversold (3 variants), RSI overbought short,
                         MFI oversold, CMF flip, Bollinger (2 variants),
                         Bollinger upper short, Keltner bounce, Stochastic
  Breakout         ( 6): Squeeze, Volume spike, 52-week high, Inside bar,
                         Force Index, Donchian 10-day
  Candle Pattern   ( 6): Morning star, Bullish engulfing at support,
                         Doji at support, Three white soldiers,
                         Shooting star short, Evening star short
  Confluence       ( 9): RSI+volume+200EMA, MACD+Ichimoku, BB squeeze+volume,
                         Pivot+Fib, Golden cross+volume, CPR+momentum,
                         Camarilla+RSI+OBV, Supertrend+Ichimoku+ADX,
                         Williams+Stoch dual oversold

Each strategy returns:
  {"fires": bool, "direction": "long"|"short", "category": str,
   "signals_used": list, "context_bullets": list}
"""

import logging
from datetime import date
from typing import Optional

import pandas as pd

from backtest.config import ENTRY_GAP_ATR_MULT, LIQUIDITY
from backtest.data.fetcher import passes_liquidity_filter
from backtest.signals.technical import compute_all_signals, count_bullish_signals

logger = logging.getLogger(__name__)


# Batch 416 (2026-05-28 owner-approved): rate-limited diagnostic logging for
# silent producer-call failures. The pre-Batch-416 try/except blocks
# swallowed exceptions without trace, which masked the SMC-keys-absent bug
# in the AWS cube run (0 of 29,159 trades had smc_* keys despite the
# function returning 28 keys when called in isolation). Replaces silent
# `except Exception: pass` with `_log_silent_producer_failure(...)` so the
# first instance of each failure mode surfaces in logs. Rate-limited to
# 1 per (mode, exception_type) per process to avoid log spam at universe
# scale (1900+ tickers x daily calls).
_SILENT_PRODUCER_SEEN_FAILURES: set = set()
_SILENT_PRODUCER_SEEN_EMPTIES: set = set()


def _log_silent_producer_failure(producer_name: str, exc: BaseException) -> None:
    """One-shot log per (producer, exception-type) per process. Surfaces
    exceptions that the old `except Exception: pass` blocks swallowed."""
    key = (producer_name, type(exc).__name__)
    if key in _SILENT_PRODUCER_SEEN_FAILURES:
        return
    _SILENT_PRODUCER_SEEN_FAILURES.add(key)
    logger.warning(
        "Batch 416 silent-producer failure (first occurrence; subsequent "
        "suppressed): producer=%s exception=%s: %s",
        producer_name, type(exc).__name__, exc,
    )


def _log_silent_producer_empty(producer_name: str) -> None:
    """One-shot log per producer-name per process when the call returns
    empty / falsy output but did not raise. Catches the SMC pattern: the
    function returns {} silently when guard conditions fail."""
    if producer_name in _SILENT_PRODUCER_SEEN_EMPTIES:
        return
    _SILENT_PRODUCER_SEEN_EMPTIES.add(producer_name)
    logger.warning(
        "Batch 416 silent-producer empty-return (first occurrence; "
        "subsequent suppressed): producer=%s returned empty/falsy",
        producer_name,
    )


# -----------------------------------------------------------------------------
# STRATEGY HELPERS
# -----------------------------------------------------------------------------

def _short_borrow_trap_active(s) -> bool:
    """B671 Round 2 Q5 + Q6 (2026-06-10 owner-approved per AskUserQuestion
    Round 2): SM-5 borrow-trap consult helper.

    Returns True if days_to_cover > 8.0 on the ticker for the bar. When
    True, all SHORT-direction strategy fires on this ticker are blocked
    per the per-strategy pre-fire gate pattern owner approved in Q5.

    Q6 owner decision (2026-06-10): threshold tightened from 5.0 -> 8.0
    per reviewer F5 observation that 5.0 is loose (GME 2021 ~5-7
    borderline; MSTR 2021 ~8-12; BBBY ~6-10). The B519 original
    docstring still resides in strat_short_borrow_trap_avoid (SM-5);
    that strategy's own threshold also updated to 8.0 for consistency.

    Note: SM-5 itself emits direction="avoid", not "short", so its own
    emission is unaffected by this gate. Only direction="short" strategies
    are blocked; direction="long" and direction="avoid" are unaffected.
    """
    dtc = s.get("days_to_cover", 0.0) or 0.0
    return dtc > 8.0


def _strat(fires, direction, category, signals_used, context_bullets):
    """Single-direction strategy  -  fires True/False with fixed direction.

    B671 Round 2 Q5 (owner-approved 2026-06-10 per AskUserQuestion Round 2,
    option "Per-strategy pre-fire gate (cleanest, biggest blast radius)"):
    SHORT-direction emissions are CENTRALLY gated by SM-5 borrow-trap
    consult via inspect.currentframe access to the caller strategy's `s`
    variable. Centralizing the consult here (rather than requiring per-
    strategy edits at every fire call) ensures:

      (1) Every current SHORT strategy is automatically protected
      (2) Every FUTURE SHORT strategy is automatically protected
          (no risk of new strategy author forgetting the consult,
          which was the reviewer F5 concern that motivated this work)
      (3) Single point of policy enforcement; threshold change in
          _short_borrow_trap_active() propagates immediately to all
          consumers

    The gate fires when direction == "short" AND caller has `s` in its
    local frame AND _short_borrow_trap_active(s) returns True. When all
    three conditions hold, `fires` is forced to False before constructing
    the return dict.

    SAFETY:
      - direction == "avoid" (SM-5 itself, other avoid emitters) unaffected
      - direction == "long" unaffected
      - Test-path callers that lack `s` in caller frame are unaffected
        (caller_locals.get("s") returns None -> no block)
      - Backward compatible with all existing test fixtures
    """
    if direction == "short":
        import inspect
        caller_locals = inspect.currentframe().f_back.f_locals
        s = caller_locals.get("s")
        if s is not None and _short_borrow_trap_active(s):
            fires = False
    return {
        "fires":           bool(fires),
        "direction":       direction,
        "category":        category,
        "signals_used":    signals_used,
        "context_bullets": context_bullets,
    }


# -----------------------------------------------------------------------------
# BUG-290 fix (Batch 314 2026-05-24): cap_band signal producer.
# -----------------------------------------------------------------------------
# Owner-approved bands per directive 2026-05-24:
#   micro: < $300M
#   small: $300M - $2B
#   mid:   $2B - $10B
#   large: $10B - $200B
#   mega:  >= $200B
#
# Consumers in the signals dict (screen-time / entry-time):
#   - strat_january_effect_long checks `cap_band in ("micro", "small")`
#
# Note: exit_context._derive_cap_band (used in trade_exit_detail) historically
# emitted suffixed labels ("mega_ge_200B" / "large_10_200B" / "mid_2_10B" /
# "small_lt_2B" / "unknown") and lacked a "micro" tier. Aligning that helper
# with the same 5-band taxonomy is a separate analyzer-side fix (queued); the
# screen-time producer here is authoritative for entry-time gates.
def cap_band_from_market_cap(market_cap) -> str:
    """Map raw market cap (USD) to canonical 5-band label.

    Inputs:
      market_cap - numeric (USD); falsey or non-numeric -> "unknown"
    """
    try:
        cap_b = float(market_cap or 0) / 1e9
    except (TypeError, ValueError):
        return "unknown"
    if cap_b <= 0:
        return "unknown"
    if cap_b >= 200:
        return "mega"
    if cap_b >= 10:
        return "large"
    if cap_b >= 2:
        return "mid"
    if cap_b >= 0.3:
        return "small"
    return "micro"


def _strat3(fires_long, fires_short, category, signals_used_long, signals_used_short,
            bullets_long, bullets_short):
    """Three-state strategy  -  evaluates long, short, or avoid independently.
    Returns the dominant direction; if both fire, returns avoid (conflicting signals).

    B671 Round 2 Q5 (owner-approved 2026-06-10 per AskUserQuestion Round 2):
    SHORT branch gated by SM-5 borrow-trap consult via inspect.currentframe.
    LONG branch unaffected. See _strat docstring for the full rationale +
    safety analysis; same centralized policy applied here.
    """
    if fires_short:
        import inspect
        caller_locals = inspect.currentframe().f_back.f_locals
        s = caller_locals.get("s")
        if s is not None and _short_borrow_trap_active(s):
            fires_short = False
    if fires_long and not fires_short:
        return {"fires": True,  "direction": "long",  "category": category,
                "signals_used": signals_used_long, "context_bullets": bullets_long}
    if fires_short and not fires_long:
        return {"fires": True,  "direction": "short", "category": category,
                "signals_used": signals_used_short, "context_bullets": bullets_short}
    if fires_long and fires_short:
        return {"fires": True,  "direction": "avoid", "category": category,
                "signals_used": signals_used_long + signals_used_short,
                "context_bullets": ["Conflicting long and short signals  -  avoid"]}
    return {"fires": False, "direction": None, "category": category,
            "signals_used": [], "context_bullets": []}


# -----------------------------------------------------------------------------
# CATEGORY 1: PIVOT-BASED (10 strategies)
# -----------------------------------------------------------------------------

def strat_pivot_s1_bounce(s):
    """Floor-trader pivot S1 support bounce / R1 resistance rejection
    with single-bar candle confirmation + OBV flow.

    Fires LONG when ALL THREE: (a) price within 0.3% of pivot S1
    (computed from yesterday's H/L/C); (b) `hammer` OR `bullish_pin
    _bar` formed today; (c) OBV above its 20-bar mean (accumulation).
    SHORT mirror: near_r1 + (shooting_star OR bearish_engulfing) +
    obv_bearish.

    Batch 628 (2026-06-08): F1 family-sweep -> positive symmetric
    `obv_bearish` per feedback_never_use_NOT_s_get_pattern.

    Batch 641 (2026-06-09 owner-directed Tier 1 ship via external-AI
    audit of B640 walk bundle):
      F1 - pin_bar direction-contamination fix. Pre-B641 LONG OR-disjunct
        was `hammer OR pin_bar`. The `pin_bar` producer is direction-
        AGNOSTIC (max(uwk,lwk) > 0.66*rng) - a bar with a dominant
        upper wick (bearish rejection from above) satisfied it, so a
        bearish pin AT SUPPORT could trigger a LONG entry. Fix:
        producer-additive `bullish_pin_bar` / `bearish_pin_bar`
        emitted by compute_candle_signals; LONG side switches to
        `bullish_pin_bar` (dominant lower wick = bullish rejection
        from below). SHORT side already used directionally-clean
        shooting_star + bearish_engulfing; no swap needed.
      F2 - docstring added.
      F3 - STRATEGY_REGIME_AFFINITY['pivot_s1_bounce'] {neutral, bear}
        entry DELETED -- B271 mass-edit single-direction-era family-
        bug. Now falls back to B291 direction-aware default.

    OPEN: external-AI audit also surfaced OBV-vs-location tension
    (fresh decline into support means OBV likely below 20-bar mean,
    so obv_bullish gate fights the support premise). Queued as
    S4-OBV-LOCATION-TENSION-DESIGN; not auto-fixed B641.
    """
    fl = (s.get("near_s1") and (s.get("hammer") or s.get("bullish_pin_bar")) and s.get("obv_bullish"))
    fs = (s.get("near_r1") and (s.get("shooting_star") or s.get("bearish_engulfing"))
          and s.get("obv_bearish"))
    return _strat3(fl, fs, "pivot",
        ["near_s1","hammer/bullish_pin_bar","obv_bullish"],
        ["near_r1","shooting_star/bearish_engulfing","obv_bearish"],
        ["Price at S1 pivot support","Hammer or bullish pin bar confirming buyers (B641 F1: direction-aware)","OBV rising - accumulation"],
        ["Price at R1 pivot resistance","Shooting star or bearish engulfing rejecting highs","OBV falling - distribution (B628 F1)"])


def strat_pivot_s2_bounce(s):
    fl = (s.get("near_s2") and s.get("rsi_14", 50) < 40 and (s.get("hammer") or s.get("bullish_engulfing")))
    fs = (s.get("near_r2") and s.get("rsi_14", 50) > 60 and s.get("bearish_engulfing"))
    return _strat3(fl, fs, "pivot",
        ["near_s2","rsi_14<40","bullish_candle"], ["near_r2","rsi_14>60","bearish_engulfing"],
        [f"Price at S2 deep support","RSI-14 oversold","Bullish candle confirms buyers"],
        [f"Price at R2 strong resistance","RSI-14 overbought","Bearish engulfing confirms sellers"])


def strat_pivot_s3_capitulation(s):
    """Floor-trader pivot S3 capitulation LONG with REVERSAL CONFIRMATION
    (Wyckoff Selling Climax + Spring/Test sequence).

    Batch 643 (2026-06-09 owner-directed W5 redesign option C per
    B640 external-AI audit + B641 fire-count measurement
    FAIL_FIRE_STARVED 14.7/yr universe-wide):

    PRE-B643 BEHAVIOR (knife-catch by construction):
      fires = near_s3 AND rsi<30 AND vol_spike_2x  -- fired SAME bar
      as capitulation conditions. Translates to "price crashed +
      oversold + panic volume = BUY". No element of the gate-set
      asked whether the decline had stopped. The B640 audit + B641
      measured fire rate confirmed both the structural danger AND
      the fire-starvation.

    POST-B643 BEHAVIOR (buy the turn, not the fall):
      DECOUPLED into two parts:
        (1) DETECTION: `recent_capitulation_at_s3` (new producer
            `compute_capitulation_lookback` in technical.py) = True
            when the pre-B643 conditions (near_s3 + rsi<30 +
            vol_spike_2x) were satisfied on ANY of the last 5 bars
            (inclusive of today). Emits a 5-day eligibility window
            after a capitulation event.
        (2) ENTRY CONFIRMATION: a reversal trigger fires today --
            `bullish_engulfing` (Nison two-bar reversal) OR `hammer`
            (Nison single-bar reversal with dominant lower wick) OR
            `above_prev_high` (key reversal bar -- today closed above
            yesterday's high, engulfs prior-day range).
      Strategy fires LONG only when BOTH (1) AND (2) are True.

    Wyckoff Selling Climax + Spring/Test sequence: the capitulation
    bar is the Selling Climax (SC); the 5-day window after captures
    the Automatic Rally (AR) and Spring/Test phase where price
    re-tests the SC low on weaker volume; reversal-confirmation
    bar inside the window signals the Test held -> bias to the
    Sign-of-Strength (SoS) rally. Buying the Test (with
    confirmation), not the SC (without), is the canonical
    Wyckoff play.

    Class 7 NEW mirror `strat_pivot_r3_blowoff_short` deferred
    pending W5 redesign fire-count + edge validation per
    measurement-pass workflow (S5-FIRE-COUNT-MEASURED-RUN).
    Symmetric design will mirror this two-gate structure post-
    validation.

    Regime affinity: B617 family-audit KEPT `{neutral, bear, crisis}`
    entry (no `_strat3` dual-direction conflict; LONG-only single-
    direction strategy). Capitulation-buy fits down/crisis regimes
    (no capitulation in bull).

    STATUS POST-B644: EXPLORATORY (per owner directive W5-i 2026-06-09).
    Measurement pass shipped same day produced 18.3/yr universe-wide
    fire rate -- BELOW min_trades=30 PASSING_CRITERIA threshold. Owner
    decision: ship the correctness fix; do NOT loosen gates pre-cube
    to chase the threshold. Stage 5 cube empirically validates whether
    18/yr fires produce alpha at sufficient statistical power.

    BATCH 650 (2026-06-09 owner-directed external-AI critique #3a fix):
    Added `vol_below_avg` AND-required on the reversal-trigger bar.
    Pre-B650 the reversal-trigger OR-disjunct (bullish_engulfing OR
    hammer OR above_prev_high) caught the timing window but missed the
    Bulkowski/Wyckoff Spring volume-condition: a successful Test of
    the SC low requires LOWER volume on the test bar (supply-absorption
    thesis). Without the volume gate, `above_prev_high` could fire on
    dead-cat bounces during sustained declines -- the redesign REDUCED
    knife-catch risk but didn't ELIMINATE it. Adding `vol_below_avg`
    (B594 producer: `today_volume / 20-bar_avg < 1.0`) as AND-required
    on the bar of fire closes the dead-cat-bounce hole. The strategy
    now properly distinguishes a Wyckoff Spring (low-volume Test) from
    a continuation bounce on heavy distribution volume.

    BATCH 651 (2026-06-09 owner-directed external-AI critique #3b fix):
    Regime affinity STRATEGY_REGIME_AFFINITY['pivot_s3_capitulation']
    expanded from {neutral, bear, crisis} to {bull, neutral, bear,
    crisis} (all regimes). The original 3-regime entry was correct for
    "buy the crash day" pre-B643. Post-B643 the strategy buys the turn
    UP TO 5 days later via the lookback window -- by which point the
    regime classifier (especially post-B642 R3 sticky-bear hysteresis)
    may still be reading bear/crisis even though the recovery is
    underway, OR may have already transitioned to neutral/bull. Either
    direction, blocking the LONG at the recovery moment is exactly
    the failure mode the redesign was supposed to fix. Permissive
    all-regimes entry preserves capitulation-LONG fires across the
    transition window. Safe because the strategy is so selective
    (~18-50/yr FAIL_FIRE_STARVED-to-borderline depending on scale)
    that allowing all regimes doesn't materially expand risk.

    OPEN (deferred): per S4-SURVIVORSHIP-T1A-VERIFY ticket, this
    strategy's expectancy is left-tail-dominated -- backtest validity
    depends on T1a PIT universe including delisted-during-window
    names (falling knives that didn't bounce). Per DEC-477 T1a is
    PIT-canonical with 111 historical-removed rows, but per-strategy
    adversarial verification has not been run for W5.
    """
    fires = (
        s.get("recent_capitulation_at_s3")
        and s.get("vol_below_avg")  # B650: Wyckoff Spring -- LOW-volume Test bar
        and (
            s.get("bullish_engulfing")
            or s.get("hammer")
            or s.get("above_prev_high")
        )
    )
    return _strat(fires, "long", "pivot",
        ["recent_capitulation_at_s3", "vol_below_avg", "reversal_trigger"],
        ["S3 capitulation event within last 5 bars (Wyckoff Selling Climax)",
         "LOW-volume Test bar (B650 vol_below_avg = supply-absorption per Bulkowski/Wyckoff Spring)",
         "Reversal-confirmation today: bullish_engulfing / hammer / key reversal bar above prev high",
         "Buys the TURN inside the window on Wyckoff Spring volume, not the FALL on capitulation day (B643 + B650 + B651)"])


def strat_pivot_r3_blowoff_short(s):
    """Floor-trader pivot R3 blowoff-top SHORT with REVERSAL CONFIRMATION
    (Wyckoff Buying Climax + Upthrust-Test sequence).

    Batch 645 (2026-06-09 Class 7 NEW wired per owner directive (a) from
    B643 follow-on bundle question): symmetric mirror of B643-redesigned
    strat_pivot_s3_capitulation. Two-gate structure decouples blowoff
    DETECTION (5-bar window) from ENTRY (reversal-trigger today).

    Per feedback_long_short_inverse_audit +
    feedback_wire_new_strategies_on_the_spot.

    Fires SHORT when ALL TWO:
      (1) DETECTION: `recent_blowoff_at_r3` (producer
          compute_blowoff_lookback in technical.py) = True when blowoff
          conditions (near_r3 + rsi>70 + vol_spike_2x) were satisfied
          on ANY of the last 5 bars (inclusive of today).
      (2) ENTRY CONFIRMATION: a bearish-reversal trigger fires today --
          `bearish_engulfing` (Nison two-bar reversal at top) OR
          `shooting_star` (Nison single-bar reversal with dominant
          upper wick) OR `below_prev_low` (key reversal bar -- today
          closed below yesterday's low; B616 producer-additive symmetric
          to above_prev_high).

    Wyckoff Buying Climax + Upthrust-Test: the blowoff bar is the
    Buying Climax (BC); the 5-day window captures Automatic Reaction
    (AR) and Upthrust-Test where price re-tests the BC high on weaker
    volume; bearish-reversal-confirmation bar inside the window
    signals the Test failed -> bias to the Sign-of-Weakness (SoW)
    decline. Shorting the failed Upthrust (with confirmation), not
    the BC (without), is the canonical Wyckoff distribution-phase
    play. Sells the TURN inside the window, not the SPIKE on
    blowoff day.

    STATUS POST-B652: EXPLORATORY -- STRONGER WARNING (per owner
    directive 2026-06-09 post-external-AI critique #5).

    PRE-DEPLOYMENT GATE: This strategy MUST NOT be deployed to live
    trading until BOTH of the following land:
      (1) M10 cost-aware cube -- slippage haircut + borrow cost lookup
          + gap-at-entry modelling (DEFERRED ticket; reviewer C6).
          The W5m fat right-tail (squeeze risk on overbought
          short-target names) is exactly the structural risk that
          the current flat-bps slippage model cannot evaluate.
      (2) S5-MULTIPLE-TESTING-CORRECTION (deflated Sharpe / Hansen
          SPA / Benjamini-Hochberg FDR; reviewer C2). With 222
          strategies on shared OHLCV features, the cube's PASS/FAIL
          adjudication is selection-bias-contaminated by
          construction. W5m's measured 7.3/yr universe-wide
          (B645 small-sample; expected ~17/yr post-B648 scaling fix)
          provides too few trades to overcome multiple-testing
          haircut at any honest correction.

    EXPECTANCY ASYMMETRY ACKNOWLEDGED per feedback_structural
    _symmetry_not_economic_symmetry: equity upward drift + squeeze
    risk on overbought shorts + borrow costs structurally bias
    against SHORT. Owner-approved wire per directive (a) WITH FULL
    UNDERSTANDING that the cube cannot yet evaluate the specific
    risks that make this strategy dangerous (per reviewer #5: "W5m
    is being parked in a cube that can't yet evaluate the specific
    risk that makes it dangerous").

    The strategy stays REGISTERED to preserve the dataflow + R5
    cube replay coverage; it must NOT be promoted to live trade
    routing until (1) + (2) above ship.

    Regime affinity: no explicit STRATEGY_REGIME_AFFINITY entry; B291
    direction-aware default applies -> SHORT fires in
    {bear, crisis, neutral}. (LONG counterpart strat_pivot_s3
    _capitulation has explicit {neutral, bear, crisis} entry; SHORT
    mirror gets identical-ish effective regime via B291 default plus
    `bear` substitution for `bull`.)

    Batch 659 (2026-06-09 owner-directed S4-W5M-SYMMETRIC-VOL-GATE
    resolution per Wyckoff Distribution Upthrust-Test symmetry with
    W5 LONG's B650 vol_below_avg gate):

    Pre-B659 the SHORT side reversal-trigger lacked the volume-
    condition that B650 added to W5 LONG. Wyckoff Buying Climax +
    Upthrust-Test sequence symmetrically requires LOWER volume on
    the failed-upthrust Test bar (supply-was-absorbed mirror of
    demand-was-absorbed Spring volume condition). Without the
    volume gate, `below_prev_low` during a sustained rally could
    fire on counter-rally pullbacks on heavy buy-volume -- the
    SHORT mirror of W5's pre-B650 dead-cat-bounce hole.

    Fix: `s.get("vol_below_avg")` AND-required on the bar of fire
    (B594 producer: today_volume / 20-bar_avg < 1.0). Strategy now
    properly distinguishes a Wyckoff Upthrust-Test (low-volume
    failed retest of BC high) from a continuation rally on heavy
    accumulation volume.

    OPEN (deferred): per S4-SURVIVORSHIP-T1A-VERIFY ticket, mirror
    of the W5 left-tail caveat -- SHORT side has its own structural
    risks (squeezes that aren't in the survivor universe; merger
    arbitrage that puts a floor on shorts of acquisition targets).
    """
    fires = (
        s.get("recent_blowoff_at_r3")
        and s.get("vol_below_avg")  # B659: Wyckoff Upthrust-Test -- LOW-volume failed-upthrust bar (mirrors B650 W5 Spring volume condition)
        and (
            s.get("bearish_engulfing")
            or s.get("shooting_star")
            or s.get("below_prev_low")
        )
    )
    return _strat(fires, "short", "pivot",
        ["recent_blowoff_at_r3", "vol_below_avg", "reversal_trigger"],
        ["R3 blowoff event within last 5 bars (Wyckoff Buying Climax)",
         "LOW-volume failed-upthrust bar (B659 vol_below_avg = supply-absorbed mirror of B650 W5 Spring volume; Wyckoff Distribution Upthrust-Test)",
         "Reversal-confirmation today: bearish_engulfing / shooting_star / key reversal bar below prev low",
         "Shorts the TURN inside the window on Wyckoff Upthrust-Test volume, not the SPIKE on blowoff day (B645 + B659)"])


def strat_pivot_r1_breakout(s):
    """Pivot R1 breakout. Batch 205 (Pivot optimization 2026-05-17 owner-
    approved research review): stacked with Anchored VWAP gate (Brian
    Shannon 2022) + DiNapoli volume confirmation. AVWAP-from-252-day-low
    is the institutional reference level; breakouts above R1 that ALSO
    hold above AVWAP are markedly higher quality than R1 breaks in
    isolation.

    Batch 659 (2026-06-09 owner-directed S4-W6-W7-W8-LONG-DEFAULT-TRUE
    -UNIFY resolution per 2nd-wave external-AI critique M5): LONG
    AVWAP gates swapped from default-True (silent-gap auto-pass-on-
    missing) to default-False (strict; symmetric with SHORT side
    which has used default-False since B633). Same fix pattern as
    B641 W8 F1+F1b + B657 T8 weekly Kumo. Strategy now properly
    fails-safe to no-fire when AVWAP signals are absent rather than
    auto-passing the gate.
    """
    # B659: symmetric default-False on BOTH directions (was asymmetric
    # default-True LONG + default-False SHORT per pre-B659 hardcoded asymmetry).
    avwap_long_ok = s.get("above_avwap_252low", False) and s.get("above_avwap_50low", False)
    # B633 sweep: positive symmetric below_avwap_252low/50low (B612 producers)
    avwap_short_ok = s.get("below_avwap_252low", False) and s.get("below_avwap_50low", False)
    fl = (
        s.get("above_r1") and s.get("vol_spike_15x")
        and s.get("macd_12_26_9_bullish") and avwap_long_ok
    )
    # B630 sweep: positive symmetric macd_12_26_9_bearish (B609 producer)
    fs = (
        s.get("below_s1") and s.get("vol_spike_15x")
        and s.get("macd_12_26_9_bearish") and avwap_short_ok
    )
    return _strat3(fl, fs, "pivot",
        ["above_r1", "vol_spike_1.5x", "macd_bullish",
         "above_avwap_252low", "above_avwap_50low"],
        ["below_s1", "vol_spike_1.5x", "macd_bearish",
         "below_avwap_252low", "below_avwap_50low"],
        ["Price broke above R1 resistance",
         "Volume 1.5x ADV(20) - institutional buying",
         "MACD positive",
         "Above Anchored VWAP (252d low + 50d low) - institutional reference"],
        ["Price broke below S1 support",
         "Volume 1.5x ADV(20) - institutional selling",
         "MACD negative",
         "Below Anchored VWAP (252d low + 50d low) - distribution"])


def strat_pivot_r2_continuation(s):
    """Pivot R2 trend-continuation. Batch 205: requires AVWAP + 2x volume
    (stronger threshold than R1 since R2 is the secondary breakout) +
    EMA 50/200 trend confirmation.

    Batch 659 (2026-06-09 owner-directed S4-W6-W7-W8-LONG-DEFAULT-TRUE
    -UNIFY): LONG AVWAP defaults swapped True -> False symmetric with
    SHORT side. Same fix as B641 W8 + B657 T8 + B659 W6 simultaneously.
    """
    # B659: symmetric default-False on BOTH directions
    avwap_long_ok = s.get("above_avwap_252low", False) and s.get("above_avwap_50low", False)
    # B633 sweep: positive symmetric below_avwap_252low/50low (B612 producers)
    avwap_short_ok = s.get("below_avwap_252low", False) and s.get("below_avwap_50low", False)
    # Stronger volume confirmation for R2 (2x ADV instead of 1.5x)
    fl = (
        s.get("above_r2") and s.get("adx_trending")
        and s.get("ema_50_200_bullish") and avwap_long_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    # B634 sweep: positive symmetric ema_50_200_bearish (B634 producer)
    fs = (
        s.get("below_s2") and s.get("adx_trending")
        and s.get("ema_50_200_bearish") and avwap_short_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    return _strat3(fl, fs, "pivot",
        ["above_r2", "adx_trending", "ema_50_200_bullish",
         "vol_spike_2x", "above_avwap_252low_and_50low"],
        ["below_s2", "adx_trending", "ema_50_200_bearish",
         "vol_spike_2x", "below_avwap_252low_and_50low"],
        ["Price above R2 - strong trend continuation",
         "ADX confirms trend", "Above 50/200 EMA",
         "Volume 2x ADV - heavy participation",
         "Above Anchored VWAP - institutional reference"],
        ["Price below R2 - strong downtrend continuation",
         "ADX confirms trend", "Below 50/200 EMA",
         "Volume 2x ADV - heavy participation",
         "Below Anchored VWAP - distribution"])


def strat_cpr_narrow_bullish(s):
    """Central Pivot Range narrow breakout. Batch 205: stacked with
    Anchored VWAP gate per Brian Shannon. Narrow CPR + above CPR + above
    AVWAP is the canonical institutional-grade directional day signal.

    Batch 358 (2026-05-25 owner-approved cell-audit Bucket B): added
    200-EMA regime gate per direction. Cell audit
    (cpr_narrow_bullish x atr_trail_1x) lost -1670pp at WR 17.7% in
    bull regime - the strategy fired LONG into anti-regime cells because
    no regime gate. Long now requires above_200_ema; short requires
    below_200_ema (canonical regime alignment).

    Batch 641 (2026-06-09 owner-directed Tier 1 ship via external-AI
    audit of B640 walk bundle):
      F1 - SHORT side AVWAP gate `not s.get("above_avwap_50low", False)`
        was a NOT-pattern silent-gap: missing key returns False, then
        `not False = True` AUTO-PASSED the gate. Replaced with positive
        symmetric `s.get("below_avwap_50low", False)` (B612 producer)
        which defaults False -> fail-safe to no-fire on missing key.
      F1b - SHORT side regime gate `(not above_200)` where above_200 was
        a local with default False: same auto-pass on missing key.
        Replaced with explicit `s.get("below_ema_200", False)` (B630
        producer-additive symmetric to price_above_ema_200).

    Batch 654 (2026-06-09 owner-directed W8 redundancy-audit option
    B-local per 2nd-wave external-AI critique #2 corrected methodology):

    PRE-B654 the strategy had 5 STATE-mostly gates per direction. B648
    random-30 measurement showed 34,000/yr universe-wide fires (~48
    per ticker per year, i.e. firing every ~5 trading days). Per-gate
    marginal-rate audit revealed:
      * cpr_narrow at 0.15-threshold = 87.3% True (NEAR-NO-OP filter)
      * rsi_14>50/<50 strict-inequality on default-50 = ~50% True (near
        no-op; already queued S4-W8-RSI-NOOP-GATE)
      * Effective strategy was ~"any uptrending day" (3 distinct gates:
        above_cpr + above_avwap_50low + price_above_ema_200) with two
        no-op gates providing false-precision camouflage.

    B654 FIX (option B-local per feedback_narrow_scope_blast_radius):
      - NEW producer `cpr_narrow_tight` in compute_pivots
        (`cpr_width < rng * 0.05`; B574-style local variant) -- W8
        ONLY switches to consume the tighter signal. The two other
        consumers `strat_cpr_narrow_momentum` and `strat_cpr_narrow
        _momentum_short` retain their existing 0.15 threshold pending
        their own walks.
      - Dropped rsi_14>50/<50 from both directions (closes
        S4-W8-RSI-NOOP-GATE; rsi midpoint is a no-op).
      - Post-B654 gate set: 3 distinct gates per direction.
        LONG:  cpr_narrow_tight + above_cpr + above_avwap_50low + price_above_ema_200
        SHORT: cpr_narrow_tight + below_cpr + below_avwap_50low + below_ema_200
      - Strategy is now properly "narrow CPR setup + above-pivot directional + uptrend regime" -- the docstring matches the implementation honestly.

    OPEN (unchanged): the LONG side `above_avwap_50low` still defaults
    True (S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY queued); fire-count
    measurement re-run pending (expected ~10-15k/yr post-B654 down
    from 34k/yr; threshold-tightening should remove the no-op
    contribution).
    """
    # B641 F1+F1b: positive symmetric gates on SHORT side (no NOT patterns)
    # B659 W8 portion of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY: LONG AVWAP
    # default swapped True -> False symmetric with SHORT side. Strategy
    # now properly fails-safe to no-fire when above_avwap_50low key is
    # absent rather than auto-passing the gate.
    avwap_long_ok = s.get("above_avwap_50low", False)   # B659: default-False symmetric with SHORT
    avwap_short_ok = s.get("below_avwap_50low", False)  # B641 F1: positive symmetric
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)           # B641 F1b: positive symmetric (B630 producer)
    # B654: switched cpr_narrow -> cpr_narrow_tight (0.05 threshold;
    # local variant only consumed by this strategy) + dropped no-op
    # rsi_14>50/<50 strict-inequality gates per S4-W8-RSI-NOOP-GATE.
    fl = (
        s.get("cpr_narrow_tight") and s.get("above_cpr")
        and avwap_long_ok
        and above_200
    )
    fs = (
        s.get("cpr_narrow_tight") and s.get("below_cpr")
        and avwap_short_ok
        and below_200
    )
    return _strat3(fl, fs, "pivot",
        ["cpr_narrow_tight", "above_cpr", "above_avwap_50low", "price_above_ema_200"],
        ["cpr_narrow_tight", "below_cpr", "below_avwap_50low", "below_ema_200"],
        ["Narrow CPR (0.05 tight; B654 redundancy-fix) - directional day likely",
         "Above CPR - bullish daily bias",
         "Above Anchored VWAP (50d low) - institutional reference",
         "Above 200 EMA - long-term uptrend regime"],
        ["Narrow CPR (0.05 tight; B654 redundancy-fix) - directional day likely",
         "Below CPR - bearish daily bias",
         "Below Anchored VWAP (50d low) - distribution (B641 F1 positive symmetric)",
         "Below 200 EMA - long-term downtrend regime (B641 F1b positive symmetric)"])


def strat_camarilla_s3_bounce(s):
    """Camarilla S3/R3 mean-reversion bounce with RSI extreme + OBV
    flow confirmation.

    Camarilla pivots (Slim Khan / Nick Scott) compute support/
    resistance levels at C +/- rng*1.1/{12, 6, 4, 2} from prev-day
    close+range; S3/R3 are the primary support/resistance pair.
    Strategy fires LONG when price approaches S3 (near_cam_s3) AND
    RSI is oversold AND OBV confirms accumulation. SHORT mirrors at
    R3 with overbought RSI + OBV distribution.

    Batch 628 (2026-06-08 owner-directed family-bug sweep per
    CHECKLIST #105 (n) on `not s.get("obv_bullish")` pattern -
    bundled 7-strategy sweep):

      F1 - silent-gap fix per `feedback_never_use_NOT_s_get_pattern`.
        SHORT side `not s.get("obv_bullish")` -> positive symmetric
        `s.get("obv_bearish", False)` (B617 producer: OBV < 20-bar MA).
      F2 - docstring added with Camarilla source attribution + B628
        walk record (pre-B628 the strategy had only context bullets).

    Post-B628 gate set (unchanged count; F1 hardens pattern only):
      LONG:  near_cam_s3 + rsi_14<35 + obv_bullish
      SHORT: near_cam_r3 + rsi_14>65 + obv_bearish  (B628 F1)

    DEFERRED to R5 per B624 manifest M1: STRATEGY_REGIME_AFFINITY
    entry `{bear, crisis, neutral}` is a B623 REMOVE_OK candidate
    (REMOVE gains +104.2pp PnL). Map removal pends R5 direction-
    aware confirmation.
    """
    # B628 F1: positive symmetric (B617 producer)
    fl = (s.get("near_cam_s3") and s.get("rsi_14", 50) < 35 and s.get("obv_bullish"))
    fs = (s.get("near_cam_r3") and s.get("rsi_14", 50) > 65 and s.get("obv_bearish"))
    return _strat3(fl, fs, "pivot",
        ["near_cam_s3","rsi_14<35","obv_bullish"],
        ["near_cam_r3","rsi_14>65","obv_bearish"],
        ["Price at Camarilla S3 - primary support (Slim Khan / Nick Scott)",
         "RSI oversold (<35)",
         "OBV confirming accumulation (above 20-bar MA)"],
        ["Price at Camarilla R3 - primary resistance",
         "RSI overbought (>65)",
         "OBV confirming distribution (B628 F1 positive symmetric)"])


def strat_camarilla_r4_breakout(s):
    """Camarilla R4 breakout / S4 breakdown with volume confirmation.

    Batch 641 (2026-06-09 owner-directed Tier 1 ship via external-AI
    audit of B640 walk bundle W10):
      F1 RENAME + RE-ANCHOR -- pre-B641 this strategy was
      `strat_camarilla_r3_breakout` firing on `above_cam_r3` /
      `below_cam_s3`. That is a SOURCE-SYSTEM CONTRADICTION: in
      Camarilla theory (Slim Khan / Nick Scott), R3/S3 are the
      reversal/fade levels (price reaching them is expected to
      mean-revert into yesterday's value area); R4/S4 are the
      breakout levels. Firing LONG above R3 directly contradicts
      the system this strategy is named after, and creates a
      same-level opposite-direction conflict with
      strat_camarilla_s3_bounce (W9): a single bar at R3 with a
      volume spike could fire W9 SHORT and W10 LONG simultaneously
      -- portfolio-level contradiction that nets to noise and
      double costs. B641 re-anchors to R4/S4 (the canonical
      breakout levels): producer signals `above_cam_r4` /
      `below_cam_s4` already emitted by compute_pivots
      (technical.py:134-135 -- BUG-09 RESOLVED-IMPLEMENTED Pass 53
      symmetric pair). Strategy function renamed from
      `strat_camarilla_r3_breakout` -> `strat_camarilla_r4
      _breakout`; registry key renamed `camarilla_r3_breakout` ->
      `camarilla_r4_breakout`; W9 (camarilla_s3_bounce) keeps R3/S3
      proximity (correct fade-level usage).
      F2 - docstring added with Camarilla source citation + B641
      rename record.

    Fires LONG when BOTH: (a) today's close > Camarilla R4 (the
    deepest standard resistance; canonical breakout threshold); (b)
    volume >= 2x 20-day average (institutional buying confirmation).
    SHORT mirror: close < Camarilla S4 + vol_spike_2x.

    Distinct from strat_camarilla_s3_bounce (W9) which trades
    MEAN-REVERSION AT R3/S3 (proximity + RSI extreme + OBV flow);
    this strategy trades BREAKOUT BEYOND R4/S4 with volume. The
    two strategies now operate at non-overlapping price levels
    consistent with Camarilla's design: R3=fade, R4=breakout.

    Fire-count projection (independent-product UB): WIDE 2-gate
    strategy. Per external-AI critique, the independent-product
    estimate over-counts when gates are correlated -- measured
    fire rate pending fire-count measurement pass (S5-FIRE-COUNT
    -MEASURED-RUN, B641 follow-on).

    Camarilla source: Slim Khan / Nick Scott. Levels computed at
    C +/- Range*1.1/{12, 6, 4, 2} from yesterday's H/L/C; R4/S4
    are the outermost levels (Range*1.1/2 from C).
    """
    fl = (s.get("above_cam_r4") and s.get("vol_spike_2x"))
    fs = (s.get("below_cam_s4") and s.get("vol_spike_2x"))
    return _strat3(fl, fs, "pivot",
        ["above_cam_r4","vol_spike_2x"], ["below_cam_s4","vol_spike_2x"],
        ["Price broke above Camarilla R4  -  breakout level (Slim Khan / Nick Scott; B641 re-anchored from R3 misuse)","Volume 2x confirms institutional buying"],
        ["Price broke below Camarilla S4  -  breakdown level","Volume 2x confirms institutional selling"])


def strat_prev_day_high_break(s):
    fl = (s.get("above_prev_high") and s.get("vol_spike_15x") and s.get("above_vwap"))
    # B634 sweep: positive symmetric below_vwap (B634 producer)
    fs = (s.get("below_prev_low") and s.get("vol_spike_15x") and s.get("below_vwap"))
    return _strat3(fl, fs, "pivot",
        ["above_prev_high","vol_spike_1.5x","above_vwap"], ["below_prev_low","vol_spike_1.5x","below_vwap"],
        ["Price broke above previous day's high","Volume confirms participation","Above VWAP  -  buyers in control"],
        ["Price broke below previous day's low","Volume confirms participation","Below VWAP  -  sellers in control"])


def strat_prev_day_low_bounce(s):
    # B629 F1 cmf-family sweep: positive symmetric cmf_negative (B629 producer)
    fl = (s.get("near_prev_low") and s.get("hammer") and s.get("cmf_positive"))
    fs = (s.get("near_prev_high") and s.get("shooting_star") and s.get("cmf_negative"))
    return _strat3(fl, fs, "pivot",
        ["near_prev_low","hammer","cmf_positive"],
        ["near_prev_high","shooting_star","cmf_negative"],
        ["Price holding at previous day's low","Hammer - buyers defended the level","CMF positive"],
        ["Price stalling at previous day's high","Shooting star - sellers rejected the level","CMF negative (B629 F1)"])


# -----------------------------------------------------------------------------
# CATEGORY 2: MOMENTUM (9 strategies)
# -----------------------------------------------------------------------------

def strat_macd_crossover(s):
    fl = s.get("macd_12_26_9_crossover_up")
    fs = s.get("macd_12_26_9_crossover_dn")
    return _strat3(fl, fs, "momentum",
        ["macd_12_26_9_crossover_up"], ["macd_12_26_9_crossover_dn"],
        ["MACD 12/26/9 crossed above zero  -  momentum turning positive"],
        ["MACD 12/26/9 crossed below zero  -  momentum turning negative"])


def strat_macd_fast_crossover(s):
    fl = s.get("macd_8_21_5_crossover_up")
    fs = s.get("macd_8_21_5_crossover_dn")
    return _strat3(fl, fs, "momentum",
        ["macd_8_21_5_crossover_up"], ["macd_8_21_5_crossover_dn"],
        ["Fast MACD 8/21/5 crossed above zero  -  early momentum shift bullish"],
        ["Fast MACD 8/21/5 crossed below zero  -  early momentum shift bearish"])


def strat_hull_rsi(s):
    """Hull MA + RSI(9) momentum. Batch 207 (2026-05-17 owner-approved
    research review): added ADX(14) > 20 trend confirmation gate. Hull
    alone whipsaws in choppy markets; Hull + ADX>20 cuts false-signal
    rate in half per multiple SSRN replications (cited in research
    report B.4). The 26 trades in Phase 1A-beta yielded Sharpe -0.26 and
    win rate 30.8% - classic whipsaw failure mode without trend filter.

    Batch 358 (2026-05-25 owner-approved cell-audit Bucket B): added
    bear-regime block on long leg via price_above_ema_200. Cell audit
    showed (hull_rsi x atr_trail_1x) lost -1371pp at WR 25% in bear
    regime - long-only mean-reversion catching falling knives. Symmetric
    short leg gets the inverse gate (not price_above_ema_200) so it
    only fires below 200-EMA. See PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md.

    Batch 656 (2026-06-09 owner-directed T3 redundancy-audit option
    A+C per 2nd-wave external-AI critique #2 corrected methodology):

    AUDIT FINDING: unlike W8 (cpr_narrow 87% True NO-OP) and T10
    (supertrend_bullish 99% True NO-OP), T3 hull_rsi has NO extreme
    no-op gate -- all 5 gates are 38-53% True. The 28-fires/ticker/year
    rate is honest CONFLUENCE (gates positively correlate AT the
    strategy's intended setup: hull_bullish + price_above_hull
    correlate +0.41 because both measure Hull-MA uptrend semantics
    from different angles -- slope vs current position -- but they
    screen distinct failure modes; not redundant).

    Per critique #2 corrected methodology: T3 is honest STATE
    composite, not redundancy-with-no-op-camouflage. Status quo
    structure preserved (option A).

    The ONE no-op-class concern: `rsi_9>50/<50` strict-inequality on
    default-50 is the same accidentally-safe pattern that B654
    closed for W8 RSI -- midpoint strict-inequality removes ~half
    the sample but adds almost no information beyond what
    hull_bullish + price_above_hull already encode. Per option C:
    DROP both rsi_9 gates.

    Post-B656 gate set (4 distinct gates per direction):
      LONG:  hull_bullish + price_above_hull + adx>20 + price_above_ema_200
      SHORT: hull_bearish + price_below_hull + adx>20 + below-200-EMA*
    (*) SHORT side still uses `(not above_200)` NOT-pattern silent-
        gap -- separate concern queued as
        `S4-T3-NOT-ABOVE-200-EMA-PATTERN` (B656 surface for owner
        decision). NOT auto-fixed here per CHECKLIST (g) sequence-
        or-split.
    """
    adx_trend_ok = s.get("adx", 0) > 20 or s.get("adx_trending", False)
    above_200 = s.get("price_above_ema_200", False)
    # B659 S4-T3-NOT-ABOVE-200-EMA-PATTERN resolution: replace
    # `(not above_200)` NOT-pattern silent-gap with positive symmetric
    # `s.get("below_ema_200", False)` (B630 producer-additive). Same
    # fix template as B641 W8 F1b (cpr_narrow_bullish SHORT-side
    # `(not above_200)` -> `below_ema_200` positive symmetric).
    below_200 = s.get("below_ema_200", False)
    # B656: dropped rsi_9>50/<50 (option C from T3 redundancy audit;
    # same accidentally-safe + near-no-op pattern as B654 W8 RSI drop).
    fl = (
        s.get("hull_bullish") and s.get("price_above_hull")
        and adx_trend_ok
        and above_200
    )
    # B634 sweep: positive symmetric hull_bearish + price_below_hull (B634 producers)
    fs = (
        s.get("hull_bearish") and s.get("price_below_hull")
        and adx_trend_ok
        and below_200  # B659: was `(not above_200)` NOT-pattern silent-gap
    )
    return _strat3(fl, fs, "momentum",
        ["hull_bullish", "price_above_hull", "adx>20", "price_above_ema_200"],
        ["hull_bearish", "price_below_hull", "adx>20", "price_below_ema_200"],
        ["Hull MA rising - fast trend bullish", "Price above Hull",
         "ADX>20 confirms trend",
         "Above 200-EMA (bull regime gate, Batch 358)"],
        ["Hull MA falling - fast trend bearish", "Price below Hull",
         "ADX>20 confirms trend",
         "Below 200-EMA (bear regime gate, Batch 358)"])


def strat_williams_r_oversold(s):
    """Williams %R oversold-bounce. Batch 206 (Connors stack 2026-05-17):
    primary entry is Williams %R OR Connors RSI(2) extreme; both confirm
    short-window oversold. 200-EMA regime gate preserved (current best-
    performing strategy in Phase 1A-beta with Sharpe 0.30; intent is to
    tighten further without losing fill rate).

    BUG-11 RESOLVED-IMPLEMENTED Pass 53 v8h+1: short branch uses explicit
    default to prevent firing when key absent.
    """
    rsi_2 = s.get("rsi_2", 50)
    # B663 family-bug sweep: positive symmetric below_ema_200 (B630 producer) replaces (not above_200) NOT-pattern silent-gap per feedback_never_use_NOT_s_get_pattern
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    fl = (
        (s.get("williams_r_oversold") or (rsi_2 < 5))
        and above_200
        and s.get("cmf_positive")
    )
    # B629 F1 cmf-family sweep: positive symmetric cmf_negative
    fs = (
        (s.get("williams_r", 0) > -20 or (rsi_2 > 95))
        and below_200
        and s.get("cmf_negative")
    )
    return _strat3(fl, fs, "momentum",
        ["williams_r_oversold_or_rsi_2<5", "above_ema_200", "cmf_positive"],
        ["williams_r_overbought_or_rsi_2>95", "below_ema_200", "cmf_negative"],
        ["Williams %R oversold OR Connors RSI(2)<5 (short-window extreme)",
         "Above 200 EMA (regime gate)", "CMF positive"],
        ["Williams %R overbought OR RSI(2)>95",
         "Below 200 EMA (bear regime)", "CMF negative"])


def strat_roc_burst(s):
    fl = (s.get("roc_turning_up") and s.get("vol_spike_15x"))
    fs = (s.get("roc_turning_dn") and s.get("vol_spike_15x"))
    return _strat3(fl, fs, "momentum",
        ["roc_turning_up","vol_spike_1.5x"], ["roc_turning_dn","vol_spike_1.5x"],
        ["ROC-12 flipped positive  -  early momentum shift up","Volume confirms"],
        ["ROC-12 flipped negative  -  early momentum shift down","Volume confirms"])


def strat_awesome_oscillator(s):
    """Bill Williams Awesome Oscillator (AO) zero-line cross with
    EMA-20 trend filter.

    AO = SMA(5, midprice) - SMA(34, midprice); zero-line cross flips
    momentum bias. EMA-20 confirms direction alignment with the
    underlying trend.

    Batch 627 (2026-06-08 owner-directed family-bug sweep per
    CHECKLIST #105 (n) - B626 force_index walk surfaced 3 instances
    of `not s.get("price_above_ema_20")` pattern; bundled sweep of
    the 2 remaining):

      F1 - silent-gap fix per `feedback_never_use_NOT_s_get_pattern`.
        SHORT side `not s.get("price_above_ema_20")` -> `s.get(
        "below_ema_20", False)` (B609 positive symmetric producer).
        Pre-B627: missing EMA-20 key auto-fired SHORT (None falsy ->
        not None = True). Post-B627: missing key blocks SHORT.

    Post-B627 gate set (unchanged count; F1 hardens pattern only):
      LONG:  ao_cross_up + price_above_ema_20
      SHORT: ao_cross_dn + below_ema_20  (B627 F1 positive symmetric)
    """
    fl = (s.get("ao_cross_up") and s.get("price_above_ema_20"))
    # B627 F1: positive symmetric (B609 producer)
    fs = (s.get("ao_cross_dn") and s.get("below_ema_20"))
    return _strat3(fl, fs, "momentum",
        ["ao_cross_up","price_above_ema_20"],
        ["ao_cross_dn","below_ema_20"],
        ["Awesome Oscillator crossed above zero - momentum positive",
         "Above EMA-20 (trend filter)"],
        ["Awesome Oscillator crossed below zero - momentum negative",
         "Below EMA-20 (trend filter; B627 F1 positive symmetric)"])


def strat_stochrsi_oversold(s):
    """StochRSI oversold-bounce. Batch 206 (Connors stack 2026-05-17):
    add 200-EMA regime gate (Connors discipline). StochRSI cross-up is
    a momentum-turn signal; without the regime gate it fires aggressively
    in downtrends (Phase 1A-beta showed -1.01 expected_value at 132
    trades, indicating the strategy fires inside bear/downtrend bias)."""
    rsi_2 = s.get("rsi_2", 50)
    # B663 family-bug sweep: was default-True silent-gap; positive symmetric below_ema_200 (B630 producer) per feedback_never_use_NOT_s_get_pattern
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    fl = (
        s.get("stochrsi_oversold") and s.get("stochrsi_cross_up")
        and s.get("rsi_14", 50) < 55 and above_200
    )
    fs = (
        s.get("stochrsi_overbought") and s.get("stochrsi_cross_dn")
        and s.get("rsi_14", 50) > 45 and below_200
    )
    return _strat3(fl, fs, "momentum",
        ["stochrsi_oversold", "stochrsi_cross_up", "rsi_14<55", "above_ema_200"],
        ["stochrsi_overbought", "stochrsi_cross_dn", "rsi_14>45", "below_ema_200"],
        ["StochRSI oversold - below 20", "K crossed above D - momentum turning up",
         "RSI not overbought", "Above 200 EMA (regime gate)"],
        ["StochRSI overbought - above 80", "K crossed below D - momentum turning down",
         "RSI not oversold", "Below 200 EMA (bear regime)"])


def strat_ppo_crossover(s):
    fl = (s.get("ppo_crossover_up") and s.get("adx_trending"))
    fs = (s.get("ppo_crossover_dn") and s.get("adx_trending"))
    return _strat3(fl, fs, "momentum",
        ["ppo_crossover_up","adx_trending"], ["ppo_crossover_dn","adx_trending"],
        ["PPO crossed above signal  -  momentum bullish","ADX confirms trend"],
        ["PPO crossed below signal  -  momentum bearish","ADX confirms trend"])


def strat_ultimate_oscillator(s):
    """Ultimate Oscillator oversold-bounce (Larry Williams 1976).

    Williams UO = 100 * (4*avg7 + 2*avg14 + avg28) / 7 of buying-
    pressure ratios across 7/14/28-day windows. Oversold below 30 +
    overbought above 70 are the canonical extremes; mean-reversion
    bounce playbook with 200-SMA regime gate.

    Batch 206 (Connors stack 2026-05-17): primary signal upgraded to
    (uo_oversold OR rsi_2<5). Phase 1A-beta showed UO is the best
    Sharpe (0.49) carrier in the oversold family but only 27 trades;
    stacking with Connors RSI(2) increases fill rate without
    sacrificing regime discipline.

    Batch 631 (2026-06-08 owner-directed Stage 4 walk per CHECKLIST
    #105 + B623 REMOVE_OK candidate review; option C: F1+F2+(a)):

      F1 - silent-gap fix per `feedback_never_use_NOT_s_get_pattern`.
        SHORT side `not s.get("price_above_sma_200")` -> positive
        symmetric `s.get("below_sma_200", False)` (B630 producer).
        Was the LAST instance of this pattern (Tier 3 sub-threshold
        per B629 grep; eliminating it closes the price_above_sma_200
        silent-gap signal entirely - 0 active instances post-B631).
      F2 - polish: SHORT now uses producer signal `uo_overbought`
        (= uo > 70, already emitted by compute_ultimate_oscillator)
        instead of raw `s.get("uo", 50) > 70` threshold check.
        Symmetric with LONG's use of `uo_oversold`; semantically
        identical, code clarity improvement.
      (a) - B589-family bullish/bearish bar gate: close_above_open
        (LONG) / close_below_open (SHORT).

    Post-B631 gate set (LONG/SHORT, 3 gates per direction):
      LONG:  (uo_oversold OR rsi_2<5) + price_above_sma_200
             + close_above_open
      SHORT: (uo_overbought OR rsi_2>95) + below_sma_200
             + close_below_open

    DEFERRED to R5 per B624 manifest M1: STRATEGY_REGIME_AFFINITY
    entry `{bull}` is a B623 REMOVE_OK candidate (REMOVE gains
    +31.1pp PnL). Map removal pends R5 direction-aware confirmation.
    """
    rsi_2 = s.get("rsi_2", 50)
    fl = (
        (s.get("uo_oversold") or (rsi_2 < 5))
        and s.get("price_above_sma_200")
        and s.get("close_above_open")          # B631 (a)
    )
    # B631 F1 + F2 + (a): positive symmetric + uo_overbought + bear bar.
    fs = (
        (s.get("uo_overbought") or (rsi_2 > 95))
        and s.get("below_sma_200")
        and s.get("close_below_open")
    )
    return _strat3(fl, fs, "momentum",
        ["uo_oversold_or_rsi_2<5", "price_above_sma_200", "close_above_open"],
        ["uo_overbought_or_rsi_2>95", "below_sma_200", "close_below_open"],
        ["Ultimate Oscillator below 30 OR Connors RSI(2)<5",
         "Above 200 SMA (regime gate)",
         "Bullish bar - close above open (B631 a B589-family)"],
        ["Ultimate Oscillator above 70 OR RSI(2)>95",
         "Below 200 SMA (bear regime; B631 F1 positive symmetric)",
         "Bearish bar - close below open (B631 a B589-family)"])


# -----------------------------------------------------------------------------
# CATEGORY 3: TREND FOLLOWING (9 strategies)
# -----------------------------------------------------------------------------

def strat_golden_cross_50_200(s):
    fl = s.get("ema_50_200_golden_cross")
    fs = s.get("ema_50_200_death_cross")
    return _strat3(fl, fs, "trend",
        ["ema_50_200_golden_cross"], ["ema_50_200_death_cross"],
        ["EMA-50 crossed above EMA-200  -  golden cross  -  structural shift bullish"],
        ["EMA-50 crossed below EMA-200  -  death cross  -  structural shift bearish"])


def strat_golden_cross_9_21(s):
    fl = (s.get("ema_9_21_golden_cross") and s.get("price_above_sma_50"))
    # B630 sweep: positive symmetric below_sma_50 (B630 producer)
    fs = (s.get("ema_9_21_death_cross") and s.get("below_sma_50"))
    return _strat3(fl, fs, "trend",
        ["ema_9_21_golden_cross","price_above_sma_50"], ["ema_9_21_death_cross","price_below_sma_50"],
        ["EMA-9 crossed above EMA-21  -  early trend bullish","Above 50 SMA confirms"],
        ["EMA-9 crossed below EMA-21  -  early trend bearish","Below 50 SMA confirms"])


def strat_golden_cross_20_50(s):
    fl = (s.get("ema_20_50_golden_cross") and s.get("price_above_ema_200"))
    # B630 sweep: positive symmetric below_ema_200 (silent-gap fix; no default=True)
    fs = (s.get("ema_20_50_death_cross") and s.get("below_ema_200"))
    return _strat3(fl, fs, "trend",
        ["ema_20_50_golden_cross","price_above_ema_200"], ["ema_20_50_death_cross","price_below_ema_200"],
        ["EMA-20 crossed above EMA-50  -  medium-term trend bullish","Above 200 EMA confirms"],
        ["EMA-20 crossed below EMA-50  -  medium-term trend bearish","Below 200 EMA confirms"])


def strat_parabolic_sar_flip(s):
    fl = (s.get("psar_flip_up") and s.get("adx_trending"))
    fs = (s.get("psar_flip_dn") and s.get("adx_trending"))
    return _strat3(fl, fs, "trend",
        ["psar_flip_up","adx_trending"], ["psar_flip_dn","adx_trending"],
        ["Parabolic SAR flipped below price  -  trend reversal up","ADX confirms trend strength"],
        ["Parabolic SAR flipped above price  -  trend reversal down","ADX confirms trend strength"])


def strat_tema_dema(s):
    # B634 sweep: positive symmetric price_below_tema (B634 producer)
    fl = (s.get("tema_cross_up") and s.get("price_above_tema"))
    fs = (s.get("tema_cross_dn") and s.get("price_below_tema"))
    return _strat3(fl, fs, "trend",
        ["tema_cross_up","price_above_tema"], ["tema_cross_dn","price_below_tema"],
        ["TEMA crossed above DEMA  -  fast MA system bullish","Price above TEMA"],
        ["TEMA crossed below DEMA  -  fast MA system bearish","Price below TEMA"])


def strat_ichimoku_tk_cross(s):
    # B634 sweep: positive symmetric ichi_above_cloud (existing producer).
    # Semantic note: pre-B634 `not s.get("ichi_below_cloud")` = "above OR
    # in cloud"; post-B634 strict `ichi_above_cloud` = "strictly above
    # cloud" (in-cloud no longer fires). Minor tightening matches the
    # strategy's "TK cross + trend confirmation" intent - in-cloud is
    # ambiguous/neutral, not confirming.
    fl = (s.get("ichi_tk_cross_up") and s.get("ichi_above_cloud"))
    fs = (s.get("ichi_tk_cross_dn") and s.get("ichi_below_cloud"))
    return _strat3(fl, fs, "trend",
        ["ichi_tk_cross_up","not_below_cloud"], ["ichi_tk_cross_dn","ichi_below_cloud"],
        ["Ichimoku Tenkan crossed above Kijun  -  TK cross bullish","Not below cloud"],
        ["Ichimoku Tenkan crossed below Kijun  -  TK cross bearish","Below cloud confirms downtrend"])


def strat_ichimoku_cloud_breakout(s):
    """Ichimoku cloud breakout. Batch 207 (2026-05-17 owner-approved
    research review): multi-timeframe Kumo gate per Linda Bradford
    Raschke - weekly Ichimoku cloud position must align with daily
    breakout direction. Phase 1A-beta showed 43 trades / 18.6% WR /
    Sharpe -1.00 - the second-worst strategy by Sharpe in the carrier
    set, indicating the daily-only Kumo is too permissive.

    Batch 657 (2026-06-09 owner-directed T8 redundancy-audit option E
    per 2nd-wave external-AI critique #2 corrected methodology):

    AUDIT FINDING (different from W8/T10 but same default-True
    concern as W6/W7/W8 pivot cluster): T8 has NO extreme NO-OP gate
    (all 4 marginals 38-51% True). The gate set is HONEST CONFLUENCE
    -- Ichimoku measured from multiple angles (daily cloud / short-
    term TK / multi-TF weekly cloud / trend-strength) where each
    component screens a distinct failure mode. Per option A: status
    quo on the 4-gate confluence structure.

    BUT the weekly Kumo gate had a DEFAULT-TRUE silent-gap (same
    auto-pass-on-missing class as W6/W7/W8 LONG AVWAP defaults
    queued in S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY). Pre-B657:
        weekly_long_ok = s.get("ichi_weekly_above_cloud", True)
        weekly_short_ok = s.get("ichi_weekly_below_cloud", True)
    When weekly Kumo signals were missing (early backtest history
    with <260 daily bars insufficient for weekly resample), BOTH
    directions auto-passed the gate -- backward-compat for early
    history but a silent-gap that defeats the "multi-TF confirm"
    thesis when it matters.

    Per option D from the audit: fixed by swapping default True ->
    False on BOTH directions. Strict semantics: require weekly Kumo
    data emitted; lose fires in early backtest when data absent.

    Net B657 changes:
      A = status quo on confluence structure (4 distinct gates)
      D = default-True -> default-False on both weekly Kumo gates
          (closes T8 portion of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY;
          W6/W7/W8 portions remain pending separate decisions)
    """
    # B657 D: strict default-False on multi-TF weekly Kumo gates (was
    # default-True silent-gap pre-B657).
    weekly_long_ok = s.get("ichi_weekly_above_cloud", False)
    weekly_short_ok = s.get("ichi_weekly_below_cloud", False)
    fl = (
        s.get("ichi_above_cloud") and s.get("ichi_tk_bullish")
        and s.get("adx_trending") and weekly_long_ok
    )
    fs = (
        s.get("ichi_below_cloud") and s.get("ichi_tk_bearish")
        and s.get("adx_trending") and weekly_short_ok
    )
    return _strat3(fl, fs, "trend",
        ["ichi_above_cloud", "ichi_tk_bullish", "adx_trending",
         "ichi_weekly_above_cloud"],
        ["ichi_below_cloud", "ichi_tk_bearish", "adx_trending",
         "ichi_weekly_below_cloud"],
        ["Price above Ichimoku Cloud (daily) - full bullish structure",
         "Tenkan above Kijun", "ADX confirms",
         "Weekly Kumo also above cloud (multi-TF regime confirm)"],
        ["Price below Ichimoku Cloud (daily) - full bearish structure",
         "Tenkan below Kijun", "ADX confirms",
         "Weekly Kumo also below cloud (multi-TF regime confirm)"])


def strat_adx_initiation(s):
    # B634 sweep: positive symmetric adx_di_bear (B634 producer)
    fl = (s.get("adx_cross_up") and s.get("adx_di_bull"))
    fs = (s.get("adx_cross_up") and s.get("adx_di_bear"))
    return _strat3(fl, fs, "trend",
        ["adx_cross_up","adx_di_bull"], ["adx_cross_up","adx_di_bear"],
        ["ADX crossed above 25  -  trend initiating","DI+ above DI-  -  bullish direction"],
        ["ADX crossed above 25  -  trend initiating","DI- above DI+  -  bearish direction"])


def strat_supertrend_macd(s):
    """Supertrend trend-confirmation + MACD momentum + ADX trend-strength,
    with B655 redesign to EVENT-anchored signal (Olivier Seban Supertrend
    + Appel MACD + Wilder ADX).

    Batch 655 (2026-06-09 owner-directed T10 redundancy-audit option B
    per 2nd-wave external-AI critique #2 + feedback_no_rushing_per
    _strategy_tweak):

    PRE-B655 BEHAVIOR: 3 STATE gates per direction (supertrend_bullish
    + macd_12_26_9_bullish + adx > 20). B648 random-30 measurement
    showed 32,913/yr universe-wide fires (~98 per ticker per year =
    fires every 2.5 trading days). Per-gate marginal-rate audit:
      * supertrend_bullish = 99.19% True (EXTREME NO-OP -- Supertrend
        is a trailing trend indicator; once bullish, stays bullish
        until a large pullback flips it; on the random-30 sample
        covering 2022 bear + 2023-24 bull, the LONG-side filter was
        nearly always-on).
      * macd_12_26_9_bullish = 50.3% True (coin-flip STATE)
      * adx > 20 = STATE trend-strength filter
    Per CHECKLIST (s): 3 STATE gates, ZERO EVENT, so the strategy had
    no bar-of-fire timing alpha -- effectively "MACD + ADX wearing
    supertrend as 99%-True camouflage."

    POST-B655 BEHAVIOR (B643/B645/B650 template applied): EVENT-anchored
    via B655 producer-additive `supertrend_flip_recent_long_5d` /
    `_short_5d` (B643-style 5-bar lookback window from the
    supertrend_flip_up / _dn EVENT). Strategy fires LONG when ALL
    THREE:
      (1) supertrend_flip_recent_long_5d -- supertrend flipped bullish
          on any of the last 5 bars (the EVENT-anchored window)
      (2) macd_12_26_9_bullish -- MACD has confirmed momentum positive
          within the window
      (3) adx > 20 -- trend-strength filter unchanged
    SHORT mirrors with flip_recent_short + macd_bearish + adx > 20.

    Thesis: the supertrend flip is the bar-of-fire EVENT (genuine
    timing alpha); the 5-bar window allows MACD/ADX confirmation to
    materialize after the flip rather than requiring same-bar
    confluence (which was too restrictive). Same lookback semantics
    as B643 W5 capitulation + B645 W5m blowoff.

    Other consumers of supertrend signals UNCHANGED per
    feedback_narrow_scope_blast_radius (B574 precedent). New
    `supertrend_flip_recent_*_5d` is producer-additive in
    `compute_supertrend`.

    Regime affinity: STRATEGY_REGIME_AFFINITY[supertrend_macd] entry
    `{bull}` DEFERRED-R5 per existing S5-REGIME-AFFINITY-21-DEFERRED.
    No B655 change (queue-blocked).
    """
    # B655: EVENT-anchored 5-bar lookback replaces all-STATE composite
    fl = (s.get("supertrend_flip_recent_long_5d")
          and s.get("macd_12_26_9_bullish")
          and s.get("adx", 0) > 20)
    fs = (s.get("supertrend_flip_recent_short_5d")
          and s.get("macd_12_26_9_bearish")
          and s.get("adx", 0) > 20)
    return _strat3(fl, fs, "trend",
        ["supertrend_flip_recent_long_5d","macd_bullish","adx>20"],
        ["supertrend_flip_recent_short_5d","macd_bearish","adx>20"],
        ["Supertrend flip-up within last 5 bars (B655 EVENT-anchored; pre-B655 used always-on supertrend_bullish)",
         "MACD positive  -  momentum confirms within window",
         "ADX > 20  -  trend strength confirmed"],
        ["Supertrend flip-down within last 5 bars",
         "MACD negative  -  momentum confirms within window",
         "ADX > 20  -  trend strength confirmed"])


# -----------------------------------------------------------------------------
# CATEGORY 4: MEAN REVERSION (11 strategies  -  including 2 shorts)
# -----------------------------------------------------------------------------

def strat_rsi_oversold(s):
    """RSI oversold dip-buy. Batch 206 (Connors stack 2026-05-17): upgrade
    primary signal to (rsi_2<5 OR rsi_14<35). Connors discipline: short-
    window RSI(2) extreme is the canonical mean-reversion trigger, with
    long-window RSI(14) as the slower-moving fallback. Adds 200-EMA
    regime gate (Connors filter) in addition to 50-SMA pullback context.
    Strategy had 0 trades in Phase 1A-beta with rsi_14<35 alone (rarely
    triggers); the rsi_2<5 path opens the strategy to fire on intraday
    extremes."""
    rsi_2 = s.get("rsi_2", 50)
    rsi_14 = s.get("rsi_14", 50)
    # B663 family-bug sweep: was default-True silent-gap; positive symmetric below_ema_200 (B630 producer)
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    fl = (
        (rsi_2 < 5 or rsi_14 < 35)
        and s.get("price_above_sma_50")
        and above_200
    )
    # B630 sweep: positive symmetric below_sma_50 (B630 producer)
    fs = (
        (rsi_2 > 95 or rsi_14 > 65)
        and s.get("below_sma_50")
        and below_200
    )
    return _strat3(fl, fs, "mean_reversion",
        ["rsi_2<5_or_rsi_14<35", "price_above_sma_50", "price_above_ema_200"],
        ["rsi_2>95_or_rsi_14>65", "price_below_sma_50", "price_below_ema_200"],
        ["Connors RSI(2)<5 OR RSI(14)<35", "Above 50 SMA - buying dip",
         "Above 200 EMA (regime gate)"],
        ["RSI(2)>95 OR RSI(14)>65", "Below 50 SMA - selling rally",
         "Below 200 EMA (bear regime)"])


def strat_rsi9_extreme(s):
    # No natural short inverse  -  stays long-only (extreme oversold in uptrend)
    fires = (s.get("rsi_9_extreme_os") and s.get("price_above_ema_200") and s.get("rsi_9_rising"))
    return _strat(fires, "long", "mean_reversion",
        ["rsi_9<20","price_above_ema_200","rsi_9_rising"],
        [f"RSI-9 extreme oversold below 20","Above 200 EMA  -  uptrend context","RSI-9 rising  -  recovering"])


def strat_rsi21_slow(s):
    # B630 sweep: positive symmetric below_sma_50 (B630 producer)
    fl = (s.get("rsi_21", 50) < 35 and s.get("price_above_sma_50"))
    fs = (s.get("rsi_21", 50) > 65 and s.get("below_sma_50"))
    return _strat3(fl, fs, "mean_reversion",
        ["rsi_21<35","price_above_sma_50"], ["rsi_21>65","price_below_sma_50"],
        [f"Slow RSI-21 oversold below 35","Above 50 SMA  -  uptrend context"],
        [f"Slow RSI-21 overbought above 65","Below 50 SMA  -  downtrend context"])


def strat_rsi_overbought_short(s):
    # B630 sweep: positive symmetric below_sma_50 (B630 producer)
    fires = (s.get("rsi_14", 50) > 68 and
             s.get("below_sma_50") and
             (s.get("bearish_engulfing") or s.get("rsi_14_rising") == False))
    return _strat(fires, "short", "mean_reversion",
        ["rsi_14>68","below_sma_50","bearish_signal"],
        [f"RSI-14 overbought at {s.get('rsi_14',0):.1f}  -  above 68",
         "Below 50 SMA  -  selling rally in downtrend",
         "Bearish momentum confirms sellers taking control"])


def strat_mfi_oversold(s):
    # B628 F1 family-sweep: positive symmetric obv_bearish.
    fl = (s.get("mfi_oversold") and (s.get("near_s1") or s.get("near_s2")) and s.get("obv_bullish"))
    fs = (s.get("mfi_overbought") and (s.get("near_r1") or s.get("near_r2"))
          and s.get("obv_bearish"))
    return _strat3(fl, fs, "mean_reversion",
        ["mfi_oversold","at_support","obv_bullish"],
        ["mfi_overbought","at_resistance","obv_bearish"],
        ["MFI oversold - volume-weighted RSI below 20","At pivot support","OBV rising"],
        ["MFI overbought - volume-weighted RSI above 80","At pivot resistance","OBV falling (B628 F1)"])


def strat_cmf_flip(s):
    fl = (s.get("cmf_cross_up") and s.get("rsi_14", 50) < 50)
    fs = (s.get("cmf_cross_dn") and s.get("rsi_14", 50) > 50)
    return _strat3(fl, fs, "mean_reversion",
        ["cmf_cross_up","rsi_14<50"], ["cmf_cross_dn","rsi_14>50"],
        ["CMF crossed above zero  -  money flow turned positive","RSI below 50"],
        ["CMF crossed below zero  -  money flow turned negative","RSI above 50"])


def strat_bollinger_lower(s):
    """Bollinger lower-band mean-reversion. Batch 204 (2026-05-17 owner-approved
    research review): stacked with Connors RSI(2)<5 OR vanilla RSI(14)<40
    AND price > 200-EMA regime gate (Connors discipline filter from
    Quantified Strategies 2024 backtest). VIX-conditional threshold:
    in low-VIX bands tighten to RSI(14)<35; in high-VIX bands loosen to
    RSI(14)<45 (Atlantis-Press Su 2024 multi-indicator confluence study).
    """
    rsi_2 = s.get("rsi_2", 50)
    rsi_14 = s.get("rsi_14", 50)
    # B663 family-bug sweep: was default-True silent-gap; positive symmetric below_ema_200 (B630 producer)
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    adx_ok = s.get("adx", 30) < 30
    # VIX-conditional RSI threshold (defaults to 40 when no VIX context)
    if s.get("vix_band_low"):
        rsi_thr_long, rsi_thr_short = 35, 65
    elif s.get("vix_band_high"):
        rsi_thr_long, rsi_thr_short = 45, 55
    else:
        rsi_thr_long, rsi_thr_short = 40, 60
    # Long: BB touch lower AND (Connors RSI(2)<5 OR vanilla RSI<thr) AND
    # regime gate (price > 200-EMA) AND no strong trend.
    rsi_long_ok = (rsi_2 < 5) or (rsi_14 < rsi_thr_long)
    fl = (s.get("bb_20_20_touch_lower") and rsi_long_ok and above_200 and adx_ok)
    # Short: opposite side; positive-symmetric below_ema_200 (B663 from NOT-pattern).
    rsi_short_ok = (rsi_2 > 95) or (rsi_14 > rsi_thr_short)
    fs = (s.get("bb_20_20_touch_upper") and rsi_short_ok and below_200 and adx_ok)
    return _strat3(fl, fs, "mean_reversion",
        ["bb_20_20_touch_lower", f"rsi_2<5_or_rsi_14<{rsi_thr_long}",
         "price_above_ema_200", "adx<30"],
        ["bb_20_20_touch_upper", f"rsi_2>95_or_rsi_14>{rsi_thr_short}",
         "price_below_ema_200", "adx<30"],
        [f"Price at lower Bollinger Band - statistically extreme low",
         f"RSI(2)<5 Connors extreme OR RSI(14)<{rsi_thr_long}",
         "Price above 200-EMA (regime gate)", "No strong trend"],
        [f"Price at upper Bollinger Band - statistically extreme high",
         f"RSI(2)>95 OR RSI(14)>{rsi_thr_short}",
         "Price below 200-EMA (bear regime)", "No strong trend"])


def strat_bollinger_tight(s):
    """Tight Bollinger touch mean-reversion. Batch 204 (owner-approved
    research review 2026-05-17): same stacking discipline as
    strat_bollinger_lower but uses tighter 1.5-sigma band and a softer
    RSI threshold (Bollinger 1.5sig is by definition more frequent so
    requires less-stringent oscillator confirmation).
    """
    rsi_2 = s.get("rsi_2", 50)
    rsi_14 = s.get("rsi_14", 50)
    # B663 family-bug sweep: was default-True silent-gap; positive symmetric below_ema_200 (B630 producer)
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    # VIX-conditional threshold (slightly looser than bollinger_lower since
    # the 1.5sig band is more frequent)
    if s.get("vix_band_low"):
        rsi_thr_long, rsi_thr_short = 40, 60
    elif s.get("vix_band_high"):
        rsi_thr_long, rsi_thr_short = 50, 50
    else:
        rsi_thr_long, rsi_thr_short = 45, 55
    rsi_long_ok = (rsi_2 < 10) or (rsi_14 < rsi_thr_long)
    fl = (
        (s.get("bb_20_15_touch_lower") or s.get("bb_20_20_touch_lower"))
        and rsi_long_ok
        and above_200
    )
    rsi_short_ok = (rsi_2 > 90) or (rsi_14 > rsi_thr_short)
    fs = (
        (s.get("bb_20_15_touch_upper") or s.get("bb_20_20_touch_upper"))
        and rsi_short_ok
        and below_200
    )
    return _strat3(fl, fs, "mean_reversion",
        ["bb_touch_lower_tight", f"rsi_2<10_or_rsi_14<{rsi_thr_long}",
         "price_above_ema_200"],
        ["bb_touch_upper_tight", f"rsi_2>90_or_rsi_14>{rsi_thr_short}",
         "price_below_ema_200"],
        ["Price at tight lower Bollinger Band - extreme low",
         f"RSI(2)<10 OR RSI(14)<{rsi_thr_long}",
         "Price above 200-EMA (regime gate)"],
        ["Price at tight upper Bollinger Band - extreme high",
         f"RSI(2)>90 OR RSI(14)>{rsi_thr_short}",
         "Price below 200-EMA (bear regime)"])


def strat_bollinger_upper_short(s):
    fires = (s.get("bb_20_20_touch_upper") and
             s.get("rsi_14", 50) > 70 and
             s.get("shooting_star"))
    return _strat(fires, "short", "mean_reversion",
        ["bb_20_20_touch_upper","rsi_14>70","shooting_star"],
        [f"Price at upper Bollinger Band (20,2)  -  overbought extreme",
         f"RSI-14 at {s.get('rsi_14',0):.1f}  -  overbought above 70",
         "Shooting star candle  -  sellers rejecting the high"])


def strat_keltner_lower(s):
    # B628 F1 family-sweep: positive symmetric obv_bearish.
    fl = (s.get("kc_touch_lower") and s.get("hammer") and s.get("obv_bullish"))
    fs = (s.get("kc_touch_upper") and s.get("shooting_star") and s.get("obv_bearish"))
    return _strat3(fl, fs, "mean_reversion",
        ["kc_touch_lower","hammer","obv_bullish"],
        ["kc_touch_upper","shooting_star","obv_bearish"],
        ["Price at lower Keltner Channel","Hammer confirms buyers","OBV rising"],
        ["Price at upper Keltner Channel","Shooting star confirms sellers","OBV falling (B628 F1)"])


def strat_stoch_oversold(s):
    """Stochastic oversold/overbought mean-reversion with K-vs-D cross
    + EMA-20 trend filter.

    LONG fires when Stochastic %K is <20 (oversold) AND K crosses above
    D (turning bullish) AND price aligned with uptrend (above EMA-20).
    SHORT fires on the symmetric overbought + bearish cross + downtrend.

    Batch 627 (2026-06-08 owner-directed family-bug sweep per
    CHECKLIST #105 (n) - bundled F1 fix with strat_awesome_oscillator):

      F1 - silent-gap fix per `feedback_never_use_NOT_s_get_pattern`.
        SHORT side `not s.get("price_above_ema_20")` -> `s.get(
        "below_ema_20", False)` (B609 positive symmetric producer).

    Post-B627 gate set (unchanged count; F1 hardens pattern only):
      LONG:  stoch_oversold + stoch_bullish_cross + price_above_ema_20
      SHORT: stoch_overbought + stoch_bearish_cross + below_ema_20
             (B627 F1 positive symmetric)
    """
    fl = (s.get("stoch_oversold")
          and s.get("stoch_bullish_cross")
          and s.get("price_above_ema_20"))
    # B627 F1: positive symmetric (B609 producer)
    fs = (s.get("stoch_overbought")
          and s.get("stoch_bearish_cross")
          and s.get("below_ema_20"))
    return _strat3(fl, fs, "mean_reversion",
        ["stoch_oversold","stoch_bullish_cross","price_above_ema_20"],
        ["stoch_overbought","stoch_bearish_cross","below_ema_20"],
        ["Stochastic oversold below 20",
         "K crossed above D - turning bullish",
         "Above EMA-20 (trend filter)"],
        ["Stochastic overbought above 80",
         "K crossed below D - turning bearish",
         "Below EMA-20 (trend filter; B627 F1 positive symmetric)"])


# -----------------------------------------------------------------------------
# CATEGORY 5: BREAKOUT (6 strategies)
# -----------------------------------------------------------------------------

def strat_squeeze_breakout(s):
    fires = s.get("squeeze_fire_up")
    return _strat(fires, "long", "breakout",
        ["squeeze_fire_up"],
        ["Bollinger Bands were inside Keltner Channels  -  coiling",
         "Squeeze released with positive momentum  -  energy unleashing",
         "One of the highest probability breakout signals"])


def strat_volume_spike_breakout(s):
    """Batch 597 (2026-06-05 owner-directed Stage 4 walk):
      (a) Added close_above_open + close_in_top_40pct_of_range (long) /
          close_below_open + close_in_bottom_40pct_of_range (short).
          Standardizes with the donchian family upgrades (B589 / B591).
      (c) Loosened vol gate vol_spike_2x -> vol_spike_15x (>= 1.5x).
          The 2.0x threshold was gating too many real breakouts at
          Phase 1A-beta scale (same logic Batch 320 used for
          donchian_10_breakout from 1.5x -> 1.0x; here 2.0x -> 1.5x).
      (d) Replaced above_vwap (cumulative-since-history) with
          Brian Shannon (2022) anchored VWAP. Batch 598 owner-directed
          symmetry fix: BOTH directions now use 20-day anchors matching
          the DC20 breakout window:
            LONG : above_avwap_20low (above AVWAP anchored at recent
                   20-day swing low - 20-day upleg intact)
            SHORT: NOT above_avwap_20high (price below AVWAP anchored
                   at recent 20-day swing high - 20-day rally given back)
          B598 added avwap_20low to the compute_vwap producer
          (additive; existing consumers of avwap_50low / 20high / 252low
          unchanged).
      (e) Regime affinity: REMOVED explicit allow-all entry from
          STRATEGY_REGIME_AFFINITY (was {bull, neutral, bear, crisis}
          - defeated regime classification). Now relies on Batch 291
          direction-aware default: LONG -> {bull, neutral}; SHORT ->
          {bear, crisis, neutral}.
    """
    fl = (s.get("dc20_breakout_up")
          and s.get("vol_spike_15x")
          and s.get("above_avwap_20low")
          and s.get("close_above_open")
          and s.get("close_in_top_40pct_of_range"))
    # B612 refactor: NOT s.get(above_avwap_20high) (no default - silent-gap
    # risk) -> positive below_avwap_20high (B612 added).
    fs = (s.get("dc20_breakout_dn")
          and s.get("vol_spike_15x")
          and s.get("below_avwap_20high")
          and s.get("close_below_open")
          and s.get("close_in_bottom_40pct_of_range"))
    return _strat3(fl, fs, "breakout",
        ["dc20_breakout_up","vol_spike_15x","above_avwap_20low","close_above_open","close_in_top_40pct_of_range"],
        ["dc20_breakout_dn","vol_spike_15x","below_avwap_20high","close_below_open","close_in_bottom_40pct_of_range"],
        ["Price broke above 20-day Donchian high",
         "Volume 1.5x confirms institutional buying",
         "Above 20-day swing-low AVWAP (Brian Shannon 2022) - 20d upleg intact",
         "Bullish bar (close above open)",
         "Strong close (top 40pct of range)"],
        ["Price broke below 20-day Donchian low",
         "Volume 1.5x confirms institutional selling",
         "Below 20-day swing-high AVWAP - 20d rally given back",
         "Bearish bar (close below open)",
         "Strong close (bottom 40pct of range)"])


def strat_52w_high_breakout(s):
    """Batch 589 (2026-06-04 owner directive '52w_high_breakout previous
    strategies - add close above open and close within 40% of day high'):
      - B586: vol_spike_2x -> vol_spike_17x; added sector_outperforming_spy
      - B589: added close_above_open + close_in_top_40pct_of_range
    Producer signals: break_52w_high (B582 fix), vol_spike_17x (B586),
    sector_outperforming_spy (B586), close_above_open (existing),
    close_in_top_40pct_of_range (B589).
    """
    fires = (s.get("break_52w_high")
             and s.get("vol_spike_17x")
             and s.get("sector_outperforming_spy")
             and s.get("close_above_open")
             and s.get("close_in_top_40pct_of_range"))
    return _strat(fires, "long", "breakout",
        ["break_52w_high", "vol_spike_17x", "sector_outperforming_spy",
         "close_above_open", "close_in_top_40pct_of_range"],
        [f"Price broke 52-week high at ${s.get('year_high',0):.2f}",
         "George-Hwang 2004 JF - new highs attract buyers",
         "Volume >1.7x confirms institutional conviction",
         "Sector ETF outperforming SPY 20d - trade strong sectors only",
         "Bullish bar with close in top 40% of range - strong-close signal (B589)"])


def strat_52w_high_breakout_pullback_long(s):
    """Batch 586 owner directive 'MISSING -- 52w_high_breakout_pullback_long
    - add along with inverse'. Pullback variant per owner spec: wait
    for daily close above 52w high, monitor retest, enter on bounce
    off the new support on lower volume.
    Producer near_52w_high_retest_long is emitted by compute_volume
    when (a) prior_year_high broken in last 10 days, (b) close now
    within 1pct of that level, (c) volume below 20d avg, (d) bullish
    bar.
    """
    fires = s.get("near_52w_high_retest_long", False)
    return _strat(fires, "long", "breakout",
        ["near_52w_high_retest_long"],
        ["52-week high RETEST long (classical breakout pullback)",
         "Prior 252d high broken in last 10 days; price now retesting as support",
         "Low-volume retest = sellers exhausted; bullish close = bounce confirmed",
         "Higher conviction than chase-the-breakout"])


def strat_52w_low_breakdown_pullback_short(s):
    """Batch 586 inverse of strat_52w_high_breakout_pullback_long
    per feedback_long_short_inverse_audit. Stock broke prior_year_low
    in last 10 days; retests it as resistance with low-volume
    rejection + bearish bar."""
    fires = s.get("near_52w_low_retest_short", False)
    return _strat(fires, "short", "breakout",
        ["near_52w_low_retest_short"],
        ["52-week low RETEST short (mirror of pullback long)",
         "Prior 252d low broken in last 10 days; price now retesting as resistance",
         "Low-volume retest + bearish close = rejection of bounce-back",
         "Higher conviction than chase-the-breakdown"])


def strat_inside_bar_breakout(s):
    fires = (s.get("inside_bar") and
             s.get("adx_trending") and
             s.get("above_vwap"))
    return _strat(fires, "long", "breakout",
        ["inside_bar","adx_trending","above_vwap"],
        ["Inside bar formed  -  consolidation within prior bar's range",
         "Classic pre-breakout compression setup",
         "ADX trending and above VWAP  -  breakout direction likely up"])


def strat_force_index_breakout(s):
    """Elder 1993 *Trading for a Living* Force Index zero-line cross with
    EMA-20 trend filter + B589-family bullish/bearish bar gate.

    Force Index (Elder) = (close.diff x volume) smoothed by 13-period
    EMA. A zero-line cross UP indicates price-x-volume momentum has
    turned positive (accumulation pressure); a cross DN indicates
    distribution pressure. The EMA-20 trend filter ensures the cross
    aligns with the prevailing trend direction.

    Batch 626 (2026-06-08 owner-directed Stage 4 walk per CHECKLIST
    #105 + B623 REMOVE_OK candidate review; C option approved):

      F1 - silent-gap fix per `feedback_never_use_NOT_s_get_pattern`.
        Pre-B626 SHORT side used `not s.get("price_above_ema_20")`
        which auto-passed when the EMA-20 key was missing (None is
        falsy; not None = True). Producer DOES emit price_above
        _ema_20 + the symmetric below_ema_20 (B609 producer), so the
        positive symmetric signal is wired.
      F2 - docstring + Elder 1993 source citation added (pre-B626 the
        strategy had zero docstring).
      (a) - B589-family bullish/bearish bar gate: close_above_open
        (LONG) / close_below_open (SHORT). Aligns this 2-gate strategy
        with the family standardization for momentum-event entries.

    Post-B626 3-gate set per direction:
      LONG:  force_index_cross_up + price_above_ema_20 + close_above_open
      SHORT: force_index_cross_dn + below_ema_20 + close_below_open

    DEFERRED to R5 per B624 manifest M1: STRATEGY_REGIME_AFFINITY
    entry `{bull, bear, crisis, neutral}` (all-4 regimes; effectively
    no constraint) is a B623 REMOVE_OK candidate (REMOVE gains
    +620.5pp PnL). Map removal pends R5 direction-aware confirmation.

    Family-bug surfaced (CHECKLIST n; not actioned in this batch):
    2 other strategies use the same `not s.get("price_above_ema_20")`
    pattern - strat_awesome_oscillator + strat_stoch_oversold (SHORT
    sides). Owner-directed follow-up batch to sweep both with the same
    F1 swap.

    Regime affinity per current map: all 4 regimes (deferred per
    B624 manifest).
    """
    # B626 F1 + (a): positive symmetric signal + bullish-bar gate
    fl = (s.get("force_index_cross_up")
          and s.get("price_above_ema_20")
          and s.get("close_above_open"))
    fs = (s.get("force_index_cross_dn")
          and s.get("below_ema_20")          # B626 F1 (B609 producer)
          and s.get("close_below_open"))     # B626 (a)
    return _strat3(fl, fs, "breakout",
        ["force_index_cross_up","price_above_ema_20","close_above_open"],
        ["force_index_cross_dn","below_ema_20","close_below_open"],
        ["Force Index crossed above zero - price-x-volume momentum positive (Elder 1993)",
         "Above EMA-20 (trend filter)",
         "Bullish bar - close above open (B589-family; B626 a)"],
        ["Force Index crossed below zero - price-x-volume momentum negative (Elder 1993)",
         "Below EMA-20 (trend filter; B626 F1 positive symmetric)",
         "Bearish bar - close below open (B589-family; B626 a)"])


def strat_donchian_10_breakout(s):
    """Batch 320 (2026-05-25): loosened vol gate from vol_spike_15x to
    vol_above_avg (>=1.0x) per owner directive. The 1.5x bar at Phase
    1A-beta scale gated out all 10-day breakouts on the trade log;
    above-average volume on the breakout day is still required.

    Batch 591 (2026-06-04 owner-directed Stage 4 walk):
      (b) dc10_breakout_up/dn -> dc10_breakout_up_1pct/dn_1pct (1% tolerance,
          LOCAL signals consumed by donchian_10_breakout alone)
      (c) added close_above_open (long) / close_below_open (short)
      (d) added close_in_top_40pct_of_range (long) /
          close_in_bottom_40pct_of_range (short)

    Batch 592 (2026-06-05 owner answer (i) "Strong-breakout requirement"
    closing the B591 (e) deferred item): added dc10_strong_breakout_up
    (long) / dc10_strong_breakout_dn (short) gate. Today's close must
    clear prior 10-day high by at least 0.5 * ATR(14) (long) or break
    prior 10-day low by at least 0.5 * ATR(14) (short) - filters
    trivial closes-just-above-level pseudo-breakouts.
    """
    fl = (s.get("dc10_breakout_up_1pct") and s.get("vol_above_avg")
          and s.get("macd_12_26_9_bullish")
          and s.get("close_above_open")
          and s.get("close_in_top_40pct_of_range")
          and s.get("dc10_strong_breakout_up"))
    # B612 (2026-06-07 owner+AI critique refactor): SHORT side switched
    # from `not s.get("macd_12_26_9_bullish")` (no default - silent-gap
    # risk) to explicit `s.get("macd_12_26_9_bearish")` per
    # feedback_never_use_NOT_s_get_pattern. Producer signal added in B609.
    fs = (s.get("dc10_breakout_dn_1pct") and s.get("vol_above_avg")
          and s.get("macd_12_26_9_bearish")
          and s.get("close_below_open")
          and s.get("close_in_bottom_40pct_of_range")
          and s.get("dc10_strong_breakout_dn"))
    return _strat3(fl, fs, "breakout",
        ["dc10_breakout_up_1pct","vol_above_avg","macd_bullish","close_above_open","close_in_top_40pct_of_range","dc10_strong_breakout_up"],
        ["dc10_breakout_dn_1pct","vol_above_avg","macd_bearish","close_below_open","close_in_bottom_40pct_of_range","dc10_strong_breakout_dn"],
        ["Price broke 10-day Donchian high (1pct tolerance)","Volume above 20d avg confirms","MACD positive","Bullish bar (close above open)","Strong close (top 40pct of range)","Strong breakout (close >= prior_high + 0.5*ATR14)"],
        ["Price broke 10-day Donchian low (1pct tolerance)","Volume above 20d avg confirms","MACD negative","Bearish bar (close below open)","Strong close (bottom 40pct of range)","Strong breakdown (close <= prior_low - 0.5*ATR14)"])


# BUG-111 retest variants (Batch 329 2026-05-25 owner-approved option b):
# explicit _retest variants for the 6 price-pattern breakouts that didn't yet
# have one. Reuse the shared resistance_break_retest / support_break_retest
# primitive from technical.compute_break_retest_signals (DC20-anchored), which
# is the same approach strat_r1_break_retest takes for R1-anchored breakouts.
# Bulkowski Encyclopedia of Chart Patterns: post-break retest is the
# canonical pullback that confirms the breakout; volume on the retest is
# typically LOWER than the break (per Batch 320 Cat-3 B rationale).
# pre_rebalance_long is event-based (not a price-pattern break) so excluded.


# Batch 599 (2026-06-05 owner B596 convergence option 2):
# strat_donchian_20_breakout_retest DELETED. After B596 made the tight
# retest pair (donchian_breakout_retest_long + donchian_breakdown_retest
# _short) functionally identical to this dual strategy, owner chose
# Option 2 (delete dual, keep explicit per-direction pair) for
# (i) per-direction regime affinity ease and (ii) naming consistency
# with the rest of the donchian family. Strategy walk history
# (B591 + B594) preserved in approvals.json + git history.


# Batch 592 (2026-06-05 owner correction): strat_donchian_breakdown_retest_short
# RESTORED. B591 deletion was a misinterpretation - owner intent was to
# RESTORE long/short symmetry by ADDING the missing tight-long mirror
# (strat_donchian_breakout_long), NOT to delete the tight-short. Both
# tight-long AND tight-short variants now coexist post-B592.
def strat_donchian_breakdown_retest_short(s):
    """BUG-111 (Batch 329): retest variant of donchian_breakdown_short.
    Short on the post-break retest of broken support.

    Batch 592 (2026-06-05 owner correction): RESTORED with original
    3-gate logic after misinterpreted B591 deletion.

    Batch 596 (2026-06-05 owner-directed Stage 4 walk of tight retest
    pair):
      (a) Symmetry: added close_below_open + close_in_bottom_40pct_of_range
          to match donchian_breakout_retest_long gate count.
      (b) Flipped vol_spike_15x -> vol_below_avg per Bulkowski retest
          thesis (retest forms on LOWER volume = supply absorption).
      (c) Replaced support_break_retest with B594 LOCAL strong variant
          dc20_support_break_retest_strong (original breakdown bar must
          clear level by >= 0.5*ATR(14)).
      (e) Regime affinity: rely on Batch 291 direction-aware default
          (SHORT -> {bear, crisis, neutral}).
    """
    # B612 refactor: NOT s.get(macd_bullish) -> positive macd_bearish.
    fires = (s.get("dc20_support_break_retest_strong")
             and s.get("vol_below_avg")
             and s.get("macd_12_26_9_bearish")
             and s.get("close_below_open")
             and s.get("close_in_bottom_40pct_of_range"))
    return _strat(fires, "short", "breakout",
        ["dc20_support_break_retest_strong","vol_below_avg","macd_bearish","close_below_open","close_in_bottom_40pct_of_range"],
        ["Post-break retest of broken Donchian support (strong break: >=0.5*ATR clearance)",
         "Volume below 20d avg (Bulkowski retest thesis)",
         "MACD bearish - trend agrees",
         "Bearish bar (close below open)",
         "Strong close (bottom 40pct of range)"])


# -----------------------------------------------------------------------------
# strat_volume_spike_breakout_retest DELETED Batch 682 (2026-06-10 owner-approved)
# -----------------------------------------------------------------------------
# DELETION RATIONALE per B680 self-critique CC-B + owner approval 2026-06-10:
#
# B621 fire-count estimator: 0.01/yr universe-wide projected (HIGHEST RISK
# FAIL_FIRE_STARVED in entire 222-strategy roster). Even allowing 100x
# under-estimate (estimator-to-actual ratio), realized fire count ~1/yr --
# below `min_trades=30` per regime by 1.5 orders of magnitude. The strategy
# CANNOT be statistically validated by ANY cube replay; registration consumes
# correction budget for zero return.
#
# Per B620 squeeze_setup_event_only_long DELETION precedent (FAIL_FIRE_STARVED
# at 2.5 fires/yr, owner-approved): BR-15 is 250x worse case (0.01/yr vs
# 2.5/yr). The precedent argues for deletion before B660 cube wastes effort
# on a zero-fire strategy.
#
# Per `project_no_apriori_strategy_pruning` explicit owner override on
# confirmed empirical failure: owner approved deletion 2026-06-10 in
# response to B680 self-critique recommendation.
#
# Post-B600 design (5-gate dual with dc20_strong_break_retest + vol_spike_2x
# + AVWAP + bullish/bearish bar + close-strength) preserved in git history
# at commit `<this-batch-parent>` for any future re-introduction with looser
# gates.
#
# No downstream code references; ALL_STRATEGIES registry entry also removed.
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# CATEGORY 6: CANDLE PATTERNS (6 strategies  -  2 shorts)
# -----------------------------------------------------------------------------

def strat_morning_star(s):
    """B639 (2026-06-09 owner-directed walk option 2 reconcile-to-reversal):
    canonical Nison 1991 morning-star / evening-star three-bar reversal
    pair per Nison _Japanese Candlestick Charting Techniques_ Sec 6.4-6.5.
    Pre-B639 had ema_50_200_bullish (LONG) and ema_50_200_bearish (SHORT)
    trend gates that filtered out exactly the regime Nison wrote the
    pattern for - the morning star is a BOTTOM reversal pattern; requiring
    a confirmed uptrend before it can fire encodes a continuation thesis
    (buy-the-dip) under a reversal-pattern docstring. Owner walk option 2
    removed the trend gates so the strategy fires on canonical Nison
    turns: pattern + RSI-not-overbought/oversold band only.

    Producer pair compute_candles in technical.py:1460-1475 (Nison strict
    4-condition AND - bar -3 directional + bar -2 small body <30pct of
    range + bar -1 directional + bar -1 close past bar -3 midpoint;
    B559 OPT-C operator-precedence fix).

    Same-walk siblings: strat_evening_star_short DELETED B639 as strictly
    redundant after reconciliation (its post-B639 form would be a strict
    subset of this strategy's SHORT side); STRATEGY_REGIME_AFFINITY
    `morning_star: {bear}` entry deleted (F3 - LONG side could never
    fire under it since LONG requires bullish setup conditions and bear
    regime gates them out; SHORT side over-restricted vs B291 default).

    Gates:
      LONG  = morning_star AND rsi_14 < 45  (RSI band rejects fires
              already deep in oversold blow-off territory).
      SHORT = evening_star AND rsi_14 > 55  (mirror).
    """
    fl = (s.get("morning_star") and s.get("rsi_14", 50) < 45)
    fs = (s.get("evening_star") and s.get("rsi_14", 50) > 55)
    return _strat3(fl, fs, "candle",
        ["morning_star","rsi_14<45"], ["evening_star","rsi_14>55"],
        ["Three-bar morning star  -  Nison bullish reversal (bottom call)","RSI not deep-oversold"],
        ["Three-bar evening star  -  Nison bearish reversal (top call)","RSI not deep-overbought"])


def strat_bullish_engulfing_support(s):
    # B628 F1 family-sweep: positive symmetric obv_bearish.
    fl = (s.get("bullish_engulfing") and (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and s.get("obv_bullish"))
    fs = (s.get("bearish_engulfing") and (s.get("near_r1") or s.get("near_r2") or s.get("at_key_fib"))
          and s.get("obv_bearish"))
    return _strat3(fl, fs, "candle",
        ["bullish_engulfing","at_support","obv_bullish"],
        ["bearish_engulfing","at_resistance","obv_bearish"],
        ["Bullish engulfing at support - two systems confirming","OBV rising"],
        ["Bearish engulfing at resistance - two systems confirming","OBV falling (B628 F1)"])


def strat_hammer_at_support_long(s):
    """Batch 685 (2026-06-10 owner-approved Class 7 NEW) per
    feedback_long_short_inverse_audit + B683 self-critique CC-4
    missing-inverse audit. Symmetric mirror of CC-4
    strat_shooting_star_short.

    Hammer at support is the canonical 1-bar bullish reversal pattern
    per Nison 1991 *Japanese Candlestick Charting Techniques* -
    small body with long lower wick at support level shows sellers
    exhausted + buyers stepping in. Symmetric to shooting_star (small
    body + long upper wick at resistance).

    Producer: technical.py:1623 `hammer = lwk>2*body and uwk<body and
    body>0` (Nison canonical hammer definition; already emitted +
    consumed by W3/W5 pivot strategies as confluence-gate; no producer
    change needed).

    3-gate structure symmetric with CC-4 (mirror with hammer + support +
    RSI oversold replacing shooting_star + resistance + RSI overbought):
    """
    fires = (s.get("hammer") and
             (s.get("near_s1") or s.get("near_s2") or
              s.get("bb_20_20_touch_lower")) and
             s.get("rsi_14", 50) < 35)
    return _strat(fires, "long", "candle",
        ["hammer","at_support","rsi_14<35"],
        ["Hammer at support level - bullish reversal",
         "Long lower wick shows buyers rejecting lower prices",
         f"RSI-14 at {s.get('rsi_14',0):.1f} - oversold at support"])


def strat_doji_at_support(s):
    # B574 (2026-06-04 owner-directed narrow-scope per
    # feedback_narrow_scope_blast_radius): consumes `_wide` flag
    # variants (1.5pct band) exclusively. Other strategies that use
    # the narrow 0.3pct near_s1/at_key_fib stay unchanged.
    fires = (s.get("doji") and
             (s.get("near_s1_wide") or s.get("near_s2_wide") or s.get("at_key_fib_wide")) and
             s.get("vol_spike_15x"))
    return _strat(fires, "long", "candle",
        ["doji","at_support_wide_1.5pct","vol_spike_1.5x"],
        ["Doji candle at support  -  indecision after downmove",
         "Buyers and sellers equally matched  -  reversal often follows",
         "Volume spike confirms the level is being contested",
         "Wide 1.5pct support band (B574 owner-directed)"])


def strat_doji_at_resistance_short(s):
    """Batch 572 (2026-06-04): inverse of doji_at_support per
    feedback_long_short_inverse_audit. Mirror of strat_doji_at_support
    per Nison symmetric pattern.

    B574 (2026-06-04): consumes `_wide` flag variants (1.5pct band)
    exclusively, narrow-scoped to doji strategies per
    feedback_narrow_scope_blast_radius. Other strategies use the
    standard 0.3pct near_r1/at_key_fib unchanged.
    """
    fires = (s.get("doji") and
             (s.get("near_r1_wide") or s.get("near_r2_wide") or s.get("at_key_fib_wide")) and
             s.get("vol_spike_15x"))
    return _strat(fires, "short", "candle",
        ["doji","at_resistance_wide_1.5pct","vol_spike_1.5x"],
        ["Doji candle at resistance  -  indecision after upmove",
         "Buyers and sellers equally matched at overhead level",
         "Volume spike confirms the level is being contested"])


def strat_three_white_soldiers(s):
    """Three White Soldiers bullish reversal pattern (Nison
    *Japanese Candlestick Charting Techniques* 1991).

    Three consecutive bullish candles, each closing higher than the
    prior + each open higher than the prior. Strong reversal signal
    indicating sustained buying pressure over 3 days. RSI<60 gate
    keeps the entry from already-overbought territory.

    Batch 636 (2026-06-08 owner-directed Stage 4 walk per CHECKLIST
    #105 + EXECUTION_QUEUE S4-WALK deferred candle-cluster):

      F1 - Class 7 NEW missing-inverse wired: `strat_three_black
        _crows_short` added per `feedback_long_short_inverse_audit` +
        `feedback_wire_new_strategies_on_the_spot`. Producer signal
        `three_black_crows` exists (technical.py:1483-1486) but no
        SHORT strategy consumed it pre-B636. Nison documents the
        bearish mirror as a canonical reversal pattern with the same
        playbook semantics.
      F2 - docstring added with Nison 1991 source citation.

    Economic symmetry per CHECKLIST (m): structurally + economically
    symmetric to three_black_crows (Nison canonical bearish reversal).
    """
    fires = (s.get("three_white_soldiers") and
             s.get("rsi_14", 50) < 60)
    return _strat(fires, "long", "candle",
        ["three_white_soldiers","rsi_14<60"],
        ["Three consecutive bullish candles each closing near their high",
         "Strong reversal signal - sustained buying pressure over 3 days (Nison 1991)",
         "RSI below 60 - room to run, not entering overbought"])


def strat_three_black_crows_short(s):
    """Three Black Crows bearish reversal pattern (Nison
    *Japanese Candlestick Charting Techniques* 1991).

    Symmetric SHORT mirror of strat_three_white_soldiers wired in
    Batch 636 (2026-06-08 owner-directed Class 7 NEW per
    `feedback_long_short_inverse_audit`).

    Three consecutive bearish candles, each closing lower than the
    prior + each open lower than the prior. Strong bearish reversal
    indicating sustained selling pressure over 3 days. RSI>40 gate
    keeps the entry from already-oversold territory (mirror of
    LONG side's RSI<60 cap).

    Producer: `three_black_crows` from compute_candle_signals
    (technical.py:1483-1486) - same B-T-C strict-monotone bearish
    3-bar pattern.

    Regime affinity: Batch 291 direction-aware default
      (SHORT -> {bear, crisis, neutral}).
    """
    fires = (s.get("three_black_crows") and
             s.get("rsi_14", 50) > 40)
    return _strat(fires, "short", "candle",
        ["three_black_crows","rsi_14>40"],
        ["Three consecutive bearish candles each closing near their low",
         "Strong reversal signal - sustained selling pressure over 3 days (Nison 1991)",
         "RSI above 40 - room to fall, not entering oversold"])


def strat_shooting_star_short(s):
    fires = (s.get("shooting_star") and
             (s.get("near_r1") or s.get("near_r2") or
              s.get("bb_20_20_touch_upper")) and
             s.get("rsi_14", 50) > 65)
    return _strat(fires, "short", "candle",
        ["shooting_star","at_resistance","rsi_14>65"],
        ["Shooting star at resistance level  -  bearish reversal",
         "Long upper wick shows sellers rejecting higher prices",
         f"RSI-14 at {s.get('rsi_14',0):.1f}  -  overbought at resistance"])


# strat_evening_star_short DELETED Batch 639 (2026-06-09 owner-directed walk
# of strat_morning_star option (a)). After B639 applied option 2 reconcile-
# to-reversal to strat_morning_star (removed ema_50_200_bullish/bearish trend
# gates), strat_evening_star_short's gate set (evening_star + rsi_14>55 +
# below_sma_50) became a strict subset of strat_morning_star's SHORT side
# (evening_star + rsi_14>55). Every fire of strat_evening_star_short was
# also a fire of strat_morning_star SHORT -> cube double-counted. Deleted
# per F4 finding from B637 walk. The standalone also carried the same
# reversal-vs-continuation thesis mismatch the dual was reconciled out of.


# -----------------------------------------------------------------------------
# CATEGORY 7: CONFLUENCE (9 strategies  -  highest conviction)
# -----------------------------------------------------------------------------

def strat_rsi_volume_200ema(s):
    """Batch 320 (2026-05-25): loosened vol gate from vol_spike_2x to
    vol_above_avg (>=1.0x) per owner directive. The 2x bar combined with
    RSI<35 AND above-200-EMA was nearly impossible to satisfy in trending
    markets (RSI<30 + uptrend is itself rare); the volume gate compounded
    that to zero. Above-average volume on the oversold day still confirms
    the move, without the 2x sledgehammer."""
    fl = (s.get("rsi_14", 50) < 35 and s.get("vol_above_avg") and s.get("price_above_ema_200"))
    # B630 sweep: positive symmetric below_ema_200 (silent-gap fix; no default=True)
    fs = (s.get("rsi_14", 50) > 65 and s.get("vol_above_avg") and s.get("below_ema_200"))
    return _strat3(fl, fs, "confluence",
        ["rsi_14<35","vol_above_avg","above_ema_200"], ["rsi_14>65","vol_above_avg","below_ema_200"],
        ["RSI oversold + volume above 20d avg + above 200 EMA  -  triple confluence bullish"],
        ["RSI overbought + volume above 20d avg + below 200 EMA  -  triple confluence bearish"])


def strat_macd_ichimoku(s):
    fl = (s.get("macd_12_26_9_crossover_up") and s.get("ichi_above_cloud"))
    fs = (s.get("macd_12_26_9_crossover_dn") and s.get("ichi_below_cloud"))
    return _strat3(fl, fs, "confluence",
        ["macd_crossover_up","ichi_above_cloud"], ["macd_crossover_dn","ichi_below_cloud"],
        ["MACD crossover up + above cloud  -  two systems bullish simultaneously"],
        ["MACD crossover down + below cloud  -  two systems bearish simultaneously"])


def strat_bb_squeeze_volume(s):
    fl = (s.get("squeeze_fire_up") and s.get("vol_spike_2x") and s.get("above_vwap"))
    # B634 sweep: positive symmetric below_vwap (B634 producer)
    fs = (s.get("squeeze_fire_dn") and s.get("vol_spike_2x") and s.get("below_vwap"))
    return _strat3(fl, fs, "confluence",
        ["squeeze_fire_up","vol_spike_2x","above_vwap"], ["squeeze_fire_dn","vol_spike_2x","below_vwap"],
        ["BB squeeze releasing upward with 2x volume","Above VWAP  -  buyers in control"],
        ["BB squeeze releasing downward with 2x volume","Below VWAP  -  sellers in control"])


def strat_pivot_fib_confluence(s):
    fl = ((s.get("near_s1") or s.get("near_s2")) and s.get("at_key_fib") and (s.get("hammer") or s.get("bullish_engulfing")))
    fs = ((s.get("near_r1") or s.get("near_r2")) and s.get("at_key_fib") and s.get("bearish_engulfing"))
    return _strat3(fl, fs, "confluence",
        ["at_pivot_support","at_key_fib","bullish_candle"], ["at_pivot_resistance","at_key_fib","bearish_engulfing"],
        ["Pivot support + Fibonacci + bullish candle  -  two systems at same level bullish"],
        ["Pivot resistance + Fibonacci + bearish engulfing  -  two systems at same level bearish"])


def strat_golden_cross_volume(s):
    fl = (s.get("ema_50_200_golden_cross") and s.get("vol_spike_2x"))
    fs = (s.get("ema_50_200_death_cross") and s.get("vol_spike_2x"))
    return _strat3(fl, fs, "confluence",
        ["ema_50_200_golden_cross","vol_spike_2x"], ["ema_50_200_death_cross","vol_spike_2x"],
        ["Golden cross with 2x volume  -  institutional confirmation of bullish shift"],
        ["Death cross with 2x volume  -  institutional confirmation of bearish shift"])


def strat_cpr_narrow_momentum(s):
    """Batch 358 (2026-05-25 owner-approved cell-audit Bucket B): added
    200-EMA regime gate per direction. Cell audit
    (cpr_narrow_momentum x atr_trail_1x) lost -355pp at WR 30.6% with
    no regime gate. Long now requires above_200_ema; short requires
    below_200_ema."""
    # B663 family-bug sweep: positive symmetric below_ema_200 (B630 producer) replaces (not above_200) NOT-pattern silent-gap per feedback_never_use_NOT_s_get_pattern. Pre-B663 the "left as-is for readability" comment was incorrect: `not s.get(key, False)` returns True on missing key, which auto-PASSES SHORT -- exactly the silent-gap class the feedback memory warned against.
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    fl = (s.get("cpr_narrow") and s.get("above_cpr") and s.get("rsi_14", 50) > 50
          and s.get("macd_12_26_9_bullish") and above_200)
    # B630 sweep: positive symmetric macd_12_26_9_bearish (B609 producer).
    fs = (s.get("cpr_narrow") and s.get("below_cpr") and s.get("rsi_14", 50) < 50
          and s.get("macd_12_26_9_bearish") and below_200)
    return _strat3(fl, fs, "confluence",
        ["cpr_narrow","above_cpr","rsi_14>50","macd_bullish","price_above_ema_200"],
        ["cpr_narrow","below_cpr","rsi_14<50","macd_bearish","price_below_ema_200"],
        ["Narrow CPR + above CPR + RSI>50 + MACD bullish + above 200-EMA - five-signal bullish day"],
        ["Narrow CPR + below CPR + RSI<50 + MACD bearish + below 200-EMA - five-signal bearish day"])


def strat_camarilla_rsi_obv(s):
    # B628 F1: obv_bullish -> obv_bearish (positive symmetric).
    # B629 F1 cmf-family sweep: cmf_positive -> cmf_negative
    # (B629 producer signal). Both silent-gaps now closed.
    fl = (s.get("near_cam_s3") and s.get("rsi_14", 50) < 35
          and s.get("obv_bullish") and s.get("cmf_positive"))
    fs = (s.get("near_cam_r3") and s.get("rsi_14", 50) > 65
          and s.get("obv_bearish")
          and s.get("cmf_negative"))
    return _strat3(fl, fs, "confluence",
        ["near_cam_s3","rsi_14<35","obv_bullish","cmf_positive"],
        ["near_cam_r3","rsi_14>65","obv_bearish","cmf_negative"],
        ["Camarilla S3 + RSI oversold + OBV rising + CMF positive - highest conviction long"],
        ["Camarilla R3 + RSI overbought + OBV bearish + CMF negative - highest conviction short (B628 F1 + B629 F1)"])


def strat_supertrend_ichimoku_adx(s):
    # B630 sweep: positive symmetric supertrend_bearish (B630 producer)
    fl = (s.get("supertrend_bullish") and s.get("ichi_above_cloud") and s.get("adx_strong"))
    fs = (s.get("supertrend_bearish") and s.get("ichi_below_cloud") and s.get("adx_strong"))
    return _strat3(fl, fs, "confluence",
        ["supertrend_bullish","ichi_above_cloud","adx_strong"], ["supertrend_bearish","ichi_below_cloud","adx_strong"],
        ["Supertrend + Ichimoku cloud + ADX  -  three trend systems bullish"],
        ["Supertrend + Ichimoku cloud + ADX  -  three trend systems bearish"])


def strat_williams_stoch_dual(s):
    fl = (s.get("williams_r_oversold") and s.get("stoch_oversold") and (s.get("near_s1") or s.get("near_s2") or s.get("near_cam_s3")))
    fs = (s.get("williams_r", 0) > -20 and s.get("stoch_overbought") and (s.get("near_r1") or s.get("near_r2") or s.get("near_cam_r3")))
    return _strat3(fl, fs, "confluence",
        ["williams_r_oversold","stoch_oversold","at_pivot_support"], ["williams_r_overbought","stoch_overbought","at_pivot_resistance"],
        ["Williams %R + Stochastic both oversold at pivot support  -  high conviction long"],
        ["Williams %R + Stochastic both overbought at pivot resistance  -  high conviction short"])


# -----------------------------------------------------------------------------
# CATEGORY 8: DEDICATED SHORT STRATEGIES (12 new  -  sell the rip)
# -----------------------------------------------------------------------------

# --- Trend-following shorts (4) ---

def strat_death_cross_50_200_volume(s):
    fires = (s.get("ema_50_200_death_cross") and s.get("vol_spike_2x"))
    return _strat(fires, "short", "trend",
        ["ema_50_200_death_cross", "vol_spike_2x"],
        ["EMA-50 crossed below EMA-200  -  death cross",
         "Volume 2x confirms institutional selling on the cross",
         "Structural shift to bearish  -  strong follow-through expected"])


def strat_supertrend_macd_short(s):
    # B630 sweep: double F1 - supertrend_bullish -> supertrend_bearish
    # (B630 producer) + macd_12_26_9_bullish -> macd_12_26_9_bearish.
    fires = (s.get("supertrend_bearish") and
             s.get("macd_12_26_9_bearish") and
             s.get("adx", 0) > 20)
    return _strat(fires, "short", "trend",
        ["supertrend_bearish", "macd_bearish", "adx>20"],
        ["Supertrend indicator bearish  -  trend confirmed downward",
         "MACD histogram negative  -  momentum aligned bearish",
         "ADX above 20  -  trend has real strength, not a sideways drift"])


def strat_ichimoku_cloud_breakdown(s):
    fires = (s.get("ichi_below_cloud") and
             s.get("ichi_tk_cross_dn") and
             s.get("adx_trending"))
    return _strat(fires, "short", "trend",
        ["ichi_below_cloud", "ichi_tk_cross_dn", "adx_trending"],
        ["Price broke below Ichimoku Cloud  -  full bearish structure",
         "Tenkan crossed below Kijun  -  short-term momentum confirming",
         "ADX trending  -  downtrend has strength"])


def strat_parabolic_sar_flip_short(s):
    fires = (s.get("psar_flip_dn") and s.get("adx_trending"))
    return _strat(fires, "short", "trend",
        ["psar_flip_dn", "adx_trending"],
        ["Parabolic SAR flipped above price  -  trend reversed downward",
         "Clean unambiguous signal  -  SAR is now resistance",
         "ADX trending  -  reversal has follow-through potential"])


# --- Momentum shorts (3) ---

def strat_macd_crossover_short(s):
    fires = s.get("macd_12_26_9_crossover_dn")
    return _strat(fires, "short", "momentum",
        ["macd_12_26_9_crossover_dn"],
        ["MACD 12/26/9 histogram crossed below zero",
         "Momentum turned negative  -  trend shift to downside",
         "High-probability momentum entry  -  catching the shift early"])


def strat_hull_rsi_short(s):
    # B634 sweep: positive symmetric hull_bearish + price_below_hull
    fires = (s.get("hull_bearish") and
             s.get("price_below_hull") and
             s.get("rsi_9", 50) < 50)
    return _strat(fires, "short", "momentum",
        ["hull_bearish", "price_below_hull", "rsi_9<50"],
        ["Hull MA falling  -  fast trend confirmed bearish",
         "Price below Hull MA  -  momentum aligned downward",
         "RSI-9 below 50  -  below midpoint, no upside momentum"])


def strat_stochrsi_overbought_short(s):
    fires = (s.get("stochrsi_overbought") and
             s.get("stochrsi_cross_dn") and
             s.get("rsi_14", 50) > 45)
    return _strat(fires, "short", "momentum",
        ["stochrsi_overbought", "stochrsi_cross_dn", "rsi_14>45"],
        ["StochRSI above 80  -  momentum exhausted at overbought",
         "K crossed below D  -  momentum turning down",
         "RSI-14 not oversold  -  room to fall"])


# --- Breakdown shorts (3  -  no long equivalent) ---

# Batch 592 (2026-06-05 owner correction): strat_donchian_breakdown_short
# RESTORED. B591 deletion was a misinterpretation - owner intent was
# symmetry via ADDING the missing tight-long mirror (donchian_breakout_long),
# NOT replacing the tight-short. Both tight variants now coexist post-B592.
def strat_donchian_breakdown_short(s):
    """Tight short Donchian-10 breakdown - 1.5x vol gate + MACD bearish.

    Batch 592 (2026-06-05 owner correction): RESTORED with original
    3-gate logic after misinterpreted B591 deletion.

    Batch 595 (2026-06-05 owner-directed Stage 4 walk of the tight
    non-retest pair):
      (a) Restore long/short symmetry with donchian_breakout_long.
          B591 added close_above_open + close_in_top_40pct_of_range to
          the long-only tight mirror but NOT to this short variant.
          B595 fixes that asymmetry. Now requires all 5 gates:
            dc10_breakout_dn + vol_spike_15x + NOT macd_bullish
            + close_below_open + close_in_bottom_40pct_of_range
      (e) Regime affinity: rely on Batch 291 direction-aware default
          (SHORT -> {bear, crisis, neutral}). NOT in
          STRATEGY_REGIME_AFFINITY map; default handles it.
    """
    # B612 refactor: NOT s.get(macd_bullish) -> positive macd_bearish (B609 added).
    fires = (s.get("dc10_breakout_dn")
             and s.get("vol_spike_15x")
             and s.get("macd_12_26_9_bearish")
             and s.get("close_below_open")
             and s.get("close_in_bottom_40pct_of_range"))
    return _strat(fires, "short", "breakout",
        ["dc10_breakout_dn","vol_spike_15x","macd_bearish","close_below_open","close_in_bottom_40pct_of_range"],
        ["Price broke 10-day Donchian low - downside breakout",
         "Volume 1.5x confirms institutional selling pressure",
         "MACD negative - momentum confirms the breakdown",
         "Bearish bar (close below open)",
         "Strong close (bottom 40pct of range)"])


def strat_donchian_breakout_long(s):
    """Batch 591 (2026-06-04 owner-directed Class 7 NEW): tight long-only
    Donchian-10 breakout. Mirror of donchian_breakdown_short
    (1.5x vol gate) plus B589-style strong-close + bullish-bar gates.
    Producer signals: dc10_breakout_up (existing 0.2pct tolerance),
    vol_spike_15x, macd_12_26_9_bullish, close_above_open,
    close_in_top_40pct_of_range.

    Batch 595 (2026-06-05 owner-directed Stage 4 walk of the tight
    non-retest pair): no gate changes here - this strategy already
    had all 5 gates from B591 inception. B595 (a) brought the SHORT
    mirror to parity by adding close_below_open + close_in_bottom_40pct
    _of_range to donchian_breakdown_short. (e) Regime affinity: rely
    on Batch 291 direction-aware default (LONG -> {bull, neutral}).
    """
    fires = (s.get("dc10_breakout_up")
             and s.get("vol_spike_15x")
             and s.get("macd_12_26_9_bullish")
             and s.get("close_above_open")
             and s.get("close_in_top_40pct_of_range"))
    return _strat(fires, "long", "breakout",
        ["dc10_breakout_up","vol_spike_15x","macd_bullish","close_above_open","close_in_top_40pct_of_range"],
        ["Price broke 10-day Donchian high - upside breakout",
         "Volume 1.5x confirms institutional buying pressure",
         "MACD positive - momentum confirms the breakout",
         "Bullish bar (close above open)",
         "Strong close (top 40pct of range)"])


def strat_donchian_breakout_retest_long(s):
    """Batch 591 (2026-06-04 owner-directed Class 7 NEW retest mirror):
    tight long-only retest variant. Mirror of donchian_breakdown_retest
    _short. Owner B591 answer C: (c)+(d) apply but skip (e) for retest
    variants. Producer: resistance_break_retest, vol_spike_15x,
    macd_12_26_9_bullish, close_above_open, close_in_top_40pct_of_range.

    Batch 596 (2026-06-05 owner-directed Stage 4 walk of tight retest
    pair):
      (a) Already had 5 gates from B591; no change.
      (b) Flipped vol_spike_15x -> vol_below_avg per Bulkowski thesis.
      (c) Replaced resistance_break_retest with B594 LOCAL strong
          variant dc20_resistance_break_retest_strong (original
          breakout bar must clear level by >= 0.5*ATR(14)).
      (e) Regime affinity: rely on Batch 291 direction-aware default
          (LONG -> {bull, neutral}).

    CONVERGENCE NOTE: post-B596 this strategy is functionally identical
    to the LONG side of donchian_20_breakout_retest (B594). Duplication
    flagged for owner resolution.
    """
    fires = (s.get("dc20_resistance_break_retest_strong")
             and s.get("vol_below_avg")
             and s.get("macd_12_26_9_bullish")
             and s.get("close_above_open")
             and s.get("close_in_top_40pct_of_range"))
    return _strat(fires, "long", "breakout",
        ["dc20_resistance_break_retest_strong","vol_below_avg","macd_bullish","close_above_open","close_in_top_40pct_of_range"],
        ["Post-break retest of broken Donchian resistance (strong break: >=0.5*ATR clearance)",
         "Volume below 20d avg (Bulkowski retest thesis)",
         "MACD bullish - trend agrees",
         "Bullish bar (close above open)",
         "Strong close (top 40pct of range)"])


def strat_52w_low_breakdown(s):
    """Batch 589 (2026-06-04 owner directive 'add inverse for mirror'
    on B589 52w_high_breakout changes):
      - B587: vol_spike_2x -> vol_spike_17x; sector_underperforming_spy
      - B589: added close_below_open + close_in_bottom_40pct_of_range
    Producer signals: break_52w_low (B582 fix), vol_spike_17x (B586),
    sector_underperforming_spy (B587), close_below_open (existing),
    close_in_bottom_40pct_of_range (B589).
    """
    fires = (s.get("break_52w_low")
             and s.get("vol_spike_17x")
             and s.get("sector_underperforming_spy")
             and s.get("close_below_open")
             and s.get("close_in_bottom_40pct_of_range"))
    return _strat(fires, "short", "breakout",
        ["break_52w_low", "vol_spike_17x", "sector_underperforming_spy"],
        [f"Price broke 52-week low  -  serious capitulation signal",
         "Volume >1.7x confirms institutional distribution (George-Hwang 2004 JF mirror)",
         "Sector ETF underperforming SPY 20d  -  sell weak sectors only",
         "Stocks at new 52-week lows in weak sectors tend to continue lower"])


def strat_prev_day_low_breakdown(s):
    # B634 sweep: positive symmetric below_vwap (B634 producer)
    fires = (s.get("below_prev_low") and
             s.get("vol_spike_15x") and
             s.get("below_vwap"))
    return _strat(fires, "short", "breakout",
        ["below_prev_low", "vol_spike_1.5x", "below_vwap"],
        ["Price broke below previous day's low  -  failed to hold support",
         "Volume confirms sellers in control",
         "Below VWAP  -  intraday sellers dominating"])


# --- Confluence shorts (2) ---

def strat_camarilla_rsi_obv_short(s):
    # B628 F1: obv_bullish -> obv_bearish (positive symmetric).
    # B629 F1 cmf-family sweep: cmf_positive -> cmf_negative.
    # Both silent-gaps now closed.
    fires = (s.get("near_cam_r3") and
             s.get("rsi_14", 50) > 65 and
             s.get("obv_bearish") and
             s.get("cmf_negative"))
    return _strat(fires, "short", "confluence",
        ["near_cam_r3", "rsi_14>65", "obv_bearish", "cmf_negative"],
        ["Camarilla R3 - strongest institutional resistance",
         "RSI-14 overbought above 65",
         "OBV bearish + CMF negative - four systems confirming short (B628 F1 + B629 F1)"])


def strat_cpr_narrow_momentum_short(s):
    # B630 sweep: positive symmetric macd_12_26_9_bearish (B609 producer)
    fires = (s.get("cpr_narrow") and
             s.get("below_cpr") and
             s.get("rsi_14", 50) < 50 and
             s.get("macd_12_26_9_bearish"))
    return _strat(fires, "short", "confluence",
        ["cpr_narrow", "below_cpr", "rsi_14<50", "macd_bearish"],
        ["Narrow CPR  -  directional day expected",
         "Price below CPR  -  bearish professional bias",
         "RSI<50 and MACD bearish  -  four signals confirming bearish day"])


# -----------------------------------------------------------------------------
# BREAK-AND-RETEST STRATEGIES  -  BUG-111 Layer 3 additions
# DEC-355 through DEC-362 chart pattern spec (config.py CHART_PATTERN_STRATEGIES)
# mandates break+retest entry trigger. These 5 strategies implement that requirement
# for the core breakout categories (Breakout + Pivot + Confluence).
# -----------------------------------------------------------------------------

def strat_dc20_break_retest(s):
    """BUG-111: DC20 break-and-retest -- breakout above 20-day channel confirmed by retest hold.

    Batch 682 (2026-06-10 owner-approved thesis-implementation alignment per
    B680 self-critique CC-A): swapped `vol_spike_15x` -> `vol_below_avg` on
    BOTH directions. Pre-B682 the strategy gated on HIGH volume at the
    retest bar -- which contradicts Bulkowski 2005 *Encyclopedia of Chart
    Patterns* retest absorption thesis: retests form on LOWER volume than
    the initial breakout bar (supply has been absorbed; sellers are
    exhausted; the retest is a low-conviction probe). High-volume retests
    are not retests in the Bulkowski sense -- they are either (a) initial
    breakouts mis-classified or (b) failed retests with renewed selling
    pressure. The B682 swap aligns strategy logic with cited methodology.

    Cross-cluster note: this aligns BR-8 (`strat_dc20_break_retest`) with
    the Bulkowski thesis consistently applied across BR-2/BR-4 (52w
    pullback) + BR-5/BR-6 (52w break-retest) + BR-7 (break_retest_volume)
    + BR-12/BR-13 (donchian break-retest) -- all of which use vol_below_avg
    per Bulkowski. Pre-B682 BR-8 was the ODD ONE OUT in the breakout
    cluster's retest-family.

    LONG: resistance_break_retest + vol_below_avg + adx_trending
    SHORT: support_break_retest + vol_below_avg + adx_trending
    """
    fl = (s.get("resistance_break_retest") and s.get("vol_below_avg") and s.get("adx_trending"))
    fs = (s.get("support_break_retest") and s.get("vol_below_avg") and s.get("adx_trending"))
    return _strat3(fl, fs, "breakout",
        ["resistance_break_retest", "vol_below_avg", "adx_trending"],
        ["support_break_retest", "vol_below_avg", "adx_trending"],
        "DC20 break-and-retest: channel high broken, retested on lower volume (Bulkowski 2005), ADX trending",
        "DC20 breakdown-and-retest: channel low broken, retested on lower volume (Bulkowski 2005), ADX trending")


def strat_r1_break_retest(s):
    """BUG-111 (Batch 162) ORIGINAL: documented as Pivot R1 break-and-
    retest but consumed DC20-anchored resistance_break_retest (same
    name-vs-implementation bug pattern as strat_52wh_break_retest,
    fixed in B605). R1 is a 1-day level recomputed daily from prior
    day's H/L/C; the DC20-max-CLOSE bore no relationship to any
    specific R1 value. The above_r1 gate was a same-day position
    filter, not a "broken R1 acting as support" check.

    Batch 606 (2026-06-06 owner-directed F1 bug fix per CHECKLIST #105
    deep-read; full walk + a+b+d+e+i applied):

      F1 - Replaced resistance_break_retest / support_break_retest
        with NEW r1_break_retest_long / s1_break_retest_short
        primitives (compute_pivot_break_retest_signals). Now the retest
        event is anchored on the specific R1/S1 value computed at the
        break-bar B (from bar B-1's H/L/C using standard pivot formula),
        not on the unrelated DC20-max-CLOSE.
      (a) Added close_above_open (LONG) / close_below_open (SHORT)
          (B589-family bullish/bearish bar).
      (b) Added close_in_top_40pct_of_range (LONG) /
          close_in_bottom_40pct_of_range (SHORT) (B589-family).
      (d) Added vol_below_avg (Bulkowski canonical retest = supply-
          absorption on LOWER volume; same as B594/B596/B603/B605).
      (e) Added above_avwap_20low (LONG) / NOT above_avwap_20high
          (SHORT) (Brian Shannon 2022 AVWAP; same family as
          B597/B598/B600/B601/B603/B605).
      (i) Regime affinity: Batch 291 direction-aware default
          (LONG -> {bull, neutral}; SHORT -> {bear, crisis, neutral}).

    NOTE: above_r1 / below_s1 gates PRESERVED. They check today's
    close vs today's R1/S1 (intraday position context) - distinct
    from the F1 anchored-retest detection. Together they require
    BOTH a historical R1 break-retest event AND today's close to be
    on the correct side of today's R1.

    Post-B606 7-gate set per direction:
      LONG:  r1_break_retest_long + above_r1 + macd_12_26_9_bullish +
             close_above_open + close_in_top_40pct_of_range +
             vol_below_avg + above_avwap_20low
      SHORT: s1_break_retest_short + below_s1 + NOT macd_bullish +
             close_below_open + close_in_bottom_40pct_of_range +
             vol_below_avg + NOT above_avwap_20high
    """
    fl = (s.get("r1_break_retest_long")
          and s.get("above_r1")
          and s.get("macd_12_26_9_bullish")
          and s.get("close_above_open")
          and s.get("close_in_top_40pct_of_range")
          and s.get("vol_below_avg")
          and s.get("above_avwap_20low"))
    # B612 refactor: NOT s.get(macd_bullish) -> positive macd_bearish (B609);
    # NOT s.get(above_avwap_20high, True) -> positive below_avwap_20high (B612).
    fs = (s.get("s1_break_retest_short")
          and s.get("below_s1")
          and s.get("macd_12_26_9_bearish")
          and s.get("close_below_open")
          and s.get("close_in_bottom_40pct_of_range")
          and s.get("vol_below_avg")
          and s.get("below_avwap_20high"))
    return _strat3(fl, fs, "pivot",
        ["r1_break_retest_long", "above_r1", "macd_12_26_9_bullish",
         "close_above_open", "close_in_top_40pct_of_range",
         "vol_below_avg", "above_avwap_20low"],
        ["s1_break_retest_short", "below_s1", "macd_12_26_9_bearish",
         "close_below_open", "close_in_bottom_40pct_of_range",
         "vol_below_avg", "below_avwap_20high"],
        ["R1 broken 2-8 bars ago + retested within 1.5*ATR + still above (anchored on the SPECIFIC R1 at the break-bar)",
         "Today's close above today's R1 (intraday position)",
         "MACD positive (momentum)",
         "Bullish bar (close above open)",
         "Strong close (top 40% of range)",
         "Volume below 20d avg (Bulkowski retest = supply absorption)",
         "Above 20d swing-low AVWAP (Brian Shannon)"],
        ["S1 broken 2-8 bars ago + retested within 1.5*ATR + still below (anchored on the SPECIFIC S1 at the break-bar)",
         "Today's close below today's S1 (intraday position)",
         "MACD negative",
         "Bearish bar (close below open)",
         "Strong close (bottom 40% of range)",
         "Volume below 20d avg (Bulkowski retest characteristic)",
         "Below 20d swing-high AVWAP - recent rally given back"])


def strat_52wh_break_retest(s):
    """BUG-111 (Batch 162) ORIGINAL: documented as 52-week high break-and-
    retest but consumed DC20-anchored resistance_break_retest (the only
    retest primitive at the time). Strategy name + docstring lied about
    what it detected; near_52w_high was just a proximity filter, not a
    tie between the break event and the year_high.

    Batch 605 (2026-06-06 owner-directed F1 bug fix per CHECKLIST #105
    deep-read; full walk + a+b+c+g+e applied):

      F1 - Replaced resistance_break_retest with NEW
        year_high_break_retest_long primitive (compute_52w_break_retest
        _signals). Now the retest event is anchored on year_high (prior-
        252d max-HIGH excluding today) as the strategy name promises.
      (a) Added close_above_open + close_in_top_40pct_of_range
          (B589-family bullish-bar + strong-close).
      (b) Added vol_below_avg (Bulkowski canonical retest = supply-
          absorption on LOWER volume).
      (c) Added above_avwap_20low (Brian Shannon 2022 AVWAP from
          recent 20-day swing low; consistent with B597/B598/B600/B603
          AVWAP family).
      (e) Regime affinity: Batch 291 direction-aware default (LONG ->
          {bull, neutral}).

    Post-B605 7-gate set:
      year_high_break_retest_long + near_52w_high + price_above_ema_200
      + close_above_open + close_in_top_40pct_of_range + vol_below_avg
      + above_avwap_20low

    Academic backing:
      - George-Hwang 2004 JF: 52w-high attracts sustained buying.
      - Bulkowski 2005: post-break retest is canonical confirmation;
        retest forms on LOWER volume (supply absorption).
    """
    fl = (s.get("year_high_break_retest_long")
          and s.get("near_52w_high")
          and s.get("price_above_ema_200")
          and s.get("close_above_open")
          and s.get("close_in_top_40pct_of_range")
          and s.get("vol_below_avg")
          and s.get("above_avwap_20low"))
    return _strat(fl, "long", "breakout",
        ["year_high_break_retest_long", "near_52w_high",
         "price_above_ema_200", "close_above_open",
         "close_in_top_40pct_of_range", "vol_below_avg",
         "above_avwap_20low"],
        ["52-week high broken 2-8 bars ago + retested within 1.5*ATR + still above",
         "Today's close within 2% of 52-week high",
         "Above 200-day EMA (trend filter)",
         "Bullish bar (close above open)",
         "Strong close (top 40% of range)",
         "Volume below 20d avg (Bulkowski retest = supply absorption)",
         "Above 20d swing-low AVWAP (Brian Shannon)"])


def strat_52wl_break_retest_short(s):
    """Batch 605 (2026-06-06 owner-directed Class 7 NEW): symmetric
    inverse of strat_52wh_break_retest. 52-week LOW breakdown-and-
    retest -- historical support confirmed as resistance below 200 EMA.

    Mirror 7-gate structure:
      year_low_break_retest_short + near_52w_low + NOT price_above
      _ema_200 + close_below_open + close_in_bottom_40pct_of_range +
      vol_below_avg + NOT above_avwap_20high

    Producer signals: year_low_break_retest_short from B605 NEW
    compute_52w_break_retest_signals; all others pre-existing.

    Regime affinity: Batch 291 direction-aware default (SHORT ->
    {bear, crisis, neutral}).
    """
    # B616 (2026-06-07 owner-directed LOW-priority refactor): swapped
    # `not s.get("price_above_ema_200", False)` -> `below_ema_200`
    # (B609 producer) and `not s.get("above_avwap_20high", True)` ->
    # `below_avwap_20high` (B612 producer) for positive symmetric
    # signals per feedback_never_use_NOT_s_get_pattern. Behavior
    # preserved (default=True was functionally safe; this hardens it
    # against future producer edits).
    fs = (s.get("year_low_break_retest_short")
          and s.get("near_52w_low")
          and s.get("below_ema_200", False)
          and s.get("close_below_open")
          and s.get("close_in_bottom_40pct_of_range")
          and s.get("vol_below_avg")
          and s.get("below_avwap_20high", False))
    return _strat(fs, "short", "breakout",
        ["year_low_break_retest_short", "near_52w_low",
         "below_ema_200", "close_below_open",
         "close_in_bottom_40pct_of_range", "vol_below_avg",
         "below_avwap_20high"],
        ["52-week low broken 2-8 bars ago + retested within 1.5*ATR + still below",
         "Today's close within 2% of 52-week low",
         "Below 200-day EMA (bearish trend filter)",
         "Bearish bar (close below open)",
         "Strong close (bottom 40% of range)",
         "Volume below 20d avg (Bulkowski retest = lower volume)",
         "Below 20d swing-high AVWAP - recent rally given back"])


def strat_break_retest_volume(s):
    """BUG-111: Break-and-retest with OBV-vs-20-bar-MA flow confirmation
    + Bulkowski retest dry-up volume.

    Batch 617 (2026-06-07 owner-directed external-AI critique re-fix on
    B608 walk):

    The B608 walk landed two real fixes (F1 regime; F2 silent-gap) but
    missed three issues the critique surfaced:

      (1) B320 deleted vol_spike_2x citing Bulkowski - but Bulkowski's
          rule is HIGH volume on the BREAK + low volume on the retest.
          B320 threw away the breakout-bar volume half. B608 added
          vol_below_avg (the retest dry-up half) but still has no
          breakout-bar volume confirmation. The producer signal
          resistance_break_retest fires on TODAY's still-holding-above
          bar (2-8 bars post-break) - the breakout-bar volume cannot
          be re-captured via a current-bar gate without a new producer
          signal. B617 leaves the breakout-bar volume gap acknowledged
          (recategorization deferred) and switches the FLOW gate to
          a cleaner OBV signal.

      (2) obv_rising = OBV[-1] > OBV[-5] is a 5-BAR TREND window, not
          a "bounce-bar" confirmation. The label and docstring claimed
          bounce-bar timing but the producer is a multi-bar window -
          a soft thesis-vs-impl mismatch.

      (3) The 5-bar OBV window at the retest bar still contains the
          breakout bar's volume - obv_rising reads "rising" largely
          because the breakout day hasn't aged out, not because of
          accumulation on the dip. Near-tautological on valid setups.

    B617 fixes (2) + (3) by switching to obv_bullish (OBV[-1] > 20-bar
    MA - longer baseline, less contaminated by the in-window breakout
    bar) for LONG and the new symmetric obv_bearish for SHORT.

    Fix (1) acknowledged but deferred: restoring breakout-bar volume
    requires a new producer signal (break_retest_breakout_bar_vol) that
    captures the original breakout bar's volume relative to its 20-day
    average at break-time. Out of scope for this re-fix; queued.

    Post-B617 4-gate set per direction:
      LONG:  resistance_break_retest + obv_bullish + close_above_open
             + vol_below_avg
      SHORT: support_break_retest + obv_bearish + close_below_open
             + vol_below_avg

    Lineage of prior walk batches preserved (B320 / B608 / B617 history
    in code commit log).
    """
    fl = (s.get("resistance_break_retest")
          and s.get("obv_bullish")           # B617: switched from obv_rising
          and s.get("close_above_open")
          and s.get("vol_below_avg"))
    fs = (s.get("support_break_retest")
          and s.get("obv_bearish")           # B617: switched from obv_falling
          and s.get("close_below_open")
          and s.get("vol_below_avg"))
    return _strat3(fl, fs, "breakout",
        ["resistance_break_retest", "obv_bullish", "close_above_open",
         "vol_below_avg"],
        ["support_break_retest", "obv_bearish", "close_below_open",
         "vol_below_avg"],
        ["Break-and-retest + OBV above 20-bar MA: institutional accumulation flow (B617 cleaner baseline)",
         "Bullish bar (close above open)",
         "Volume below 20d avg (Bulkowski retest characteristic)"],
        ["Breakdown-and-retest + OBV below 20-bar MA: institutional distribution flow (B617 symmetric)",
         "Bearish bar (close below open)",
         "Volume below 20d avg (Bulkowski retest characteristic)"])


def strat_break_retest_confluence(s):
    """BUG-111: Break-and-retest with multi-indicator confluence confirmation.

    Batch 609 (2026-06-07 owner-directed Stage 4 walk per CHECKLIST #105
    deep-read; F1 + F2 + a + d + i applied; same bug pattern as B608):

      F1 - regime affinity bug fixed. Strategy is DUAL but
        STRATEGY_REGIME_AFFINITY had explicit {bull} entry that
        capped BOTH directions to bull-only since the Batch 271
        mass-edit. LONG over-restricted; SHORT mis-regimed (firing
        in bull = wrong for short bias). Fixed by removing the entry;
        falls back to Batch 291 direction-aware default (LONG ->
        {bull, neutral}; SHORT -> {bear, crisis, neutral}).
      F2 - silent-gap bugs fixed (THREE gates this time). SHORT side
        previously used `not s.get(macd_12_26_9_bullish)`,
        `not s.get(price_above_ema_20)`, `not s.get(price_above_ema
        _50)` - each auto-passed when the respective key was missing
        (None is falsy; not None = True). Labels said macd_bearish /
        below_ema_20 / below_ema_50 but producer never emitted them.
        B609 F2 added macd_12_26_9_bearish to compute_macd +
        below_ema_20 / below_ema_50 to compute_ema_sma; SHORT consumes
        them explicitly.
      (a) Added close_above_open (LONG) / close_below_open (SHORT)
        per B589-family standardization.
      (d) Added vol_below_avg per Bulkowski canonical retest =
        supply-absorption on LOWER volume (consistent with B594/B596/
        B603/B605/B606/B607/B608 retest family).
      (i) Regime: Batch 291 direction-aware default (post-F1).

    Skipped: (b) strong-close 40pct / (c) B594 strong variants /
    (e) AVWAP - strategy already has 4 confluence signals; adding
    more on top would over-tighten.

    Post-B609 6-gate set per direction:
      LONG:  resistance_break_retest + macd_12_26_9_bullish +
             price_above_ema_20 + price_above_ema_50 + close_above_open
             + vol_below_avg
      SHORT: support_break_retest + macd_12_26_9_bearish (explicit) +
             below_ema_20 (explicit) + below_ema_50 (explicit) +
             close_below_open + vol_below_avg
    """
    fl = (s.get("resistance_break_retest")
          and s.get("macd_12_26_9_bullish")
          and s.get("price_above_ema_20")
          and s.get("price_above_ema_50")
          and s.get("close_above_open")
          and s.get("vol_below_avg"))
    fs = (s.get("support_break_retest")
          and s.get("macd_12_26_9_bearish")
          and s.get("below_ema_20")
          and s.get("below_ema_50")
          and s.get("close_below_open")
          and s.get("vol_below_avg"))
    return _strat3(fl, fs, "confluence",
        ["resistance_break_retest", "macd_12_26_9_bullish",
         "price_above_ema_20", "price_above_ema_50",
         "close_above_open", "vol_below_avg"],
        ["support_break_retest", "macd_12_26_9_bearish",
         "below_ema_20", "below_ema_50",
         "close_below_open", "vol_below_avg"],
        ["Break-and-retest confluence: MACD + dual EMA confirms breakout continuation",
         "Bullish bar (close above open)",
         "Volume below 20d avg (Bulkowski retest characteristic)"],
        ["Breakdown-and-retest confluence: MACD + dual EMA (explicit bearish signals post-B609 F2)",
         "Bearish bar (close below open)",
         "Volume below 20d avg (Bulkowski retest characteristic)"])


# -----------------------------------------------------------------------------
# STRATEGY REGISTRY  -  Layer 1 baseline 60 + currently-implemented dedicated shorts
# (full layered roster ~108-133 classes per CANONICAL_FACTS.md F-002; layered
#  roster: Layer 1 baseline 60 + Layer 2 Phase 0.D ICT/Earnings/Calendar + Layer 2D
#  form-derived ICT + Layer 3 Pass 52 RESOLVED chart-pattern/categories + Layer 4
#  PENDING strategy-additive). Run `len(ALL_STRATEGIES)` for current count.
# -----------------------------------------------------------------------------

def strat_orb_stocks_in_play_long(s):
    """Batch 211 (ORB stocks-in-play 2026-05-17 owner-approved research review).
    Opening Range Breakout for "stocks in play" per Zarattini-Barbon-Aziz
    (2024) SSRN 4729284 "A Profitable Day Trading Strategy For The U.S.
    Equity Market". Paper documents +1,600% return / Sharpe 2.81 on Top-20
    high-volume stocks-in-play with intraday 5-min ORB.

    DAILY-BAR APPROXIMATION: true intraday ORB requires 5-min bars (this
    engine operates on daily). Daily proxy uses:
      - "in-play" filter: gap_up_pct > +2% (vs prev close) - market is
        reacting to overnight catalyst, matching Zarattini's stocks-in-play
        criteria
      - "ORB high break" proxy: close > today's open (close-above-open
        is the daily-bar analogue of breaking the opening range high)
      - Volume confirmation: 2x ADV(20) (Zarattini emphasizes institutional
        participation as a primary edge)
      - 200-EMA regime gate (long-only buy bias)
    """
    fires = (
        s.get("gap_up_2pct", False)
        and s.get("close_above_open", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_200", False)
    )
    gap = s.get("gap_up_pct", 0.0)
    return _strat(fires, "long", "orb",
        ["gap_up_pct>2", "close_above_open", "vol_spike_2x", "price_above_ema_200"],
        [f"Gap up +{gap:.1f}% - in-play catalyst",
         "Close above open - intraday momentum positive",
         "Volume 2x ADV(20) - institutional participation",
         "Above 200 EMA (regime gate)"])


def strat_orb_stocks_in_play_short(s):
    """Batch 211: Symmetric short for gap-down stocks-in-play.
    Daily-bar proxy: gap_dn_pct > 2%, close < open, 2x volume, below
    200-EMA regime gate."""
    fires = (
        s.get("gap_dn_2pct", False)
        and s.get("close_below_open", False)
        and s.get("vol_spike_2x", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    gap = s.get("gap_dn_pct", 0.0)
    return _strat(fires, "short", "orb",
        ["gap_dn_pct>2", "close_below_open", "vol_spike_2x", "price_below_ema_200"],
        [f"Gap down -{gap:.1f}% - in-play catalyst",
         "Close below open - intraday momentum negative",
         "Volume 2x ADV(20) - institutional participation",
         "Below 200 EMA (bear regime confirmation)"])


def strat_pre_fomc_long_sleeve(s):
    """Batch 224 (pre-FOMC drift 2026-05-18 owner-approved research review).
    Lucca-Moench 2015 JF "The Pre-FOMC Announcement Drift": +50bps/yr
    alpha concentrating in 24h preceding FOMC announcements. Refined
    by Cieslak-Pang 2024 conditional on yield-curve slope.

    Reverses Batch 191 FOMC suppression for the LONG sleeve via
    STRATEGIES_BYPASS_EVENT_SUPPRESSION (config.py). Long entry on the
    pre-FOMC day (d-1) when broad bullish context holds.
    """
    fires = (
        s.get("pre_fomc_d1", False)
        and s.get("price_above_ema_200", False)
    )
    days = s.get("days_until_fomc", -1)
    return _strat(fires, "long", "event_driven",
        ["pre_fomc_d1", "price_above_ema_200"],
        [f"Pre-FOMC day-1 (FOMC in {days} day) - Lucca-Moench drift",
         "Above 200 EMA - bullish backdrop"])


def strat_pre_fomc_quality_momentum_long(s):
    """Batch 224: Higher-conviction pre-FOMC variant - require top-decile
    cross-sectional momentum (Goyal-Jegadeesh 2024) on top of pre-FOMC
    timing. Combines macro-event drift with quality-momentum selection."""
    fires = (
        s.get("pre_fomc_d1", False)
        and s.get("xs_momentum_top_decile", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "event_driven",
        ["pre_fomc_d1", "xs_momentum_top_decile", "price_above_ema_200"],
        ["Pre-FOMC day-1 (Lucca-Moench drift)",
         "Top-decile cross-sectional 12-1 momentum (quality momentum)",
         "Above 200 EMA - regime gate"])


# -----------------------------------------------------------------------------
# strat_buyback_8k_recent_long DELETED Batch 682 (2026-06-10 owner-approved)
# -----------------------------------------------------------------------------
# DELETION RATIONALE per B680 self-critique CC-B + owner approval 2026-06-10:
#
# F-population-mixing CONFIRMED defect: strategy fired on ANY 8-K type
# (Items 1.01-9.01) without item-level text parsing -- mixing M&A target
# (Item 1.01; B673 reviewer flagged as feasibility failure SM-4), buyback
# (Item 8.01), Reg FD (Item 7.01), officer change (Item 5.02), Reg G
# (Item 7.01). The original docstring acknowledged this as "placeholder/
# proxy" with "true buyback parsing deferred to a future batch with 8-K
# text extraction" -- but the proxy population includes the SM-4
# M&A-target population that the B673 external reviewer flagged as
# feasibility-failure (uncapturable via next-day-open after announcement
# gap).
#
# Per `feedback_audit_recommendations_against_existing_directives` + B673
# SM-4 reviewer disposition: continuing to fire EV-7 on M&A target 8-K
# Item 1.01 filings reproduces the feasibility-failure SM-4 was
# reclassified for. Pre-cube deletion avoids contaminating cube data
# with the same uncapturable population.
#
# B660 early-finding (visible at 17:47:07 on 2026-06-10): EV-7 actual
# fire count = 0 long / 0 short / 0 avoid universe-wide across 6 years
# x 503 tickers -- empirical confirmation that even the broad 8-K-any-
# type proxy doesn't fire in the engine's gating context (or the producer
# signal `recent_8k_filed` may itself be dead -- separate audit).
#
# Future work: if buyback alpha matters, ship a NEW strategy with proper
# 8-K Item 8.01 text parsing per Manconi-Peyer-Vermaelen 2019 JFQA
# specification -- different from the deleted-as-proxy EV-7.
#
# No downstream code references; ALL_STRATEGIES registry entry also removed.
# -----------------------------------------------------------------------------


def strat_insider_cluster_long(s):
    """Batch 222 (insider clusters 2026-05-18 owner-approved). Cluster of
    insider buys (>=2 unique insiders, open-market purchases, last 30
    days) -> documented ~7pct 12-month alpha.

    Source: Cohen-Malloy-Pomorski 2012 JF "Decoding Inside Information";
    Akbas-Jiang-Koch 2024 RFS update confirming post-publication.
    """
    fires = (
        s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", False)
    )
    n = s.get("insider_unique_buyers_30d", 0)
    return _strat(fires, "long", "event_driven",
        ["insider_cluster_active", "price_above_ema_200"],
        [f"Insider buying cluster: {n} unique insiders bought "
         f"open-market in last 30 days",
         "Above 200 EMA (regime gate)"])


def strat_insider_cluster_with_director_long(s):
    """Batch 222: Higher-conviction insider variant - cluster requires
    at least 1 DIRECTOR (board member) as a buyer. Director purchases
    are documented as having higher signal value than purely-officer
    transactions (Lakonishok-Lee 2001 RFS)."""
    fires = (
        s.get("insider_cluster_active", False)
        and s.get("insider_director_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)
    )
    n = s.get("insider_unique_buyers_30d", 0)
    n_dir = s.get("insider_director_buyers_30d", 0)
    return _strat(fires, "long", "event_driven",
        ["insider_cluster_active", "insider_director>=1",
         "price_above_ema_200"],
        [f"Insider cluster: {n} unique buyers incl. {n_dir} director(s)",
         "Above 200 EMA (regime gate)"])


def strat_xs_quality_top_quintile_long(s):
    """Batch 222 (quality factor 2026-05-18). Long top-quintile gross
    profitability + 200-EMA gate. Source: Novy-Marx 2013 JFE; Asness-
    Frazzini-Pedersen 2019 RAS 'Quality Minus Junk'. Documented
    Sharpe 0.8-1.1 standalone; combined with momentum reaches 1.4."""
    fires = (
        s.get("xs_quality_top_quintile", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "factor",
        ["xs_quality_top_quintile", "price_above_ema_200"],
        ["Top quintile gross profitability (Novy-Marx 2013)",
         "Above 200 EMA (regime gate)"])


def strat_xs_momentum_quality_combined(s):
    """Batch 222: Quality-momentum joint signal. Top-decile 12-1
    momentum AND top-quintile gross profitability. Asness-Moskowitz-
    Pedersen 2013 JF documents Sharpe approaches 1.4 in this
    combination. Higher conviction than either factor alone."""
    fires = (
        s.get("xs_momentum_top_decile", False)
        and s.get("xs_quality_top_quintile", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "factor",
        ["xs_momentum_top_decile", "xs_quality_top_quintile",
         "price_above_ema_200"],
        ["Top-decile 12-1 momentum",
         "Top-quintile gross profitability",
         "Above 200 EMA - quality-momentum joint signal"])


def strat_pead_with_insider_confirmation_long(s):
    """Batch 222: PEAD positive surprise + concurrent insider buying
    cluster = high-conviction post-earnings drift. Insider activity is
    independent confirmation that the earnings move is fundamental
    rather than noise."""
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
        and s.get("insider_cluster_active", False)
    )
    return _strat(fires, "long", "event_driven",
        ["within_pead_window", "pead_positive_surprise",
         "insider_cluster_active"],
        ["Within PEAD drift window (<=60d post-earnings)",
         "Positive earnings surprise (YoY+ AND ann-ret>+2pct)",
         "Concurrent insider buying cluster - independent confirmation"])


def strat_xs_momentum_top_decile(s):
    """Batch 220 (cross-sectional factor 2026-05-18 owner-approved research
    review). Long top decile of 12-1 momentum (Moskowitz-Ooi-Pedersen 2012
    JFE; refreshed Goyal-Jegadeesh-Subrahmanyam 2024 RFS - Sharpe 1.2-1.6
    net of costs 1985-2023). Single highest-ROI addition per the review.

    Filters: IVOL filter (Ang-Hodrick-Xing-Zhang 2006 - avoid top IVOL
    decile) + MAX filter (Bali-Cakici-Whitelaw 2011 - avoid top MAX decile)
    + 200-EMA regime gate."""
    fires = (
        s.get("xs_momentum_top_decile", False)
        and s.get("xs_avoid_high_ivol", True)
        and s.get("xs_avoid_high_max", True)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "factor",
        ["xs_momentum_top_decile", "xs_avoid_high_ivol",
         "xs_avoid_high_max", "price_above_ema_200"],
        ["Cross-sectional 12-1 momentum top decile",
         "Not in top IVOL decile (Ang-Hodrick-Xing-Zhang filter)",
         "Not in top MAX-anomaly decile (Bali-Cakici-Whitelaw filter)",
         "Above 200 EMA (regime gate)"])


def strat_xs_momentum_bottom_decile_short(s):
    """Batch 220: Symmetric short on bottom-decile 12-1 momentum +
    below-200-EMA regime gate."""
    fires = (
        s.get("xs_momentum_bottom_decile", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "factor",
        ["xs_momentum_bottom_decile", "price_below_ema_200"],
        ["Cross-sectional 12-1 momentum bottom decile",
         "Below 200 EMA (bear regime)"])


def strat_xs_low_beta_long(s):
    """Batch 220: Betting-against-beta (Frazzini-Pedersen 2014 JFE;
    Blitz-van Vliet 2024 JPM update). Long bottom-2-decile beta names.
    Low-beta names systematically outperform on a risk-adjusted basis.

    Batch 358 (2026-05-25 owner-approved cell-audit Bucket C Option A):
    REMOVED the price_above_ema_200 bull-regime gate. The published BAB
    Sharpe is across the full sample (not bull-only). Cell audit data
    showed (xs_low_beta_long x atr_trail_1x in neutral regime) lost
    -6.22% mean PnL on n=30 - the strategy was firing in neutral regime
    when the EMA gate let through (low-beta absolute returns lag in
    strong-bull regimes per BAB literature; bear / neutral is where
    absolute alpha is captured). Removing the gate aligns the
    implementation with the published full-sample edge. See
    PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md Bucket C."""
    fires = (
        s.get("xs_low_beta_decile", False)
        and s.get("xs_avoid_high_ivol", True)
    )
    return _strat(fires, "long", "factor",
        ["xs_low_beta_decile", "xs_avoid_high_ivol"],
        ["Bottom-2-decile beta vs SPY (BAB tilt)",
         "Not high-IVOL"])


def strat_xs_combined_momentum_low_ivol(s):
    """Batch 220: Combined factor signal - top-decile momentum AND
    bottom-quintile IVOL (high quality momentum). Asness-Moskowitz-
    Pedersen 2013 JF "Value and Momentum Everywhere" documented Sharpe
    approaches 1.4 when momentum combined with quality/low-vol filter."""
    fires = (
        s.get("xs_momentum_top_decile", False)
        and s.get("xs_ivol_decile", 5) <= 3   # bottom 30% IVOL = high quality
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "factor",
        ["xs_momentum_top_decile", "xs_ivol_decile<=3",
         "price_above_ema_200"],
        ["Top-decile 12-1 momentum",
         "Bottom-quintile IVOL (high quality momentum)",
         "Above 200 EMA - regime gate"])


def strat_po3_bullish(s):
    """Batch 217 (PO3 + multi-TF 2026-05-18 owner-approved). Power of 3
    bullish daily candle: open near top, manipulation sweeps below
    prior-day low, distribution closes in upper third of range. ICT
    pattern marking institutional accumulation after a stop hunt."""
    fires = (
        s.get("po3_bullish", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "po3",
        ["po3_bullish", "price_above_ema_200"],
        ["Bullish PO3 daily candle: sweep below prior low + close upper third",
         "Above 200 EMA (regime gate)"])


def strat_po3_bearish(s):
    """Batch 217: Symmetric bearish PO3 daily."""
    fires = (
        s.get("po3_bearish", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "po3",
        ["po3_bearish", "price_below_ema_200"],
        ["Bearish PO3 daily candle: sweep above prior high + close lower third",
         "Below 200 EMA (bear regime)"])


def strat_po3_htf_aligned_long(s):
    """Batch 217: PO3 bullish + weekly bias bullish - high-conviction
    long with higher-timeframe directional alignment."""
    fires = (
        s.get("po3_bullish", False)
        and s.get("weekly_bias_bull", False)
    )
    return _strat(fires, "long", "po3",
        ["po3_bullish", "weekly_bias_bull"],
        ["Bullish PO3 daily candle",
         "Weekly bias bullish - higher-TF alignment"])


def strat_po3_htf_aligned_short(s):
    """Batch 217: Symmetric for bearish PO3 with weekly bear bias."""
    fires = (
        s.get("po3_bearish", False)
        and s.get("weekly_bias_bear", False)
    )
    return _strat(fires, "short", "po3",
        ["po3_bearish", "weekly_bias_bear"],
        ["Bearish PO3 daily candle",
         "Weekly bias bearish - higher-TF alignment"])


def strat_htf_aligned_breakout_long(s):
    """Batch 217: Multi-timeframe-aligned daily breakout. Daily breakout
    above prev-day high + weekly + monthly biases both bullish. Triple-
    timeframe confluence per Brian Shannon discipline."""
    fires = (
        s.get("above_prev_high", False)
        and s.get("vol_spike_15x", False)
        and s.get("htf_aligned_bull", False)
    )
    return _strat(fires, "long", "multi_timeframe",
        ["above_prev_high", "vol_spike_1.5x", "htf_aligned_bull"],
        ["Price broke above previous day's high",
         "Volume 1.5x ADV(20) - institutional participation",
         "Weekly + Monthly bias both bullish - HTF aligned"])


def strat_htf_aligned_breakout_short(s):
    """Batch 217: Symmetric short on prev-day low break + HTF bearish."""
    fires = (
        s.get("below_prev_low", False)
        and s.get("vol_spike_15x", False)
        and s.get("htf_aligned_bear", False)
    )
    return _strat(fires, "short", "multi_timeframe",
        ["below_prev_low", "vol_spike_1.5x", "htf_aligned_bear"],
        ["Price broke below previous day's low",
         "Volume 1.5x ADV(20) - institutional participation",
         "Weekly + Monthly bias both bearish - HTF aligned"])


def strat_weekly_bias_pullback_long(s):
    """Batch 217: Weekly bull bias + daily pullback (RSI(14)<40) +
    bullish reversal candle = high-quality long. Trades WITH the weekly
    trend after a daily oversold pullback."""
    fires = (
        s.get("weekly_bias_bull", False)
        and s.get("rsi_14", 50) < 40
        and (s.get("hammer") or s.get("bullish_engulfing"))
    )
    return _strat(fires, "long", "multi_timeframe",
        ["weekly_bias_bull", "rsi_14<40", "bullish_reversal_candle"],
        ["Weekly bias bullish - trade WITH weekly trend",
         "Daily RSI<40 - oversold pullback",
         "Bullish reversal candle (hammer or engulfing)"])


def strat_weekly_bias_pullback_short(s):
    """Batch 217: Symmetric weekly bear bias + daily rally pullback."""
    fires = (
        s.get("weekly_bias_bear", False)
        and s.get("rsi_14", 50) > 60
        and (s.get("shooting_star") or s.get("bearish_engulfing"))
    )
    return _strat(fires, "short", "multi_timeframe",
        ["weekly_bias_bear", "rsi_14>60", "bearish_reversal_candle"],
        ["Weekly bias bearish - trade WITH weekly trend",
         "Daily RSI>60 - overbought rally",
         "Bearish reversal candle (shooting star or engulfing)"])


def strat_monthly_bias_momentum_long(s):
    """Batch 217: Monthly bull bias + positive 6-month momentum + daily
    breakout = swing-trade long with structural multi-TF backing."""
    fires = (
        s.get("monthly_bias_bull", False)
        and s.get("monthly_momentum_pos", False)
        and s.get("above_prev_high", False)
    )
    return _strat(fires, "long", "multi_timeframe",
        ["monthly_bias_bull", "monthly_momentum_pos", "above_prev_high"],
        ["Monthly bias bullish + positive 6-month momentum",
         "Daily breakout above previous high",
         "Triple-TF structural confluence"])


def strat_smc_fvg_retest_long(s):
    """Batch 216 (SMC expansion 2026-05-18 owner-approved): price returned
    to an unmitigated bullish Fair Value Gap zone -> long entry.
    FVG = institutional 3-bar imbalance; retests of bullish FVGs are
    canonical ICT continuation entries."""
    fires = (
        s.get("smc_fvg_retest_long_zone", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_fvg_retest_long_zone", "price_above_ema_200"],
        ["Price inside unmitigated bullish Fair Value Gap zone",
         "Above 200 EMA (regime gate)"])


def strat_smc_fvg_retest_short(s):
    """Batch 216: bearish FVG retest -> short entry. Symmetric to long."""
    fires = (
        s.get("smc_fvg_retest_short_zone", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "smc",
        ["smc_fvg_retest_short_zone", "price_below_ema_200"],
        ["Price inside unmitigated bearish Fair Value Gap zone",
         "Below 200 EMA (bear regime)"])


def strat_smc_inverse_fvg(s):
    """Batch 216: Inverse FVG - bullish FVG was invalidated (price closed
    below) -> the zone flips role and acts as resistance (short).
    Symmetric for bearish FVG invalidated upward (long).
    ICT 'IFVG' concept: a failed institutional imbalance becomes the new
    opposing reference.

    Batch 262 fix (Pass 53 Day 9+ 2026-05-20 post-1A-alpha forensic):
    Original signal fired 478 trades (40% of all flow) with 24.7% WR /
    -3.47% mean PnL = -1659pp total contribution = ~95% of aggregate loss.
    Root cause: no regime gate, no volume confirmation, no momentum filter.
    Fired on every IFVG flag indiscriminately.

    Added confluence gates:
    - 200-EMA regime alignment (long above, short below)
    - vol_spike OR price_acceleration confirms institutional follow-through
      (IFVG breakdown without volume = false signal per ICT canon)
    """
    fl_base = s.get("smc_inverse_fvg_bullish", False)
    fs_base = s.get("smc_inverse_fvg_bearish", False)
    # B663 family-bug sweep: was default-True silent-gap; positive symmetric below_ema_200 (B630 producer) replaces (not above_200)
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    # Volume confirmation: vol_spike_2x (2x ADV) OR force_index_breakout
    # signals institutional follow-through on the role-flip
    vol_confirms = s.get("vol_spike_2x", False) or s.get("force_index_breakout", False)
    fl = fl_base and above_200 and vol_confirms
    fs = fs_base and below_200 and vol_confirms
    return _strat3(fl, fs, "smc",
        ["smc_inverse_fvg_bullish", "price_above_ema_200", "vol_confirms"],
        ["smc_inverse_fvg_bearish", "price_below_ema_200", "vol_confirms"],
        ["Inverse FVG bullish + 200-EMA gate + volume confirms",
         "ICT IFVG role-flip with institutional follow-through"],
        ["Inverse FVG bearish + 200-EMA gate + volume confirms",
         "ICT IFVG role-flip with institutional follow-through"])


def strat_smc_breaker_block_short(s):
    """Batch 216: Breaker block short - bullish OB that was mitigated +
    price now below bottom -> the OB flips role and becomes resistance.
    Classic ICT 'breaker block' reversal setup."""
    fires = (
        s.get("smc_breaker_block_bearish", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "smc",
        ["smc_breaker_block_bearish", "price_below_ema_200"],
        ["Bullish Order Block mitigated + price below - role flipped to resistance",
         "Below 200 EMA (bear regime)"])


def strat_smc_breaker_block_long(s):
    """Batch 216: Breaker block long - bearish OB that was mitigated +
    price now above top -> flips to support."""
    fires = (
        s.get("smc_breaker_block_bullish", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_breaker_block_bullish", "price_above_ema_200"],
        ["Bearish Order Block mitigated + price above - role flipped to support",
         "Above 200 EMA (regime gate)"])


def strat_smc_mitigation_block_long(s):
    """Batch 216: Price entering an UN-mitigated bullish Order Block
    zone - the institutional zone is being mitigated NOW. Lower-risk
    entry than waiting for the OB to fully play out; pairs naturally
    with subsequent CHoCH/BOS confirmation."""
    fires = (
        s.get("smc_mitigation_block_long", False)
        and s.get("price_above_ema_200", False)
        and s.get("rsi_14", 50) < 50
    )
    return _strat(fires, "long", "smc",
        ["smc_mitigation_block_long", "price_above_ema_200", "rsi_14<50"],
        ["Price inside bullish Order Block zone - mitigation underway",
         "Above 200 EMA (regime gate)",
         "RSI pullback context (not overbought)"])


def strat_smc_mitigation_block_short(s):
    """Batch 216: Symmetric mitigation block short."""
    fires = (
        s.get("smc_mitigation_block_short", False)
        and s.get("below_ema_200", False)  # B630 sweep
        and s.get("rsi_14", 50) > 50
    )
    return _strat(fires, "short", "smc",
        ["smc_mitigation_block_short", "price_below_ema_200", "rsi_14>50"],
        ["Price inside bearish Order Block zone - mitigation underway",
         "Below 200 EMA (bear regime)",
         "RSI rally context (not oversold)"])


def strat_smc_discount_long(s):
    """Batch 216: Premium/Discount filter - long only when price is in
    DISCOUNT zone (below 50% of recent dealing range) AND there is
    bullish structure (BOS bullish OR CHoCH bullish). ICT discipline:
    'buy low, sell high' inside the dealing range. Mitigates against
    chasing tops in an uptrend."""
    fires = (
        s.get("smc_in_discount_zone", False)
        and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False))
        and s.get("price_above_ema_200", False)
    )
    pct = s.get("smc_dealing_range_pct", 0.5)
    return _strat(fires, "long", "smc",
        ["smc_in_discount_zone", "smc_bos_or_choch_bullish", "price_above_ema_200"],
        [f"Price at {pct*100:.0f}% of dealing range - discount zone",
         "Bullish BOS or CHoCH - structural support",
         "Above 200 EMA (regime gate)"])


def strat_smc_premium_short(s):
    """Batch 216: Premium short - symmetric inverse of discount long.
    Price in top 50% of dealing range + bearish structure."""
    fires = (
        s.get("smc_in_premium_zone", False)
        and (s.get("smc_bos_bearish", False) or s.get("smc_choch_bearish", False))
        and s.get("below_ema_200", False)  # B630 sweep
    )
    pct = s.get("smc_dealing_range_pct", 0.5)
    return _strat(fires, "short", "smc",
        ["smc_in_premium_zone", "smc_bos_or_choch_bearish", "price_below_ema_200"],
        [f"Price at {pct*100:.0f}% of dealing range - premium zone",
         "Bearish BOS or CHoCH - structural resistance",
         "Below 200 EMA (bear regime)"])


def strat_smc_ote_long(s):
    """Batch 216: Optimal Trade Entry long - Fibonacci 62-79%
    retracement zone after bullish CHoCH/BOS. ICT canonical 'sweet
    spot' for high-conviction trend continuation entries."""
    fires = (
        s.get("smc_ote_long_zone", False)
        and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False))
    )
    pct = s.get("smc_retracement_pct", 0.0)
    return _strat(fires, "long", "smc",
        ["smc_ote_long_zone", "smc_bos_or_choch_bullish"],
        [f"OTE zone: {pct:.0f}% retracement (62-79% Fib)",
         "Bullish BOS/CHoCH - structural backdrop"])


def strat_smc_ote_short(s):
    """Batch 216: Symmetric OTE short."""
    fires = (
        s.get("smc_ote_short_zone", False)
        and (s.get("smc_bos_bearish", False) or s.get("smc_choch_bearish", False))
    )
    pct = s.get("smc_retracement_pct", 0.0)
    return _strat(fires, "short", "smc",
        ["smc_ote_short_zone", "smc_bos_or_choch_bearish"],
        [f"OTE zone: {pct:.0f}% retracement (62-79% Fib)",
         "Bearish BOS/CHoCH - structural backdrop"])


def strat_smc_equal_highs_sweep_short(s):
    """Batch 216: Equal-highs cluster swept (taking out stops above
    cluster) + bearish FVG below = high-conviction reversal short.
    Classic ICT stop-hunt-then-reverse pattern."""
    fires = (
        s.get("smc_equal_highs_swept", False)
        and s.get("smc_fvg_bearish_active", False)
    )
    return _strat(fires, "short", "smc",
        ["smc_equal_highs_swept", "smc_fvg_bearish_active"],
        ["Equal-highs cluster swept - buy-side liquidity taken",
         "Bearish FVG active below - reversal confluence"])


def strat_smc_equal_lows_sweep_long(s):
    """Batch 216: Equal-lows cluster swept + bullish FVG above =
    high-conviction reversal long."""
    fires = (
        s.get("smc_equal_lows_swept", False)
        and s.get("smc_fvg_bullish_active", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_equal_lows_swept", "smc_fvg_bullish_active"],
        ["Equal-lows cluster swept - sell-side liquidity taken",
         "Bullish FVG active above - reversal confluence"])


def strat_smc_bos_retest_entry(s):
    """Batch 216: BOS retest - price returns to within 0.5pct of a
    recently-broken structure level. Empirically higher hit rate than
    naive BOS continuation per ICT discipline (allow the broken level
    to confirm-as-support before adding risk)."""
    fl = (
        s.get("smc_bos_retest_long", False)
        and s.get("price_above_ema_200", False)
    )
    fs = (
        s.get("smc_bos_retest_short", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat3(fl, fs, "smc",
        ["smc_bos_retest_long", "price_above_ema_200"],
        ["smc_bos_retest_short", "price_below_ema_200"],
        ["Price retesting broken structure level (BOS bullish)",
         "Above 200 EMA (regime gate)"],
        ["Price retesting broken structure level (BOS bearish)",
         "Below 200 EMA (bear regime)"])


def strat_smc_bos_continuation(s):
    """Batch 210 (SMC/ICT family 2026-05-17 owner-approved research review).
    Break of Structure continuation: market makes a new structural high
    (BOS up) after a CHoCH; trend-continuation entry. Quantum Algo Mar
    2026 backtest: combined SMC stack achieved 61% WR / 2.17 PF / +2.27R
    average on 2,600 trades over 26 months.

    Batch 278 (Tier 2 gate tightening 2026-05-20 owner-approved option B):
    Stage B v2 showed 13 trades / 15.4% WR / -6.60% mean / -86 pp. Root
    cause: Batch 273's event_recency_bars=90 means BOS signal stays True
    for up to 90 bars, so entries fire on stale structural breaks where
    trend may have already reversed. Added: vol_confirms (vol_spike_2x OR
    force_index_breakout) + momentum confirm (RSI direction-aligned) to
    require institutional follow-through on the BOS bar.
    """
    vol_confirms = s.get("vol_spike_2x", False) or s.get("force_index_breakout", False)
    rsi = s.get("rsi_14", 50)
    fl = (
        s.get("smc_bos_bullish", False)
        and s.get("price_above_ema_200", False)
        and vol_confirms
        and rsi > 50
    )
    fs = (
        s.get("smc_bos_bearish", False)
        and s.get("below_ema_200", False)  # B630 sweep
        and vol_confirms
        and rsi < 50
    )
    return _strat3(fl, fs, "smc",
        ["smc_bos_bullish", "price_above_ema_200", "vol_confirms", "rsi_14>50"],
        ["smc_bos_bearish", "price_below_ema_200", "vol_confirms", "rsi_14<50"],
        ["Break of Structure (continuation) up + volume + momentum confirms",
         "Above 200 EMA (regime gate)"],
        ["Break of Structure (continuation) down + volume + momentum confirms",
         "Below 200 EMA (bear regime)"])


def strat_smc_choch_reversal(s):
    """Batch 210: Change of Character reversal. CHoCH marks the FIRST
    structural shift opposing the prior trend; high-conviction reversal
    setup per ICT/SMC discipline. Pairs with FVG-aligned entry."""
    fl = (
        s.get("smc_choch_bullish", False)
        and s.get("smc_fvg_bullish_active", False)
    )
    fs = (
        s.get("smc_choch_bearish", False)
        and s.get("smc_fvg_bearish_active", False)
    )
    return _strat3(fl, fs, "smc",
        ["smc_choch_bullish", "smc_fvg_bullish_active"],
        ["smc_choch_bearish", "smc_fvg_bearish_active"],
        ["Change of Character bullish (reversal)",
         "Bullish Fair Value Gap active - confluence"],
        ["Change of Character bearish (reversal)",
         "Bearish Fair Value Gap active - confluence"])


def strat_smc_order_block_bounce(s):
    """Batch 210: Order block bounce. Bullish OB = last opposing
    (bearish) candle before an impulse up; price returning to this zone
    acts as institutional support. Symmetric for bearish OB."""
    fl = (
        s.get("smc_ob_bullish_active", False)
        and s.get("rsi_14", 50) < 45  # pullback context
        and s.get("price_above_ema_200", False)
    )
    fs = (
        s.get("smc_ob_bearish_active", False)
        and s.get("rsi_14", 50) > 55
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat3(fl, fs, "smc",
        ["smc_ob_bullish_active", "rsi_14<45", "price_above_ema_200"],
        ["smc_ob_bearish_active", "rsi_14>55", "price_below_ema_200"],
        ["Bullish Order Block active - institutional support zone",
         "RSI pullback context", "Above 200 EMA"],
        ["Bearish Order Block active - institutional resistance zone",
         "RSI rally context", "Below 200 EMA"])


def strat_smc_liquidity_sweep_reversal(s):
    """Batch 210: Liquidity sweep reversal. Price sweeps a cluster of
    equal highs/lows (taking out stops), then reverses. Classic ICT
    'stop hunt' pattern. Pairs with CHoCH for additional reversal
    confirmation."""
    fl = (
        s.get("smc_liquidity_swept_dn", False)  # lows swept -> bullish reversal
        and (s.get("smc_choch_bullish", False) or s.get("smc_bos_bullish", False))
    )
    fs = (
        s.get("smc_liquidity_swept_up", False)
        and (s.get("smc_choch_bearish", False) or s.get("smc_bos_bearish", False))
    )
    return _strat3(fl, fs, "smc",
        ["smc_liquidity_swept_dn", "smc_choch_or_bos_bullish"],
        ["smc_liquidity_swept_up", "smc_choch_or_bos_bearish"],
        ["Liquidity sweep down (stops taken below low cluster)",
         "Followed by bullish CHoCH/BOS - reversal confirmed"],
        ["Liquidity sweep up (stops taken above high cluster)",
         "Followed by bearish CHoCH/BOS - reversal confirmed"])


def strat_turtle_soup_long(s):
    """Batch 580 (2026-06-04): Turtle Soup mean-reversion long per Linda
    Bradford Raschke 'Street Smarts' (1996). First Layer 2D ICT pattern
    wired via inline-spec protocol (Option A 2026-06-04 per
    feedback_layer_2d_ict_inline_specification).

    Setup: downside liquidity has been swept (retail stops below
    support taken out) AND today's bar closes back ABOVE prior-day-low
    AND closes bullish. The failed-breakdown pattern suggests the
    downside move was a stop-hunt rather than a genuine trend
    continuation. ICT framing: 'Judas Swing failed', return-to-range.

    Distinct from `smc_liquidity_sweep_reversal` (which requires CHoCH
    or BOS confirmation). Turtle Soup is the pure Raschke pattern -
    no structure-shift confirmation needed, just the sweep + close
    bullish + back-inside-range. Cleaner same-day signal; mean-reversion
    direction.

    Producer signals (all Layer 2A wired):
      - smc_liquidity_swept_dn (smc_ict.py:341)
      - above_prev_low / below_prev_high (technical.py:139; above_prev_low
        added in B616 as positive symmetric pair to existing below_prev_low)
      - close_above_open (technical.py:153)

    B616 (2026-06-07 owner-directed LOW-priority refactor): swapped
    `not s.get("below_prev_low", True)` -> `above_prev_low` (B616 NEW
    producer signal) for positive symmetric signal per
    feedback_never_use_NOT_s_get_pattern. Behavior preserved up to the
    strict-vs-inclusive convention at-tick equality (today_close exactly
    == prior_low is empirically rare).
    """
    fires = (
        s.get("smc_liquidity_swept_dn", False)
        and s.get("above_prev_low", False)     # B616: closed back ABOVE prior-day-low
        and s.get("close_above_open", False)   # bullish reversal bar
    )
    return _strat(fires, "long", "ict",
        ["smc_liquidity_swept_dn", "above_prev_low", "close_above_open"],
        ["Turtle Soup long (Raschke Street Smarts 1996)",
         "Downside liquidity swept - retail stops taken below support",
         "Price reversed back ABOVE prior-day-low - stop-hunt failed",
         "Bullish close above open - rejection of downside breakout"])


def strat_turtle_soup_short(s):
    """Batch 580 (2026-06-04): Turtle Soup mean-reversion short. Mirror
    of strat_turtle_soup_long per feedback_long_short_inverse_audit.
    Setup: upside liquidity swept (retail stops above resistance taken)
    AND today closed back BELOW prior-day-high AND closes bearish.
    Failed-breakout / stop-hunt pattern; mean-reversion to downside.

    B616 (2026-06-07 owner-directed LOW-priority refactor): swapped
    `not s.get("above_prev_high", True)` -> `below_prev_high` (B616 NEW
    producer signal symmetric to existing above_prev_high).
    """
    fires = (
        s.get("smc_liquidity_swept_up", False)
        and s.get("below_prev_high", False)     # B616: closed back BELOW prior-day-high
        and s.get("close_below_open", False)    # bearish reversal bar
    )
    return _strat(fires, "short", "ict",
        ["smc_liquidity_swept_up", "below_prev_high", "close_below_open"],
        ["Turtle Soup short (Raschke Street Smarts 1996)",
         "Upside liquidity swept - retail stops taken above resistance",
         "Price reversed back BELOW prior-day-high - stop-hunt failed",
         "Bearish close below open - rejection of upside breakout"])


def strat_judas_swing_long(s):
    """Batch 581 (2026-06-04): Judas Swing variant per ICT specification.
    Distinct from `smc_liquidity_sweep_reversal` (which requires CHoCH/BOS)
    AND from `turtle_soup_long` (which requires close back above prior_low).
    Judas Swing focuses on FALSE RANGE BREAK + return to RANGE INTERIOR
    (deeper return to pivot midpoint vs Turtle Soup's just-back-inside).

    Setup: liquidity swept down (range low taken out) AND price returned
    near the pivot midpoint (deep return to range interior) AND bullish
    bar. Catches the "manipulation" move in ICT framing - retail stops
    hunted then institutions reverse deeper into the range.

    Producers (Layer 2A + technical.py):
      - smc_liquidity_swept_dn
      - near_pivot (close within 0.3pct of standard pivot point P; range midpoint)
      - close_above_open (bullish rejection bar)
    """
    fires = (
        s.get("smc_liquidity_swept_dn", False)
        and s.get("near_pivot", False)
        and s.get("close_above_open", False)
    )
    return _strat(fires, "long", "ict",
        ["smc_liquidity_swept_dn", "near_pivot", "close_above_open"],
        ["Judas Swing long (ICT manipulation reversal)",
         "Downside liquidity swept - retail stops taken below range low",
         "Price returned deep to pivot midpoint - institutional reversal",
         "Bullish bar - rejection of stop-hunt extension"])


def strat_judas_swing_short(s):
    """Mirror of strat_judas_swing_long per feedback_long_short_inverse_audit."""
    fires = (
        s.get("smc_liquidity_swept_up", False)
        and s.get("near_pivot", False)
        and s.get("close_below_open", False)
    )
    return _strat(fires, "short", "ict",
        ["smc_liquidity_swept_up", "near_pivot", "close_below_open"],
        ["Judas Swing short (ICT manipulation reversal)",
         "Upside liquidity swept - retail stops taken above range high",
         "Price returned deep to pivot midpoint - institutional reversal",
         "Bearish bar - rejection of stop-hunt extension"])


def strat_mmbm_long(s):
    """Batch 581 (2026-06-04): Market Maker Buy Model (MMBM) - bullish
    Power-of-3 cycle per ICT methodology + owner inline-spec.

    Setup: Accumulation (tight range last N bars) -> Manipulation
    (sweep below accumulation low) -> Distribution (close back above
    accumulation low with bullish bar). The institutional-flow pattern:
    market makers accumulate at the range low, manipulate price down to
    trigger retail stops + accumulate cheap liquidity, then distribute
    upward toward the original range high.

    Producer: compute_po3_signals() in backtest/signals/ict_producers.py
    consumed via po3_mmbm_setup boolean (combined gate: accumulation +
    sweep-down + close-above-low + bullish-bar).
    """
    fires = bool(s.get("po3_mmbm_setup", False))
    return _strat(fires, "long", "ict",
        ["po3_mmbm_setup"],
        ["MMBM Market Maker Buy Model (ICT PO3 bullish cycle)",
         "Phase 1 ACCUMULATION: tight range over last N bars",
         "Phase 2 MANIPULATION: sweep below accumulation low (stops taken)",
         "Phase 3 DISTRIBUTION setup: price reversed back inside range,",
         "  bullish bar - institutional reversal into upward distribution"])


def strat_mmsm_short(s):
    """Mirror of strat_mmbm_long. Market Maker Sell Model - bearish PO3.
    Sweep up to take stops above range high, then distribute downward."""
    fires = bool(s.get("po3_mmsm_setup", False))
    return _strat(fires, "short", "ict",
        ["po3_mmsm_setup"],
        ["MMSM Market Maker Sell Model (ICT PO3 bearish cycle)",
         "Phase 1 ACCUMULATION: tight range over last N bars",
         "Phase 2 MANIPULATION: sweep above accumulation high (stops taken)",
         "Phase 3 DISTRIBUTION setup: price reversed back inside range,",
         "  bearish bar - institutional reversal into downward distribution"])


def strat_week_opening_gap_fill_down(s):
    """Batch 581 (2026-06-04): Week Opening Gap Fill - SHORT direction.
    Daily-bar proxy for ICT Sunday gap. When Monday opens with a
    significant gap UP (Mon_open > Fri_close by >= 1.5pct), price often
    drifts DOWN to fill the gap. Fade the gap up.

    Producer: compute_week_opening_gap_signals() in ict_producers.py.
    """
    fires = bool(s.get("week_open_gap_up_15pct", False))
    return _strat(fires, "short", "ict",
        ["is_week_open", "week_open_gap_up_15pct"],
        ["Week Opening Gap Fill - fade upside gap (ICT Sunday gap proxy)",
         "Monday opened with gap up >= 1.5pct vs prior Friday close",
         "Statistical bias: gaps tend to fill on the week-open bar"])


def strat_week_opening_gap_fill_up(s):
    """Mirror of strat_week_opening_gap_fill_down. When Monday opens
    with a gap DOWN >= 1.5pct, price often drifts UP to fill. Fade
    the gap down."""
    fires = bool(s.get("week_open_gap_down_15pct", False))
    return _strat(fires, "long", "ict",
        ["is_week_open", "week_open_gap_down_15pct"],
        ["Week Opening Gap Fill - fade downside gap (ICT Sunday gap proxy)",
         "Monday opened with gap down >= 1.5pct vs prior Friday close",
         "Statistical bias: gaps tend to fill on the week-open bar"])


def strat_pead_long(s):
    """Batch 209 (PEAD module 2026-05-17 owner-approved research review).
    Post-Earnings Announcement Drift long entry per Bernard-Thomas (1989)
    *Journal of Accounting Research* + Garfinkel-Hribar-Hsiao (2024)
    update. Strong positive earnings surprise + YoY growth -> 60 trading
    days of price drift continuation.

    Long: within 60d of last earnings filing AND positive YoY EPS growth
    AND positive announcement-day return (>+2%).
    """
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
    )
    yoy = s.get("earnings_eps_yoy_growth", 0.0)
    ann = s.get("earnings_announcement_return", 0.0)
    return _strat(fires, "long", "event_driven",
        ["within_pead_window", "pead_positive_surprise",
         "earnings_eps_yoy_growth>0", "announcement_return>+2pct"],
        [f"Within PEAD drift window (<=60d post-earnings)",
         f"YoY EPS growth: {yoy*100:.1f}%",
         f"Announcement-day return: {ann*100:.1f}% (>+2% surprise threshold)",
         "Bernard-Thomas (1989) 60-day drift continuation"])


def strat_pead_short(s):
    """Batch 209: PEAD short - symmetric for negative-surprise drift.
    Documented effect: bottom-decile-surprise stocks underperform for
    same 60-day window (Garfinkel et al. 2024)."""
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_negative_surprise", False)
    )
    yoy = s.get("earnings_eps_yoy_growth", 0.0)
    ann = s.get("earnings_announcement_return", 0.0)
    return _strat(fires, "short", "event_driven",
        ["within_pead_window", "pead_negative_surprise",
         "earnings_eps_yoy_growth<0", "announcement_return<-2pct"],
        [f"Within PEAD drift window (<=60d post-earnings)",
         f"YoY EPS growth: {yoy*100:.1f}% (negative)",
         f"Announcement-day return: {ann*100:.1f}% (<-2% surprise)",
         "Bernard-Thomas 60-day drift continuation (negative)"])


# -----------------------------------------------------------------------------
# strat_pead_long_high_yoy_growth_only + strat_pead_short_negative_yoy_growth
# DELETED Batch 682 (2026-06-10 owner-approved)
# -----------------------------------------------------------------------------
# DELETION RATIONALE per B680 self-critique CC-C + owner approval 2026-06-10:
#
# Pattern W (NEW for event-driven cluster B677 self-critique): EV-3 and
# EV-4 are DETERMINISTIC STRICT SUBSETS of EV-1 (`strat_pead_long`) and
# EV-2 (`strat_pead_short`) respectively on the YoY-growth axis:
#
#   EV-1 fires when: within_pead_window AND pead_positive_surprise
#                    (yoy_growth > 0 AND announcement_return > +2%)
#   EV-3 fires when: within_pead_window AND yoy_surprise_high
#                    (yoy_growth >= +5%)
#
# Every YoY >= 5% case is ALSO yoy > 0; EV-3's fires are a subset of
# EV-1's fires (on the YoY axis alone; EV-1's ann_ret > +2% gate adds
# a narrowing axis EV-3 lacks, but the YoY-axis subset relationship
# holds). Cube replay would produce near-identical per-trade Sharpe
# by construction.
#
# Per `project_no_apriori_strategy_pruning` explicit owner override on
# Pattern W deterministic-subset evidence (mechanical not empirical):
# owner approved deletion 2026-06-10 in response to B680 self-critique
# recommendation. Pattern W reskin pattern = Pattern N reskin in
# specific deterministic-subset form.
#
# B507 M6 Path-2 sleeve rationale: shipped YoY-growth proxy in lieu of
# paid Finnhub analyst-surprise re-prefetch. The methodology was sound
# but the implementation as separate registry entries (vs as a parameter
# variant of EV-1/EV-2) was structurally redundant.
#
# Future work: if YoY-growth-specific PEAD validation is needed, ship as
# a CONFIGURATION variant (yoy_threshold_strict parameter on EV-1/EV-2)
# rather than separate registry slots -- cube can sensitivity-sweep without
# inflating family-wise correction budget.
#
# No downstream code references; ALL_STRATEGIES registry entries also removed.
# -----------------------------------------------------------------------------


def strat_squeeze_setup_long(s):
    """Batch 615 (2026-06-07 owner-directed F1 docstring reframe per
    feedback_13f_state_signal_staleness B611 staleness playbook):

    The L1 layer is a POSITIONING ELIGIBILITY FILTER (slow STATE
    signals), NOT bar-of-fire conviction:
      - short_interest_pct (FINRA bi-monthly, ~14d stale)
      - days_to_cover (FINRA bi-monthly, ~14d stale)
      - institutional_buy (13F quarterly + DEC-325 45d lag - up to
        135d stale; provides factor-tilt eligibility, NOT timing)
      - insider_cluster_active (rolling-30d quasi-event)

    The L1 STATE half supplies the YES/NO permission to consider a
    name; it does NOT carry timing alpha at the bar of fire. The
    timing alpha + reversal conviction comes from L2 catalyst +
    L3 confirmation (the EVENT layers below).

    Walker correction: prior docstring described L1c smart-money OR
    as "the squeeze fuel that turns SI from a paper-position into
    actual upside risk". That overclaimed for the institutional_buy
    13F STATE half (which is typically constant for 90+45d).

    For an EVENT-only L1c variant, see strat_squeeze_setup_event_only
    _long (B615 B-twin) - cube replay will compare current OR composite
    vs strict EVENT-only smart-money requirement.

    LINEAGE:
      - B519 (P15) ORIGINAL: high SI + DC20 breakout + above-avg volume
        (3 weak gates, mostly lagging confirmations).
      - B601 (Stage 4 walk + desk-research redesign): Option A
        3-layer composite. Eliminated Donchian. See full structure
        below.
      - B615 (Stage 4 re-walk per CHECKLIST #105 a-j): F1 docstring
        reframed (honest STATE/EVENT framing); B-twin added for
        empirical A/B vs EVENT-only L1c.

    Architecture:

      LAYER 1 - POSITIONING ELIGIBILITY (slow STATE; weeks-ahead
        permission, NOT timing):
        (1a) short_interest_pct >= 0.20 (preserved from B519)
        (1b) days_to_cover >= 8 (owner-framework directive; was unused
             on the long side - only short_borrow_trap_avoid consumed
             days_to_cover via the > 5 gate)
        (1c) institutional_buy OR insider_cluster_active
             (smart-money present on the name - EVENT half supplies
             rolling-30d insider quasi-event; STATE half supplies 13F
             eligibility tilt. OR composite allows pure-STATE firing,
             which the B615 B-twin tightens to EVENT-only for A/B.)

      LAYER 2 - CATALYST (leading, hours-to-days):
        (2a) news_sentiment_shift > 0.4 (strong positive narrative
             shift; owner-framework "catalyst trigger")
        OR (2b) within_pead_window AND pead_positive_surprise
             (earnings beat as the catalyst; PEAD post-announcement
             drift window typically 60d)

      LAYER 3 - CONFIRMATION (entry timing):
        (3a) above_avwap_20low (institutional reference reclaimed -
             Brian Shannon 2022 AVWAP from recent 20-day swing low;
             replaces dc20_breakout_up as a CONTEMPORANEOUS rather
             than post-event signal. The Donchian breakout fires AFTER
             the move; AVWAP reclaim fires AS the institutional flow
             tips.)
        (3b) vol_spike_15x (>=1.5x volume - institutional aggression
             vs B519 vol_above_avg >= 1.0x which let retail noise through)
        (3c) close_above_open (bullish bar; B589-family)
        (3d) close_in_top_40pct_of_range (strong close; B589-family)

    Academic & professional backing:
      - Cohen-Diether-Malloy 2007 JF (high SI + positive shock = squeeze)
      - Boehmer-Jones-Zhang 2008 JF (composition matters: institutional
        squeeze on retail shorts)
      - Diether-Lee-Werner 2009 RFS (high SI has concentrated upside
        tail; multi-signal scoring needed to capture it)
      - Owner-framework 2026-06-05: SI >= 20% + DTC 8-10 + catalyst +
        VWAP confirmation + above-avg volume + bullish-bar
      - Industry alignment: S3 Partners / Ortex / Hazeltree composite
        squeeze-scoring uses positioning + catalyst + microstructure

    Producer signals required (all already emitted, zero new code):
      short_interest_pct, days_to_cover  (FINRA cache; B519)
      institutional_buy, insider_cluster_active  (Quiver smart-money)
      news_sentiment_shift  (Polygon news)
      within_pead_window, pead_positive_surprise  (earnings cache)
      above_avwap_20low  (Brian Shannon AVWAP; B205 + B598)
      vol_spike_15x, close_above_open, close_in_top_40pct_of_range
        (compute_volume; B589 family)

    NOTE: This eliminates the Donchian primitive from the strategy
    entirely. Drops the Donchian-touching footprint from 22 -> 21
    strategies (10% -> 9.7%).
    """
    si_pct = s.get("short_interest_pct", 0.0) or 0.0
    dtc    = s.get("days_to_cover",      0.0) or 0.0

    layer1_positioning = (
        si_pct >= 0.20
        and dtc >= 8.0
        and (s.get("institutional_buy", False)
             or s.get("insider_cluster_active", False))
    )
    layer2_catalyst = (
        (s.get("news_sentiment_shift", 0.0) or 0.0) > 0.4
        or (s.get("within_pead_window", False)
            and s.get("pead_positive_surprise", False))
    )
    layer3_confirmation = (
        s.get("above_avwap_20low", False)
        and s.get("vol_spike_15x", False)
        and s.get("close_above_open", False)
        and s.get("close_in_top_40pct_of_range", False)
    )
    fires = layer1_positioning and layer2_catalyst and layer3_confirmation

    return _strat(fires, "long", "smart_money_sleeve",
        ["short_interest_pct>=20pct", "days_to_cover>=8",
         "institutional_buy|insider_cluster_active",
         "news_sentiment_shift>0.4|within_pead_window+pead_positive_surprise",
         "above_avwap_20low", "vol_spike_15x",
         "close_above_open", "close_in_top_40pct_of_range"],
        [f"L1 positioning: SI {si_pct*100:.1f}% + DTC {dtc:.1f}d + smart-money present (B615 eligibility filter)",
         "L2 catalyst: news sentiment shift OR positive earnings surprise (PEAD window)",
         "L3 confirmation: above 20d swing-low AVWAP + 1.5x volume + bullish bar + strong close",
         "Cohen-Diether-Malloy 2007 + Boehmer-Jones-Zhang 2008 + Diether-Lee-Werner 2009",
         "S3/Ortex-style composite squeeze-scoring (B601 redesign)"])


# Batch 620 (2026-06-08 owner-directed B619 fire-count estimator finding):
# strat_squeeze_setup_event_only_long DELETED. The B-twin (B615) added an
# EVENT-only L1c variant for A/B test vs strat_squeeze_setup_long's broader
# OR composite. Fire-count estimator (B619) flagged ~2.5 fires/yr universe-
# wide upper bound (FAIL_FIRE_STARVED per CHECKLIST (k)) - the conjunction
# of high-SI eligibility + EVENT-only L1c + 4-gate L3 confirmation drops
# below min_trades=30/regime by an order of magnitude. The same A/B
# question can be answered POST-CUBE by filtering strat_squeeze_setup_long's
# trade log to the subset where insider_cluster_active=True at fire bar -
# no separate registered strategy needed. Consistent with `feedback_minimum
# _fire_count_gate_before_cube` resolution "treat as exploratory or split"
# without weaponizing the cube on an unrunnable cell.


def strat_activist_13d_long(s):
    """Batch 522 (2026-05-31, P17b SCAFFOLD per EXECUTION_QUEUE).

    Long fires when SC 13D (activist) filing landed in the last
    30 days. Trigger boolean is `sc_13d_filed_within_30d` from
    `compute_sec_edgar_signals(ticker, as_of)`.

    Academic backing: Brav-Jiang-Partnoy-Thomas 2008 *Journal of
    Finance* documented +6.8% abnormal return in the 30d window around
    13D filing announcement; Bebchuk-Brav-Jiang 2015 RFS show sustained
    +3-5pp/yr alpha for 5 years post-filing. Filers most associated:
    Icahn, Ackman, Peltz, Elliott, ValueAct, Starboard.

    NOT REGISTERED in ALL_STRATEGIES in Batch 522 -- ships SCAFFOLD-only
    pending P17a scoped extraction completion (in flight ~6h) + owner
    approval for ALL_STRATEGIES wire-in.
    """
    fires = bool(s.get("sc_13d_filed_within_30d", False))
    filer = s.get("sc_13d_latest_filer_identity", "")
    pct = s.get("sc_13d_latest_percent_owned", None)
    bullets = ["SC 13D filed within last 30 days (activist signal)"]
    if filer:
        bullets.append(f"Filer: {filer}")
    if pct is not None:
        bullets.append(f"Percent owned: {pct:.1f}%")
    bullets.append("Brav-Jiang-Partnoy-Thomas 2008 +6.8% 30d CAR")
    return _strat(fires, "long", "sec_edgar_sleeve",
        ["sc_13d_filed_within_30d"], bullets)


def strat_m_and_a_target_long(s):
    """Batch 522 (2026-05-31, P17c SCAFFOLD per EXECUTION_QUEUE).

    Long fires when 8-K Item 1.01 (material definitive agreement)
    landed in the last 30 days. Trigger boolean is
    `8k_item_1_01_filed_within_30d` from `compute_sec_edgar_signals`.

    Academic backing: Pawliczek-Skinner 2018 *Review of Accounting
    Studies* -- Items 1.01 + 2.02 predict short-term returns
    (~2-3pp 10-day CAR). Item 1.01 is frequently the FIRST public
    disclosure that a company is being acquired or signed a major
    partnership; stock often gaps 10-30% on the next bar.

    NOT REGISTERED in ALL_STRATEGIES in Batch 522 -- ships SCAFFOLD-only
    pending P17a scoped extraction completion + owner approval for
    ALL_STRATEGIES wire-in.
    """
    fires = bool(s.get("8k_item_1_01_filed_within_30d", False))
    return _strat(fires, "long", "sec_edgar_sleeve",
        ["8k_item_1_01_filed_within_30d"],
        ["8-K Item 1.01 (material definitive agreement) filed <=30d ago",
         "Often first public disclosure of M&A or major partnership",
         "Pawliczek-Skinner 2018 +2-3pp 10-day CAR"])


def strat_short_borrow_trap_avoid(s):
    """Batch 519 (2026-05-31, P15 sleeve per owner directive).
    Avoid-side gate for short strategies when borrow is tight.

    B671 Round 2 Q6 (2026-06-10 owner-approved per AskUserQuestion Round 2):
    threshold tightened from days_to_cover > 5.0 to > 8.0 per reviewer F5
    observation that 5.0 was loose (GME 2021 pre-squeeze ~5-7 borderline;
    MSTR 2021 ~8-12; BBBY pre-collapse ~6-10). New threshold (8.0) captures
    GME 2021 pre-squeeze + BBBY borderline inside the gate while reducing
    false-positive blocks on routine moderate-DTC names.

    B671 Round 2 Q5 (2026-06-10 owner-approved): SM-5's avoid emission is
    now actually consulted by ALL SHORT strategies via centralized gate in
    _strat() / _strat3() helpers. Pre-B671 SM-5 was an orphan emitter
    (engine dropped avoid output per backtest.py:1457-1466 skipped_trades
    path); post-B671 every SHORT strategy fire is gated by
    _short_borrow_trap_active(s) consult per reviewer F5 architectural
    concern.

    Fires `avoid` direction when days_to_cover > 8 -- meaning it would
    take >8 trading days of typical volume to cover the open short
    interest. Hard-to-borrow names carry asymmetric upside risk: when
    they DO move against shorts, the squeeze is rapid (FINRA Reg SHO).
    Per CHECKLIST risk-management convention, an 'avoid' strategy
    blocks SHORT entries on the ticker for the bar -- works the same
    way as Batch 190 crisis-long-exclusion list, but per-bar instead
    of by-ticker.

    Academic backing: Cohen-Diether-Malloy 2007 -- shorted names with
    high DTC have higher subsequent positive returns (the 'borrow
    constraint' premium).
    """
    dtc = s.get("days_to_cover", 0.0) or 0.0
    fires = dtc > 8.0  # B671 Q6 owner-approved 5.0 -> 8.0
    return _strat(fires, "avoid", "smart_money_sleeve",
        ["days_to_cover>8"],
        [f"Days-to-cover {dtc:.1f} (>8 threshold; B671 Q6 tighten from 5.0)",
         "Hard-to-borrow -> squeeze risk asymmetric vs upside expectancy",
         "Cohen-Diether-Malloy 2007 borrow-constraint premium"])


def strat_avwap_252_breakout(s):
    """Batch 208 (new strategy family 2026-05-17 owner-approved research review).
    Anchored VWAP from 252-day swing low breakout. Brian Shannon (2022)
    Maximum Trading Gains With Anchored VWAP, CMT Association whitepaper.

    Long: price reclaims AVWAP-252-low (was below, now above) + volume
    confirms + RSI not extreme-overbought. Marks an institutional-level
    inflection - the year's accumulation-distribution reference.

    Short: price loses AVWAP-252-low to the downside + volume confirms.
    Symmetric inverse for distribution / breakdown days.
    """
    above_252 = s.get("above_avwap_252low", False)
    pct_from_252 = s.get("pct_from_avwap_252low", 0.0)
    vol_ok = s.get("vol_spike_15x", False)
    rsi_14 = s.get("rsi_14", 50)
    # Long: just reclaimed (close to AVWAP but above) + volume + RSI not capped
    fl = (
        above_252
        and abs(pct_from_252) < 2.0   # within 2% of AVWAP (close to inflection)
        and vol_ok
        and rsi_14 < 70
    )
    # Short: just lost (close below AVWAP) + volume + RSI not capped
    fs = (
        (not above_252)
        and abs(pct_from_252) < 2.0
        and vol_ok
        and rsi_14 > 30
    )
    return _strat3(fl, fs, "vwap",
        ["above_avwap_252low", "near_avwap_252low<2pct", "vol_spike_1.5x", "rsi_14<70"],
        ["below_avwap_252low", "near_avwap_252low<2pct", "vol_spike_1.5x", "rsi_14>30"],
        ["Price reclaimed Anchored VWAP from 252d low - institutional accumulation",
         "Close to AVWAP inflection (within 2%)", "Volume 1.5x ADV(20)",
         "RSI not extreme overbought"],
        ["Price lost Anchored VWAP from 252d low - distribution",
         "Close to AVWAP inflection (within 2%)", "Volume 1.5x ADV(20)",
         "RSI not extreme oversold"])


def strat_avwap_50_reclaim(s):
    """Batch 208: AVWAP-50-low reclaim with confirming momentum. Higher-
    frequency variant of the 252-low strategy targeting recent-leg
    reclaims rather than annual-reference inflections. Pairs naturally
    with the 50-day momentum window."""
    above_50 = s.get("above_avwap_50low", False)
    pct_from_50 = s.get("pct_from_avwap_50low", 0.0)
    macd_bull = s.get("macd_12_26_9_bullish", False)
    # Long: just reclaimed AVWAP-50 + MACD turning bullish
    fl = (
        above_50
        and abs(pct_from_50) < 1.5
        and macd_bull
        and s.get("price_above_ema_200", False)  # require uptrend regime
    )
    # Short: just lost AVWAP-50 + MACD turning bearish
    fs = (
        (not above_50)
        and abs(pct_from_50) < 1.5
        and (not macd_bull)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat3(fl, fs, "vwap",
        ["above_avwap_50low", "near_avwap_50low<1.5pct", "macd_bullish",
         "price_above_ema_200"],
        ["below_avwap_50low", "near_avwap_50low<1.5pct", "macd_bearish",
         "price_below_ema_200"],
        ["Price reclaimed Anchored VWAP from 50d low - recent leg accumulation",
         "Within 1.5% of AVWAP inflection", "MACD bullish",
         "Above 200 EMA (regime gate)"],
        ["Price lost Anchored VWAP from 50d low - recent leg distribution",
         "Within 1.5% of AVWAP inflection", "MACD bearish",
         "Below 200 EMA (bear regime)"])


def strat_avwap_20high_rejection_short(s):
    """Batch 208: short-side rejection at AVWAP from 20-day swing high.
    Recent high acts as resistance; price tests then rejects with
    bearish candle + volume. Designed to fire in neutral/bear regime
    (high-quality short setup per Anchored VWAP discipline)."""
    pct_from_20h = s.get("pct_from_avwap_20high", 0.0)
    fires = (
        not s.get("above_avwap_20high", True)  # below 20-high AVWAP
        and abs(pct_from_20h) < 1.0
        and (s.get("shooting_star") or s.get("bearish_engulfing"))
        and s.get("vol_spike_15x", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "vwap",
        ["below_avwap_20high", "near_avwap_20high<1pct",
         "shooting_star_or_bearish_engulfing", "vol_spike_1.5x",
         "price_below_ema_200"],
        ["Price tested Anchored VWAP from 20d high and rejected",
         "Within 1% of AVWAP inflection",
         "Bearish reversal candle confirms sellers",
         "Volume 1.5x ADV(20)",
         "Below 200 EMA (bear regime confirmation)"])


# ---------------------------------------------------------------------------
# Batch 252 (Phase 1C+ Wave 1 strategy registrations 2026-05-20)
# Chart patterns (DEC-355-362 / Batch 242) - 5 strategies
# ---------------------------------------------------------------------------
def strat_head_and_shoulders_bottom_long(s):
    """Batch 252: inverse H&S long entry (Edwards-Magee + Bulkowski 2005)."""
    fires = (
        s.get("head_shoulders_bottom_detected", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "chart_pattern",
        ["head_shoulders_bottom_detected", "price_above_ema_200"],
        ["Inverse head-and-shoulders pattern detected",
         "Edwards-Magee 1948 / Bulkowski 2005 canonical reversal",
         "Above 200 EMA (regime gate)"])


def strat_head_and_shoulders_top_short(s):
    """Batch 685 (2026-06-10 owner-approved Class 7 NEW) per
    feedback_long_short_inverse_audit + B683 self-critique B678 CC-B
    missing-inverse audit. Mirror of strat_head_and_shoulders_bottom_long.

    Head-and-shoulders TOP is the canonical bearish reversal pattern per
    Edwards-Magee 1948 *Technical Analysis of Stock Trends* + Bulkowski
    2005 *Encyclopedia of Chart Patterns* (~74% measured WR on neckline-
    confirmed breakdowns per Bulkowski published stats; mirror reliability
    to the H&S bottom long counterpart). 3 peaks with middle (head) highest;
    shoulders roughly symmetric; price breaks down through neckline.

    Producer signal head_shoulders_top_detected from
    chart_patterns.compute_head_and_shoulders (line 83-113); pre-existing
    + already PIT-disciplined.

    Symmetric 2-gate structure with CP-3 (mirror of bottom-long).
    B671 borrow-trap gate applies (SHORT-direction via _strat).
    """
    fires = (
        s.get("head_shoulders_top_detected", False)
        and s.get("below_ema_200", False)  # B630 producer-additive (positive symmetric)
    )
    return _strat(fires, "short", "chart_pattern",
        ["head_shoulders_top_detected", "price_below_ema_200"],
        ["Head-and-shoulders top pattern detected (3 peaks; middle = head)",
         "Edwards-Magee 1948 / Bulkowski 2005 canonical bearish reversal",
         "Below 200 EMA (bear regime)"])


def strat_double_bottom_long(s):
    """Batch 252: double-bottom long entry."""
    fires = (
        s.get("double_bottom_detected", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "chart_pattern",
        ["double_bottom_detected", "price_above_ema_200"],
        ["Double-bottom pattern detected (2 lows at same level + trough)",
         "Above 200 EMA (regime gate)"])


def strat_inverted_cup_and_handle_short(s):
    """Batch 686 (2026-06-10 owner-approved Class 7 NEW per B683 self-
    critique CP-1 missing-inverse audit; deferred from B685 pending
    producer-side methodology work; now scoped + executed B686).

    Bearish mirror of strat_cup_and_handle_long. Inverted cup-and-handle
    per Bulkowski 2005 *Encyclopedia of Chart Patterns* (sometimes
    called 'rounded top with handle' or 'dump and pop'). Symmetric to
    O'Neil CANSLIM cup-and-handle bullish setup but inverted topology.

    Producer signal inverted_cup_handle_detected from B686 NEW
    detect_inverted_cup_and_handle in chart_patterns.py:179+.

    Symmetric gate structure with CP-1 cup_and_handle_long (B685
    Pattern A WAVE 2 swept; post-fix design):
      - inverted_cup_handle_detected (pattern)
      - below_ema_200 (bearish trend; B630 producer-additive)
      - vol_spike_2x (B278 forensic-fix volume confirmation -
        symmetric to LONG cup-and-handle B278 gate)
      - below_ema_50 (B630 producer-additive intermediate trend)
      - rsi_14 > 30 (not already oversold; symmetric to CP-1's
        rsi_14 < 70 not overbought)

    B671 borrow-trap gate applies (SHORT-direction via _strat).

    Per `feedback_structural_symmetry_not_economic_symmetry` (owner
    correction 2026-06-07 B617): structural symmetry to CP-1 does NOT
    imply economic symmetry. Equity upward drift bias + bear-pattern
    arbitrage + borrow costs all bias against the SHORT side. Cube
    replay will validate per-cell Sharpe; do NOT assume inherited
    win-rate from CP-1.

    EXPLORATORY-candidate post-B660: same Pattern G fire-starve risk
    class as CP-1 (Bulkowski 2005 published frequencies for cup-and-
    handle patterns indicate ~5-15/yr per universe; inverted variant
    likely similar or rarer in upward-drift equity).
    """
    fires = (
        s.get("inverted_cup_handle_detected", False)
        and s.get("below_ema_200", False)  # B630 producer-additive
        and s.get("vol_spike_2x", False)
        and s.get("below_ema_50", False)  # B630 producer-additive (symmetric to CP-1 ema_50 gate)
        and s.get("rsi_14", 50) > 30
    )
    return _strat(fires, "short", "chart_pattern",
        ["inverted_cup_handle_detected", "below_ema_200",
         "vol_spike_2x", "below_ema_50", "rsi_14>30"],
        ["Inverted cup-and-handle pattern detected (Bulkowski 2005 rounded top with handle)",
         "Bearish breakdown + 2x volume confirmation (symmetric to CP-1 B278 fix)",
         "Below 200 + 50 EMA (dual trend gate)",
         "RSI not oversold (avoid late-stage entries; symmetric to CP-1 not-overbought)"])


def strat_cup_and_handle_long(s):
    """Batch 252: O'Neil CANSLIM cup-and-handle long.

    Batch 278 (Tier 2 gate tightening 2026-05-20 owner-approved option B):
    Stage B v2 showed 12 trades / 16.7% WR / -4.30% mean / -52 pp. Root
    cause: pattern detection without volume confirmation. O'Neil's CANSLIM
    canonical setup REQUIRES volume on the handle breakout bar - without
    it, the breakout is unconfirmed and often fails. Added: vol_spike_2x
    + above 50-EMA (intermediate trend filter) + RSI < 70 (not overbought,
    avoid late-stage entries).
    """
    fires = (
        s.get("cup_handle_detected", False)
        and s.get("price_above_ema_200", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", False)
        and s.get("rsi_14", 50) < 70
    )
    return _strat(fires, "long", "chart_pattern",
        ["cup_handle_detected", "price_above_ema_200",
         "vol_spike_2x", "price_above_ema_50", "rsi_14<70"],
        ["Cup-and-handle pattern detected (O'Neil 1988)",
         "CANSLIM breakout + 2x volume confirmation (canonical)",
         "Above 200 EMA + 50 EMA (dual trend gate)",
         "RSI not overbought (avoid late-stage entries)"])


def strat_flag_bull_long(s):
    """Batch 252 ORIGINAL: bull flag long (Edwards-Magee + Bulkowski).

    Batch 618 (2026-06-07 owner-directed B607 critique correction):
    PHANTOM-BREAKOUT BUG FIXED. Pre-B618 the strategy fired on
    flag_bull_detected + EMA-200 alone - but flag_bull_detected fires
    the day the flag COMPLETES, and the flag window includes today's
    bar. By construction today's close <= flag_high (high >= close).
    So the strategy could not fire on an actual breakout - only on
    flag-detected-while-still-inside-the-flag. The strategy name said
    "breakout" but no breakout had occurred.

    Fix: require flag_bull_broke (B618 NEW producer signal in
    compute_flag_break_retest_signals) - a flag completed K bars ago
    (K in 1..8), today's close > the historical flag_high. PIT-
    disciplined via historical-slice detect_flag.

    Naming correction (critique #6): pre-B618 docstring claimed
    "high-tight flag" but detect_flag defaults are +10% pole / <5%
    flag, NOT the classic Weinstein high-tight (>=90% pole). Renamed
    to "standard flag" in the description.
    """
    fires = (
        s.get("flag_bull_broke", False)         # B618: breakout-occurred gate
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "chart_pattern",
        ["flag_bull_broke", "price_above_ema_200"],
        ["Bull flag (+10% pole / <5% consolidation - standard flag NOT high-tight)",
         "Today's close > historical flag-high (B618 phantom-breakout fix)",
         "Above 200 EMA (regime gate)"])


def strat_triangle_ascending_long(s):
    """Batch 252: ascending triangle long (flat top + rising lows)."""
    fires = (
        s.get("triangle_ascending_detected", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "chart_pattern",
        ["triangle_ascending_detected", "price_above_ema_200"],
        ["Ascending triangle (flat resistance + rising support)",
         "Bulkowski 2005: breakout direction follows trend ~70%",
         "Above 200 EMA (regime gate)"])


def strat_triangle_descending_short(s):
    """Batch 685 (2026-06-10 owner-approved Class 7 NEW) per
    feedback_long_short_inverse_audit + B683 self-critique B678 CC-B
    missing-inverse audit. Mirror of strat_triangle_ascending_long.

    Descending triangle is the documented bearish continuation pattern
    per Edwards-Magee 1948 + Bulkowski 2005 (~64% measured WR on
    confirmed breakdowns; symmetric reliability to ascending counterpart).
    Flat support + descending highs; price breaks down through flat support.

    Producer signal triangle_descending_detected from
    chart_patterns.compute_triangle_patterns (line 308-317); pre-existing.

    Symmetric 2-gate structure with CP-7 (mirror of ascending-long).
    B671 borrow-trap gate applies (SHORT-direction via _strat).
    """
    fires = (
        s.get("triangle_descending_detected", False)
        and s.get("below_ema_200", False)  # B630 producer-additive
    )
    return _strat(fires, "short", "chart_pattern",
        ["triangle_descending_detected", "price_below_ema_200"],
        ["Descending triangle (flat support + falling highs)",
         "Bulkowski 2005: breakdown direction follows trend ~64%",
         "Below 200 EMA (bear regime)"])


def strat_cup_and_handle_retest_long(s):
    """BUG-111 (Batch 329) ORIGINAL: retest variant of cup_and_handle_long.

    Batch 685 (2026-06-10 owner-approved per B683 self-critique CP-9):
    REPLACED `resistance_break_retest` (DC20-anchored proxy; explicitly
    acknowledged as proxy in docstring) with `cup_handle_neckline_break
    _retest_long` (B685 NEW producer in chart_patterns.compute_cup_handle
    _neckline_break_retest_signals) -- now anchored on the SPECIFIC
    cup_handle_breakout_level (handle high). Same B607-pattern fix as
    B607 (flag) + B605 (52w) + B606 (R1) lineage.

    Also Pattern A WAVE 2 sweep B685: swapped `price_above_ema_50`
    default-True -> default-False (silent-gap closure).

    O'Neil 1988 + Bulkowski 2005: the handle retest is the canonical
    low-risk entry for CANSLIM cup.
    """
    fires = (
        s.get("cup_handle_detected", False)
        and s.get("cup_handle_neckline_break_retest_long", False)  # B685: replaces resistance_break_retest
        and s.get("price_above_ema_200", False)
        and s.get("price_above_ema_50", False)  # B685 Pattern A WAVE 2: default-True -> False
        and s.get("rsi_14", 50) < 70
    )
    return _strat(fires, "long", "chart_pattern",
        ["cup_handle_detected","cup_handle_neckline_break_retest_long",
         "price_above_ema_200","price_above_ema_50","rsi_14<70"],
        ["Cup-and-handle pattern detected (O'Neil 1988)",
         "Post-break retest of SPECIFIC handle high / neckline (B685 producer fix)",
         "Above 200 + 50 EMA (dual trend gate)",
         "RSI not overbought"])


def strat_flag_bull_retest_long(s):
    """BUG-111 (Batch 329) ORIGINAL: retest variant of flag_bull_long.
    Documented as "Bull flag + post-break retest" but consumed DC20-
    anchored resistance_break_retest signal. The DC20-max-CLOSE bore
    no relationship to the flag-high level (which is what should be
    retested per Edwards-Magee + Bulkowski). Same name-vs-implementation
    bug pattern that B605 fixed for 52wh_break_retest and B606 fixed
    for r1_break_retest.

    Batch 607 (2026-06-07 owner-directed F1 bug fix per CHECKLIST #105
    deep-read; F1 + a + c + g + i applied):

      F1 - Replaced resistance_break_retest with NEW
        flag_bull_break_retest_long primitive
        (compute_flag_break_retest_signals in chart_patterns.py).

    Batch 618 (2026-06-07 owner-directed B607 critique correction):
    DOCSTRING REFRAME per critique #1 - the breakout-occurred gate
    was buried in producer helper logic. Lifted to first-class
    requirement. The flag_bull_break_retest_long producer signal
    encodes a 4-condition AND chain (FIRST-CLASS REQUIREMENTS):
      (1) FLAG-COMPLETED: a bull flag completed K bars ago
          (K in 3..12) on a HISTORICAL slice df.iloc[:n-K] - PIT-
          disciplined so flag_high is computed over bars strictly
          BEFORE the breakout/retest window.
      (2) BREAKOUT-OCCURRED: at least one bar in (n-K, n-1) closed
          STRICTLY ABOVE flag_bull_breakout_level. Without this gate
          the strategy would anchor a "retest" to a level that was
          never breached (critique #1 phantom-breakout concern).
      (3) RETEST: at least one subsequent bar's LOW touched within
          1.5*ATR(14) of breakout_level.
      (4) STILL-ABOVE: today's close >= breakout_level (holding the
          broken level).

    The strategy gate `s.get("flag_bull_break_retest_long")` returns
    True only when ALL FOUR conditions hold. The producer is unit-
    tested for PIT discipline in test_batch618_pit_discipline.py.

      (a) Added close_above_open (B589-family bullish bar).
      (c) Added vol_below_avg (Bulkowski canonical retest =
          supply-absorption on LOWER volume).
      (i) Regime affinity: Batch 291 direction-aware default
          (LONG -> {bull, neutral}).

    SKIPPED at B607: (b) strong-close top-40% / (d) AVWAP / (e) global
    pole tighten / (f) MACD / (h) flag_bear_short non-retest. Owner
    chose narrower set to test F1 effect first.

    NAMING NOTE (B618 critique #6): detect_flag defaults are +10% pole
    / <5% flag - this is a STANDARD flag, NOT the classic Weinstein
    high-tight flag (>=90% pole). Per-strategy docstring + STRATEGY
    _ROSTER updated.

    BULKOWSKI WIN-RATE CITATION CAVEAT (B618 critique #5): prior
    docstring/walk cited ~70% conditional win-rate from Bulkowski.
    Bulkowski stats are definition-sensitive; the implementation
    here (fixed-window detection + ATR tolerance + no minimum-move
    pole) doesn't match Bulkowski's hand-labeled population. Edge
    must be validated empirically by the backtest, not assumed from
    textbook.

    Post-B607 4-gate set (unchanged in B618 - this is a docstring
    + naming correction batch, no behavior change):
      flag_bull_break_retest_long + price_above_ema_200 +
      close_above_open + vol_below_avg
    """
    fires = (
        s.get("flag_bull_break_retest_long", False)
        and s.get("price_above_ema_200", False)
        and s.get("close_above_open", False)
        and s.get("vol_below_avg", False)
    )
    return _strat(fires, "long", "chart_pattern",
        ["flag_bull_break_retest_long","price_above_ema_200",
         "close_above_open","vol_below_avg"],
        ["Bull flag broken + retested at SPECIFIC flag_bull_breakout_level (Edwards-Magee + Bulkowski 2005)",
         "Above 200 EMA (trend filter)",
         "Bullish bar (close above open)",
         "Volume below 20d avg (Bulkowski retest = supply absorption on lower volume)"])


def strat_flag_bear_retest_short(s):
    """Batch 607 (2026-06-07 owner-directed Class 7 NEW): symmetric
    inverse of strat_flag_bull_retest_long per
    feedback_long_short_inverse_audit. Producer emits flag_bear
    _break_retest_short (same B607 F1 primitive); strategy fires on
    bear-flag breakdown-and-retest with below-200-EMA bearish trend
    + bearish bar + Bulkowski below-avg volume on the retest.

    Mirror 4-gate structure:
      flag_bear_break_retest_short + NOT price_above_ema_200 +
      close_below_open + vol_below_avg

    Batch 618 (2026-06-07 owner-directed B607 critique correction
    per CHECKLIST #105 (m) economic-symmetry audit):
    STRUCTURAL SYMMETRY does NOT imply ECONOMIC SYMMETRY. Bull and
    bear flag base rates differ in equities (upward drift bias +
    squeeze asymmetry disrupt bear-flag downside follow-through;
    Bulkowski's own stats give bull and bear flags different
    measured-move reliabilities). This SHORT must be validated as
    its own strategy with its own expectancy in the cube - NOT
    assumed to inherit the LONG's hit-rate.

    Producer signal flag_bear_break_retest_short from B607 NEW
    compute_flag_break_retest_signals; all others pre-existing.

    PIT-disciplined: producer uses df.iloc[:n-K] historical slice
    so flag_low is computed over a window strictly BEFORE the
    breakdown/retest window. Regression-pinned in
    test_batch618_pit_discipline.

    Regime affinity: Batch 291 direction-aware default
      (SHORT -> {bear, crisis, neutral}).
    """
    # B616 (2026-06-07 owner-directed LOW-priority refactor): swapped
    # `not s.get("price_above_ema_200", False)` -> `below_ema_200`
    # (B609 producer) for positive symmetric signal.
    fires = (
        s.get("flag_bear_break_retest_short", False)
        and s.get("below_ema_200", False)
        and s.get("close_below_open", False)
        and s.get("vol_below_avg", False)
    )
    return _strat(fires, "short", "chart_pattern",
        ["flag_bear_break_retest_short","below_ema_200",
         "close_below_open","vol_below_avg"],
        ["Bear flag broken + retested at SPECIFIC flag_bear_breakdown_level",
         "Below 200 EMA (bearish trend filter)",
         "Bearish bar (close below open)",
         "Volume below 20d avg (Bulkowski retest characteristic)"])


def strat_triangle_ascending_retest_long(s):
    """BUG-111 (Batch 329) ORIGINAL: retest variant of triangle_ascending_long.

    Batch 685 (2026-06-10 owner-approved per B683 self-critique CP-8
    DESIGN BUG CANDIDATE): REPLACED `resistance_break_retest` (DC20-
    anchored - bug class) with `triangle_apex_break_retest_long` (B685
    NEW producer in chart_patterns.compute_triangle_apex_break_retest
    _signals) -- now anchored on the SPECIFIC triangle_resistance_level
    (flat top of ascending triangle = apex). Same B607-pattern fix as
    B607 (flag) + B605 (52w) + B606 (R1) lineage.

    Ascending triangle + post-break retest of the flat-top resistance.
    Bulkowski 2005: triangle apex breakout retest is the canonical entry."""
    fires = (
        s.get("triangle_ascending_detected", False)
        and s.get("triangle_apex_break_retest_long", False)  # B685: replaces resistance_break_retest
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "chart_pattern",
        ["triangle_ascending_detected","triangle_apex_break_retest_long","price_above_ema_200"],
        ["Ascending triangle + post-break retest of SPECIFIC apex resistance (B685 producer fix)",
         "Bulkowski 2005: retest entry filter ~70% win on confirmed breaks",
         "Above 200 EMA (regime gate)"])


# ---------------------------------------------------------------------------
# Wave 3 13F-based strategies (Batch 330 2026-05-25 owner-approved Path C):
# institutional flow as PRIMARY entry trigger (not just tier-adjust confirmation).
# Producer at screen_instrument injects institutional_signal / strong_buy /
# buy / negative / new_positions / increased into the per-ticker signals dict.
# Cohen-Frazzini-Malloy 2008 RFS; Bushee-Goodman 2007 JAR; Yan-Zhang 2009 RFS
# (short-horizon institutional persistence).
# ---------------------------------------------------------------------------


def strat_institutional_cluster_long(s):
    """Wave 3 (Batch 330): institutional cluster-buy long.
    13F shows new_positions >= 3 OR (new_pos >= 1 AND increased >= 2) in
    the most recent quarter (Cohen-Frazzini-Malloy 2008 RFS: cluster-buys
    forecast ~1-month alpha). Gated by 200-EMA regime to avoid catching
    falling-knife positions."""
    fires = (
        s.get("institutional_strong_buy", False)
        and s.get("price_above_ema_200", False)
    )
    new_pos = s.get("institutional_new_positions", 0)
    incr = s.get("institutional_increased", 0)
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_strong_buy","price_above_ema_200"],
        [f"13F cluster: {new_pos} new positions + {incr} increased",
         "Cohen-Frazzini-Malloy 2008 - cluster-buys forecast 1-mo alpha",
         "Above 200 EMA (regime gate)"])


def strat_institutional_buy_momentum_long(s):
    """Wave 3 (Batch 330): institutional buy + price momentum.
    Looser 13F signal (any buy/strong_buy) combined with price momentum
    confirmation (MACD bullish + above 50-EMA). Yan-Zhang 2009 RFS:
    short-horizon institutional persistence + price trend agreement
    filters out one-off institutional buys at tops."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_50", False)
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_buy","macd_12_26_9_bullish","price_above_ema_50"],
        ["13F new/increased institutional positions",
         "MACD bullish - price momentum agrees with institutional flow",
         "Above 50 EMA (intermediate trend gate)"])


# SM-9 strat_institutional_distribution_short DELETED Batch 670 (2026-06-10
# owner-approved per STAGE_4_SMART_MONEY_CLUSTER_WALKS.md B669 cluster-walk
# critique reviewer F2 + Pattern C STRENGTHENED disposition).
#
# DELETION RATIONALE:
#   - 13F is SEC long-only by rule (Cohen-Frazzini-Malloy 2008 RFS documents
#     long-side institutional accumulation; NO analog for trimming-as-bear-
#     signal)
#   - `institutional_negative` (decreased > increased) means institutions
#     trimmed LONGS for rebalancing/redemption/tax-loss/profit-taking,
#     NOT that smart money is short
#   - 13F is quarterly STATE with DEC-325 45-day filing lag = eligibility
#     filter, NOT bar-of-fire timing signal
#   - The empirical engine (Stage-D cube) is structurally BLIND to the
#     falseness because survivorship gap (C5, still open) + cost-borrow
#     gap (C6, still open) mask the cases that would expose it
#   - `project_no_apriori_strategy_pruning` was misapplied here per
#     reviewer F2: the prior is a regulatory fact (13F SEC long-only)
#     not a guess; the no-pruning rule's purpose is to prevent premature
#     deletion on weak priors
#
# PRECEDENT: B611 deletion of strat_institutional_breakdown_confirmation_short
# established the same data-source-asymmetry deletion criterion on a
# structurally identical strategy. B669 reviewer F2 argued the B611
# precedent applies; owner approved deletion in B670.
#
# REPLACEMENT: Class 7 NEW strat_simple_below_ema_50_short below preserves
# the only gate that was actually doing discriminative work (below_ema_50)
# without the 13F-trim-disguise. Registered in `momentum_trend` category;
# does NOT belong to smart money cluster.
#
# CITATION RETRACTION: the Sias 2004 + Lo-Wang 2000 citations in the
# deleted SM-9 docstring were citation-overreach (Pattern F7 honesty
# class) - those papers document realized-trading institutional herding
# with observable seller motive, NOT 13F position-delta filings. The
# Class 7 NEW replacement below does NOT carry those citations.


def strat_simple_below_ema_50_short(s):
    """Batch 670 (2026-06-10) Class 7 NEW: clean SHORT replacement for
    deleted SM-9 strat_institutional_distribution_short per owner-
    approved cluster-walk critique disposition.

    Fires SHORT when:
      below_ema_50 (trend agreement; only gate that was actually doing
                    discriminative work in deleted SM-9)

    Registered in `momentum_trend` category; does NOT belong to smart
    money cluster (no smart-money data dependency). Pure-technical SHORT
    that honestly describes its thesis: trend continuation when price is
    below the 50-EMA.

    Regime affinity: NO ENTRY -> B291 SHORT default {bear, crisis, neutral}.
    No regime entry needed; trend-following SHORT naturally fits the
    direction-aware default.
    """
    fires = s.get("below_ema_50", False)
    return _strat(fires, "short", "momentum_trend",
        ["below_ema_50"],
        ["Price below 50 EMA -- trend continuation SHORT"])


# Wave 3 13F Batch 331 (2026-05-25): 4 additional 13F-driven strategies
# leveraging the producer infrastructure shipped in Batch 330. Each combines
# the institutional flow signal with a complementary entry trigger:


def strat_institutional_oversold_long(s):
    """Wave 3 (Batch 331): institutional buy + RSI oversold mean-rev.
    Cohen-Malloy-Pomorski 2012 JF combined with Bondt-Thaler 1985 JF
    overreaction: institutional accumulation during oversold pullback
    is the classic Schwed 'cash on the sidelines' setup. Distinct from
    Batch 330's momentum variant - this is the COUNTER-TREND entry."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("rsi_14", 50) < 35
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_buy","rsi_14<35","price_above_ema_200"],
        ["13F new/increased institutional positions",
         "RSI<35 oversold (counter-trend mean-rev entry)",
         "Above 200 EMA (regime gate - filter out falling-knife)"])


def strat_institutional_breakout_confirmation_long(s):
    """Wave 3 (Batch 331) ORIGINAL: institutional sponsorship of post-break
    retest. Combines Batch 330's smart-money producer with Bulkowski 2005
    retest primitive. Institutional accumulation during the retest is the
    canonical 'smart money sponsored breakout' setup that distinguishes
    sustained breakouts from fakeouts.

    Batch 610 (2026-06-07 owner-directed Stage 4 walk per CHECKLIST #105
    deep-read; a + d + g + i applied):

      (a) Added close_above_open (B589-family bullish bar).
      (d) Added vol_below_avg per Bulkowski canonical retest =
          supply-absorption on LOWER volume (consistent with
          B594/B596/B603/B605/B606/B607/B608/B609 retest family).
      (g) [REVERSED B611] -- the Class 7 NEW strat_institutional
          _breakdown_confirmation_short was deleted same-day per
          external-AI critique. 13F data is long-only by SEC rule;
          the mechanical mirror was economically false.
      (i) Regime: Batch 291 direction-aware default
          (LONG -> {bull, neutral}).

    Batch 611 (2026-06-07 external-AI critique correction):
      HONEST REFRAMING of `institutional_buy` role. Original B610
      docstring claimed "smart-money sponsorship" and "smart money
      sponsored breakout" - both implied conviction TIMING.

      Reality: `institutional_buy` is classified off the most recent
      observable 13F filing (with DEC-325 45-day lag). 13F filings are
      QUARTERLY. Between filings, the boolean is CONSTANT for ~90 days.
      At fire-time (the retest day), it does ~zero discriminative work -
      it's effectively "is this name in the institutional-holdings
      universe with recent positive flow over the last reportable
      quarter."

      Correct framing: institutional_buy is a slow-moving ELIGIBILITY
      FILTER (universe restriction to names with confirmed 13F
      accumulation in the most recent observable quarter), NOT an event-
      timing signal. The actual TIMING comes from `resistance_break
      _retest` + `close_above_open` + `vol_below_avg` (Bulkowski retest
      pattern, fresh each bar) + `price_above_ema_200` (trend filter).

      Implications:
        - No "smart-money sponsorship" claim (the AI was right - 13F
          staleness gives no sponsorship CONVICTION on the bar)
        - Alpha attribution should credit Bulkowski retest + trend
          filter, NOT 13F sponsorship
        - 13F adds factor-tilt (Cohen-Frazzini-Malloy 2008 documented
          long-horizon institutional-ownership premium), not timing alpha

    Producer signal `institutional_buy` integrity verified end-to-end:
      - 13F two-source resolution (B294 fix for BUG-273) - bulk path
        for recency, per-ticker fallback for historical depth
      - 45-day reporting lag (DEC-325) correctly applied
      - Classification: buy = new_pos>=1 OR increased>=2
      - STATE (constant 90d between filings), NOT EVENT

    Post-B611 5-gate set (unchanged from B610):
      institutional_buy (eligibility filter) + resistance_break_retest
      (timing) + price_above_ema_200 (trend) + close_above_open (bar
      shape) + vol_below_avg (Bulkowski supply absorption)

    Academic backing:
      - Cohen-Frazzini-Malloy 2008 RFS (13F ownership predicts forward
        long-horizon returns - factor-tilt, not bar-of-fire timing)
      - Bulkowski 2005 (post-break retest with drying volume - the
        timing component)
    """
    fires = (
        s.get("institutional_buy", False)
        and s.get("resistance_break_retest", False)
        and s.get("price_above_ema_200", False)
        and s.get("close_above_open", False)
        and s.get("vol_below_avg", False)
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_buy","resistance_break_retest","price_above_ema_200",
         "close_above_open","vol_below_avg"],
        ["13F institutional accumulation during pullback to broken level",
         "Bulkowski 2005 retest entry with smart-money sponsorship",
         "Above 200 EMA (regime gate)",
         "Bullish bar (close above open)",
         "Volume below 20d avg (Bulkowski retest characteristic)"])


# Batch 611 (2026-06-07 external-AI critique): strat_institutional_breakdown
# _confirmation_short DELETED. The B610 walk applied a mechanical long/short
# symmetry rule to an asymmetric data source. 13F reports LONG positions of
# >$100M managers only; ZERO short-side data. `institutional_negative`
# (decreased > increased) means institutions trimmed LONGS - rebalancing,
# redemptions, tax-loss, profit-taking - NOT that smart money is short. The
# "Bulkowski breakdown-retest with smart-money distribution" thesis was
# economically false. Plus the staleness flaw (13F is a quarterly background
# state, not a timing signal) made the short leg far noisier than the long
# without any compensating academic grounding (Cohen-Frazzini-Malloy 2008
# is documented for long-side institutional ACCUMULATION; no analog for
# trimming-as-bear-signal). Strategy removed; LONG-side institutional
# _breakout_confirmation_long docstring reframed (see above) to drop the
# "smart-money sponsorship" claim in favor of "13F-eligibility filter +
# Bulkowski retest timing".


def strat_institutional_insider_combo_long(s):
    """Wave 3 (Batch 331): dual smart-money confirmation (13F + insiders).
    Cohen-Malloy-Pomorski 2012 JF (insiders) + Cohen-Frazzini-Malloy 2008
    RFS (institutions) - when BOTH sources accumulate simultaneously, the
    edge is multiplicative not additive (independent information channels).
    Stronger conviction than either alone."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smart_money_combo",
        ["institutional_buy","insider_cluster_active","price_above_ema_200"],
        ["13F institutional new/increased positions",
         "Insider cluster active (>=2 insiders buying open-market 30d)",
         "Dual smart-money sources agree (multiplicative edge)",
         "Above 200 EMA (regime gate)"])


# ---------------------------------------------------------------------------
# Wave 3 classification_change strategies (Batch 332 2026-05-25):
# fire on recent GICS reclassification events. Chen-Chen 2010 (industry
# classification + price discovery); Brogaard-Heath-Saadi 2019 (industry
# classification + analyst forecasts). Producer at
# universe.get_classification_change_signals reads sector_history.csv
# (DEC-323) and detects moves within a 90-day lookback.
# ---------------------------------------------------------------------------


def strat_classification_change_recent_long(s):
    """Wave 3 (Batch 332): generic recent GICS reclassification + bullish
    regime. Brogaard-Heath-Saadi 2019: reclassifications co-incide with
    analyst re-rating windows; entering on the new-classification side
    captures the analyst-cycle re-evaluation alpha. Gated by 200-EMA
    to filter out cases where reclassification follows business
    deterioration."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("price_above_ema_200", False)
    )
    days = s.get("days_since_classification_change", 0)
    new_sec = s.get("new_sector", "?")
    prior_sec = s.get("prior_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","price_above_ema_200"],
        [f"Reclassified {prior_sec} -> {new_sec} ({days}d ago)",
         "Brogaard-Heath-Saadi 2019: analyst re-rating window",
         "Above 200 EMA (filter out deterioration cases)"])


def strat_classification_change_to_tech_long(s):
    """Wave 3 (Batch 332): reclassification INTO growth sectors (IT,
    Communication Services, Health Care). Chen-Chen 2010: moves into
    high-multiple sectors trigger sustained re-rating. Examples in our
    sector_history.csv: META/GOOGL 2018 IT->Comms (Comms is growth);
    V/MA 2023 IT->Financials (NOT growth -- gated off correctly)."""
    fires = (
        s.get("classification_change_to_tech", False)
        and s.get("price_above_ema_200", False)
    )
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_change_to_tech","price_above_ema_200"],
        [f"Reclassified INTO growth sector ({new_sec})",
         "Chen-Chen 2010: re-rating into high-multiple sector",
         "Above 200 EMA"])


def strat_classification_change_to_defensive_short(s):
    """Wave 3 (Batch 332): reclassification INTO defensive sectors
    (Materials, Utilities, Real Estate, Consumer Staples) + bearish
    trend. Defensive re-classification + price weakness = continuation
    short setup. Less common than growth re-classification but cleaner
    signal when both conditions align."""
    fires = (
        s.get("classification_change_to_defensive", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "short", "classification_change",
        ["classification_change_to_defensive","price_below_ema_200"],
        [f"Reclassified INTO defensive sector ({new_sec})",
         "Re-rating into low-multiple sector",
         "Below 200 EMA - trend agrees with defensive re-rating"])


# Wave 3 classification_change Batch 335 (2026-05-25): 4 more strategies
# combining recent-reclassification signal with complementary entry triggers
# (volume confirmation, momentum agreement, from-tech inverse, break-retest
# sponsorship). Producer signals from
# universe.get_classification_change_signals (DEC-323 sector_history.csv).


def strat_classification_change_volume_long(s):
    """Wave 3 (Batch 335): recent reclassification + volume spike confirming
    market notice. Brogaard-Heath-Saadi 2019 + Lo-Wang 2000: volume
    confirms broad-market price discovery on the reclassification event."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_200", False)
    )
    days = s.get("days_since_classification_change", 0)
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","vol_spike_2x","price_above_ema_200"],
        [f"Reclassified to {new_sec} ({days}d ago) + volume confirming",
         "Lo-Wang 2000 volume-as-information",
         "Above 200 EMA (regime gate)"])


def strat_classification_change_momentum_long(s):
    """Wave 3 (Batch 335): reclassification + MACD bullish (price momentum
    agrees with analyst re-rating). Chen-Chen 2010 + standard momentum
    confirmation. Distinct from Batch 332 generic version by requiring
    momentum confluence."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_50", False)
    )
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","macd_12_26_9_bullish","price_above_ema_50"],
        ["Reclassification + MACD bullish momentum",
         "Chen-Chen 2010 re-rating + price-trend agreement",
         "Above 50 EMA (intermediate trend confirms)"])


def strat_classification_change_from_tech_short(s):
    """Wave 3 (Batch 335): inverse-rating short. Ticker moved OUT of growth
    sector (IT/Comms/Health). Symmetric to to_tech long: re-rating INTO
    a lower-multiple sector + bearish trend = continuation short. Example:
    V/MA 2023 IT -> Financials (would fire if price trended below 200-EMA
    in the 90d post-reclassification window)."""
    fires = (
        s.get("classification_change_from_tech", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    prior_sec = s.get("prior_sector", "?")
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "short", "classification_change",
        ["classification_change_from_tech","price_below_ema_200"],
        [f"Reclassified OUT of growth ({prior_sec} -> {new_sec})",
         "Inverse re-rating signal (Chen-Chen 2010 mirror)",
         "Below 200 EMA - trend agrees with downward re-rating"])


def strat_classification_change_breakout_long(s):
    """Wave 3 (Batch 335): recent reclassification + post-break retest.
    The institutional-sponsorship signature of a reclassification-driven
    breakout. Sustained re-rating + technical confirmation."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("resistance_break_retest", False)
        and s.get("price_above_ema_200", False)
    )
    days = s.get("days_since_classification_change", 0)
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","resistance_break_retest","price_above_ema_200"],
        [f"Reclassified to {new_sec} ({days}d ago) + post-break retest",
         "Re-rating-driven breakout with retest confirmation",
         "Above 200 EMA (regime gate)"])


# Wave 3 Batch 337 (2026-05-25): 3 more classification_change (completing
# the category) + 3 more persistence variants. All combinations of existing
# signal vocabulary - no new producers.


def strat_classification_change_with_institutional_long(s):
    """Wave 3 (Batch 337): smart-money validates re-rating. Reclassification
    co-incident with institutional accumulation = highest-conviction
    re-rating signal. Brogaard-Heath-Saadi 2019 (re-rating) +
    Cohen-Frazzini-Malloy 2008 (institutional cluster)."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("institutional_buy", False)
        and s.get("price_above_ema_200", False)
    )
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","institutional_buy","price_above_ema_200"],
        [f"Reclassified to {new_sec} + institutional accumulation",
         "Dual signal: analyst re-rating + smart-money conviction",
         "Above 200 EMA (regime gate)"])


def strat_classification_change_with_insider_long(s):
    """Wave 3 (Batch 337): insider validates re-rating. Insider cluster
    co-incident with reclassification = board-level + analyst agreement.
    Cohen-Malloy-Pomorski 2012 (insider) + reclassification literature."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", False)
    )
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","insider_cluster_active","price_above_ema_200"],
        [f"Reclassified to {new_sec} + insider cluster buying",
         "Board-level + analyst re-rating agreement",
         "Above 200 EMA (regime gate)"])


def strat_classification_change_oversold_long(s):
    """Wave 3 (Batch 337): reclassification at oversold = early-entry
    mean-reversion. Re-rating that hasn't yet been priced in by the market
    creates the cleanest entry window. RSI<35 + above 200-EMA filters out
    falling-knife reclassifications (e.g., distressed companies re-classed
    to lower-multiple sectors)."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("rsi_14", 50) < 35
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","rsi_14<35","price_above_ema_200"],
        ["Reclassification at oversold RSI<35",
         "Early-entry mean-rev before re-rating prices in",
         "Above 200 EMA (filter falling-knife)"])


def strat_institutional_persistence_breakout_long(s):
    """Wave 3 (Batch 337): institutional persistence + post-break retest.
    5+ funds growing position + technical breakout retest = institutional-
    sponsored breakout (Sias 2004 herding + Bulkowski retest)."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("resistance_break_retest", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","resistance_break_retest","price_above_ema_200"],
        ["5+ institutional funds grew position this quarter",
         "Post-break retest entry with institutional sponsorship",
         "Above 200 EMA (regime gate)"])


def strat_institutional_persistence_volume_long(s):
    """Wave 3 (Batch 337): institutional persistence + volume spike. 5+
    funds growing + retail tape participating = broad-market price
    discovery on the institutional position."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", False)
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","vol_spike_2x","price_above_ema_50"],
        ["5+ institutional funds grew position",
         "Volume 2x ADV - retail tape participating",
         "Above 50 EMA (intermediate trend)"])


def strat_institutional_persistence_oversold_long(s):
    """Wave 3 (Batch 337): institutional persistence + oversold mean-rev.
    Combines persistent institutional accumulation with RSI<40 counter-
    trend entry. Distinct from Batch 331 institutional_oversold_long by
    requiring multi-fund persistence (increased>=5), not just any
    institutional_buy."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("rsi_14", 50) < 40
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","rsi_14<40","price_above_ema_200"],
        ["5+ institutional funds grew position (persistence)",
         "RSI<40 oversold (counter-trend mean-rev)",
         "Above 200 EMA (filter falling-knife)"])


# Wave 3 Batch 338 (2026-05-25): final 3 persistence variants completing
# the category at 10/10 (Wave 3 total 30/30). All use existing Batch 330
# 13F producer + insider/momentum/volume keys. True multi-quarter
# persistence precompute (333b) is deferred to a future Sprint as
# infrastructure refinement; current proxies are sufficient for Stage D.


def strat_institutional_recent_init_momentum_long(s):
    """Wave 3 (Batch 338): early institutional initiation + price momentum.
    new_positions >= 2 (smaller cluster than Batch 330) + MACD bullish +
    EMA200 regime. Targets institutional initiations that the market has
    NOT yet priced in - momentum agreement filters for sustained moves."""
    fires = (
        s.get("institutional_new_positions", 0) >= 2
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_200", False)
    )
    n_new = s.get("institutional_new_positions", 0)
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_new_positions>=2","macd_12_26_9_bullish","price_above_ema_200"],
        [f"{n_new} institutional funds initiated new positions this quarter",
         "MACD bullish - price momentum agrees with smart-money flow",
         "Above 200 EMA (regime gate)"])


def strat_institutional_recent_init_volume_long(s):
    """Wave 3 (Batch 338): early initiation + retail volume confirmation.
    Same threshold as recent_init_momentum_long but trades volume gate for
    intermediate-trend gate. Lo-Wang 2000: volume confirms institutional
    sponsorship is broad-market not just smart-money private positioning."""
    fires = (
        s.get("institutional_new_positions", 0) >= 2
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", False)
    )
    n_new = s.get("institutional_new_positions", 0)
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_new_positions>=2","vol_spike_2x","price_above_ema_50"],
        [f"{n_new} institutional funds initiated new positions this quarter",
         "Volume 2x ADV - retail tape participating",
         "Above 50 EMA (intermediate trend gate)"])


def strat_institutional_multi_quarter_persistence_long(s):
    """Batch 344 (333b consumer) 2026-05-25: TRUE multi-quarter persistence
    strategy reading the offline precompute via institutional_persistence_consumer.

    Distinct from Batch 333 single-quarter proxies: requires institutional
    holders that have HELD POSITION across >=4 consecutive quarters. This
    is the canonical Yan-Zhang 2009 RFS "persistence" definition (not just
    same-quarter cross-fund consensus).

    Gate: persistent_holders_4q >= 10 (strong cross-fund persistence)
          AND price_above_ema_200 (regime gate)."""
    fires = (
        s.get("institutional_persistence_strong", False)
        and s.get("price_above_ema_200", False)
    )
    p4q = s.get("persistent_holders_4q", 0)
    total = s.get("total_active_holders", 0)
    return _strat(fires, "long", "institutional_persistence",
        ["persistent_holders_4q>=10", "price_above_ema_200"],
        [f"{p4q}/{total} funds held position 4+ consecutive quarters",
         "Yan-Zhang 2009 RFS multi-quarter persistence (NOT single-quarter)",
         "Above 200 EMA (regime gate)"])


def strat_institutional_committed_growth_long(s):
    """Batch 344 (333b consumer) 2026-05-25: institutional funds GROWING
    their position over 4+ quarters. Distinct from Batch 333's
    institutional_increased proxy by requiring multi-quarter share growth
    (>10% over 4 quarters from precompute), not just same-quarter
    increased count.

    Gate: committed_growth_holders >= 5 AND price_above_ema_200."""
    fires = (
        s.get("institutional_persistence_growing", False)
        and s.get("price_above_ema_200", False)
    )
    n_grow = s.get("committed_growth_holders", 0)
    return _strat(fires, "long", "institutional_persistence",
        ["committed_growth_holders>=5", "price_above_ema_200"],
        [f"{n_grow} funds grew position over 4+ quarters (>10% growth)",
         "Frazzini-Lamont 2008 institutional consensus + share growth",
         "Above 200 EMA (regime gate)"])


def strat_institutional_increased_with_directors_long(s):
    """Wave 3 (Batch 338): persistence + director-level insider buying.
    Combines institutional_increased>=5 (persistence proxy from Batch 333)
    with director purchases (Batch 222 insider producer; Akbas-Jiang-Koch
    2024 RFS director-premium). Triple validation: existing funds growing,
    new funds entering (implicit via cluster signal), AND board-level
    insider conviction."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("insider_director_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)
    )
    n_incr = s.get("institutional_increased", 0)
    n_dir = s.get("insider_director_buyers_30d", 0)
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","insider_director_buyers_30d>=1",
         "price_above_ema_200"],
        [f"{n_incr} institutional funds grew position (persistence)",
         f"{n_dir} director(s) buying open-market in 30d",
         "Triple smart-money validation",
         "Above 200 EMA"])


# ---------------------------------------------------------------------------
# Wave 3 persistence strategies (Batch 333 2026-05-25):
# institutional position persistence proxies using the Batch 330 producer's
# institutional_increased + institutional_new_positions counts. Yan-Zhang
# 2009 RFS: short-horizon institutional persistence forecasts alpha.
# Note: TRUE multi-quarter persistence requires precompute over 4+ quarters
# of holdings history; that's queued as Batch 333b. This batch ships
# single-quarter persistence proxies that are useful as-is.
# ---------------------------------------------------------------------------


def strat_institutional_persistent_holders_long(s):
    """Wave 3 (Batch 333): high count of institutional position increases
    (current quarter) + bullish regime. Proxy for persistence:
    institutional_increased >= 5 means at least 5 funds grew their position
    same quarter = strong consensus. Yan-Zhang 2009 RFS."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("price_above_ema_200", False)
    )
    n_incr = s.get("institutional_increased", 0)
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","price_above_ema_200"],
        [f"{n_incr} institutional funds grew position this quarter",
         "Yan-Zhang 2009 RFS - cross-fund consensus = persistence proxy",
         "Above 200 EMA (regime gate)"])


def strat_institutional_strong_conviction_long(s):
    """Wave 3 (Batch 333): fresh capital (new positions) + existing-holder
    growth (increased) simultaneously. Distinct conviction signature -
    both new entrants AND existing holders agree. Frazzini-Lamont 2008
    notes new-money + position-growth = institutional consensus."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("institutional_new_positions", 0) >= 2
        and s.get("price_above_ema_200", False)
    )
    n_new = s.get("institutional_new_positions", 0)
    n_incr = s.get("institutional_increased", 0)
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","institutional_new_positions>=2",
         "price_above_ema_200"],
        [f"{n_new} new + {n_incr} grew institutional positions",
         "Fresh capital agrees with existing-holder conviction",
         "Above 200 EMA (regime gate)"])


# SM-23 strat_institutional_capitulation_short DELETED Batch 670 (2026-06-10
# owner-approved per STAGE_4_SMART_MONEY_CLUSTER_WALKS.md B669 cluster-walk
# critique reviewer F2 + F3 + Pattern C STRENGTHENED disposition).
#
# DELETION RATIONALE (same as SM-9 deletion above):
#   - Same Pattern C data-source-asymmetry as SM-9 (13F SEC long-only by
#     rule; institutional_negative != bear conviction)
#   - Same B611 deletion precedent applies
#   - Same cube-blindness argument (C5 survivorship + C6 cost-borrow
#     still open; cube can't detect the falseness)
#   - Additionally per reviewer F3: SM-23 had a NAME-vs-THESIS
#     contradiction (name "capitulation_short" implies contrarian-
#     bottom; implementation is momentum-continuation SHORT). B669
#     docstring fix added THESIS-vs-NAME DISAMBIGUATION block; B670
#     deletion supersedes that fix and renders the rename question moot.
#
# REPLACEMENT: Class 7 NEW strat_vol_spike_2x_below_ema_50_short below
# preserves the actual tape-capitulation signal (vol_spike_2x +
# below_ema_50) that was doing real discriminative work in deleted
# SM-23, without the 13F-trim noise that Pattern C identified as
# economically false. Registered in `momentum_trend` category; does NOT
# belong to smart money cluster.
#
# CITATION RETRACTION: same Sias 2004 + Lo-Wang 2000 citation-overreach
# (Pattern F7 honesty class) as deleted SM-9; not carried forward to
# the Class 7 NEW replacement.


def strat_vol_spike_2x_below_ema_50_short(s):
    """Batch 670 (2026-06-10) Class 7 NEW: clean SHORT replacement for
    deleted SM-23 strat_institutional_capitulation_short per owner-
    approved cluster-walk critique disposition.

    Fires SHORT when ALL TWO:
      vol_spike_2x  (volume >= 2x 20-day average; EVENT - today's
                     volume confirming retail tape participation)
      below_ema_50  (trend agreement; STATE - price below 50-EMA
                     confirms downtrend continuation context)

    Thesis: tape-capitulation continuation SHORT - retail dumping into
    downtrend = sell-the-wash-out trade. Honest 2-gate framing of what
    deleted SM-23's vol_spike + below_ema_50 gates were actually doing
    (the 13F-trim gate was Pattern C noise per cluster-walk Step 7).

    Registered in `momentum_trend` category; does NOT belong to smart
    money cluster (no smart-money data dependency).

    Regime affinity: NO ENTRY -> B291 SHORT default {bear, crisis, neutral}.
    """
    fires = (
        s.get("vol_spike_2x", False)
        and s.get("below_ema_50", False)
    )
    return _strat(fires, "short", "momentum_trend",
        ["vol_spike_2x", "below_ema_50"],
        ["Volume 2x 20-day average -- retail tape participating in dump",
         "Price below 50 EMA -- downtrend continuation context"])


# Wave 3 Batch 336 (2026-05-25): 3 more 13F + 1 more persistence strategies
# completing the 13F category at 10 strategies. All combine the Batch 330
# producer's institutional signals with existing insider / momentum keys
# already in the per-ticker signals dict.


def strat_institutional_high_conviction_long(s):
    """Wave 3 (Batch 336): pure new-positions signal with looser regime.
    institutional_new_positions >= 3 alone is the canonical Cohen-Frazzini-
    Malloy 2008 RFS cluster signal. Distinct from Batch 330's cluster_long
    by using a LOOSER regime gate (50-EMA vs 200-EMA), capturing early
    institutional initiations before they fully appear in trend metrics."""
    fires = (
        s.get("institutional_new_positions", 0) >= 3
        and s.get("price_above_ema_50", False)
    )
    n_new = s.get("institutional_new_positions", 0)
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_new_positions>=3","price_above_ema_50"],
        [f"{n_new} institutional funds initiated new positions this quarter",
         "Cohen-Frazzini-Malloy 2008 RFS - pure cluster signal",
         "Above 50 EMA (looser regime to catch early initiation)"])


def strat_institutional_with_directors_long(s):
    """Wave 3 (Batch 336): institutional + director-level insider buying.
    Director purchases are higher-information signal than officer/10pct-
    owner trades (Akbas-Jiang-Koch 2024 RFS). When combined with
    institutional accumulation, dual board-level + fund-manager
    confirmation = strongest smart-money agreement signature."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_director_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)
    )
    n_dir = s.get("insider_director_buyers_30d", 0)
    return _strat(fires, "long", "smart_money_combo",
        ["institutional_buy","insider_director_buyers_30d>=1","price_above_ema_200"],
        ["13F institutional new/increased positions",
         f"{n_dir} director(s) buying open-market in 30d",
         "Akbas-Jiang-Koch 2024 RFS - director-level signal premium",
         "Above 200 EMA (regime gate)"])


def strat_institutional_with_officers_long(s):
    """Wave 3 (Batch 336): institutional + officer-level insider buying.
    Officers are CEO/CFO/COO buying their own company's stock - direct
    competence and conviction signal. Lower information value than
    directors but still meaningfully higher than 10pct-owner trades."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_officer_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)
    )
    n_off = s.get("insider_officer_buyers_30d", 0)
    return _strat(fires, "long", "smart_money_combo",
        ["institutional_buy","insider_officer_buyers_30d>=1","price_above_ema_200"],
        ["13F institutional new/increased positions",
         f"{n_off} officer(s) buying open-market in 30d",
         "Direct competence + conviction signal",
         "Above 200 EMA"])


def strat_institutional_persistence_momentum_long(s):
    """Wave 3 (Batch 336): high institutional increased + MACD momentum +
    50-EMA trend. Single-quarter persistence proxy (per Batch 333) combined
    with price-trend confirmation. Distinct from Batch 333's persistent_holders
    by requiring MACD bullish (momentum confluence, not just regime gate)."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_50", False)
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","macd_12_26_9_bullish","price_above_ema_50"],
        ["5+ institutional funds grew position this quarter",
         "MACD bullish - momentum confirms institutional conviction",
         "Above 50 EMA (intermediate trend)"])


def strat_institutional_volume_confirmation_long(s):
    """Wave 3 (Batch 331): institutional buy + retail volume confirmation.
    Per Sias 2004 JFE institutional herding + Lo-Wang 2000 RFS volume-as-
    information: retail tape volume confirming institutional accumulation
    suggests the price discovery is broadly recognized, not just
    smart-money positioning. Reduces false-positive risk on stale 13F
    filings (45-day reporting lag)."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", False)
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_buy","vol_spike_2x","price_above_ema_50"],
        ["13F institutional new/increased positions",
         "Volume 2x ADV(20) - retail tape confirming",
         "Above 50 EMA (intermediate trend agrees)"])


# ---------------------------------------------------------------------------
# Volume profile / VPVR (DEC-370 P2 / Batch 233) - 3 strategies, Batch 255 reg
# ---------------------------------------------------------------------------
def strat_poc_magnet_long(s):
    """Batch 255: POC magnet long. Steidlmayer 1985 Market Profile.
    Entry: close within 4% of POC + bullish bias + 200-EMA.
    Batch 314 Cat-3 A loosen: 2% -> 4% (owner-approved 2026-05-24)."""
    fires = (
        s.get("vp_close_near_poc_pct", 1.0) < 0.04
        and s.get("vp_close_above_poc", False)
        and s.get("price_above_ema_200", False)
    )
    dist = s.get("vp_close_near_poc_pct", 0.0)
    return _strat(fires, "long", "volume_profile",
        ["vp_close_near_poc_pct<0.04", "vp_close_above_poc", "price_above_ema_200"],
        [f"Within {dist*100:.1f}% of 60d POC (volume magnetism)",
         "Bullish bias (close above POC)",
         "Above 200 EMA (regime gate)"])


def strat_value_area_breakout_long(s):
    """Batch 255: Value Area breakout long with volume confirmation.
    Dalton-Jones-Dalton 1990 Market Profile."""
    fires = (
        s.get("vp_above_value_area", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "volume_profile",
        ["vp_above_value_area", "vol_spike_2x", "price_above_ema_200"],
        ["Close above Value Area High (institutional acceptance)",
         "Volume 2x ADV(20) (breakout confirmation)",
         "Above 200 EMA (regime gate)"])


def strat_naked_poc_retest_long(s):
    """Batch 255: Naked POC retest long. Within 2% of an untested
    period POC + bullish bias. Levels act as magnetic attractors.
    Batch 314 Cat-3 B loosen: 1% -> 2% (owner-approved 2026-05-24)."""
    fires = (
        s.get("naked_poc_count", 0) > 0
        and s.get("naked_poc_nearest_distance_pct", 1.0) < 0.02
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "volume_profile",
        ["naked_poc_nearest_distance_pct<0.02", "price_above_ema_200"],
        ["Within 2% of naked POC (untested institutional level)",
         f"{s.get('naked_poc_count', 0)} naked POCs identified (6-period)",
         "Above 200 EMA (regime gate)"])


# ---------------------------------------------------------------------------
# Calendar effects (DEC-368 / Batch 231) - 4 strategies, Batch 254 registration
# Day-level caching via lru_cache so universe-wide signals computed once per as_of
# ---------------------------------------------------------------------------
from functools import lru_cache


@lru_cache(maxsize=4)
def _cached_calendar_signals(as_of_iso: str) -> dict:
    from datetime import date as _d
    from backtest.signals.calendar_effects import compute_calendar_signals
    return compute_calendar_signals(_d.fromisoformat(as_of_iso))


@lru_cache(maxsize=4)
def _cached_cross_asset_signals(as_of_iso: str) -> dict:
    from datetime import date as _d
    from backtest.signals.cross_asset import compute_cross_asset_signals
    return compute_cross_asset_signals(_d.fromisoformat(as_of_iso))


def strat_totm_long(s):
    """Batch 254: Ariel 1987 TOTM (last-4 + first-3 trading days)."""
    fires = s.get("is_totm_window", False) and s.get("price_above_ema_200", False)
    return _strat(fires, "long", "calendar",
        ["is_totm_window", "price_above_ema_200"],
        ["TOTM window (Ariel 1987: last-4 + first-3 trading days)",
         "Above 200 EMA (regime gate)"])


def strat_pre_holiday_long(s):
    """Batch 254: Lakonishok-Smidt 1988 + Ariel 1990 pre-holiday drift."""
    fires = (
        s.get("is_pre_holiday", False)
        and s.get("dow", 0) != 0  # not Monday
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "calendar",
        ["is_pre_holiday", "dow!=0", "price_above_ema_200"],
        ["Pre-holiday session (Lakonishok-Smidt 1988)",
         "Not Monday (avoid Cross 1973 weakness)",
         "Above 200 EMA (regime gate)"])


def strat_january_effect_small_cap_long(s):
    """Batch 254: Rozeff-Kinney 1976 January Effect (small/micro-cap subset)."""
    fires = (
        s.get("is_january", False)
        and s.get("cap_band", "") in ("micro", "small")
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "calendar",
        ["is_january", "cap_band in (micro,small)", "price_above_ema_200"],
        ["January Effect (Rozeff-Kinney 1976; small-cap subset)",
         "Easterday-Sen-Stephan 2009: persists in micro/small-cap",
         "Above 200 EMA (regime gate)"])


def strat_halloween_seasonal_long(s):
    """Batch 254: Bouman-Jacobsen 2002 Halloween Indicator."""
    fires = s.get("is_halloween_period", False) and s.get("price_above_ema_200", False)
    return _strat(fires, "long", "calendar",
        ["is_halloween_period", "price_above_ema_200"],
        ["Halloween period Nov-Apr (Bouman-Jacobsen 2002)",
         "Above 200 EMA (regime gate)"])


# ---------------------------------------------------------------------------
# Cross-asset signals (DEC-369 / Batch 232) - 5 strategies, Batch 254 reg
# ---------------------------------------------------------------------------
def strat_risk_off_bond_equity_short(s):
    """Batch 254: short equity when TLT/SPY rising (risk-off bond flight).
    Asness 2003 Fed Model / Connolly-Stivers-Sun 2005."""
    fires = s.get("risk_off_regime_bond_signal", False)
    return _strat(fires, "short", "cross_asset",
        ["risk_off_regime_bond_signal"],
        ["TLT/SPY ratio rising (bond flight = risk-off)",
         "Asness 2003 / Connolly-Stivers-Sun 2005"])


def strat_vix_backwardation_long(s):
    """Batch 254: long quality when VIX > VIX3M (stress regime).
    Cheng 2019 JFE: short-vol unwinds; convexity for longs."""
    fires = (
        s.get("vix_term_backwardation", False)
        and s.get("xs_quality_decile", 0) >= 8
    )
    return _strat(fires, "long", "cross_asset",
        ["vix_term_backwardation", "xs_quality_decile>=8"],
        ["VIX > VIX3M backwardation (stress regime)",
         "Top-quintile quality (defensive sleeve)"])


def strat_sector_rotation_defensive_long(s):
    """Batch 254: long defensive sectors when defensive_leadership active.
    Conover-Jensen-Johnson-Mercer 2008 JoF."""
    fires = (
        s.get("defensive_leadership", False)
        and s.get("sector", "") in ("Utilities", "Consumer Staples", "Health Care")
    )
    return _strat(fires, "long", "cross_asset",
        ["defensive_leadership", "sector in defensive"],
        ["Defensive sectors leading XLU/XLP/XLV vs cyclicals",
         f"Ticker in defensive sector {s.get('sector', '')}"])


def strat_gold_silver_risk_off_long(s):
    """Batch 254: gold-silver ratio rising = risk-off; long defensive
    overlay. Hammoudeh-Yuan 2008 Resources Policy."""
    fires = (
        s.get("risk_off_regime_gold_signal", False)
        and s.get("sector", "") in ("Utilities", "Consumer Staples")
    )
    return _strat(fires, "long", "cross_asset",
        ["risk_off_regime_gold_signal", "sector in defensive"],
        ["Gold/Silver ratio rising (risk-off confirmation)",
         f"Defensive sector {s.get('sector', '')}"])


def strat_dxy_headwind_multinational_short(s):
    """Batch 254: short SPY-multinational names when DXY strengthening.
    Fratzscher 2009 JoB."""
    fires = (
        s.get("usd_strengthening", False)
        and s.get("foreign_rev_pct", 0.0) > 40.0
    )
    return _strat(fires, "short", "cross_asset",
        ["usd_strengthening", "foreign_rev_pct>40"],
        ["DXY strengthening 20d > 2% (multinational headwind)",
         f"Foreign rev {s.get('foreign_rev_pct', 0):.0f}% (translation risk)"])


# ---------------------------------------------------------------------------
# Pairs trading (DEC-369 / Batch 229) - 2 strategies, Batch 253 registration
# ---------------------------------------------------------------------------
def strat_pairs_mean_reversion_long(s):
    """Batch 253: cointegrated-pair mean-reversion long. Krauss 2024 +
    Gatev-Goetzmann-Rouwenhorst 2006. Entry: z<-2 (ticker underpriced
    vs peer) + half-life >= 5 (post-HFT survival)."""
    fires = (
        s.get("pair_count_active", 0) > 0
        and s.get("pair_zscore_signed", 0.0) < -2.0
        and s.get("pair_half_life", 0.0) >= 5
    )
    z = s.get("pair_zscore_signed", 0.0)
    peer = s.get("pair_counterparty", "")
    return _strat(fires, "long", "pairs",
        ["pair_zscore_signed<-2", "pair_half_life>=5", "pair_count_active>0"],
        [f"Pair z={z:.2f} vs {peer} (underpriced)",
         f"Half-life {s.get('pair_half_life', 0):.1f}d",
         "Cointegrated relationship validated at T5b precompute"])


def strat_pairs_mean_reversion_short(s):
    """Batch 253: cointegrated-pair mean-reversion short. Symmetric pair."""
    fires = (
        s.get("pair_count_active", 0) > 0
        and s.get("pair_zscore_signed", 0.0) > 2.0
        and s.get("pair_half_life", 0.0) >= 5
    )
    z = s.get("pair_zscore_signed", 0.0)
    peer = s.get("pair_counterparty", "")
    return _strat(fires, "short", "pairs",
        ["pair_zscore_signed>2", "pair_half_life>=5", "pair_count_active>0"],
        [f"Pair z={z:.2f} vs {peer} (overpriced)",
         f"Half-life {s.get('pair_half_life', 0):.1f}d",
         "Cointegrated relationship validated at T5b precompute"])


# ---------------------------------------------------------------------------
# News sentiment (DEC-370/411 / Batch 230) - 2 strategies, Batch 253 reg
# ---------------------------------------------------------------------------
def strat_news_sentiment_long(s):
    """Batch 253: positive-sentiment cluster long. Lopez-Lira-Tang 2023 +
    Loughran-McDonald 2011.

    Batch 278 tightening (2026-05-20): mean 0.3->0.5, count 3->5, added
    bullish-momentum confirm (MACD bullish OR RSI > 55). Reduced firing
    rate to ZERO across the 7191-trade Phase 1A-beta run.

    Batch 314 loosening (2026-05-24 owner-approved Cat-2 B+C): the
    Batch 278 tightening was too aggressive at Phase 1A-beta scale.
    Removed the momentum AND clause (false-positive filter that also
    blocked valid news-driven entries when underlying was rangebound)
    and lowered article count threshold 5 -> 3 (Lopez-Lira-Tang's
    original empirical threshold). Mean > 0.5 threshold retained
    (stronger consensus is still core to thesis). To be validated in
    Stage D Hetzner re-run before any Phase 1A-beta deployment.
    """
    fires = (
        s.get("news_sentiment_mean", 0.0) > 0.5
        and s.get("news_article_count", 0) >= 3
        and s.get("price_above_ema_200", False)
    )
    sent = s.get("news_sentiment_mean", 0.0)
    return _strat(fires, "long", "news_sentiment",
        ["news_sentiment_mean>0.5", "news_article_count>=3",
         "price_above_ema_200"],
        [f"7-day mean sentiment +{sent:.2f} (strong positive cluster, >+0.5)",
         f"{s.get('news_article_count', 0)} articles in window (>=3)",
         "Above 200 EMA (regime gate)"])


def strat_news_sentiment_shift_long(s):
    """Batch 253: sentiment-shift long (delta detector). +0.4 shift vs
    prior 7d + 200-EMA. Captures news-driven momentum onset."""
    fires = (
        s.get("news_sentiment_shift", 0.0) > 0.4
        and s.get("news_article_count", 0) >= 2
        and s.get("price_above_ema_200", False)
    )
    shift = s.get("news_sentiment_shift", 0.0)
    return _strat(fires, "long", "news_sentiment",
        ["news_sentiment_shift>0.4", "news_article_count>=2", "price_above_ema_200"],
        [f"Sentiment shift +{shift:.2f} (positive delta vs prior 7d)",
         "Coverage threshold met",
         "Above 200 EMA (regime gate)"])


def strat_news_momentum_long(s):
    """Batch 467 (P10) ORIGINAL: news-driven breakout. Requires positive
    5-day recency-weighted sentiment AND unusual news volume AND a 20-day
    Donchian breakout. Captures "news-confirmed breakout" entries.

    Source: Tetlock 2007 RFS news-tone return predictability +
    Da-Engelberg-Gao 2011 RFS news-attention predicts attention-induced
    returns. Combined with a price-breakout filter to avoid pure
    sentiment-driven false positives.

    Batch 603 (2026-06-05 owner-directed Stage 4 walk):
      (a) Added close_above_open + close_in_top_40pct_of_range
          (B589-family bullish-bar + strong-close standardization)
      (b) Added vol_above_avg (news-confirmed price moves should
          carry volume conviction; pure-sentiment moves without
          volume = noise risk)
      (c) Added above_avwap_20low (Brian Shannon 2022 AVWAP from
          recent 20-day swing low - institutional reference; same
          AVWAP family as B597/B598/B601)
      (f) Preserved dc20_breakout_up as the breakout primitive -
          original B603 A/B test plan retains DC anchor for the
          baseline; SMC twin (B603 A/B target) gets built separately
      (i) Regime affinity: Batch 291 direction-aware default
          (LONG -> {bull, neutral})

    Post-B603 7-gate set:
      news_sentiment_5d >= 0.5 + news_volume_zscore_5d >= 1.5 +
      dc20_breakout_up + close_above_open + close_in_top_40pct_of_range +
      vol_above_avg + above_avwap_20low
    """
    fires = (
        s.get("news_sentiment_5d", 0.0) >= 0.5
        and s.get("news_volume_zscore_5d", 0.0) >= 1.5
        and s.get("dc20_breakout_up", False)
        and s.get("close_above_open", False)
        and s.get("close_in_top_40pct_of_range", False)
        and s.get("vol_above_avg", False)
        and s.get("above_avwap_20low", False)
    )
    sent = s.get("news_sentiment_5d", 0.0)
    vz   = s.get("news_volume_zscore_5d", 0.0)
    return _strat(fires, "long", "news_sentiment",
        ["news_sentiment_5d>=0.5", "news_volume_zscore_5d>=1.5",
         "dc20_breakout_up", "close_above_open",
         "close_in_top_40pct_of_range", "vol_above_avg",
         "above_avwap_20low"],
        [f"5d recency-weighted sentiment {sent:.2f} (bullish)",
         f"News volume z-score {vz:.2f} (unusual coverage)",
         "Donchian-20 breakout up (price confirms)",
         "Bullish bar (close above open)",
         "Strong close (top 40pct of range)",
         "Volume above 20d avg (institutional confirmation)",
         "Above 20-day swing-low AVWAP (Brian Shannon 2022)"])


def strat_news_momentum_short(s):
    """Batch 603 (2026-06-05 owner-directed Class 7 NEW): symmetric
    inverse of news_momentum_long. Negative-news-confirmed breakdown.

    Mirror of news_momentum_long. Fires when 5-day recency-weighted
    sentiment is STRONGLY NEGATIVE, unusual news volume confirms
    attention, and price has broken down through the 20-day Donchian
    low. Tetlock 2007 negative-tone return predictability has stronger
    effect than positive-tone (negative news drags returns more
    durably than positive news lifts them).

    7 gates per direction matching news_momentum_long structure:
      news_sentiment_5d <= -0.5 + news_volume_zscore_5d >= 1.5 +
      dc20_breakout_dn + close_below_open +
      close_in_bottom_40pct_of_range + vol_above_avg +
      NOT above_avwap_20high (price BELOW 20d swing-high AVWAP =
      recent rally given back; symmetric to LONG above_avwap_20low)

    Regime affinity: Batch 291 direction-aware default
      (SHORT -> {bear, crisis, neutral})
    """
    # B616 (2026-06-07 owner-directed LOW-priority refactor): swapped
    # `not s.get("above_avwap_20high", True)` -> `below_avwap_20high`
    # (B612 producer) for positive symmetric signal.
    fires = (
        s.get("news_sentiment_5d", 0.0) <= -0.5
        and s.get("news_volume_zscore_5d", 0.0) >= 1.5
        and s.get("dc20_breakout_dn", False)
        and s.get("close_below_open", False)
        and s.get("close_in_bottom_40pct_of_range", False)
        and s.get("vol_above_avg", False)
        and s.get("below_avwap_20high", False)
    )
    sent = s.get("news_sentiment_5d", 0.0)
    vz   = s.get("news_volume_zscore_5d", 0.0)
    return _strat(fires, "short", "news_sentiment",
        ["news_sentiment_5d<=-0.5", "news_volume_zscore_5d>=1.5",
         "dc20_breakout_dn", "close_below_open",
         "close_in_bottom_40pct_of_range", "vol_above_avg",
         "below_avwap_20high"],
        [f"5d recency-weighted sentiment {sent:.2f} (bearish)",
         f"News volume z-score {vz:.2f} (unusual coverage)",
         "Donchian-20 breakdown (price confirms negative news)",
         "Bearish bar (close below open)",
         "Strong close (bottom 40pct of range)",
         "Volume above 20d avg (institutional confirmation)",
         "Below 20-day swing-high AVWAP - recent rally given back"])


def strat_news_reversal_short(s):
    """Batch 614 (2026-06-07 owner-directed Stage 4 walk per CHECKLIST
    #105 a-j + feedback_sequence_or_split_when_stacking_changes attribution
    tradeoff explicitly accepted by owner): a+b+c+d applied.

    Lineage:
      - B467 (P10) ORIGINAL: news-overreaction fade short. Sentiment >= +0.7
        AND pct_change_5d > +10pct AND news_article_count >= 3 (7d window).
      - B614 (a): added close_below_open + close_in_bottom_40pct_of_range
        gates so the FIRE BAR must itself be the reversal candle (not a
        delayed echo of a panic move that ended days ago). EVENT gates
        anchor an otherwise rolling-state strategy.
      - B614 (b): added news_sentiment_shift < -0.2 (today's news tone
        DETERIORATING vs prior 7d week). Catches the actual sentiment
        turn-point rather than rolling-window state. Producer emits
        news_sentiment_shift natively (news_sentiment.py B267).
      - B614 (c): swapped news_article_count (7d default) -> news_count_5d
        for window consistency with the other 5d gates. Producer emits
        news_count_5d natively (news_sentiment.py B467 P10).
      - B614 (d): loosened sentiment threshold +0.7 -> +0.5 (symmetric to
        news_momentum_long's -0.5; B603 docstring claim that "0.7 is more
        selective" was assertion without empirical backing). Fire-count
        relief addresses minimum-trades risk per
        feedback_minimum_fire_count_gate_before_cube.

    Tetlock 2007 RFS shows news-tone-driven price moves of >10pct in short
    windows tend to partially reverse over 5-10 trading days. De Bondt-
    Thaler 1985 overreaction hypothesis adapted to the news cycle.
    """
    fires = (
        s.get("news_sentiment_5d", 0.0) >= 0.5  # B614 (d): 0.7 -> 0.5
        and s.get("pct_change_5d", 0.0) > 0.10
        and s.get("news_count_5d", 0) >= 3       # B614 (c): article_count -> count_5d
        and s.get("news_sentiment_shift", 0.0) < -0.2  # B614 (b): tone turning
        and s.get("close_below_open", False)     # B614 (a): EVENT bar gate
        and s.get("close_in_bottom_40pct_of_range", False)  # B614 (a)
    )
    sent = s.get("news_sentiment_5d", 0.0)
    pct  = s.get("pct_change_5d", 0.0)
    shift = s.get("news_sentiment_shift", 0.0)
    return _strat(fires, "short", "news_sentiment",
        ["news_sentiment_5d>=0.5", "pct_change_5d>0.10",
         "news_count_5d>=3", "news_sentiment_shift<-0.2",
         "close_below_open", "close_in_bottom_40pct_of_range"],
        [f"5d sentiment {sent:.2f} (bullish; B614 d loosened to >=+0.5)",
         f"Price up {pct*100:.1f} pct in 5d (large positive move)",
         "Coverage threshold met (>=3 articles in 5d; B614 c window-consistent)",
         f"News tone shift {shift:+.2f} - DETERIORATING (B614 b reversal turn)",
         "Bearish bar + close in bottom 40pct of range (B614 a EVENT anchor)"])


def strat_news_reversal_long(s):
    """Batch 614 (2026-06-07 owner-directed Stage 4 walk per CHECKLIST
    #105 a-j + feedback_sequence_or_split_when_stacking_changes attribution
    tradeoff explicitly accepted by owner): a+b+c+d applied.

    Lineage:
      - B603 (Class 7 NEW): symmetric inverse of news_reversal_short. -0.7
        sentiment + -10pct 5d move + >=3 articles (7d window).
      - B614 (a): added close_above_open + close_in_top_40pct_of_range so
        fire bar IS the reversal candle (not a delayed echo of a crash
        that ended days ago). EVENT anchor.
      - B614 (b): added news_sentiment_shift > +0.2 (today's tone IMPROVING
        vs prior week) to capture the actual reversal moment, not stale
        rolling-state panic.
      - B614 (c): swapped news_article_count -> news_count_5d for window
        consistency.
      - B614 (d): loosened sentiment threshold -0.7 -> -0.5 (symmetric to
        news_momentum_long's -0.5; addresses fire-count risk per
        feedback_minimum_fire_count_gate_before_cube).

    Tetlock 2007 RFS + De Bondt-Thaler 1985 overreaction: sharp 5d down
    moves driven by negative news tend to partially reverse 5-10 days
    later as panic exhausts and bargain buyers emerge.

    Regime affinity: Batch 291 direction-aware default (LONG ->
    {bull, neutral}). Counter-trend long; works best when panic is
    macro-tolerable. In bear-trend the down move is real, not
    overreaction.
    """
    fires = (
        s.get("news_sentiment_5d", 0.0) <= -0.5  # B614 (d): -0.7 -> -0.5
        and s.get("pct_change_5d", 0.0) < -0.10
        and s.get("news_count_5d", 0) >= 3       # B614 (c)
        and s.get("news_sentiment_shift", 0.0) > 0.2  # B614 (b): tone turning UP
        and s.get("close_above_open", False)     # B614 (a)
        and s.get("close_in_top_40pct_of_range", False)  # B614 (a)
    )
    sent = s.get("news_sentiment_5d", 0.0)
    pct  = s.get("pct_change_5d", 0.0)
    shift = s.get("news_sentiment_shift", 0.0)
    return _strat(fires, "long", "news_sentiment",
        ["news_sentiment_5d<=-0.5", "pct_change_5d<-0.10",
         "news_count_5d>=3", "news_sentiment_shift>0.2",
         "close_above_open", "close_in_top_40pct_of_range"],
        [f"5d sentiment {sent:.2f} (bearish; B614 d loosened to <=-0.5)",
         f"Price down {pct*100:.1f} pct in 5d (large negative move)",
         "Coverage threshold met (>=3 articles in 5d; B614 c window-consistent)",
         f"News tone shift {shift:+.2f} - IMPROVING (B614 b reversal turn)",
         "Bullish bar + close in top 40pct of range (B614 a EVENT anchor)",
         "De Bondt-Thaler 1985 overreaction fade - long the panic"])


# ---------------------------------------------------------------------------
# SM1 smart-money sleeve strategies (Batch 487 / SM1 queue item 2026-05-30)
# ---------------------------------------------------------------------------
# Owner directive 2026-05-25 Batch 450: smart money currently sizing-only.
# These sleeves gate ENTRY on a smart-money composite signal so the cube
# replay can rank sleeve cells vs base cells empirically. The smart-money
# composite OR's together: insider_cluster_active, institutional_strong_buy,
# institutional_buy, cfo_buy (Batch 469), large_dollar_buy (Batch 469).
# Each sleeve adds the gate on top of an existing base condition.
def _has_smart_money_buy(s) -> bool:
    """Batch 613 (2026-06-07 owner-directed F2a honest-framing per B611
    staleness playbook): UNION ELIGIBILITY FILTER mixing EVENT and STATE
    components, NOT a "smart-money confluence" signal.

    EVENT components (bar-of-fire timing alpha):
      - insider_cluster_active (rolling-30d quasi-event - >=2 unique insider
        buyers in last 30 days)
      - cfo_buy (event)
      - large_dollar_buy (event)

    STATE components (slow background eligibility filter, 90d persistence;
    13F quarterly with DEC-325 45-day lag; provide factor-tilt, NOT
    bar-of-fire conviction):
      - institutional_strong_buy (13F state)
      - institutional_buy (13F state)

    Strategy thesis check: docstrings using `_has_smart_money_buy` must NOT
    claim "smart-money confluence" or "sponsorship" at the bar of fire when
    only the STATE components are True. The 13F-state half is ~constant 90d
    at a time; alpha attribution at fire-bar belongs to the EVENT components
    + the fast price/volume gates.
    """
    return bool(
        # EVENT components (bar-of-fire timing)
        s.get("insider_cluster_active", False)
        or s.get("cfo_buy", False)
        or s.get("large_dollar_buy", False)
        # STATE components (slow 13F eligibility filter)
        or s.get("institutional_strong_buy", False)
        or s.get("institutional_buy", False)
    )


# Batch 613 (2026-06-07 owner-directed F3b): _has_smart_money_sell helper
# DELETED. 13F filings are SEC long-only by rule (Cohen-Frazzini-Malloy 2008
# applies to accumulation, not distribution); 4 of 5 composite components
# (insider_cluster_sell, institutional_strong_sell, institutional_sell,
# cluster_sell) were NEVER EMITTED by producer (smart_money.py) -> silent-gap
# auto-False at fire time. Only concentrated_sell was actually emitted -> the
# "OR composite" reduced to a single-signal gate that misled walkers. Per
# feedback_asymmetric_data_sources_break_mechanical_inverse: the mechanical
# inverse strategy strat_52w_low_breakdown_with_smart_money_short is also
# deleted in this batch. No surviving consumer post-B613.


def strat_bollinger_tight_with_smart_money_long(s):
    """Bollinger-tight squeeze + smart-money confirmation. Sleeve variant
    of bollinger_tight base; smart-money signal validates the squeeze
    is fundamentally backed rather than technical-only."""
    base_fires = (
        s.get("bb_squeeze", False)
        and s.get("close_above_open", True)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["bb_squeeze", "close_above_open", "price_above_ema_200",
         "smart_money_buy"],
        ["Bollinger band squeeze tight", "Above 200 EMA",
         "Smart-money buy confirmation"])


def strat_mfi_oversold_with_smart_money_long(s):
    """MFI oversold + smart-money buy. Money-flow oversold often precedes
    a bounce; smart-money buy raises confidence the bounce is real."""
    base_fires = (
        s.get("mfi_14_oversold", False)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["mfi_14_oversold", "price_above_ema_200", "smart_money_buy"],
        ["MFI(14) oversold", "Above 200 EMA",
         "Smart-money buy confirmation"])


def strat_rsi_oversold_with_smart_money_long(s):
    """RSI oversold + smart-money buy. Classic mean-reversion entry with
    institutional / insider corroboration."""
    base_fires = (
        s.get("rsi_14_oversold", False)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["rsi_14_oversold", "price_above_ema_200", "smart_money_buy"],
        ["RSI(14) oversold", "Above 200 EMA",
         "Smart-money buy confirmation"])


def strat_52w_high_breakout_with_smart_money_long(s):
    """Batch 613 (2026-06-07 owner-directed F1+F2a+a re-walk per
    feedback_13f_state_signal_staleness staleness playbook):

    F1 (docstring reframe): the EVENT half of _has_smart_money_buy
    (insider_cluster_active / cfo_buy / large_dollar_buy) supplies
    bar-of-fire timing alpha (Cohen-Frazzini-Malloy 2008 RFS insider
    accumulation). The STATE half (institutional_strong_buy /
    institutional_buy) is a slow 13F-derived eligibility filter with
    ~90d persistence and DEC-325 45-day filing lag - it provides
    factor-tilt, NOT bar-of-fire conviction. George-Hwang 2004 JF
    52-week-high anomaly supplies the price-momentum thesis.

    F2a (composite honest-framing): see _has_smart_money_buy docstring
    update in this batch - mixed EVENT/STATE union, not "confluence".

    (a) Owner directive B589-family standardization: added
    close_in_top_40pct_of_range gate so the breakout requires a
    strong-close bar (matches B589 standard for momentum breakouts).

    Lineage:
      - B588: NEW strategy wired (smart-money sleeve)
      - B589: vol_above_avg (1.0x) -> vol_spike_12x (1.2x); near_52w_high
        (98pct) -> near_52w_high_95pct (95pct of prior 52w high)
      - B613: docstring reframe + close_in_top_40pct_of_range added
    """
    base_fires = (
        s.get("near_52w_high_95pct", False)
        and s.get("close_above_open", True)
        and s.get("close_in_top_40pct_of_range", False)
        and s.get("vol_spike_12x", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["near_52w_high_95pct", "close_above_open",
         "close_in_top_40pct_of_range", "vol_spike_12x", "smart_money_buy"],
        ["Close >= 95pct of prior 252d high (broader window per B589)",
         "Bullish bar + close in top 40pct of range (B613 a strong-close gate)",
         "Volume >= 1.2x 20d avg (B589 tightened from 1.0x)",
         "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a"])


def strat_52w_high_breakout_with_smart_money_vol_below_long(s):
    """Batch 613 (2026-06-07 owner-directed B-twin for A/B test of (b)
    vol_spike_12x vs vol_below_avg):

    Owner directive: "I am unsure of b and want to A/B test that too."

    A/B-test hypothesis: at the 52-week high with smart-money sponsorship,
    is lower-volume confirmation (Bulkowski 2005 retest-of-resistance
    absorption pattern) MORE or LESS reliable than a high-volume breakout
    bar (vol_spike_12x)?

    Twin strategy: identical to strat_52w_high_breakout_with_smart_money_long
    EXCEPT vol_spike_12x is replaced by vol_below_avg. Cube replay will
    surface the empirical verdict per (strategy x exit) cell. Walker may
    deprecate one twin post-cube based on the result.
    """
    base_fires = (
        s.get("near_52w_high_95pct", False)
        and s.get("close_above_open", True)
        and s.get("close_in_top_40pct_of_range", False)
        and s.get("vol_below_avg", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["near_52w_high_95pct", "close_above_open",
         "close_in_top_40pct_of_range", "vol_below_avg", "smart_money_buy"],
        ["Close >= 95pct of prior 252d high (broader window per B589)",
         "Bullish bar + close in top 40pct of range (B613 a strong-close gate)",
         "Volume BELOW 20d avg (B613 b A/B twin: Bulkowski 2005 retest absorption)",
         "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a"])


# Batch 613 (2026-06-07 owner-directed F3b): SHORT mirror DELETED.
# strat_52w_low_breakdown_with_smart_money_short was added B588 as a
# mechanical inverse but violated feedback_asymmetric_data_sources_break
# _mechanical_inverse - 13F filings are SEC long-only by rule, so the
# "smart-money sell" composite collapsed to a near-silent gate (see helper
# deletion above). No empirical data; not in any cube; safe to delete
# pre-R5 per feedback_r5_paused_pending_stage4_completion.


def strat_squeeze_breakout_with_smart_money_long(s):
    """Squeeze breakout + smart-money buy. Volatility-contraction trade
    with institutional sponsor."""
    base_fires = (
        s.get("squeeze_on_release", False)
        and s.get("close_above_open", True)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["squeeze_on_release", "close_above_open", "smart_money_buy"],
        ["TTM squeeze releasing", "Bullish candle",
         "Smart-money buy confirmation"])


def strat_xs_momentum_with_smart_money_long(s):
    """Cross-sectional momentum (top-decile) + smart-money buy. Jegadeesh-
    Titman 12-1 momentum with smart-money corroboration."""
    base_fires = (
        s.get("xs_momentum_top_decile", False)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["xs_momentum_top_decile", "price_above_ema_200",
         "smart_money_buy"],
        ["XS momentum top decile", "Above 200 EMA",
         "Smart-money buy confirmation"])


def strat_xs_low_beta_with_smart_money_long(s):
    """Cross-sectional low-beta (Frazzini-Pedersen 2014 betting-against-beta)
    + smart-money buy. Pairs the BAB anomaly with smart-money confirmation."""
    base_fires = (
        s.get("xs_low_beta_top_quintile", False)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["xs_low_beta_top_quintile", "price_above_ema_200",
         "smart_money_buy"],
        ["XS low-beta top quintile", "Above 200 EMA",
         "Smart-money buy confirmation"])


def strat_donchian_breakout_with_smart_money_long(s):
    """Donchian 20 breakout + smart-money buy. Classic trend-following
    entry; smart-money confirms the breakout has fundamental backing."""
    base_fires = (
        s.get("dc20_breakout_up", False)
        and s.get("close_above_open", True)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["dc20_breakout_up", "close_above_open", "smart_money_buy"],
        ["Donchian-20 breakout up", "Bullish candle",
         "Smart-money buy confirmation"])


def strat_macd_bullish_with_smart_money_long(s):
    """MACD bullish cross + smart-money buy. Momentum-onset signal with
    institutional/insider sponsor."""
    base_fires = (
        s.get("macd_bullish_cross", False)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["macd_bullish_cross", "price_above_ema_200", "smart_money_buy"],
        ["MACD bullish cross", "Above 200 EMA",
         "Smart-money buy confirmation"])


def strat_pead_with_smart_money_long(s):
    """PEAD (post-earnings-announcement drift) + smart-money composite
    buy. Variant of strat_pead_with_insider_confirmation_long that uses
    the broader smart-money composite (insider + institutional + CFO +
    large-dollar) rather than insider_cluster alone."""
    base_fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["within_pead_window", "pead_positive_surprise",
         "smart_money_buy"],
        ["Within PEAD window", "Positive earnings surprise",
         "Smart-money buy confirmation"])


# ---------------------------------------------------------------------------
# Index rebalance (DEC-370 / Batch 251) - 4 strategies, imported from module
# ---------------------------------------------------------------------------
from backtest.signals.index_rebalance import (
    strat_post_inclusion_drift_long as _strat_post_inclusion_drift_long,
    strat_post_inclusion_reversal_short as _strat_post_inclusion_reversal_short,
    strat_post_deletion_drift_short as _strat_post_deletion_drift_short,
    strat_pre_rebalance_long as _strat_pre_rebalance_long,
)


def strat_post_inclusion_drift_long(s):
    return _strat_post_inclusion_drift_long(s)


def strat_post_inclusion_reversal_short(s):
    return _strat_post_inclusion_reversal_short(s)


def strat_post_deletion_drift_short(s):
    return _strat_post_deletion_drift_short(s)


def strat_pre_rebalance_long(s):
    return _strat_pre_rebalance_long(s)


ALL_STRATEGIES = {
    # ORB stocks-in-play (2 - Batch 211 2026-05-17 owner-approved research review)
    "orb_stocks_in_play_long":      strat_orb_stocks_in_play_long,
    "orb_stocks_in_play_short":     strat_orb_stocks_in_play_short,
    # SMC / ICT family (4 - Batch 210 2026-05-17 owner-approved research review)
    "smc_bos_continuation":         strat_smc_bos_continuation,
    "smc_choch_reversal":           strat_smc_choch_reversal,
    "smc_order_block_bounce":       strat_smc_order_block_bounce,
    "smc_liquidity_sweep_reversal": strat_smc_liquidity_sweep_reversal,
    # ICT Layer 2D first inline-spec pattern (B580 owner directive
    # 2026-06-04). Raschke Street Smarts 1996 Turtle Soup; mean-reversion
    # fade of stop-hunt breakouts. Long + short symmetric per
    # feedback_long_short_inverse_audit.
    "turtle_soup_long":             strat_turtle_soup_long,
    "turtle_soup_short":            strat_turtle_soup_short,
    # ICT Layer 2D second batch (B581 owner directive 2026-06-04):
    # Judas Swing + MMBM/MMSM + Week Opening Gap. 6 new strategies.
    "judas_swing_long":             strat_judas_swing_long,
    "judas_swing_short":            strat_judas_swing_short,
    "mmbm_long":                    strat_mmbm_long,
    "mmsm_short":                   strat_mmsm_short,
    "week_opening_gap_fill_down":   strat_week_opening_gap_fill_down,
    "week_opening_gap_fill_up":     strat_week_opening_gap_fill_up,
    # Pre-FOMC + 8-K event-driven (2 - Batch 224 2026-05-18 owner-approved;
    # buyback_8k_recent_long DELETED Batch 682 per B680 self-critique CC-B
    # population-mixing + B660 zero-fire confirmation)
    "pre_fomc_long_sleeve":                strat_pre_fomc_long_sleeve,
    "pre_fomc_quality_momentum_long":      strat_pre_fomc_quality_momentum_long,
    # Event-driven + quality factor (5 - Batch 222 2026-05-18 owner-approved)
    "insider_cluster_long":                strat_insider_cluster_long,
    "insider_cluster_with_director_long":  strat_insider_cluster_with_director_long,
    "xs_quality_top_quintile_long":        strat_xs_quality_top_quintile_long,
    "xs_momentum_quality_combined":        strat_xs_momentum_quality_combined,
    "pead_with_insider_confirmation_long": strat_pead_with_insider_confirmation_long,
    # Cross-sectional factor strategies (4 - Batch 220 2026-05-18 owner-approved)
    "xs_momentum_top_decile":           strat_xs_momentum_top_decile,
    "xs_momentum_bottom_decile_short":  strat_xs_momentum_bottom_decile_short,
    "xs_low_beta_long":                 strat_xs_low_beta_long,
    "xs_combined_momentum_low_ivol":    strat_xs_combined_momentum_low_ivol,
    # PO3 + multi-TF (9 - Batch 217 2026-05-18 owner-approved)
    "po3_bullish":                  strat_po3_bullish,
    "po3_bearish":                  strat_po3_bearish,
    "po3_htf_aligned_long":         strat_po3_htf_aligned_long,
    "po3_htf_aligned_short":        strat_po3_htf_aligned_short,
    "htf_aligned_breakout_long":    strat_htf_aligned_breakout_long,
    "htf_aligned_breakout_short":   strat_htf_aligned_breakout_short,
    "weekly_bias_pullback_long":    strat_weekly_bias_pullback_long,
    "weekly_bias_pullback_short":   strat_weekly_bias_pullback_short,
    "monthly_bias_momentum_long":   strat_monthly_bias_momentum_long,
    # SMC / ICT expansion (13 - Batch 216 2026-05-18 owner-approved)
    "smc_fvg_retest_long":          strat_smc_fvg_retest_long,
    "smc_fvg_retest_short":         strat_smc_fvg_retest_short,
    "smc_inverse_fvg":              strat_smc_inverse_fvg,
    "smc_breaker_block_short":      strat_smc_breaker_block_short,
    "smc_breaker_block_long":       strat_smc_breaker_block_long,
    "smc_mitigation_block_long":    strat_smc_mitigation_block_long,
    "smc_mitigation_block_short":   strat_smc_mitigation_block_short,
    "smc_discount_long":            strat_smc_discount_long,
    "smc_premium_short":            strat_smc_premium_short,
    "smc_ote_long":                 strat_smc_ote_long,
    "smc_ote_short":                strat_smc_ote_short,
    "smc_equal_highs_sweep_short":  strat_smc_equal_highs_sweep_short,
    "smc_equal_lows_sweep_long":    strat_smc_equal_lows_sweep_long,
    "smc_bos_retest_entry":         strat_smc_bos_retest_entry,
    # PEAD family (2 - Batch 209 2026-05-17 owner-approved research review)
    "pead_long":                    strat_pead_long,
    "pead_short":                   strat_pead_short,
    # Batch 507 (2026-05-31, M6 Path-2 sleeves registered per owner go) -
    # pead_long_high_yoy_growth_only + pead_short_negative_yoy_growth
    # DELETED Batch 682 per B680 self-critique CC-C Pattern W
    # deterministic-subset finding. If YoY-threshold variant needed,
    # implement as parameter on EV-1/EV-2 not separate registry slot.
    # Batch 519 (2026-05-31, P15 sleeves registered per owner directive):
    "squeeze_setup_long":               strat_squeeze_setup_long,
    # Batch 615 -> Batch 620: B-twin strat_squeeze_setup_event_only_long
    # registered B615, DELETED B620 per B619 fire-count finding
    # (~2.5 fires/yr - unrunnable in cube). A/B test of EVENT-only L1c
    # can be answered offline post-cube from strat_squeeze_setup_long's
    # trade log filtered by insider_cluster_active=True at fire bar.
    "short_borrow_trap_avoid":          strat_short_borrow_trap_avoid,
    # Batch 531 (2026-05-31, P17 sleeves activated per owner directive
    # 2026-05-31 "wire in activate truly pending items"). Scaffolded
    # in Batch 522; producer compute_sec_edgar_signals wired below in
    # screen_instrument; modifier helpers wired in
    # backtest/data/smart_money.py + tier-assignment per Batch 531.
    "activist_13d_long":                strat_activist_13d_long,
    "m_and_a_target_long":              strat_m_and_a_target_long,
    # Anchored VWAP family (3 - Batch 208 2026-05-17 owner-approved research review)
    "avwap_252_breakout":           strat_avwap_252_breakout,
    "avwap_50_reclaim":             strat_avwap_50_reclaim,
    "avwap_20high_rejection_short": strat_avwap_20high_rejection_short,
    # Pivot (11) -- B645 (2026-06-09) wired pivot_r3_blowoff_short as
    # Class 7 NEW symmetric mirror of pivot_s3_capitulation (B643
    # redesign) per owner directive (a) from B643+B644 follow-on +
    # feedback_long_short_inverse_audit + feedback_wire_new_strategies
    # _on_the_spot. Both LONG (capitulation) and SHORT (blowoff) marked
    # EXPLORATORY pending Stage 5 cube validation.
    "pivot_s1_bounce":          strat_pivot_s1_bounce,
    "pivot_s2_bounce":          strat_pivot_s2_bounce,
    "pivot_s3_capitulation":    strat_pivot_s3_capitulation,
    "pivot_r3_blowoff_short":   strat_pivot_r3_blowoff_short,
    "pivot_r1_breakout":        strat_pivot_r1_breakout,
    "pivot_r2_continuation":    strat_pivot_r2_continuation,
    "cpr_narrow_bullish":       strat_cpr_narrow_bullish,
    "camarilla_s3_bounce":      strat_camarilla_s3_bounce,
    # B641 W10 (2026-06-09): renamed from camarilla_r3_breakout to
    # camarilla_r4_breakout per external-AI audit Camarilla source-system
    # critique. R3 is the fade level (W9 strat_camarilla_s3_bounce uses
    # it correctly); R4 is the breakout level per Slim Khan / Nick Scott.
    "camarilla_r4_breakout":    strat_camarilla_r4_breakout,
    "prev_day_high_break":      strat_prev_day_high_break,
    "prev_day_low_bounce":      strat_prev_day_low_bounce,
    # Momentum (9)
    "macd_crossover":           strat_macd_crossover,
    "macd_fast_crossover":      strat_macd_fast_crossover,
    "hull_rsi":                 strat_hull_rsi,
    "williams_r_oversold":      strat_williams_r_oversold,
    "roc_burst":                strat_roc_burst,
    "awesome_oscillator":       strat_awesome_oscillator,
    "stochrsi_oversold":        strat_stochrsi_oversold,
    "ppo_crossover":            strat_ppo_crossover,
    "ultimate_oscillator":      strat_ultimate_oscillator,
    # Trend (9)
    "golden_cross_50_200":      strat_golden_cross_50_200,
    "golden_cross_9_21":        strat_golden_cross_9_21,
    "golden_cross_20_50":       strat_golden_cross_20_50,
    "parabolic_sar_flip":       strat_parabolic_sar_flip,
    "tema_dema":                strat_tema_dema,
    "ichimoku_tk_cross":        strat_ichimoku_tk_cross,
    "ichimoku_cloud_breakout":  strat_ichimoku_cloud_breakout,
    "adx_initiation":           strat_adx_initiation,
    "supertrend_macd":          strat_supertrend_macd,
    # Mean Reversion (11)
    "rsi_oversold":             strat_rsi_oversold,
    "rsi9_extreme":             strat_rsi9_extreme,
    "rsi21_slow":               strat_rsi21_slow,
    "rsi_overbought_short":     strat_rsi_overbought_short,
    "mfi_oversold":             strat_mfi_oversold,
    "cmf_flip":                 strat_cmf_flip,
    "bollinger_lower":          strat_bollinger_lower,
    "bollinger_tight":          strat_bollinger_tight,
    "bollinger_upper_short":    strat_bollinger_upper_short,
    "keltner_lower":            strat_keltner_lower,
    "stoch_oversold":           strat_stoch_oversold,
    # Breakout (6)
    "squeeze_breakout":         strat_squeeze_breakout,
    "volume_spike_breakout":    strat_volume_spike_breakout,
    "52w_high_breakout":        strat_52w_high_breakout,
    # B586 (2026-06-04 owner-directed pullback variants for 52w pair):
    "52w_high_breakout_pullback_long":   strat_52w_high_breakout_pullback_long,
    "52w_low_breakdown_pullback_short":  strat_52w_low_breakdown_pullback_short,
    "inside_bar_breakout":      strat_inside_bar_breakout,
    "force_index_breakout":     strat_force_index_breakout,
    "donchian_10_breakout":     strat_donchian_10_breakout,
    # Candle (6)
    "morning_star":             strat_morning_star,
    "bullish_engulfing_support": strat_bullish_engulfing_support,
    "doji_at_support":          strat_doji_at_support,
    "doji_at_resistance_short": strat_doji_at_resistance_short,
    "three_white_soldiers":     strat_three_white_soldiers,
    # B636 (2026-06-08 owner-directed Class 7 NEW per Stage 4 walk of
    # three_white_soldiers): symmetric bearish-reversal mirror per
    # feedback_long_short_inverse_audit + feedback_wire_new_strategies
    # _on_the_spot. Nison canonical bearish reversal pattern.
    "three_black_crows_short":  strat_three_black_crows_short,
    "shooting_star_short":      strat_shooting_star_short,
    # evening_star_short DELETED Batch 639 (2026-06-09) - strictly redundant
    # with strat_morning_star SHORT post option-2 reconciliation.
    # Batch 685 (2026-06-10 owner-approved Class 7 NEW per B683 self-critique
    # missing-inverse audit): hammer at support is canonical Nison 1991
    # 1-bar bullish reversal mirror to shooting_star_short.
    "hammer_at_support_long":   strat_hammer_at_support_long,
    # Confluence (9)
    "rsi_volume_200ema":        strat_rsi_volume_200ema,
    "macd_ichimoku":            strat_macd_ichimoku,
    "bb_squeeze_volume":        strat_bb_squeeze_volume,
    "pivot_fib_confluence":     strat_pivot_fib_confluence,
    "golden_cross_volume":      strat_golden_cross_volume,
    "cpr_narrow_momentum":      strat_cpr_narrow_momentum,
    "camarilla_rsi_obv":        strat_camarilla_rsi_obv,
    "supertrend_ichimoku_adx":  strat_supertrend_ichimoku_adx,
    "williams_stoch_dual":      strat_williams_stoch_dual,
    # Dedicated shorts  -  Trend (4)
    "death_cross_50_200_volume":    strat_death_cross_50_200_volume,
    "supertrend_macd_short":        strat_supertrend_macd_short,
    "ichimoku_cloud_breakdown":     strat_ichimoku_cloud_breakdown,
    "parabolic_sar_flip_short":     strat_parabolic_sar_flip_short,
    # Dedicated shorts  -  Momentum (3)
    "macd_crossover_short":         strat_macd_crossover_short,
    "hull_rsi_short":               strat_hull_rsi_short,
    "stochrsi_overbought_short":    strat_stochrsi_overbought_short,
    # Dedicated shorts  -  Breakdown (3) - Batch 592 restored donchian_breakdown_short
    "donchian_breakdown_short":     strat_donchian_breakdown_short,
    "52w_low_breakdown":            strat_52w_low_breakdown,
    "prev_day_low_breakdown":       strat_prev_day_low_breakdown,
    # Batch 591 (2026-06-04) added tight-long mirrors to restore symmetry;
    # Batch 592 (2026-06-05) owner correction kept both tight pairs coexisting:
    "donchian_breakout_long":           strat_donchian_breakout_long,
    "donchian_breakout_retest_long":    strat_donchian_breakout_retest_long,
    # Dedicated shorts  -  Confluence (2)
    "camarilla_rsi_obv_short":      strat_camarilla_rsi_obv_short,
    "cpr_narrow_momentum_short":    strat_cpr_narrow_momentum_short,
    # Break-and-Retest (5)  -  BUG-111 / DEC-355 through DEC-362 chart pattern spec
    "dc20_break_retest":            strat_dc20_break_retest,
    "r1_break_retest":              strat_r1_break_retest,
    "52wh_break_retest":            strat_52wh_break_retest,
    # Batch 605 (2026-06-06) Class 7 NEW symmetric inverse per F1 walk:
    "52wl_break_retest_short":      strat_52wl_break_retest_short,
    "break_retest_volume":          strat_break_retest_volume,
    "break_retest_confluence":      strat_break_retest_confluence,
    # -----------------------------------------------------------------------
    # Batch 277 (2026-05-20 owner-approved option C): New strategies from
    # Batches 252-255 moved to BACK of dict. Stage B v2 forensic showed
    # these newly-registered strategies were winning dedup over established
    # profitable strategies (rsi_oversold, williams_r_oversold, etc.) due
    # to their dict-insertion-order position at the FRONT (Batches 252-255
    # were appended at top during registration). Moving them here lets the
    # established roster win dedup until these new strategies prove edge
    # at larger scale (Stage C / D1 full T1a). No logic change - pure
    # ordering. Strategies remain registered + can still fire when no
    # earlier strategy claims the same ticker-day.
    # -----------------------------------------------------------------------
    # Chart patterns (5 - Batch 252 2026-05-20 Phase 1C+ Wave 1 / DEC-355-362)
    "head_and_shoulders_bottom_long":   strat_head_and_shoulders_bottom_long,
    "double_bottom_long":               strat_double_bottom_long,
    "cup_and_handle_long":              strat_cup_and_handle_long,
    "flag_bull_long":                   strat_flag_bull_long,
    "triangle_ascending_long":          strat_triangle_ascending_long,
    # Batch 685 (2026-06-10 owner-approved Class 7 NEW per B683 self-critique
    # missing-inverse audit): Edwards-Magee 1948 + Bulkowski 2005 SHORT mirrors.
    "head_and_shoulders_top_short":     strat_head_and_shoulders_top_short,
    "triangle_descending_short":        strat_triangle_descending_short,
    # Batch 686 (2026-06-10 owner-approved Class 7 NEW; deferred from B685
    # pending inverted-cup producer methodology work; scoped + executed B686):
    # Bulkowski 2005 inverted cup-and-handle (rounded top with handle) bearish
    # mirror of CP-1 strat_cup_and_handle_long. Producer detect_inverted_cup
    # _and_handle in chart_patterns.py.
    "inverted_cup_and_handle_short":    strat_inverted_cup_and_handle_short,
    # BUG-111 retest variants (Batch 329 2026-05-25 owner-approved option b):
    # 6 explicit _retest variants for breakouts that previously fired only
    # on the initial break. Reuses resistance_break_retest / support_break_retest
    # primitive from technical.compute_break_retest_signals.
    # Batch 599 deleted donchian_20_breakout_retest (B596 convergence
    # option 2 - duplicate of explicit pair donchian_breakout_retest_long
    # + donchian_breakdown_retest_short).
    # Batch 592 restored donchian_breakdown_retest_short:
    "donchian_breakdown_retest_short":  strat_donchian_breakdown_retest_short,
    # volume_spike_breakout_retest DELETED Batch 682 per B620 precedent +
    # B680 self-critique CC-B (0.01/yr B621 estimator FAIL_FIRE_STARVED).
    "cup_and_handle_retest_long":       strat_cup_and_handle_retest_long,
    "flag_bull_retest_long":            strat_flag_bull_retest_long,
    # Batch 607 (2026-06-07) Class 7 NEW symmetric inverse per F1 walk:
    "flag_bear_retest_short":           strat_flag_bear_retest_short,
    "triangle_ascending_retest_long":   strat_triangle_ascending_retest_long,
    # Wave 3 13F-based (Batch 330 2026-05-25 owner-approved Path C): 3 of ~10
    # planned 13F-trigger strategies. Producer injection at screen_instrument
    # adds institutional_signal / strong_buy / buy / negative / new_positions /
    # increased to per-ticker signals dict.
    "institutional_cluster_long":        strat_institutional_cluster_long,
    "institutional_buy_momentum_long":   strat_institutional_buy_momentum_long,
    # SM-9 strat_institutional_distribution_short DELETED Batch 670 per cluster-
    # walk reviewer F2 + Pattern C deletion disposition. Replaced by Class 7 NEW
    # strat_simple_below_ema_50_short registered below in momentum_trend section.
    "simple_below_ema_50_short":         strat_simple_below_ema_50_short,
    # Wave 3 Batch 331 (2026-05-25): 4 more 13F-driven strategies combining
    # the producer signal with complementary entry triggers (RSI oversold,
    # break-retest, insider co-confirmation, volume spike).
    "institutional_oversold_long":             strat_institutional_oversold_long,
    "institutional_breakout_confirmation_long": strat_institutional_breakout_confirmation_long,
    # Batch 611 (2026-06-07) DELETED institutional_breakdown_confirmation_short
    # (mechanical long/short symmetry applied to asymmetric 13F data source -
    # false economics + reintroduced silent-gap pattern; see external-AI
    # critique addressed in B611).
    "institutional_insider_combo_long":        strat_institutional_insider_combo_long,
    "institutional_volume_confirmation_long":  strat_institutional_volume_confirmation_long,
    # Wave 3 classification_change (Batch 332 2026-05-25 Path C): 3 strategies
    # firing on recent GICS reclassification events via sector_history.csv.
    "classification_change_recent_long":         strat_classification_change_recent_long,
    "classification_change_to_tech_long":        strat_classification_change_to_tech_long,
    "classification_change_to_defensive_short":  strat_classification_change_to_defensive_short,
    # Wave 3 classification_change Batch 335 (2026-05-25 Path C): 4 more
    # combining the producer signal with vol / momentum / from-tech inverse /
    # break-retest sponsorship.
    "classification_change_volume_long":     strat_classification_change_volume_long,
    "classification_change_momentum_long":   strat_classification_change_momentum_long,
    "classification_change_from_tech_short": strat_classification_change_from_tech_short,
    "classification_change_breakout_long":   strat_classification_change_breakout_long,
    # Wave 3 Batch 337 (2026-05-25 Path C): 3 more classification_change
    # (completing category at 10/10) + 3 more persistence variants.
    "classification_change_with_institutional_long": strat_classification_change_with_institutional_long,
    "classification_change_with_insider_long":       strat_classification_change_with_insider_long,
    "classification_change_oversold_long":           strat_classification_change_oversold_long,
    # Wave 3 persistence (Batch 333 2026-05-25 Path C): 3 strategies using
    # the Batch 330 producer's institutional_increased / institutional_new_positions
    # counts. Single-quarter persistence proxies; true multi-quarter
    # precompute queued as Batch 333b.
    "institutional_persistent_holders_long":  strat_institutional_persistent_holders_long,
    "institutional_strong_conviction_long":   strat_institutional_strong_conviction_long,
    # SM-23 strat_institutional_capitulation_short DELETED Batch 670 per
    # cluster-walk reviewer F2 + F3 + Pattern C deletion disposition. Replaced
    # by Class 7 NEW strat_vol_spike_2x_below_ema_50_short registered below in
    # momentum_trend section.
    "vol_spike_2x_below_ema_50_short":        strat_vol_spike_2x_below_ema_50_short,
    # Wave 3 Batch 336 (2026-05-25 Path C): 3 more 13F + 1 more persistence,
    # completing 13F at 10/10. Combines Batch 330 producer with director /
    # officer insider keys (Batch 222 insider_buying producer).
    "institutional_high_conviction_long":         strat_institutional_high_conviction_long,
    "institutional_with_directors_long":          strat_institutional_with_directors_long,
    "institutional_with_officers_long":           strat_institutional_with_officers_long,
    "institutional_persistence_momentum_long":    strat_institutional_persistence_momentum_long,
    # Wave 3 Batch 337 (Path C) persistence trio.
    "institutional_persistence_breakout_long":    strat_institutional_persistence_breakout_long,
    "institutional_persistence_volume_long":      strat_institutional_persistence_volume_long,
    "institutional_persistence_oversold_long":    strat_institutional_persistence_oversold_long,
    # Wave 3 Batch 338 (Path C final): completes persistence at 10/10
    # (Wave 3 total 30/30).
    "institutional_recent_init_momentum_long":    strat_institutional_recent_init_momentum_long,
    "institutional_recent_init_volume_long":      strat_institutional_recent_init_volume_long,
    "institutional_increased_with_directors_long": strat_institutional_increased_with_directors_long,
    # Batch 344 (333b multi-quarter persistence) 2026-05-25: 2 TRUE multi-
    # quarter persistence strategies reading the new precompute via
    # institutional_persistence_consumer. Distinct from Batch 333-338
    # single-quarter proxies.
    "institutional_multi_quarter_persistence_long": strat_institutional_multi_quarter_persistence_long,
    "institutional_committed_growth_long":          strat_institutional_committed_growth_long,
    # Index rebalance (4 - Batch 252 2026-05-20 / DEC-370)
    "post_inclusion_drift_long":        strat_post_inclusion_drift_long,
    "post_inclusion_reversal_short":    strat_post_inclusion_reversal_short,
    "post_deletion_drift_short":        strat_post_deletion_drift_short,
    "pre_rebalance_long":               strat_pre_rebalance_long,
    # Pairs trading (2 - Batch 253 2026-05-20 / DEC-369)
    "pairs_mean_reversion_long":        strat_pairs_mean_reversion_long,
    "pairs_mean_reversion_short":       strat_pairs_mean_reversion_short,
    # News sentiment (4 - Batch 253 + Batch 467 P10 2026-05-29)
    "news_sentiment_long":              strat_news_sentiment_long,
    "news_sentiment_shift_long":        strat_news_sentiment_shift_long,
    "news_momentum_long":               strat_news_momentum_long,
    "news_reversal_short":              strat_news_reversal_short,
    # Batch 603 (2026-06-05) Class 7 NEW symmetric inverses per owner walk:
    "news_momentum_short":              strat_news_momentum_short,
    "news_reversal_long":               strat_news_reversal_long,
    # SM1 smart-money sleeves (10 - Batch 487 2026-05-30)
    "bollinger_tight_with_smart_money_long":    strat_bollinger_tight_with_smart_money_long,
    "mfi_oversold_with_smart_money_long":       strat_mfi_oversold_with_smart_money_long,
    "rsi_oversold_with_smart_money_long":       strat_rsi_oversold_with_smart_money_long,
    "52w_high_breakout_with_smart_money_long":  strat_52w_high_breakout_with_smart_money_long,
    # B613 (2026-06-07 owner-directed B-twin for A/B test of (b)
    # vol_spike_12x vs vol_below_avg per Bulkowski 2005 retest hypothesis)
    "52w_high_breakout_with_smart_money_vol_below_long":
        strat_52w_high_breakout_with_smart_money_vol_below_long,
    # B613 (2026-06-07 owner-directed F3b): SHORT mirror DELETED -
    # asymmetric-data violation per feedback_asymmetric_data_sources_break_
    # mechanical_inverse; 13F is SEC long-only by rule.
    "squeeze_breakout_with_smart_money_long":   strat_squeeze_breakout_with_smart_money_long,
    "xs_momentum_with_smart_money_long":        strat_xs_momentum_with_smart_money_long,
    "xs_low_beta_with_smart_money_long":        strat_xs_low_beta_with_smart_money_long,
    "donchian_breakout_with_smart_money_long":  strat_donchian_breakout_with_smart_money_long,
    "macd_bullish_with_smart_money_long":       strat_macd_bullish_with_smart_money_long,
    "pead_with_smart_money_long":               strat_pead_with_smart_money_long,
    # Calendar effects (4 - Batch 254 2026-05-20 / DEC-368)
    "totm_long":                        strat_totm_long,
    "pre_holiday_long":                 strat_pre_holiday_long,
    "january_effect_small_cap_long":    strat_january_effect_small_cap_long,
    "halloween_seasonal_long":          strat_halloween_seasonal_long,
    # Cross-asset (5 - Batch 254 2026-05-20 / DEC-369)
    "risk_off_bond_equity_short":       strat_risk_off_bond_equity_short,
    "vix_backwardation_long":           strat_vix_backwardation_long,
    "sector_rotation_defensive_long":   strat_sector_rotation_defensive_long,
    "gold_silver_risk_off_long":        strat_gold_silver_risk_off_long,
    "dxy_headwind_multinational_short": strat_dxy_headwind_multinational_short,
    # Volume profile / VPVR (3 - Batch 255 2026-05-20 / Batch 233 module)
    "poc_magnet_long":                  strat_poc_magnet_long,
    "value_area_breakout_long":         strat_value_area_breakout_long,
    "naked_poc_retest_long":            strat_naked_poc_retest_long,
}

STRATEGY_CATEGORIES = {
    name: fn({}).__class__  # placeholder  -  category stored in each fn
    for name, fn in ALL_STRATEGIES.items()
}


def validate_strategy_roster() -> dict:
    """Batch 270 (Tier 2.3 of T1A_COMPREHENSIVE_REVIEW_2026_05_20 §7):
    Roster sanity gate at startup. Verifies every entry in ALL_STRATEGIES is
    a callable function that returns a dict on empty-signals input. Catches
    the failure mode that hid in plain sight during the 2026-05-19 T1a run:
    Batches 252-255 registered 25 new strategies in the dict 16 hours AFTER
    the backtest launched, but the running process kept the stale roster
    (148 keys without the new ones) and silently produced zero candidates
    for all 25.

    Returns a summary dict for logging. Raises RuntimeError if any strategy
    is unloadable - fail fast at startup rather than silently producing
    zero candidates across a 17h run.
    """
    from backtest.config import DEPRECATED_STRATEGIES as _DEPRECATED
    from backtest.config import STRATEGIES_DISABLED_MISSING_PRODUCER as _MISSING_PRODUCER
    _BLOCKED = _DEPRECATED | _MISSING_PRODUCER
    summary = {
        "total_registered":         len(ALL_STRATEGIES),
        "deprecated_count":         sum(1 for k in ALL_STRATEGIES if k in _DEPRECATED),
        "missing_producer_count":   sum(1 for k in ALL_STRATEGIES if k in _MISSING_PRODUCER),
        "active_count":             sum(1 for k in ALL_STRATEGIES if k not in _BLOCKED),
        "callable_ok":              0,
        "callable_failed":          [],
        "load_errors":              [],
    }
    for name, fn in ALL_STRATEGIES.items():
        if not callable(fn):
            summary["callable_failed"].append((name, "not_callable"))
            continue
        try:
            result = fn({})
            if not isinstance(result, dict):
                summary["callable_failed"].append((name, f"returned_{type(result).__name__}"))
                continue
            if "fires" not in result:
                summary["callable_failed"].append((name, "missing_fires_key"))
                continue
            summary["callable_ok"] += 1
        except Exception as exc:
            summary["load_errors"].append((name, str(exc)[:80]))
    if summary["callable_failed"] or summary["load_errors"]:
        raise RuntimeError(
            f"Strategy roster validation failed at startup. "
            f"callable_failed={summary['callable_failed']} "
            f"load_errors={summary['load_errors']}. "
            f"Fix or remove the strategies before launching a backtest."
        )
    return summary


# -----------------------------------------------------------------------------
# ENTRY ZONE VALIDATOR
# -----------------------------------------------------------------------------

def validate_entry_zone(
    open_price: float,
    signal_close: float,
    atr: float,
    category: str,
    direction: str,
) -> tuple[bool, str]:
    """Check if the next-day open is within the acceptable entry zone.

    Returns (valid: bool, reason: str).

    BUG-060 fix 2026-05-13: for short entries, only ADVERSE gap-ups are rejected.
    A gap-down on a short is FAVORABLE (lower entry = more downside room) and must
    NOT be filtered out. Previous code incorrectly applied gap_down > mult*ATR as a
    short-entry rejection, understating short strategy performance. Correct logic:
    - Long  entry: reject excessive gap-UP   (adverse: entered above signal level)
    - Short entry: reject excessive gap-UP   (adverse: stock moved against the short)
    - Long  entry: gap-down is acceptable    (favorable: better long entry price)
    - Short entry: gap-down is acceptable    (favorable: lower short entry price)
    """
    from backtest.config import ENTRY_GAP_ATR_MULT
    mult    = ENTRY_GAP_ATR_MULT.get(category, 1.5)
    gap_atr = (open_price - signal_close) / atr if atr > 0 else 0
    gap_pct = (open_price - signal_close) / signal_close * 100 if signal_close > 0 else 0

    if direction == "long":
        # Reject excessive gap-UP for longs (opened too far above signal close)
        if gap_atr > mult:
            return False, f"gap_up_{gap_pct:.1f}pct_exceeds_{mult}x_atr_limit"
        return True, f"entry_valid_gap_{gap_pct:.1f}pct"
    else:  # short
        # BUG-060: reject only adverse gap-UPs for shorts; gap-downs are favorable
        if gap_atr > mult:
            return False, f"short_adverse_gap_up_{gap_pct:.1f}pct_exceeds_{mult}x_atr_limit"
        return True, f"entry_valid_gap_{gap_pct:.1f}pct"


# -----------------------------------------------------------------------------
# SCREENING PIPELINE
# -----------------------------------------------------------------------------

def screen_lead_lag_sector(
    ohlcv_dict: dict,
    info_dict: dict,
    as_of: date,
) -> list:
    """DEC-458: Lead-lag intra-sector momentum cross-ticker candidates.

    Groups tickers by GICS sector, ranks by 5-day momentum (LEAD_LAG_INTRA_SECTOR_STRATEGY
    spec from config.py). For sectors with >=4 members: fires long on the bottom 2-3
    laggards (mean-reversion rotation toward sector leader).
    ETF-proxy sectors excluded so rotation targets are individual equities only.
    """
    from backtest.config import LEAD_LAG_INTRA_SECTOR_STRATEGY, ATR_FALLBACK_PCT
    lookback = LEAD_LAG_INTRA_SECTOR_STRATEGY["lookback_days"]

    ETF_SECTORS = {
        "Broad Market", "Volatility", "Fixed Income",
        "Commodities", "Emerging Markets", "International", "Small Cap",
    }

    sector_members: dict[str, list] = {}
    for ticker, df in ohlcv_dict.items():
        if df is None or len(df) < lookback + 2:
            continue
        info = info_dict.get(ticker, {})
        sector = info.get("sector") or info.get("Sector") or "Unknown"
        if sector in ETF_SECTORS or sector == "Unknown":
            continue
        try:
            close_now  = float(df["close"].iloc[-1])
            close_back = float(df["close"].iloc[-(lookback + 1)])
            momentum   = (close_now - close_back) / close_back if close_back > 0 else 0.0
        except (IndexError, ValueError, ZeroDivisionError):
            continue
        sector_members.setdefault(sector, []).append(
            {"ticker": ticker, "df": df, "momentum": momentum}
        )

    candidates = []
    for sector, members in sector_members.items():
        if len(members) < 4:
            continue
        members.sort(key=lambda x: x["momentum"], reverse=True)
        leader   = members[0]
        n        = len(members)
        lag_count = 3 if n >= 5 else 2
        laggards  = members[n - lag_count:]

        for rank_from_bottom, lag in enumerate(reversed(laggards), 1):
            ticker = lag["ticker"]
            df_lag = lag["df"]
            close  = float(df_lag["close"].iloc[-1])
            try:
                atr = float(
                    (df_lag["high"] - df_lag["low"]).rolling(14).mean().iloc[-1]
                )
                if not (atr > 0):
                    atr = close * ATR_FALLBACK_PCT
            except Exception:
                atr = close * ATR_FALLBACK_PCT
            strat_entry = {
                "strategy":        "lead_lag_sector_rotation",
                "direction":       "long",
                "category":        "rotation",
                "signals_used":    ["sector_5d_momentum_rank", "intra_sector_lag"],
                "context_bullets": [
                    f"Sector {sector}: laggard rank {rank_from_bottom} of {n}",
                    f"5d return {lag['momentum']:.1%} vs leader {leader['ticker']} ({leader['momentum']:.1%})",
                    "Rotation signal: mean-reversion toward sector leader",
                ],
            }
            candidates.append({
                "ticker":             ticker,
                "as_of":              as_of,
                "liquidity_ok":       True,
                "fail_reason":        None,
                "strategies":         [strat_entry],
                "long_strategies":    [dict(strat_entry)],
                "short_strategies":   [],
                "avoid_strategies":   [],
                "strategy_count":     1,
                "long_count":         1,
                "short_count":        0,
                "avoid_count":        0,
                "tech_signal_count":  0,
                "signals":            {},
                "last_close":         round(close, 4),
                "atr":                round(atr, 4),
                "initial_stop_long":  round(close * 0.90, 4),
                "initial_stop_short": round(close * 1.10, 4),
            })
    return candidates


def screen_instrument(
    ticker: str,
    df: pd.DataFrame,
    info: dict,
    as_of: date,
    regime: str = "neutral",
    vix_value: float = None,
    vix_history: list = None,
    xs_features: dict = None,
    panel_signals: dict = None,
) -> dict:
    """
    Run single instrument through full pipeline.
    Returns candidate dict with all strategies triggered, signals, and bullets.

    Batch 204 (Bollinger optimization 2026-05-17): optional VIX context
    kwargs flow through to compute_macro_overlays so regime-aware
    strategies (bollinger_*) can read vix_percentile/vix_band from the
    signals dict. When None, behavior is unchanged.

    Batch 220 (cross-sectional infrastructure 2026-05-18): xs_features
    is the per-ticker dict from compute_cross_sectional_features (called
    once in screen_universe before iteration). Merged into the signals
    dict so factor strategies can read xs_momentum_decile, xs_beta_decile,
    xs_ivol_decile, xs_max_anomaly_decile. None when universe-wide
    compute was not run (backward-compatible).
    """
    # Liquidity already checked at universe load time (annually)
    # Light check: price > 0 and sufficient history only
    if df is None or len(df) < 30:
        return {"ticker": ticker, "as_of": as_of, "liquidity_ok": False,
                "fail_reason": "insufficient_history", "strategies": []}

    # Batch 541 OPT-D Phase 2: try pre-computed signals cache FIRST.
    # If hit, skip compute_all_signals entirely (~25ms savings per
    # call). Falls back to compute path on miss (backward-compat for
    # tickers/dates not yet materialized).
    signals = None
    try:
        from backtest.config import USE_PRECOMPUTED_SIGNALS
    except Exception:
        USE_PRECOMPUTED_SIGNALS = False
    if USE_PRECOMPUTED_SIGNALS:
        try:
            from backtest.signals.precomputed_cache import (
                load_precomputed_signals,
            )
            precomp = load_precomputed_signals(ticker, as_of)
            if precomp is not None:
                signals = precomp
        except Exception:
            signals = None

    if signals is None:
        # Batch 538 OPT-B Phase 7: when caller pre-computed panel signals
        # (RSI/EMA/SMA/simple_returns via technical_panel), skip those in
        # the per-ticker compute_all_signals call + seed signals dict with
        # the panel results upfront. Net: same final signal set, 1 panel
        # op replaces 388 per-ticker function calls.
        if panel_signals:
            skip = {"rsi", "ema_sma", "simple_returns"}
            signals = compute_all_signals(df, skip_indicators=skip)
            signals.update(panel_signals)
        else:
            signals = compute_all_signals(df)
    if not signals:
        return {"ticker": ticker, "as_of": as_of, "liquidity_ok": True,
                "fail_reason": "no_signals", "strategies": []}
    # BUG-290 fix (Batch 314 2026-05-24): cap_band producer. Owner-mandated
    # taxonomy: micro <$300M / small $300M-$2B / mid $2B-$10B / large
    # $10B-$200B / mega >=$200B. Previously strat_january_effect_long was a
    # silent-gap consumer (always falsey because no producer). info dict
    # already carries Polygon-reference market_cap (DEC-440).
    signals["cap_band"] = cap_band_from_market_cap(info.get("market_cap"))
    # Batch 204: layer macro overlays (VIX percentile + band) so strategies
    # can read regime-aware fields inline. No-op when vix_value/history None.
    if vix_value is not None and vix_history is not None:
        from backtest.signals.technical import compute_macro_overlays
        signals = compute_macro_overlays(signals, vix_value, vix_history)
    # Batch 209: PEAD signals (post-earnings drift). No-op when financials
    # prefetch missing for this ticker. Strategy gates inside strat_pead_*
    # check within_pead_window / pead_positive_surprise / etc.
    try:
        from backtest.signals.pead import compute_pead_signals
        pead = compute_pead_signals(ticker, df, as_of)
        if pead:
            signals.update(pead)
    except Exception as _e:
        _log_silent_producer_failure("pead", _e)
    # Batch 507 (2026-05-31, M6 Path-2 sleeves wired per owner directive):
    # YoY-growth surprise signal layered on top of PEAD. Emits
    # yoy_surprise_high / yoy_surprise_negative consumed by
    # strat_pead_long_high_yoy_growth_only + strat_pead_short_negative_yoy_growth.
    # Graceful empty when PEAD data missing (degrades same as PEAD).
    try:
        from backtest.signals.earnings_surprise_yoy import compute_yoy_surprise_signal
        yoy_signal = compute_yoy_surprise_signal(ticker, df, as_of)
        if yoy_signal:
            signals.update(yoy_signal)
    except Exception as _e:
        _log_silent_producer_failure("earnings_surprise_yoy", _e)
    # Batch 519 (2026-05-31, P15 sleeves wired per owner directive):
    # FINRA short-interest signals -- short_interest_pct + days_to_cover.
    # Consumed by strat_squeeze_setup_long (long entry when high SI +
    # bullish breakout) + strat_short_borrow_trap_avoid (avoid-direction
    # gate when DTC > 5 days; blocks short entries on hard-to-borrow
    # names). Graceful empty when ticker missing from
    # data_prefetch/finra/short_interest/ cache (Batch 516 populated
    # 1926 universe tickers).
    try:
        from backtest.signals.short_interest import compute_short_interest_signals
        si_signal = compute_short_interest_signals(ticker, as_of)
        if si_signal:
            signals.update(si_signal)
    except Exception as _e:
        _log_silent_producer_failure("short_interest", _e)
    # Batch 222: insider buying cluster signals (Quiver SEC Form 4).
    # No-op when global insiders parquet missing or ticker has no
    # qualifying transactions in lookback.
    try:
        from backtest.signals.insider_buying import compute_insider_cluster_signals
        insider = compute_insider_cluster_signals(ticker, as_of)
        if insider:
            signals.update(insider)
    except Exception as _e:
        _log_silent_producer_failure("insider_buying", _e)
    # Batch 332 (2026-05-25 owner-approved Path C Wave 3 classification_change):
    # inject recent-classification-change signals into per-ticker signals
    # dict. Reads sector_history.csv via universe.get_classification_change_signals.
    # No-op when ticker has no qualifying change row in 90-day lookback.
    try:
        from backtest.data.universe import get_classification_change_signals
        cc_out = get_classification_change_signals(ticker, as_of)
        if cc_out:
            signals.update(cc_out)
    except Exception as _e:
        # Batch 416 (2026-05-28): rate-limited logging replaces silent pass.
        # Without this, a producer failure on AWS / Hetzner was undetectable
        # post-run (29,159 trades, 0 classification_* keys, 0 visible errors).
        _log_silent_producer_failure("classification_change", _e)
    # Batch 330 (2026-05-25 owner-approved Path C Wave 3): inject
    # institutional 13F signal into the per-ticker signals dict so
    # screener strategies can gate on it as the PRIMARY trigger.
    # Previously, institutional_signal was computed post-screen in the
    # engine (smart_money_score call at backtest.py:1309) and only used
    # for tier adjustment - NOT for strategy firing.
    # Cohen-Frazzini-Malloy 2008 RFS: institutional new-buys forecast
    # 1-month alpha; Bushee-Goodman 2007 JAR: cluster-buys particularly.
    try:
        from backtest.data.smart_money import institutional_signal
        inst = institutional_signal(ticker, as_of)
        if inst and isinstance(inst, dict):
            sig_kind = inst.get("signal", "none")
            signals["institutional_signal"] = sig_kind
            signals["institutional_strong_buy"] = sig_kind == "strong_buy"
            signals["institutional_buy"] = sig_kind in ("buy", "strong_buy")
            signals["institutional_negative"] = sig_kind == "negative"
            signals["institutional_new_positions"] = int(inst.get("new_pos", 0) or 0)
            signals["institutional_increased"] = int(inst.get("increased", 0) or 0)
    except Exception as _e:
        _log_silent_producer_failure("institutional_signal", _e)
    # Batch 344 (333b consumer) 2026-05-25: inject TRUE multi-quarter
    # persistence metrics from the offline precompute at
    # data_prefetch/derived/institutional_persistence_t1a/{YYYY-01-01}.parquet.
    # Producer is module-level cached; reads the most recent snapshot
    # <= as_of. Keys emitted (all absent when precompute missing):
    #   persistent_holders_4q       int (funds held >=4 consecutive quarters)
    #   persistent_holders_8q       int (funds held >=8 consecutive quarters)
    #   avg_position_age_quarters   float
    #   committed_growth_holders    int
    #   total_active_holders        int
    # Yan-Zhang 2009 RFS: cross-fund consensus over multiple quarters
    # forecasts alpha at the 1-3 month horizon.
    try:
        from backtest.signals.institutional_persistence_consumer import (
            compute_persistence_signals,
        )
        pers = compute_persistence_signals(ticker, as_of)
        if pers:
            signals.update(pers)
    except Exception as _e:
        _log_silent_producer_failure("institutional_persistence", _e)
    # Batch 224: macro event signals (pre-FOMC proximity) + recent 8-K
    # filing flag (buyback proxy). Pre-FOMC signals are universe-wide
    # (same value for all tickers on a given day); 8-K is per-ticker.
    try:
        from backtest.signals.macro_events import (
            compute_pre_fomc_signals,
            compute_recent_8k_signal,
        )
        pre_fomc = compute_pre_fomc_signals(as_of)
        if pre_fomc:
            signals.update(pre_fomc)
        recent_8k = compute_recent_8k_signal(ticker, as_of)
        if recent_8k:
            signals.update(recent_8k)
    except Exception as _e:
        _log_silent_producer_failure("macro_events", _e)
    # Batch 210: SMC / ICT signals via vendored smartmoneyconcepts library.
    # Returns empty dict when library unavailable or insufficient history.
    try:
        from backtest.signals.smc_ict import compute_smc_signals
        # B555 OPT-C Phase 4: pass ticker so compute_smc_signals can
        # read the 6 SMC primitives from the panel cache (primed at
        # engine init from full per-ticker OHLCV) instead of recomputing
        # via the vendored library on every (ticker, as_of) call.
        smc_out = compute_smc_signals(df, ticker=ticker)
        if smc_out:
            signals.update(smc_out)
        else:
            # Batch 416 (2026-05-28): empty-output diagnostic. The AWS cube
            # run found 0 smc_* keys in 29,159 trades despite the function
            # returning 28 keys when called directly in local Python. Log
            # the first empty-return per process so the AWS rerun's logs
            # reveal whether the library import failed, vendored path was
            # missing, or some other silent gap.
            _log_silent_producer_empty("smc_ict.compute_smc_signals")
    except Exception as _e:
        _log_silent_producer_failure("smc_ict", _e)
    # B581 (2026-06-04): wire ICT custom producers (PO3 + week-open gap)
    # per owner inline-spec for MMBM/MMSM + Week Opening Gap. Producers
    # are additive - emit new keys only consumed by the 4 new B581
    # strategies (mmbm_long, mmsm_short, week_opening_gap_fill_down,
    # week_opening_gap_fill_up). No existing strategies depend on them.
    try:
        from backtest.signals.ict_producers import (
            compute_po3_signals, compute_week_opening_gap_signals,
        )
        po3_out = compute_po3_signals(df)
        if po3_out:
            signals.update(po3_out)
        wog_out = compute_week_opening_gap_signals(df)
        if wog_out:
            signals.update(wog_out)
    except Exception as _e:
        _log_silent_producer_failure("ict_producers", _e)
    # B586 (2026-06-04 owner directive 52w_high_breakout walk): sector
    # strength filter producer. Reads stock's sector via get_sector_pit
    # + maps to sector-SPDR ETF + compares 20d return vs SPY.
    # Currently consumed only by strat_52w_high_breakout. Producer is
    # ADDITIVE; no impact on existing strategies.
    try:
        from backtest.signals.sector_strength import compute_sector_strength_signals
        from backtest.data.universe import get_sector_pit
        # PIT-correct sector resolution
        sector = get_sector_pit(ticker, as_of) if as_of else None
        if sector and sector != "Unknown":
            ss_out = compute_sector_strength_signals(sector, as_of)
            if ss_out:
                signals.update(ss_out)
    except Exception as _e:
        _log_silent_producer_failure("sector_strength", _e)
    # Batch 252: chart pattern signals (DEC-355-362). Graceful no-op when
    # history insufficient (most patterns need 60-150 bars).
    try:
        from backtest.signals.chart_patterns import compute_all_chart_patterns
        chart_out = compute_all_chart_patterns(df)
        if chart_out:
            signals.update(chart_out)
    except Exception as _e:
        _log_silent_producer_failure("chart_patterns", _e)
    # Batch 252: index rebalance signals (DEC-370). Graceful no-op when
    # data_prefetch/derived/index_rebalance_events.parquet missing.
    try:
        from backtest.signals.index_rebalance import compute_index_rebalance_signals
        ir_out = compute_index_rebalance_signals(ticker, as_of)
        if ir_out:
            signals.update(ir_out)
    except Exception as _e:
        _log_silent_producer_failure("index_rebalance", _e)
    # Batch 253: pairs trading signals (DEC-369). Reads T5b precompute
    # parquet. Graceful no-op when precompute missing (fires 0 trades).
    try:
        from backtest.signals.pairs_trading import compute_pair_signals_for_ticker
        ticker_close = pd.Series(df["close"].values[-90:], index=df.index[-90:])
        pair_out = compute_pair_signals_for_ticker(ticker, as_of, ticker_close)
        if pair_out:
            signals.update(pair_out)
    except Exception as _e:
        _log_silent_producer_failure("pairs_trading", _e)
    # Batch 253: news sentiment signals (DEC-411). 7-day window from
    # Polygon news cache (1.05M articles).
    try:
        from backtest.signals.news_sentiment import compute_news_sentiment_signals
        news_out = compute_news_sentiment_signals(ticker, as_of, lookback_days=7)
        if news_out:
            signals.update(news_out)
    except Exception as _e:
        _log_silent_producer_failure("news_sentiment", _e)
    # Batch 471 (P13): Google Trends search-volume signals.
    try:
        from backtest.signals.search_volume import compute_search_volume_signals
        sv_out = compute_search_volume_signals(ticker, as_of)
        if sv_out:
            signals.update(sv_out)
    except Exception as _e:
        _log_silent_producer_failure("search_volume", _e)
    # Batch 472 (P11): CFTC COT macro positioning (universe-wide).
    try:
        from backtest.signals.cot_positioning import get_all_cot_signals
        cot_out = get_all_cot_signals(as_of)
        if cot_out:
            signals.update(cot_out)
    except Exception as _e:
        _log_silent_producer_failure("cot_positioning", _e)
    # Batch 473 (P16-housetrading): Quiver House-member trading signals.
    try:
        from backtest.signals.congressional_alt_data import compute_housetrading_signals
        ht_out = compute_housetrading_signals(ticker, as_of)
        if ht_out:
            signals.update(ht_out)
    except Exception as _e:
        _log_silent_producer_failure("housetrading", _e)
    # Batch 473 (P16-gov_contracts): Quiver federal contract awards.
    try:
        from backtest.signals.congressional_alt_data import compute_gov_contracts_signals
        gc_out = compute_gov_contracts_signals(ticker, as_of)
        if gc_out:
            signals.update(gc_out)
    except Exception as _e:
        _log_silent_producer_failure("gov_contracts", _e)
    # Batch 480 (P16-lobbying): Quiver federal lobbying spend (Hill-Kelly-
    # Lockhart 2014 alpha factor).
    try:
        from backtest.signals.congressional_alt_data import compute_lobbying_signals
        lb_out = compute_lobbying_signals(ticker, as_of)
        if lb_out:
            signals.update(lb_out)
    except Exception as _e:
        _log_silent_producer_failure("lobbying", _e)
    # Batch 528 (P16-completion 2026-05-31): 3 remaining Quiver alt-data
    # sub-feeds wired with silent-failure logger pattern. Closes P16
    # PARTIAL -> RESOLVED.
    try:
        from backtest.signals.congressional_alt_data import compute_patentmomentum_signals
        pm_out = compute_patentmomentum_signals(ticker, as_of)
        if pm_out:
            signals.update(pm_out)
    except Exception as _e:
        _log_silent_producer_failure("patentmomentum", _e)
    try:
        from backtest.signals.congressional_alt_data import compute_offexchange_signals
        oe_out = compute_offexchange_signals(ticker, as_of)
        if oe_out:
            signals.update(oe_out)
    except Exception as _e:
        _log_silent_producer_failure("offexchange", _e)
    try:
        from backtest.signals.congressional_alt_data import compute_corporatedonors_signals
        cd_out = compute_corporatedonors_signals(ticker, as_of)
        if cd_out:
            signals.update(cd_out)
    except Exception as _e:
        _log_silent_producer_failure("corporatedonors", _e)
    # Batch 531 (2026-05-31, P17 wire-in activation per owner directive
    # "wire in activate truly pending items"). Producer bundle returns
    # `sc_13d_filed_within_30d`, `sc_13d_latest_filer_identity`,
    # `sc_13d_latest_percent_owned`, `8k_item_1_01_filed_within_30d`,
    # `8k_item_5_02_filed_within_7d`, `sc_13g_filed_within_30d`,
    # `sc_13g_latest_filer_identity`, `sc_13g_latest_percent_owned`.
    # Consumed by strat_activist_13d_long (P17b) +
    # strat_m_and_a_target_long (P17c) + tier_modifier_officer_change_5_02
    # (P17d) + smart_money_score_modifier_13g (P17e).
    # Silent-failure: missing decoded parquet -> empty dict -> sleeves
    # don't fire that bar; modifiers no-op. Safe-additive.
    try:
        from backtest.signals.sec_edgar_extractor import compute_sec_edgar_signals
        se_out = compute_sec_edgar_signals(ticker, as_of)
        if se_out:
            signals.update(se_out)
    except Exception as _e:
        _log_silent_producer_failure("sec_edgar", _e)
    # Batch 254: calendar effects (DEC-368). Universe-wide; lru_cache once
    # per as_of date.
    try:
        cal_out = _cached_calendar_signals(str(as_of))
        if cal_out:
            signals.update(cal_out)
    except Exception as _e:
        _log_silent_producer_failure("calendar_effects", _e)
    # Batch 254: cross-asset signals (DEC-369). Universe-wide; lru_cache.
    try:
        xa_out = _cached_cross_asset_signals(str(as_of))
        if xa_out:
            signals.update(xa_out)
    except Exception as _e:
        _log_silent_producer_failure("cross_asset", _e)
    # Batch 255: volume profile signals (60-day VPVR + naked POCs).
    try:
        from backtest.signals.volume_profile import compute_volume_profile, compute_period_pocs
        vp_out = compute_volume_profile(df, lookback_days=60)
        if vp_out:
            signals.update(vp_out)
        period_pocs = compute_period_pocs(df, period_lookback=252, n_periods=6)
        if period_pocs:
            close = float(df["close"].iloc[-1])
            signals["naked_poc_count"] = len(period_pocs)
            if close > 0:
                signals["naked_poc_nearest_distance_pct"] = min(
                    abs(close - p) / close for p in period_pocs
                )
    except Exception as _e:
        _log_silent_producer_failure("volume_profile", _e)
    # Batch 220: merge cross-sectional factor ranks from the universe-
    # wide pre-pass. No-op when xs_features is None.
    if xs_features:
        signals.update(xs_features)
    # Batch 217: PO3 daily candle + multi-TF (weekly/monthly bias) +
    # HTF alignment. Each helper returns empty dict on insufficient
    # data; merged in order so strategy gates can read po3_*,
    # weekly_*, monthly_*, htf_aligned_* keys.
    try:
        from backtest.signals.multi_timeframe import (
            compute_po3_signal,
            compute_weekly_bias,
            compute_monthly_bias,
            compute_htf_alignment,
        )
        po3 = compute_po3_signal(df)
        if po3:
            signals.update(po3)
        weekly = compute_weekly_bias(df)
        if weekly:
            signals.update(weekly)
        monthly = compute_monthly_bias(df)
        if monthly:
            signals.update(monthly)
        if weekly or monthly:
            signals.update(compute_htf_alignment(weekly, monthly))
    except Exception as _e:
        _log_silent_producer_failure("multi_timeframe", _e)

    triggered_long  = []
    triggered_short = []
    # BUG-77 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 19 2026-05-10
    # (owner-approved Option A): third bucket for avoid direction. Previously
    # the else branch merged avoid into triggered_short, inflating
    # strategy_count and distorting candidate ranking - a ticker with
    # mixed/conflicting signals could rank above one with strong directional
    # conviction. Source-side counterpart to BUG-04 (consumer-side filter
    # at backtest.py:410). avoid signals are kept in the candidate dict for
    # downstream diagnostics but excluded from all_triggered / strategy_count.
    triggered_avoid = []

    # Batch 218 (research-review deprecations 2026-05-18 owner-approved):
    # skip strategies in DEPRECATED_STRATEGIES (no replicable peer-reviewed
    # edge in 2015-2024 literature). Shrinks the multi-testing denominator
    # for Bonferroni/DSR gates without deleting strategy function bodies.
    from backtest.config import DEPRECATED_STRATEGIES as _DEPRECATED
    # Batch 372 (2026-05-26 owner-directed): also skip strategies whose
    # upstream data producer does not yet exist. Semantically distinct
    # from DEPRECATED_STRATEGIES (literature-null); these are blocked on
    # Sprint-1 data deliverables. See config.py docstring on
    # STRATEGIES_DISABLED_MISSING_PRODUCER for re-enablement criteria.
    from backtest.config import STRATEGIES_DISABLED_MISSING_PRODUCER as _MISSING_PRODUCER
    # Batch 310 (2026-05-24): Phase 1B-alpha disable mechanism REVERTED per
    # owner directive "DO NOT DISABLE ANYTHING TILL I ANALYZE AND COMMAND".
    # The PHASE_1B_ALPHA_DISABLED_STRATEGIES constant in config.py is now
    # reference-only (not used as a screener gate). Phase 1A-beta losers
    # are to be analyzed per-regime / per-ticker / per-classifier before any
    # universal disable. Roster decisions move to STRATEGY_REGIME_AFFINITY
    # (regime-stratified) instead of a global skip list.
    # Batch 263 (Class A confirmation entry, owner-approved 2026-05-20):
    # Mean-reversion strategies INTENTIONALLY enter against the day's candle
    # (oversold dip-buy = enter when price down). All other strategies should
    # require directional confirmation on signal day. Per Edwards-Magee 1948
    # + Bulkowski 2005: signals fired on weak candles tend to fail.
    # Post-1A-alpha forensic showed 479 trades (41pct) never developed past
    # entry - this gate filters those that fire on indecisive/contrary days.
    MEAN_REVERSION_CATEGORIES = {
        "mean_reversion", "oversold_bounce", "counter_trend",
    }
    MEAN_REVERSION_STRATEGIES = {
        # Explicit list of strategies that intentionally counter day direction
        "bollinger_lower", "rsi_oversold", "mfi_oversold", "stoch_oversold",
        "stochrsi_oversold", "williams_r_oversold", "ultimate_oscillator",
        "stochrsi_overbought_short",  # short counterpart
        "pivot_s1_bounce", "pivot_s2_bounce", "pivot_s3_capitulation",
        "prev_day_low_bounce", "camarilla_s3_bounce",
        "pairs_mean_reversion_long", "pairs_mean_reversion_short",
        "post_inclusion_reversal_short",  # fade-the-pop is counter-day
    }
    close_above_open = signals.get("close_above_open", True)  # default-permissive
    close_below_open = signals.get("close_below_open", False)
    for name, fn in ALL_STRATEGIES.items():
        if name in _DEPRECATED:
            continue
        if name in _MISSING_PRODUCER:
            # Batch 372: gated by Sprint-1 data deliverable, not literature.
            # Re-enable in same line by removing from
            # STRATEGIES_DISABLED_MISSING_PRODUCER once producer lands.
            continue
        # Batch 310 (2026-05-24): PHASE_1B_ALPHA_DISABLED_STRATEGIES skip
        # REVERTED per owner directive. All previously-disabled strategies
        # are re-active. Roster pruning will move to STRATEGY_REGIME_AFFINITY
        # after owner per-regime / per-ticker / per-classifier analysis.
        try:
            result = fn(signals)
            if not result["fires"]:
                continue
            direction = result["direction"]
            category = result.get("category", "")
            # Batch 263 Class A: directional confirmation gate
            is_mean_reversion = (
                name in MEAN_REVERSION_STRATEGIES
                or category in MEAN_REVERSION_CATEGORIES
            )
            if not is_mean_reversion:
                if direction == "long" and not close_above_open:
                    continue  # long signal on a red candle -> skip
                if direction == "short" and not close_below_open:
                    continue  # short signal on a green candle -> skip
            # Regime context  -  no hard direction blocks (buy-the-dip philosophy)
            # Crisis regime: long trades flagged, position size reduced in engine
            # Bull regime: short trades allowed but at reduced size
            entry = {
                "strategy":        name,
                "direction":       direction,
                "category":        category,
                "signals_used":    result["signals_used"],
                "context_bullets": result["context_bullets"],
            }
            if direction == "long":
                triggered_long.append(entry)
            elif direction == "short":
                triggered_short.append(entry)
            else:  # avoid - BUG-77: do NOT inflate triggered_short
                triggered_avoid.append(entry)
        except Exception as exc:
            logger.debug("Strategy %s error for %s: %s", name, ticker, exc)

    all_triggered = triggered_long + triggered_short  # BUG-77: no avoid here
    tech_count    = count_bullish_signals(signals)
    atr           = signals.get("atr", 0.0)
    close         = float(df["close"].iloc[-1])

    return {
        "ticker":            ticker,
        "as_of":             as_of,
        "liquidity_ok":      True,
        "fail_reason":       None,
        "strategies":        all_triggered,
        "long_strategies":   triggered_long,
        "short_strategies":  triggered_short,
        "avoid_strategies":  triggered_avoid,  # BUG-77: kept for diagnostics
        "strategy_count":    len(all_triggered),
        "long_count":        len(triggered_long),
        "short_count":       len(triggered_short),
        "avoid_count":       len(triggered_avoid),
        "tech_signal_count": tech_count,
        "signals":           signals,
        "last_close":        round(close, 4),
        "atr":               atr,
        "initial_stop_long":  round(close * 0.90, 4),
        "initial_stop_short": round(close * 1.10, 4),
    }


# ---------------------------------------------------------------------------
# Batch 321 (2026-05-25): process-pool infrastructure for per-ticker
# screen_instrument parallelization. See BATCH_318_PROCESS_POOL_DESIGN.md.
#
# Workers hold their own copy of ohlcv_dict + info_dict in module-level
# globals (set by _pool_init). This keeps the per-day work-tuple SMALL
# (just (ticker, as_of, regime, vix_value, vix_history, xs_features)) so
# IPC cost amortizes well over 1937 tkrs x 1044 days.
#
# Engine wiring (BacktestEngine.__init__ + _process_day pool init/dispatch)
# lands in Batch 322 after this infrastructure validates in isolation.
# Until 322 ships, the pool path is unused by the engine; sequential path
# remains the only call site.
# ---------------------------------------------------------------------------
_WORKER_OHLCV: dict | None = None
_WORKER_INFO: dict | None = None


def _pool_init(ohlcv_dict: dict, info_dict: dict) -> None:
    """Process-pool initializer. Each worker stores ohlcv_dict + info_dict
    in module-level globals so per-call work-tuples stay small."""
    global _WORKER_OHLCV, _WORKER_INFO
    _WORKER_OHLCV = ohlcv_dict
    _WORKER_INFO = info_dict
    # Pre-warm module-level data caches inside the worker so the first
    # screen_instrument call doesn't pay the parquet-read latency.
    try:
        from backtest.signals.insider_buying import _load_insiders_global
        _load_insiders_global()
    except Exception:
        pass
    try:
        from backtest.signals.index_rebalance import _load_events
        _load_events()
    except Exception:
        pass


def _worker_screen_ticker(args):
    """Pool worker entry. Reads ohlcv from worker-global; slices to as_of
    locally; returns the screen_instrument result (or None on bad inputs)."""
    ticker, as_of, regime, vix_value, vix_history, xs_features = args
    if _WORKER_OHLCV is None or _WORKER_INFO is None:
        return None
    df = _WORKER_OHLCV.get(ticker)
    if df is None:
        return None
    # Slice to as_of in worker (same logic as BacktestEngine._process_day
    # uses to build ohlcv_pit). Avoids sending pre-sliced df over IPC.
    try:
        if hasattr(df.index, "date"):
            df_pit = df[df.index.date <= as_of]
        else:
            df_pit = df[df.index <= as_of]
    except Exception:
        return None
    if df_pit is None or df_pit.empty:
        return None
    info = _WORKER_INFO.get(ticker, {"ticker": ticker})
    try:
        return screen_instrument(
            ticker, df_pit, info, as_of, regime,
            vix_value=vix_value, vix_history=vix_history,
            xs_features=xs_features,
        )
    except Exception:
        return None


def screen_universe(
    ohlcv_dict: dict,
    info_dict: dict,
    as_of: date,
    regime: str = "neutral",
    min_strategies: int = 1,
    vix_value: float = None,
    vix_history: list = None,
    pool=None,
) -> list:
    """Screen all instruments. Returns candidates sorted by strategy count.

    Batch 204: optional VIX context kwargs flow through to each
    screen_instrument call so regime-aware strategies see the
    vix_percentile / vix_band overlays. Backward-compatible: when None,
    behavior is unchanged.

    Batch 220 (cross-sectional infrastructure 2026-05-18 owner-approved):
    pre-compute universe-wide factor ranks ONCE before per-ticker
    iteration; inject per-ticker rank into each ticker's signals via
    screen_instrument kwarg. Factor strategies (xs_momentum_*,
    xs_low_beta_*, IVOL/MAX filters) read these injected ranks. Defaults
    to no-op when ohlcv_dict has insufficient history or compute fails.

    Batch 321 (2026-05-25): optional `pool` kwarg (any executor with
    `map(fn, iterable)` semantics). When provided, per-ticker
    screen_instrument calls dispatch to pool workers. Workers must be
    pre-initialized via _pool_init(ohlcv_dict, info_dict). The xs_features
    pre-pass STAYS in main process (cheap, runs once per day). Result
    sort happens in main process so candidate ordering is deterministic
    regardless of worker return order.
    """
    # Batch 220 cross-sectional pre-pass (always main-process)
    xs_features = {}
    try:
        from backtest.signals.cross_sectional import compute_cross_sectional_features
        xs_features = compute_cross_sectional_features(ohlcv_dict, as_of)
    except Exception as _e:
        _log_silent_producer_failure("cross_sectional_features", _e)
        xs_features = {}

    # Batch 538 OPT-B Phase 7: panel-style technical signals pre-pass.
    # When USE_PANEL_TECHNICAL_SIGNALS=True, pre-build close_panel from
    # all per-ticker OHLCV in ohlcv_dict + compute RSI/EMA/SMA/returns
    # for ALL tickers in one vectorized pandas op. Per-ticker
    # compute_all_signals downstream then SKIPS those indicators
    # (no double-compute). 10x speedup on the covered indicators.
    panel_signals_per_ticker: dict = {}
    try:
        from backtest.config import USE_PANEL_TECHNICAL_SIGNALS
    except Exception:
        USE_PANEL_TECHNICAL_SIGNALS = False
    if USE_PANEL_TECHNICAL_SIGNALS and ohlcv_dict:
        try:
            from backtest.signals.technical_panel import (
                compute_panel_signals_for_as_of,
            )
            # Build close_panel: rows=dates, cols=tickers. Each
            # ohlcv_dict[ticker] is a DataFrame with 'close' column.
            close_series = {
                t: df["close"]
                for t, df in ohlcv_dict.items()
                if df is not None and "close" in df.columns and not df.empty
            }
            if close_series:
                close_panel = pd.DataFrame(close_series)
                panel_signals_per_ticker = compute_panel_signals_for_as_of(
                    close_panel
                )
        except Exception as _e:
            _log_silent_producer_failure("panel_technical_signals", _e)
            panel_signals_per_ticker = {}

    candidates = []
    if pool is not None:
        # Batch 321 parallel path
        work_items = [
            (ticker, as_of, regime, vix_value, vix_history, xs_features.get(ticker))
            for ticker in ohlcv_dict
        ]
        for result in pool.map(_worker_screen_ticker, work_items):
            if (result is not None
                and result.get("liquidity_ok")
                and result.get("strategy_count", 0) >= min_strategies):
                candidates.append(result)
    else:
        # Sequential path (pre-Batch-321 behavior; current call site)
        for ticker, df in ohlcv_dict.items():
            info   = info_dict.get(ticker, {"ticker": ticker})
            result = screen_instrument(
                ticker, df, info, as_of, regime,
                vix_value=vix_value, vix_history=vix_history,
                xs_features=xs_features.get(ticker),
                panel_signals=panel_signals_per_ticker.get(ticker),
            )
            if result.get("liquidity_ok") and result.get("strategy_count", 0) >= min_strategies:
                candidates.append(result)
    # DEC-458: merge lead-lag cross-ticker candidates (sector rotation)
    lead_lag = screen_lead_lag_sector(ohlcv_dict, info_dict, as_of)
    existing_map = {c["ticker"]: c for c in candidates}
    for ll in lead_lag:
        t = ll["ticker"]
        if t in existing_map:
            existing_map[t]["strategies"].extend(ll["strategies"])
            existing_map[t]["long_strategies"].extend(ll["long_strategies"])
            existing_map[t]["strategy_count"] += 1
            existing_map[t]["long_count"] += 1
        else:
            candidates.append(ll)

    candidates.sort(key=lambda x: (x["strategy_count"], x["tech_signal_count"]), reverse=True)
    logger.info("screen_universe [%s] regime=%s: %d/%d passed (incl. %d lead-lag)",
                as_of, regime, len(candidates), len(ohlcv_dict), len(lead_lag))
    return candidates
