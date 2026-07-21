import pandas as pd, json, time, os
from datetime import date
import backtest.signals.screener as sc

# data-fed strategies + the signal key that gates them + a non-default test
DATAFED = {
 "classification_changed_recent":"classification_changed_recent",
 "insider_unique_buyers_30d":"insider_unique_buyers_30d",
 "insider_cluster_active":"insider_cluster_active",
 "institutional_increased":"institutional_increased",
 "risk_off_regime_gold_signal":"risk_off_regime_gold_signal",
 "defensive_leadership":"defensive_leadership",
 "is_january_extended":"is_january_extended",
 "news_count_5d":"news_count_5d",
 "news_sentiment_shift":"news_sentiment_shift",
}
silent_datafed=["classification_change_recent_long","classification_change_to_defensive_short",
 "classification_change_from_tech_short","insider_cluster_long","insider_cluster_with_director_long",
 "pead_with_insider_confirmation_long","institutional_increased_with_directors_long",
 "gold_silver_risk_off_long","sector_rotation_defensive_long","january_effect_small_cap_long",
 "news_reversal_long","news_reversal_short","news_momentum_short","post_deletion_drift_short",
 "pre_rebalance_long"]

def load(tk):
    p=f"backtest/data/cache/ohlcv/{tk}.parquet"
    if not os.path.exists(p): return None
    df=pd.read_parquet(p); df.columns=[c.lower() for c in df.columns]
    df["date"]=pd.to_datetime(df["date"]); return df.set_index("date").sort_index()

# grid: reclassified tickers @ their window + broad names @ monthly + Jan + risk-off dates
recl=["V","MA","TGT","DG","ADP","PAYX","PYPL","DLTR"]
broad=["AAPL","MSFT","NVDA","TSLA","COIN","JPM","XOM","F","GM","INTC","MU","AMD","BAC","GS","NFLX"]
dates=[date(y,m,15) for y in (2022,2023,2024,2025) for m in (1,3,6,9,12)]+[date(2023,4,1),date(2023,5,1),date(2025,4,10)]
tickers=list(dict.fromkeys(recl+broad))

key_hits={k:0 for k in DATAFED}; key_examples={k:None for k in DATAFED}
strat_fires={s:0 for s in silent_datafed}
t0=time.time(); calls=0
for tk in tickers:
    df=load(tk)
    if df is None: continue
    for as_of in dates:
        sl=df[df.index.date<=as_of]
        if len(sl)<210: continue
        try:
            res=sc.screen_instrument(tk, sl, {}, as_of)
        except Exception as e:
            continue
        calls+=1
        sig=res.get("signals",{})
        for k in DATAFED:
            v=sig.get(k)
            if v is True or (isinstance(v,(int,float)) and v):
                key_hits[k]+=1
                if key_examples[k] is None: key_examples[k]=f"{tk}@{as_of}={v}"
        for cand in res.get("strategies",[]):
            nm=cand.get("strategy")
            if nm in strat_fires: strat_fires[nm]+=1
    print(f"{tk} done calls={calls} elapsed={time.time()-t0:.0f}s", flush=True)

print("\n=== DATA-FED PRODUCER EMIT (does key ever go non-default?) ===")
for k in DATAFED:
    st="EMITS" if key_hits[k]>0 else "*** NEVER-EMITS (RED FLAG) ***"
    print(f"  {k:35} hits={key_hits[k]:4} {st}  {key_examples[k] or ''}")
print("\n=== DATA-FED STRATEGY FIRES (via real screen_instrument) ===")
for s in silent_datafed:
    print(f"  {s:48} fires={strat_fires[s]}")
json.dump({"calls":calls,"key_hits":key_hits,"key_examples":key_examples,"strat_fires":strat_fires},
          open(r"C:\Users\jeetm\Github\stock-picks-app\output_audit\b1340_datafed_probe.json","w"),indent=2)
print(f"\nDONE calls={calls} elapsed={time.time()-t0:.0f}s")
