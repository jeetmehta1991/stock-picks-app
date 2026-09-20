#!/usr/bin/env python
"""B2841 (owner-directed 2026-09-16: "I want all the Producer bands defined
for table a post r1 in all of the 12 strategies") - the R1 band definitions,
CURATED from producer source reads, merged into the generated Table A files by
build_table_a.py so regeneration never loses them.

Every row: production value READ at its evidence line, a band with its stated
BASIS (#165 - BRACKET production / CANON literature / MEASURED), the honest
OFFLINE-vs-RESIM split (offline iff the variant re-evaluates from magnitudes
PERSISTED in signals_at_entry; anything needing unpersisted bars is engine),
and the env-actuator status - a knob with no env actuator can have NO resim
level run (validate_spec refuses it, the S6-B2569a class), so those rows are
DEFINED-NO-ACTUATOR: the band exists, the plumbing is follow-up work.

ALL BANDS AWAIT THE T3 OWNER BAND REVIEW before any grid runs - defining is
not running (standing rule 2026-08-10; the owner's directive here is the word
to DEFINE, per-strategy grid words still gate execution).

Keyed by the P-row subject (producer boolean, helper, or depth key);
STRATEGY_EXTRAS adds strategy-layer gates the source pattern cannot see
(comparisons routed through local variables)."""

# knob dict fields: param, production, band, basis, offline, resim, env,
#                   evidence  (env=None -> DEFINED-NO-ACTUATOR for resim legs)

_EMA200 = {"param": "ema span (the 200 in above/below_ema_200)",
           "production": 200, "band": [150, 200, 250],
           "basis": "BRACKET production; 150/250 are the adjacent canon spans",
           "offline": "none - other spans' values are unpersisted",
           "resim": "the whole band", "env": None,
           "evidence": "backtest/signals/technical.py compute_ema_sma"}

PRODUCER_BANDS = {
    # ---- candle patterns (shared shape, strict zeros) ---------------------
    "three_black_crows": [
        {"param": "n_bars (pattern length)", "production": 3, "band": [3, 4],
         "basis": "CANON (Nison 1991: three); 4 as the strict extension",
         "offline": "none - pattern bars' OHLC unpersisted",
         "resim": "the whole band", "env": "CANDLE_N_BARS",
         "evidence": "backtest/signals/technical.py:2108-2111"},
        {"param": "min_body_pct_of_range per candle", "production": 0.0,
         "band": [0.0, 0.3, 0.5],
         "basis": "CANON (Nison long-body crows); production accepts ANY body",
         "offline": "none", "resim": "the whole band", "env": "CANDLE_MIN_BODY_PCT",
         "evidence": "technical.py:2109 (c<o only - no magnitude)"},
        {"param": "min_step_down_pct (close[i] below close[i-1] by)",
         "production": 0.0, "band": [0.0, 0.1, 0.25],
         "basis": "BRACKET zero upward; strict < today",
         "offline": "none", "resim": "the whole band", "env": "CANDLE_MIN_STEP_PCT",
         "evidence": "technical.py:2110"},
        {"param": "max_lower_wick_pct (close near low)", "production": None,
         "band": [None, 0.3, 0.2],
         "basis": "CANON (crows close at/near lows); production unenforced",
         "offline": "none", "resim": "the whole band", "env": "CANDLE_MAX_WICK_PCT",
         "evidence": "technical.py:2108-2111 (absent today)"},
    ],
    # mirror: same producer block, bullish inequalities. B2842 (owner
    # screenshot): a one-line "as the sibling, mirrored" stub is an axis
    # REFERENCED, not inventoried - each file stands alone at its own T3
    # review, so the four knobs are explicit here too.
    "three_white_soldiers": [
        {"param": "n_bars (pattern length)", "production": 3, "band": [3, 4],
         "basis": "CANON (Nison 1991: three); 4 as the strict extension",
         "offline": "none - pattern bars' OHLC unpersisted",
         "resim": "the whole band", "env": "CANDLE_N_BARS",
         "evidence": "backtest/signals/technical.py:2104-2107"},
        {"param": "min_body_pct_of_range per candle", "production": 0.0,
         "band": [0.0, 0.3, 0.5],
         "basis": "CANON (Nison long-body soldiers); production accepts ANY body",
         "offline": "none", "resim": "the whole band", "env": "CANDLE_MIN_BODY_PCT",
         "evidence": "technical.py:2105 (c>o only - no magnitude)"},
        {"param": "min_step_up_pct (close[i] above close[i-1] by)",
         "production": 0.0, "band": [0.0, 0.1, 0.25],
         "basis": "BRACKET zero upward; strict > today",
         "offline": "none", "resim": "the whole band", "env": "CANDLE_MIN_STEP_PCT",
         "evidence": "technical.py:2106"},
        {"param": "max_upper_wick_pct (close near high)", "production": None,
         "band": [None, 0.3, 0.2],
         "basis": "CANON (soldiers close at/near highs); production unenforced",
         "offline": "none", "resim": "the whole band", "env": "CANDLE_MAX_WICK_PCT",
         "evidence": "technical.py:2104-2107 (absent today)"},
    ],
    # ---- stochrsi family --------------------------------------------------
    "stochrsi_oversold": [
        {"param": "period (rsi+stoch length)", "production": 14,
         "band": [10, 14, 21],
         "basis": "BRACKET production with the adjacent canon spans",
         "offline": "none - k/d at other periods unpersisted",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:574-600"},
        {"param": "oversold threshold on k", "production": 20,
         "band": [10, 15, 20, 25],
         "basis": "BRACKET canon 20; stochrsi_k IS persisted",
         "offline": "TIGHTER (k < 15, k < 10) - subset on persisted stochrsi_k",
         "resim": "LOOSER (k < 25)", "env": None,
         "evidence": "technical.py:597"},
    ],
    "stochrsi_overbought": [
        {"param": "overbought threshold on k", "production": 80,
         "band": [75, 80, 85, 90],
         "basis": "BRACKET canon 80; stochrsi_k IS persisted",
         "offline": "TIGHTER (k > 85, k > 90) - subset on persisted stochrsi_k",
         "resim": "LOOSER (k > 75)", "env": None,
         "evidence": "backtest/signals/technical.py:598"},
        {"param": "period (rsi+stoch length)", "production": 14,
         "band": [10, 14, 21], "basis": "BRACKET production",
         "offline": "none", "resim": "the whole band", "env": None,
         "evidence": "technical.py:574"},
    ],
    "stochrsi_cross_up": [
        {"param": "cross guard band (k < 80 on cross_up)", "production": 80,
         "band": [70, 80], "basis": "BRACKET production guard",
         "offline": "TIGHTER (k < 70) on persisted k/d",
         "resim": "freshness itself (k vs d needs both persisted - both ARE)",
         "env": None, "evidence": "backtest/signals/technical.py:599"},
    ],
    "stochrsi_cross_dn": [
        {"param": "cross guard band (k > 20 on cross_dn)", "production": 20,
         "band": [20, 30], "basis": "BRACKET production guard",
         "offline": "TIGHTER (k > 30) on persisted k/d",
         "resim": "none needed - k and d both persisted", "env": None,
         "evidence": "backtest/signals/technical.py:600"},
    ],
    # ---- williams ----------------------------------------------------------
    "williams_r_oversold": [
        {"param": "period", "production": 14, "band": [10, 14, 20],
         "basis": "BRACKET production", "offline": "none",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:692"},
        {"param": "oversold threshold", "production": -80,
         "band": [-90, -85, -80],
         "basis": "BRACKET canon -80; williams_r IS persisted",
         "offline": "TIGHTER (< -85, < -90) - subset on persisted williams_r",
         "resim": "LOOSER (> -80)", "env": None,
         "evidence": "technical.py:702"},
    ],
    # ---- cmf ---------------------------------------------------------------
    "cmf_cross_up": [
        {"param": "cmf window", "production": 20, "band": [14, 20, 30],
         "basis": "BRACKET production", "offline": "none",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:1695"},
        {"param": "cross level (zero line)", "production": 0.0,
         "band": [0.0, 0.02, 0.05],
         "basis": "BRACKET zero upward (require conviction, not a graze)",
         "offline": "LEVEL side (cmf > 0.02/0.05) - persisted cmf; the "
                    "FRESHNESS (prior bar <= level) needs the unpersisted "
                    "prior cmf",
         "resim": "freshness at any non-production level", "env": None,
         "evidence": "technical.py:1706"},
    ],
    "cmf_cross_dn": [
        {"param": "as cmf_cross_up, mirrored", "production": 0.0,
         "band": [0.0, -0.02, -0.05], "basis": "mirror",
         "offline": "level side on persisted cmf", "resim": "freshness",
         "env": None, "evidence": "backtest/signals/technical.py:1707"},
    ],
    "cmf_positive": [
        {"param": "level (cmf > 0)", "production": 0.0,
         "band": [0.0, 0.02, 0.05], "basis": "BRACKET zero",
         "offline": "TIGHTER levels on persisted cmf",
         "resim": "LOOSER (cmf > -0.02)", "env": None,
         "evidence": "backtest/signals/technical.py:1699"},
    ],
    "cmf_negative": [
        {"param": "level (cmf < 0)", "production": 0.0,
         "band": [0.0, -0.02, -0.05], "basis": "mirror of cmf_positive",
         "offline": "TIGHTER levels on persisted cmf", "resim": "LOOSER",
         "env": None, "evidence": "technical.py cmf block"},
    ],
    # ---- hull family -------------------------------------------------------
    "hull_bullish": [
        {"param": "hull period", "production": 20, "band": [14, 20, 30],
         "basis": "BRACKET production (WMA(sqrt n, 2WMA(n/2)-WMA(n)))",
         "offline": "none - hull at other periods unpersisted; the "
                    "rising test needs the unpersisted prior hull",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:1304-1323"},
    ],
    "hull_bearish": [
        {"param": "as hull_bullish (v < prev)", "production": 20,
         "band": [14, 20, 30], "basis": "mirror", "offline": "none",
         "resim": "the whole band", "env": None,
         "evidence": "technical.py:1327"},
    ],
    "price_above_hull": [
        {"param": "buffer pct (close > hull by)", "production": 0.0,
         "band": [0.0, 0.25, 0.5],
         "basis": "BRACKET zero; hull_ma persisted but close is not a "
                  "signal key - distance not reconstructible offline",
         "offline": "none", "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:1330"},
    ],
    "price_below_hull": [
        {"param": "mirror of price_above_hull", "production": 0.0,
         "band": [0.0, 0.25, 0.5], "basis": "mirror", "offline": "none",
         "resim": "the whole band", "env": None,
         "evidence": "technical.py hull block"},
    ],
    "adx_trending": [
        {"param": "trending threshold", "production": 25, "band": [20, 25, 30],
         "basis": "BRACKET canon 25; adx IS persisted",
         "offline": "any level - re-derive from persisted adx",
         "resim": "none needed", "env": None,
         "evidence": "backtest/signals/technical.py:915"},
    ],
    "price_above_ema_200_break_recent_5d": [
        {"param": "recency lookback (bars)", "production": 5,
         "band": [3, 5, 10],
         "basis": "BRACKET production (B722 STATE->EVENT conversion)",
         "offline": "none - the break history is unpersisted",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:814-825"},
        dict(_EMA200),
    ],
    "below_ema_200_break_recent_5d": [
        {"param": "mirror of the above (5d lookback + span)",
         "production": 5, "band": [3, 5, 10], "basis": "mirror",
         "offline": "none", "resim": "the whole band", "env": None,
         "evidence": "technical.py:825"},
    ],
    "price_above_ema_200": [dict(_EMA200)],
    "below_ema_200": [dict(_EMA200)],
    # ---- bollinger reclaim + vix conditioning ------------------------------
    "bb_20_20_reclaim_from_lower_recent_3d": [
        {"param": "bb period / k", "production": "20 / 2.0",
         "band": "period [20]; k [1.5, 2.0, 2.5]",
         "basis": "k BRACKETs canon 2.0; period held (the 20_20 identity)",
         "offline": "none - band values at other k unpersisted for the "
                    "reclaim test", "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py bb block + :1402"},
        {"param": "reclaim recency (bars)", "production": 3, "band": [1, 3, 5],
         "basis": "BRACKET production (B800 EVENT conversion)",
         "offline": "none - reclaim history unpersisted",
         "resim": "the whole band", "env": None, "evidence": "technical.py:1402"},
    ],
    "vix_band_low": [
        {"param": "tercile edges on vix_percentile", "production": "1/3, 2/3",
         "band": "[0.25/0.75] and [1/3, 2/3]",
         "basis": "BRACKET terciles vs quartile edges; vix_percentile IS "
                  "persisted",
         "offline": "any re-banding - re-derive from persisted vix_percentile",
         "resim": "none needed", "env": None,
         "evidence": "backtest/signals/technical.py:2690-2702"},
    ],
    "vix_band_high": [
        {"param": "as vix_band_low (upper edge)", "production": "2/3",
         "band": "[0.75] alternative", "basis": "as vix_band_low",
         "offline": "re-derive from persisted vix_percentile",
         "resim": "none needed", "env": None, "evidence": "technical.py:2700"},
    ],
    # ---- cpr + macd --------------------------------------------------------
    "cpr_narrow_tight": [
        {"param": "width threshold (cpr_width < rng * X)", "production": 0.05,
         "band": [0.03, 0.05, 0.08],
         "basis": "BRACKET production (B654 local 0.05; the family's 0.15 "
                  "stays with its own consumers)",
         "offline": "none - cpr_width IS persisted but the denominator "
                    "(prior-day range) is not",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:103"},
    ],
    "below_cpr": [
        {"param": "buffer pct (price below cpr_bottom by)", "production": 0.0,
         "band": [0.0, 0.25], "basis": "BRACKET zero",
         "offline": "none - entry price is not a signal key",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:146"},
    ],
    "macd_12_26_9_bearish": [
        {"param": "span triple (fast, slow, signal)", "production": "(12,26,9)",
         "band": "[(8,21,5), (12,26,9)] both computed in production; other "
                 "triples are new",
         "basis": "MEASURED availability - both triples are emitted and "
                  "macd_8_21_5_* IS persisted",
         "offline": "the (8,21,5) SWAP - re-evaluate on persisted "
                    "macd_8_21_5 keys",
         "resim": "any third triple", "env": None,
         "evidence": "backtest/signals/technical.py:634-648"},
    ],
    # ---- naked poc ---------------------------------------------------------
    "naked_poc_count": [
        {"param": "period_lookback (bars)", "production": 252,
         "band": [126, 252], "basis": "BRACKET production (1y; half-year alt)",
         "offline": "none - POC set at other windows unpersisted",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/volume_profile.py:152-168"},
        {"param": "n_periods (POC chunks)", "production": 6, "band": [4, 6, 8],
         "basis": "BRACKET production", "offline": "none",
         "resim": "the whole band", "env": None,
         "evidence": "volume_profile.py:155"},
        {"param": "n_bins (price bins)", "production": 40, "band": [30, 40, 50],
         "basis": "BRACKET production", "offline": "none",
         "resim": "the whole band", "env": None,
         "evidence": "volume_profile.py:156"},
        {"param": "count floor (> N naked POCs)", "production": 0,
         "band": [0, 1, 2],
         "basis": "BRACKET production; naked_poc_count IS persisted",
         "offline": "TIGHTER floors (> 1, > 2) - subset on the persisted count",
         "resim": "none on this knob", "env": None,
         "evidence": "backtest/signals/screener.py:7004"},
    ],
    # ---- pairs -------------------------------------------------------------
    "pair_count_active": [
        {"param": "EG cointegration significance", "production": 0.05,
         "band": [0.01, 0.05],
         "basis": "BRACKET production toward strict (precompute-side)",
         "offline": "none - pair set is a PRECOMPUTE",
         "resim": "the whole band (re-run pairs precompute + engine)",
         "env": None,
         "evidence": "backtest/signals/pairs_trading.py:46"},
        {"param": "zscore rolling window (bars)", "production": 60,
         "band": [40, 60, 90], "basis": "BRACKET production",
         "offline": "none - z at other windows unpersisted",
         "resim": "the whole band", "env": None,
         "evidence": "pairs_trading.py:147-170"},
        {"param": "half-life admission bounds (days)", "production": "5-30",
         "band": "[5-30] and [3-45]",
         "basis": "BRACKET production (post-HFT-survival window)",
         "offline": "TIGHTER inner cuts via the persisted pair_half_life "
                    "(the strategy-layer hl gate already bands it offline)",
         "resim": "WIDER bounds (admit pairs the precompute excluded)",
         "env": None, "evidence": "pairs_trading.py:191, :216"},
    ],
}

# ---------------------------------------------------------------------------
# B2845 (owner-corrected scope 2026-09-17: "i want r1 to be executed for each
# of the tighten n both strategies ... a ready and final table a for review
# for each strategy"): band definitions for EVERY distinct producer leg the
# 41 TIGHTEN+BOTH strategies touch - 61 further legs beyond the B2841 set,
# enumerated mechanically (gate_legs census) so none is silent. Compact
# factories keep one definition per shape; every entry still carries its
# production value, band, basis, offline/resim split and evidence line.
# ---------------------------------------------------------------------------

def _K(param, production, band, basis, offline, resim, evidence, env=None):
    return {"param": param, "production": production, "band": band,
            "basis": basis, "offline": offline, "resim": resim,
            "env": env, "evidence": evidence}


def _candle(name, line, extra=""):
    """A single-candle/multi-candle pattern with NO explicit magnitude today:
    the implicit anatomy knobs (min body / wick / step pct) are the band."""
    return [_K(f"implicit anatomy knobs (min body/wick/step pct){extra}",
               "0 / absent (any magnitude counts)", "[0, 0.3, 0.5] per knob",
               "CANON candle anatomy (Nison); production accepts any magnitude",
               "none - pattern bars' OHLC unpersisted", "the whole band",
               f"backtest/signals/technical.py:{line} (compute_candle_signals)")]


def _near(level_key):
    return [_K(f"proximity tolerance to {level_key} (abs dist/level)", 0.003,
               "[0.002, 0.003, 0.005, 0.015 (the _wide variant)]",
               "BRACKET production 0.003; 0.015 is the shipped near_*_wide",
               "none - the level is persisted but today's price is not a signal key",
               "the whole band",
               "backtest/signals/technical.py:76 (near), :81 (near_wide)")]


def _span(what, production, band, evidence):
    return [_K(f"{what} span", production, band,
               "BRACKET production with adjacent canon spans",
               "none - values at other spans unpersisted", "the whole band",
               evidence)]


def _price_vs_level(what, evidence, note=""):
    return [_K(f"buffer pct (price vs {what}){note}", 0.0, "[0, 0.25, 0.5]",
               "BRACKET zero; strict inequality today",
               "none - today's price is not a signal key", "the whole band",
               evidence)]


PRODUCER_BANDS.update({
    # ---- candle patterns (structural today; anatomy knobs are the band) ---
    "hammer": _candle("hammer", "candle block"),
    "shooting_star": _candle("shooting_star", "candle block"),
    "hanging_man": _candle("hanging_man", "candle block"),
    "dark_cloud_cover": _candle("dark_cloud_cover", "candle block"),
    "bearish_pin_bar": _candle("bearish_pin_bar", "candle block (B641 W3)"),
    "bullish_engulfing": _candle("bullish_engulfing", "candle block"),
    "bearish_engulfing": _candle("bearish_engulfing", "candle block"),
    "inside_bar": [_K("(structural) h[-1]<h[-2] and l[-1]>l[-2] - no parameter",
                      "-", "optional containment-margin pct [0, 0.1, 0.25]",
                      "BRACKET zero; strict containment today",
                      "none - bar OHLC unpersisted", "the whole band",
                      "backtest/signals/technical.py:2027")],
    "morning_star": [
        _K("mid-candle small-body ratio (body < X * range)", 0.3,
           "[0.2, 0.3, 0.4]", "BRACKET production (the one EXPLICIT candle knob)",
           "none - the mid bar's body/range unpersisted", "the whole band",
           "backtest/signals/technical.py:2088"),
        _K("recovery rule (close above midpoint of bar-3)", "structural",
           "midpoint vs [0.382, 0.5, 0.618] retrace", "BRACKET the midpoint rule",
           "none", "the whole band", "technical.py:2093")],
    "evening_star": [_K("mirror of morning_star's two knobs", "0.3 / midpoint",
                        "as morning_star, mirrored", "mirror",
                        "none", "the whole band",
                        "backtest/signals/technical.py:2095-2100")],
    # ---- oscillators ------------------------------------------------------
    "uo_oversold": [
        _K("oversold threshold", 30, "[20, 25, 30]",
           "BRACKET canon 30; the uo value itself is persisted where emitted",
           "TIGHTER (< 25, < 20) where `uo` is persisted on the fires",
           "LOOSER; and the (7,14,28) period triple", None,
           "backtest/signals/technical.py:751"),
        _K("period triple", "(7, 14, 28)", "[(7,14,28), (5,10,20), (14,28,56)]",
           "BRACKET canon triple", "none - other triples unpersisted",
           "the whole band", "backtest/signals/technical.py:738-750")],
    "uo_overbought": [_K("overbought threshold", 70, "[70, 75, 80]",
                         "BRACKET canon 70 (mirror of oversold)",
                         "TIGHTER (> 75, > 80) where `uo` is persisted",
                         "LOOSER", "backtest/signals/technical.py:752")],
    "stoch_bullish_cross": [
        _K("stochastic (k, smooth, d)", "(14, 3, 3)", "[(14,3,3), (5,3,3), (21,5,5)]",
           "BRACKET canon", "none - other spans unpersisted", "the whole band",
           "backtest/signals/technical.py:604-624"),
        _K("cross freshness (k over d today)", "structural",
           "add guard band: k below [20, 30] at cross",
           "BRACKET the oversold zone",
           "guard-band side on persisted stoch_k/stoch_d",
           "the freshness itself (prior k/d unpersisted)",
           "technical.py:629")],
    "stoch_bearish_cross": [_K("mirror of stoch_bullish_cross", "(14,3,3)",
                               "as bullish, mirrored (guard k above [70, 80])",
                               "mirror", "guard-band side on persisted k/d",
                               "freshness", "backtest/signals/technical.py:604-630")],
    "rsi_14": _span("rsi", 14, "[9, 14, 21]",
                    "backtest/signals/technical.py rsi block"),
    "rsi_2": _span("rsi (fast escape-hatch)", 2, "[2, 3, 5]",
                   "backtest/signals/technical.py rsi block"),
    "obv_bullish": [
        _K("obv vs its moving average", "obv > obv_ma", "MA span [10, 20, 50]",
           "BRACKET the shipped span", "none - obv_ma at other spans unpersisted",
           "the whole band", "backtest/signals/technical.py:1570"),
        _K("margin pct over the MA", 0.0, "[0, 1, 2] pct",
           "BRACKET zero", "TIGHTER margins where obv and obv_ma are persisted",
           "LOOSER", "technical.py:1570")],
    "obv_bearish": [_K("mirror of obv_bullish", "obv < obv_ma",
                       "as obv_bullish, mirrored", "mirror",
                       "tighter margins on persisted obv/obv_ma", "looser",
                       "backtest/signals/technical.py obv block")],
    # ---- pivots / levels proximity ---------------------------------------
    "near_s1": _near("S1"), "near_s2": _near("S2"), "near_s3": _near("S3"),
    "near_r1": _near("R1"), "near_r2": _near("R2"),
    "near_cam_s3": _near("Camarilla S3"), "near_cam_r3": _near("Camarilla R3"),
    "near_wood_s1": _near("Woodie S1"), "near_wood_r1": _near("Woodie R1"),
    "above_cpr": _price_vs_level("cpr_top",
                                 "backtest/signals/technical.py:146 region"),
    "above_vwap": _price_vs_level("vwap", "backtest/signals/technical.py vwap block"),
    "below_avwap_20high": _price_vs_level(
        "avwap anchored at 20d high",
        "backtest/signals/technical.py avwap block",
        " + anchor choice [20high, 50high, 252high]"),
    "price_above_sma_50": _span("sma", 50, "[20, 50, 100]",
                                "backtest/signals/technical.py sma block"),
    "price_above_sma_200": _span("sma", 200, "[150, 200, 250]",
                                 "backtest/signals/technical.py sma block"),
    "below_sma_50": _span("sma", 50, "[20, 50, 100]",
                          "backtest/signals/technical.py sma block"),
    "below_sma_200": _span("sma", 200, "[150, 200, 250]",
                           "backtest/signals/technical.py sma block"),
    "price_above_ema_50": _span("ema", 50, "[20, 50, 100]",
                                "backtest/signals/technical.py compute_ema_sma"),
    # ---- channels / bands -------------------------------------------------
    "dc20_breakout_up": [_K("breakout tolerance (close >= upper * (1-t))",
                            0.002, "[0, 0.002, 0.005, 0.01]",
                            "BRACKET production 0.2pct (B591 1pct variant exists "
                            "for dc10 only)",
                            "none - close unpersisted",
                            "the whole band",
                            "backtest/signals/technical.py:1470 region")],
    "dc20_breakout_dn": [_K("mirror of dc20_breakout_up", 0.002,
                            "[0, 0.002, 0.005, 0.01]", "mirror", "none",
                            "the whole band",
                            "backtest/signals/technical.py:1470 region")],
    "bb_20_20_touch_lower": [
        _K("bb (period, k)", "(20, 2.0)", "k [1.5, 2.0, 2.5]; period [20]",
           "BRACKET canon k", "none - bands at other k unpersisted for the touch",
           "the whole band", "backtest/signals/technical.py bb block")],
    "bb_20_20_touch_upper": [_K("mirror of touch_lower", "(20, 2.0)",
                                "k [1.5, 2.0, 2.5]", "mirror", "none",
                                "the whole band",
                                "backtest/signals/technical.py bb block")],
    "bb_20_20_reclaim_from_upper_recent_3d": [
        _K("reclaim recency (bars) + (period, k)", "3 / (20, 2.0)",
           "recency [1, 3, 5]; k [1.5, 2.0, 2.5]",
           "BRACKET production (B800 EVENT conversion, upper mirror)",
           "none - reclaim history unpersisted", "the whole band",
           "backtest/signals/technical.py:1402 region")],
    # ---- bar anatomy ------------------------------------------------------
    "close_above_open": [_K("(structural) c > o - optional min body pct",
                            0.0, "[0, 0.2, 0.5] pct",
                            "BRACKET zero", "none - bar OHLC unpersisted",
                            "the whole band",
                            "backtest/signals/technical.py bar-anatomy block")],
    "close_below_open": [_K("mirror of close_above_open", 0.0,
                            "[0, 0.2, 0.5] pct", "mirror", "none",
                            "the whole band", "technical.py bar-anatomy block")],
    "close_in_top_40pct_of_range": [
        _K("range-position cutoff", 0.40, "[0.25, 0.40, 0.50]",
           "BRACKET production 0.40", "none - bar OHLC unpersisted",
           "the whole band", "backtest/signals/technical.py:1682")],
    "close_in_bottom_40pct_of_range": [
        _K("mirror of top_40pct", 0.40, "[0.25, 0.40, 0.50]", "mirror",
           "none", "the whole band", "backtest/signals/technical.py:1682 region")],
    "vol_above_avg": [_K("volume ratio floor (vol / avg)", 1.0,
                         "[1.0, 1.2, 1.5, 2.0]",
                         "BRACKET production 1.0; avg window is the second knob "
                         "[10, 20, 50]",
                         "TIGHTER floors where the vol ratio key is persisted "
                         "on the fires; else none",
                         "LOOSER, and any window change",
                         "backtest/signals/technical.py:1600")],
    # ---- trend / regime ---------------------------------------------------
    "supertrend_flip_recent_short_5d": [
        _K("(period, multiplier) + flip lookback", "(7, 3.0) + 5d",
           "period/mult [(7,3),(10,3),(7,2)]; lookback [3, 5, 10]",
           "BRACKET canon (B655 EVENT conversion)",
           "none - flip history unpersisted", "the whole band",
           "backtest/signals/technical.py:1179 + flip block")],
    "vix_term_backwardation": [
        _K("backwardation margin (VIX over VIX3M)", 0.0, "[0, 2, 5] pct",
           "BRACKET zero (strict > today)",
           "none - vix3m is not persisted per-fire", "the whole band",
           "backtest/signals/cross_asset.py:216-231")],
    "weekly_bias_bull": [
        _K("weekly ema pair", "(10, 20)", "[(5,10), (10,20), (20,40)]",
           "BRACKET production", "none - weekly emas unpersisted",
           "the whole band", "backtest/signals/multi_timeframe.py:45-90")],
    # ---- ict / gaps -------------------------------------------------------
    "week_open_gap_up_15pct": [
        _K("gap threshold pct (NAME IS DECIMAL-SHIFTED: 15pct = 1.5pct, the "
           "vol_spike naming convention)", 1.5, "[1.0, 1.5, 2.0, 3.0]",
           "BRACKET production 1.5",
           "none - the gap pct is not persisted", "the whole band",
           "backtest/signals/ict_producers.py:147-149")],
    # ---- volume profile / smc / patterns ----------------------------------
    "vp_close_above_poc": [
        _K("profile (lookback_days, n_bins) + side rule", "(60, 40)",
           "lookback [30, 60, 120]; bins [30, 40, 50]",
           "BRACKET production", "none - POC at other params unpersisted",
           "the whole band", "backtest/signals/volume_profile.py:46-58")],
    "smc_mitigation_block_long": [
        _K("smc family knobs (swing_length, event_recency_bars)", "(20, 90)",
           "swing [5, 10, 20, 30, 50]; recency [45, 90, 180]",
           "the smc SPECS family bands (producer_variant_table)",
           "none - other-knob values unpersisted",
           "the whole band", "backtest/signals/smc_ict.py mitigation block",
           env="SMC_SWING_LENGTH / SMC_EVENT_RECENCY_BARS")],
    "smc_mitigation_block_short": [
        _K("mirror of mitigation_long", "(20, 90)", "as long, mirrored",
           "mirror", "none", "the whole band",
           "backtest/signals/smc_ict.py mitigation block",
           env="SMC_SWING_LENGTH / SMC_EVENT_RECENCY_BARS")],
    "smc_ob_bullish_tap_recent_5d": [
        _K("obb SPECS knobs (swing, close_mitigation, tail_n, age, break_pct, "
           "tap lookback 5d)", "SPECS production line",
           "the registered SPECS bands (P1-P6)",
           "SPECS-REGISTERED (producer_variant_table smc_breaker/ob family)",
           "none beyond persisted keys", "the SPECS resim bands",
           "scripts/producer_variant_table.py SPECS + smc_ict.py:387",
           env="SMC_* (registered)")],
    "smc_ob_bearish_tap_recent_5d": [
        _K("mirror of ob_bullish_tap", "SPECS production line",
           "the registered SPECS bands", "SPECS-REGISTERED", "none",
           "the SPECS resim bands",
           "scripts/producer_variant_table.py SPECS",
           env="SMC_* (registered)")],
    "cup_handle_detected": [
        _K("detector tolerances (rim match, depth, handle pullback)",
           "detect_cup_and_handle defaults",
           "each tolerance bracketed [0.5x, 1x, 1.5x] of production",
           "BRACKET the detector's shipped tolerances",
           "none - pattern geometry unpersisted", "the whole band",
           "backtest/signals/chart_patterns.py detect_cup_and_handle")],
    "cup_handle_neckline_break_retest_long": [
        _K("retest window + neckline tolerance", "producer defaults",
           "window [3, 5, 10]; tolerance [0, 0.2, 0.5] pct",
           "BRACKET production (B685 producer)",
           "none", "the whole band",
           "backtest/signals/chart_patterns.py "
           "compute_cup_handle_neckline_break_retest_signals")],
    # ---- events / smart money / factor ------------------------------------
    "insider_cluster_active": [
        _K("cluster rule (unique buyers >= N in window)", "N in 30d",
           "N [2, 3, 5]; window [14, 30, 60] days",
           "BRACKET the shipped cluster rule",
           "N-side TIGHTER via persisted insider_unique_buyers_30d",
           "window changes", "backtest/data/smart_money.py cluster block")],
    "insider_unique_buyers_30d": [
        _K("count window (days)", 30, "[14, 30, 60]",
           "BRACKET production", "count floors via the persisted count",
           "window changes", "backtest/data/smart_money.py:433-439 region")],
    "xs_momentum_top_quintile": [
        _K("quantile cut (quintile)", "top 20pct", "[decile, quintile, tercile]",
           "BRACKET the cut; the underlying 12-1 momentum and decile keys are "
           "persisted", "re-cuts via persisted xs decile/raw keys - OFFLINE",
           "recompute at other formation windows",
           "backtest/signals cross-sectional factor block")],
    "macd_12_26_9_bullish": [
        _K("span triple (mirror of the bearish entry)", "(12,26,9)",
           "[(8,21,5), (12,26,9)] both computed; others new",
           "MEASURED availability (both persisted)",
           "the (8,21,5) swap on persisted keys", "any third triple",
           "backtest/signals/technical.py:634-648")],
    # ---- non-gate display key ---------------------------------------------
    "pair_counterparty": [
        _K("(not a gate) display field naming the paired ticker", "-", "-",
           "no band - rationale text only", "-", "-",
           "backtest/signals/pairs_trading.py:377 region")],
})

# strategy-layer gates the source pattern cannot see (local-variable compares)
# - each IS a persisted magnitude, so tighter sides are OFFLINE today.
STRATEGY_EXTRAS = {
    "williams_r_oversold": [
        {"param": "rsi_2 escape-hatch thresholds (long < 5, short > 95)",
         "production": "5 / 95", "band": "[3, 5] / [95, 97]",
         "basis": "BRACKET production (Connors RSI-2 canon); rsi_2 persisted",
         "offline": "TIGHTER (< 3, > 97) - subset on persisted rsi_2",
         "resim": "LOOSER", "env": None,
         "evidence": "backtest/signals/screener.py strat_williams_r_oversold "
                     "(local rsi_2 compare - invisible to the extractor)"},
    ],
    "ultimate_oscillator": [
        {"param": "rsi_2 escape-hatch thresholds (long < 5, short > 95)",
         "production": "5 / 95", "band": "[3, 5] / [95, 97]",
         "basis": "BRACKET production (Connors RSI-2 canon); rsi_2 persisted",
         "offline": "TIGHTER (< 3, > 97) - subset on persisted rsi_2",
         "resim": "LOOSER", "env": None,
         "evidence": "backtest/signals/screener.py strat_ultimate_oscillator "
                     "(local rsi_2 compare - invisible to the extractor)"},
    ],
    "bollinger_lower": [
        {"param": "VIX-conditional RSI thresholds (low 40/60, mid 45/55, "
                  "high 50/50)", "production": "B1147 widened set",
         "band": "each edge +/-5 around production",
         "basis": "BRACKET production (Connors canonical, B1147 history); "
                  "rsi_2/rsi_14 and vix_percentile all persisted",
         "offline": "TIGHTER edges - subset on persisted rsi keys per band",
         "resim": "LOOSER edges", "env": None,
         "evidence": "backtest/signals/screener.py:1855-1863"},
    ],
}


# ---------------------------------------------------------------------------
# B2851 (owner-caught format conformance): WHAT EACH PRODUCER DOES - the
# per-leg defining condition for the Table A "what it does" column and the
# Formula's producer lines. NUMERIC definitions only where the source was
# READ this arc (evidence beside each group); canon-level wording elsewhere,
# never an invented magnitude.
# ---------------------------------------------------------------------------
def _same(defn, *keys):
    return {k: defn for k in keys}


LEG_DEFN = {}
LEG_DEFN.update(_same("3 consecutive bullish bodies, each close AND open above the prior bar's (strict; technical.py:2104-2107)", "three_white_soldiers"))
LEG_DEFN.update(_same("3 consecutive bearish bodies, each close AND open below the prior bar's (strict; technical.py:2108-2111)", "three_black_crows"))
LEG_DEFN.update(_same("3-bar reversal: bar-3 bearish, mid body < 0.3x its range, bar-1 bullish closing above bar-3's midpoint (technical.py:2085-2094)", "morning_star"))
LEG_DEFN.update(_same("mirror of morning_star (technical.py:2095-2100)", "evening_star"))
LEG_DEFN.update(_same("inside bar: high < prior high AND low > prior low (technical.py:2027)", "inside_bar"))
LEG_DEFN.update(_same("canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer)", "hammer", "shooting_star", "hanging_man", "dark_cloud_cover", "bearish_pin_bar", "bullish_engulfing", "bearish_engulfing"))
LEG_DEFN.update(_same("stochastic-RSI k over period 14; oversold = k < 20 (technical.py:597)", "stochrsi_oversold"))
LEG_DEFN.update(_same("stochastic-RSI overbought = k > 80 (technical.py:598)", "stochrsi_overbought"))
LEG_DEFN.update(_same("k crosses above d while k < 80 (technical.py:599)", "stochrsi_cross_up"))
LEG_DEFN.update(_same("k crosses below d while k > 20 (technical.py:600)", "stochrsi_cross_dn"))
LEG_DEFN.update(_same("Williams %R(14) < -80 (technical.py:702)", "williams_r_oversold"))
LEG_DEFN.update(_same("Chaikin Money Flow, 20-bar rolling (technical.py:1695-1699)", "cmf_positive", "cmf_negative"))
LEG_DEFN.update(_same("CMF crosses the zero line vs the prior bar (technical.py:1706-1707)", "cmf_cross_up", "cmf_cross_dn"))
LEG_DEFN.update(_same("Hull MA(20) rising/falling vs prior bar (technical.py:1304-1327)", "hull_bullish", "hull_bearish"))
LEG_DEFN.update(_same("close vs the Hull MA level (technical.py:1330)", "price_above_hull", "price_below_hull"))
LEG_DEFN.update(_same("ADX(14) > 25 (technical.py:915)", "adx_trending"))
LEG_DEFN.update(_same("Ultimate Oscillator (7,14,28) < 30 / > 70 (technical.py:738-752)", "uo_oversold", "uo_overbought"))
LEG_DEFN.update(_same("stochastic (14,3,3) k/d cross with prior-bar confirmation (technical.py:604-630)", "stoch_bullish_cross", "stoch_bearish_cross"))
LEG_DEFN.update(_same("price within 0.3pct of the named pivot level (near(); technical.py:76)", "near_s1", "near_s2", "near_s3", "near_r1", "near_r2", "near_cam_s3", "near_cam_r3", "near_wood_s1", "near_wood_r1"))
LEG_DEFN.update(_same("today's price above cpr_top / below cpr_bottom (technical.py:146 region)", "above_cpr"))
LEG_DEFN.update(_same("CPR width < 0.05 x prior range - the B654 tight local variant (technical.py:103)", "cpr_narrow_tight"))
LEG_DEFN.update(_same("MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)", "macd_12_26_9_bearish", "macd_12_26_9_bullish"))
LEG_DEFN.update(_same("close beyond the prior-20d extreme with 0.2pct tolerance (technical.py:1470 region)", "dc20_breakout_up", "dc20_breakout_dn"))
LEG_DEFN.update(_same("close at/beyond the Bollinger(20, 2.0) band (bb block)", "bb_20_20_touch_lower", "bb_20_20_touch_upper"))
LEG_DEFN.update(_same("close back inside the band within the last 3 bars after being outside (technical.py:1402 region)", "bb_20_20_reclaim_from_upper_recent_3d"))
LEG_DEFN.update(_same("bar direction: close vs open (bar-anatomy block)", "close_above_open", "close_below_open"))
LEG_DEFN.update(_same("close inside the top/bottom 40pct of the bar's range (technical.py:1682)", "close_in_top_40pct_of_range", "close_in_bottom_40pct_of_range"))
LEG_DEFN.update(_same("volume / 20d average >= 1.0 (technical.py:1600)", "vol_above_avg"))
LEG_DEFN.update(_same("Supertrend(7, 3.0) flipped short within the last 5 bars (B655 EVENT form; technical.py:1179+)", "supertrend_flip_recent_short_5d"))
LEG_DEFN.update(_same("Monday-equivalent open gapped up >= 1.5pct vs prior close (ict_producers.py:147-149; DECIMAL-SHIFTED name)", "week_open_gap_up_15pct"))
LEG_DEFN.update(_same("today's close above the 60d/40-bin volume-profile POC (volume_profile.py:140)", "vp_close_above_poc"))
LEG_DEFN.update(_same("VIX close above VIX3M close - term-structure stress (cross_asset.py:216-231)", "vix_term_backwardation"))
LEG_DEFN.update(_same("weekly close above weekly EMA(10) AND EMA(20) (multi_timeframe.py:45-90)", "weekly_bias_bull"))
LEG_DEFN.update(_same("insider buy cluster active in the 30d window (smart_money.py cluster block)", "insider_cluster_active"))
LEG_DEFN.update(_same("count of unique insider buyers in 30d (smart_money.py)", "insider_unique_buyers_30d"))
LEG_DEFN.update(_same("OBV vs its moving average (technical.py:1570)", "obv_bullish", "obv_bearish"))
LEG_DEFN.update(_same("close vs the named SMA/EMA span (compute_ema_sma family)", "price_above_sma_50", "price_above_sma_200", "below_sma_50", "below_sma_200", "price_above_ema_50", "price_above_ema_200", "below_ema_200"))
LEG_DEFN.update(_same("close vs session VWAP (vwap block)", "above_vwap"))
LEG_DEFN.update(_same("close below the anchored-VWAP from the 20d high (avwap block)", "below_avwap_20high"))
LEG_DEFN.update(_same("EMA-200 cross within the last 5 bars (B722 EVENT form; technical.py:814-825)", "price_above_ema_200_break_recent_5d", "below_ema_200_break_recent_5d"))
LEG_DEFN.update(_same("smc mitigation-block signal at production knobs (smc_ict.py; SPECS family)", "smc_mitigation_block_long", "smc_mitigation_block_short"))
LEG_DEFN.update(_same("order-block tap within 5 bars at the registered SPECS knobs (smc_ict.py:387)", "smc_ob_bullish_tap_recent_5d", "smc_ob_bearish_tap_recent_5d"))
LEG_DEFN.update(_same("cup-and-handle geometry detected / neckline break-retest (chart_patterns.py)", "cup_handle_detected", "cup_handle_neckline_break_retest_long"))
LEG_DEFN.update(_same("cross-sectional 12-1 momentum in the top quintile (factor block)", "xs_momentum_top_quintile"))
LEG_DEFN.update(_same("display field naming the paired ticker - not a gate (pairs_trading.py:377)", "pair_counterparty"))
LEG_DEFN.update(_same("close back inside the LOWER band within 3 bars after being outside (technical.py:1402)", "bb_20_20_reclaim_from_lower_recent_3d"))
LEG_DEFN.update(_same("today's price below cpr_bottom (technical.py:146)", "below_cpr"))
LEG_DEFN.update(_same("Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540)", "rsi_14", "rsi_2"))
LEG_DEFN.update(_same("VIX percentile tercile flag: low < 1/3, high > 2/3 (technical.py:2690-2702)", "vix_band_low", "vix_band_high"))


# ---------------------------------------------------------------------------
# S6-B2862 (council-directed 2026-09-19): AXIS DECOMPOSITION FOR NON-LIST BANDS
#
# build_table_a computed a band's level count as `len(b) if isinstance(b, list)
# else 1`, and 70 of 110 PRODUCER_BANDS entries hold `band` as prose - so 89
# factorial rows across 30 of 41 files printed n=1 beside a band cell that
# visibly listed several values.
#
# This is a HAND-AUTHORED table, deliberately NOT a parser. A regex over
# brackets gets at least six of these wrong, and wrong in the confident
# direction that produced the bug:
#   '[0, 0.3, 0.5] per knob'  is THREE knobs (min body / wick / step pct) at
#       three levels each = 27, not 3. It appears in 7 files.
#   'period [20]; k [1.5, 2.0, 2.5]'  is TWO axes (1 x 3), not one axis of 3.
#   'swing [5, 10, 20, 30, 50]; recency [45, 90, 180]'  is 5 x 3 = 15.
#   'as morning_star, mirrored'  carries no countable band at all - it mirrors
#       another leg, whose axes are already counted there. [] means "contributes
#       no INDEPENDENT axis", which is not the same as "one axis of one level".
#   'the registered SPECS bands'  defers to the SPECS entry, counted there.
#   '[5-30] and [3-45]'  are CONTINUOUS admission bounds with no discrete level
#       set; [1] records that it is a single un-swept axis, not 2 ranges.
#
# An entry may also carry its own "axes" key, which wins over this table.
BAND_AXES: dict[str, list[int]] = {
    "[0.002, 0.003, 0.005, 0.015 (the _wide variant)]": [4],
    "[0, 0.3, 0.5] per knob": [3, 3, 3],
    "[0, 0.25, 0.5]": [3],
    "[20, 50, 100]": [3],
    "[150, 200, 250]": [3],
    "[0, 0.002, 0.005, 0.01]": [4],
    "[0, 0.2, 0.5] pct": [3],
    "[0.25, 0.40, 0.50]": [3],
    "period [20]; k [1.5, 2.0, 2.5]": [1, 3],
    "k [1.5, 2.0, 2.5]; period [20]": [3, 1],
    "k [1.5, 2.0, 2.5]": [3],
    "recency [1, 3, 5]; k [1.5, 2.0, 2.5]": [3, 3],
    "[0.25/0.75] and [1/3, 2/3]": [2],
    "[0.75] alternative": [1],
    "[(8,21,5), (12,26,9)] both computed in production; other triples are new": [2],
    "[5-30] and [3-45]": [1],
    "optional containment-margin pct [0, 0.1, 0.25]": [3],
    "[0.2, 0.3, 0.4]": [3],
    "midpoint vs [0.382, 0.5, 0.618] retrace": [4],
    "as morning_star, mirrored": [],
    "as bullish, mirrored (guard k above [70, 80])": [2],
    "as obv_bullish, mirrored": [],
    "as long, mirrored": [],
    "the registered SPECS bands (P1-P6)": [],
    "the registered SPECS bands": [],
    "[20, 25, 30]": [3],
    "[(7,14,28), (5,10,20), (14,28,56)]": [3],
    "[70, 75, 80]": [3],
    "[(14,3,3), (5,3,3), (21,5,5)]": [3],
    "add guard band: k below [20, 30] at cross": [2],
    "[9, 14, 21]": [3],
    "[2, 3, 5]": [3],
    "MA span [10, 20, 50]": [3],
    "[0, 1, 2] pct": [3],
    "[1.0, 1.2, 1.5, 2.0]": [4],
    "period/mult [(7,3),(10,3),(7,2)]; lookback [3, 5, 10]": [3, 3],
    "[0, 2, 5] pct": [3],
    "[(5,10), (10,20), (20,40)]": [3],
    "[1.0, 1.5, 2.0, 3.0]": [4],
    "lookback [30, 60, 120]; bins [30, 40, 50]": [3, 3],
    "swing [5, 10, 20, 30, 50]; recency [45, 90, 180]": [5, 3],
    "each tolerance bracketed [0.5x, 1x, 1.5x] of production": [3],
    "window [3, 5, 10]; tolerance [0, 0.2, 0.5] pct": [3, 3],
    "N [2, 3, 5]; window [14, 30, 60] days": [3, 3],
    "[14, 30, 60]": [3],
    "[decile, quintile, tercile]": [3],
    "[(8,21,5), (12,26,9)] both computed; others new": [2],
    # a display-only field: not a gate, carries no swept axis
    "-": [],
}


def band_axes(row: dict) -> list[int]:
    """The INDEPENDENT axes a band row contributes, as level counts.

    A list band is one axis of len(band). A non-list band must be declared -
    either on the row ("axes") or in BAND_AXES. Anything else raises, because
    the alternative is the silent n=1 that S6-B2862 is about."""
    if "axes" in row:
        return [int(x) for x in row["axes"]]
    b = row.get("band")
    if isinstance(b, list):
        return [len(b)]
    key = str(b)
    if key in BAND_AXES:
        return list(BAND_AXES[key])
    raise ValueError(
        "table_a_bands: band %r on param %r has no axis decomposition. A "
        "non-list band cannot be counted by len() - add it to BAND_AXES (by "
        "hand, having read what it means) or give the row an explicit 'axes' "
        "key. S6-B2862." % (b, row.get("param")))


def _b2862_validate_every_band_is_countable() -> None:
    """Runs at import: no PRODUCER_BANDS row may carry an uncountable band."""
    bad = []
    for leg, rows in PRODUCER_BANDS.items():
        for r in rows:
            try:
                band_axes(r)
            except ValueError as e:
                bad.append("%s/%s: %s" % (leg, r.get("param"), e))
    if bad:
        raise ValueError("S6-B2862 - uncountable bands:\n  " + "\n  ".join(bad))


_b2862_validate_every_band_is_countable()
