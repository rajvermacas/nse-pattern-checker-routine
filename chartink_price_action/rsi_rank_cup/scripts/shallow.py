import sys, json, numpy as np, pandas as pd
sys.path.insert(0,'rsi15')
from daily_series import load_all

MAX_DEPTH = 0.07     # user constraint
MIN_LEN   = 8        # a base, not a 2-bar pause
MIN_RALLY = 0.15     # >= +15% run into the rim
LOOKBACK  = 150      # search window for the rim

g_all = load_all()
rank = {r['symbol']: (i+1, r['rsi14']) for i,r in enumerate(json.load(open('rsi15/ranking.json')))}

out=[]
for sym,g in g_all.items():
    h=g['high'].values.astype(float); l=g['low'].values.astype(float)
    c=g['close'].values.astype(float); d=g['d'].values; n=len(c)
    best=None
    for i in range(max(0,n-LOOKBACK), n-MIN_LEN):
        # rim = local swing high over a trailing 20-bar window
        if h[i] < h[max(0,i-20):i+1].max(): continue
        # base runs until the first CLOSE back above the rim
        j=n
        for k in range(i+1,n):
            if c[k] > h[i]: j=k; break
        blen = min(j,n)-i
        if blen < MIN_LEN: continue
        seg = l[i+1:min(j,n)]
        if not len(seg): continue
        depth = 1 - seg.min()/h[i]
        if depth > MAX_DEPTH or depth <= 0: continue
        rally = h[i]/l[max(0,i-90):i+1].min() - 1
        if rally < MIN_RALLY: continue
        rec = dict(symbol=sym, rank=rank[sym][0], rsi=rank[sym][1],
                   rim=round(float(h[i]),2), rim_date=str(d[i]),
                   depth_pct=round(100*depth,2), base_bars=int(blen),
                   rally_pct=round(100*rally,1),
                   resolved=(j<n), close=round(float(c[-1]),2),
                   vs_rim_pct=round(100*(c[-1]/h[i]-1),2),
                   bars_since_rim=int(n-1-i))
        # prefer the longest qualifying base, tie-break on shallower
        key=(blen, -depth)
        if best is None or key>best[0]: best=(key,rec)
    if best: out.append(best[1])

df=pd.DataFrame(out).sort_values(['base_bars','depth_pct'],ascending=[False,True]).reset_index(drop=True)
pd.set_option('display.width',250)
print('symbols with a <%.0f%% base: %d of 107' % (100*MAX_DEPTH, len(df)))
print(df.to_string(index=False))
df.to_json('rsi15/shallow_hits.json',orient='records',indent=1)
