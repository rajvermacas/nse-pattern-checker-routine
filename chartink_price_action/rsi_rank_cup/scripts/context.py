import sys, json, numpy as np, pandas as pd
sys.path.insert(0,'rsi15')
from daily_series import load_all

g_all = load_all()
top = [l.strip() for l in open('rsi15/top15.txt') if l.strip()]
rank = {r['symbol']:(i+1,r['rsi14']) for i,r in enumerate(json.load(open('rsi15/ranking.json')))}

rows=[]
for s in top:
    g=g_all[s]; c=g['close'].values; h=g['high'].values; l=g['low'].values; v=g['volume'].values
    n=len(c); r,q = rank[s]
    hi250=h.max(); hi110=h[-110:].max(); ihi=int(np.argmax(h[-110:]))+n-110
    # drawdown from the 110-bar high, and where the low since that high sits
    post=l[ihi:]; lo_post=post.min() if len(post) else np.nan
    rows.append({
      '#':r,'sym':s,'rsi':q,'close':round(c[-1],2),
      'pct_off_250hi':round(100*(c[-1]/hi250-1),1),
      'pct_off_110hi':round(100*(c[-1]/hi110-1),1),
      'bars_since_110hi': n-1-ihi,
      'deepest_drop_after_hi_%': round(100*(lo_post/hi110-1),1),
      'ret_60d_%': round(100*(c[-1]/c[-61]-1),1),
      'ret_120d_%': round(100*(c[-1]/c[-121]-1),1),
      'vol_last5_vs20': round(float(v[-5:].mean()/v[-20:].mean()),2),
    })
d=pd.DataFrame(rows); pd.set_option('display.width',220)
print(d.to_string(index=False))
d.to_json('rsi15/context.json',orient='records',indent=1)
