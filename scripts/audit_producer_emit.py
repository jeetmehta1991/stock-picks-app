import pandas as pd, inspect, re, json, time, os
from datetime import date
from backtest.signals.technical import compute_all_signals
from backtest.signals.chart_patterns import compute_all_chart_patterns
import backtest.signals.screener as sc

tl=pd.read_parquet("output_batches/batch_1/trade_log.parquet")
traded=set(tl.strategy.unique())
silent=sorted(set(sc.ALL_STRATEGIES)-traded)

def keys_of(fn):
    try: src=inspect.getsource(fn)
    except Exception: return set()
    a=set(re.findall(r"s\.get\(\s*[\"']([a-zA-Z0-9_]+)[\"']", src))
    b=set(re.findall(r"s\[[\"']([a-zA-Z0-9_]+)[\"']\]", src))
    return a|b
req={s:keys_of(sc.ALL_STRATEGIES[s]) for s in silent}

sample=["AAPL","MSFT","NVDA","MU","WDC","AMD","TSLA","COIN","MARA","RIOT",
        "XOM","CVX","JPM","GS","JNJ","LLY","PG","KO","CAT","GE",
        "AMZN","META","NFLX","CRM","ORCL","INTC","F","GM","BAC","PYPL"]
WIN=(date(2022,5,5),date(2026,5,5))
avail=[t for t in sample if os.path.exists(f"backtest/data/cache/ohlcv/{t}.parquet")]
print(f"silent={len(silent)} sample_avail={len(avail)}: {avail}", flush=True)

fires={s:0 for s in silent}; key_seen=set(); t0=time.time()
for ti,tk in enumerate(avail):
    df=pd.read_parquet(f"backtest/data/cache/ohlcv/{tk}.parquet"); df.columns=[c.lower() for c in df.columns]
    df["date"]=pd.to_datetime(df["date"]); df=df.set_index("date").sort_index()
    win=[d for d in df.index if WIN[0]<=d.date()<=WIN[1]]
    for as_of in win:
        sl=df[df.index<=as_of]
        if len(sl)<210: continue
        sig=compute_all_signals(sl); cp=compute_all_chart_patterns(sl)
        if cp: sig.update(cp)
        key_seen.update(sig.keys())
        for s in silent:
            try:
                if sc.ALL_STRATEGIES[s](sig)["fires"]: fires[s]+=1
            except Exception: pass
    print(f"[{ti+1}/{len(avail)}] {tk} elapsed={time.time()-t0:.0f}s fires>0={sum(1 for v in fires.values() if v>0)}", flush=True)

out=[]
for s in silent:
    missing=req[s]-key_seen
    if fires[s]>0: cls="FIRES_OK_rare"
    elif missing: cls="DATA_FED_inconclusive"
    else: cls="RED_FLAG_0fire_keys_present"
    out.append({"strategy":s,"fires":fires[s],"class":cls,"missing_keys":sorted(missing)[:6]})
out.sort(key=lambda r:(r["class"],-r["fires"]))
json.dump({"sample":avail,"window":str(WIN),"n_key_seen":len(key_seen),"results":out},
          open(r"C:\Users\jeetm\Github\stock-picks-app\output_audit\b1340_producer_emit_audit.json","w"),indent=2)
from collections import Counter
print("\n=== CLASSIFICATION ===",flush=True); print(Counter(r["class"] for r in out))
for r in out: print(f"  {r['strategy']:46} fires={r['fires']:4} {r['class']} {r['missing_keys'] if r['class']=='DATA_FED_inconclusive' else ''}")
print(f"\nDONE elapsed={time.time()-t0:.0f}s",flush=True)
