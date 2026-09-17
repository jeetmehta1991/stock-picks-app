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
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:2108-2111"},
        {"param": "min_body_pct_of_range per candle", "production": 0.0,
         "band": [0.0, 0.3, 0.5],
         "basis": "CANON (Nison long-body crows); production accepts ANY body",
         "offline": "none", "resim": "the whole band", "env": None,
         "evidence": "technical.py:2109 (c<o only - no magnitude)"},
        {"param": "min_step_down_pct (close[i] below close[i-1] by)",
         "production": 0.0, "band": [0.0, 0.1, 0.25],
         "basis": "BRACKET zero upward; strict < today",
         "offline": "none", "resim": "the whole band", "env": None,
         "evidence": "technical.py:2110"},
        {"param": "max_lower_wick_pct (close near low)", "production": None,
         "band": [None, 0.3, 0.2],
         "basis": "CANON (crows close at/near lows); production unenforced",
         "offline": "none", "resim": "the whole band", "env": None,
         "evidence": "technical.py:2108-2111 (absent today)"},
    ],
    # mirror: same producer block, bullish inequalities
    "three_white_soldiers": [
        {"param": "n_bars / min_body / min_step_up / max_upper_wick "
                  "(the bearish rows mirrored)", "production": "3 / 0 / 0 / -",
         "band": "as three_black_crows, mirrored",
         "basis": "CANON (Nison soldiers)", "offline": "none",
         "resim": "the whole band", "env": None,
         "evidence": "backtest/signals/technical.py:2104-2107"},
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
