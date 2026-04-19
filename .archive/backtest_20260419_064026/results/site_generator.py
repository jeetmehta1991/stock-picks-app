"""
results/site_generator.py — Generate daily site picks JSON for the website.

Produces site_picks_YYYY-MM-DD.json containing:
  - active_picks (EXCEPTIONAL + VERY_HIGH) — up to 10 total
  - watchlist (HIGH + MEDIUM_HIGH)
  - market_context (regime, VIX, macro summary)

Each pick card contains:
  - ticker, direction, confidence_tier
  - entry_zone (lower + upper bounds)
  - initial_stop (specific price)
  - estimated_hold_days (from regime_performance)
  - technical_bullets (list)
  - smart_money_bullets (list)
  - macro_bullets (list)
  - risk_bullets (list)
  - position_sizing (% and dollar amount on $10k)
  - why_this_trade_paragraph (Decision Agent output)
  - signals_snapshot (key numeric values)
"""

import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from backtest.config import CONFIDENCE_TIERS, SITE, TRAILING_STOP

logger = logging.getLogger(__name__)


def build_entry_zone(close: float, atr: float, category: str, direction: str) -> dict:
    """Build entry zone with lower and upper bounds."""
    from backtest.config import ENTRY_GAP_ATR_MULT
    mult  = ENTRY_GAP_ATR_MULT.get(category, 1.5)
    lower = round(close, 2)
    upper = round(close + mult * atr, 2) if direction == "long" else round(close - mult * atr, 2)
    return {"lower": lower, "upper": upper, "note": f"Valid entry up to {mult}× ATR from close"}


def build_stop_price(entry_price: float, direction: str) -> dict:
    """Calculate initial trailing stop price."""
    pct  = TRAILING_STOP["initial_pct"]
    stop = entry_price * (1 - pct) if direction == "long" else entry_price * (1 + pct)
    return {
        "price":       round(stop, 2),
        "pct_from_entry": pct * 100,
        "description": f"Trailing stop at {pct*100:.0f}% — moves up with price, never reverses",
    }


def build_position_sizing(confidence_tier: str, direction: str) -> dict:
    """Build position sizing guidance from confidence tier."""
    cfg  = CONFIDENCE_TIERS.get(confidence_tier, CONFIDENCE_TIERS["LOW"])
    pct  = cfg["position_pct"]
    return {
        "pct_of_capital":  pct * 100,
        "on_10k_portfolio": round(pct * 10_000, 0),
        "on_50k_portfolio": round(pct * 50_000, 0),
        "note": ("Full position — maximum allocation" if pct >= 0.02
                 else "Reduced position — watch list only" if pct == 0
                 else f"{pct*100:.1f}% of capital per trade"),
    }


def build_smart_money_bullets(smart_money_data: dict) -> list:
    """Generate smart money bullet points from signal data."""
    bullets = []
    cong  = smart_money_data.get("congressional_sig", {})
    ins   = smart_money_data.get("insider_sig", {})
    inst  = smart_money_data.get("institutional_sig", {})

    if cong.get("signal") in ("strong_buy", "buy"):
        ch = cong.get("chamber", "Congress")
        bk = cong.get("buy_count", 0)
        bullets.append(f"Congressional buy signal — {ch}, {bk} purchase(s) in last 45 days")
        if cong.get("cluster_buy"):
            bullets.append("Cluster congressional buying — multiple politicians buying simultaneously")

    if ins.get("signal") in ("strong_buy", "buy"):
        bullets.append("Insider buying detected — Form 4 disclosure")
        if ins.get("ceo_buy"):
            bullets.append("CEO discretionary purchase — strongest company-level signal")
        if ins.get("cluster_buy"):
            bullets.append(f"Cluster insider buying — {ins.get('buy_count',0)} insiders in 30 days")

    if inst.get("signal") in ("strong_buy", "buy"):
        new = inst.get("new_positions", 0)
        if new > 0:
            bullets.append(f"{new} new institutional position(s) — latest 13F filing")
        inc = inst.get("increased_positions", 0)
        if inc > 0:
            bullets.append(f"{inc} institutions increased position last quarter")

    if not bullets:
        bullets.append("No smart money signal — technical setup only")

    return bullets


def build_macro_bullets(macro: dict) -> list:
    """Generate macro bullet points."""
    bullets = []
    vix = macro.get("vix_value")
    yc  = macro.get("yield_curve_regime", "unknown")
    dxy = macro.get("dxy_trend", "unknown")
    reg = macro.get("regime", "neutral")

    if vix:
        vix_desc = "low — favours longs" if vix < 20 else "elevated — risk-off" if vix > 30 else "normal"
        bullets.append(f"VIX at {vix:.1f} — {vix_desc}")

    yc_map = {
        "normal":   "Yield curve normal — healthy risk-on environment",
        "flat":     "Yield curve flat — neutral macro signal",
        "inverted": "Yield curve inverted — recession risk, be selective",
        "unknown":  "Yield curve data unavailable",
    }
    bullets.append(yc_map.get(yc, f"Yield curve: {yc}"))

    if dxy == "falling":
        bullets.append("Dollar index falling — tailwind for large-cap US stocks")
    elif dxy == "rising":
        bullets.append("Dollar index rising — headwind for multinationals")

    return bullets


def build_risk_bullets(risk_flags: dict, direction: str) -> list:
    """Generate risk flag bullets."""
    bullets = []
    earn   = risk_flags.get("days_to_earnings")
    near_e = risk_flags.get("near_fomc") or risk_flags.get("near_cpi") or risk_flags.get("near_nfp")
    ev_type = risk_flags.get("event_type", "economic event")
    vol_r   = risk_flags.get("volume_ratio", 1.0)

    if earn and earn <= 14:
        bullets.append(f"⚠️  Earnings in {earn} days — trailing stop protects downside, consider sizing down")
    elif earn and earn <= 30:
        bullets.append(f"Earnings in {earn} days — monitor closely")

    if near_e:
        bullets.append(f"⚠️  {ev_type} in {risk_flags.get('event_days_away',2)} days — consider waiting or sizing down")

    if vol_r and vol_r >= 1.5:
        bullets.append(f"Volume {vol_r:.1f}× average — strong participation confirms signal")
    elif vol_r and vol_r < 0.8:
        bullets.append(f"⚠️  Volume below average ({vol_r:.1f}×) — reduced conviction")

    if not bullets:
        bullets.append("No major risk flags at entry")

    return bullets


def build_site_card(
    candidate: dict,
    strategy_entry: dict,
    smart_money_data: dict,
    macro: dict,
    sent: dict,
    optimal_hold: Optional[int],
    context_paragraph: str,
    confidence_tier: str,
) -> dict:
    """Build complete site card for a single pick."""
    ticker    = candidate["ticker"]
    close     = candidate["last_close"]
    atr       = candidate.get("atr", close * 0.02)
    direction = strategy_entry["direction"]
    category  = strategy_entry["category"]

    entry_zone  = build_entry_zone(close, atr, category, direction)
    stop        = build_stop_price(entry_zone["lower"], direction)
    sizing      = build_position_sizing(confidence_tier, direction)
    sm_bullets  = build_smart_money_bullets(smart_money_data)
    macro_bulls = build_macro_bullets({**macro, "regime": macro.get("regime","neutral")})
    risk_bulls  = build_risk_bullets({
        "days_to_earnings": candidate.get("days_to_earnings"),
        "near_fomc":        macro.get("near_high_impact_event"),
        "event_type":       macro.get("event_type"),
        "event_days_away":  macro.get("event_days_away"),
        "volume_ratio":     candidate.get("signals", {}).get("vol_ratio_20d", 1.0),
    }, direction)

    regime_desc = {
        "bull":    "Bull — VIX low, SPY uptrend",
        "neutral": "Neutral — mixed conditions",
        "bear":    "Bear — VIX elevated, SPY downtrend",
        "crisis":  "Crisis — extreme volatility",
    }.get(macro.get("regime","neutral"), "Unknown")

    return {
        "ticker":           ticker,
        "direction":        direction.upper(),
        "confidence_tier":  confidence_tier,
        "confidence_label": CONFIDENCE_TIERS.get(confidence_tier, {}).get("site_label",""),
        "section":          CONFIDENCE_TIERS.get(confidence_tier, {}).get("section",""),
        "strategy":         strategy_entry["strategy"],
        "category":         category,
        "regime":           regime_desc,

        "entry_zone":       entry_zone,
        "initial_stop":     stop,
        "trailing_stop_rule": "10% below highest closing price — moves up, never down",
        "estimated_hold_days": optimal_hold or "5–15",

        "technical_bullets":   strategy_entry["context_bullets"],
        "smart_money_bullets": sm_bullets,
        "macro_bullets":       macro_bulls,
        "risk_bullets":        risk_bulls,

        "position_sizing":  sizing,

        "why_this_trade":   context_paragraph or _auto_paragraph(
            ticker, direction, strategy_entry, macro, smart_money_data, stop),

        "signals_snapshot": {
            k: v for k, v in candidate.get("signals", {}).items()
            if k in ["rsi_14","macd_12_26_9_hist","adx","vwap","vol_ratio_20d",
                     "atr","bb_20_20_bandwidth","stoch_k","hull_ma","psar_bullish"]
        },

        "generated_at":    datetime.utcnow().isoformat(),
    }


def _auto_paragraph(ticker, direction, strat, macro, sm, stop) -> str:
    """Rule-based paragraph when agent is not available."""
    bullets = strat["context_bullets"]
    sm_sig  = sm.get("composite_signal","none")
    vix     = macro.get("vix_value")
    regime  = macro.get("regime","neutral")

    lines = [f"{ticker} shows a {strat['strategy'].replace('_',' ')} signal today. "]
    if bullets:
        lines.append(bullets[0] + ". ")
        if len(bullets) > 1:
            lines.append(bullets[1].lower() + ". ")
    if sm_sig not in ("none","negative"):
        lines.append("Smart money signals are supportive. ")
    if vix and vix < 20:
        lines.append(f"Macro environment is favourable — VIX at {vix:.1f}. ")
    lines.append(f"Trailing stop set at ${stop['price']:.2f} — {stop['pct_from_entry']:.0f}% "
                 f"below entry, moves up with price as the trade progresses.")
    return "".join(lines)


def generate_daily_picks(
    candidates: list,
    smart_money_map: dict,
    macro: dict,
    sent: dict,
    regime_perf: dict,
    as_of: date,
    output_dir: Path,
) -> dict:
    """
    Generate the daily site_picks JSON file.

    candidates:      list of screener results (sorted by strategy_count)
    smart_money_map: {ticker: smart_money_score_dict}
    regime_perf:     {strategy_name: optimal_hold_days} from backtest results
    """
    active_picks = []
    watchlist    = []
    seen_tickers = set()

    active_tiers    = set(SITE["active_picks_tiers"])
    watchlist_tiers = set(SITE["watchlist_tiers"])
    max_picks       = SITE["max_active_picks"]

    for cand in candidates:
        if len(active_picks) + len(watchlist) >= max_picks * 2:
            break
        ticker = cand["ticker"]
        if ticker in seen_tickers:
            continue

        sm   = smart_money_map.get(ticker, {"composite_signal":"none","score":0})
        tier = _assign_tier(len(cand.get("strategies",[])), sm, macro, sent)

        if tier not in active_tiers and tier not in watchlist_tiers:
            continue

        for strat_entry in cand.get("strategies", []):
            hold = regime_perf.get(strat_entry["strategy"])
            card = build_site_card(
                cand, strat_entry, sm, macro, sent, hold, "", tier)

            if tier in active_tiers and len(active_picks) < max_picks:
                active_picks.append(card)
            elif tier in watchlist_tiers:
                watchlist.append(card)

            seen_tickers.add(ticker)
            break

    output = {
        "date":           as_of.isoformat(),
        "generated_at":   datetime.utcnow().isoformat(),
        "market_context": {
            "regime":      macro.get("regime","unknown"),
            "vix":         macro.get("vix_value"),
            "yield_curve": macro.get("yield_curve_regime"),
            "dxy_trend":   macro.get("dxy_trend"),
            "aaii_signal": sent.get("aaii",{}).get("signal"),
            "fear_greed":  sent.get("fear_greed",{}).get("score"),
        },
        "active_picks":   active_picks,
        "watchlist":      watchlist,
        "total_picks":    len(active_picks),
        "total_watchlist": len(watchlist),
    }

    filename = f"site_picks_{as_of.isoformat()}.json"
    path     = output_dir / filename
    with open(path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    logger.info("Wrote %s (%d picks, %d watchlist)", filename,
                len(active_picks), len(watchlist))

    return output


def _assign_tier(strategy_count, sm, macro, sent) -> str:
    """Mirror of engine's tier assignment for live use."""
    sm_sig = sm.get("composite_signal", "none")
    if sm_sig in ("congressional+insider_cluster",) and strategy_count >= 3:
        return "EXCEPTIONAL"
    if sm_sig in ("congressional_or_insider",) and strategy_count >= 2:
        return "VERY_HIGH"
    if strategy_count >= 3:
        return "HIGH"
    if strategy_count >= 2:
        return "MEDIUM_HIGH"
    if sm.get("score", 0) >= 2 and strategy_count >= 1:
        return "MEDIUM"
    return "LOW"
