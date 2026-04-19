"""
data/smart_money.py — Smart money + analyst consensus data.

Sources:
  - Quiver Quantitative free tier: congressional, insider, 13F, analyst revisions
  - yfinance: analyst consensus, price targets, EPS estimates (no key required)
  - SEC EDGAR: Form 4, 13D/13G
  - OpenInsider: insider trades

All functions enforce point-in-time data (as_of parameter).
QUIVER_API_KEY env var required for Quiver data — gracefully skips if absent.
yfinance analyst data requires no API key.
"""

import os
import time
import logging
import requests
from datetime import date, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

QUIVER_KEY  = os.environ.get("QUIVER_API_KEY", "")
QUIVER_BASE = "https://api.quiverquant.com/beta"
_DELAY      = 1.5


def _quiver_get(endpoint: str) -> Optional[list]:
    if not QUIVER_KEY:
        return None
    try:
        resp = requests.get(
            f"{QUIVER_BASE}/{endpoint}",
            headers={"Authorization": f"Token {QUIVER_KEY}"},
            timeout=20,
        )
        if resp.status_code == 429:
            time.sleep(60)
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.debug("Quiver %s: %s", endpoint, exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# ANALYST CONSENSUS — yfinance primary, no API key required
# ─────────────────────────────────────────────────────────────────────────────

def get_analyst_data(ticker: str, as_of: date) -> dict:
    """
    Fetch analyst consensus, price targets, EPS estimates, and recent revisions.

    Returns dict with:
      consensus          — Strong Buy / Buy / Hold / Sell / Strong Sell
      buy_count          — number of Buy + Strong Buy ratings
      hold_count         — number of Hold ratings
      sell_count         — number of Sell + Strong Sell ratings
      total_analysts     — total analysts covering
      buy_pct            — % of analysts with Buy/Strong Buy
      target_mean        — average price target
      target_high        — highest price target
      target_low         — lowest price target
      target_upside_pct  — % upside from current price to mean target
      eps_estimate_next_q — EPS consensus estimate next quarter
      eps_estimate_next_y — EPS consensus estimate next year
      recent_upgrades    — upgrades in last 30 days (from Quiver if available)
      recent_downgrades  — downgrades in last 30 days
      revision_direction — "up" / "down" / "flat"
      signal             — "strong_buy" / "buy" / "hold" / "sell" / "unknown"
    """
    result = {
        "consensus": "unknown", "buy_count": 0, "hold_count": 0,
        "sell_count": 0, "total_analysts": 0, "buy_pct": 0.0,
        "target_mean": None, "target_high": None, "target_low": None,
        "target_upside_pct": None, "eps_estimate_next_q": None,
        "eps_estimate_next_y": None, "recent_upgrades": 0,
        "recent_downgrades": 0, "revision_direction": "flat",
        "signal": "unknown",
    }
    try:
        t    = yf.Ticker(ticker)
        info = t.info

        # Consensus label
        rec_mean = info.get("recommendationMean")   # 1=Strong Buy, 5=Strong Sell
        rec_key  = info.get("recommendationKey", "").lower()
        result["consensus"] = {
            "strong_buy": "Strong Buy", "buy": "Buy",
            "hold": "Hold", "sell": "Sell", "strong_sell": "Strong Sell",
        }.get(rec_key, rec_key.replace("_"," ").title() if rec_key else "Unknown")

        # Analyst counts
        n = info.get("numberOfAnalystOpinions", 0) or 0
        result["total_analysts"] = n

        # Price targets
        cur  = info.get("currentPrice") or info.get("regularMarketPrice")
        mean = info.get("targetMeanPrice")
        high = info.get("targetHighPrice")
        low  = info.get("targetLowPrice")
        result["target_mean"] = round(mean, 2) if mean else None
        result["target_high"] = round(high, 2) if high else None
        result["target_low"]  = round(low,  2) if low  else None
        if mean and cur and cur > 0:
            result["target_upside_pct"] = round((mean - cur) / cur * 100, 2)

        # EPS estimates
        try:
            earnings = t.earnings_estimate
            if earnings is not None and not earnings.empty:
                if "0q" in earnings.index:
                    result["eps_estimate_next_q"] = earnings.loc["0q", "Avg"] \
                        if "Avg" in earnings.columns else None
                if "0y" in earnings.index:
                    result["eps_estimate_next_y"] = earnings.loc["0y", "Avg"] \
                        if "Avg" in earnings.columns else None
        except Exception:
            pass

        # Recommendations history — parse buy/hold/sell counts and recent changes
        try:
            recs = t.recommendations
            if recs is not None and not recs.empty:
                # Point-in-time: only use recommendations on or before as_of
                recs.index = pd.to_datetime(recs.index).tz_localize(None)
                recs = recs[recs.index.date <= as_of]
                if not recs.empty:
                    # Count latest snapshot
                    latest = recs.iloc[-1]
                    sb = int(latest.get("strongBuy", 0) or 0)
                    b  = int(latest.get("buy",       0) or 0)
                    h  = int(latest.get("hold",      0) or 0)
                    s  = int(latest.get("sell",      0) or 0)
                    ss = int(latest.get("strongSell",0) or 0)
                    total = sb + b + h + s + ss
                    result["buy_count"]      = sb + b
                    result["hold_count"]     = h
                    result["sell_count"]     = s + ss
                    result["total_analysts"] = total
                    result["buy_pct"]        = round((sb+b)/total*100, 1) if total else 0
        except Exception:
            pass

        # Recent upgrades/downgrades (last 30 days)
        try:
            upgrades = t.upgrades_downgrades
            if upgrades is not None and not upgrades.empty:
                upgrades.index = pd.to_datetime(upgrades.index).tz_localize(None)
                window_start   = pd.Timestamp(as_of - timedelta(days=30))
                recent = upgrades[
                    (upgrades.index >= window_start) &
                    (upgrades.index.date <= as_of)
                ]
                if not recent.empty and "Action" in recent.columns:
                    result["recent_upgrades"]   = int((recent["Action"].str.lower() == "up").sum())
                    result["recent_downgrades"]  = int((recent["Action"].str.lower() == "down").sum())
                    ups   = result["recent_upgrades"]
                    downs = result["recent_downgrades"]
                    result["revision_direction"] = (
                        "up"   if ups > downs else
                        "down" if downs > ups else "flat"
                    )
        except Exception:
            pass

        # Quiver analyst revisions enhancement (if key available)
        if QUIVER_KEY:
            quiver_revs = _quiver_get(f"historical/analystestimates/{ticker}")
            if quiver_revs:
                time.sleep(_DELAY)
                df_q = pd.DataFrame(quiver_revs)
                if not df_q.empty and "Date" in df_q.columns:
                    df_q["Date"] = pd.to_datetime(df_q["Date"]).dt.date
                    recent_q = df_q[
                        (df_q["Date"] >= as_of - timedelta(days=30)) &
                        (df_q["Date"] <= as_of)
                    ]
                    if not recent_q.empty:
                        # Quiver provides direction field
                        if "Direction" in recent_q.columns:
                            ups   = (recent_q["Direction"].str.lower() == "up").sum()
                            downs = (recent_q["Direction"].str.lower() == "down").sum()
                            result["recent_upgrades"]   = max(result["recent_upgrades"],   int(ups))
                            result["recent_downgrades"] = max(result["recent_downgrades"], int(downs))
                            if ups > downs:
                                result["revision_direction"] = "up"
                            elif downs > ups:
                                result["revision_direction"] = "down"

        # Derive signal
        buy_pct = result["buy_pct"]
        rev     = result["revision_direction"]
        ups_cnt = result["recent_upgrades"]
        if buy_pct >= 70 and rev == "up" and ups_cnt >= 2:
            result["signal"] = "strong_buy"
        elif buy_pct >= 60 and rev in ("up", "flat"):
            result["signal"] = "buy"
        elif buy_pct < 40 or rev == "down":
            result["signal"] = "sell"
        elif result["total_analysts"] > 0:
            result["signal"] = "hold"

    except Exception as exc:
        logger.debug("get_analyst_data(%s): %s", ticker, exc)

    return result


def analyst_bullets(analyst: dict, current_price: Optional[float] = None) -> list:
    """
    Generate bullet points for the site card analyst section.
    Returns list of plain-English strings.
    """
    bullets = []
    n     = analyst.get("total_analysts", 0)
    cons  = analyst.get("consensus", "Unknown")
    b_pct = analyst.get("buy_pct", 0)
    b_cnt = analyst.get("buy_count", 0)
    h_cnt = analyst.get("hold_count", 0)
    s_cnt = analyst.get("sell_count", 0)

    if n > 0:
        bullets.append(
            f"Analyst consensus: {cons} — {b_cnt} Buy / {h_cnt} Hold / {s_cnt} Sell "
            f"({n} analysts covering)"
        )

    tgt = analyst.get("target_mean")
    upside = analyst.get("target_upside_pct")
    if tgt:
        upside_str = f" — {upside:+.1f}% from current" if upside is not None else ""
        bullets.append(f"Average price target: ${tgt:.2f}{upside_str}")

    tgt_h = analyst.get("target_high")
    tgt_l = analyst.get("target_low")
    if tgt_h and tgt_l:
        bullets.append(f"Target range: ${tgt_l:.2f} – ${tgt_h:.2f}")

    eps_q = analyst.get("eps_estimate_next_q")
    if eps_q is not None:
        bullets.append(f"EPS estimate next quarter: ${eps_q:.2f} (consensus)")

    ups   = analyst.get("recent_upgrades", 0)
    downs = analyst.get("recent_downgrades", 0)
    rev   = analyst.get("revision_direction", "flat")
    if ups > 0 or downs > 0:
        if rev == "up":
            bullets.append(
                f"{ups} upgrade{'s' if ups != 1 else ''} in last 30 days — "
                f"positive estimate momentum"
            )
        elif rev == "down":
            bullets.append(
                f"⚠️  {downs} downgrade{'s' if downs != 1 else ''} in last 30 days — "
                f"negative estimate momentum"
            )
        else:
            bullets.append(f"Mixed revisions: {ups} up / {downs} down in last 30 days")

    if not bullets:
        bullets.append("Analyst data unavailable for this instrument")

    return bullets


# ─────────────────────────────────────────────────────────────────────────────
# CONGRESSIONAL TRADES
# ─────────────────────────────────────────────────────────────────────────────

def congressional_signal(ticker: str, as_of: date, lookback_days: int = 45) -> dict:
    data = _quiver_get(f"historical/congresstrading/{ticker}")
    if not data:
        return {"signal": "none", "buy_count": 0, "sell_count": 0}
    time.sleep(_DELAY)
    try:
        df = pd.DataFrame(data)
        if df.empty:
            return {"signal": "none", "buy_count": 0, "sell_count": 0}
        df["disclosure_date"] = pd.to_datetime(
            df.get("Date", df.get("date", ""))).dt.date
        df = df[df["disclosure_date"] <= as_of]
        window_start = as_of - timedelta(days=lookback_days)
        recent = df[df["disclosure_date"] >= window_start]
        buys   = recent[recent.get("Transaction","transaction").str.contains(
            "Purchase|Buy", case=False, na=False)]
        sells  = recent[recent.get("Transaction","transaction").str.contains(
            "Sale|Sell", case=False, na=False)]
        senate_buys  = buys[buys.get("Chamber","chamber").str.lower() == "senate"]
        cluster_buy  = buys.get("Representative","representative").nunique() >= 3
        signal = "none"
        if len(sells) > len(buys) and len(sells) >= 2:
            signal = "sell"
        elif len(senate_buys) >= 2 or cluster_buy:
            signal = "strong_buy"
        elif len(buys) >= 1:
            signal = "buy"
        return {"signal": signal, "buy_count": len(buys), "sell_count": len(sells),
                "senate_buys": len(senate_buys), "cluster_buy": cluster_buy}
    except Exception as exc:
        logger.debug("congressional_signal(%s): %s", ticker, exc)
        return {"signal": "none", "buy_count": 0, "sell_count": 0}


# ─────────────────────────────────────────────────────────────────────────────
# INSIDER TRADES
# ─────────────────────────────────────────────────────────────────────────────

def insider_signal(ticker: str, as_of: date, lookback_days: int = 30) -> dict:
    data = _quiver_get(f"historical/insiders/{ticker}")
    if not data:
        return {"signal": "none", "buy_count": 0, "sell_count": 0}
    time.sleep(_DELAY)
    try:
        df = pd.DataFrame(data)
        if df.empty:
            return {"signal": "none", "buy_count": 0, "sell_count": 0}
        df["filing_date"] = pd.to_datetime(
            df.get("Date", df.get("date", ""))).dt.date
        df = df[df["filing_date"] <= as_of]
        # Exclude non-discretionary
        tx_col = "Transaction" if "Transaction" in df else "transaction"
        df = df[~df[tx_col].str.contains(
            "Option|Exercise|10b5-1|Gift|Transfer", case=False, na=False)]
        window_start = as_of - timedelta(days=lookback_days)
        recent = df[df["filing_date"] >= window_start]
        buys   = recent[recent[tx_col].str.contains(
            "Purchase|Buy|Acquisition", case=False, na=False)]
        sells  = recent[recent[tx_col].str.contains(
            "Sale|Sell", case=False, na=False)]
        role_col = "InsiderTitle" if "InsiderTitle" in df else "insiderTitle"
        ceo_buy  = buys[role_col].str.contains("CEO|Chief Executive", case=False, na=False).any() \
                   if role_col in buys else False
        cluster  = buys.get("InsiderName", buys.get("insiderName",
                   pd.Series())).nunique() >= 3
        signal   = "none"
        if sells.get("InsiderName", sells.get("insiderName",
                     pd.Series())).nunique() >= 3:
            signal = "cluster_sell"
        elif ceo_buy and cluster:
            signal = "strong_buy"
        elif ceo_buy or cluster:
            signal = "buy"
        elif len(buys) >= 1:
            signal = "weak_buy"
        return {"signal": signal, "buy_count": len(buys), "sell_count": len(sells),
                "ceo_buy": ceo_buy, "cluster_buy": cluster}
    except Exception as exc:
        logger.debug("insider_signal(%s): %s", ticker, exc)
        return {"signal": "none", "buy_count": 0, "sell_count": 0}


# ─────────────────────────────────────────────────────────────────────────────
# INSTITUTIONAL (13F)
# ─────────────────────────────────────────────────────────────────────────────

def institutional_signal(ticker: str, as_of: date) -> dict:
    data = _quiver_get(f"historical/institutionalholdings/{ticker}")
    if not data:
        return {"signal": "none"}
    time.sleep(_DELAY)
    try:
        df = pd.DataFrame(data)
        if df.empty:
            return {"signal": "none"}
        df["quarter_end"]    = pd.to_datetime(
            df.get("Date", df.get("date", ""))).dt.date
        df["available_after"] = df["quarter_end"].apply(
            lambda d: d + timedelta(days=45) if d else None)
        df = df[df["available_after"] <= as_of]
        if df.empty:
            return {"signal": "none"}
        latest_q = df["quarter_end"].max()
        latest   = df[df["quarter_end"] == latest_q]
        sc = "SharesChange" if "SharesChange" in df else "sharesChange"
        sh = "Shares" if "Shares" in df else "shares"
        df[sc] = pd.to_numeric(df.get(sc, 0), errors="coerce").fillna(0)
        df[sh] = pd.to_numeric(df.get(sh, 0), errors="coerce").fillna(0)
        new_pos   = (latest[sc] == latest[sh]).sum()
        increased = (latest[sc] > 0).sum()
        decreased = (latest[sc] < 0).sum()
        signal = "none"
        if new_pos >= 3 or (new_pos >= 1 and increased >= 2):
            signal = "strong_buy"
        elif new_pos >= 1 or increased >= 2:
            signal = "buy"
        elif decreased > increased:
            signal = "negative"
        return {"signal": signal, "new_positions": int(new_pos),
                "increased": int(increased), "decreased": int(decreased)}
    except Exception as exc:
        logger.debug("institutional_signal(%s): %s", ticker, exc)
        return {"signal": "none"}


# ─────────────────────────────────────────────────────────────────────────────
# COMPOSITE SMART MONEY SCORE
# ─────────────────────────────────────────────────────────────────────────────

def smart_money_score(
    ticker: str, as_of: date,
    cong: Optional[dict] = None,
    ins:  Optional[dict] = None,
    inst: Optional[dict] = None,
) -> dict:
    if cong is None: cong = congressional_signal(ticker, as_of)
    if ins  is None: ins  = insider_signal(ticker, as_of)
    if inst is None: inst = institutional_signal(ticker, as_of)

    cs, iss, ints = (cong.get("signal","none"),
                     ins.get("signal","none"),
                     inst.get("signal","none"))

    if cs == "sell" and iss == "cluster_sell":
        return {"composite_signal": "congressional_sell+insider_cluster_sell",
                "score": -5,
                "details": {"congressional": cs, "insider": iss, "institutional": ints}}

    score = 0
    if cs  == "strong_buy":  score += 4
    elif cs == "buy":         score += 2
    elif cs == "sell":        score -= 3
    if iss == "strong_buy":  score += 4
    elif iss == "buy":        score += 2
    elif iss == "weak_buy":   score += 1
    elif iss == "cluster_sell": score -= 3
    if ints == "strong_buy": score += 2
    elif ints == "buy":       score += 1
    elif ints == "negative":  score -= 1

    if score >= 6:   composite = "congressional+insider_cluster"
    elif score >= 4: composite = "congressional_or_insider"
    elif score >= 2: composite = "any_buy"
    elif score >= 1: composite = "weak_buy"
    elif score <= -4: composite = "congressional_sell+insider_cluster_sell"
    elif score < 0:  composite = "negative"
    else:            composite = "none"

    return {"composite_signal": composite, "score": score,
            "details": {"congressional": cs, "insider": iss, "institutional": ints}}
